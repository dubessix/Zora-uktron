<div align="center">

# 🦾 ULTRON — Personal AI Operating System & Coding Partner

**A Jarvis-style personal assistant, developer partner, and emotional companion.**

Built on **FastAPI + React**, Ultron combines a cognitive orchestrator, multi-provider
LLM routing (Groq · Gemini · NVIDIA), long-term memory, real-time WebSockets, voice,
and a Codex-style autonomous **coding-agent mode**.

</div>

---

## ✨ Features

### 🧠 Cognitive Core
- **Cognitive Orchestrator** — intent analysis → confidence check → speed-track decision → memory sync → tool execution.
- **Multi-provider LLM routing** — Groq (fast chat) · Gemini (fallback) · **NVIDIA Build (coding)** with key rotation, rate-limit cooling, and automatic failover.
- **Smart caching** with configurable cache policy + disk persistence.

### 💾 Jarvis-style Memory
- Short-term, episodic, semantic, emotional, persistent (SQLite) and project memory layers.
- Vector store (NumPy cosine similarity) with duplicate detection + bounded retention (stays tiny over years).
- Long-term recall injected into the system prompt — Ultron "remembers" past sessions.

### 💻 Coding-Agent Mode (Codex-style)
- **NVIDIA coding brain** — used *only* on coding turns; normal chat stays fast on Groq.
- **Auto-detect** coding intent **+ manual toggle** (`/api/coding-mode`).
- **Permission-first** file writes with automatic **`.bak` backup** on overwrite.
- **Project-aware** context injection (structure + stored facts).
- **Multi-file** task loop with an 8-step limit (never runs away).
- **Safe, timeout-bounded** syntax verification after writes.
- **Diff-style feedback** — created/updated, line counts, backup path.
- **Error self-healing** for Python + Node/JS + backend — real file/line resolution and concrete fix hints (pip vs npm).

### 🌐 Real-Time + Voice
- WebSockets: `/ws/chat`, `/ws/events`, `/ws/logs`, `/ws/dashboard`.
- Browser-native wake-word voice (Hinglish / English / Hindi) with mic toggle.
- Reminder scheduler, USGS emergency monitor, and proactive intelligence loops.

### 🛠 65+ Tools
Filesystem, git/GitHub, browser, weather, research/web search, tasks, reminders,
calendar, code optimizer, semantic code graph, security guardian, system metrics,
music/Spotify, world monitor, and more.

### 🎨 Frontend (React + Vite + Tailwind)
Glassmorphic 3-panel dashboard with draggable widgets, dynamic **Ultron (emerald) /
Zora (pink)** identity, and a conversation-following coding panel.

---

## 🧱 Architecture

```
Zora-uktron/
├── backend/app/
│   ├── main.py                 # FastAPI app + WebSocket endpoints + background loops
│   ├── router.py               # REST routes: /api/chat, /api/history, /api/tools/execute, /api/coding-mode
│   ├── cli.py                  # 'ultron' click CLI (setup, doctor, version)
│   ├── core/                   # orchestrator, intent_analyzer, confidence, decision
│   ├── brain/                  # llm_router, api_key_manager, smart_cache, cache_policy
│   ├── memory/                 # short_term, episodic, semantic, emotional, persistent, project, vector_store, gate
│   ├── skills/                 # modular coding-agent instruction blocks (clean, maintainable)
│   ├── personalities/          # ultron.md, zora.md + engine
│   ├── tools/                  # 65+ tools + tool_registry + security gates
│   ├── voice/                  # edge-tts provider + interrupt handler
│   ├── websocket/              # connection manager
│   └── emotion/  security/  session/  database/
├── frontend/                   # React + Vite + Tailwind dashboard
├── docs/                       # architecture, API reference, memory, testing, etc.
├── launcher.py                 # boots backend + frontend together
├── config.yaml                 # all system configuration
└── requirements.txt
```

> Full maps: [`docs/project_structure.md`](docs/project_structure.md) · [`docs/architecture.md`](docs/architecture.md)

---

## 🚀 Quick Start (First Run)

> Requirement: **Python 3.10+**, **Node 18+**, **npm**, and an internet connection.

```bash
# 1. Clone & enter
git clone https://github.com/dubessix/Zora-uktron.git
cd Zora-uktron

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure .env (copy from the template)
#    Edit .env and add your real API keys (see below). Placeholder keys work —
#    Ultron will run in mock mode instead of crashing.

# 5. Launch everything (backend :8000 + frontend :5173 + browser)
python launcher.py
```

The launcher checks ports, starts both services, and opens
`http://127.0.0.1:5173` in your default browser.

---

## 🔑 Environment Variables (`.env`)

Create a `.env` file in the project root:

