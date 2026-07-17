"""
backend/summarizer.py
======================
Generates a short, cited research summary across a set of retrieved
chunks (or an entire document's chunks). Reuses the same LLM + citation
machinery as Q&A so summaries stay grounded and source-tagged.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from backend.citations import build_context_block
from backend.llm import generate_answer
from backend.retriever import RetrievedChunk
from config import PROMPTS_DIR


def summarize_chunks(retrieved: List[RetrievedChunk]) -> str:
    """Produce a cited summary of the given chunks."""
    if not retrieved:
        return "No content available to summarize."

    template_path = PROMPTS_DIR / "summary_prompt.txt"
    template = template_path.read_text(encoding="utf-8")
    context = build_context_block(retrieved)
    user_prompt = template.format(context=context)

    system_prompt_path = PROMPTS_DIR / "system_prompt.txt"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    return generate_answer(system_prompt=system_prompt, user_prompt=user_prompt)


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Lightweight keyword extraction (no extra ML dependency).

    Uses simple frequency scoring over non-stopword tokens. Good enough
    for a "related keywords" bonus feature without adding heavyweight
    NLP dependencies to a 24-hour build.
    """
    import re
    from collections import Counter

    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "is", "are", "was", "were", "be", "been", "this",
        "that", "it", "as", "by", "from", "will", "shall", "we", "you",
        "your", "our", "their", "its", "not", "have", "has", "had", "can",
    }
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    counts = Counter(w for w in words if w not in stopwords)
    return [w for w, _ in counts.most_common(top_n)]
