# Ultron V1 Directory & Project Structure Map
*Document Version: 1.0.7 — Synchronized Sprints 0-11 Structural Map*

This document provides a complete, raw directory tree map representing the active state of the Ultron V1 workspace. It defines file statuses (NEW, UPDATED, UNCHANGED, DEPRECATED) and details folder responsibilities for developers to understand the tree immediately.

---

## 1. Project Directory Tree

```
ultron/
├── config.yaml                        # [UNCHANGED] Holds persistent settings, thresholds, and triggers
├── .env                               # [UNCHANGED] Secure API key template
├── .gitignore                         # [UNCHANGED] Platform-independent Git exclusion profile
├── launcher.py                        # [UNCHANGED] Cross-platform FastAPI & Vite runner
├── requirements.txt                   # [UNCHANGED] Unified Python dependencies profile
├── setup.py                           # [UNCHANGED] Global 'ultron' console command registration
├── backend/
│   └── app/
│       ├── main.py                    # [UNCHANGED] Registered native WebSocket endpoints
│       ├── router.py                  # [UNCHANGED] HTTP Chat, History, and unified Tools execution routes
│       ├── cli.py                     # [UNCHANGED] click administrative CLI commands
│       ├── core/                      # [UNCHANGED] Cognitive Orchestrator Module
│       │   ├── orchestrator.py        # [UNCHANGED] Coordinates the 7-step completion pipeline
│       │   ├── intent_analyzer.py     # [UNCHANGED] Text prompt intent categorization
│       │   ├── confidence_engine.py   # [UNCHANGED] Vague/digit prompt verification
│       │   └── decision_engine.py     # [UNCHANGED] Fast / Medium / Heavy speed path selector
│       ├── brain/                     # [UNCHANGED] LLM Router and Caching Module
│       │   ├── api_key_manager.py     # [UNCHANGED] Key pools, rotation, and cooldowns
│       │   ├── smart_cache.py         # [UNCHANGED] In-memory persistent LRU cache
│       │   ├── cache_policy.py        # [UNCHANGED] Decoupled abstract BaseCachePolicy
│       │   └── llm_router.py          # [UNCHANGED] Primary async LLM client dispatcher
│       ├── memory/                    # [UNCHANGED] Multi-tiered Memory Module
│       │   ├── short_term.py          # [UNCHANGED] Sliding windowRAM conversation deque (last 50)
│       │   ├── persistent_memory.py   # [UNCHANGED] SQLite Key-Value user profile store
│       │   ├── project_memory.py      # [UNCHANGED] SQLite project configurations store
│       │   ├── vector_store.py        # [UNCHANGED] NumPy Cosine Similarity database
│       │   ├── memory_gate.py         # [UNCHANGED] Low-density greeting bypass filter
│       │   ├── episodic_memory.py     # [UNCHANGED] Time-based past events vector handler
│       │   ├── semantic_memory.py     # [UNCHANGED] Developer concepts vector handler
│       │   └── emotional_memory.py    # [UNCHANGED] Stress/sentiment vector handler
│       ├── personalities/             # [UNCHANGED] Conversational Identity Module
│       │   ├── base_personality.py    # [UNCHANGED] Abstract BasePersonality class
│       │   ├── personality_engine.py  # [UNCHANGED] State state models and auto-returns
│       │   ├── ultron.md              # [UNCHANGED] Ultron markdown prompt template
│       │   └── zora.md                # [UNCHANGED] Zora markdown prompt template
│       ├── emotion/                   # [UNCHANGED] Stress Analysis Module
│       │   ├── signal_analyzer.py     # [UNCHANGED] Extensible OCP Stress Score calculations
│       │   └── zora_trigger.py        # [UNCHANGED] Threshold monitor for auto-switchovers
│       ├── tools/                     # [UPDATED] Autonoumous local tools execution module
│       │   ├── tool_base.py           # [UNCHANGED] BaseTool ABC abstract interface and ToolResult
│       │   ├── tool_registry.py       # [UPDATED] Tool registry with un-mocked V2 tool registries
│       │   ├── folder_tools.py        # [UPDATED] Folder management and un-mocked folder organizer tools
│       │   ├── browser_tools.py       # [UPDATED] Browser tab closer, refresh, back, forward, and scraping tools
│       │   ├── web_search_tools.py    # [UNCHANGED] Deep Google, GitHub, and StackOverflow search tools
│       │   ├── music_tools.py         # [UPDATED] Music play/pause/resume/next/prev and volume tools
│       │   ├── spotify_tools.py       # [UPDATED] Spotify play/pause/resume/next/prev and volume tools
│       │   ├── context_builder.py     # [UNCHANGED] Filters relevant tools dynamically to save tokens
│       │   ├── filesystem_tools.py    # [UNCHANGED] FileRead and FileWrite tools with metadata
│       │   └── system_tools.py        # [UPDATED] Self-Healing Terminal, Calc, Chrome, and VS Code tools
│       │   └── README.md              # [UPDATED] Developer manual of tool execution
│       ├── security/                  # [UNCHANGED] Security managers and gates module
│       │   ├── permission_manager.py  # [UNCHANGED] Maps security levels (0-3) and requirements
│       │   └── confirmation_gate.py   # [UNCHANGED] Intercepts level 2/3 requests to halt execution
│       ├── websocket/                 # [UNCHANGED] Real-Time Streaming Subsystem Module
│       │   ├── connection_manager.py  # [UNCHANGED] Multi-channel thread-safe connection pool manager
│       │   └── README.md              # [UNCHANGED] Developer manual of websocket module
│       ├── voice/                     # [UNCHANGED] Duplex Voice Subsystem Module
│       │   ├── base_voice_provider.py # [UNCHANGED] Abstract BaseVoiceProvider ABC (Strategy OCP)
│       │   ├── edge_tts_provider.py   # [UNCHANGED] Concrete MS Edge cloud neural synthesizer
│       │   ├── interrupt_handler.py   # [UNCHANGED] Instant barge-in task canceller
│       │   ├── voice_system.py        # [UNCHANGED] Central voice engine, configurations and Event Bus
│       │   └── README.md              # [UNCHANGED] Developer manual of voice modules
│       └── database/                  # [UNCHANGED] Core Persistence Connection Module
│           ├── db.py                  # [UNCHANGED] WAL-enabled SQLite thread connections
│           └── models.py              # [UNCHANGED] Parameterized tables initialization
├── frontend/                          # [UPDATED] React + CSS + Vite Client
│   ├── package.json                   # [UNCHANGED] Frontend npm packages profile
│   ├── vite.config.js                 # [UNCHANGED] Vite compiler parameters
│   ├── postcss.config.js              # [UNCHANGED] PostCSS Tailwind binder
│   ├── tailwind.config.js             # [UNCHANGED] Custom color scheme and animations
│   ├── index.html                     # [UNCHANGED] Root entry HTML viewport
│   └── src/
│       ├── main.jsx                   # [UNCHANGED] React entry mounting hook
│       ├── index.css                  # [UNCHANGED] Base styling and goo filter layers
│       ├── App.jsx                    # [UNCHANGED] Complete chat UI with live telemetry
│       ├── hooks/                     # [UNCHANGED] Custom react hooks directory
│       │   └── useDraggable.js        # [UNCHANGED] Hardware accelerated pointer coordinate tracker
│       └── components/                # [UPDATED] Glassmorphism Dashboard Layout Components
│           ├── AppShell.jsx           # [UNCHANGED] Decoupled dynamic widget registry map
│           ├── LeftPanel.jsx          # [UNCHANGED] Monitors network latency, CPU, and RAM
│           ├── RightPanel.jsx         # [UNCHANGED] Monospace message bubbles and query text box
│           ├── BlobCanvas.jsx         # [UNCHANGED] Asynchronous Canvas 2D Particle Core
│           └── widgets/               # [UPDATED] Glassmorphic floating components
│               ├── WidgetContainer.jsx # [UNCHANGED] Draggable container and double-click collapse triggers
│               ├── TodoWidget.jsx      # [UNCHANGED] Daily life priority task tracker
│               ├── CalendarWidget.jsx  # [UNCHANGED] Scheduling day planner list
│               ├── GitWidget.jsx       # [UNCHANGED] Fully connected git branch watcher (no mock)
│               ├── FileExplorerWidget.jsx # [UNCHANGED] Fully connected filesystem browser (no mock)
│               ├── UniversalSearchWidget.jsx # [UNCHANGED] Fully connected search indexer (no mock)
│               ├── DeepResearchWidget.jsx # [UNCHANGED] Fully connected Tavily search widget (no mock)
│               ├── WeatherWidget.jsx   # [UNCHANGED] Fully connected keyless Open-Meteo weather (no mock)
│               ├── MarketWidget.jsx    # [UNCHANGED] Fully connected live stock watch (no mock)
│               ├── TerminalWidget.jsx  # [UNCHANGED] Fully connected terminal logs view (no mock)
│               ├── MemoryWidget.jsx    # [UNCHANGED] Fully connected memory browser (no mock)
│               ├── NotificationWidget.jsx # [UNCHANGED] Fully connected background tasks view (no mock)
│               ├── SystemWidget.jsx    # [UNCHANGED] Fully connected psutil metrics view (no mock)
│               └── README.md           # [UNCHANGED] Developer manual of widget additions
├── tests/                             # [UPDATED] Phase-by-Phase Diagnostic Test Suite
│   ├── test_phase1.py                 # [UNCHANGED] Validates database transactions, history, and mock completion asserts
│   ├── test_phase2.py                 # [UNCHANGED] Validates LRU-TTL cache and key rotation
│   ├── test_phase3.py                 # [UNCHANGED] Validates persistent SQLite config memory
│   ├── test_phase4.py                 # [UNCHANGED] Validates orchestrator pipeline and speeds
│   ├── test_phase5.py                 # [UNCHANGED] Validates NumPy Cosine Similarity and Gate
│   ├── test_phase6.py                 # [UNCHANGED] Validates extensible stress scores and auto-return
│   ├── test_phase7.py                 # [UNCHANGED] Validates tools, registries and timeouts
│   ├── test_phase8.py                 # [UNCHANGED] Validates WebSocket connections, streaming, and broadcasts
│   ├── test_phase9.py                 # [UNCHANGED] Validates voice strategies, lifecycles, and barge-in cancels
│   ├── test_phase10.py                # [UNCHANGED] Validates 3-panel grids, offscreen Canvas, and Vision Feed removal
│   ├── test_phase11.py                # [UNCHANGED] Validates useDraggable client coordinates and container styles
│   ├── test_phase12.py                # [UNCHANGED] Validates notifications, structured actions, and OCP search order resolution
│   └── test_phase13.py                # [UPDATED] Validates folder creations, browser operations, Spotify launchers, and Self-Healing compiler loops
└── docs/                              # [UPDATED] Documentation Core Folder
    ├── adr_001_intelligent_cache_policy.md # [UNCHANGED] ADR concerning cache decisions
    └── *                                    # [UPDATED] Synchronized Markdown Reference Manuals
```
