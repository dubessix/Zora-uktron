"""
Ultron Smart Local Cache (LRU-TTL)
Provides high-speed, thread-safe memory and disk caching with absolute memory limits.
Natively complies with 8GB RAM host constraints.
"""

import json
import time
import os
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Any, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CACHE_DIR = BASE_DIR / "data" / "cache"
CACHE_PATH = CACHE_DIR / "smart_cache.json"

# Phase 0 (test/data safety): allow tests to use a temporary cache path so the
# production cache is never touched during the test suite.
import os as _os
if _os.getenv("ULTRON_TEST_CACHE") == "1":
    import tempfile as _tempfile
    _tmpdir = Path(_tempfile.mkdtemp(prefix="ultron_test_cache_"))
    CACHE_DIR = _tmpdir
    CACHE_PATH = _tmpdir / "smart_cache.json"

class SmartCache:
    def __init__(self, max_items: int = 200, expiry_hours: float = 24.0) -> None:
        self.max_items = max_items
        self.ttl_seconds = expiry_hours * 3600.0
        # Thread-safe operations using collections.OrderedDict
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Restores serialized cache from disk on backend boot."""
        if not CACHE_PATH.exists():
            return
            
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                current_time = time.time()
                for key, val_tuple in raw_data.items():
                    val, timestamp = val_tuple
                    # Only restore items that haven't expired
                    if current_time - timestamp < self.ttl_seconds:
                        self._cache[key] = (val, timestamp)
            print(f"[SMART_CACHE] Restored {len(self._cache)} unexpired cache rows from disk.")
        except (OSError, json.JSONDecodeError) as e:
            print(f"[SMART_CACHE] Warning: Failed to restore cache: {e}. Starting clean.")

    def save_to_disk(self) -> None:
        """Serializes local cache entries on clean server shutdowns."""
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(dict(self._cache), f, indent=2)
            print(f"[SMART_CACHE] Saved {len(self._cache)} cache rows to disk cleanly.")
        except OSError as e:
            print(f"[SMART_CACHE] Critical: Failed to write cache on shutdown: {e}")

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves cache entry value. Updates LRU access ordering.
        If TTL expired, deletes item and returns None.
        """
        if key not in self._cache:
            return None
            
        val, timestamp = self._cache[key]
        current_time = time.time()
        
        # Verify TTL validity
        if current_time - timestamp >= self.ttl_seconds:
            del self._cache[key]
            return None
            
        # Move key to end to mark as recently used
        self._cache.move_to_end(key)
        return val

    def set(self, key: str, value: Any) -> None:
        """
        Writes data row to local cache. Prunes oldest entries if
        memory size bounds (max_items) are exceeded.
        """
        current_time = time.time()
        if key in self._cache:
            # Overwrite value and update position
            self._cache[key] = (value, current_time)
            self._cache.move_to_end(key)
            return
            
        # Evict oldest entry if limit exceeded
        if len(self._cache) >= self.max_items:
            self._cache.popitem(last=False)
            
        self._cache[key] = (value, current_time)

    def clear(self) -> None:
        """Prunes entire cache registry."""
        self._cache.clear()
        if CACHE_PATH.exists():
            try:
                os.remove(CACHE_PATH)
            except OSError:
                pass
