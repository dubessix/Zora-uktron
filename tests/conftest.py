"""
Pytest shared fixtures for the Ultron test-suite.

Phase 0 (test/data safety):
- Force a TEMPORARY SQLite database + cache so the real Ultron data
  (data/memory, data/cache, memories, conversations, tasks, reminders) is
  NEVER touched by tests.
- Hard guard: refuse to run if the DB still resolves to the production path.
"""

import os
import tempfile
from pathlib import Path

import pytest


def _enable_test_isolation():
    """Point the backend at a temporary DB/cache and set the test flag."""
    # 1. Force backend DB to a temporary file (see backend/app/database/db.py).
    os.environ["ULTRON_TEST_DB"] = "1"

    # 2. Force the smart cache to a temporary path too.
    os.environ["ULTRON_TEST_CACHE"] = "1"


# Apply BEFORE any backend module import so db.py reads the flag at import time.
_enable_test_isolation()

# Verify the backend resolves the DB to a temp path, not production.
from backend.app.database import db as _db  # noqa: E402

_PROD_DB = (Path(__file__).resolve().parent.parent / "data" / "memory" / "ultron.db").resolve()


def _assert_not_production():
    db_path = Path(_db.DB_PATH).resolve()
    if db_path == _PROD_DB:
        raise RuntimeError(
            "REFUSING TO RUN TESTS: database resolves to production path "
            f"{db_path}. Tests must use a temporary database."
        )


_assert_not_production()


@pytest.fixture(autouse=True, scope="session")
def ensure_database_schema():
    """Create all required tables in the TEMPORARY database once."""
    from backend.app.database.db import get_db_connection
    from backend.app.database.models import initialize_database
    with get_db_connection() as conn:
        initialize_database(conn)
    yield
