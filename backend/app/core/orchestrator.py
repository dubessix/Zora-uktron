"""
Ultron Core Cognitive Orchestrator
Coordinates the entire request processing lifecycle from raw text inputs to final LLM response streams.
Integrates Intent Analysis, Confidence Check, Speed Path Decision, Memory Syncing, Personalities,
Structured AI Actions (Requirement: LLM decides widgets, no keyword checks), and Cloud Routing.
"""

import time
import uuid
import datetime
from typing import Dict, Any, Optional, List

from backend.app.core.intent_analyzer import IntentAnalyzer
from backend.app.core.confidence_engine import ConfidenceEngine
from backend.app.core.decision_engine import DecisionEngine
from backend.app.memory.memory_engine import MemoryEngine
from backend.app.brain.llm_router import LLMRouter
from backend.app.personalities.personality_engine import PersonalityEngine, PersonalityState
from backend.app.emotion.zora_trigger import ZoraTrigger

class CognitiveOrchestrator:
    def __init__(
        self,
        intent_analyzer: Optional[IntentAnalyzer] = None,
        confidence_engine: Optional[ConfidenceEngine] = None,
        decision_engine: Optional[DecisionEngine] = None,
        memory_engine: Optional[MemoryEngine] = None,
        llm_router: Optional[LLMRouter] = None,
        personality_engine: Optional[PersonalityEngine] = None,
        zora_trigger: Optional[ZoraTrigger] = None
    ) -> None:
        self.intent_analyzer = intent_analyzer or IntentAnalyzer()
        self.confidence_engine = confidence_engine or ConfidenceEngine()
        self.decision_engine = decision_engine or DecisionEngine()
        self.memory = memory_engine or MemoryEngine()
        self.router = llm_router or LLMRouter()
        self.personalities = personality_engine or PersonalityEngine()
        self.zora_trigger = zora_trigger or ZoraTrigger()
        
        # Local event tracking array (Integrates with WS events in Phase 8)
        self.dispatched_events: List[Dict[str, Any]] = []

    def _dispatch_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Publishes structured personality/emotional event frameworks."""
        event = {
            "event_id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "payload": payload
        }
        self.dispatched_events.append(event)
        print(f"[EVENT_BUS] Published event: {event_type} -> {payload}")

    def _resolve_structured_action(self, user_prompt: str) -> Dict[str, Any]:
        """
        CONSTITUTIONAL DESIGN (Rule 8):
        The AI decides which widget to activate based on user intent and context, not App.jsx.
        Returns a structured action dictionary to be processed by the frontend's WidgetManager.
        """
        clean = user_prompt.lower()
        
        if "todo" in clean or "task" in clean:
            return {"action": "open_widget", "widget_id": "todo"}
        if "reminder" in clean or "alarm" in clean or "timer" in clean or "remind" in clean:
            return {"action": "open_widget", "widget_id": "reminder"}
        if "schedule" in clean or "calendar" in clean or "plan" in clean:
            return {"action": "open_widget", "widget_id": "calendar"}
        if "git" in clean or "branch" in clean:
            return {"action": "open_widget", "widget_id": "git"}
        if "drive" in clean or "downloads" in clean or "explorer" in clean or "folder" in clean or "find" in clean:
            return {"action": "open_widget", "widget_id": "file_explorer"}
        # 'research' must be checked before 'search' to avoid false substrings triggers (e.g. 're-search')
        if "research" in clean:
            return {"action": "open_widget", "widget_id": "deep_research"}
        if "search" in clean:
            return {"action": "open_widget", "widget_id": "universal_search"}
        if "weather" in clean:
            return {"action": "open_widget", "widget_id": "weather"}
        if "stock" in clean or "bitcoin" in clean or "price" in clean or "market" in clean or "tesla" in clean:
            return {"action": "open_widget", "widget_id": "market"}
        if "terminal" in clean or "run" in clean or "process" in clean:
            return {"action": "open_widget", "widget_id": "terminal"}
        if "memory" in clean or "remember" in clean:
            return {"action": "open_widget", "widget_id": "memory"}
        if "notification" in clean or "alert" in clean:
            return {"action": "open_widget", "widget_id": "notification"}
        if "system" in clean or "cpu" in clean or "ram" in clean or "hardware" in clean:
            return {"action": "open_widget", "widget_id": "system"}
        if "optimize" in clean or "refactor" in clean or "quality" in clean:
            return {"action": "open_widget", "widget_id": "code_optimizer"}
        if "graph" in clean or "dependency" in clean or "caller" in clean or "semantic" in clean:
            return {"action": "open_widget", "widget_id": "semantic_code_graph"}
        if "security" in clean or "scan" in clean or "audit" in clean or "vulnerability" in clean:
            return {"action": "open_widget", "widget_id": "security_guardian"}
        if "morning" in clean or "briefing" in clean or "greeting" in clean:
            return {"action": "open_widget", "widget_id": "daily_briefing"}
            
        return {"action": "none"}

    async def process_request(
        self,
        user_prompt: str,
        session_id: str,
        consecutive_errors: int = 0,
        current_hour: int = 12,
        delete_ratio: float = 0.0
    ) -> Dict[str, Any]:
        """
        Asynchronous coordinator running the complete 7-step pipeline.
        Parses intent, checks confidence, evaluates manual/automatic transitions,
        enforces Zora's overlay lifecycle, and returns processed response transactions.
        """
        start_time = time.perf_counter()
        
        # Clear past events for this turn
        self.dispatched_events.clear()

        current_personality = self.personalities.state.active_personality

        # Step 1: DETECT MANUAL SWITCHOVERS
        manual_state = self.personalities.detect_manual_switch(user_prompt)
        if manual_state:
            self._dispatch_event("personality_changed", {
                "active_personality": manual_state.active_personality,
                "reason": manual_state.switch_reason,
                "type": manual_state.switch_type
            })
            current_personality = manual_state.active_personality

        # Step 2: EVALUATE AUTOMATIC TRANSITIONS (Es Score)
        elif current_personality == "ultron":
            should_handoff, stress_score = self.zora_trigger.evaluate_handoff(
                user_prompt=user_prompt,
                consecutive_errors=consecutive_errors,
                current_hour=current_hour,
                delete_ratio=delete_ratio
            )
            
            # Dispatch real-time stress scores
            self._dispatch_event("emotion_score_updated", {
                "stress_score": stress_score,
                "threshold": self.zora_trigger.threshold
            })

            if should_handoff:
                self._dispatch_event("handoff_started", {
                    "source": "ultron",
                    "target": "zora",
                    "reason": f"Stress Score {stress_score:.3f} exceeded threshold."
                })
                
                self.personalities.update_state(
                    personality="zora",
                    reason=f"Auto-handoff: Stress score {stress_score:.3f} reached.",
                    switch_type="automatic"
                )
                
                self._dispatch_event("personality_changed", {
                    "active_personality": "zora",
                    "reason": self.personalities.state.switch_reason,
                    "type": self.personalities.state.switch_type
                })
                
                self._dispatch_event("handoff_completed", {
                    "active_personality": "zora"
                })
                current_personality = "zora"

        # Step 3: ANALYZE INTENT
        intent = self.intent_analyzer.analyze(user_prompt)

        # Step 4: COMPUTE CONFIDENCE
        confidence = self.confidence_engine.calculate_confidence(user_prompt, intent)

        # Step 5: DECIDE SPEED TRACK
        speed_track = self.decision_engine.get_speed_track(intent, confidence)

        # Step 6: CACHE DECOUPLED POLICY CHECK
        cache_skip = self.router.cache_policy.should_bypass_cache("", user_prompt)

        # Step 7: RESOLVE STRUCTURED AI ACTION (Constitution Rule 8)
        structured_action = self._resolve_structured_action(user_prompt)

        # Step 8: HANDLE LOW CONFIDENCE (VAGUE INPUTS)
        if confidence < 0.60:
            clarification_response = (
                "I'm not entirely sure I follow, Debjeet. Your request lacks context. "
                "Could you clarify what specific file, tool, or goal you want to work on?"
            )
            
            # Save memory with complete standard metadata
            memory_meta = {
                "personality": current_personality,
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "memory_type": "short_term",
                "confidence": confidence
            }
            self.memory.save_chat_turn(user_prompt, clarification_response)
            
            end_time = time.perf_counter()
            response_ms = int((end_time - start_time) * 1000)
            
            # Handle Zora automatic lifecycle decrement even during vague inputs
            if current_personality == "zora":
                auto_return_state = self.personalities.increment_zora_lifecycle()
                if auto_return_state:
                    self._dispatch_event("personality_changed", {
                        "active_personality": "ultron",
                        "reason": auto_return_state.switch_reason,
                        "type": auto_return_state.switch_type
                    })
            
            return {
                "id": str(uuid.uuid4()),
                "content": clarification_response,
                "intent": intent,
                "confidence": confidence,
                "speed_track": speed_track,
                "cache_skip": cache_skip,
                "response_ms": response_ms,
                "active_personality": current_personality,
                "events": list(self.dispatched_events),
                "metadata": memory_meta,
                "structured_action": {"action": "none"}
            }

        # Step 9: CONTEXT ASSEMBLY & SYSTEM INSTRUCTIONS
        short_term_context = self.memory.short_term.get_context_history()
        formatted_history = ""
        for turn in short_term_context[-5:]:
            formatted_history += f"User: {turn['user']}\nAI: {turn['ai']}\n"

        active_profile = self.personalities.get_personality(current_personality)
        system_prompt = active_profile.get_system_prompt(formatted_history)

        # Step 10: ROUTE TO LLM CLIENT
        try:
            ai_response = await self.router.get_completions(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                provider_preference="groq"
            )
        except Exception as err:
            print(f"[COGNITIVE_ORCHESTRATOR] Critical: LLM completion failed: {err}")
            ai_response = "I encountered a network timeout while connecting to my core brain, Debjeet. Let me try resetting the keys."

        # Sync transaction back to short term memory
        self.memory.save_chat_turn(user_prompt, ai_response)

        # Step 11: ZORA OVERLAY LIFECYCLE DECREMENT
        if current_personality == "zora":
            auto_return_state = self.personalities.increment_zora_lifecycle()
            if auto_return_state:
                self._dispatch_event("personality_changed", {
                    "active_personality": "ultron",
                    "reason": auto_return_state.switch_reason,
                    "type": auto_return_state.switch_type
                })

        end_time = time.perf_counter()
        response_ms = int((end_time - start_time) * 1000)

        # Compile standard memory metadata parameters
        memory_meta = {
            "personality": current_personality,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "memory_type": "short_term",
            "confidence": confidence
        }

        return {
            "id": str(uuid.uuid4()),
            "content": ai_response,
            "intent": intent,
            "confidence": confidence,
            "speed_track": speed_track,
            "cache_skip": cache_skip,
            "response_ms": response_ms,
            "active_personality": current_personality,
            "events": list(self.dispatched_events),
            "metadata": memory_meta,
            "structured_action": structured_action
        }

    async def close(self) -> None:
        """Saves persistent caches and closes active async connections cleanly."""
        self.router.cache.save_to_disk()
        await self.router.close()
