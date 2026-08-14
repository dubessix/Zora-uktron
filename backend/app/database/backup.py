"""
Ultron Database Backup / Restore / Integrity (Phase 9 durability)

Provides a verified backup + restore path for the local SQLite database so a
personal assistant used daily for years can survive disk issues, bad migrations,
or accidental data loss.

  - backup_database()   : atomic-ish copy of the live DB (WAL checkpoint first)
                          into a timestamped file, then VERIFIES the backup by
                          reopening it and running PRAGMA integrity_check.
  - restore_database()  : verifies a backup file is a valid, non-empty SQLite DB
                          (integrity_check) BEFORE overwriting the live DB, and
                          keeps a safety copy of the current DB.
  - check_integrity()   : returns PRAGMA integrity_check output + row counts.

Never touches test DBs: tests set ULTRON_TEST_DB=1 and db.py already redirects
DB_PATH to a temp file, so backups operate on whatever DB_PATH resolves to.
"""

import os
import time
import shutil
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from backend.app.database import db as _db

# Reference the DB path/root dynamically through the module so a re-pointed DB
# (e.g. tests) is always honored instead of a stale copy captured at import.


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def _checkpoint_and_close() -> None:
    """Force a WAL checkpoint so the main .db file is self-contained for backup."""
    try:
        conn = sqlite3.connect(str(_db.DB_PATH), timeout=15.0)
        try:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        finally:
            conn.close()
    except sqlite3.Error:
        pass


def verify_db_file(path: Path) -> Dict[str, Any]:
    """Open a DB file, run integrity_check + count core tables. Returns a report."""
    report = {"valid": False, "integrity": [], "tables": {}, "error": None}
    if not path.exists() or path.stat().st_size == 0:
        report["error"] = "file missing or empty"
        return report
    try:
        conn = sqlite3.connect(str(path), timeout=15.0)
        try:
            rows = conn.execute("PRAGMA integrity_check;").fetchall()
            report["integrity"] = [r[0] for r in rows]
            report["valid"] = all(r[0] == "ok" for r in rows)
            tables = [t[0] for t in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()]
            for t in ("sessions", "conversations", "vector_memories", "reminders_alarms",
                      "project_tasks", "calendar_events", "tool_audit_logs"):
                if t in tables:
                    report["tables"][t] = conn.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error as e:
        report["error"] = str(e)
    return report


def backup_database(dest_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Create a verified timestamped backup of the live DB.

    Returns success dict with backup_path + verification report, or error.
    """
    dest_dir = dest_dir or (_db.DB_DIR / "backups")
    dest_dir.mkdir(parents=True, exist_ok=True)
    backup_path = dest_dir / f"ultron_{_timestamp()}.db"

    _checkpoint_and_close()
    try:
        shutil.copy2(str(_db.DB_PATH), str(backup_path))
    except OSError as e:
        return {"success": False, "error": f"Backup copy failed: {e}", "data": {}}

    # Verify the backup is a valid, intact DB before declaring success.
    report = verify_db_file(backup_path)
    if not report["valid"]:
        try:
            backup_path.unlink(missing_ok=True)
        except OSError:
            pass
        return {"success": False, "error": f"Backup verification failed: {report['error']}", "data": {}}

    return {
        "success": True,
        "data": {
            "backup_path": str(backup_path),
            "bytes": backup_path.stat().st_size,
            "verification": report,
        },
        "error": None,
    }


def restore_database(backup_path: str) -> Dict[str, Any]:
    """Restore the live DB from a verified backup file.

    Verifies the backup integrity FIRST. Keeps a safety copy of the current DB
    before overwriting. Returns success/error with the safety backup path.
    """
    src = Path(backup_path).resolve()
    report = verify_db_file(src)
    if not report["valid"]:
        return {
            "success": False,
            "error": f"Refusing to restore: backup is not a valid DB ({report['error'] or report['integrity']})",
            "data": {"verification": report},
        }

    _checkpoint_and_close()

    # Safety copy of the current DB before replacing it.
    safety = _db.DB_DIR / f"ultron_pre_restore_{_timestamp()}.db"
    try:
        shutil.copy2(str(_db.DB_PATH), str(safety))
    except OSError as e:
        return {"success": False, "error": f"Failed to make safety copy: {e}", "data": {}}

    try:
        shutil.copy2(str(src), str(_db.DB_PATH))
    except OSError as e:
        return {"success": False, "error": f"Restore copy failed: {e}", "data": {}}

    # Post-restore integrity check.
    post = verify_db_file(_db.DB_PATH)
    if not post["valid"]:
        return {
            "success": False,
            "error": f"Restored DB failed integrity check — please restore safety copy {safety}",
            "data": {"safety_backup": str(safety), "verification": post},
        }

    return {
        "success": True,
        "data": {
            "restored_from": str(src),
            "safety_backup": str(safety),
            "verification": post,
        },
        "error": None,
    }


def check_integrity() -> Dict[str, Any]:
    """Report the live DB integrity + core table row counts."""
    return {"success": True, "data": verify_db_file(_db.DB_PATH), "error": None}
