"""
Ultron Central Memory Engine
Co-ordinates data transfers across Short-Term, Persistent, Project, Episodic, Semantic, and Emotional layers.
"""

from typing import Optional
from backend.app.memory.short_term import ShortTermMemory
from backend.app.memory.persistent_memory import PersistentMemory
from backend.app.memory.project_memory import ProjectMemory
from backend.app.memory.vector_store import VectorStore
from backend.app.memory.memory_gate import MemoryGate
from backend.app.memory.episodic_memory import EpisodicMemory
from backend.app.memory.semantic_memory import SemanticMemory
from backend.app.memory.emotional_memory import EmotionalMemory

class MemoryEngine:
    def __init__(self) -> None:
        self.short_term = ShortTermMemory(limit=50)
        self.persistent = PersistentMemory()
        self.project = ProjectMemory()
        
        # Initialize Hybrid Vector Engine layers
        self.vector_store = VectorStore()
        self.gate = MemoryGate()
        self.episodic = EpisodicMemory(self.vector_store)
        self.semantic = SemanticMemory(self.vector_store)
        self.emotional = EmotionalMemory(self.vector_store)

    def save_chat_turn(self, user_message: str, ai_response: str) -> None:
        """Syncs latest dialogue turn into the fast, short-term context cache."""
        self.short_term.add_turn(user_message, ai_response)

    def set_user_profile_param(self, key: str, value: str) -> None:
        """Saves a permanent user configuration parameter into persistent SQLite."""
        self.persistent.set(key, value)

    def get_user_profile_param(self, key: str) -> Optional[str]:
        """Retrieves a permanent user configuration parameter from persistent SQLite."""
        return self.persistent.get(key)
