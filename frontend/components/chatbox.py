"""
frontend/components/chatbox.py — Premium chat bubble renderer.
"""
from __future__ import annotations
from typing import List
import streamlit as st
from frontend.components.citation_card import render_citations, render_not_found_banner


def render_message(role: str, content: str, citations: list | None = None, not_found: bool = False) -> None:
    if role == "user":
        st.markdown(
            f"""
            <div class="rm-chat-user-row rm-animate-fade-up">
                <div class="rm-chat-user">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="rm-chat-assistant-row rm-animate-fade-up">
                <div class="rm-ai-icon">🧠</div>
                <div class="rm-chat-assistant">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not_found:
            render_not_found_banner()
        if citations:
            render_citations(citations)


def render_conversation(messages: List[dict]) -> None:
    if not messages:
        st.markdown(
            """
            <div class="rm-empty rm-animate-fade-in">
                <span class="rm-empty-icon">💬</span>
                <div class="rm-empty-title">Start a conversation</div>
                <div class="rm-empty-sub">Ask anything about your uploaded documents below.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="rm-chat-wrapper">', unsafe_allow_html=True)
    for msg in messages:
        render_message(
            role=msg["role"],
            content=msg["content"],
            citations=msg.get("citations"),
            not_found=msg.get("not_found", False),
        )
    st.markdown("</div>", unsafe_allow_html=True)
