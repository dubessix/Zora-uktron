"""
Ultron Hybrid Vector Store Engine
Enforces standard SQLite BLOB persistence and runs high-speed local NumPy Cosine Similarity math.
Bypasses local transformers footprint, fully complying with 8GB RAM host limitations.
"""

import json
import yaml
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.app.database.db import get_db_connection
from backend.app.brain.api_key_manager import APIKeyManager
from backend.app.brain.model_config import get_model, get_embedding_dimensions

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"

# Lazy-load numpy only when needed (cosine math / embeddings), so the heavy
# NumPy dependency is NOT pulled into memory at backend boot time. This keeps
# startup light on 8GB / dual-core hosts while preserving all functionality.
_np = None

def _lazy_numpy():
    """Import numpy lazily on first use and cache the module reference."""
    global _np
    if _np is None:
        import numpy
        _np = numpy
    return _np

class VectorStore:
    def __init__(self, key_manager: Optional[APIKeyManager] = None) -> None:
        self.key_manager = key_manager or APIKeyManager()
        self.duplicate_threshold = self._load_threshold_from_config()
        self._writes_since_prune = 0
        self.prune_interval = 100  # Run retention check every N writes (keeps writes cheap)
        self._embedding_cache: Dict[str, List[float]] = {}
        self._embedding_cache_limit = 256
        self._initialize_table()

    def _load_threshold_from_config(self) -> float:
        """Loads similarity deduplication threshold from config.yaml safely."""
        if not CONFIG_PATH.exists():
            return 0.95
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("memory", {}).get("duplicate_similarity_threshold", 0.95)
        except Exception:
            return 0.95

    def _initialize_table(self) -> None:
        """Initializes the self-contained vector_memories table."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,         -- episodic | semantic | emotional
                    content TEXT NOT NULL,
                    embedding BLOB NOT NULL,     -- NumPy float32 array serialized
                    metadata TEXT DEFAULT '{}',  -- JSON formatted meta variables
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Dispatches an async request to the Gemini embeddings API to generate a
        vector of the configured dimensionality (default 768, matching stored
        vectors so new memories stay comparable to legacy ones).

        The embedding model + dimensions are config-driven (env
        GEMINI_EMBEDDING_MODEL / GEMINI_EMBEDDING_DIMS, or config.yaml) — the
        retired text-embedding-004 is no longer hardcoded. Repeated text is served
        from an in-memory cache so we never burn API calls on the same query twice.
        """
        key = text.strip()
        if key in self._embedding_cache:
            return self._embedding_cache[key]

        model = get_model("embedding")
        dims = get_embedding_dimensions()
        api_key = self.key_manager.get_active_key("gemini")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": f"models/{model}",
            "content": {
                "parts": [{"text": text}]
            },
            "outputDimensionality": dims,
        }
        
        # Safe fallback check for local mock test executions
        if "dummy_fallback" in api_key:
            # Generate a reproducible pseudo-embedding vector for testing
            np = _lazy_numpy()
            np.random.seed(hash(text) % (2**32))
            vec = np.random.randn(dims).tolist()
            self._embedding_cache[key] = vec
            return vec

        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if response.status_code == 200:
                    res_data = response.json()
                    vec = res_data["embedding"]["values"]
                    self._cache_embedding(key, vec)
                    return vec
                else:
                    raise RuntimeError(f"Embedding API returned status code: {response.status_code}")
            except Exception as e:
                raise RuntimeError(f"Failed to connect to cloud embedding client: {e}")

    def _cache_embedding(self, key: str, vec: List[float]) -> None:
        """Bounded in-memory embedding cache (token saver)."""
        self._embedding_cache[key] = vec
        if len(self._embedding_cache) > self._embedding_cache_limit:
            # Drop the oldest entry (dicts preserve insertion order).
            self._embedding_cache.pop(next(iter(self._embedding_cache)))

    def save_vector_memory(
        self,
        msg_id: str,
        mem_type: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Saves a serialized vector memory row. Implements duplicate checks:
        if a high similarity exceeds config-defined threshold, halts writing.
        """
        # Convert list to high-performance NumPy float32 array
        np = _lazy_numpy()
        new_vec = np.array(embedding, dtype=np.float32)
        
        # 1. Run Duplicate Verification check
        existing_matches = self.search_similarity(mem_type, embedding, limit=1)
        if existing_matches:
            top_similarity = existing_matches[0]["similarity"]
            if top_similarity > self.duplicate_threshold:
                print(f"[VECTOR_STORE] Duplicate write aborted. Similarity ({top_similarity:.3f}) exceeds threshold ({self.duplicate_threshold}).")
                return False

        # 2. Serialize vector array to raw binary BLOB
        vec_blob = new_vec.tobytes()
        metadata_str = json.dumps(metadata or {})

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO vector_memories (id, type, content, embedding, metadata)
                VALUES (?, ?, ?, ?, ?);
                """,
                (msg_id, mem_type, content, sqlite3.Binary(vec_blob), metadata_str)
            )
            conn.commit()

            # Opportunistic storage-retention guard (bounds long-term growth).
            self._writes_since_prune += 1
            if self._writes_since_prune >= self.prune_interval:
                self._writes_since_prune = 0
                try:
                    self.prune()
                except Exception as e:
                    print(f"[VECTOR_STORE] Warning: retention prune failed: {e}")

            return True

    def search_similarity(
        self,
        mem_type: str,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Loads all matching type vector binaries from SQLite, deserializes them to NumPy arrays,
        computes local Cosine Similarities, and returns sorted top matches.
        """
        np = _lazy_numpy()
        target_vec = np.array(query_embedding, dtype=np.float32)
        target_norm = np.linalg.norm(target_vec)
        
        if target_norm == 0:
            return []

        matches = []
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, content, embedding, metadata, created_at FROM vector_memories WHERE type = ?;",
                (mem_type,)
            )
            rows = cursor.fetchall()

            for row in rows:
                # Load binary BLOB back to NumPy float32 array
                db_vec = np.frombuffer(row["embedding"], dtype=np.float32)
                db_norm = np.linalg.norm(db_vec)
                
                if db_norm == 0:
                    continue

                # Robustness: if a stored vector's dimensionality differs from the
                # current embedding (e.g. a legacy model change), skip it instead of
                # crashing the whole recall with a dimension mismatch. These rows can
                # be re-embedded / pruned later.
                if db_vec.shape != target_vec.shape:
                    print(f"[VECTOR_STORE] Skipping memory {row['id']}: dimension mismatch "
                          f"({db_vec.shape[0]} != {target_vec.shape[0]}). Re-embed to migrate.")
                    continue

                # Execute Cosine Similarity equation: dot(A, B) / (norm(A) * norm(B))
                similarity = float(np.dot(target_vec, db_vec) / (target_norm * db_norm))
                
                matches.append({
                    "id": row["id"],
                    "content": row["content"],
                    "similarity": similarity,
                    "metadata": json.loads(row["metadata"]),
                    "created_at": row["created_at"]
                })

        # Sort matches chronologically by similarity descending
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return matches[:limit]

    def delete_vector_memory(self, msg_id: str) -> bool:
        """Delete a specific vector memory row by id (used by memory forget)."""
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM vector_memories WHERE id = ?;", (msg_id,))
                conn.commit()
                return cur.rowcount > 0
        except sqlite3.Error as e:
            print(f"[VECTOR_STORE] Delete failed: {e}")
            return False

    def list_recent_memories(self, limit: int = 20, mem_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return recent memory rows (id/type/content/created_at) for display/export."""
        with get_db_connection() as conn:
            cur = conn.cursor()
            if mem_type:
                cur.execute(
                    "SELECT id, type, content, created_at FROM vector_memories WHERE type = ? ORDER BY rowid DESC LIMIT ?;",
                    (mem_type, limit),
                )
            else:
                cur.execute(
                    "SELECT id, type, content, created_at FROM vector_memories ORDER BY rowid DESC LIMIT ?;",
                    (limit,),
                )
            return [dict(r) for r in cur.fetchall()]

    def prune(self, max_per_type: int = 2000) -> int:
        """
        Lightweight storage-retention guard. Keeps only the most recent
        `max_per_type` rows per memory type, deleting the oldest beyond the cap.
        This bounds long-term growth so memory stays tiny even over years of use.
        Returns the number of rows removed.
        """
        removed = 0
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # For each distinct type, delete rows beyond the newest max_per_type.
            cursor.execute("SELECT DISTINCT type FROM vector_memories;")
            types = [row["type"] for row in cursor.fetchall()]
            for mem_type in types:
                # Find the cutoff id: the id at offset max_per_type when ordered newest-first.
                cursor.execute(
                    """
                    SELECT id FROM vector_memories
                    WHERE type = ?
                    ORDER BY created_at DESC, rowid DESC
                    LIMIT 1 OFFSET ?;
                    """,
                    (mem_type, max_per_type),
                )
                cutoff = cursor.fetchone()
                if cutoff:
                    cursor.execute(
                        """
                        DELETE FROM vector_memories
                        WHERE type = ? AND rowid <= (SELECT rowid FROM vector_memories
                                                     WHERE id = ?);
                        """,
                        (mem_type, cutoff["id"]),
                    )
                    removed += cursor.rowcount
            conn.commit()
        if removed:
            print(f"[VECTOR_STORE] Storage retention: pruned {removed} old memory rows (bounded to {max_per_type}/type).")
        return removed
