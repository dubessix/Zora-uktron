# IRIS — Ultron V1 (Zora-Uktron)

> Your elite AI operating system, **Senior Systems Architect**, **CTO**, and permanent
> digital partner — a Jarvis-style personal coding assistant that remembers you,
> understands coding tasks, and helps you build a SaaS.

**IRIS** is a full-stack personal AI assistant with a FastAPI backend, a React/Vite
dashboard, long-term memory, emotion-aware personalities (Ultron + Zora), browser-native
voice, and a **Codex-style autonomous coding mode** powered by NVIDIA's coding models.

---

## ✨ Features

### 🧠 Dual Personalities
- **Ultron** — calm, dry-witted Jarvis-style engineer ("Sir"). Replies in short, warm
  English and acts as your SaaS co-founder.
- **Zora** — warm, caring emotional-support companion (Hinglish/English/Bengali/Hindi)
  that steps in when you're stressed, then hands back to Ultron.
- Personality auto-switches based on a stress score and manual commands.

### 🖥 Coding Agent Mode (Codex-style)
- **NVIDIA coding brain** — coding tasks use NVIDIA's best coding model (Nemotron 3 Ultra),
  normal conversation stays on Groq.
- **Auto-detect** coding intent ("make an auth API") **and** a manual toggle.
- **Permission-first**: Ultron asks "Shall I create `auth.py`?" before writing.
- **Backup safety**: every overwrite makes a `.bak` backup first.
- **Project-aware**: scans your project structure + stored project facts so code matches
  your stack.
- **Multi-file tasks**: works through files one at a time, capped at 8 steps (no runaway),
  reports per-file results.
- **Auto-verify**: syntax-checks written files (timeout-bounded, non-destructive).
- **Diff feedback**: tells you created/updated + line counts + backup path.
- **Error self-healing**: parses real Python/Node/backend errors, resolves the actual
  file + line, and suggests concrete fixes (pip vs npm, etc.).

### 🧠 Jarvis-style Long-Term Memory
- Short-term (last 50 turns) + **episodic / semantic** memory with vector recall.
- Token-smart: memory only triggers on meaningful turns; embeddings are cached.
- Project state memory (name, tech stack, goals) injected into coding turns.

### 🎙 Voice (browser-native)
- Wake-word listening (e.g. "Ultron", "Jarvis") with the Web Speech API.
- Understands mixed Hinglish / English / Hindi.
- No heavy local STT — light on 8GB / dual-core machines.

### 🔧 Tools (65+)
Weather, web search (real results, opens the answer page), research, git, GitHub,
filesystem & folders, code optimizer, semantic code graph, reminders, calendar, tasks,
security guardian, daily briefing, system metrics, world monitor, music/Spotify, browser
control, file format conversion, and more.

### ⚙️ Optimized for your hardware
- Lazy-loads heavy deps (numpy, edge-tts) so boot stays light.
- No local LLM — all intelligence is cloud (Groq/Gemini/NVIDIA), so **no GPU needed**.
- Background loops tuned; storage-bounded memory (auto-prune).
- Works on Windows 11 and Ubuntu 24.04.

---

## 🏗 Architecture

```
Zora-Uktron/
├── backend/                 # FastAPI app
│   └── app/
│       ├── brain/           # LLM router (Groq/Gemini/NVIDIA), key rotation, cache
│       ├── core/            # Orchestrator, intent, confidence, decision engines
│       ├── memory/          # short-term, episodic, semantic, project, vector store
│       ├── personalities/   # ultron.md, zora.md personality prompts
│       ├── skills/          # modular coding-agent instruction blocks
│       ├── emotion/         # stress scoring & Zora auto-handoff
│       ├── tools/           # 65+ tools
│       ├── voice/           # edge-tts voice provider
│       ├── security/        # confirmation gate, permission manager
│       ├── session/         # session management
│       ├── websocket/       # real-time chat/events/logs/dashboard channels
│       ├── router.py        # REST API
│       └── main.py          # FastAPI entrypoint
├── frontend/                # React 19 + Vite 5 + Tailwind dashboard
│   └── src/components/      # app shell + 17 widgets
├── tests/                   # 79 pytest tests
├── config.yaml              # configuration
├── launcher.py              # one-command launcher (backend + frontend)
├── requirements.txt         # Python deps
└── docs/                    # detailed docs
```

