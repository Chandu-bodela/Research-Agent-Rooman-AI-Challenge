"""
pages/3_History.py — Premium timeline history page.
"""
from __future__ import annotations
import streamlit as st
from backend.citations import Citation
from backend.export import export_to_markdown, export_to_pdf
from database.history import clear_history, delete_entry, get_history, init_db
from frontend.common import configure_page, get_knowledge_base, init_session_state
from frontend.components.footer import render_footer
from frontend.components.sidebar import render_sidebar

configure_page("History", icon="🕒")
init_session_state()
init_db()

kb = get_knowledge_base()
render_sidebar(kb)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="rm-navbar rm-animate-fade-in">
        <div class="rm-navbar-brand">🕒 Research History</div>
        <div class="rm-navbar-right">
            <span>All your past questions &amp; answers</span>
            <div class="rm-avatar">R</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

entries = get_history(limit=200)

# Header row
hcol1, hcol2 = st.columns([5, 1])
hcol1.markdown(f'<div class="rm-section-header">📋 {len(entries)} saved question(s)</div>', unsafe_allow_html=True)
with hcol2:
    if st.button("🗑️ Clear all", disabled=not entries, use_container_width=True):
        clear_history()
        st.rerun()

if not entries:
    st.markdown(
        """
        <div class="rm-empty rm-animate-fade-in">
            <span class="rm-empty-icon">🕒</span>
            <div class="rm-empty-title">No history yet</div>
            <div class="rm-empty-sub">Ask a question on the Chat page — it will appear here automatically.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for entry in entries:
        st.markdown(
            f"""
            <div class="rm-history-item rm-animate-fade-up">
                <div class="rm-history-q">❓ {entry.question}</div>
                <div class="rm-history-a">{entry.answer[:300]}{"…" if len(entry.answer) > 300 else ""}</div>
                <div class="rm-history-meta">
                    🕐 {entry.created_at} &nbsp;·&nbsp;
                    🤖 {entry.provider} &nbsp;·&nbsp;
                    📎 {len(entry.citations)} source(s)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 1, 1])
        citation_objs = [Citation(**c) for c in entry.citations] if entry.citations else []

        with col1:
            if st.button("📝 Export MD", key=f"md_{entry.id}", use_container_width=True):
                path = export_to_markdown(entry.question, entry.answer, citation_objs)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download", f, file_name=path.name,
                                       mime="text/markdown", key=f"dl_md_{entry.id}")
        with col2:
            if st.button("📄 Export PDF", key=f"pdf_{entry.id}", use_container_width=True):
                path = export_to_pdf(entry.question, entry.answer, citation_objs)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download", f, file_name=path.name,
                                       mime="application/pdf", key=f"dl_pdf_{entry.id}")
        with col3:
            if st.button("🗑️ Delete", key=f"del_{entry.id}", use_container_width=True):
                delete_entry(entry.id)
                st.rerun()

        if entry.citations:
            with st.expander(f"📎 View {len(entry.citations)} source(s)"):
                for c in entry.citations:
                    st.markdown(
                        f"- **[{c.get('label','?')}]** {c.get('document_name','?')} "
                        f"— Page {c.get('page_number','?')} "
                        f"({c.get('score', 0):.0%} relevance)"
                    )

render_footer()
