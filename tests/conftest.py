"""
Pytest shared fixtures for the Ultron test-suite.

Fixes a hidden test-ordering dependency: several tests (e.g.
tests/test_final_dance.py) hit the SQLite tables (project_tasks,
reminders_alarms, calendar_events) but never created them themselves --
they silently passed only when tests/test_phase1.py happened to run first
and called initialize_database(). Running those files in isolation failed
with "no such table".

This autouse fixture guarantees the schema exists before any test runs,
making the suite deterministic regardless of collection order.
"""

import pytest

from backend.app.database.db import get_db_connection
from backend.app.database.models import initialize_database


@pytest.fixture(autouse=True, scope="session")
def ensure_database_schema():
    """Create all required tables once, before the full test session starts."""
    with get_db_connection() as conn:
        initialize_database(conn)
    yield
