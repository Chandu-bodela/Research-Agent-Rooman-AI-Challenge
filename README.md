# 🧠 ResearchMind AI

**An intelligent Retrieval-Augmented Generation (RAG) research assistant that answers questions using *only* your uploaded documents — and always shows its sources.**

Upload PDFs, Word docs, text files, or Markdown notes. Ask questions in plain English. Get answers with inline citations pointing to the exact document and page — and if the answer isn't in your documents, ResearchMind AI says so instead of making something up.

Built for the **Rooman AI Challenge — Research Agent (with Citations)** track.

---

## ✨ Features

| Category | Features |
|---|---|
| **Ingestion** | Drag-and-drop upload of PDF, DOCX, TXT, and Markdown; automatic text extraction with page-level tracking |
| **RAG Pipeline** | Sentence-transformer embeddings (`all-MiniLM-L6-v2`) + FAISS vector search |
| **Grounded Answers** | Every claim tagged to its source `[S1]`, `[S2]`... rendered as citation cards (document + page + relevance) |
| **Anti-hallucination** | Similarity threshold filtering *and* an explicit "not found in documents" instruction — two independent safeguards |
| **Multi-LLM** | Works with OpenAI, Anthropic (Claude), Google Gemini, or Groq (Llama 3) — just set one API key |
| **Chat UI** | ChatGPT-style conversation interface with full history |
| **Export** | Download any answer + citations as Markdown or PDF |
| **History** | All Q&A turns persisted in SQLite, browsable and re-exportable |
| **Theming** | Light/dark mode, professional blue-and-purple design system |

---

## 🖥️ Screenshots

> Run the app locally and add your own screenshots to `docs/screenshots/` — see `docs/architecture.md` for the Mermaid diagrams used during design.

---

## 🏗️ Architecture

See [`docs/architecture.md`](docs/architecture.md) for full Mermaid diagrams (system architecture, RAG workflow, and citation sequence diagram). High-level flow:

```
Upload → Extract Text → Chunk → Embed → FAISS Index
                                            │
User Question → Embed Query → Similarity Search ──┘
                                            │
                              Labeled Context [S1][S2]...
                                            │
                                    LLM (cited answer)
                                            │
                          Parse citations → Display → Save to history
```

---

## 📁 Project Structure

```
ResearchMind-AI/
├── app.py                      # Streamlit entry point (Landing page)
├── config.py                   # Central settings (env-driven)
├── requirements.txt
├── .env.example
├── pytest.ini
│
├── pages/                      # Streamlit multipage app
│   ├── 1_Upload.py
│   ├── 2_Chat.py
│   ├── 3_History.py
│   └── 4_Settings.py
│
├── backend/
│   ├── loader.py                # Save uploads to disk
│   ├── parser.py                # PDF/DOCX/TXT/MD → text (page-aware)
│   ├── chunker.py                # Overlapping chunk splitter
│   ├── embeddings.py             # sentence-transformers wrapper
│   ├── vector_store.py           # FAISS index wrapper + persistence
│   ├── retriever.py              # KnowledgeBase: ingest + retrieve
│   ├── citations.py              # Context building + citation parsing
│   ├── llm.py                    # Multi-provider LLM client
│   ├── summarizer.py              # Cited summaries + keyword extraction
│   ├── export.py                  # Markdown / PDF export
│   └── utils.py
│
├── database/
│   └── history.py                # SQLite conversation history
│
├── frontend/
│   ├── common.py                 # Page config, CSS injection, cached KB
│   └── components/
│       ├── sidebar.py
│       ├── chatbox.py
│       ├── uploader.py
│       ├── citation_card.py
│       └── footer.py
│
├── prompts/
│   ├── system_prompt.txt
│   ├── citation_prompt.txt
│   └── summary_prompt.txt
│
├── assets/css/style.css          # Design system (blue/purple theme)
├── data/
│   ├── uploads/                  # Saved raw uploads
│   ├── processed/
│   ├── embeddings/                # Persisted FAISS index + metadata
│   └── sample_documents/          # Ready-to-use demo files
├── outputs/{reports,answers}/     # Exported files land here
├── docs/architecture.md           # Mermaid diagrams
└── tests/                         # pytest unit tests
```

---

## 🚀 Setup & Installation

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url> ResearchMind-AI
cd ResearchMind-AI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** you don't need every LLM SDK's API key — only the provider you plan to use.
> The first run will also download the `all-MiniLM-L6-v2` embedding model (~80MB) from
> Hugging Face; this requires an internet connection once, after which it's cached locally.

### 3. Configure your API key

```bash
cp .env.example .env
```

Edit `.env` and set **one** provider:

```dotenv
LLM_PROVIDER=groq          # or: openai | anthropic | gemini
GROQ_API_KEY=your_key_here
```

| Provider | Get a key | Notes |
|---|---|---|
| Groq | https://console.groq.com | Fast, generous free tier — recommended for quick demos |
| OpenAI | https://platform.openai.com | `gpt-4o-mini` default |
| Anthropic | https://console.anthropic.com | `claude-sonnet-5` default |
| Gemini | https://aistudio.google.com | `gemini-1.5-flash` default |

