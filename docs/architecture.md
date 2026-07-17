# ResearchMind AI — Architecture

## 1. System Architecture

```mermaid
flowchart TB
    subgraph Client["Browser"]
        UI[Streamlit UI]
    end

    subgraph App["ResearchMind AI — Streamlit App"]
        Home[Landing Page<br/>app.py]
        Upload[Upload Page<br/>pages/1_Upload.py]
        Chat[Chat Page<br/>pages/2_Chat.py]
        History[History Page<br/>pages/3_History.py]
        Settings[Settings Page<br/>pages/4_Settings.py]

        subgraph Backend["backend/"]
            Loader[loader.py<br/>Save uploads]
            Parser[parser.py<br/>PDF/DOCX/TXT/MD → text]
            Chunker[chunker.py<br/>Overlapping chunks]
            Embeddings[embeddings.py<br/>sentence-transformers]
            VectorStore[vector_store.py<br/>FAISS index]
            Retriever[retriever.py<br/>KnowledgeBase]
            Citations[citations.py<br/>Context + citation build]
            LLM[llm.py<br/>OpenAI/Claude/Gemini/Groq]
            Export[export.py<br/>Markdown + PDF export]
        end

        DB[(SQLite<br/>database/history.py)]
    end

    UI --> Home & Upload & Chat & History & Settings
    Upload --> Loader --> Parser --> Chunker --> Embeddings --> VectorStore
    Chat --> Retriever
    Retriever --> VectorStore
    Retriever --> Embeddings
    Chat --> Citations --> LLM
    LLM --> Chat
    Chat --> DB
    History --> DB
    Chat --> Export
    History --> Export
```

## 2. Retrieval-Augmented Generation Workflow

```mermaid
flowchart LR
    A[Upload Document] --> B[Extract Text<br/>PyMuPDF / python-docx]
    B --> C[Chunk Text<br/>~800 chars, 150 overlap]
    C --> D[Generate Embeddings<br/>all-MiniLM-L6-v2]
    D --> E[(FAISS Vector Store)]

    F[User Question] --> G[Embed Query]
    G --> H[Similarity Search<br/>top-k chunks]
    E --> H
    H --> I{Any chunks above<br/>similarity threshold?}
    I -- No --> J["'Not found in documents' response"]
    I -- Yes --> K[Build labeled context<br/>S1, S2, S3...]
    K --> L[LLM Call<br/>with citation instructions]
    L --> M[Parse citation labels<br/>from answer]
    M --> N[Render answer +<br/>citation cards]
    N --> O[(Save to SQLite history)]
```

## 3. Data Flow: Citation Grounding

```mermaid
sequenceDiagram
    participant U as User
    participant C as Chat Page
    participant R as Retriever
    participant V as FAISS Store
    participant L as LLM Provider
    participant D as SQLite History

    U->>C: Ask question
    C->>R: retrieve(question, top_k)
    R->>V: search(query_vector)
    V-->>R: [(chunk, score), ...]
    R-->>C: RetrievedChunk list (score >= threshold)
    alt No chunks above threshold
        C-->>U: "I couldn't find this in the uploaded documents."
    else Chunks found
        C->>C: build_context_block() -> [S1] [S2] ...
        C->>L: system_prompt + question + labeled context
        L-->>C: answer text with [S#] tags
        C->>C: filter_citations_to_used()
        C-->>U: Answer + citation cards
        C->>D: save(question, answer, citations)
    end
```

## Component Responsibilities

| Layer | Module(s) | Responsibility |
|---|---|---|
| Ingestion | `loader.py`, `parser.py` | Save uploads, extract text + page numbers |
| Processing | `chunker.py` | Split text into overlapping, retrievable chunks |
| Indexing | `embeddings.py`, `vector_store.py` | Vectorize chunks, store/search in FAISS |
| Retrieval | `retriever.py` | Orchestrate ingest + retrieve, own persistence |
| Grounding | `citations.py` | Build labeled prompt context, parse/verify citations |
| Reasoning | `llm.py` | Provider-agnostic LLM call (OpenAI/Claude/Gemini/Groq) |
| Persistence | `database/history.py` | SQLite conversation history |
| Export | `export.py` | Markdown / PDF export of any answer |
| Presentation | `app.py`, `pages/*.py`, `frontend/*` | Streamlit UI, components, theming |

## Why these design choices

- **FAISS `IndexFlatIP` over HNSW/IVF**: exact search is fast enough at hackathon scale
  (hundreds to low thousands of chunks) and avoids tuning approximate-search parameters
  under time pressure. Documented as a scaling tradeoff in the README.
- **Page-level provenance carried from parser → chunk → citation**: this is what makes
  citations trustworthy ("Document X, Page Y") instead of just naming the file.
- **Similarity threshold + explicit "not found" instruction** (belt-and-suspenders):
  chunks below the threshold are dropped before they ever reach the prompt, *and* the
  system prompt instructs the model to say so explicitly — reducing hallucination risk
  from two independent angles.
- **Provider-agnostic LLM layer**: judges/reviewers can run the project with whichever
  of OpenAI, Anthropic, Gemini, or Groq they already have a key for, with zero code changes.
