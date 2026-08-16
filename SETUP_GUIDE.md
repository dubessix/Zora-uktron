# Ultron Personal V1 Setup Guide

## Beginner path (no command typing)

- Windows 11: double-click `SETUP_ULTRON_WINDOWS.bat`.
- Ubuntu: double-click/run `SETUP_ULTRON_UBUNTU.sh`.

The setup window keeps live progress text at the top. Paste only the keys you have, click `Install / Repair`, and wait for the ready message. It creates branded application-menu entries for `Ultron`, `Stop Ultron`, and `Ultron Keys`, plus the main `Ultron` desktop shortcut when the desktop folder exists. Daily launch runs hidden/minimized and writes diagnostics to `data/logs/launcher-ui.log`; no command typing is required. Re-running setup refreshes the shortcuts and branded icon while preserving `.env`, config, database, memory, reminders, and backups.

The included verified prebuilt frontend means Node/npm is not required for the normal default-port installation. Node 20.19+ or 22.12+ is needed only for frontend development, changed frontend source, or a custom backend port.

## GitHub Codespaces Ubuntu desktop demo (no card, no local install)

1. Open the repository on GitHub and select `Code` → `Codespaces` → `Create codespace on main`.
2. Wait while GitHub builds the Ubuntu development container. The first build downloads the lightweight desktop and browser, so it can take several minutes.
3. The private forwarded page labelled `Ultron Ubuntu Desktop` opens. Select `Connect` and enter the demo desktop password `vscode`.
4. The real `SETUP_ULTRON_UBUNTU.sh` wrapper opens the Ultron Setup window automatically. Leave every key field empty and select `Install / Repair`.
5. Wait for `Ultron installation is ready`, then select `Start Ultron`. Chrome opens inside the cloud desktop at the normal loopback-only Ultron address.
6. Test the UI and local demo widgets. No-key chat must return the explicit Offline message rather than a fabricated model answer.
7. Use `Stop Ultron` when finished, then delete the Codespace from GitHub to stop compute/storage quota use.

This is a temporary Ubuntu development container, not Windows 11 and not the owner's real laptop. It cannot provide final microphone, speaker, Spotify, Windows Start Menu, private-provider, or long-duration acceptance. Never enter real API keys, GitHub tokens, passwords, or personal files into the demo.

## Free cloud pre-check (does not touch the owner's laptop)

On GitHub, open `Actions` → `Ultron Cloud Test` → `Run workflow`. GitHub creates temporary Ubuntu 24.04 and Windows cloud machines, installs the locked project, runs both Python suites and the frontend build, creates/inspects platform shortcuts, and performs an isolated real Start/Health/Stop cycle. The workflow is manual, read-only, uses no owner provider keys, retains diagnostic artifacts for seven days, and fails if source `data/` is touched.

A green cloud run verifies only the automated cloud scope. The Windows runner is not the owner's Windows 11 desktop, and cloud runners cannot verify real Start Menu clicks, microphone, speakers, Spotify, VS Code GUI, private provider credentials, or long-duration laptop behavior.

## 1. Prerequisites

Required:

- Python 3.10 or newer
- Git

Optional:

- Node.js 20.19+ or 22.12+ and npm for frontend rebuilding/custom ports
- ffmpeg for media conversion/playback workflows
- Spotify desktop for local Spotify controls
- a Chromium/Edge browser for the Web Speech API

## 2. Create the Python environment

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

For development/audits:

```bash
python -m pip install -r requirements-dev.txt
```

## 3. Initialize personal runtime files

```bash
python -m backend.app.cli setup
```

For a wheel installation use:

```bash
ultron setup
```

This creates writable database/cache/log directories, a user `config.yaml`, and a template `.env`. Re-running setup does not overwrite an existing `.env` or config.

## 4. Configure providers

Edit the generated `.env` locally. Example variable names:

```dotenv
GROQ_API_KEY_1=
GEMINI_API_KEY_1=
NVIDIA_API_KEY_1=
TAVILY_API_KEY=
GITHUB_TOKEN_1=
GITHUB_USERNAME_1=
```

Do not commit `.env`, paste credentials into source/config files, or place tokens in Git remote URLs.

Without a provider key, chat returns an explicit offline/unprocessed response. Local non-LLM tools remain available through their widgets/API.

## 5. Configure allowed directories

The secure default in `config.yaml` is the project/application home only:

```yaml
security:
  allowed_directories: ["."]
```

Add only personal roots that tools should access:

```yaml
security:
  allowed_directories:
    - "."
    - "~/Documents"
    - "~/Downloads"
    - "D:/Projects"
```

Sensitive/system paths and symlink escapes remain blocked.

## 6. Verify installation

```bash
python -m backend.app.cli doctor
python -m backend.app.cli start --check
```

or:

```bash
ultron doctor
ultron start --check
```

`doctor` reports required failures separately from optional warnings. It validates Node version, binaries, ports, writable storage, and YAML configuration; it does not claim live AI/microphone/Spotify readiness.

## 7. Start and stop

```bash
ultron start
```

The UI is loopback-only at `http://127.0.0.1:5173`. Press `Ctrl+C` in the launcher terminal to stop both child services. If a child exits unexpectedly, the launcher stops the sibling and returns a non-zero status.

## 8. Backups

Manual backup:

```bash
ultron backup
```

Integrity check:

```bash
ultron integrity
```

Restore is restricted to the approved backup directory and asks for the exact path confirmation:

```bash
ultron backup --restore --path <approved-backup.db>
```

Automatic daily backups and retention are configured under `durability:` in `config.yaml`.

## 9. Verification commands

```bash
python -m pytest -q
python -m unittest discover -s tests -p 'test*.py'
python -m pip_audit -r requirements-dev.txt --progress-spinner off
ruff check backend tests launcher.py setup.py
bandit -q -r backend
cd frontend
npm ci
npm audit --audit-level=low
npm run build
```

## 10. Owner-hardware acceptance

Before calling the laptop installation accepted, manually verify:

- browser opens only after both services are healthy;
- microphone permission and wake words work;
- Edge-TTS returns audible speech and interruption works;
- Spotify commands reflect the real desktop player;
- provider status/live checks work with the owner's keys;
- Windows shutdown leaves no child process or occupied port;
- backup and confirmed restore work on a disposable test copy first.
