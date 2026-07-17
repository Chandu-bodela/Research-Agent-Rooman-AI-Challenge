"""
app.py — ResearchMind AI Home Page
Run with: streamlit run app.py
"""
from __future__ import annotations
import streamlit as st
from backend.llm import available_providers
from frontend.common import configure_page, get_knowledge_base, init_session_state
from frontend.components.footer import render_footer
from frontend.components.sidebar import render_sidebar

configure_page("Home", icon="🧠")
init_session_state()

kb = get_knowledge_base()
render_sidebar(kb)

# ── Navbar ──────────────────────────────────────────────────────────────────
providers = available_providers()
provider_status = f"✅ {', '.join(providers)}" if providers else "⚠️ No API key"

st.markdown(
    f"""
    <div class="rm-navbar rm-animate-fade-in">
        <div class="rm-navbar-brand">🧠 ResearchMind AI</div>
        <div class="rm-navbar-right">
            <span>Workspace: <strong>Default</strong></span>
            <span class="rm-badge rm-badge-{'success' if providers else 'warning'}">{provider_status}</span>
            <div class="rm-avatar">R</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Hero / Dashboard ───────────────────────────────────────────────────────
st.markdown(
    """
    <div class="rm-dashboard-shell">
        <div class="rm-dashboard-hero">
            <div>
                <span class="rm-pill">RAG · Vector Search · Cited Answers</span>
                <h1 style="margin:0.45rem 0 0.25rem 0; font-size:2rem;">Research Smarter with AI</h1>
                <p style="margin:0; color:#374151; max-width:600px;">Upload your documents, index them once, and ask grounded questions with citations in a simple workspace.</p>
            </div>
            <div class="rm-dashboard-actions">
                <span class="rm-pill">⚡ Fast setup</span>
                <span class="rm-pill">🔒 Grounded answers</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("📤 Upload Documents", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Upload.py")
with col2:
    if st.button("💬 Start Chatting", use_container_width=True):
        st.switch_page("pages/2_Chat.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Stats ────────────────────────────────────────────────────────────────────
docs = kb.documents()
stat_cols = st.columns(4)
stat_cols[0].markdown(
    "<div class='rm-dashboard-card'><div class='rm-section-header'>📄 Indexed Documents</div><div class='rm-metric-value'>" + str(len(docs)) + "</div></div>",
    unsafe_allow_html=True,
)
stat_cols[1].markdown(
    "<div class='rm-dashboard-card'><div class='rm-section-header'>🧩 Chunks Ready</div><div class='rm-metric-value'>" + str(kb.store.chunk_count()) + "</div></div>",
    unsafe_allow_html=True,
)
stat_cols[2].markdown(
    "<div class='rm-dashboard-card'><div class='rm-section-header'>🔎 Retrieval Top-K</div><div class='rm-metric-value'>" + str(st.session_state.get("top_k", 4)) + "</div></div>",
    unsafe_allow_html=True,
)
stat_cols[3].markdown(
    "<div class='rm-dashboard-card'><div class='rm-section-header'>🤖 Active Provider</div><div class='rm-metric-value'>" + str(st.session_state.get("llm_provider", "groq")).capitalize() + "</div></div>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Start ─────────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">🚀 Quick Start</div>', unsafe_allow_html=True)
quick_cols = st.columns(3)
with quick_cols[0]:
    st.markdown("<div class='rm-quick-action'><div class='rm-section-header'>📤 Upload content</div><div style='color:#6B7280;font-size:0.9rem;'>Add PDFs, DOCX, TXT, or Markdown files to build a searchable workspace.</div></div>", unsafe_allow_html=True)
with quick_cols[1]:
    st.markdown("<div class='rm-quick-action'><div class='rm-section-header'>💬 Ask a question</div><div style='color:#6B7280;font-size:0.9rem;'>Try prompts like “summarize this document” or “what are the main decisions?”.</div></div>", unsafe_allow_html=True)
with quick_cols[2]:
    st.markdown("<div class='rm-quick-action'><div class='rm-section-header'>🕘 Review history</div><div style='color:#6B7280;font-size:0.9rem;'>Every answer is saved for later export or re-checking.</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">✨ Features</div>', unsafe_allow_html=True)

features = [
    ("📄", "Document Intelligence", "Upload PDF, DOCX, TXT, and Markdown. Text extracted automatically with page numbers preserved."),
    ("🔗", "Citation Engine",        "Every answer is tagged to its exact source document and page — no hallucinations."),
    ("🔍", "Semantic Search",        "FAISS-powered vector search finds the most relevant passages in milliseconds."),
    ("🤖", "AI Summaries",           "Get concise, cited summaries of any document or topic in your knowledge base."),
    ("📥", "Export Reports",         "Download answers with full citations as Markdown or PDF with one click."),
]

cols = st.columns(len(features))
for col, (icon, title, desc) in zip(cols, features):
    with col:
        st.markdown(
            f"""
            <div class="rm-feature-card rm-animate-fade-up">
                <span class="rm-feature-icon">{icon}</span>
                <div class="rm-feature-title">{title}</div>
                <div class="rm-feature-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">🔄 How it works</div>', unsafe_allow_html=True)

steps = ["Upload", "Extract", "Chunk", "Embed", "Index", "Ask", "Retrieve", "Answer + Cite"]
cols = st.columns(len(steps))
for i, (col, step) in enumerate(zip(cols, steps)):
    with col:
        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="width:32px;height:32px;border-radius:50%;
                    background:linear-gradient(135deg,#2563EB,#7C3AED);
                    color:white;display:flex;align-items:center;justify-content:center;
                    margin:0 auto 6px;font-weight:700;font-size:0.8rem;">{i+1}</div>
                <div style="font-size:0.75rem;color:#374151;font-weight:500;">{step}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

render_footer()
