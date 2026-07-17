"""
backend/citations.py
=====================
Turns retrieved chunks into (a) a labeled context block to feed the LLM,
and (b) structured `Citation` objects the UI can render as citation cards.

The core anti-hallucination trick is simple but effective: every chunk in
the prompt is given a bracketed source label like [S1], and the model is
instructed to tag each claim with the matching label. We then parse those
labels back out to build citation cards, and separately verify that every
label the model used actually exists in our retrieved set.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from backend.retriever import RetrievedChunk


@dataclass
class Citation:
    """One source citation, ready for display in a citation card."""

    label: str            # e.g. "S1"
    document_name: str
    page_number: int
    snippet: str          # short excerpt for the card
    score: float


NOT_FOUND_PHRASE = (
    "I couldn't find this in the uploaded documents."
)


def build_context_block(retrieved: List[RetrievedChunk]) -> str:
    """Build the labeled context string injected into the user prompt.

    Example output:
        [S1] (policy.pdf, page 3): "Employees accrue 1.5 days..."
        [S2] (handbook.docx, page 1): "Remote work requires manager..."
    """
    lines = []
    for i, r in enumerate(retrieved, start=1):
        c = r.chunk
        lines.append(f"[S{i}] (Source: {c.document_name}, Page {c.page_number})\n{c.text}")
    return "\n\n".join(lines)


def build_citations(retrieved: List[RetrievedChunk], max_snippet_len: int = 220) -> List[Citation]:
    """Build Citation objects (one per retrieved chunk) for the UI."""
    citations = []
    for i, r in enumerate(retrieved, start=1):
        c = r.chunk
        snippet = c.text.strip().replace("\n", " ")
        if len(snippet) > max_snippet_len:
            snippet = snippet[:max_snippet_len].rsplit(" ", 1)[0] + "..."
        citations.append(
            Citation(
                label=f"S{i}",
                document_name=c.document_name,
                page_number=c.page_number,
                snippet=snippet,
                score=r.score,
            )
        )
    return citations


def used_citation_labels(answer_text: str) -> List[str]:
    """Extract the [S#] labels the model actually referenced in its answer."""
    return sorted(set(re.findall(r"\[S(\d+)\]", answer_text)), key=int)


def filter_citations_to_used(citations: List[Citation], answer_text: str) -> List[Citation]:
    """Keep only citations the model actually cited in the answer text.

    Falls back to returning all citations if the model didn't use the
    [S#] tagging convention (e.g. a weaker model that ignored instructions) —
    better to over-cite than to silently drop sourcing.
    """
    used = used_citation_labels(answer_text)
    if not used:
        return citations
    used_set = {f"S{n}" for n in used}
    filtered = [c for c in citations if c.label in used_set]
    return filtered or citations


def is_not_found_answer(answer_text: str) -> bool:
    """Heuristic check for whether the model declared 'not found in docs'."""
    lowered = answer_text.lower()
    triggers = [
        "couldn't find this in the uploaded documents",
        "not found in the uploaded documents",
        "does not contain",
        "documents do not mention",
        "no information about this",
        "i don't know based on the provided documents",
    ]
    return any(t in lowered for t in triggers)
