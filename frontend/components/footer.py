"""
frontend/components/footer.py — Shared footer.
"""
from __future__ import annotations
import streamlit as st


def render_footer() -> None:
    st.markdown(
        """
        <div class="rm-footer">
            Built with ❤️ using Streamlit · sentence-transformers · FAISS &nbsp;|&nbsp;
            ResearchMind AI © 2025
        </div>
        """,
        unsafe_allow_html=True,
    )
