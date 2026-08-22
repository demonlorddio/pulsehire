"""SQLite connection helper.

Single source of truth for the DB file location and the connection factory.
Read DATABASE.md for the full schema.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv

# Load .env from the project root (one level above backend/) if it exists.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# Path defaults to backend/data/pulsehire.db if DATABASE_PATH isn't set.
_DEFAULT_DB = Path(__file__).resolve().parent / "data" / "pulsehire.db"


def get_db_path() -> str:
    """Resolve the absolute path to the SQLite file."""
    raw = os.getenv("DATABASE_PATH", str(_DEFAULT_DB))
    # Relative paths are anchored at the project root, not CWD.
    path = Path(raw)
    if not path.is_absolute():
        path = _PROJECT_ROOT / raw
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_connection() -> sqlite3.Connection:
    """Open a new connection. Caller is responsible for closing it."""
    conn = sqlite3.connect(get_db_path())
    # Return rows as dicts so service code is more readable.
    conn.row_factory = sqlite3.Row
    # Enforce FK constraints (off by default in SQLite).
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Context manager that commits on success and rolls back on error."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
