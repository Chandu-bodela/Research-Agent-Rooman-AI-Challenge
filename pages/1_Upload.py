"""
pages/1_Upload.py — Premium document upload & management page.
"""
from __future__ import annotations
import streamlit as st
from frontend.common import configure_page, get_knowledge_base, init_session_state
from frontend.components.footer import render_footer
from frontend.components.sidebar import render_sidebar
from frontend.components.uploader import render_uploader

configure_page("Documents", icon="📄")
init_session_state()

kb = get_knowledge_base()
render_sidebar(kb)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="rm-navbar rm-animate-fade-in">
        <div class="rm-navbar-brand">📄 Documents</div>
        <div class="rm-navbar-right">
            <span>Upload &amp; manage your research files</span>
            <div class="rm-avatar">R</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Uploader ──────────────────────────────────────────────────────────────────
render_uploader(kb)

# ── Document Library ──────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">📚 Knowledge Base</div>', unsafe_allow_html=True)

docs = kb.documents()
stats = kb.stats()

if not docs:
    st.markdown(
        """
        <div class="rm-empty rm-animate-fade-in">
            <span class="rm-empty-icon">📭</span>
            <div class="rm-empty-title">No documents yet</div>
            <div class="rm-empty-sub">Upload a file above, or try the samples in
                <code>data/sample_documents/</code></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Grid: 3 columns
    ext_icons = {".pdf": "📕", ".docx": "📘", ".txt": "📄", ".md": "📝", ".markdown": "📝"}
    cols = st.columns(3)
    for i, name in enumerate(docs):
        ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
        icon = ext_icons.get(ext, "📄")
        chunks = stats.get(name, 0)

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="rm-doc-card rm-animate-fade-up">
                    <div class="rm-doc-icon">{icon}</div>
                    <div class="rm-doc-name">{name}</div>
                    <div class="rm-doc-meta">{chunks} chunks indexed</div>
                    <span class="rm-doc-badge">✅ Indexed</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🗑️ Remove", key=f"rm_{name}", use_container_width=True):
                with st.spinner(f"Removing {name}…"):
                    kb.remove_document(name)
                st.rerun()

st.divider()
st.caption("💡 Tip: Use the sample documents in `data/sample_documents/` to try the app instantly.")

render_footer()
