"""
Ultron API Key State Manager
Manages state transitions, round-robin rotation, and automated cooldown counters for Groq and Gemini API keys.
"""

import os
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from pathlib import Path

# Load env variables platform-independently on module import
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class APIKeyManager:
    def __init__(self) -> None:
        # State definitions: "ACTIVE", "COOLING", "FAILED"
        self._keys: Dict[str, List[Dict[str, Any]]] = {
            "groq": [],
            "gemini": [],
            "nvidia": []
        }
        # Cooldown track map: {key_value: timestamp_cooldown_ends}
        self._cooldowns: Dict[str, float] = {}
        # Cursor indexes for round-robin rotation
        self._cursors: Dict[str, int] = {
            "groq": 0,
            "gemini": 0,
            "nvidia": 0
        }
        self._load_keys_from_env()

    def _load_keys_from_env(self) -> None:
        """Pulls keys dynamically from current .env profile."""
        # Load Groq keys pool
        for i in range(1, 4):
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if key and "your_groq_api_key" not in key:
                self._keys["groq"].append({"key": key, "state": "ACTIVE"})
                
        # Load Gemini keys pool
        for i in range(1, 3):
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and "your_gemini_api_key" not in key:
                self._keys["gemini"].append({"key": key, "state": "ACTIVE"})
                
        # Load NVIDIA Build (NIM) keys pool — OpenAI-compatible coding provider.
        for i in range(1, 4):
            key = os.getenv(f"NVIDIA_API_KEY_{i}")
            if key and "your_nvidia_api_key" not in key:
                self._keys["nvidia"].append({"key": key, "state": "ACTIVE"})

    def _clean_cooldowns(self) -> None:
        """Pipes through expired cooldown timers, returning keys back to ACTIVE state."""
        current_time = time.time()
        for provider in ["groq", "gemini", "nvidia"]:
            for item in self._keys[provider]:
                key_val = item["key"]
                if item["state"] == "COOLING" and key_val in self._cooldowns:
                    if current_time >= self._cooldowns[key_val]:
                        item["state"] = "ACTIVE"
                        del self._cooldowns[key_val]

    def get_active_key(self, provider: str) -> str:
        """
        Extracts the next active, healthy key for the requested provider.
        Utilizes round-robin selection. If no keys are active, raises RuntimeError.
        """
        self._clean_cooldowns()
        
        provider = provider.lower()
        if provider not in self._keys:
            raise ValueError(f"Unsupported LLM provider requested: {provider}")
            
        pool = self._keys[provider]
        if not pool:
            # Fallback check in case the user has not updated their .env file yet
            # Provide standard fallback to prevent startup crash, but log error
            dummy_key = f"dummy_fallback_{provider}_key"
            print(f"[WARNING] No active keys detected for provider {provider}. Utilizing local placeholder.")
            return dummy_key

        # Traverse the list starting from active cursor index
        start_idx = self._cursors[provider]
        for offset in range(len(pool)):
            idx = (start_idx + offset) % len(pool)
            if pool[idx]["state"] == "ACTIVE":
                # Advance cursor index for next call
                self._cursors[provider] = (idx + 1) % len(pool)
                return pool[idx]["key"]
                
        # If all keys are locked, search if any are in cooling state and force-resolve the earliest expiration
        active_cooling = [item for item in pool if item["state"] == "COOLING"]
        if active_cooling:
            earliest = min(active_cooling, key=lambda x: self._cooldowns.get(x["key"], float('inf')))
            print(f"[WARNING] Key Pool Exhaustion: Forcing earliest cooling key for {provider}.")
            return earliest["key"]

        raise RuntimeError(f"All registered API keys for {provider} are currently in failed states.")

    def has_real_key(self, provider: str) -> bool:
        """True if a provider has at least one real (non-placeholder) key configured.

        A 'placeholder' is the dummy_fallback key returned when a provider has no
        .env keys at all — it must NOT be treated as a usable provider so the
        failover cascade can move on to a provider that actually has a key.
        """
        provider = provider.lower()
        if provider not in self._keys:
            return False
        return any("dummy_fallback" not in item["key"] for item in self._keys[provider])

    def has_any_real_key(self) -> bool:
        """True if ANY provider has at least one real (non-placeholder) key."""
        return any(self.has_real_key(p) for p in self._keys)

    def mark_key_cooling(self, provider: str, key: str, cooldown_duration_sec: int = 60, duration_sec: Optional[int] = None) -> None:
        """
        Transitions key to COOLING state and sets dynamic lock timer.
        Supports both parameter naming configurations to ensure backward compatibility.
        """
        provider = provider.lower()
        actual_cooldown = duration_sec if duration_sec is not None else cooldown_duration_sec
        
        for item in self._keys.get(provider, []):
            if item["key"] == key:
                item["state"] = "COOLING"
                self._cooldowns[key] = time.time() + actual_cooldown
                print(f"[API_KEY_MANAGER] Provider {provider} key cooling activated for {actual_cooldown} seconds.")
                return

    def mark_key_failed(self, provider: str, key: str) -> None:
        """Transitions key to FAILED state. Requires administrative intervention or app restart to restore."""
        provider = provider.lower()
        for item in self._keys.get(provider, []):
            if item["key"] == key:
                item["state"] = "FAILED"
                print(f"[API_KEY_MANAGER] CRITICAL: Key {key[:10]}... for provider {provider} marked as FAILED.")
                return
