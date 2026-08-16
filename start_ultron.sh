#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [ ! -x ".venv/bin/python" ]; then
    echo "Ultron is not installed yet. Opening setup..."
    exec "$ROOT/SETUP_ULTRON_UBUNTU.sh"
fi

exec "$ROOT/.venv/bin/python" -m backend.app.cli start
