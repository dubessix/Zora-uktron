# Ultron V1: Backend File Structure & Module Index
*Document Version: 1.0.5 — Sprints 0-11 Backend Index*

This document provides a highly detailed, file-by-file index of the Ultron V1 FastAPI backend. For every file, we specify its precise purpose, public classes, functions, caller modules, and downstream dependencies.

---

## 1. Database & Persistence Layer (`backend/app/database/`)

### `db.py`
*   **Responsibility**: Establishes thread-safe local connections to SQLite and enforces WAL-mode concurrency.

### `models.py`
*   **Responsibility**: Performs database table migrations and holds raw SQL parameter transaction scripts.

---

## 2. LLM Brain & Caching Layer (`backend/app/brain/`)

### `api_key_manager.py`
*   **Responsibility**: Coordinates pool of 3 Groq and 2 Gemini keys, managing round-robin rotators and 429 cooldowns.

### `smart_cache.py`
*   **Responsibility**: Lightweight, persistent LRU-TTL cache managing up to 200 items in-memory.

### `cache_policy.py`
*   **Responsibility**: Abstract interface defining SOLID cache bypassing behaviors.

### `llm_router.py`
*   **Responsibility**: Async HTTPX pool connection client handling Groq-to-Gemini automatic failovers.

---

## 3. Memory Subsystem Layers (`backend/app/memory/`)

### `short_term.py`
*   **Responsibility**: RAM-based dialogue sliding deque limited to 50 turns.

### `vector_store.py`
*   **Responsibility**: Coordinates with Gemini embeddings and runs local NumPy Cosine Similarity. Loads parameters dynamically.

### `memory_gate.py`
*   **Responsibility**: Bypasses vector searches for low-density greetings based on config lists, saving cloud API tokens.

---

## 4. Personalities & Emotional State Layers

### `/personalities/base_personality.py`
*   **Responsibility**: Strict base ABC interface for personalities. Loads and caches markdown prompts.

### `/personalities/personality_engine.py`
*   **Responsibility**: State custodian tracking active `PersonalityState` models and Zora's automatic lifecycle return transitions.

### `/emotion/signal_analyzer.py`
*   **Responsibility**: OCP-compliant, modular stress signal classes evaluating Stress Scores ($E_s$).

### `/emotion/zora_trigger.py`
*   **Responsibility**: Compares calculated $E_s$ against config thresholds, triggering handoffs.

---

## 5. Tool System & Security Gate (`backend/app/tools/` & `/security/`)

### `tools/tool_base.py`
*   **Responsibility**: Abstract Base Class `BaseTool`. Enforces required security levels, category, tags, and Pydantic input schemas. Declares standard `ToolResult` validation schema model.

### `tools/filesystem_tools.py`
*   **Responsibility**: Deployed filesystem automation utilities with rich metadata properties.

### `tools/system_tools.py`
*   **Responsibility**: Deployed system command shell runner, using non-blocking asynchronous subprocesses, featuring un-mocked Self-Healing compiling loops.

### `tools/folder_tools.py`
*   **Responsibility**: Deployed un-mocked local directory creators, renamers, copiers, and dynamic folders organization automation.

### `tools/browser_tools.py`
*   **Responsibility**: Deployed un-mocked browser tab closer, page refresh, back, forward, and web scraping utilities.

### `tools/web_search_tools.py`
*   **Responsibility**: Deployed un-mocked Google, GitHub, and StackOverflow targeted searches.

### `tools/music_tools.py`
*   **Responsibility**: Deployed un-mocked local play/stop process triggers and ALSA audio mixers.

### `tools/spotify_tools.py`
*   **Responsibility**: Deployed un-mocked local Spotify client trackers and deep-link wrappers.

### `tools/context_builder.py`
*   **Responsibility**: Filters, selects, and packages relevant tool metadata payloads, minimizing prompt token waste.

### `tools/tool_registry.py`
*   **Responsibility**: Coordinates tools list, runs Pydantic input verification, checks Security Gate, executes tools asynchronously under timeout constraints, and logs transactions into SQLite.

### `security/permission_manager.py`
*   **Responsibility**: Maps security levels (0-3) and checks manual authorization triggers.

### `security/confirmation_gate.py`
*   **Responsibility**: Intercepts Level 2/3 queries to return `PENDING_CONFIRMATION` if not explicitly approved.

---

## 6. Real-Time Streaming Subsystem (`backend/app/websocket/`)

### `websocket/connection_manager.py`
*   **Responsibility**: Thread-safe manager registering clients under 4 designated channels (`chat`, `events`, `logs`, `dashboard`) and executing clean connection-drop prunes.

---

## 7. Duplex Voice Subsystem (`backend/app/voice/`)

### `voice/base_voice_provider.py`
*   **Responsibility**: Abstract base class `BaseVoiceProvider` defining the unified speech stream interface contract (Strategy pattern).

### `voice/edge_tts_provider.py`
*   **Responsibility**: Concrete cloud speech client streaming binary packets via MS Edge neural TTS.

### `voice/interrupt_handler.py`
*   **Responsibility**: Tracks active asyncio speech tasks, cancelling them instantly on client-side barge-in interrupts.

### `voice/voice_system.py`
*   **Responsibility**: Central voice coordinator loading settings from config profiles, managing speak lifecycles, and publishing events directly to the Event Bus.

---

## 8. Central Cognitive Pipeline & Server Entry

### `main.py`
*   **Responsibility**: FastAPI startup engine. Hooks database WAL migrations, includes core API routers, and registers the active WebSocket channels (`/ws/chat`, `/ws/events`, `/ws/logs`, `/ws/dashboard`).

### `orchestrator.py`
*   **Responsibility**: The master conductor running the asynchronous 7-step request-to-response pipeline.
