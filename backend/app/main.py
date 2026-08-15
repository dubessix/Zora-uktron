"""
Ultron Core Backend Application Service (FastAPI)
Bridges communication logs, WS routing maps, and system health status.
Registers WebSocket endpoints natively for real-time tokens, logs, and dashboard streams.
"""

import time
import os
import json
import asyncio
import platform
import psutil
import datetime
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import database, routing, and websocket engines
from backend.app.database.db import get_db_connection
from backend.app.database.models import initialize_database
from backend.app.router import api_router
from backend.app.websocket.connection_manager import WebSocketManager

# Initialize the global application registry
app = FastAPI(
    title="ULTRON CORE ENGINE API",
    description="Asynchronous processing gateway for local system automation and developer chat.",
    version="1.0.0",
)

# Configure Cross-Origin Resource Sharing (CORS) limits
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount core REST routes
app.include_router(api_router)

# Initialize the global, thread-safe WebSocket Connection Coordinator
ws_manager = WebSocketManager()

class HealthStatusResponse(BaseModel):
    status: str
    uptime_seconds: float
    system_metrics: dict
    environment: dict
    providers: dict
    provider_key_states: dict
    models: dict

# Boot timestamp tracker
START_TIME = time.time()

async def run_reminder_scheduler():
    """
    Background scheduler loop that runs every 5 seconds to look for
    pending or snoozed reminders/alarms whose target_time is <= now.
    If triggered, broadcasts an event to /ws/events and updates their database status.
    """
    print("[SCHEDULER] Starting background reminders and alarms scheduler...")
    while True:
        try:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Find due reminders
                cursor.execute(
                    """
                    SELECT id, type, title, description, target_time, recurrence, recurrence_details, snooze_count, status
                    FROM reminders_alarms
                    WHERE status IN ('pending', 'snoozed') AND target_time <= ?;
                    """,
                    (now_iso,)
                )
                due_rows = cursor.fetchall()
                
                for row in due_rows:
                    item = dict(row)
                    item_id = item["id"]
                    title = item["title"]
                    type_val = item["type"]
                    rec = (item["recurrence"] or "one_time").lower()
                    
                    print(f"[SCHEDULER] Triggering {type_val} '{title}' (ID: {item_id})")
                    
                    # 1. Update database status
                    if rec == "one_time":
                        cursor.execute("UPDATE reminders_alarms SET status = 'triggered' WHERE id = ?;", (item_id,))
                    else:
                        # Auto-recurrence calculations: calculate the next target time
                        current_target = datetime.datetime.fromisoformat(item["target_time"])
                        if rec == "daily":
                            next_target = current_target + datetime.timedelta(days=1)
                        elif rec == "weekly":
                            next_target = current_target + datetime.timedelta(days=7)
                        else:
                            next_target = current_target + datetime.timedelta(minutes=5)
                        
                        cursor.execute(
                            """
                            UPDATE reminders_alarms 
                            SET target_time = ?, status = 'pending', snooze_count = 0 
                            WHERE id = ?;
                            """,
                            (next_target.isoformat(), item_id)
                        )
                    conn.commit()
                    
                    # 2. Broadcast WebSocket event on the 'events' channel
                    event_payload = {
                        "type": "reminder_triggered",
                        "reminder": {
                            "id": item_id,
                            "type": type_val,
                            "title": title,
                            "description": item["description"],
                            "recurrence": rec,
                            "snooze_count": item["snooze_count"]
                        }
                    }
                    await ws_manager.broadcast("events", event_payload)
                    
        except Exception as e:
            print(f"[SCHEDULER] Error in scheduler loop: {e}")
            
        await asyncio.sleep(5.0)

