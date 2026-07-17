"""
config.py
=========
Central configuration for ResearchMind AI.

All tunable settings live here (or are pulled from environment variables via
`.env`). Keeping configuration in one module makes the rest of the codebase
easy to reason about and test.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a local .env file (if present) into os.environ.
load_dotenv()

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_documents"
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
ANSWERS_DIR = OUTPUTS_DIR / "answers"
PROMPTS_DIR = BASE_DIR / "prompts"
DATABASE_PATH = BASE_DIR / "database" / "history.db"

for _dir in (UPLOAD_DIR, PROCESSED_DIR, EMBEDDINGS_DIR, SAMPLE_DOCS_DIR,
             REPORTS_DIR, ANSWERS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    """Runtime-tunable settings for the app.

    Most values can be overridden from the Settings page in the UI
    (stored in `st.session_state`) or from environment variables at
    startup. This dataclass provides the defaults.
    """

    # --- LLM provider ------------------------------------------------ #
    # One of: "openai", "anthropic", "gemini", "groq"
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")

    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    temperature: float = _env_float("LLM_TEMPERATURE", 0.2)
    max_tokens: int = _env_int("LLM_MAX_TOKENS", 800)

    # --- Embeddings / retrieval --------------------------------------- #
    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    chunk_size: int = _env_int("CHUNK_SIZE", 800)          # characters
    chunk_overlap: int = _env_int("CHUNK_OVERLAP", 150)     # characters
    top_k: int = _env_int("TOP_K", 4)
    similarity_threshold: float = _env_float("SIMILARITY_THRESHOLD", 0.15)

    # --- App metadata --------------------------------------------------- #
    app_name: str = "ResearchMind AI"
    app_tagline: str = "Ask your documents anything. Get grounded, cited answers."
    theme_primary: str = "#2563EB"
    theme_secondary: str = "#7C3AED"
    theme_success: str = "#10B981"
    theme_warning: str = "#F59E0B"
    theme_background: str = "#F8FAFC"
    theme_text: str = "#111827"

    supported_extensions: tuple = field(
        default_factory=lambda: (".pdf", ".docx", ".txt", ".md", ".markdown")
    )


settings = Settings()
