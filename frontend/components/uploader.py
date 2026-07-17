"""
frontend/components/uploader.py — Premium drag-and-drop uploader.
"""
from __future__ import annotations
import streamlit as st
from backend.loader import InvalidFileTypeError, save_uploaded_file
from backend.parser import ParsingError, UnsupportedFileTypeError
from backend.retriever import KnowledgeBase


def render_uploader(kb: KnowledgeBase) -> None:
    # Upload zone header
    st.markdown(
        """
        <div class="rm-upload-zone">
            <span class="rm-upload-icon">📂</span>
            <div class="rm-upload-title">Drop your documents here</div>
            <div class="rm-upload-sub">or click below to browse files</div>
            <div style="margin-top:0.75rem;">
                <span class="rm-format-badge">PDF</span>
                <span class="rm-format-badge">DOCX</span>
                <span class="rm-format-badge">TXT</span>
                <span class="rm-format-badge">Markdown</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf", "docx", "txt", "md", "markdown"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if not uploaded_files:
        return

    already_ingested = st.session_state.get("ingested_hashes", set())

    for uploaded in uploaded_files:
        file_bytes = uploaded.getvalue()
        size_kb = len(file_bytes) / 1024
        size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"

        with st.status(f"Processing **{uploaded.name}** ({size_str})…", expanded=False) as status:
            try:
                saved = save_uploaded_file(file_bytes, uploaded.name)

                if saved.content_hash in already_ingested:
                    status.update(label=f"⏭️ {uploaded.name} — already indexed", state="complete")
                    continue

                status.write("✂️ Extracting text and chunking…")
                num_chunks = kb.ingest_document(saved.path, display_name=uploaded.name)

                if num_chunks == 0:
                    status.update(label=f"⚠️ No text found in {uploaded.name}", state="error")
                    continue

                already_ingested.add(saved.content_hash)
                st.session_state["ingested_hashes"] = already_ingested
                status.write(f"🧠 Embedded {num_chunks} chunks into vector store…")
                status.update(label=f"✅ {uploaded.name} — {num_chunks} chunks indexed", state="complete")

            except (InvalidFileTypeError, UnsupportedFileTypeError, ParsingError) as exc:
                status.update(label=f"❌ {uploaded.name}: {exc}", state="error")
            except Exception as exc:  # noqa: BLE001
                status.update(label=f"❌ {uploaded.name}: unexpected error — {exc}", state="error")
