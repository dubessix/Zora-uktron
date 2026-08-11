# ULTRON V1: DEFINITIVE ENGINEERING BLUEPRINT & MASTER ROADMAP
*Document Version: 1.2.0 — Jarvis/Friday Organic Behavior & Skill-Based Event-Driven Architecture Refinements*

---

## 1. EXECUTIVE CONSTRAINTS & THE "UNDER 3GB RAM" MASTER STRATEGY

Building a real-time, voice-first, dual-personality developer partner designed to run continuously for **2 years on an 8GB RAM Windows 11/Ubuntu host** requires severe engineering discipline. Windows 11 consumes approximately 3.5GB to 4.5GB of RAM in idle states, leaving a maximum pool of **3.5GB of actual RAM** for VS Code, browser tabs, local SaaS builds, and Ultron.

To meet the strict target of **under 3.0GB RAM in normal use** and **under 4.0GB RAM during active voice operations**, Ultron V1 rejects the industry standard of "local-heavy LLMs/STTs" and embraces an optimized **Cloud-Logic, Local-Control** architecture:

```
+----------------------------------------------------------------------------------------+
|                          ULTRON 8GB RAM SYSTEM ALLOCATION                              |
+----------------------------------------------------------------------------------------+
| [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] Windows 11 + VS Code + Chrome   (approx 4.5 GB) |
| [■■■■■■■■■■■■] FastAPI + SQLite + Vector Store + React Frontend            (approx 1.2 GB) |
| [■■■] Available Safety Buffer                                              (approx 2.3 GB) |
+----------------------------------------------------------------------------------------+
```

### The Three Columns of Ram Optimization:
1. **Client-Side Transruption (Zero-RAM STT)**: Rather than running `Faster-Whisper` locally (which consumes 250MB–400MB static RAM and introduces a 3-5 second model-load delay), the voice system leverages the browser's hardware-accelerated, native **Web Speech API (`webkitSpeechRecognition`)**. This delegates the heavy audio transcription workload to the OS/Cloud, reducing local Python RAM usage to **0MB** and dropping voice startup latency to **under 150ms**.
2. **Serverless Vector Embeddings & Numpy Core**: Instead of loading an in-memory PyTorch/SentenceTransformers model (e.g., `all-MiniLM-L6-v2`, requiring 350MB–500MB RAM), Ultron utilizes Gemini's free `text-embedding-004` API. The resulting vectors are managed using an ultra-lightweight, native Python index built on NumPy and SQLite, utilizing **$<10\text{MB}$ of RAM** even with 10,000 memories.
3. **Lazy Module Loading & Code Splitting**: Expensive Python libraries (such as GitPython, PyAutoGUI, and advanced document parsers) are deferred at startup. FastAPI boots with an essential footprint of under 80MB. Non-essential helper modules are dynamically imported on their first execution and cleared from memory when idle.

---

## 2. MODULE-BY-MODULE TECHNICAL SPECIFICATION

The system is decoupled into 8 specialized modules. Below is the structural layout, component responsibilities, and clear data interaction boundaries:

```
                            +-----------------------------------------+
                            |       React Web Client (Vite)           |
                            |   (Canvas Particle Blob + CSS Glass)    |
                            +----+-------------------------------+----+
                                 |                               |
                   ws_chat / ws_voice / ws_events etc.           HTTP REST
                                 |                               |
                                 v                               v
+-------------------------------------------------------------------------------------+
|                                FastAPI Server Core                                  |
+-------------------------------------------------------------------------------------+
|  +---------------------------+   +---------------------------+   +---------------+  |
|  | Module 1: Orchestrator    |   | Module 2: Switcher/Emotion|   | Module 5: Brain|  |
|  | (Intent & Plan Engine)    |   | (Zora / Ultron Profiles)  |   | (LLM Router)  |  |
|  +-------------+-------------+   +-------------+-------------+   +-------+-------+  |
|                |                               |                         |          |
|                v                               v                         v          |
|  +---------------------------+   +---------------------------+   +---------------+  |
|  | Module 4: Tool Registry   |   | Module 3: Memory Engine   |   | Module 6: Comm|  |
|  | (Permissions & Security)  |   | (SQLite + NumPy BLOB)     |   | (WS Server)   |  |
|  +---------------------------+   +---------------------------+   +---------------+  |
+-------------------------------------------------------------------------------------+
|  +-------------------------------------------------------------------------------+  |
|  | Module 8: Background Task Daemon & System CLI (Launcher, Setup, Doctor)       |  |
+-------------------------------------------------------------------------------------+
```