```env
# --- AI Providers ---
GROQ_API_KEY_1=your_groq_key            # primary chat provider
GEMINI_API_KEY_1=your_gemini_key        # fallback provider (also used for memory embeddings)
NVIDIA_API_KEY_1=your_nvidia_key        # coding-agent provider (build.nvidia.com, free nvapi- key)

# --- Security / Environment ---
ENV_STATE=production
SECRET_KEY=your_random_long_string

# --- Optional Tools (mock until set) ---
GITHUB_TOKEN=your_github_pat
TAVILY_API_KEY=your_tavily_key

# --- Frontend (optional; default http://127.0.0.1:8000) ---
VITE_API_URL=http://127.0.0.1:8000
```

- **Groq:** https://console.groq.com (free tier, generous)
- **Gemini:** https://aistudio.google.com (free embedding + flash)
- **NVIDIA (coding):** https://build.nvidia.com — free `nvapi-` key, no credit card.
  Ultron uses `nvidia/nemotron-3-ultra-550b-a55b:free` **only on coding turns**.
- Without real keys, the system still boots and runs using **mock responses** — it never crashes.

---

## 🎭 Personas

Ultron's personality engine auto-switches between two personas:

| Persona | Role | Accent | Provider |
|---------|------|--------|----------|
| **Ultron** | Engineering / coding / SaaS co-founder | English, Jarvis-style, 25–40 words | Groq + **NVIDIA** (coding) |
| **Zora** | Emotional support / cognitive companion | Hinglish / English / Bengali / Hindi | Groq |

Switch manually with "switch to zora" / "back to work", or Ultron auto-handoffs
to Zora on high stress. Coding tasks automatically use the NVIDIA brain.

---

## 🖥 Using Coding-Agent Mode

Ask Ultron naturally, for example:

> "Ultron, build an auth API with JWT login."
> "Can you review the CSS?"
> "Run the backend and fix any error."

Ultron will:
1. Detect it as a **coding turn** and use the **NVIDIA** coding brain.
2. **Plan in steps** and ask permission before writing ("Shall I create auth.py?").
3. **Back up** any existing file (`.bak`) before overwriting.
4. **Verify** syntax after writing (timeout-bounded, safe).
5. Report a **diff summary** (created/updated, lines, backup path).
6. Offer the next step ("Next, shall I build the /login route?").

You can also force coding mode from the UI (the 💻 button) or the API:
```bash
curl -X POST http://127.0.0.1:8000/api/coding-mode -H "Content-Type: application/json" -d '{"enabled":true}'
```

---

## 🧪 Testing

```bash
pip install pytest pyflakes
python -m pytest tests/ -q        # 79 tests, all green
```

---

## 📡 API Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/chat` | Send a message (returns `coding` flag for coding turns) |
| GET  | `/api/health` | Health + system metrics |
| GET  | `/api/history?session_id=` | Conversation history |
| POST | `/api/tools/execute` | Execute a registered tool |
| POST | `/api/coding-mode` | Toggle NVIDIA coding mode |
| WS   | `/ws/chat` | Streamed chat (tokens, widgets, done) |
| WS   | `/ws/events` | Server-pushed events (reminders, alerts) |
| WS   | `/ws/logs` | Log streaming |
| WS   | `/ws/dashboard` | Live CPU/RAM metrics |

> Full contract: [`docs/websocket_contract.md`](docs/websocket_contract.md) · [`docs/api_reference.md`](docs/api_reference.md)

---

## 🧭 Documentation

| Doc | Purpose |
|-----|---------|
| [`docs/architecture.md`](docs/architecture.md) | System architecture |
| [`docs/memory_architecture.md`](docs/memory_architecture.md) | Memory layers |
| [`docs/api_reference.md`](docs/api_reference.md) | REST/WS API reference |
| [`docs/websocket_contract.md`](docs/websocket_contract.md) | WebSocket contract |
| [`docs/testing_strategy.md`](docs/testing_strategy.md) | Testing strategy |
| [`docs/frontend_structure.md`](docs/frontend_structure.md) | Frontend layout |
| [`docs/ultron_daily_operating_manual.md`](docs/ultron_daily_operating_manual.md) | Operating manual |
| [`ultron_cross_platform_launch_guide.md`](ultron_cross_platform_launch_guide.md) | Windows/Linux launch guide |

---

## 🧰 Requirements

See [`requirements.txt`](requirements.txt). Core stack:
`fastapi · uvicorn · websockets · python-dotenv · PyYAML · pydantic · numpy · httpx · click · psutil · edge-tts`

> Runs comfortably on **8GB RAM / dual-core / 0-GPU** hosts — no local LLM, no GPU needed.

---

## 🔒 Security Notes

- `.env`, `data/`, `node_modules/`, `dist/`, and `.cache/` are gitignored — never commit keys.
- File overwrites in coding mode are always backed up (`.bak`).
- Destructive operations require confirmation (permission levels).
- All SQL is parameterized.

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch (`git checkout -b feat/xyz`).
3. Commit your changes.
4. Open a Pull Request.

---

## 📄 License

This project is provided for personal/educational use. See the repo owner for
commercial licensing.

---

<div align="center">
  <sub>Built with FastAPI, React, and a lot of coffee · **Ultron & Zora**</sub>
</div>
