#!/usr/bin/env bash
# ============================================================================
# MiroFish-Offline — Prerequisite Checker (Linux/macOS)
# ============================================================================
# Checks for common prerequisites without installing anything.
#
# Usage:
#   bash scripts/linux/check_prereqs.sh
#   bash scripts/linux/check_prereqs.sh --docker
# ============================================================================

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; NC='\033[0m'

section() { echo -e "\n${CYAN}$(printf '=%.0s' {1..78})${NC}"; echo -e "${CYAN}$1${NC}"; echo -e "${CYAN}$(printf '=%.0s' {1..78})${NC}"; }
ok()    { echo -e "  ${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "  ${YELLOW}[!!]${NC} $1"; }
missing() { echo -e "  ${RED}[MISSING]${NC} $1"; }

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

section "MiroFish-Offline Prereqs Check"
echo "  Repo root: $REPO_ROOT"
echo "  Bash: $BASH_VERSION"

section "Core Tools"

for cmd in python3 node npm git; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>/dev/null | head -1 || echo "installed")
        ok "$cmd : $ver"
    else
        missing "$cmd"
    fi
done

section "Local Services (Optional But Recommended)"

if command -v ollama &>/dev/null; then
    ok "ollama cli : $(ollama --version 2>/dev/null || echo 'installed')"
else
    missing "ollama cli"
fi

if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    ok "Ollama HTTP (http://localhost:11434)"
else
    warn "Ollama HTTP : NOT LISTENING"
fi

if curl -s http://localhost:7687 >/dev/null 2>&1 || nc -z localhost 7687 2>/dev/null; then
    ok "Neo4j Bolt (bolt://localhost:7687)"
else
    warn "Neo4j Bolt : NOT LISTENING"
fi

if curl -s http://localhost:5001/health >/dev/null 2>&1; then
    ok "Backend (http://localhost:5001) : LISTENING"
else
    warn "Backend : NOT LISTENING"
fi

if curl -s http://localhost:5173 >/dev/null 2>&1; then
    ok "Frontend dev (http://localhost:5173) : LISTENING"
else
    warn "Frontend dev : NOT LISTENING"
fi

section "Docker (Optional)"

if [[ "${1:-}" == "--docker" ]]; then
    if command -v docker &>/dev/null; then
        ok "docker : $(docker version --format '{{.Server.Version}}' 2>/dev/null || echo 'installed')"
    else
        missing "docker"
        echo "  Hint: install Docker Desktop or Docker Engine."
    fi
else
    echo "  Skipped docker checks. Re-run with --docker to validate."
fi

section "Next Steps"
echo "  1) Read: docs/ARCHITECTURE.md"
echo "  2) Install: bash install/install.sh"
echo "  3) Start: bash scripts/linux/start_swarmbook.sh"
echo "  4) Smoke test: bash scripts/linux/smoke_test_swarmbook.sh"