### Module 1: Core Orchestrator & Cognitive Pipeline (`core/`)
*   **Purpose**: Manages the life cycle of a request. It parses intent, determines execution paths, coordinates tools, and streams structured tokens back to the user.
*   **Key Components**:
    *   `orchestrator.py`: Main execution runner coordinating steps 1 through 7.
    *   `intent_analyzer.py`: Leverages a lightweight semantic classification model to analyze user inputs, outputting the category (e.g., `Git`, `Research`, `Planning`) and confidence score.
    *   `decision_engine.py`: Directs inputs into three logical processing speeds:
        *   *Fast Path*: Direct chat, template matches, or cache hits ($\approx 1\text{--}3\text{s}$). skips planning entirely.
        *   *Medium Path*: Requests requiring a single tool lookup (e.g., "What files are in `/src`?") ($\approx 2\text{--}5\text{s}$).
        *   *Heavy Path*: Complex orchestration (e.g., "Analyze my git status, check my database schema, and plan my next sprint") ($\approx 5\text{--}15\text{s}$). Runs the dynamic planner.
    *   `planner.py` & `parallel_executor.py`: Translates complex requests into a Directed Acyclic Graph (DAG) of dependency-resolved execution steps. Executes independent tasks concurrently using Python's asynchronous thread pool.
    *   `result_reviewer.py`: Compares the combined tool outputs against the developer's original request. If inconsistencies or errors are detected, it schedules a self-healing retry.