### 4. Run the app

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

### 5. Try it out

1. Go to **Upload** and drag in a file — or use the bundled samples in `data/sample_documents/`
   (`company_handbook.md`, `market_research_notes.txt`, `warranty_policy.pdf`, `engineering_onboarding.docx`).
2. Go to **Chat** and ask a question (see examples below).
3. Check the citation cards under the answer, then try **Export as PDF/Markdown**.
4. Visit **History** to see every past Q&A, and **Settings** to switch providers or tune retrieval.

---

## 💬 Example Questions & Expected Answers

Using the bundled sample documents:

| Question | Expected behavior |
|---|---|
| "How many PTO days do employees accrue per month?" | Cites `company_handbook.md`, page 1 — "1.5 days per completed month..." |
| "What's the extended warranty cost?" | Cites `warranty_policy.pdf`, page 1 — "12% of the original product price" |
| "How fast did NPS improve in Q1 2026?" | Cites `market_research_notes.txt` — "+24 to +31" |
| "What's the on-call stipend for engineers?" | Cites `engineering_onboarding.docx` — "$200 stipend per week" |
| "What is the company's stock ticker symbol?" | Responds: *"I couldn't find this in the uploaded documents."* (correctly refuses to hallucinate) |

---

## 🧪 Running Tests

```bash
pytest
```

Covers chunking (boundary conditions, page-number preservation), parsing (all four
file types, error handling), and citation logic (labeling, filtering, the "not found"
heuristic).

---

## ⚙️ Configuration Reference

All settings can be set via `.env` (see `.env.example`) or tuned live from the **Settings** page:

| Setting | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `openai` \| `anthropic` \| `gemini` \| `groq` |
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between consecutive chunks |
| `TOP_K` | `4` | Chunks retrieved per question |
| `SIMILARITY_THRESHOLD` | `0.15` | Minimum cosine similarity to include a chunk |
| `LLM_TEMPERATURE` | `0.2` | Lower = more literal/grounded answers |

---

## 🎯 Design Decisions & Tradeoffs

**Why FAISS `IndexFlatIP` instead of ChromaDB or an approximate index?**
Exact search is plenty fast at the scale a 24-hour hackathon project realistically handles
(hundreds to low-thousands of chunks) and needs zero index-tuning. It also normalizes
embeddings at write time so inner product == cosine similarity, keeping the math simple.
Tradeoff: won't scale gracefully past ~100K+ chunks without moving to HNSW/IVF or ChromaDB.

**Why character-window chunking instead of a semantic/recursive splitter?**
It's fast, dependency-light, and — combined with sentence-boundary snapping and overlap —
good enough to keep most claims intact within a single chunk. Tradeoff: it can still split
a table or a long multi-clause sentence awkwardly; a production system would use a
structure-aware splitter (e.g. per-heading for Markdown, per-cell for tables).

**Why two anti-hallucination layers (threshold + prompt instruction) instead of one?**
A similarity threshold alone can still let borderline-irrelevant chunks through; a prompt
instruction alone can still be ignored by weaker models. Combining both is cheap and
meaningfully reduces the chance of a confidently wrong answer — which matters most for a
"citations" product where trust is the entire value proposition.

**Why store history in SQLite instead of just session state?**
Session state disappears on refresh. SQLite persistence means the History page actually
demonstrates value across sessions, and it's a five-line dependency-free addition.

**What's not implemented (documented honestly rather than hidden):**
- OCR for scanned/image-only PDFs (dependency on system Tesseract; stubbed as a bonus).
- Voice question input (SpeechRecognition is in `requirements.txt` but not wired into the UI).
- Multi-document comparison mode and mind-map generation (listed as bonus features in the
  brief; out of scope for the 24-hour core build).
- True incremental FAISS deletion — removing a document currently rebuilds the index from
  the remaining chunks rather than deleting in place (fine at this scale, not at large scale).

**What we'd improve with more time:**
- Swap to ChromaDB or FAISS HNSW for larger document sets.
- Structure-aware chunking (respect Markdown headings, table boundaries).
- Streaming LLM responses for a snappier chat feel.
- Per-document confidence/AI-certainty score surfaced in the UI.
- Multi-document comparison and mind-map bonus features from the brief.

---

## 🧰 Tech Stack

- **Frontend:** Streamlit (multipage app, custom CSS design system)
- **Backend:** Python 3.11+
- **Parsing:** PyMuPDF (PDF), python-docx (DOCX), `markdown` (MD)
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`)
- **Vector Store:** FAISS (`IndexFlatIP`)
- **LLM:** OpenAI / Anthropic / Gemini / Groq (pluggable)
- **Database:** SQLite (conversation history)
- **Export:** fpdf2 (PDF), native Markdown

---

## 📄 License

Built for the Rooman Technologies AI Challenge. Free to use and adapt for learning purposes.
