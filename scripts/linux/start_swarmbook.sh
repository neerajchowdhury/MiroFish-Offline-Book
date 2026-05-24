#!/usr/bin/env bash
# ============================================================================
# MiroFish-Offline — Start Script (Linux/macOS)
# ============================================================================
# Starts backend (Flask) and frontend (Vite dev server) in background.
# Writes PID files under .mirofish_pids/ for stop_swarmbook.sh.
#
# Usage:
#   bash scripts/linux/start_swarmbook.sh
#   bash scripts/linux/start_swarmbook.sh --backend-port 5001 --frontend-port 5173
#   bash scripts/linux/start_swarmbook.sh --skip-frontend
# ============================================================================

set -euo pipefail

GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

BACKEND_PORT=5001
FRONTEND_PORT=5173
SKIP_FRONTEND=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --backend-port)  BACKEND_PORT="$2"; shift 2 ;;
        --frontend-port) FRONTEND_PORT="$2"; shift 2 ;;
        --skip-frontend) SKIP_FRONTEND=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PID_DIR="$REPO_ROOT/.mirofish_pids"
mkdir -p "$PID_DIR"

BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"

# Use venv python when available
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
if [[ ! -f "$VENV_PYTHON" ]]; then
    VENV_PYTHON="python3"
fi

echo -e "${CYAN}>>> Starting MiroFish-Offline${NC}"

# Backend
echo "  Starting backend on port $BACKEND_PORT..."
cd "$BACKEND_DIR"
$VENV_PYTHON -m flask --app app run --port "$BACKEND_PORT" &>/dev/null &
echo $! > "$PID_DIR/backend.pid"
cd - >/dev/null
echo -e "  ${GREEN}Backend PID: $(cat $PID_DIR/backend.pid)${NC}"

# Frontend
if [[ "$SKIP_FRONTEND" != "true" ]]; then
    echo "  Starting frontend on port $FRONTEND_PORT..."
    cd "$FRONTEND_DIR"
    npm run dev -- --port "$FRONTEND_PORT" &>/dev/null &
    echo $! > "$PID_DIR/frontend.pid"
    cd - >/dev/null
    echo -e "  ${GREEN}Frontend PID: $(cat $PID_DIR/frontend.pid)${NC}"
fi

echo ""
echo -e "  ${GREEN}Backend:${NC}  http://localhost:$BACKEND_PORT"
if [[ "$SKIP_FRONTEND" != "true" ]]; then
    echo -e "  ${GREEN}Frontend:${NC} http://localhost:$FRONTEND_PORT"
fi
echo ""
echo "  Stop: bash scripts/linux/stop_swarmbook.sh"
