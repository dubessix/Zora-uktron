"""
Ultron Memory Management Tool (Phase 9 durability)
Lets the user explicitly manage long-term memory: list / remember / forget /
export. Restore is handled at the DB level (database/backup.restore_database).
"""

import uuid
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool
from backend.app.memory.memory_engine import MemoryEngine


class MemoryArgs(BaseModel):
    action: str = Field(..., description="Action: list, remember, forget, export.")
    content: Optional[str] = Field(None, description="Fact to remember (for action='remember').")
    memory_id: Optional[str] = Field(None, description="Memory id to forget (for action='forget').")
    mem_type: Optional[str] = Field(None, description="Optional type filter for list/export.")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Max rows for list/export.")


class MemoryTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="manage_memory",
            name="Memory Manager",
            description="Lists, remembers, forgets, or exports Ultron's long-term memory.",
            category="memory",
            tags=["memory", "remember", "forget", "export", "recall"],
            permission_level=1,  # Write (no confirmation)
            args_model=MemoryArgs,
            usage_examples=[
                "manage_memory(action='remember', content='Debjeet prefers the Emerald theme.')",
                "manage_memory(action='list')",
                "manage_memory(action='forget', memory_id='<id>')",
            ],
        )
        self.memory = MemoryEngine()

    async def execute(self, **kwargs) -> Dict[str, Any]:
        action = (kwargs.get("action") or "list").lower()
        content = kwargs.get("content")
        memory_id = kwargs.get("memory_id")
        mem_type = kwargs.get("mem_type")
        limit = kwargs.get("limit", 10)

        if action == "remember":
            if not content or not content.strip():
                return {"success": False, "error": "content is required for action='remember'.", "data": {}}
            ok = await self.memory.episodic.record_event(
                content=content.strip(),
                metadata={"kind": "explicit_remember", "source": "user"},
            )
            if ok:
                return {"success": True, "data": {"message": "Remembered."}, "error": None}
            return {"success": False, "error": "Failed to save memory (duplicate or error).", "data": {}}

        if action == "list":
            rows = self.memory.vector_store.list_recent_memories(limit=limit, mem_type=mem_type)
            return {"success": True, "data": {"count": len(rows), "memories": rows}, "error": None}

        if action == "forget":
            if not memory_id:
                return {"success": False, "error": "memory_id is required for action='forget'.", "data": {}}
            deleted = self.memory.vector_store.delete_vector_memory(memory_id)
            if deleted:
                return {"success": True, "data": {"message": f"Forgot memory {memory_id}."}, "error": None}
            return {"success": False, "error": f"No memory found with id {memory_id}.", "data": {}}

        if action == "export":
            rows = self.memory.vector_store.list_recent_memories(limit=limit, mem_type=mem_type)
            return {
                "success": True,
                "data": {
                    "count": len(rows),
                    "format": "json",
                    "memories": rows,
                },
                "error": None,
            }

        return {"success": False, "error": f"Unsupported action '{action}'.", "data": {}}
