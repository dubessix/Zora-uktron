r"""
Ultron Path Guard
Enforces the `security.allowed_directories` / `security.blocked_directories`
rules from config.yaml at the tool layer. Prevents tools from reading/writing
system-critical paths (e.g. /etc, C:\Windows) even if the model emits a
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


# Default system-critical roots blocked even if absent from config.yaml.
# Checked as directory membership: a target is blocked if it is INSIDE any of
# these (target == root or target.startswith(root + os.sep)). A project folder
# legitimately named e.g. "dev" under /home is NOT blocked because its absolute
# path starts with /home, not /dev.
_DEFAULT_BLOCKED_ROOTS = [
    "/etc", "/var", "/proc", "/sys", "/boot", "/root", "/dev", "/bin",
    "/sbin", "/lib", "/lib64", "/usr/sbin", "/System", "/Library",
    "C:\\Windows", "C:\\System32", "C:\\Program Files",
]

# Sensitive file/dir names blocked AT ANY DEPTH of the path (secrets, git creds,
# keys, environment files). A file anywhere under one of these is refused.
_SENSITIVE_NAMES = {
    ".ssh", ".gnupg", ".aws", ".env", ".git-credentials", ".netrc",
    "credentials", "secrets", "keystore", "id_rsa", "id_ed25519",
}


def get_blocked_paths() -> list:
    """Resolve blocked directories to absolute paths where possible."""
    cfg = _load_security_config()
    blocked = cfg.get("blocked_directories", []) or []
    resolved = []
    for p in blocked:
        if not p:
            continue
        # Try to resolve Windows-style paths (C:\...) only on Windows.
        p = p.replace("\\", "/")
        if ":" in p and os.name != "nt":
            continue  # skip Windows paths on non-Windows
        try:
            resolved.append(str(Path(p).resolve()))
        except Exception:
            pass
    # Merge in the default system roots (already absolute).
    for root in _DEFAULT_BLOCKED_ROOTS:
        if root not in resolved:
            resolved.append(root)
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


def _contains_sensitive_component(path: Path) -> bool:
    """True if any component of the resolved path is a sensitive secret location."""
    for part in path.parts:
        lower = part.lower()
        if lower in _SENSITIVE_NAMES:
            return True
        if lower.startswith(".env"):  # .env, .env.local, .env.example, ...
            return True
    return False


def is_path_safe(path_str: str) -> bool:
    """
    Return True if the given path is allowed (not inside a blocked directory and
    not touching a sensitive secret location at any depth).
    """
    if not path_str:
        return False
    try:
        target = Path(path_str).resolve()
    except Exception:
        return False
    target_str = str(target)

    # Block any sensitive component (secrets/keys/env/credentials) at any depth.
    if _contains_sensitive_component(target):
        return False

    for blocked in get_blocked_paths():
        # Block exact match or anything inside a blocked directory.
        if target_str == blocked or target_str.startswith(blocked + os.sep):
            return False

    return True
