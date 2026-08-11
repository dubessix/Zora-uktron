"""
Ultron Semantic Memory Layer
Handles developer concepts, rules, coding tricks, and long-term tech notes.
"""

import uuid
from typing import List, Dict, Any, Optional
from backend.app.memory.vector_store import VectorStore

class SemanticMemory:
    def __init__(self, store: Optional[VectorStore] = None) -> None:
        self.store = store or VectorStore()

    async def learn_concept(self, concept_text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Generates embeddings and saves developer tech concepts to SQLite vector tables."""
        msg_id = str(uuid.uuid4())
        try:
            embedding = await self.store.generate_embedding(concept_text)
            return self.store.save_vector_memory(
                msg_id=msg_id,
                mem_type="semantic",
                content=concept_text,
                embedding=embedding,
                metadata=metadata or {}
            )
        except Exception as e:
            print(f"[SEMANTIC_MEMORY] Warning: Failed to learn concept: {e}")
            return False

    async def recall_related_concepts(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Searches tech concepts matching query."""
        try:
            query_emb = await self.store.generate_embedding(query)
            return self.store.search_similarity("semantic", query_emb, limit=limit)
        except Exception as e:
            print(f"[SEMANTIC_MEMORY] Warning: Failed to recall concepts: {e}")
            return []
