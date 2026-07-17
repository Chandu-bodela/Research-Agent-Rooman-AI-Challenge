"""
backend/loader.py
==================
Handles saving Streamlit-uploaded files to disk (data/uploads) before
they're parsed. Kept separate from parsing so ingestion has one clear
"file arrives on disk" boundary — useful for testing and for swapping in
a cloud storage backend later without touching the parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.utils import file_hash, get_logger, safe_filename
from config import UPLOAD_DIR, settings

logger = get_logger(__name__)


@dataclass
class SavedFile:
    path: Path
    original_name: str
    size_bytes: int
    content_hash: str


class InvalidFileTypeError(Exception):
    """Raised when a file extension isn't in `settings.supported_extensions`."""


def validate_extension(filename: str) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.supported_extensions:
        raise InvalidFileTypeError(
            f"'{suffix}' is not supported. Allowed types: "
            f"{', '.join(settings.supported_extensions)}"
        )


def save_uploaded_file(file_bytes: bytes, filename: str) -> SavedFile:
    """Persist an uploaded file's bytes to `data/uploads` and return metadata.

    The saved filename is prefixed with a short content hash to avoid
    collisions between different files that happen to share a name.
    """
    validate_extension(filename)
    clean_name = safe_filename(filename)
    digest = file_hash(file_bytes)
    stored_name = f"{digest}_{clean_name}"
    path = UPLOAD_DIR / stored_name

    if not path.exists():
        path.write_bytes(file_bytes)
        logger.info("Saved upload: %s (%d bytes)", path, len(file_bytes))
    else:
        logger.info("Duplicate upload detected, reusing existing file: %s", path)

    return SavedFile(
        path=path,
        original_name=filename,
        size_bytes=len(file_bytes),
        content_hash=digest,
    )
