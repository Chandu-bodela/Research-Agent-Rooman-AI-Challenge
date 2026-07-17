"""
frontend/components/sidebar.py — Premium sidebar with nav, stats, model selector.
"""
from __future__ import annotations
import streamlit as st
from backend.retriever import KnowledgeBase


def render_sidebar(kb: KnowledgeBase | None = None) -> None:
    with st.sidebar:
        # Logo
        st.markdown(
            """
            <div class="rm-sidebar-logo">
                <h2>🧠 ResearchMind AI</h2>
                <p>Your documents. Grounded answers.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation
        st.markdown('<div class="rm-sidebar-section">Navigation</div>', unsafe_allow_html=True)
        st.page_link("app.py",               label="🏠  Home")
        st.page_link("pages/1_Upload.py",     label="📄  Documents")
        st.page_link("pages/2_Chat.py",       label="💬  Research Chat")
        st.page_link("pages/3_History.py",    label="🕒  History")
        st.page_link("pages/4_Analytics.py",  label="📊  Analytics")
        st.page_link("pages/5_Settings.py",   label="⚙️  Settings")

        st.divider()

        # Knowledge base stats
        if kb is not None:
            docs = kb.documents()
            stats = kb.stats()
            st.markdown('<div class="rm-sidebar-section">Knowledge Base</div>', unsafe_allow_html=True)
            if not docs:
                st.markdown(
                    """
                    <div class="rm-empty" style="padding:1rem 0.5rem;">
                        <span class="rm-empty-icon" style="font-size:1.5rem;">📭</span>
                        <div class="rm-empty-sub">No documents yet</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                for name in docs[:6]:
                    chunks = stats.get(name, 0)
                    short = name if len(name) <= 22 else name[:20] + "…"
                    st.markdown(
                        f"""
                        <div style="display:flex;align-items:center;gap:0.5rem;
                             padding:0.4rem 0.5rem;border-radius:8px;margin-bottom:2px;">
                            <span style="font-size:1rem;">📄</span>
                            <div>
                                <div style="font-size:0.82rem;font-weight:500;color:#111827;">{short}</div>
                                <div style="font-size:0.72rem;color:#6B7280;">{chunks} chunks</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                if len(docs) > 6:
                    st.caption(f"+ {len(docs)-6} more documents")

        st.divider()

        # Model selector
        st.markdown('<div class="rm-sidebar-section">Model</div>', unsafe_allow_html=True)
        providers = ["groq", "openai", "anthropic", "gemini"]
        current = st.session_state.get("llm_provider", "groq")
        idx = providers.index(current) if current in providers else 0
        chosen = st.selectbox(
            "LLM Provider",
            providers,
            index=idx,
            label_visibility="collapsed",
        )
        st.session_state["llm_provider"] = chosen

        st.divider()

        # Dark mode + user
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(
                """
                <div style="display:flex;align-items:center;gap:0.5rem;">
                    <div class="rm-avatar">R</div>
                    <div style="font-size:0.82rem;font-weight:500;">Researcher</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            dm = st.toggle("🌙", value=st.session_state.get("dark_mode", False), help="Dark mode")
            st.session_state["dark_mode"] = dm
