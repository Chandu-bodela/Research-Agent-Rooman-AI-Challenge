"""
pages/2_Chat.py — Premium ChatGPT-style research chat page.
"""
from __future__ import annotations
import streamlit as st
from backend.citations import (
    build_citations, build_context_block,
    filter_citations_to_used, is_not_found_answer,
)
from backend.export import export_to_markdown, export_to_pdf
from backend.llm import LLMError, generate_answer
from config import PROMPTS_DIR
from database.history import add_entry, init_db
from frontend.common import configure_page, get_knowledge_base, init_session_state
from frontend.components.chatbox import render_conversation
from frontend.components.citation_card import render_not_found_banner
from frontend.components.footer import render_footer
from frontend.components.sidebar import render_sidebar

configure_page("Chat", icon="💬")
init_session_state()
init_db()

kb = get_knowledge_base()
render_sidebar(kb)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="rm-navbar rm-animate-fade-in">
        <div class="rm-navbar-brand">💬 Research Chat</div>
        <div class="rm-navbar-right">
            <span>Ask anything about your documents</span>
            <div class="rm-avatar">R</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Empty KB warning ──────────────────────────────────────────────────────────
if kb.is_empty():
    st.markdown(
        """
        <div class="rm-dashboard-card">
            <div class="rm-section-header">📤 Start with a document</div>
            <div style="color:#6B7280; font-size:0.95rem;">Upload a PDF, DOCX, TXT, or Markdown file first so the chat workspace has content to search.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="rm-dashboard-card">
            <div class="rm-section-header">🗂️ Workspace status</div>
            <div style="color:#6B7280; font-size:0.95rem;">Your knowledge base is ready. Ask a question to retrieve the best passages and get a cited answer.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Suggested prompts ───────────────────────────────────────────────────────
if not st.session_state["chat_messages"] and not kb.is_empty():
    prompt_examples = [
        "Summarize this document in three bullet points",
        "What is the main takeaway?",
        "List the key decisions mentioned in the file",
    ]
    st.markdown(
        """
        <div class="rm-dashboard-card rm-inline-card">
            <div class="rm-section-header">💡 Try a prompt</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(len(prompt_examples))
    for col, example in zip(cols, prompt_examples):
        with col:
            if st.button(example, use_container_width=True, key=f"prompt_{example}"):
                st.session_state["chat_messages"].append({"role": "user", "content": example})
                st.rerun()

# ── Conversation ──────────────────────────────────────────────────────────────
render_conversation(st.session_state["chat_messages"])

# ── Chat Input ────────────────────────────────────────────────────────────────
question = st.chat_input("Ask anything about your documents…")

if question:
    st.session_state["chat_messages"].append({"role": "user", "content": question})

    with st.spinner("🔎 Searching your documents…"):
        retrieved = kb.retrieve(question, top_k=st.session_state.get("top_k"))

    if not retrieved:
        answer_text = "I couldn't find this in the uploaded documents."
        citations, not_found = [], True
    else:
        context = build_context_block(retrieved)
        system_prompt = (PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8")
        template = (PROMPTS_DIR / "citation_prompt.txt").read_text(encoding="utf-8")
        user_prompt = template.format(question=question, context=context)

        try:
            with st.spinner("🤖 Generating answer…"):
                answer_text = generate_answer(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    provider=st.session_state.get("llm_provider"),
                    temperature=st.session_state.get("temperature"),
                )
        except LLMError as exc:
            answer_text = f"⚠️ {exc}"
            st.session_state["chat_messages"].append(
                {"role": "assistant", "content": answer_text, "citations": [], "not_found": False}
            )
            st.rerun()

        not_found = is_not_found_answer(answer_text)
        all_cits = build_citations(retrieved)
        citations = [] if not_found else filter_citations_to_used(all_cits, answer_text)

    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": answer_text, "citations": citations, "not_found": not_found}
    )
    add_entry(
        question=question,
        answer=answer_text,
        citations=[c.__dict__ for c in citations],
        provider=st.session_state.get("llm_provider", "unknown"),
    )
    st.rerun()

# ── Export last answer ────────────────────────────────────────────────────────
messages = st.session_state["chat_messages"]
if messages and messages[-1]["role"] == "assistant":
    last_a = messages[-1]
    last_q = messages[-2]["content"] if len(messages) >= 2 else ""

    st.divider()
    st.markdown('<div class="rm-section-header" style="font-size:1rem;">📥 Export last answer</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("📝 Markdown", use_container_width=True):
            path = export_to_markdown(last_q, last_a["content"], last_a.get("citations", []))
            with open(path, "rb") as f:
                st.download_button("⬇️ Download .md", f, file_name=path.name, mime="text/markdown")
    with col2:
        if st.button("📄 PDF", use_container_width=True):
            path = export_to_pdf(last_q, last_a["content"], last_a.get("citations", []))
            with open(path, "rb") as f:
                st.download_button("⬇️ Download .pdf", f, file_name=path.name, mime="application/pdf")
    with col3:
        if st.button("🗑️ Clear chat", use_container_width=False):
            st.session_state["chat_messages"] = []
            st.rerun()

render_footer()
