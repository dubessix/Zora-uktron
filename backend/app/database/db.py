"""
Ultron Core Database Connection Manager
Establishes thread-safe local connections to SQLite and enforces Write-Ahead Logging (WAL) concurrency.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

# Ensure data storage directories are resolved platform-independently
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = BASE_DIR / "data" / "memory"
DB_PATH = DB_DIR / "ultron.db"

# Phase 0 (test/data safety): allow an explicit override so tests can point at a
# temporary database instead of the real one. Set ULTRON_TEST_DB=1 to use a
# temp DB in a temp dir — production data is never touched during tests.
import os as _os
if _os.getenv("ULTRON_TEST_DB") == "1":
    import tempfile as _tempfile
    _tmp = Path(_tempfile.mkdtemp(prefix="ultron_test_")) / "test_ultron.db"
    DB_DIR = _tmp.parent
    DB_PATH = _tmp

# Ensure directory existences before running transactions
DB_DIR.mkdir(parents=True, exist_ok=True)

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields a thread-safe connection to the SQLite database.
    Configures journal mode to WAL and synchronous to NORMAL for fast concurrent access.
    """
    conn = None
    try:
        conn = sqlite3.connect(
            str(DB_PATH),
            timeout=15.0,  # Prevent blocking failures during multi-threading
            check_same_thread=False  # Allow shared thread execution safety
        )
        # Enable Write-Ahead Logging for non-blocking concurrent writes
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.row_factory = sqlite3.Row  # Return results as rich dictionaries
        yield conn
    except sqlite3.Error as e:
        # Roll back active transaction states in case of unexpected SQL errors
        if conn:
            conn.rollback()
        raise OSError(f"Database transaction failure: {e}") from e
    finally:
        if conn:
            conn.close()
