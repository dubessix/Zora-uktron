"""
Ultron Pending-Action Confirmation Registry (Phase 3)

Binds a user's "yes, go ahead" confirmation to the EXACT action that was
proposed (tool + target file + content hash + session), with a short expiry.

A write that needs confirmation creates an entry here and returns a one-time
token in its PENDING_CONFIRMATION response. When the user confirms, the system
re-validates that the token still matches the same tool/file/content — so a
confirmation can never be silently replayed onto different content. Entries are
consumed after a successful use and pruned when expired.
"""

import hashlib
import time
import threading
import uuid
from typing import Dict, Any, Optional

# Default lifetime of a pending confirmation before it must be re-confirmed.
DEFAULT_TTL_SECONDS = 300.0
MAX_PENDING = 200


class PendingActionRegistry:
    def __init__(self, ttl_seconds: float = DEFAULT_TTL_SECONDS) -> None:
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
        self._items: Dict[str, Dict[str, Any]] = {}

    def _content_hash(self, content: str) -> str:
        return hashlib.sha256((content or "").encode("utf-8")).hexdigest()

    def create(
        self,
        tool_id: str,
        session_id: Optional[str],
        target: str,
        content: str,
    ) -> str:
        """Register a pending action and return its one-time token."""
        token = uuid.uuid4().hex
        with self._lock:
            self._prune_locked()
            if len(self._items) >= MAX_PENDING:
                # Drop the oldest entry to bound memory.
                oldest = min(self._items, key=lambda k: self._items[k]["created"])
                self._items.pop(oldest, None)
            self._items[token] = {
                "tool_id": tool_id,
                "session_id": session_id,
                "target": str(target),
                "content_hash": self._content_hash(content),
                "created": time.time(),
            }
        return token

    def _prune_locked(self) -> None:
        now = time.time()
        expired = [
            t for t, it in self._items.items()
            if now - it["created"] >= self._ttl
        ]
        for t in expired:
            self._items.pop(t, None)

    def validate(
        self,
        token: Optional[str],
        tool_id: str,
        session_id: Optional[str],
        target: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        Validate a confirmation token against the exact proposed action.

        Returns {"valid": True} on success (and consumes the token), or
        {"valid": False, "reason": ...}.
        """
        if not token:
            return {"valid": False, "reason": "missing_confirmation_token"}

        with self._lock:
            item = self._items.get(token)
            if item is None:
                return {"valid": False, "reason": "unknown_or_expired_token"}
            now = time.time()
            if now - item["created"] >= self._ttl:
                self._items.pop(token, None)
                return {"valid": False, "reason": "token_expired"}
            if item["tool_id"] != tool_id:
                return {"valid": False, "reason": "tool_mismatch"}
            if item["session_id"] != session_id:
                return {"valid": False, "reason": "session_mismatch"}
            if item["target"] != str(target):
                return {"valid": False, "reason": "target_file_mismatch"}
            if item["content_hash"] != self._content_hash(content):
                return {"valid": False, "reason": "content_mismatch"}

            # Valid — consume the one-time token so it can't be reused.
            self._items.pop(token, None)
            return {"valid": True}

    def find_recent_match(
        self,
        tool_id: str,
        session_id: Optional[str],
        target: str,
        content: str,
    ) -> Optional[str]:
        """
        Backward-compatible lookup: when a client confirms without sending a token
        (legacy frontend), find the most recent pending action that matches the
        same tool/file/content and return its token (if any). Consumed on use by
        the caller via validate().
        """
        content_hash = self._content_hash(content)
        with self._lock:
            self._prune_locked()
            best = None
            best_created = -1.0
            for t, it in self._items.items():
                if (
                    it["tool_id"] == tool_id
                    and it["session_id"] == session_id
                    and it["target"] == str(target)
                    and it["content_hash"] == content_hash
                ):
                    if it["created"] > best_created:
                        best = t
                        best_created = it["created"]
            return best

    def pending_count(self) -> int:
        with self._lock:
            self._prune_locked()
            return len(self._items)


# Shared singleton for the whole process (thread-safe).
_pending_actions = PendingActionRegistry()


def get_pending_action_registry() -> PendingActionRegistry:
    """Returns the process-wide pending-action confirmation registry."""
    return _pending_actions
