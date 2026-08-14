"""
Ultron REST API Router
Bridges user communication requests, message history lists, and session builders.
Supports structured AI action metadata payloads and explicit backend tool execution endpoints.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.database.db import get_db_connection
from backend.app.database.models import get_conversation_history
from backend.app.core.orchestrator import CognitiveOrchestrator
from backend.app.tools.tool_registry import ToolRegistry

# Create regional router registry
api_router = APIRouter(prefix="/api")

# Fix #8: shared orchestrator singleton so short-term memory persists across
# requests within the same process (instead of resetting every message).
_shared_orchestrator = None
def get_orchestrator() -> CognitiveOrchestrator:
    global _shared_orchestrator
    if _shared_orchestrator is None:
        _shared_orchestrator = CognitiveOrchestrator()
    return _shared_orchestrator

# --- Pydantic Models for Input Validation and Type Safety ---

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Active unique conversation UUID.")
    content: str = Field(..., min_length=1, description="Raw user prompt query content.")
    has_confirmed: bool = Field(False, description="User confirmation for a pending dangerous tool (delete/terminal).")

class ChatResponse(BaseModel):
    id: str = Field(..., description="Unique generated message ID.")
    session_id: str = Field(..., description="Active resolved session UUID.")
    content: str = Field(..., description="Processed response content.")
    personality: str = Field(..., description="Active answering persona profile.")
    response_ms: int = Field(..., description="Calculated processing duration.")
    structured_action: Dict[str, Any] = Field(default_factory=dict, description="Structured AI Action metadata payload.")
    coding: bool = Field(False, description="True if this turn was a coding turn (so UI can auto-show the coding panel).")
    events: List[dict] = Field(default_factory=list, description="Operational log/event stream for the Log tab.")
    intent: str = Field("", description="Detected intent for the turn.")

class ToolExecuteRequest(BaseModel):
    tool_id: str = Field(..., description="ID of the target registered tool.")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Input arguments to validate and feed to tool execution.")
    has_confirmed: bool = Field(False, description="Explicit user confirmation for Level 2/3 security clearances.")

class CodingModeRequest(BaseModel):
    enabled: bool = Field(..., description="True to force NVIDIA coding mode ON, False to revert to auto-detect.")

class ConversationHistoryItem(BaseModel):
    id: str
    session_id: str
    timestamp: str
    user_message: str
    ai_response: str
    personality: str
    tools_used: List[str]
    widget_shown: Optional[str]
    intent: str
    mode: str
    path_used: str
    response_ms: int

# --- Endpoint Handlers ---

@api_router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def post_chat_message(request: ChatRequest) -> ChatResponse:
    """
    Processes user text prompts through the canonical chat-processing service
    (shared with /ws/chat): resolves the session, restores personality, runs the
    orchestrator, and persists the turn to SQLite.
    """
    from backend.app.services.chat_service import process_chat_message

    orchestrator = get_orchestrator()  # shared — memory persists across messages

    try:
        result = await process_chat_message(
            orchestrator=orchestrator,
            content=request.content,
            session_id=request.session_id,
            has_confirmed=request.has_confirmed,
        )
        return ChatResponse(
            id=result["id"],
            session_id=result["session_id"],
            content=result["content"],
            personality=result["personality"],
            response_ms=result["response_ms"],
            structured_action=result["structured_action"],
            coding=result["coding"],
            intent=result["intent"],
            events=result["events"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message cleanly: {str(e)}"
        )
    # Shared orchestrator is intentionally NOT closed here — it persists across
    # messages for memory. (Its persistent httpx client lives for the process.)

@api_router.post("/tools/execute", status_code=status.HTTP_200_OK)
async def execute_backend_tool(request: ToolExecuteRequest) -> Dict[str, Any]:
    """
    CONSTITUTIONAL DESIGN:
    Exposes a clean REST API interface to directly execute and validate backend tools.
    Provides standard Pydantic schema validation and security level checks.
    """
    registry = ToolRegistry()
    try:
        result = await registry.execute_tool(
            tool_id=request.tool_id,
            args=request.arguments,
            has_confirmed=request.has_confirmed
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution encountered unexpected failure: {str(e)}"
        )

@api_router.get("/history", response_model=List[ConversationHistoryItem], status_code=status.HTTP_200_OK)
async def get_session_history(session_id: str = Query(..., description="Target session UUID.")) -> List[dict]:
    """Retrieves full chronological dialogue history belonging to a specific session."""
    try:
        with get_db_connection() as conn:
            history = get_conversation_history(conn, session_id)
            return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation logs: {str(e)}"
        )

class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to speak.")
    personality: str = Field("ultron", description="Personality voice: ultron or zora.")

@api_router.post("/speak", status_code=status.HTTP_200_OK)
async def speak_text(request: SpeakRequest):
    """Text-to-speech: returns an audio stream (MP3) for the given text."""
    try:
        from backend.app.voice.voice_system import VoiceSystem
        voice = VoiceSystem()
        async def audio_stream():
            async for chunk in voice.speak(request.text, personality=request.personality):
                yield chunk
        return StreamingResponse(audio_stream(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"TTS failed: {e}")

@api_router.get("/memory/recent", status_code=status.HTTP_200_OK)
async def get_recent_memories(limit: int = Query(5, ge=1, le=20)):
    """Real recent memory rows from the vector store (Set B: no fake memory widget)."""
    try:
        from backend.app.database.db import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            total = cursor.execute("SELECT COUNT(*) FROM vector_memories").fetchone()[0]
            cursor.execute(
                "SELECT type, content, created_at FROM vector_memories ORDER BY rowid DESC LIMIT ?",
                (limit,)
            )
            rows = [{"type": r["type"], "content": (r["content"] or "")[:120], "created_at": r["created_at"]} for r in cursor.fetchall()]
        return {"total": total, "memories": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory query failed: {e}")

@api_router.post("/coding-mode", status_code=status.HTTP_200_OK)
async def set_coding_mode(request: CodingModeRequest) -> dict:
    """Manually toggle NVIDIA coding mode on/off for the orchestrator."""
    try:
        orch = CognitiveOrchestrator()
        orch.set_coding_mode(request.enabled)
        return {"success": True, "coding_mode": request.enabled}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle coding mode: {str(e)}"
        )
