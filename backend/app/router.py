"""
Ultron REST API Router
Bridges user communication requests, message history lists, and session builders.
Supports structured AI action metadata payloads and explicit backend tool execution endpoints.
"""

import time
import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.database.db import get_db_connection
from backend.app.database.models import save_conversation, get_conversation_history, update_session_personality
from backend.app.session.session_manager import SessionManager
from backend.app.core.orchestrator import CognitiveOrchestrator
from backend.app.utils.text_cleaner import clean_text
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

class ChatResponse(BaseModel):
    id: str = Field(..., description="Unique generated message ID.")
    session_id: str = Field(..., description="Active resolved session UUID.")
    content: str = Field(..., description="Processed response content.")
    personality: str = Field(..., description="Active answering persona profile.")
    response_ms: int = Field(..., description="Calculated processing duration.")
    structured_action: Dict[str, Any] = Field(default_factory=dict, description="Structured AI Action metadata payload.")
    coding: bool = Field(False, description="True if this turn was a coding turn (so UI can auto-show the coding panel).")
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
    Processes user text prompts, calculates timing, saves transactions to SQLite,
    and returns a production-ready Echo Response with structured action payloads.
    """
    start_time = time.perf_counter()
    orchestrator = get_orchestrator()  # shared — memory persists across messages
    
    try:
        # 1. Resolve active session
        session_data = SessionManager.get_or_create_session(request.session_id)
        session_id = session_data["id"]
        session_personality = session_data.get("personality") or "ultron"
        
        # 2. Process query async via Orchestrator to resolve structured actions
        result = await orchestrator.process_request(
            user_prompt=request.content,
            session_id=session_id,
            consecutive_errors=0,
            current_hour=datetime.datetime.now().hour,
            delete_ratio=0.0,
            initial_personality=session_personality
        )
        
        # Calculate process latency
        end_time = time.perf_counter()
        latency_ms = int((end_time - start_time) * 1000)
        
        # 3. Save conversational turn directly to the database
        with get_db_connection() as conn:
            # Fix #9: persist active personality on the session.
            try:
                update_session_personality(conn, session_id, result.get("active_personality", "ultron"))
            except Exception:
                pass
            save_conversation(
                conn=conn,
                msg_id=result["id"],
                session_id=session_id,
                user_message=request.content,
                ai_response=result["content"],
                personality=result["active_personality"],
                tools_used=[],
                widget_shown=None,
                intent=result["intent"],
                mode="developer",
                path_used="fast",
                response_ms=latency_ms
            )
            
        return ChatResponse(
            id=result["id"],
            session_id=session_id,
            content=clean_text(result["content"]) if result.get("content") else result["content"],
            personality=result["active_personality"],
            response_ms=latency_ms,
            structured_action=result["structured_action"],
            coding=result.get("coding", False),
            intent=result.get("intent", "")
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
