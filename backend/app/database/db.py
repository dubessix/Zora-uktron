"""
Ultron Core Database Connection Manager
Establishes thread-safe local connections to SQLite and enforces Write-Ahead Logging (WAL) concurrency.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

# Resolve all storage through one runtime policy. Under pytest/unittest this
# points to a process-local temporary root; production continues to use data/.
from backend.app.runtime_paths import TEST_MODE, runtime_data_path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = runtime_data_path("memory")
DB_PATH = DB_DIR / ("test_ultron.db" if TEST_MODE else "ultron.db")

# Ensure directory existence before running transactions.
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

        # A standalone unittest process does not load pytest fixtures. In test
        # mode, initialize the isolated schema on every fresh temporary DB so
        # pytest and unittest are independently safe and deterministic.
        if TEST_MODE:
            from backend.app.database.models import initialize_database
            initialize_database(conn)

        yield conn
    except sqlite3.Error as e:
        # Roll back active transaction states in case of unexpected SQL errors
        if conn:
            conn.rollback()
        raise OSError(f"Database transaction failure: {e}") from e
    finally:
        if conn:
            conn.close()
