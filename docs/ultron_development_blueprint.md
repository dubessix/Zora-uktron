# Ultron V1 Sprints Master Blueprint
*Document Version: 1.0.4 — Synchronized Sprints 0-11 Master Blueprint*

This document serves as the synchronized master blueprint for the Ultron V1 Cognitive Operating System. It reflects the exact implemented state of all Phases 0-11.

---

## 1. Project Vision

*   **Name**: ULTRON V1
*   **Tagline**: Personal AI Developer Partner + Companion
*   **Target Machine Constraints**: Windows 11 & Linux Ubuntu 24.04 (8GB RAM, 256GB SSD)
*   **Memory Budget**: Idle RAM $<350\text{MB}$, normal active RAM $<3.0\text{GB}$.
*   **Core Philosophy**: Understand first, execute with minimal tools, run heavy AI in cloud via multi-key routing, maintain absolute conversation history, and project complete, organic, non-robotic partner personality.

---

## 2. Completed Phase Implementations (Phases 0 - 11)

### Phase 0: Foundation Skeleton
Empty cross-platform concurrent launcher, click CLI admin diagnostics (`ultron setup`, `ultron doctor`), FastAPI REST framework, and React+Tailwind UI workspace running under a single command.

### Phase 1: Basic Chat Infrastructure
Ecosystem persistence layers. Deployed SQLite with Write-Ahead Logging (WAL) and synchronousNormal connections. Designed `/api/chat` and `/api/history` REST routers, saving conversations to SQLite.

### Phase 2: LLM Brain Connection
Key coordination and failover. Designed `APIKeyManager` coordinating 3 Groq and 2 Gemini keys with 429 cooling counters. Built `SmartCache` managing 200 LRU-TTL elements on RAM/Disk, and `LLMRouter` managing async HTTPX failovers. Implemented `BaseCachePolicy` under the **Dependency Inversion Principle**.

### Phase 3: Memory Foundations
Basic relational data buffers. Built `ShortTermMemory` managing 50-turn sliding windows in RAM, `PersistentMemory` saving permanent user configurations, and `ProjectMemory` tracking active development tech stacks.

### Phase 4: Cognitive Orchestrator
Cognitive query pipelines. Deployed `IntentAnalyzer` categorizing prompts into 6 intent states, `ConfidenceEngine` filtering out vague commands ($<60\%$ confidence asks a single clarifying question), and `DecisionEngine` mapping speed paths (`fast`, `medium`, `heavy`).

### Phase 5: Full Vector Memory
Low-RAM hybrid vector indexes. Connected Gemini `text-embedding-004` cloud API, storing 768-dimension arrays in SQLite as float32 binary BLOBs. Search executes local Cosine Similarity math using pure NumPy arrays in **$<10\text{ms}$** with **0MB local static memory overhead**. Employs **Duplicate Write Prevention** ($Similarity > 0.95$ blocks writes) and a semantic **Memory Gate** to filter greetings.

### Phase 6: Dual Personalities Engine
Refactored, SOLID-compliant identity state engine:
*   **Decoupled Prompts**: Ultron and Zora prompts are loaded and cached from `/app/personalities/ultron.md` and `/backend/app/personalities/zora.md`.
*   **PersonalityState Model**: Tracks `active_personality`, `switch_reason`, `switch_type`, and UTC ISO timestamps.
*   **Extensible Signal Analyzer (OCP)**: Stress Score ($E_s$) is calculated dynamically by registered, decoupled signal classes (`CompileErrorSignal`, `LateNightSignal`, etc.), conforming perfectly to the **Open/Closed Principle**.
*   **Zora Temporary Overlay Lifecycle**: Monitors active turns; once they exceed `cooldown_turns` (default 3), the engine automatically auto-returns state back to Ultron.
*   **Dynamic WS Events**: Dispatches structured event payloads (`personality_changed`, `emotion_score_updated`, `handoff_started`, `handoff_completed`) for WebSocket integration.

### Phase 7: Tool Execution & Security System
Refactored, SOLID-compliant, OCP-compliant local system automation and security boundary:
*   **Declarative BaseTool ABC & Standard ToolResult**: Enforces strict Pydantic argument verification (`args_model`) and required security levels. Every tool returns the exact, standard JSON structure model.
*   **Security Permission Manager**: Maps four security clearance levels (Level 0: Read-Only to Level 3: Dangerous/Destructive).
*   **Confirmation Gate Interceptor**: Pauses execution and returns `PENDING_CONFIRMATION` status on Level 2/3 tools (such as terminal runner or deletes) until explicitly confirmed.
*   **Asynchronous Non-blocking Subprocess runner**: Uses `asyncio.create_subprocess_shell` to execute console commands without blocking the event loop.
*   **Tool Context Builder**: Filters relevant tools based on user prompt tags to minimize LLM token waste.
*   **Persistent SQLite Audit Logger**: Automatically records every single tool transaction (args, duration, success, errors) in SQLite database table `tool_audit_logs`.
*   **V1 Tools Deployed**: Deployed `FileReadTool` (Level 0), `FileWriteTool` (Level 1), and `TerminalRunTool` (Level 2).

