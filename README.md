# 🧠 ResearchMind AI

> **AI-powered research assistant that answers questions from your documents with verified citations.**
> Built for the Rooman AI Challenge.

![Python](https://img.shields.io/badge/Python-3.10--3.12-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-red?style=flat-square&logo=streamlit)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## 🚀 What is ResearchMind AI?

ResearchMind AI is a **Retrieval-Augmented Generation (RAG)** research assistant that lets you upload your own documents and ask questions in plain English. Every answer is grounded in your documents and comes with **exact citations** — document name, page number, and the matching excerpt.

No hallucinations. No guessing. Just cited, verifiable answers.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Multi-format ingestion** | Upload PDF, DOCX, TXT, and Markdown files |
| 🧩 **Smart chunking** | Overlapping, semantically coherent text chunks |
| 🧠 **Local embeddings** | `all-MiniLM-L6-v2` via sentence-transformers — free, fast, offline |
| ⚡ **FAISS vector search** | Sub-second semantic search over your entire document set |
| 🔗 **Always-cited answers** | Every claim tagged to its source document and page |
| 🚫 **No hallucinations** | Says "not found" instead of guessing |
| 💬 **ChatGPT-style UI** | Familiar chat interface with full conversation history |
| 📊 **Analytics dashboard** | Questions asked, documents indexed, provider usage charts |
| 📥 **Export findings** | Download answers with citations as Markdown or PDF |
| 🌙 **Dark mode** | Toggle between light and dark themes |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit + Custom CSS (Inter/Poppins, glassmorphism) |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **Vector Store** | FAISS (IndexFlatIP — cosine similarity) |
| **Document Parsing** | PyMuPDF (PDF), python-docx (DOCX), built-in (TXT/MD) |
| **LLM Providers** | OpenAI, Anthropic Claude, Google Gemini, Groq |
| **Database** | SQLite (conversation history) |
| **Export** | fpdf2 (PDF), Markdown |
| **Analytics** | Plotly |

---

## 📁 Project Structure

```
ResearchMind-AI/
├── app.py                      # Home page (entry point)
├── config.py                   # Central configuration
├── requirements.txt
├── .env.example                # Environment variable template
│
├── pages/
│   ├── 1_Upload.py             # Document upload & management
│   ├── 2_Chat.py               # Research chat interface
│   ├── 3_History.py            # Conversation history
│   ├── 4_Analytics.py          # Usage analytics dashboard
│   └── 5_Settings.py           # LLM & retrieval settings
│
├── backend/
│   ├── parser.py               # PDF/DOCX/TXT/MD text extraction
│   ├── chunker.py              # Overlapping text chunking
│   ├── embeddings.py           # sentence-transformers wrapper
│   ├── vector_store.py         # FAISS index + metadata
│   ├── retriever.py            # KnowledgeBase (ingest + retrieve)
│   ├── citations.py            # Citation building & filtering
│   ├── llm.py                  # Multi-provider LLM interface
│   ├── summarizer.py           # Document summarization
│   └── export.py               # Markdown & PDF export
│
├── frontend/
│   ├── common.py               # Page config, CSS injection
│   └── components/
│       ├── sidebar.py          # Navigation sidebar
│       ├── chatbox.py          # Chat bubble renderer
│       ├── citation_card.py    # Citation cards with score bars
│       ├── uploader.py         # Drag-and-drop uploader
│       └── footer.py           # Shared footer
│
├── assets/css/style.css        # Complete custom theme
├── database/history.py         # SQLite history layer
├── prompts/                    # LLM prompt templates
└── data/
    ├── sample_documents/       # Ready-to-use sample files
    ├── uploads/                # Uploaded files (gitignored)
    └── embeddings/             # FAISS index (gitignored)
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Chandu-bodela/Research-Agent-Rooman-AI-Challenge.git
cd Research-Agent-Rooman-AI-Challenge
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```
> Requires **Python 3.10–3.12** for pre-built `faiss-cpu` and `PyMuPDF` wheels.

### 4. Set up your API key
```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Open `.env` and add your key — **you only need one provider**:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
```
> 🆓 Groq is free at [console.groq.com](https://console.groq.com) — no credit card needed.

### 5. Run the app
```bash
# Windows (recommended — uses venv directly)
venv\Scripts\streamlit.exe run app.py

# Mac/Linux
streamlit run app.py
```

Opens at **http://localhost:8501**

> First launch downloads the embedding model (~80MB). Internet required once.

---

## 🎯 How to Use

1. **Upload** — Go to Documents, drag in a PDF/DOCX/TXT/MD file (or use the samples in `data/sample_documents/`)
2. **Wait** — The app extracts text, chunks it, embeds it, and indexes it into FAISS
3. **Ask** — Go to Research Chat, type a question about your document
4. **Read** — Get a cited answer with source cards showing document, page, and matching excerpt
5. **Export** — Download the answer as Markdown or PDF
6. **Review** — Check History for all past Q&A sessions

---

## 🔄 How It Works

```
Upload → Extract Text → Chunk → Embed → FAISS Index
                                              ↓
Ask Question → Embed Query → Vector Search → Top-K Chunks
                                              ↓
                              LLM (with context) → Cited Answer
```

---

## 🤖 Supported LLM Providers

| Provider | Model | Notes |
|---|---|---|
| **Groq** | `llama-3.1-8b-instant` | ✅ Free tier, fastest |
| **OpenAI** | `gpt-4o-mini` | Paid |
| **Anthropic** | `claude-sonnet` | Paid |
| **Google Gemini** | `gemini-1.5-flash` | Free tier available |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: dotenv` | Run with `venv\Scripts\streamlit.exe run app.py` not system Python |
| `faiss-cpu` install fails | Use Python 3.10–3.12 |
| Port 8501 in use | Add `--server.port 8502` |
| "No documents" in chat | Upload a file on the Documents page first |
| LLM ⚠️ warning | Add your API key to `.env` |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
    Built with ❤️ using Streamlit · sentence-transformers · FAISS · Groq<br>
    <strong>ResearchMind AI — Rooman AI Challenge 2025</strong>
</div>