async def run_emergency_monitor():
    """
    Background emergency monitor loop that runs every 60 seconds to scan
    USGS live APIs for catastrophic natural events (earthquakes > 7.0 magnitude).
    If triggered, broadcasts critical alerts on /ws/events for real-time notification.
    """
    print("[EMERGENCY_MONITOR] Launching real-time global emergency monitoring loop...")
    last_triggered_event_id = None
    while True:
        try:
            # Query USGS live GeoJSON endpoint for recent significant earthquakes
            url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=6.5&limit=1"
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    features = res.json().get("features", [])
                    if features:
                        f = features[0]
                        f_id = f.get("id")
                        props = f.get("properties", {})
                        mag = float(props.get("mag", 0.0))
                        
                        # Trigger emergency protocol if magnitude is strictly > 7.0
                        if mag >= 7.0 and f_id != last_triggered_event_id:
                            last_triggered_event_id = f_id
                            
                            # Compile real-time alert payload
                            event_payload = {
                                "type": "emergency_alert",
                                "emergency": {
                                    "category": "Natural Disaster",
                                    "title": f"CRITICAL EARTHQUAKE MAGNITUDE {mag} DETECTED",
                                    "detail": props.get("title"),
                                    "source": "USGS Real-Time Detection System",
                                    "severity": "CRITICAL"
                                }
                            }
                            await ws_manager.broadcast("events", event_payload)
                            print(f"[EMERGENCY_MONITOR] Broadcasted Emergency Alert: {props.get('title')}")
        except Exception as e:
            print(f"[EMERGENCY_MONITOR] Error checking live emergency feeds: {e}")
            
        await asyncio.sleep(120.0)

async def run_proactive_intelligence_loop():
    """
    PROACTIVE INTELLIGENCE LOOP (Requirements 8 & 9)
    1. Check Downloads folder file count. If > 50, automatically trigger OrganizeFolderTool.
    2. At 08:00 AM, compile DailyBriefingTool and push events to /ws/events.
    """
    print("[PROACTIVE_INTELLIGENCE] Starting proactive auto-organizer and morning briefing loops...")
    last_briefing_date = None
    
    while True:
        try:
            # --- 1. Downloads auto-organizer removed (manual-only now for safety).
            #     Use "organize my downloads" to trigger OrganizeFolderTool explicitly.

            # --- 2. Morning 08:00 AM Auto-Briefing Trigger (fires once per hour) ---
            now = datetime.datetime.now()
            today_str = now.date().isoformat()
            
            # Fire once during the whole 8 o'clock hour (not just minute==0, which a
            # 120s loop can miss).
            if now.hour == 8 and today_str != last_briefing_date:
                last_briefing_date = today_str
                print("[PROACTIVE_INTELLIGENCE] It is 08:00 AM. Compiling and broadcasting Daily Briefing...")
                from backend.app.tools.daily_briefing_tool import DailyBriefingTool
                tool = DailyBriefingTool()
                res = await tool.execute()
                if res.get("success"):
                    event_payload = {
                        "type": "daily_briefing_triggered",
                        "briefing": res["data"]
                    }
                    await ws_manager.broadcast("events", event_payload)
                    
        except Exception as e:
            print(f"[PROACTIVE_INTELLIGENCE] Loop exception: {e}")
            
        await asyncio.sleep(120.0)

@app.on_event("startup")
async def startup_event_handler():
    """Initializes standard SQLite databases and applies parameterized table migrations."""
    try:
        with get_db_connection() as conn:
            initialize_database(conn)
            print("[INFO] Database successfully initialized with WAL mode enabled.")

        from backend.app.brain.model_config import validate_model_config
        from backend.app.router import get_orchestrator
        model_status = validate_model_config()
        if not model_status["valid"]:
            raise RuntimeError("Invalid model configuration: " + "; ".join(model_status["errors"]))
        orchestrator = get_orchestrator()
        print(f"[INFO] Effective AI models: {model_status['models']}")
        print(f"[INFO] Provider configuration: {orchestrator.router.key_manager.config_status()}")

        # Launch non-blocking background scheduler, emergency monitor, and proactive intelligence tasks
        asyncio.create_task(run_reminder_scheduler())
        asyncio.create_task(run_emergency_monitor())
        asyncio.create_task(run_proactive_intelligence_loop())
    except Exception as e:
        print(f"[ERROR] Database migration crash during startup execution: {e}")
        raise SystemExit("Core startup database initialization failure.") from e


