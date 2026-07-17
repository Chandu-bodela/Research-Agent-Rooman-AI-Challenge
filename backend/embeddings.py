"""
backend/embeddings.py
======================
Thin wrapper around `sentence-transformers` so the rest of the codebase
doesn't need to know which embedding model or library is in use.

The model (`all-MiniLM-L6-v2` by default) is loaded once per process and
cached, since loading it is the slowest part of app startup.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

import numpy as np

from backend.utils import get_logger
from config import settings

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_model():
    """Lazily load and cache the sentence-transformers model.

    Cached with lru_cache so repeated Streamlit re-runs (which re-execute
    the whole script) don't reload the model from disk every interaction.
    """
    from sentence_transformers import SentenceTransformer  # local import: heavy

    logger.info("Loading embedding model: %s", settings.embedding_model_name)
    return SentenceTransformer(settings.embedding_model_name)


class EmbeddingService:
    """Generates dense vector embeddings for text chunks and queries."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.embedding_model_name
        self._model = _get_model()

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed a batch of texts. Returns an (N, dim) float32 array."""
        if not texts:
            return np.zeros((0, self.dimension), dtype="float32")
        embeddings = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,  # cosine similarity via dot product
            convert_to_numpy=True,
        )
        return embeddings.astype("float32")

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string. Returns a (dim,) float32 vector."""
        return self.embed_texts([query])[0]
