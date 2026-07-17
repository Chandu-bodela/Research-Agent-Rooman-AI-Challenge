"""
frontend/components/citation_card.py — Premium citation cards with score bars.
"""
from __future__ import annotations
from typing import List
import streamlit as st
from backend.citations import Citation


def render_citations(citations: List[Citation]) -> None:
    if not citations:
        return
    st.markdown(
        '<div style="margin-top:0.75rem;"><span class="rm-badge rm-badge-primary">📎 Sources</span></div>',
        unsafe_allow_html=True,
    )
    for c in citations:
        score_pct = int(c.score * 100)
        score_width = min(score_pct, 100)
        st.markdown(
            f"""
            <div class="rm-citation rm-animate-fade-in">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.3rem;">
                    <div>
                        <span class="rm-citation-label">{c.label}</span>
                        <span class="rm-citation-doc">{c.document_name}</span>
                    </div>
                    <span class="rm-badge rm-badge-purple">Page {c.page_number}</span>
                </div>
                <div class="rm-citation-meta">Relevance: {score_pct}%</div>
                <div class="rm-score-bar">
                    <div class="rm-score-fill" style="width:{score_width}%;"></div>
                </div>
                <div class="rm-citation-snippet">&ldquo;{c.snippet}&rdquo;</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_not_found_banner(extra_note: str = "") -> None:
    note = f" {extra_note}" if extra_note else ""
    st.markdown(
        f"""
        <div class="rm-not-found rm-animate-fade-in">
            ⚠️ This wasn't found in your uploaded documents.{note}
        </div>
        """,
        unsafe_allow_html=True,
    )
