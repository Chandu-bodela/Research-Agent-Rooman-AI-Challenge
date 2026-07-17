"""
backend/retriever.py
=====================
Ties together parsing -> chunking -> embedding -> vector storage, and
exposes the two operations the rest of the app actually needs:

    1. `ingest_document(path)`  — add a new file to the knowledge base
    2. `retrieve(query)`        — get the top-k most relevant chunks

This module owns the on-disk persistence location for the FAISS index and
its metadata so callers (Streamlit pages) don't need to know those
details.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from backend.chunker import Chunk, chunk_document
from backend.embeddings import EmbeddingService
from backend.parser import ParsingError, UnsupportedFileTypeError, parse_document
from backend.utils import get_logger
from backend.vector_store import VectorStore
from config import EMBEDDINGS_DIR, settings

logger = get_logger(__name__)

INDEX_PATH = EMBEDDINGS_DIR / "faiss.index"
METADATA_PATH = EMBEDDINGS_DIR / "metadata.pkl"


class RetrievedChunk:
    """A chunk returned from retrieval, paired with its similarity score."""

    def __init__(self, chunk: Chunk, score: float):
        self.chunk = chunk
        self.score = score

    def __repr__(self) -> str:  # pragma: no cover - debug convenience
        return f"<RetrievedChunk doc={self.chunk.document_name!r} page={self.chunk.page_number} score={self.score:.3f}>"


class KnowledgeBase:
    """Owns the embedding model + vector store for the current session.

    A single instance is created once (cached in Streamlit session state)
    and reused across uploads and questions.
    """

    def __init__(self) -> None:
        self.embedder = EmbeddingService()
        self.store = VectorStore.load(INDEX_PATH, METADATA_PATH, self.embedder.dimension)

    # --------------------------------------------------------------- #
    # Ingestion
    # --------------------------------------------------------------- #
    def ingest_document(self, file_path: Path, display_name: Optional[str] = None) -> int:
        """Parse, chunk, embed, and index one document.

        Returns the number of chunks added. Raises `UnsupportedFileTypeError`
        or `ParsingError` if the file can't be processed — callers (the
        Upload page) should catch these and show a friendly message.
        """
        name = display_name or file_path.name
        pages = parse_document(file_path)
        if not pages:
            logger.warning("No text extracted from %s", name)
            return 0

        chunks = chunk_document(
            document_name=name,
            pages=pages,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )
        if not chunks:
            return 0

        embeddings = self.embedder.embed_texts([c.text for c in chunks])
        self.store.add(embeddings, chunks)
        self.persist()
        return len(chunks)

    def remove_document(self, document_name: str) -> None:
        """Remove a document from the knowledge base and rebuild the index."""
        remaining = [c for c in self.store.metadata if c.document_name != document_name]
        if len(remaining) == len(self.store.metadata):
            return

        # Rebuild from scratch since FAISS flat index has no cheap delete.
        new_store = VectorStore(dimension=self.embedder.dimension)
        if remaining:
            embeddings = self.embedder.embed_texts([c.text for c in remaining])
            new_store.add(embeddings, remaining)
        self.store = new_store
        self.persist()

    def persist(self) -> None:
        self.store.save(INDEX_PATH, METADATA_PATH)

    # --------------------------------------------------------------- #
    # Retrieval
    # --------------------------------------------------------------- #
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[RetrievedChunk]:
        """Return the top-k most relevant chunks for a query.

        The similarity threshold is treated as a soft signal: if some chunks
        clear it, those are preferred. If none do, the best available matches
        are still returned so the app can answer broadly grounded questions
        instead of failing too early.
        """
        top_k = top_k or settings.top_k
        query_vector = self.embedder.embed_query(query)
        raw_results = self.store.search(query_vector, top_k=top_k)

        scored_results = [
            RetrievedChunk(chunk=chunk, score=score)
            for chunk, score in raw_results
        ]
        above_threshold = [
            result for result in scored_results
            if result.score >= settings.similarity_threshold
        ]
        results = above_threshold or scored_results

        logger.info(
            "Retrieved %d/%d chunks above threshold %.2f for query: %r",
            len(above_threshold), len(scored_results), settings.similarity_threshold, query,
        )
        return results

    # --------------------------------------------------------------- #
    # Introspection (used by Upload / History / Settings pages)
    # --------------------------------------------------------------- #
    def documents(self) -> List[str]:
        return self.store.document_names()

    def stats(self) -> dict:
        return self.store.document_stats()

    def is_empty(self) -> bool:
        return self.store.chunk_count() == 0
