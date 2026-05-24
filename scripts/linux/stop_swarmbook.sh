#!/usr/bin/env bash
# ============================================================================
# MiroFish-Offline — Stop Script (Linux/macOS)
# ============================================================================
# Stops backend and frontend processes using PID files.
#
# Usage:
#   bash scripts/linux/stop_swarmbook.sh
# ============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PID_DIR="$REPO_ROOT/.mirofish_pids"

stop_by_pid() {
    local pid_file="$1"
    local name="$2"

    if [[ ! -f "$pid_file" ]]; then
        echo "  No $name pid file found: $pid_file"
        return
    fi

    local pid
    pid=$(cat "$pid_file" 2>/dev/null | head -1)
    if [[ -z "$pid" ]] || ! [[ "$pid" =~ ^[0-9]+$ ]]; then
        echo "  $name pid file is invalid: $pid_file"
        return
    fi

    if kill -0 "$pid" 2>/dev/null; then
        echo "  Stopping $name (pid $pid)..."
        kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
        echo "  Stopped $name."
    else
        echo "  $name is not running (pid $pid)."
    fi
}

stop_by_pid "$PID_DIR/frontend.pid" "frontend"
stop_by_pid "$PID_DIR/backend.pid" "backend"

echo ""
echo "If ports are still busy, check: ss -tlnp | grep -E '5001|5173'"
