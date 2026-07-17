"""
database/history.py
====================
A minimal SQLite layer for persisting conversation history (question,
answer, cited sources, timestamp). SQLite is more than sufficient for a
single-user hackathon app and needs no external server.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

from config import DATABASE_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    citations_json TEXT NOT NULL,
    provider TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""


@dataclass
class HistoryEntry:
    id: int
    question: str
    answer: str
    citations: list
    provider: str
    created_at: str


@contextmanager
def _connect(db_path: Path = DATABASE_PATH) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path = DATABASE_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(_SCHEMA)


def add_entry(
    question: str,
    answer: str,
    citations: list,
    provider: str,
    db_path: Path = DATABASE_PATH,
) -> int:
    """Insert a Q&A turn into history. `citations` should be JSON-serializable
    (e.g. a list of dicts)."""
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO history (question, answer, citations_json, provider) "
            "VALUES (?, ?, ?, ?)",
            (question, answer, json.dumps(citations), provider),
        )
        return cur.lastrowid


def get_history(limit: int = 100, db_path: Path = DATABASE_PATH) -> List[HistoryEntry]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()

    return [
        HistoryEntry(
            id=row["id"],
            question=row["question"],
            answer=row["answer"],
            citations=json.loads(row["citations_json"]),
            provider=row["provider"] or "unknown",
            created_at=row["created_at"],
        )
        for row in rows
    ]


def clear_history(db_path: Path = DATABASE_PATH) -> None:
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM history")


def delete_entry(entry_id: int, db_path: Path = DATABASE_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
