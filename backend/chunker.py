"""
backend/chunker.py
===================
Splits parsed document pages into overlapping text chunks suitable for
embedding + retrieval.

Chunking strategy
------------------
A simple, robust character-window splitter with overlap. It:
  1. Prefers to break on paragraph/sentence boundaries near the target size
     so chunks stay semantically coherent.
  2. Keeps `chunk_overlap` characters of context between consecutive chunks
     so an answer that straddles a chunk boundary isn't lost.
  3. Preserves the source page number for every chunk (critical for
     citations).

This is intentionally simple rather than using a heavier NLP-based
splitter — it's fast, dependency-light, and good enough for a RAG system
built in a 24-hour window, while still being clearly documented so its
limitations are visible (see README "Tradeoffs").
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from backend.parser import PageText
from backend.utils import get_logger, new_id

logger = get_logger(__name__)


@dataclass
class Chunk:
    """A single retrievable unit of text with full provenance metadata."""

    chunk_id: str
    document_name: str
    page_number: int
    text: str
    chunk_index: int  # position within the document, for ordering/debug


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split a block of text into overlapping windows.

    Tries to snap window boundaries to sentence breaks so we don't cut
    mid-sentence whenever a nearby boundary is available.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    sentences = _SENTENCE_BOUNDARY.split(text)
    chunks: List[str] = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            # Start new chunk, carrying over the tail of the previous one
            # for context continuity.
            overlap_text = current[-overlap:] if overlap and current else ""
            current = f"{overlap_text} {sentence}".strip()

            # Edge case: a single sentence longer than chunk_size — hard split.
            while len(current) > chunk_size:
                chunks.append(current[:chunk_size])
                current = current[chunk_size - overlap:]

    if current:
        chunks.append(current)

    return chunks


def chunk_document(
    document_name: str,
    pages: List[PageText],
    chunk_size: int,
    overlap: int,
) -> List[Chunk]:
    """Chunk every page of a parsed document, preserving page provenance."""
    all_chunks: List[Chunk] = []
    global_index = 0

    for page in pages:
        pieces = chunk_text(page.text, chunk_size=chunk_size, overlap=overlap)
        for piece in pieces:
            all_chunks.append(
                Chunk(
                    chunk_id=new_id("chk_"),
                    document_name=document_name,
                    page_number=page.page_number,
                    text=piece,
                    chunk_index=global_index,
                )
            )
            global_index += 1

    logger.info("Chunked '%s' into %d chunks", document_name, len(all_chunks))
    return all_chunks
