"""
backend/export.py
==================
Exports a question/answer + its citations to Markdown or PDF, so users can
save research findings outside the app.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from backend.citations import Citation
from backend.utils import get_logger, new_id, safe_filename, timestamp
from config import ANSWERS_DIR

logger = get_logger(__name__)


def _build_markdown(question: str, answer: str, citations: List[Citation]) -> str:
    lines = [
        "# ResearchMind AI — Answer Export",
        "",
        f"**Generated:** {timestamp()}",
        "",
        "## Question",
        question.strip(),
        "",
        "## Answer",
        answer.strip(),
        "",
        "## Sources",
    ]
    if citations:
        for c in citations:
            lines.append(
                f"- **[{c.label}]** {c.document_name} — Page {c.page_number} "
                f"(relevance: {c.score:.2f})\n  > {c.snippet}"
            )
    else:
        lines.append("_No sources were cited for this answer._")

    return "\n".join(lines)


def export_to_markdown(question: str, answer: str, citations: List[Citation]) -> Path:
    """Write the Q&A + citations to a Markdown file and return its path."""
    content = _build_markdown(question, answer, citations)
    filename = safe_filename(f"answer_{new_id()}.md")
    path = ANSWERS_DIR / filename
    path.write_text(content, encoding="utf-8")
    logger.info("Exported answer to Markdown: %s", path)
    return path


def export_to_pdf(question: str, answer: str, citations: List[Citation]) -> Path:
    """Write the Q&A + citations to a simple, clean PDF and return its path."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def line(text: str, size: int = 11, style: str = "", color=(17, 24, 39), height: int = 6) -> None:
        """Render one multi-line text block and reliably return the cursor
        to the left margin afterward (fpdf2's default multi_cell behavior
        otherwise leaves x at the right edge, which breaks subsequent calls)."""
        pdf.set_font("Helvetica", style, size)
        pdf.set_text_color(*color)
        pdf.multi_cell(0, height, _pdf_safe(text), new_x="LMARGIN", new_y="NEXT")

    line("ResearchMind AI - Answer Export", size=16, style="B", color=(37, 99, 235), height=10)
    pdf.ln(2)
    line(f"Generated: {timestamp()}", size=9, color=(107, 114, 128))
    pdf.ln(4)

    line("Question", size=12, style="B", color=(17, 24, 39), height=8)
    line(question, size=11)
    pdf.ln(3)

    line("Answer", size=12, style="B", height=8)
    line(answer, size=11)
    pdf.ln(3)

    line("Sources", size=12, style="B", height=8)
    if citations:
        for c in citations:
            line(
                f"[{c.label}] {c.document_name} - Page {c.page_number} (relevance {c.score:.2f})",
                size=10, style="B", color=(124, 58, 237),
            )
            line(c.snippet, size=10, color=(55, 65, 81), height=5)
            pdf.ln(2)
    else:
        line("No sources were cited for this answer.", size=10)

    filename = safe_filename(f"answer_{new_id()}.pdf")
    path = ANSWERS_DIR / filename
    pdf.output(str(path))
    logger.info("Exported answer to PDF: %s", path)
    return path


def _pdf_safe(text: str) -> str:
    """FPDF's core fonts are latin-1 only; degrade unsupported characters
    gracefully rather than raising an encoding error mid-export."""
    return text.encode("latin-1", errors="replace").decode("latin-1")
