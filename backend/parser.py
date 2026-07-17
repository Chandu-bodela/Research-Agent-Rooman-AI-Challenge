"""
backend/parser.py
==================
Extracts plain text (with page numbers, where the format has them) from
uploaded documents: PDF, DOCX, TXT, and Markdown.

Design note
-----------
Every parser returns a list of `PageText` objects rather than one giant
string. This keeps page-level provenance alive all the way through
chunking -> retrieval -> citation, which is what lets ResearchMind AI cite
"Document X, Page Y" instead of just "Document X".

For formats without a native concept of pages (TXT, Markdown, DOCX), we
treat the whole document as a single "page" (page = 1) unless we choose to
split DOCX by section breaks (kept simple here for hackathon scope).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import docx  # python-docx
import fitz  # PyMuPDF
import markdown as md_lib

from backend.utils import get_logger

logger = get_logger(__name__)


@dataclass
class PageText:
    """A single page (or page-like unit) of extracted text."""

    page_number: int
    text: str


class UnsupportedFileTypeError(Exception):
    """Raised when a file extension isn't one we know how to parse."""


class ParsingError(Exception):
    """Raised when a file appears to be the right type but fails to parse."""


def parse_document(file_path: Path) -> List[PageText]:
    """Dispatch to the correct parser based on file extension.

    Parameters
    ----------
    file_path:
        Path to a file already saved on disk (e.g. in `data/uploads`).

    Returns
    -------
    List[PageText]
        One entry per page (PDF) or one entry total (TXT/MD/DOCX).
    """
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _parse_pdf(file_path)
        if suffix == ".docx":
            return _parse_docx(file_path)
        if suffix in (".txt",):
            return _parse_txt(file_path)
        if suffix in (".md", ".markdown"):
            return _parse_markdown(file_path)
    except UnsupportedFileTypeError:
        raise
    except Exception as exc:  # noqa: BLE001 - we want to wrap *any* failure
        logger.exception("Failed to parse %s", file_path)
        raise ParsingError(f"Could not parse '{file_path.name}': {exc}") from exc

    raise UnsupportedFileTypeError(f"Unsupported file type: {suffix}")


def _parse_pdf(file_path: Path) -> List[PageText]:
    """Extract text page-by-page from a PDF using PyMuPDF."""
    pages: List[PageText] = []
    with fitz.open(file_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append(PageText(page_number=i, text=text))
    if not pages:
        logger.warning("No extractable text found in %s (scanned image PDF?)", file_path)
    return pages


def _parse_docx(file_path: Path) -> List[PageText]:
    """Extract text from a DOCX file.

    DOCX has no reliable page-boundary metadata (pagination happens at
    render time), so the whole document is treated as page 1. Paragraphs
    are joined with double newlines to preserve some structure for the
    chunker.
    """
    document = docx.Document(str(file_path))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n\n".join(paragraphs)
    return [PageText(page_number=1, text=text)] if text.strip() else []


def _parse_txt(file_path: Path) -> List[PageText]:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return [PageText(page_number=1, text=text)] if text.strip() else []


def _parse_markdown(file_path: Path) -> List[PageText]:
    """Extract text from Markdown, stripping formatting markup.

    We convert to HTML then strip tags rather than shipping a full HTML
    parser dependency — good enough for research-note style Markdown.
    """
    import re

    raw = file_path.read_text(encoding="utf-8", errors="ignore")
    html = md_lib.markdown(raw)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+\n", "\n", text)
    text = text.strip()
    return [PageText(page_number=1, text=text)] if text else []
