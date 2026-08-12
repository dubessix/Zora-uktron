#!/usr/bin/env bash
# =============================================================================
#  ULTRON — One-Command Launcher (Ubuntu / Linux / macOS)
#  Green, cool terminal vibe. Boots backend + frontend together.
# =============================================================================

set -e

# ---- ANSI colors (cool green terminal vibe) -------------------------------
GREEN='\033[1;32m'
DIM='\033[2;37m'
CYAN='\033[1;36m'
RED='\033[1;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'
BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}${BOLD}"
echo "  ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗"
echo "  ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║"
echo "  ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║"
echo "  ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║"
echo "  ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║"
echo "   ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝"
echo -e "${RESET}"
echo -e "${DIM}  Personal AI Operating System & Coding Partner${RESET}"
echo -e "${GREEN}  ────────────────────────────────────────────${RESET}"
echo ""

# ---- 0. Preflight: .env check ---------------------------------------------
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env not found. Creating template...${RESET}"
    cp .env.example .env 2>/dev/null || {
        echo -e "${RED}❌ No .env.example either. Run 'ultron setup' or create .env manually.${RESET}"
        exit 1
    }
    echo -e "${YELLOW}   Edit .env and add your API keys, then run again.${RESET}"
    echo -e "${YELLOW}   (Placeholder keys work too — Ultron runs in mock mode.)${RESET}"
fi

# ---- 1. Port check (backend 8000, frontend 5173) --------------------------
echo -e "${CYAN}▸ Checking ports...${RESET}"
for port in 8000 5173; do
    if (echo > /dev/tcp/127.0.0.1/$port) 2>/dev/null; then
        echo -e "${RED}❌ Port $port is already in use. Close the occupying process and retry.${RESET}"
        exit 1
    fi
done
echo -e "${GREEN}  ✓ Ports 8000 & 5173 are free${RESET}"

# ---- 2. Frontend deps -----------------------------------------------------
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${CYAN}▸ Installing frontend dependencies (first run)...${RESET}"
    (cd frontend && npm install)
fi

# ---- 3. Boot backend in background -----------------------------------------
echo -e "${CYAN}▸ Booting Ultron backend...${RESET}"
if [ ! -f ".venv/bin/activate" ]; then
    python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
else
    .venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
fi
BACKEND_PID=$!
echo -e "${GREEN}  ✓ Backend started (PID $BACKEND_PID) — http://127.0.0.1:8000${RESET}"

# ---- 4. Boot frontend in background ----------------------------------------
echo -e "${CYAN}▸ Booting Ultron frontend...${RESET}"
(cd frontend && npm run dev -- --host 127.0.0.1) &
FRONTEND_PID=$!
echo -e "${GREEN}  ✓ Frontend started (PID $FRONTEND_PID) — http://127.0.0.1:5173${RESET}"

# ---- 5. Open browser after a short wait ------------------------------------
sleep 2
echo -e "${CYAN}▸ Opening Ultron dashboard...${RESET}"
xdg-open "http://127.0.0.1:5173" 2>/dev/null || open "http://127.0.0.1:5173" 2>/dev/null || true

# ---- 6. Keep alive + graceful shutdown -------------------------------------
trap 'echo -e "${YELLOW}\n▸ Shutting down Ultron...${RESET}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e "${GREEN}✓ Ultron offline. See you, Sir.${RESET}"; exit 0' INT TERM

echo ""
echo -e "${GREEN}${BOLD}  Ultron is ONLINE. Systems synchronized. Awaiting your command, Sir.${RESET}"
echo -e "${DIM}  Press Ctrl+C to stop.${RESET}"
echo ""

wait
