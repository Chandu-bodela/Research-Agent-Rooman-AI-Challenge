from __future__ import annotations

from backend.retriever import KnowledgeBase


class DummyEmbedder:
    def __init__(self):
        self.dimension = 3

    def embed_query(self, query: str):
        return [0.0, 0.0, 0.0]

    def embed_texts(self, texts):
        return [[0.0, 0.0, 0.0] for _ in texts]


class DummyStore:
    def __init__(self, results):
        self._results = results
        self.metadata = []

    def search(self, query_vector, top_k):
        return self._results

    def chunk_count(self):
        return 0

    def document_names(self):
        return []

    def document_stats(self):
        return {}

    def save(self, *args, **kwargs):
        return None


def test_retrieve_falls_back_to_top_matches_when_threshold_is_hard(monkeypatch):
    kb = KnowledgeBase.__new__(KnowledgeBase)
    kb.embedder = DummyEmbedder()
    kb.store = DummyStore([(object(), 0.02), (object(), 0.10)])
    monkeypatch.setattr("backend.retriever.settings.similarity_threshold", 0.15)

    results = kb.retrieve("broad question", top_k=2)

    assert len(results) == 2
    assert [r.score for r in results] == [0.02, 0.10]
