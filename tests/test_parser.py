"""
tests/test_parser.py
=====================
Unit tests for document parsing across supported file types.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.parser import (
    ParsingError,
    UnsupportedFileTypeError,
    parse_document,
)

SAMPLES = Path(__file__).resolve().parent.parent / "data" / "sample_documents"


def test_parse_markdown_extracts_text():
    pages = parse_document(SAMPLES / "company_handbook.md")
    assert len(pages) == 1
    assert "Leave Policy" in pages[0].text
    assert pages[0].page_number == 1


def test_parse_txt_extracts_text():
    pages = parse_document(SAMPLES / "market_research_notes.txt")
    assert len(pages) == 1
    assert "Customer Satisfaction" in pages[0].text


def test_parse_pdf_extracts_text_and_pages():
    pdf_path = SAMPLES / "warranty_policy.pdf"
    if not pdf_path.exists():
        pytest.skip("Sample PDF not present")
    pages = parse_document(pdf_path)
    assert len(pages) >= 1
    joined = " ".join(p.text for p in pages)
    assert "Warranty" in joined


def test_parse_docx_extracts_text():
    docx_path = SAMPLES / "engineering_onboarding.docx"
    if not docx_path.exists():
        pytest.skip("Sample DOCX not present")
    pages = parse_document(docx_path)
    assert len(pages) == 1
    assert "On-Call Rotation" in pages[0].text


def test_parse_unsupported_extension_raises():
    with pytest.raises(UnsupportedFileTypeError):
        parse_document(Path("somefile.xyz"))


def test_parse_missing_file_raises_parsing_error():
    with pytest.raises((ParsingError, FileNotFoundError, UnsupportedFileTypeError)):
        parse_document(SAMPLES / "does_not_exist.txt")
