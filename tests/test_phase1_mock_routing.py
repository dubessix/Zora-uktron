"""
Phase 1 regression — LLM failover correctness.

A provider that has NO real key configured must be SKIPPED in the failover
cascade, never return its own fake mock (which would shadow a later provider
that actually has a working key). The local mock is only used as a last-resort
offline fallback when no real provider key exists anywhere.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

import httpx

from backend.app.brain.api_key_manager import APIKeyManager
from backend.app.brain.smart_cache import SmartCache
from backend.app.brain.llm_router import LLMRouter


def _run(coro):
    return asyncio.run(coro)


class TestMockRoutingSkip(unittest.TestCase):

    def _router_with(self, groq_keys, gemini_keys, nvidia_keys):
        m = APIKeyManager()
        m._keys["groq"] = groq_keys
        m._keys["gemini"] = gemini_keys
        m._keys["nvidia"] = nvidia_keys
        cache = SmartCache(max_items=5)
        return LLMRouter(key_manager=m, cache=cache)

    def test_no_real_keys_anywhere_returns_offline_mock(self):
        """With no real keys at all, the router returns an honest local mock (not a crash)."""
        router = self._router_with([], [], [])
        resp = _run(router.get_completions("sys", "hello", 0.7, "groq"))
        self.assertIn("[Mock GROQ Response]", resp)
        _run(router.close())

    @patch("httpx.AsyncClient.post")
    def test_missing_primary_key_skips_to_real_fallback(self, mock_post):
        """groq missing, gemini present: prefer groq but must use gemini, NOT a groq mock."""
        success = MagicMock(spec=httpx.Response)
        success.status_code = 200
        success.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "REAL_GEMINI_RESULT"}]}}]
        }
        mock_post.return_value = success

        router = self._router_with([], [{"key": "AIza_RealKey", "state": "ACTIVE"}], [])
        resp = _run(router.get_completions("sys", "please use fallback", 0.7, "groq"))
        self.assertEqual(resp, "REAL_GEMINI_RESULT")  # from gemini, not a groq mock
        _run(router.close())


if __name__ == "__main__":
    unittest.main()
