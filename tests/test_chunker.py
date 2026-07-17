"""
tests/test_chunker.py
======================
Unit tests for the text-chunking logic. Run with: pytest tests/
"""

from __future__ import annotations

from backend.chunker import chunk_document, chunk_text
from backend.parser import PageText


def test_chunk_text_returns_single_chunk_for_short_text():
    text = "This is a short sentence."
    chunks = chunk_text(text, chunk_size=800, overlap=150)
    assert chunks == [text]


def test_chunk_text_splits_long_text():
    text = " ".join([f"Sentence number {i}." for i in range(200)])
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 260 for c in chunks)  # allow overlap slack


def test_chunk_text_empty_input_returns_empty_list():
    assert chunk_text("", chunk_size=800, overlap=150) == []
    assert chunk_text("   ", chunk_size=800, overlap=150) == []


def test_chunk_document_preserves_page_numbers():
    pages = [
        PageText(page_number=1, text="Page one content. " * 40),
        PageText(page_number=2, text="Page two content. " * 40),
    ]
    chunks = chunk_document("doc.pdf", pages, chunk_size=200, overlap=50)

    page_numbers = {c.page_number for c in chunks}
    assert page_numbers == {1, 2}
    assert all(c.document_name == "doc.pdf" for c in chunks)
    # chunk_index should be monotonically increasing across the whole document
    indices = [c.chunk_index for c in chunks]
    assert indices == sorted(indices)


def test_chunk_document_empty_pages_returns_no_chunks():
    assert chunk_document("empty.txt", [], chunk_size=800, overlap=150) == []
