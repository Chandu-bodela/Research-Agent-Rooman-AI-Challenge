"""
pages/5_Settings.py — Premium settings page.
"""
from __future__ import annotations
import streamlit as st
from backend.llm import available_providers
from config import settings
from frontend.common import configure_page, get_knowledge_base, init_session_state
from frontend.components.footer import render_footer
from frontend.components.sidebar import render_sidebar

configure_page("Settings", icon="⚙️")
init_session_state()

kb = get_knowledge_base()
render_sidebar(kb)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="rm-navbar rm-animate-fade-in">
        <div class="rm-navbar-brand">⚙️ Settings</div>
        <div class="rm-navbar-right">
            <span>Configure your research environment</span>
            <div class="rm-avatar">R</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

configured = set(available_providers())

# ── LLM Provider ──────────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">🤖 Language Model</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="rm-card">', unsafe_allow_html=True)

    providers = ["groq", "openai", "anthropic", "gemini"]
    labels = {p: f"{p.capitalize()} {'✅' if p in configured else '⚠️ no key'}" for p in providers}
    current_idx = providers.index(st.session_state.get("llm_provider", settings.llm_provider))

    provider = st.selectbox(
        "LLM Provider",
        options=providers,
        index=current_idx,
        format_func=lambda p: labels[p],
    )
    st.session_state["llm_provider"] = provider

    if provider not in configured:
        st.warning(
            f"No API key for **{provider}**. Add `{provider.upper()}_API_KEY` to your `.env` and restart.",
            icon="⚠️",
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ── Generation Parameters ─────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">🎛️ Generation Parameters</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="rm-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.session_state["temperature"] = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=float(st.session_state.get("temperature", settings.temperature)),
            step=0.05,
            help="Higher = more creative. Lower = more precise.",
        )
    with col2:
        st.session_state["top_k"] = st.slider(
            "Top-K Retrieval",
            min_value=1, max_value=10,
            value=int(st.session_state.get("top_k", settings.top_k)),
            help="Number of document chunks retrieved per question.",
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Appearance ────────────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">🎨 Appearance</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="rm-card">', unsafe_allow_html=True)
    st.session_state["dark_mode"] = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.get("dark_mode", False),
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Knowledge Base Info ───────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">📊 Knowledge Base</div>', unsafe_allow_html=True)
with st.container():
    st.markdown('<div class="rm-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("Documents", len(kb.documents()))
    col2.metric("Chunks", kb.store.chunk_count())
    st.caption(f"Embedding model: `{settings.embedding_model_name}` · Dimension: {kb.embedder.dimension}")
    st.caption(f"Chunk size: {settings.chunk_size} chars · Overlap: {settings.chunk_overlap} chars · Threshold: {settings.similarity_threshold}")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Reset ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔄 Reset to Defaults", use_container_width=False):
    st.session_state["temperature"] = settings.temperature
    st.session_state["top_k"] = settings.top_k
    st.session_state["llm_provider"] = settings.llm_provider
    st.session_state["dark_mode"] = False
    st.success("Settings reset to defaults.", icon="✅")

render_footer()