### API Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | System health + metrics |
| POST | `/api/chat` | Send a message, get AI reply + coding flag |
| POST | `/api/coding-mode` | Toggle NVIDIA coding mode |
| POST | `/api/tools/execute` | Execute a registered tool |
| GET | `/api/history` | Conversation history for a session |
| WS | `/ws/chat` | Streaming chat (tokens, progress) |
| WS | `/ws/events` | Server-pushed events (reminders, alerts) |
| WS | `/ws/logs` | Log streaming |
| WS | `/ws/dashboard` | Live system metrics |

---

## 🚀 Quick Start (First Run)

> Requires Python 3.10+ and Node.js 18+.

### 1. Clone
```bash
git clone https://github.com/dubessix/Zora-uktron.git
cd Zora-uktron
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Configure API keys
Copy/Edit `.env` (already present, with placeholders). Add your real keys:

```env
# Primary AI provider
GROQ_API_KEY_1=your_groq_api_key_1_here

# Fallback provider
GEMINI_API_KEY_1=your_gemini_api_key_1_here

# NVIDIA Build (NIM) — coding brain
NVIDIA_API_KEY_1=your_nvidia_api_key_1_here

# Optional
ENV_STATE=production
SECRET_KEY=a_long_random_string_here
GITHUB_TOKEN=your_github_token_here      # GitHub integration
TAVILY_API_KEY=your_tavily_api_key_here  # research
```

> You can use more than one key per provider (add `_2`, `_3`) for automatic rotation.
> The app runs fine with placeholder keys (mock mode) — it just won't call real AI.

### 5. Run everything (backend + frontend together)
```bash
python launcher.py
```
Launcher checks ports, starts the FastAPI backend on `8000` and Vite frontend on
`5173`, then opens your browser.

> Or run separately: `python -m uvicorn backend.app.main:app --port 8000`
> and `cd frontend && npm run dev`.

### 6. Where to get free keys
| Provider | Purpose | Get key |
|----------|---------|---------|
| **Groq** | fast chat brain | https://console.groq.com |
| **Gemini** | embeddings + fallback | https://aistudio.google.com |
| **NVIDIA Build (NIM)** | coding brain | https://build.nvidia.com |

All offer free tiers — no GPU needed on your machine.

---

## 🧪 Running Tests
```bash
pytest tests/ -q        # 79 tests
```

---

## 💬 Usage Examples
- **Chat:** `hello` / `what's the weather in Kolkata?`
- **Coding (auto-detect):** `make an auth API`, `review the CSS`, `refactor this function`
- **Coding (manual):** click the **💻 Coding** toggle in the UI to force NVIDIA mode.
- **Memory:** `what did we decide about the auth stack?`
- **Voice:** click the mic and say *"Ultron, check the weather"* (Chrome/Edge).
- **Reminders/planning:** `set a reminder for 10 minutes`, `show my tasks`.

---

## 📁 Documentation
See the [`docs/`](docs/) folder for architecture, API reference, memory architecture,
WebSocket contract, and the development blueprint.

---

## 🛡 Security Notes
- `.env`, `data/` (database), `node_modules/`, `dist/` are gitignored — never commit keys.
- Destructive file actions require confirmation and make `.bak` backups.
- `terminal_run` requires manual confirmation (Level 2 security).

---

## 📄 License
Personal / internal project. See repo for details.

---

Built with ❤️ by **Debjeet** — IRIS V1, your permanent coding partner.
