# Ultron on Arch Linux — Complete Beginner's Guide

A step-by-step, copy-paste guide to get **Ultron** (and Zora) running on **Arch Linux**.
Written for a complete fresher — no prior knowledge assumed.

> Time: ~15–20 minutes · Free (no paid API needed to run; real AI needs free keys)

---

## 📦 What you need
- An Arch Linux machine (or a friend's Arch system)
- Internet connection
- A GitHub account (optional, for cloning) — you can also download the ZIP

---

## Step 0 — Update your system (recommended)

```bash
sudo pacman -Syu
```

---

## Step 1 — Install the base tools

Run this in a terminal:

```bash
sudo pacman -S --needed git python python-pip nodejs npm ffmpeg xdg-utils
```

- `git` — to clone the project
- `python` / `python-pip` — to run the backend
- `nodejs` / `npm` — to build the frontend
- `ffmpeg` — for voice (optional but recommended)
- `xdg-utils` — so the launcher can open your browser

Press **Enter** when asked, and let it install.

---

## Step 2 — Download the project

```bash
git clone https://github.com/dubessix/Zora-uktron.git
cd Zora-uktron
```

> No git? Download the ZIP from the GitHub page → "Code" → "Download ZIP" → extract,
> then `cd Zora-uktron`.

---

## Step 3 — Create a Python virtual environment (important on Arch)

Arch Python can block installing packages globally (PEP 668). A **venv** avoids that:

```bash
python -m venv .venv
source .venv/bin/activate
```

You'll see `(.venv)` appear at the start of your prompt — that means it's active.
> Every new terminal, run `source .venv/bin/activate` again before step 4.

---

## Step 4 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Step 5 — Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Step 6 — Create your `.env` file (API keys)

```bash
cp .env.example .env
nano .env
```

`nano` is a text editor. Fill in your keys:

```env
GROQ_API_KEY_1=your_groq_key
GEMINI_API_KEY_1=your_gemini_key
NVIDIA_API_KEY_1=your_nvidia_key
SECRET_KEY=some_long_random_text
```

**Where to get free keys:**
- **Groq** (chat): https://console.groq.com → free key
- **Gemini** (memory): https://aistudio.google.com → free key
- **NVIDIA** (coding brain): https://build.nvidia.com → free `nvapi-` key

> **You can skip real keys** — Ultron still boots and runs in **mock mode** (it just
> won't give real AI answers until you add keys). Placeholder keys never crash it.

Save in nano: **Ctrl+O**, then **Enter**, then **Ctrl+X** to exit.

---

## Step 7 — Launch Ultron

Make sure you're in the project root (`cd Zora-uktron`), then:

```bash
./start_ultron.sh
```

The script:
- Checks ports (8000 backend, 5173 frontend)
- Starts the backend
- Starts the frontend
- Opens your browser at **http://127.0.0.1:5173**

> If you get "permission denied", run once: `chmod +x start_ultron.sh`

---

## Step 8 — Your first conversation

In the Ultron dashboard, try:

| You type | What happens |
|----------|--------------|
| `Hello Ultron` | Jarvis-style greeting |
| `make an auth api` | Coding mode → asks permission → writes code |
| `what is the weather` | Real weather |
| `run the tests` | Runs pytest + fixes errors |

---

## 🛠 Troubleshooting (freshers)

**"pip not installing / externally-managed-environment"**
```bash
# make sure venv is active first
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**"Port already in use"**
```bash
# find what's using port 8000 or 5173 and stop it, or:
sudo kill $(sudo lsof -t -i:8000)
```

**"command not found: npm / node"**
```bash
sudo pacman -S --needed nodejs npm
```

**Browser doesn't open automatically**
Just open http://127.0.0.1:5173 yourself.

**Voice doesn't work**
Use **Chrome or Edge** — Web Speech API isn't in Firefox.

**Want to stop Ultron**
Press **Ctrl+C** in the terminal (or close it).

---

## ✅ Done!
Ultron & Zora are running on Arch. Add real keys whenever you want full AI power.

---

*Full docs: [`README.md`](../README.md) · [`SETUP_GUIDE.md`](../SETUP_GUIDE.md)*