### Module 2: Dual-Personality & Emotion Engine (`personalities/`, `emotion/`)
*   **Purpose**: Tracks and manages conversational personalities (Ultron and Zora), parses cognitive/stress signals, and executes smooth transitions.
*   **Key Components**:
    *   `personality_engine.py`: Injects linguistic guidelines and forbidden constraints (e.g., Zora's strict rule preventing her from saying "I am just an AI") into LLM context builders.
    *   `signal_analyzer.py`: Monitors user telemetry—including average typing speed, rapid short messages, high edit/delete ratios, compiler error recurrence rates, and temporal context.
    *   `zora_trigger.py`: Orchestrates the sliding-window "Emotional Distress/Overwhelm Score". Once the score exceeds a threshold of `0.75`, it schedules an immediate handoff to Zora.
    *   `switcher.py`: Seamlessly merges active context, conversational state, and historical memory between Ultron and Zora.

### Module 3: Unified Memory Engine (`memory/`)
*   **Purpose**: Operates as a single, shared source of truth across six database models.
*   **Key Components**:
    *   `memory_engine.py`: Coordinates lookups and writes across SQLite and vector indices.
    *   `memory_gate.py`: Acts as a fast pre-filter. Before executing slow similarity searches over ChromaDB or local vector files, it performs a heuristic check (regex/key-phrase keyword checking) to see if semantic history is required.
    *   `vector_store.py`: A native Python vector database utilizing NumPy array math. It coordinates with Gemini’s free cloud-based embeddings, saving local CPU and memory.
    *   `memory_cleaner.py`: Performs background operations every 30 days to merge short-term conversational fragments into persistent database entities and clean duplicate records.

### Module 4: Auto-Tool Execution Registry & Permission Gate (`tools/`, `security/`)
*   **Purpose**: Declaratively maps, validates, and runs system, file, and web tools under strict local security guidelines.
*   **Key Components**:
    *   `tool_registry.py` & `tool_base.py`: Implements base classes enforcing input validation (using Pydantic), logging constraints, and execution timelines.
    *   `permission_manager.py`: Assigns security levels (Level 0: Read-Only, Level 1: Write, Level 2: System Commands, Level 3: Dangerous/Destructive).
    *   `confirmation_gate.py`: Detects requests with Level 2/3 security permissions, pauses execution, and pushes a glassmorphic authorization window to the React frontend.

### Module 5: Multi-Key LLM Router & Smart Cache (`brain/`)
*   **Purpose**: Manages resilient connections to cloud LLM APIs with zero service downtime.
*   **Key Components**:
    *   `llm_router.py`: Handles high-volume routing across multiple Groq and Gemini API keys.
    *   `api_key_manager.py`: Performs round-robin rotation, tracks rate-limiting errors (HTTP 429), and marks keys as "cooling" or "failed" dynamically.
    *   `smart_cache.py`: A local LRU cache mapping user questions to past AI responses, responding instantly in under 1 second without hitting cloud APIs.

### Module 6: Live Communication Server (`websocket/`)
*   **Purpose**: Handles raw WebSocket channels for token streams, voice data, events, and telemetry.
*   **Key Components**:
    *   `ws_chat.py`: Streams output tokens, tools in use, and memory triggers in real-time.
    *   `ws_voice.py`: Directs streaming browser-transcribed inputs and packages Edge-TTS output packets.
    *   `ws_events.py`: Handles asynchronous, server-initiated pushed events (e.g., active task progress updates, calendar reminders, and Zora auto-triggers).
    *   `ws_logs.py` & `ws_dashboard.py`: Streams development system telemetry, terminal logs, RAM usage, and session metrics.

### Module 7: React Frontend & Canvas Blob Engine (React Client)
*   **Purpose**: Renders a dark glassmorphic layout, handles draggable widgets, and hosts the interactive visual canvas blob.
*   **Key Components**:
    *   `BlobCanvas.jsx` & `ParticleSystem.jsx`: Executes the fluid SVG gooey-filter canvas loop. Renders ~200 active circular particles responding to center-force physics, voice amplitude, and state changes (Idle, Listening, Thinking, Speaking).
    *   `DragWrapper.jsx` & `WidgetContainer.jsx`: Features glassmorphic, drag-anywhere containers. Avoids bulky dependencies using hardware-accelerated CSS and translation matrices.
    *   `ultronStore.js`: Centralizes client state using Zustand, managing websocket lifecycles, active widgets, and active personality states.

### Module 8: CLI, Bootstrap, and Background Worker (`cli/`, `background/`)
*   **Purpose**: Configures directories, verifies system dependencies, and launches/shuts down sub-services cleanly.
*   **Key Components**:
    *   `ultron.py`: CLI entrypoint providing commands (`setup`, `doctor`, `start`, `stop`).
    *   `launcher.py`: Bootstraps FastAPI and Vite, handling clean process shutdowns.
    *   `task_queue.py`: Standardizes a non-blocking queue (using standard `asyncio`) to run tasks (e.g., large file reading, repo indexing) without freezing the active WS thread.

---

## 3. WEBSOCKET JSON SCHEMAS & COMMUNICATION CONTRACTS

To maintain stable, real-time streaming and synchronization across both ends, all communication over WebSockets is structured using explicit JSON schemas.

### Channel 1: `ws_chat` (Main Conversation & Token Streaming)
**Endpoint**: `ws://localhost:8000/ws/chat`

*   **Client Sends (Message Payload)**:
    ```json
    {
      "type": "user_message",
      "session_id": "sess_20260730_001",
      "content": "Can you check my git status and see if there are any conflicts?"
    }
    ```
*   **Server Streams (Progress Step)**:
    ```json
    {
      "type": "progress",
      "state": "analyzing_git",
      "detail": "Running git status on local repository..."
    }
    ```
*   **Server Streams (Token Payload)**:
    ```json
    {
      "type": "token",
      "content": "You are on "
    }
    ```
*   **Server Streams (Widget Activation)**:
    ```json
    {
      "type": "widget",
      "widget_name": "GitWidget",
      "action": "open",
      "data": {
        "branch": "main",
        "uncommitted_files": ["src/App.jsx", "package.json"],
        "conflicts": []
      }
    }
    ```
*   **Server Streams (Memory Notification)**:
    ```json
    {
      "type": "memory",
      "action": "store_persistent",
      "content": "User is actively refactoring App.jsx using React 19"
    }
    ```
*   **Server Streams (Done signal)**:
    ```json
    {
      "type": "done",
      "tools_used": ["git_tool"],
      "response_time_ms": 2450
    }
    ```

---

### Channel 2: `ws_voice` (Real-Time Audio Duplex & Interrupt)
**Endpoint**: `ws://localhost:8000/ws/voice`

*   **Client Sends (Voice Start)**:
    ```json
    {
      "type": "voice_start"
    }
    ```
*   **Client Sends (Continuous Transcript from Web Speech API)**:
    ```json
    {
      "type": "transcript_chunk",
      "text": "i feel really overwhelmed",
      "is_final": true
    }
    ```
*   **Server Streams (Audio TTS Bytes)**:
    ```json
    {
      "type": "tts_chunk",
      "audio_data": "BASE64_ENCODED_BINARY_AUDIO_BYTES"
    }
    ```
*   **Client Sends (Instant Voice Interrupt / Barge-In)**:
    ```json
    {
      "type": "interrupt",
      "timestamp": "2026-07-30T08:52:10.123Z"
    }
    ```
*   **Server Sends (Acknowledge Interrupt & Stop)**:
    ```json
    {
      "type": "interrupt_acknowledged"
    }
    ```

---

### Channel 3: `ws_events` (Server-Initiated Push Pipeline)
**Endpoint**: `ws://localhost:8000/ws/events`

*   **Server Pushes (Active Zora Trigger Event)**:
    ```json
    {
      "type": "zora_auto_trigger",
      "reason": "6+ hours working past midnight with 5 consecutive compile errors",
      "message": "Hey... You okay? I've been watching you wrestle with this webpack build for a while now. Step away for a second."
    }
    ```
*   **Server Pushes (Active Reminder Trigger)**:
    ```json
    {
      "type": "reminder_trigger",
      "reminder_id": "rem_98452",
      "title": "Deployment webhook testing window starts now",
      "timestamp": "2026-07-30T09:00:00Z"
    }
    ```
*   **Server Pushes (Background Task Finished)**:
    ```json
    {
      "type": "task_done",
      "task_id": "task_index_042",
      "task_type": "repository_indexing",
      "result": {
        "files_indexed": 142,
        "duration_ms": 12400
      }
    }
    ```

---

### Channel 4: `ws_logs` (Telemetry Live Terminal Log Stream)
**Endpoint**: `ws://localhost:8000/ws/logs`

*   **Server Pushes (System Logs)**:
    ```json
    {
      "timestamp": "2026-07-30T08:52:12.001Z",
      "component": "cognitive_orchestrator",
      "level": "INFO",
      "message": "Intent verified as [Git]. Routing to medium-path execution. Confidence: 0.96."
    }
    ```

---

### Channel 5: `ws_dashboard` (Live Statistics Refresh)
**Endpoint**: `ws://localhost:8000/ws/dashboard`

*   **Server Pushes (Hardware and Session Stats)**:
    ```json
    {
      "hardware": {
        "ram_gb": 1.25,
        "cpu_percent": 12.4,
        "disk_free_gb": 142.1
      },
      "memory_stats": {
        "short_term_count": 12,
        "persistent_count": 142,
        "vector_count": 1402
      },
      "productivity": {
        "completed_todos": 5,
        "pending_todos": 12,
        "hours_active_today": 6.5
      }
    }
    ```

---

## 4. DUAL-PERSONALITY STATE MACHINE & HANDOFF MECHANICS

The centerpiece of Ultron's dual personality is the transition mechanics from the technical, focused **Ultron** to the supportive companion **Zora** without manual command requirements.

```
                           +----------------------+
                           |   State: ULTRON      |
                           |   (Active Dev Hub)   |
                           +----------+-----------+
                                      |
                       Automatic Trigger Condition:
                     Overwhelm Score (E_s) > 0.75
                                      |
                                      v
                           +----------------------+
                           |   State: ZORA        |
                           |  (Supportive Hub)    |
                           +----------+-----------+
                                      |
                         Manual / Auto Return Signal:
                     "Let's get back to work" / Calm Down
                                      |
                                      v
                           +----------------------+
                           |   State: ULTRON      |
                           +----------------------+
```

### Mathematical Formulation of the "Overwhelm Score" ($E_s$)

The engine calculates your active stress level $E_s$ continuously using an exponential sliding window ($10\text{ minutes}$):

$$E_s = w_1 \cdot C_{err} + w_2 \cdot T_{midnight} + w_3 \cdot D_{ratio} + w_4 \cdot S_{sentiment}$$

Where:
*   **$C_{err}$ (Compile Errors Metric)**: Calculated as $\min(1.0, \frac{\text{errors}}{4})$. 4 recurring compile errors on the same script in 30 minutes yields a maximum value of `1.0`.
*   **$T_{midnight}$ (Late Work Metric)**: Evaluated as `0.0` before 11:00 PM, scaling linearly to `1.0` by 2:00 AM if active.
*   **$D_{ratio}$ (Delete/Retype Metric)**: Calculated as $\frac{\text{characters deleted}}{\text{characters typed}}$ inside the prompt input box over a 5-minute rolling average. (Higher value represents frustration).
*   **$S_{sentiment}$ (Negative Sentiment Metric)**: Evaluated using a fast, local keyword/phrase density index looking for frustration tags ("I hate", "not working", "give up", "stupid", "impossible").
*   **Weights Matrix**: $w_1 = 0.3$, $w_2 = 0.2$, $w_3 = 0.2$, $w_4 = 0.3$.

### The Handoff Execution Protocol:
1.  **Detection**: The `signal_analyzer.py` calculates $E_s = 0.81$, exceeding the `0.75` trigger threshold.
2.  **Context Assembly**: `zora_trigger.py` queries `SQLite` and extracts current development telemetry (active project details, time spent, recurring errors) and relevant emotional history.
3.  **Handoff Intercept**: `orchestrator.py` pauses any pending developer command threads and shifts the active state pointer to Zora.
4.  **UI Event Notification**: The server pushes `{"type": "zora_auto_trigger"}` over `ws_events`.
5.  **Visual Morph**: The frontend canvas blob morphs from cool blue-white (`#7DD3FC`) to warm gold-pink (`#FBBF24`) over **800ms**. Monospace fonts transition smoothly to elegant, warm sans-serif weights.
6.  **The Intervention**: Zora activates the speaker directly and says: *"Hey, Debjeet. Take your hands off the keyboard for a second. You've been tackling this database driver for hours and it's late. Let's talk about it."*
7.  **Resolution & Recovery**: When you feel ready, saying *"Let's get back to work"* resets the $E_s$ accumulator to `0.0`, shifts the visual state color back, and returns you to Ultron with your current terminal history fully preserved.

---

## 5. STATE MANAGEMENT & BLOB RENDER LOOP

The front-end design is clean, fast, and free of clutter.

```
+-----------------------------------------------------------------------------+
|                                Zustand Store                                |
|   +-------------------+  +-------------------+  +-------------------------+ |
|   |  Active State     |  | Widget Registry   |  | Connection State        | |
|   |  - Personality    |  |  - Active/Closed  |  |  - Connected/Retry      | |
|   |  - Tone Profile   |  |  - Position Coord |  |  - Latency Telemetry    | |
|   +-------------------+  +-------------------+  +-------------------------+ |
+------------------------------------+----------------------------------------+
                                     |
                                     v
                        React Canvas Animation Loop
              +-----------------------------------------------+
              |   Canvas Draw Particles (x, y)                |
              |   Compute Distance matrix from center         |
              |   Apply Simplex Noise Offset                  |
              |   SVG Gooey Filter (Alpha Threshold + Blur)   |
              |   RequestAnimationFrame (Locked at 60 FPS)    |
              +-----------------------------------------------+
```

### Global Store Setup (Zustand Structure)
The client state is managed within a unified store, controlling active personality modes, WS connection states, and widget layout positions:
*   `activeState`: `{ personality: 'ultron' | 'zora', speaking: false, thinking: false, listening: false }`
*   `widgetRegistry`: Tracks active, dragged, and resized coordinates for all glassmorphic widgets (Git, Terminal, Code, Todos, Reminders).
*   `connectionState`: Establishes fallback pathways to HTTP `/api/chat` if WebSocket signals degrade.

### SVG Gooey Filter Blob Render Loop Specification
To run a gorgeous particle system inside 15MB RAM and 2% CPU, we deploy a **2D Canvas Render Loop** inside React, styled with an SVG Gooey filter:

1.  **Canvas Setup**: Instantiates a single 2D Canvas centered in the browser viewport.
2.  **Particle Instantiation**: Initializes an array of exactly 200 simple coordinate points $(x, y)$ positioned on a radius $R = 120\text{px}$ from the canvas origin.
3.  **The Physics Formula**: Each particle updates its position on every frame using standard polar-to-Cartesian noise algorithms:
    $$\theta_i = \left(\frac{i}{200}\right) \cdot 2\pi$$
    $$R_i = R_{base} + \text{Noise}(\cos\theta_i \cdot s, \sin\theta_i \cdot s, \text{time} \cdot f) \cdot A$$
    Where:
    *   $s$: Spatial noise frequency multiplier.
    *   $f$: Temporal animation speed scale.
    *   $A$: Current wave amplitude. (Increases dynamically during voice-listening and speaking events).
4.  **SVG Filter Integration**: Canvas elements are wrapped with CSS filters:
    ```css
    canvas {
      filter: blur(10px) contrast(18);
    }
    ```
    This bridges adjacent overlapping particles together, rendering a melting, organic fluid shape.
5.  **Render Loop Lifecycles**: Locked at 60 FPS using `requestAnimationFrame`. If the tab loses active focus, the loop pauses automatically, reducing idle CPU usage to **0.0%**.

---

## 6. Granular 13-Phase Development Roadmap

We segment the 22-week schedule into highly-focused sprints. Under our strict guidelines, **no phase can overlap**, and **each phase must pass its explicit success criteria** before proceeding.

### Milestone A: Core Skeleton & Communications (Weeks 1 - 8)

*   **Phase 0: Skeleton Setup (Week 1)**
    *   *Goal*: Construct absolute folder architecture with all core configuration hooks ready.
    *   *Tasks*: Create workspace file trees, configure python standard virtual environment, establish FastAPI wrapper, set up Vite + React template. Write global command setup registers.
    *   *Verification*: Run `ultron start` in terminal. Verified that the browser opens immediately displaying our active skeleton viewport on Port 5173.
*   **Phase 1: Basic Chat Infrastructure (Week 2)**
    *   *Goal*: Establish persistent message transactions between backend databases and client viewports.
    *   *Tasks*: Deploy SQLite database with WAL enabled. Create `conversations` database schema. Code basic HTTP message echo routes.
    *   *Verification*: Send test message in chat. Database logs message string, server returns text echo, React updates UI state dynamically.
*   **Phase 2: LLM Brain Connection (Week 3)**
    *   *Goal*: Connect robust, cloud-based intelligence with automated multi-key rotation and caching.
    *   *Tasks*: Build `llm_router.py`. Configure key pool arrays (3 Groq, 2 Gemini). Script error handlers for key exhaustion (429 status codes). Write fast in-memory LRU key-value cache layer.
    *   *Verification*: Temporarily revoke Groq Key 1. Router catches error, switches to Key 2 inside 100ms, and successfully resolves the prompt.
*   **Phase 3: Cognitive Orchestrator & Memory Foundations (Weeks 4 - 5)**
    *   *Goal*: Process cognitive inputs, categorize intents, and deploy SQLite memory modules.
    *   *Tasks*: Implement orchestrator fast, medium, and heavy speed tracks. Set up intent parsing rules. Establish `persistent` and `project` database schemas.
    *   *Verification*: Asking "What is my name?" accesses Persistent DB instantly. Describing a complex task triggers the orchestrator's Heavy Path.
*   **Phase 4: Real-Time WebSocket Core (Weeks 6 - 7)**
    *   *Goal*: Shift communication architectures from HTTP REST to highly efficient WebSockets.
    *   *Tasks*: Deploy native FastAPI WebSockets. Create `ws_chat` and `ws_events`. Implement auto-reconnection algorithms.
    *   *Verification*: Tokens are streamed individually over the active WS channel. System diagnostic events are pushed from server without client polling.
*   **Phase 5: Unified Memory Engine (Week 8)**
    *   *Goal*: Integrate API embeddings, a local vector index, and semantic search capabilities.
    *   *Tasks*: Connect Gemini embedding API hooks. Deploy our lightweight NumPy vector database. Program our heuristic `Memory Gate`.
    *   *Verification*: Searching "How did we resolve that CORS issue last week?" returns correct vector matches in under 15ms.

---

### Milestone B: Smart Personalities & Tools (Weeks 9 - 14)

*   **Phase 6: Dual Personalities Engine (Weeks 9 - 10)**
    *   *Goal*: Deploy Ultron and Zora personality profiles, stress signal analyzers, and auto-switching.
    *   *Tasks*: Write detailed system prompts for Ultron and Zora. Code `signal_analyzer.py` implementing the sliding-window Overwhelm Score ($E_s$).
    *   *Verification*: Simulate 4 compile errors past midnight. System triggers Zora automatically, and her visual theme loads.
*   **Phase 7: Tool Execution Registry (Weeks 11 - 12)**
    *   *Goal*: Develop a declarative tool manager with safe OS adapters and permission models.
    *   *Tasks*: Code basic toolsets (Filesystem, Todo, Git, shell command execution). Design the permission controller (Levels 0-3).
    *   *Verification*: Requesting terminal commands (Level 2) triggers the confirmation gate modal.
*   **Phase 8: Continuous Voice System (Weeks 13 - 14)**
    *   *Goal*: Establish fluid, low-latency, real-time voice conversations.
    *   *Tasks*: Connect client-side Web Speech API. Set up Edge-TTS cloud audio streaming. Code the instant voice barge-in (interrupt) loop.
    *   *Verification*: Speaking "Stop" during active TTS generation instantly silences client audio, and the backend halts generation inside 100ms.

---

### Milestone C: Interface & Polish (Weeks 15 - 22)

*   **Phase 9: The Particle Blob UI (Weeks 15 - 16)**
    *   *Goal*: Implement the living visual soul of the platform.
    *   *Tasks*: Implement 2D Canvas with SVG Gooey filter logic. Map state variables (Idle, Thinking, Listening, Speaking) to particle physics forces.
    *   *Verification*: Blob frame rate maintains solid 60 FPS on both Windows 11 and Ubuntu.
*   **Phase 10: Glassmorphic Floating Widgets (Weeks 17 - 18)**
    *   *Goal*: Create sleek, lightweight, drag-anywhere system overlays with zero package overhead.
    *   *Tasks*: Write `useDraggable.js`. Design 8 glassmorphic widgets (Todos, Git, Terminal, Code snippet container, etc.).
    *   *Verification*: Multiple widgets can be dragged concurrently with zero page lag.
*   **Phase 11: Overnight Memory Synthesis (Weeks 19 - 20)**
    *   *Goal*: Clean, compress, and organize database records during idle hours.
    *   *Tasks*: Code background async task schedulers. Deploy Gemini semantic condensation algorithms to shrink database clusters.
    *   *Verification*: Large, repetitive message blocks from past sessions are consolidated into single key facts.
*   **Phase 12: System Diagnostics & Integration Polish (Weeks 21 - 22)**
    *   *Goal*: Ensure system-wide stability, performance, and complete integration.
    *   *Tasks*: Code the `ultron doctor` suite (evaluating ports, SQLite connections, RAM profiles, API keys). Implement the slide-out history panel.
    *   *Verification*: `ultron doctor` returns all green marks. System stays active for 72 continuous hours, and idle RAM consumption remains under 350MB.

---

## 7. LOCAL PERFORMANCE & HARDWARE VERIFICATION SUITE

To protect your 8GB machine from slow degradation over its 2-year journey, the `ultron doctor` CLI execution pipeline verifies system metrics against strict limits before starting:

```
                  LOCAL HARDWARE PROFILE CHECK (8GB RAM HOST)
+--------------------------------------+-----------------+------------------------+
| HARDWARE METRIC                      | MAXIMUM ALLOWED | COMPLIANCE VERIFICATION|
+--------------------------------------+-----------------+------------------------+
| Server Boot-Up Latency               | < 5.0 Seconds   | Process timing check   |
| System Idle RAM Consumption         | < 350 Megabytes | OS process memory check|
| Active Speech RAM Consumption        | < 850 Megabytes | Thread footprint check |
| System Idle CPU Utilization          | < 2.0 Percent   | CPU loop check         |
| Database Concurrency Operations      | 0 Lock Failures | WAL file-lock check    |
| API Round-Robin Key Swapping        | < 100 Millisec  | Router switch latency  |
+--------------------------------------+-----------------+------------------------+
```

---

## 8. JARVIS & FRIDAY ORGANIC BEHAVIOR (THE "TAKE THE LIBERTY" ARCHITECTURE)

To transcend standard chatbot interactions and elevate Ultron and Zora into the realm of **Jarvis** and **Friday**, we must replace clinical "as-an-AI" structures with an active, witty, and contextual intelligence layer.

### A. The "Take the Liberty" Proactive Pipeline
Jarvis never waits for an instruction if the path forward is obvious. Instead of just displaying error logs, Ultron anticipates the fix and initiates pre-processing in the background:
*   **The "Draft-and-Suggest" Pattern**: When a terminal command fails with a typical compilation error, the orchestrator doesn't just print the error. It spins up a background thread that matches the error, generates the fix (e.g., correcting an import paths, updating an outdated npm package), and populates a small floating Code snippet widget in the background. 
*   **Natural Verbal Introduction**: Instead of asking you to prompt him, Ultron's next speech-chunk triggers with:
    > *"Your webpack compilation failed on line 14, Debjeet. I've taken the liberty of drafting the correct module import in your side panel. Want me to apply it?"*

### B. Adaptive Speech Cadence, Disfluencies & Filler Mechanics
Real partners do not speak in perfectly indexed sentences. They hesitate, adjust their tone, use colloquialisms, and vary their sentence length depending on the mood.
*   **The Colloquializer Filter**: We implement an automated regex-based string post-processor that intercepts raw LLM outputs before they reach the Edge-TTS engine. This filter injects organic conversational disfluencies and contractions:
    *   *Raw Input*: `I have analyzed your Git repository and discovered uncommitted files.`
    *   *Jarvis-Polished*: `Right, I've just scanned your repo. Looks like we have a few uncommitted files sitting around.`
    *   *Zora-Polished*: `Let's see... we've got a couple of changes in the workspace that aren't committed yet. Want to save them?`
*   **Dynamic Pace Allocation**:
    *   **Calm/Idle**: Speech rate is locked at a natural, steady 150 words-per-minute (WPM) with smooth pauses.
    *   **High Stress / Fast Work**: If the user is typing fast and compiling rapidly, Ultron switches to a sharp, rapid-fire 185 WPM, keeping responses under 5-8 words. ("No conflicts. Clean build. Go.")
    *   **Emotional High Stress**: Zora scales down to a warm, deliberate 130 WPM, extending pauses between clauses to provide psychological breathing room.

### C. Context-Aware Banter, Dry Humor & Vulnerability
To feel real, both personalities must break free of sycophancy. If you write bad code, Ultron must gently mock it (dry, professional humor, just like Jarvis), and if you have a big win, Zora must share the excitement as a true partner.
*   **Ultron's "Senior Partner" Banter**:
    *   *If you write a 400-line monolithic function*: *"Well, that's certainly one way to write React, Debjeet. Though I believe the developers of 2004 called that a 'spaghetti wrap'. Shall we modularize before the compiler has a nervous breakdown?"*
*   **Zora's "Co-Pilot" Vulnerability**:
    *   *When opening the morning check-in after you had a rough night*: *"I was actually thinking about that database issue we struggled with last night while the system was cleaning its memory. I think we were looking at it all wrong. How's your head feeling today?"*

---

## 9. ADVANCED LOW-LATENCY WEBSOCKET SYNCHRONIZATION & PACING

To ensure that the continuous live dialogue between you and Ultron feels natural, the WebSocket layer must support continuous background tracking, interrupt handshakes, and conversational "pacing".

```
+-----------------------------------------------------------------------------------------+
|                              Continuous Telemetry Sync Loop                             |
+-----------------------------------------------------------------------------------------+
| Client UI (Focus, Retype, Audio DB) ----[ws_logs / ws_voice]----> FastAPI Orchestrator  |
|                                                                    |                    |
| Client UI (Local Audio Playback) <------[Instant Mute Signal]------+ (Cancel Stream)    |
+-----------------------------------------------------------------------------------------+
```

### A. Non-Intrusive "Stream of Consciousness" Telemetry
The client-side React app operates a quiet background sync loop. Every 5 seconds, if there is active development activity, it posts a tiny, non-blocking telemetry frame over `ws_logs` with **$<1\text{KB}$ bandwidth cost**:
```json
{
  "type": "heartbeat_telemetry",
  "active_element": "input_prompt",
  "characters_typed": 42,
  "characters_deleted": 12,
  "session_elapsed_sec": 7200,
  "last_command_status": "failed_exit_1"
}
```
This enables Zora and Ultron to "see" your work style in the background without needing heavy, dangerous keyloggers, preserving your computer's resources.

### B. Immediate Audio Fade-Out on Interrupt (Barge-In)
When you speak while Zora is talking, cutting the audio instantly can sound jarringly digital. Instead, we use the **HTML5 Web Audio API Gain Node** to handle the fade-out:
1.  When the client microphone registers decibels above `-40dB` (or Web Speech API fires `onstart`), the React client triggers a fast linear ramp:
    ```javascript
    // Fade out audio over exactly 80ms rather than a digital snap
    gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.08);
    ```
2.  Simultaneously, the client sends `{"type": "interrupt"}` to the backend.
3.  The backend catches the signal, issues an async cancellation to the active generator, flushes all pending audio packets on the server, and returns:
    ```json
    {"type": "interrupt_acknowledged", "last_spoken_sentence": "I was thinking that..."}
    ```
4.  This sentence is saved in Short-Term memory, allowing Zora to naturally say: *"Sorry, go ahead,"* or *"Right, you were saying?"*—completing the illusion of a living partner.

---

## 10. ARCHITECTURE REFINEMENTS & FROZEN PRINCIPLES (FINAL UPDATE)

These refinements do not replace the existing architecture. They strengthen it while keeping the original vision unchanged, establishing high-quality modular design standards.

### 10.1 Unified Context Builder Layer
Before executing any LLM router request, the Cognitive Orchestrator dynamically resolves dependencies and constructs a single, unified context block. This avoids context-window pollution and controls token waste.

```
       User Request
            │
            ▼
   Conversation History (Short-Term RAM)
            │
            ▼
    Relevant Memories (NumPy Vetors Similarity)
            │
            ▼
      Project Context (Active File Paths & Meta)
            │
            ▼
    Active Personality (Prompt Guidelines & Slang)
            │
            ▼
   Available Tools (Selected Declarative Schemas)
            │
            ▼
    System Instructions (Forbidden Phrases / Rules)
            │
            ▼
       LLM Router (Groq/Gemini Multi-Key Hub)
```

*   **Purpose**: 
    *   Maximizes LLM deductive reasoning.
    *   Minimizes input token usage.
    *   Ensures consistent personality tone matching.
    *   Enhances precise tool execution decisions.

### 10.2 Skill-Based Directory Architecture
Every automated capability exists as an independent, decoupled module contained within a structured directory tree under `backend/skills/`.

```
skills/
├── filesystem/
├── git/
├── browser/
├── terminal/
├── research/
├── memory/
├── calendar/
└── voice/
```

Each specific Skill directory contains an explicit contractual template:
*   `manifest.json`: Defines the skill name, version, requirements, description, input/output schemas (Pydantic models), and safety permissions level.
*   `handler.py`: Houses the execution code and method hooks.
*   `prompt.md`: System prompt adjustments, instructions, or examples relevant to the skill.
*   `config.py`: Local settings and platform-specific path adapters.

**Benefits**: Solves maintenance bottlenecks, enables dynamic loading/unloading to preserve RAM, and establishes a SaaS-ready foundation.

### 10.3 Event-Driven Internal Communication
To maximize performance, reduce thread blocking, and scale efficiently, core modules communicate using a centralized, asynchronous event-publishing queue (`event_bus.py`).

```
          User Request
               │
               ▼
          Orchestrator
               │
               ▼
         Publish Event (Event Bus)
               │
               ├───► Memory Engine (Log/Embed)
               ├───► Tool Registry (Verify state)
               ├───► Widgets Controller (UI push)
               ├───► Telemetry Logger (Log files)
               └───► Voice System (TTS Pre-cache)
```

**Benefits**: Loose coupling of execution modules, high debuggability, non-blocking performance, and complete compatibility with future multi-agent configurations.

### 10.4 Frozen Development Principles
The core architecture is now **frozen**. Future changes will focus entirely on optimizing execution, adding new features through skills, and polishing the visual design, not redesigning structural foundations.

*   **Rule 1: Build Iteratively**: Never rewrite or refactor fully functional components without a strict, confirmed engineering reason.
*   **Rule 2: Extend, Don't Rebuild**: Expand capabilities exclusively through independent Skills, plugins, or front-end widget additions.
*   **Rule 3: Absolute Independence**: Maintain strict separation of concerns between state modules; errors in one widget must never crash the orchestrator.
*   **Rule 4: Working Features First**: Focus on feature completion before performance tuning.
*   **Rule 5: Backward Compatibility**: Ensure any configuration or memory format modifications preserve existing schemas.

### 10.5 Long-Term Architecture Goals
Ultron is designed from day one as a long-term AI Operating System. The modular core must naturally scale to support:
*   A **Personal AI Assistant & Work Companion** (Zora/Ultron).
*   A **Software-Development Copilot** (Directing terminal compilers and repositories).
*   An **Autonomous Task Automation & Scraping Platform**.
*   A **Self-Hosted SaaS Builder & Deployer**.
*   A **Multi-Agent Collaborative System**.

No structural or core architectural redesigns should ever be required to scale Ultron from a local V1 assistant into these enterprise horizons.

---

### Let's Build V1!
This definitive, frozen blueprint is now fully optimized with your final refinements, Jarvis-like behavior patterns, and the event-driven skill architecture. 

**I am ready. Once you are prepared to kick off Phase 0, send "Next" and we will write the foundational skeleton.**
