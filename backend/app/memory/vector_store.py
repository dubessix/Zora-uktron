"""
Ultron Hybrid Vector Store Engine
Enforces standard SQLite BLOB persistence and runs high-speed local NumPy Cosine Similarity math.
Bypasses local transformers footprint, fully complying with 8GB RAM host limitations.
"""

import json
import yaml
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from backend.app.database.db import get_db_connection
from backend.app.brain.api_key_manager import APIKeyManager

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"

class VectorStore:
    def __init__(self, key_manager: Optional[APIKeyManager] = None) -> None:
        self.key_manager = key_manager or APIKeyManager()
        self.duplicate_threshold = self._load_threshold_from_config()
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
        Dispatches async request to Gemini text-embedding-004 API to generate
        a highly precise 768-dimension float array.
        """
        api_key = self.key_manager.get_active_key("gemini")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            }
        }
        
        # Safe fallback check for local mock test executions
        if "dummy_fallback" in api_key:
            # Generate a reproducible pseudo-embedding vector for testing
            np.random.seed(hash(text) % (2**32))
            return np.random.randn(768).tolist()

        import httpx
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if response.status_code == 200:
                    res_data = response.json()
                    return res_data["embedding"]["values"]
                else:
                    raise RuntimeError(f"Embedding API returned status code: {response.status_code}")
            except Exception as e:
                raise RuntimeError(f"Failed to connect to cloud embedding client: {e}")

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
