# Ultron / Zora Personal Assistant V1

Ultron is a local-first personal assistant for one owner. It combines chat, project-scoped memory, coding/file tools, terminal controls, reminders, tasks, calendar, weather/research integrations, voice output, widgets, backups, and a localhost-only desktop web interface.

## Release status

This repository is a **Personal V1 release candidate**, not a claim of zero defects. Automated Linux verification passes, while final acceptance on the owner's Windows/browser/microphone/Spotify hardware and live AI provider accounts is still required.

## Requirements

- Python 3.10+
- Node.js 20.19+ or 22.12+
- npm and Git
- ffmpeg is optional for media workflows
- 8 GB RAM is recommended for the intended laptop profile; cloud AI is used instead of local LLMs

## Install from source

```bash
git clone https://github.com/dubessix/Zora-uktron.git
cd Zora-uktron
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m backend.app.cli setup
python -m backend.app.cli doctor
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app.cli setup
python -m backend.app.cli doctor
```

The wheel also exposes the `ultron` console command:

```bash
ultron setup
ultron doctor
ultron start --check
ultron start
```

`setup` preserves an existing `.env` and user `config.yaml`. Installed wheels use a writable per-user `ULTRON_HOME`; source checkouts use the repository root unless `ULTRON_HOME` is set.

## Configuration

Effective model IDs are in `config.yaml` and may be overridden with environment variables:

| Purpose | Default | Override |
|---|---|---|
| Groq chat | `llama-3.1-8b-instant` | `GROQ_CHAT_MODEL` |
| Gemini chat | `gemini-3.5-flash` | `GEMINI_CHAT_MODEL` |
| NVIDIA coding | `nvidia/nemotron-3-ultra-550b-a55b` | `NVIDIA_CHAT_MODEL` |
| Gemini embedding | `gemini-embedding-001` | `GEMINI_EMBEDDING_MODEL` |
| Embedding dimensions | `768` | `GEMINI_EMBEDDING_DIMS` |

Provider secrets belong only in the git-ignored `.env` or process environment. Tokens are never stored in repository files, Git remotes, or progress-tracker JSON.

## Daily operation

```bash
ultron start
```

The launcher:

1. takes a single-instance lock;
2. validates loopback ports and configuration;
3. runs `npm ci` only when the lockfile changes;
4. rebuilds production frontend assets only when source/API configuration changes;
5. starts FastAPI and the production static frontend on `127.0.0.1`;
6. opens the browser only after both schema-validated health checks pass;
7. monitors both child processes and stops the sibling if either exits;
8. performs bounded graceful shutdown with forced cleanup as a last resort.

On the first successful UI connection of each local calendar day, Ultron creates one time-appropriate Jarvis briefing (morning, afternoon, evening, or late-hour). It does not run a fixed 8 AM polling loop. Hidden browser tabs reduce health polling from five to thirty seconds and refresh immediately when visible again.

Default URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend health: `http://127.0.0.1:8000/api/health`

## Core behavior

- No configured AI key: returns an explicit `[Offline]` message; it does not fabricate an LLM answer.
- Optional hardware sensor missing: returns `Unavailable`; it does not invent temperature, battery, latency, or uptime.
- Destructive/system tools: require a one-time token bound to the exact action, session, and canonical arguments.
- Filesystem tools: are restricted to `security.allowed_directories` and reject sensitive/system paths and symlink escapes.
- Database restore: accepts approved backup paths only, enters maintenance mode, creates a verified safety copy, and rolls back automatically if post-restore integrity fails.
- Automatic backups: run daily by default with bounded generation retention.

## Main APIs

REST:

- `POST /api/chat`
- `POST /api/tools/execute`
- `POST /api/actions/confirm`
- `GET /api/history`
- `POST /api/speak`
- `GET /api/memory/recent`
- `POST /api/db/backup`
- `GET /api/db/integrity`
- `POST /api/db/restore`
- `GET /api/providers/status`
- `POST /api/personality`
- `POST /api/coding-mode`
- `GET /api/health`

WebSocket:

- `/ws/chat`
- `/ws/events`
- `/ws/logs`
- `/ws/dashboard`

Voice recognition is browser-side Web Speech API; synthesized output uses `POST /api/speak`.

## Verification

```bash
python -m pytest -q
python -m unittest discover -s tests -p 'test*.py'
python -m coverage run -m pytest -q
python -m coverage report -m
python -m pip_audit -r requirements-dev.txt --progress-spinner off
ruff check backend tests launcher.py setup.py
bandit -q -r backend
cd frontend && npm audit --audit-level=low && npm run build
```

Tests redirect SQLite, cache, backups, and generated artifacts to isolated temporary storage. The test session hashes production `data/` before and after execution.

## Current limitations

The following require real owner hardware/credentials and must not be inferred from sandbox tests:

- Groq, Gemini, NVIDIA, Tavily, and GitHub authenticated calls
- Windows process-group/taskkill behavior
- desktop browser dispatch
- microphone/Web Speech API
- Edge-TTS audio playback
- Spotify desktop controls

See `SETUP_GUIDE.md`, `docs/api_reference.md`, `docs/testing_strategy.md`, and `docs/development_progress.md` for the current operational reference.
