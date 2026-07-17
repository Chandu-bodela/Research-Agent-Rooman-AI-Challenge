"""
frontend/common.py — Shared page setup, CSS injection, session state.
"""
from __future__ import annotations
from pathlib import Path
import streamlit as st
from backend.retriever import KnowledgeBase
from config import BASE_DIR, settings

_CSS_PATH = BASE_DIR / "assets" / "css" / "style.css"


def inject_css() -> None:
    if _CSS_PATH.exists():
        css = _CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def configure_page(title: str, icon: str = "🧠") -> None:
    st.set_page_config(
        page_title=f"{title} · ResearchMind AI",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    # Apply dark mode body class if enabled
    if st.session_state.get("dark_mode", False):
        st.markdown(
            "<script>document.body.classList.add('dark-mode')</script>",
            unsafe_allow_html=True,
        )


@st.cache_resource(show_spinner="Loading knowledge base…")
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase()


def init_session_state() -> None:
    defaults = {
        "chat_messages": [],
        "ingested_hashes": set(),
        "dark_mode": False,
        "llm_provider": settings.llm_provider,
        "temperature": settings.temperature,
        "top_k": settings.top_k,
    }
    for key, val in defaults.items():
        st.session_state.setdefault(key, val)
