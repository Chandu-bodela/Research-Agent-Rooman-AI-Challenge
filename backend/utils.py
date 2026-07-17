"""
backend/utils.py
=================
Small, shared helper functions used across the backend: logging setup,
hashing, id generation, and safe-filename utilities.
"""

from __future__ import annotations

import hashlib
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """Return a configured module-level logger.

    Using one helper keeps log formatting consistent across the whole
    backend instead of every module rolling its own ``basicConfig`` call.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def safe_filename(filename: str) -> str:
    """Strip characters that are unsafe for filesystem paths."""
    name = re.sub(r"[^\w\-.]", "_", filename)
    return name[:200]  # avoid absurdly long paths


def file_hash(file_bytes: bytes) -> str:
    """Return a short, stable hash for a file's contents.

    Used to detect duplicate uploads and to build deterministic chunk IDs.
    """
    return hashlib.sha256(file_bytes).hexdigest()[:16]


def new_id(prefix: str = "") -> str:
    """Generate a short unique identifier, optionally prefixed."""
    token = uuid.uuid4().hex[:12]
    return f"{prefix}{token}" if prefix else token


def timestamp() -> str:
    """Human-readable current timestamp, used for history & exports."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
