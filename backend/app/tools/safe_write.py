"""
Ultron Safe File Write (Phase 3)

The SINGLE code path for writing files to disk, used by BOTH the `file_write`
tool and the orchestrator's coding-mode writer. Guarantees, in one place:

  1. Path safety (is_path_safe) — no writing into system/secret paths.
  2. Existing files are backed up to <name>.bak BEFORE being overwritten.
  3. The write is atomic (write to a temp file in the same directory, then
     os.replace) so a crash mid-write can never leave a truncated file.
  4. A consistent, structured result the caller can audit.

This removes the earlier divergence where the coding writer bypassed validation
and overwrote files without any backup.
"""

import os
import uuid
import tempfile
from pathlib import Path
from typing import Dict, Any


def safe_write_file(filepath: str, content: str) -> Dict[str, Any]:
    """Atomically write `content` to `filepath`, backing up any existing file.

    Returns:
        success dict with message/diff/backup, or
        error dict on failure.
    """
    if not filepath or not str(filepath).strip():
        return {"success": False, "error": "filepath required", "data": {}}

    from backend.app.security.path_guard import is_path_safe

    path = Path(filepath).resolve()

    # 1. Path safety — reject writes into blocked/system/secret locations.
    if not is_path_safe(str(path)):
        return {
            "success": False,
            "error": f"Blocked by path guard: {filepath}",
            "data": {},
        }

    exists = path.exists()
    backup_path = None

    # 2. Back up existing content before overwriting.
    if exists:
        try:
            old_content = path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read existing file for backup: {e}",
                "data": {},
            }
        try:
            backup_path = path.with_suffix(path.suffix + ".bak")
            backup_path.write_text(old_content, encoding="utf-8")
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create backup: {e}",
                "data": {},
            }

    # 3. Atomic write: temp file in the same directory, then replace.
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, str(path))
        except Exception:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise
    except Exception as e:
        return {"success": False, "error": f"Failed to write file: {e}", "data": {}}

    # 4. Consistent result summary (diff-style) for audit/feedback.
    new_lines = len(content.splitlines())
    result = {
        "success": True,
        "data": {
            "message": f"{'Created' if not exists else 'Overwrote'} file: {filepath}",
            "file": filepath,
            "backup": str(backup_path) if backup_path else None,
            "diff": {
                "action": "created" if not exists else "updated",
                "file": filepath,
                "new_lines": new_lines,
                "backup": str(backup_path) if backup_path else None,
            },
        },
        "error": None,
    }
    if exists:
        result["data"]["diff"]["old_lines"] = len(
            str(backup_path.read_text(encoding="utf-8") if backup_path else "").splitlines()
        )
        result["data"]["message"] = f"Overwrote file: {filepath} (backup: {backup_path})"
    return result