### Phase 8: WebSocket Streaming Layer
Asynchronous real-time streaming communication and notifications gateway:
*   **Multi-Channel WebSocketManager**: Thread-safe manager registering clients under 4 designated channels (`chat`, `events`, `logs`, `dashboard`).
*   **Continuous Word Streaming**: /ws/chat parses user prompt inputs, executes the orchestrator, and streams AI output words progressively as `type: "token"` packets.
*   **Active Widget Pushes**: Pushes floating widget popups (e.g. `TodoWidget`) directly to the client over websockets.
*   **Active Event Broadcasting**: Pushes background system reminders, compilation logs, and active Zora auto-handoff transitions natively to the client.
*   **Push-on-Change Telemetry**: /ws/dashboard reads system CPU and memory via `psutil`, pushing updates only on change with 5s delay intervals, keeping CPU strictly **$<2.0\%$** to fit 8GB host machine.
*   **Clean Disconnect Prunes**: Automatically drops closed sockets on-the-fly, preventing memory leaks.

### Phase 9: Duplex Voice System
Asynchronous cloud-accelerated voice synthesis and interruption processing:
*   **Strategy Pattern Abstraction**: `BaseVoiceProvider` abstract interface classes.
*   **MS Edge Neural Synthesizer**: `EdgeTTSProvider` streaming binary voice chunks from cloud neural endpoints, avoiding local neural model footprint overhead.
*   **Config-Driven Personalities**: Ultron and Zora prompts mapped to separate voices (`en-US-GuyNeural` vs `en-US-EmmaNeural`) and speed ratios.
*   **Active Event Bus Sync**: Emits seven standardized events (`listening_started`, `speech_detected`, `thinking_started`, `speaking_started`, `interrupted`, `playback_finished`, `idle`).
*   **Barge-In Interrupt Handler**: Instantly cancels active async speech synthesis tasks upon WebSocket interrupt triggers.

### Phase 10: Particle Canvas Blob UI
Widescreen glassmorphism dashboard layout and asynchronous Canvas 2D Particle Core:
*   **AppShell 3-Pane OS Grid**: Wraps LeftPanel, Center Workspace, and RightPanel under a widescreen grid layout with zero clutter or clunky third-party icon libraries.
*   **Omitted Vision Feed**: Legacy Vision Feed box completely removed from Left Panel to optimize vertical space and slide up network telemetry logs.
*   **Canvas 2D Particle sphere Core**: Renders 200 dynamic coordinates forming a floating particle sphere core.
*   **Tilted Orbital concentric loops**: Implements dual overlapping elliptical orbital loops rotating asynchronously under standard 2D rotation transforms.
*   **Active Web Audio bindings**: Core particle loop breathing rates, swirling velocity, and color lerps smoothly synchronize with ws/chat progress packets and speaking statuses.

### Phase 11: Draggable Glass Widgets & V2 Tools
High-performance, floating glassmorphism widgets overlay system and un-mocked V2 local system loaders:
*   **Custom useDraggable Hook**: Tracks raw pointer coordinates, modifying hardware-accelerated translate3d transforms directly to keep client CPU utilization **$<0.5\%$**.
*   **WidgetContainer Wrapper**: Translucent glassmorphic modal displaying close triggers and double-click collapse triggers, satisfying requirements that widgets remember collapsed states.
*   **Productivity & V2 Tools Deployed**: Deployed `FolderTools` (unzipped directory movers, creators, and **un-mocked, fully automatic folder organization subsystems**), `BrowserTools` (un-mocked URL tab launch, close tab, refresh, and scraping scripts), `WebSearchTools` (Google, GitHub, and StackOverflow targeted searches), `MusicTools` (ALSA volume mixers, stop music, next/prev track and sound process launchers), and `SpotifyTools` (Spotify local client deep link and DBus current track status metadata trackers).
*   **SOLID/OCP Extensible Catalog**: Standardized layout facilitates dynamic additions of more widgets (e.g. Weather or Research trackers) in under 5 minutes without altering the app shell.
*   **Pruned Heavy UI Automation (YAGNI / 8GB RAM Guard)**:
    *   *Decision*: Completely pruned and deleted complex OS-level GUI wrappers like `keyboard_controller` and `window_manager` from our roadmap. They require heavy local library hooks (`pywin32` / `X11`) which block thread loops, trigger security antivirus blocks, and consume over **$150\text{MB}$ of static memory**.
    *   *Replacements*: Fully developed and verified the unauthenticated, fast, and keyless **`SystemMetricsTool` (`system_metrics`)** and **`WeatherTool` (`weather_tool`)** instead, keeping backend idle RAM consistently **$<120\text{MB}$**.

---

## 3. Future Sprints Roadmap (Phase 12)

```
                            FUTURE MILESTONES (PHASES 12)
+-----------------------------------------------------------------------------------------+
| PHASE 12: ADMINISTRATIVE POLISH (Weeks 21-22)                                           |
|  - Add slide-out history list panel and sliding bottom type-mode toggles.               |
|  - Run complete integration load-testing under 8GB conditions, ensuring full green.     |
+-----------------------------------------------------------------------------------------+
```
