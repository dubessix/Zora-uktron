# ULTRON (Zora-Uktron) — Complete Setup Guide

A step-by-step guide to get Ultron running on your machine (Windows 11 or Ubuntu 24.04),
optimized for 8GB RAM / dual-core / no GPU.

---

## ✅ Requirements
- **Python 3.10+** (tested on 3.13)
- **Node.js 18+** and **npm**
- **git**
- Internet connection (for AI APIs and search)

> No GPU needed. All AI runs in the cloud.

---

## Step 1 — Clone the repository
```bash
git clone https://github.com/dubessix/Zora-uktron.git
cd Zora-uktron
```

---

## Step 2 — Install Python dependencies
```bash
pip install -r requirements.txt
```
This installs: fastapi, uvicorn, websockets, python-dotenv, PyYAML, pydantic,
pydantic-settings, numpy, httpx, click, psutil, edge-tts.

*(Optional) create a virtual environment:*
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux:   source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step 3 — Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Step 4 — Configure `.env`
An `.env` file already exists with placeholders. Edit it and add real keys.

```env
# --- Primary AI (Groq) — fast chat brain ---
GROQ_API_KEY_1=your_groq_api_key_1_here

# --- Fallback (Gemini) — embeddings + backup ---
GEMINI_API_KEY_1=your_gemini_api_key_1_here

# --- NVIDIA Build (NIM) — coding brain ---
NVIDIA_API_KEY_1=your_nvidia_api_key_1_here

# --- Environment ---
ENV_STATE=production
SECRET_KEY=a_long_random_string_here

# --- Optional tools ---
GITHUB_TOKEN=your_github_token_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Where to get each key (all free)
| Provider | Purpose | URL |
|----------|---------|-----|
| **Groq** | fast chat | https://console.groq.com → API Keys |
| **Gemini** | embeddings + fallback | https://aistudio.google.com → Get API key |
| **NVIDIA** | coding brain | https://build.nvidia.com → API Keys (free `nvapi-` key) |
| **GitHub** (optional) | GitHub integration | https://github.com/settings/tokens → Generate PAT |
| **Tavily** (optional) | research | https://tavily.com |

> **Pro tip:** You can add `_2`, `_3` keys per provider (e.g. `GROQ_API_KEY_2`) for
> automatic rotation and higher rate limits. With 2 NVIDIA accounts you get ~2× coding
> rate limit.

> The app **runs with placeholders** (mock mode) so you can test the UI immediately —
> it just won't call a real AI until you add keys.

---

## Step 5 — Run Ultron
```bash
python launcher.py
```
This:
1. Checks ports 8000 (backend) and 5173 (frontend) are free.
2. Installs frontend deps if missing.
3. Starts the FastAPI backend and Vite frontend together.
4. Opens your browser to `http://localhost:5173`.

### Run separately (optional)
```bash
# Terminal 1 — backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

---

## Step 6 — Use it
- **Type in the chat box** and press ➤.
- **Coding:** say `make an auth API` (auto-coding) or click the **💻 Coding** toggle.
- **Voice:** click the mic (Chrome/Edge only) and say a wake word, then a command.
- **Widgets:** click widget names in the top-right of the center panel to open them.

---

## 🧪 Verify it works
```bash
# Backend health
curl http://127.0.0.1:8000/api/health

# Chat
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"content":"hello"}'

# Tests
pytest tests/ -q
```

Expected: health returns `{"status":"healthy"}`, chat returns an AI reply, tests = **79 passed**.

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| Port 8000/5173 in use | Close the other app, or run `python launcher.py` again after killing it |
| Chat returns `[Mock ... Response]` | You haven't added a real API key to `.env` |
| Voice mic doesn't work | Use Chrome/Edge; allow microphone permission |
| Frontend blank | `cd frontend && npm install && npm run dev` |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |

---

## 🔒 Security checklist
- Never commit `.env` (it's gitignored).
- Never share API keys.
- The `terminal_run` tool requires confirmation for safety.
- File overwrites always create a `.bak` backup.
