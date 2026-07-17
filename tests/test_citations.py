"""
tests/test_citations.py
========================
Unit tests for citation building, filtering, and the "not found" heuristic
that helps prevent hallucinated answers.
"""

from __future__ import annotations

from backend.chunker import Chunk
from backend.citations import (
    build_citations,
    build_context_block,
    filter_citations_to_used,
    is_not_found_answer,
    used_citation_labels,
)
from backend.retriever import RetrievedChunk


def _make_retrieved(n: int) -> list[RetrievedChunk]:
    chunks = [
        Chunk(
            chunk_id=f"chk_{i}",
            document_name=f"doc{i}.pdf",
            page_number=i,
            text=f"This is chunk {i} content about topic {i}.",
            chunk_index=i,
        )
        for i in range(n)
    ]
    return [RetrievedChunk(chunk=c, score=0.9 - i * 0.1) for i, c in enumerate(chunks)]


def test_build_context_block_labels_each_source():
    retrieved = _make_retrieved(2)
    block = build_context_block(retrieved)
    assert "[S1]" in block
    assert "[S2]" in block
    assert "doc0.pdf" in block and "doc1.pdf" in block


def test_build_citations_matches_retrieved_count():
    retrieved = _make_retrieved(3)
    citations = build_citations(retrieved)
    assert len(citations) == 3
    assert citations[0].label == "S1"
    assert citations[2].label == "S3"


def test_used_citation_labels_extracts_correct_labels():
    answer = "First fact [S1]. Second fact [S2][S3]. Repeated [S1]."
    assert used_citation_labels(answer) == ["1", "2", "3"]


def test_filter_citations_to_used_drops_uncited_sources():
    retrieved = _make_retrieved(3)
    citations = build_citations(retrieved)
    answer = "Only used the first source [S1]."
    filtered = filter_citations_to_used(citations, answer)
    assert len(filtered) == 1
    assert filtered[0].label == "S1"


def test_filter_citations_falls_back_to_all_if_no_labels_used():
    retrieved = _make_retrieved(2)
    citations = build_citations(retrieved)
    answer = "An answer with no citation tags at all."
    filtered = filter_citations_to_used(citations, answer)
    assert filtered == citations


def test_is_not_found_answer_detects_standard_phrase():
    assert is_not_found_answer("I couldn't find this in the uploaded documents.")
    assert not is_not_found_answer("Employees accrue 1.5 days of PTO per month [S1].")