@app.on_event("shutdown")
async def shutdown_event_handler():
    """
    Close the shared orchestrator exactly once at application shutdown.

    The orchestrator is shared across ALL sessions and owns the persistent HTTPX
    client + smart-cache state. It must NOT be closed per-WebSocket-disconnect
    (that previously killed the client mid-session and broke later chat).
    """
    try:
        from backend.app.router import get_orchestrator
        orch = get_orchestrator()
        await orch.close()
        print("[INFO] Shared orchestrator closed cleanly at shutdown.")
    except Exception as e:
        print(f"[WARN] Shared orchestrator close during shutdown failed: {e}")

@app.get("/api/health", response_model=HealthStatusResponse, status_code=status.HTTP_200_OK)
async def get_health_status() -> dict:
    """Retrieve active backend processing status and local system resource consumption metrics."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    metrics = {
        "memory_rss_mb": memory_info.rss / (1024 ** 2),
        "cpu_percent": process.cpu_percent(interval=None),
        "total_system_ram_usage_percent": psutil.virtual_memory().percent,
    }
    
    env_details = {
        "os_platform": platform.system(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
    }

    # Honest provider config status (which providers have a key configured).
    # This is a config check, not a live reachability test.
    from backend.app.brain.model_config import validate_model_config
    from backend.app.router import get_orchestrator
    # Report the state of the actual shared router, not a freshly-created key
    # manager that would hide cooling/failed runtime keys.
    key_manager = get_orchestrator().router.key_manager
    providers = key_manager.config_status()
    model_config = validate_model_config()

    return {
        "status": "healthy" if model_config["valid"] else "degraded",
        "uptime_seconds": time.time() - START_TIME,
        "system_metrics": metrics,
        "environment": env_details,
        "providers": providers,
        "provider_key_states": key_manager.runtime_status(),
        "models": model_config,
    }

# ==============================================================================
# WEBSOCKET CHANNELS ENDPOINT REGISTRATION (Requirement 1, 2)
# ==============================================================================

def _open_task_count() -> int:
    """Real number of open (not done) tasks, read from the DB — no fake counts."""
    try:
        with get_db_connection() as conn:
            row = conn.cursor().execute(
                "SELECT COUNT(*) AS c FROM project_tasks WHERE status != 'done';"
            ).fetchone()
            return int(row["c"]) if row else 0
    except Exception as e:
        print(f"[WS_CHAT] Could not read task count: {e}")
        return 0


def _widget_payload(widget_id: str) -> dict:
    """Real per-widget data for the widget push. Uses live DB counts, never fakes."""
    if widget_id == "todo":
        return {"todos_count": _open_task_count()}
    return {}


@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket, client_id: str = "default_client"):
    """
    Main dialogue streaming channel.
    Accepts user text, runs the shared canonical chat service (same pipeline as
    /api/chat), and streams the result token-by-token with progress + widget pushes.
    """
    await ws_manager.connect("chat", client_id, websocket)
    from backend.app.router import get_orchestrator
    from backend.app.services.chat_service import process_chat_message
    orchestrator = get_orchestrator()  # shared — do NOT close it on disconnect

    try:
        while True:
            # Await incoming message payload from client
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
                prompt = (data.get("content", "") or "").strip()
                session_id = data.get("session_id", "default_sess")
                has_confirmed = bool(data.get("has_confirmed", False))
                confirmation_token = data.get("confirmation_token")
            except Exception:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format."})
                continue

            if not prompt:
                continue

            # 1. Dispatch starting progress signal
            await websocket.send_json({
                "type": "progress",
                "state": "thinking",
                "detail": "Ultron Orchestrator is running intent heuristics..."
            })

            # 2. Process query via the shared canonical chat service (persists to DB,
            #    resolves/creates the session, restores the per-session personality).
            result = await process_chat_message(
                orchestrator=orchestrator,
                content=prompt,
                session_id=session_id,
                has_confirmed=has_confirmed,
                confirmation_token=confirmation_token,
            )

            # 3. Stream token-by-token (Requirement 1)
            response_content = result["content"] or ""
            await websocket.send_json({"type": "stream_start"})
            words = response_content.split(" ")
            for idx, word in enumerate(words):
                packet = f"{word} " if idx < len(words) - 1 else word
                await websocket.send_json({"type": "token", "content": packet})
                await asyncio.sleep(0.02)
            await websocket.send_json({"type": "stream_end"})

            # 4. Publish any events fired during the orchestrator pipeline
            for event in result.get("events", []):
                await ws_manager.broadcast("events", event)

            # 5. Push a real widget trigger based on the structured action
            structured_action = result.get("structured_action") or {}
            if structured_action.get("action") == "open_widget":
                widget_id = structured_action.get("widget_id", "")
                if widget_id:
                    await websocket.send_json({
                        "type": "widget",
                        "widget_id": widget_id,
                        "action": "open",
                        "data": _widget_payload(widget_id),
                    })

            # 6. Dispatch final transaction confirmation (includes structured_action
            #    and the resolved session_id so clients stay in sync)
            await websocket.send_json({
                "type": "done",
                "message_id": result["id"],
                "session_id": result["session_id"],
                "active_personality": result["personality"],
                "response_ms": result["response_ms"],
                "coding": result["coding"],
                "intent": result["intent"],
                "structured_action": result["structured_action"],
                "events": result.get("events", []),
                "provider_route": result.get("provider_route") or {},
            })

    except WebSocketDisconnect:
        ws_manager.disconnect("chat", client_id)
        # The orchestrator is SHARED across sessions and owns the persistent HTTPX
        # client. Closing it here would break every later chat. It is only closed
        # once, at application shutdown.
    except Exception as e:
        print(f"[WS_CHAT] Error on active chat pipeline: {e}")
        ws_manager.disconnect("chat", client_id)

@app.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket, client_id: str = "default_client"):
    """Server-initiated push channel. Broadcasters trigger alerts, reminders, and Zora auto-handoffs."""
    await ws_manager.connect("events", client_id, websocket)
    try:
        while True:
            # Keeps connection alive and responsive to ping-pong frames
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect("events", client_id)

@app.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket, client_id: str = "default_client"):
    """Streams terminal subprocess and local server logging actions in real-time."""
    await ws_manager.connect("logs", client_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect("logs", client_id)

@app.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket, client_id: str = "default_client"):
    """Pushes local CPU/RAM hardware utilization and session metrics on intervals (Push-on-Change)."""
    await ws_manager.connect("dashboard", client_id, websocket)
    try:
        last_ram = 0.0
        while True:
            process = psutil.Process(os.getpid())
            ram_mb = process.memory_info().rss / (1024 ** 2)
            cpu_percent = process.cpu_percent(interval=None)
            
            # Push only on meaningful change (>0.5MB or 1% CPU) to keep CPU under 2% standard limits
            if abs(ram_mb - last_ram) > 0.5:
                payload = {
                    "type": "dashboard_update",
                    "metrics": {
                        "ram_mb": ram_mb,
                        "cpu_percent": cpu_percent,
                        "total_ram_usage_percent": psutil.virtual_memory().percent
                    }
                }
                await websocket.send_json(payload)
                last_ram = ram_mb
                
            # Yield event loop and sleep for 5 seconds to prevent background thread hogging
            await asyncio.sleep(5.0)
            
    except WebSocketDisconnect:
        ws_manager.disconnect("dashboard", client_id)
    except Exception:
        ws_manager.disconnect("dashboard", client_id)
