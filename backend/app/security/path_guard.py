"""
Ultron Path Guard
Enforces the `security.allowed_directories` / `security.blocked_directories`
rules from config.yaml at the tool layer. Prevents tools from reading/writing
system-critical paths (e.g. /etc, C:\\Windows) even if the model emits a
tool call for them.
"""
import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"


def _load_security_config() -> dict:
    """Load the security block from config.yaml safely."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return (yaml.safe_load(f) or {}).get("security", {})
    except Exception:
        return {}


def get_blocked_paths() -> list:
    """Resolve blocked directories to absolute paths where possible."""
    cfg = _load_security_config()
    blocked = cfg.get("blocked_directories", []) or []
    resolved = []
    for p in blocked:
        if not p:
            continue
        # Try to resolve Windows-style paths (C:\\...) only on Windows.
        p = p.replace("\\\\", "\\").replace("\\", "/")
        if ":" in p and os.name != "nt":
            continue  # skip Windows paths on non-Windows
        try:
            resolved.append(str(Path(p).resolve()))
        except Exception:
            pass
    return resolved


def get_allowed_paths() -> list:
    """Resolve allowed directories. Empty = no restriction (besides blocked)."""
    cfg = _load_security_config()
    allowed = cfg.get("allowed_directories", []) or []
    resolved = []
    for p in allowed:
        if p:
            try:
                resolved.append(str(Path(p).resolve()))
            except Exception:
                pass
    return resolved


def is_path_safe(path_str: str) -> bool:
    """
    Return True if the given path is allowed (not inside a blocked directory).
    - If the path matches a blocked directory (or is inside it) -> False.
    - Otherwise True (allowed).
    """
    if not path_str:
        return False
    try:
        target = str(Path(path_str).resolve())
    except Exception:
        return False

    for blocked in get_blocked_paths():
        # Block exact match or anything inside a blocked directory.
        if target == blocked or target.startswith(blocked + os.sep):
            return False
    return True
