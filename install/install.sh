#!/usr/bin/env bash
# ============================================================================
# MiroFish-Offline — Master Installer (Linux/macOS)
# ============================================================================
# Frictionless one-command setup for Linux and macOS.
#
# What it does:
#   1. Checks prerequisites (Python, Node.js, Git, Docker optional)
#   2. Validates the repository
#   3. Creates Python virtual environment and installs all dependencies
#   4. Installs Node.js frontend dependencies
#   5. Sets up .env from .env.example
#   6. Offers Docker-based (Neo4j + Ollama) or manual service setup
#   7. Pulls required Ollama models
#   8. Runs a smoke test to verify everything works
#
# Usage:
#   bash install/install.sh
#   # or: chmod +x install/install.sh && ./install/install.sh
#
# Options:
#   --repo-path /path/to/repo    # Where to install (default: script parent)
#   --skip-docker                # Skip Docker setup
#   --skip-smoke-test            # Skip post-install smoke test
#   --model qwen2.5:14b          # Override default LLM model
#   --quiet                      # Non-interactive, accept all defaults
# ============================================================================

set -euo pipefail

# ============================================================================
# Parse arguments
# ============================================================================
REPO_PATH=""
SKIP_DOCKER=false
SKIP_SMOKE_TEST=false
MODEL="qwen2.5:32b"
QUIET=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-path)    REPO_PATH="$2"; shift 2 ;;
        --skip-docker)  SKIP_DOCKER=true; shift ;;
        --skip-smoke-test) SKIP_SMOKE_TEST=true; shift ;;
        --model)        MODEL="$2"; shift 2 ;;
        --quiet)        QUIET=true; shift ;;
        *)              echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Resolve repo path
if [[ -z "$REPO_PATH" ]]; then
    REPO_PATH="$(cd "$(dirname "$0")/.." && pwd)"
fi

# ============================================================================
# Color helpers
# ============================================================================
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; GRAY='\033[0;90m'; NC='\033[0m'

ok()    { echo -e "  ${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "  ${YELLOW}[!!]${NC} $1"; }
err()   { echo -e "  ${RED}[ERR]${NC} $1"; }
step()  { echo -e "\n${CYAN}>>> $1${NC}"; }
info()  { echo -e "  ${GRAY}-> $1${NC}"; }

# ============================================================================
step "MiroFish-Offline Installer"
info "Target: $REPO_PATH"

# ============================================================================
# 1. Prerequisite checks
# ============================================================================
step "1/8 Checking prerequisites"

check_cmd() {
    if command -v "$1" &>/dev/null; then
        ver=$("$1" --version 2>/dev/null | head -1 || echo "installed")
        ok "$1 : $ver"
        return 0
    else
        err "$1 : NOT FOUND"
        return 1
    fi
}

ALL_OK=true
check_cmd python3 || ALL_OK=false
check_cmd node || ALL_OK=false
check_cmd npm || ALL_OK=false
check_cmd git || ALL_OK=false

if [[ "$ALL_OK" == "false" ]]; then
    err "Missing prerequisites. Install them first:"
    info "  Ubuntu/Debian: sudo apt install python3 python3-venv nodejs npm git"
    info "  macOS:         brew install python node git"
    exit 1
fi

# Python version check
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=${PY_VER%%.*}
PY_MINOR=${PY_VER#*.}
PY_MINOR=${PY_MINOR%%.*}
if [[ $PY_MAJOR -lt 3 ]] || [[ $PY_MAJOR -eq 3 && $PY_MINOR -lt 11 ]]; then
    err "Python $PY_VER is too old. Need 3.11+."
    exit 1
else
    ok "Python $PY_VER meets minimum 3.11"
fi

# Docker check
DOCKER_AVAILABLE=false
if command -v docker &>/dev/null; then
    if docker info &>/dev/null; then
        ok "Docker : running"
        DOCKER_AVAILABLE=true
    else
        warn "Docker : installed but not running"
    fi
else
    warn "Docker : not installed (optional)"
fi

# ============================================================================
# 2. Validate repository
# ============================================================================
step "2/8 Validating repository"

if [[ -f "$REPO_PATH/backend/run.py" ]]; then
    ok "Repository already present at $REPO_PATH"
else
    info "Repository not found at $REPO_PATH"
    if [[ "$QUIET" == "true" ]] || read -p "Clone from GitHub? (y/n) " -r; then
        PARENT=$(dirname "$REPO_PATH")
        NAME=$(basename "$REPO_PATH")
        cd "$PARENT"
        git clone https://github.com/nikmcfly/MiroFish-Offline-Book.git "$NAME"
        cd - >/dev/null
        ok "Repository cloned"
    else
        err "Cannot proceed without repository."
        exit 1
    fi
fi

# ============================================================================
# 3. Python virtual environment + dependencies
# ============================================================================
step "3/8 Setting up Python environment"

BACKEND_DIR="$REPO_PATH/backend"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
VENV_PIP="$BACKEND_DIR/.venv/bin/pip"

if [[ -f "$VENV_PYTHON" ]]; then
    ok "Virtual environment exists"
else
    info "Creating virtual environment..."
    cd "$BACKEND_DIR"
    python3 -m venv .venv
    cd - >/dev/null
    ok "Virtual environment created"
fi

info "Installing Python dependencies (this may take a few minutes)..."
cd "$BACKEND_DIR"
"$VENV_PYTHON" -m pip install --upgrade pip >/dev/null 2>&1
"$VENV_PIP" install -r requirements.txt 2>&1 | tail -5 | while read -r line; do info "$line"; done
cd - >/dev/null
ok "Python dependencies installed"

# ============================================================================
# 4. Node.js frontend dependencies
# ============================================================================
step "4/8 Setting up frontend"

FRONTEND_DIR="$REPO_PATH/frontend"
if [[ -d "$FRONTEND_DIR/node_modules" ]]; then
    ok "Frontend dependencies exist"
else
    info "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm ci 2>&1 | tail -3 | while read -r line; do info "$line"; done
    cd - >/dev/null
    ok "Frontend dependencies installed"
fi

# Root-level dev dependencies
if [[ ! -d "$REPO_PATH/node_modules/concurrently" ]]; then
    info "Installing root dev dependencies..."
    cd "$REPO_PATH"
    npm ci 2>&1 | tail -2 | while read -r line; do info "$line"; done
    cd - >/dev/null
    ok "Root dependencies installed"
fi

# ============================================================================
# 5. Environment configuration
# ============================================================================
step "5/8 Configuring environment"

ENV_FILE="$REPO_PATH/.env"
ENV_EXAMPLE="$REPO_PATH/.env.example"

if [[ -f "$ENV_FILE" ]]; then
    ok ".env already exists"
elif [[ -f "$ENV_EXAMPLE" ]]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "")
    if [[ -n "$SECRET_KEY" ]]; then
        sed -i.bak "s/SECRET_KEY=/SECRET_KEY=$SECRET_KEY/" "$ENV_FILE"
        rm -f "${ENV_FILE}.bak"
    fi
    ok ".env created from template with random SECRET_KEY"
else
    warn ".env.example not found — create .env manually"
fi

# ============================================================================
# 6. Docker services
# ============================================================================
step "6/8 Setting up services"

if [[ "$SKIP_DOCKER" == "true" ]] || [[ "$DOCKER_AVAILABLE" == "false" ]]; then
    warn "Skipping Docker setup"
    info "Ensure Neo4j and Ollama are running manually:"
    info "  docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/mirofish neo4j:5.18-community"
    info "  ollama serve"
else
    info "Starting Docker Compose services..."
    cd "$REPO_PATH"

    RUNNING=$(docker compose ps --format json 2>/dev/null | wc -l || echo "0")
    if [[ "$RUNNING" -gt 0 ]]; then
        ok "Docker services already running"
    else
        # Detect GPU
        HAS_GPU=false
        if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
            HAS_GPU=true
        fi

        PROFILE=$([[ "$HAS_GPU" == "true" ]] && echo "gpu" || echo "cpu")
        info "Using profile: $PROFILE (GPU: $HAS_GPU)"

        docker compose --profile "$PROFILE" up -d 2>&1 | while read -r line; do info "$line"; done

        # Wait for Neo4j
        info "Waiting for Neo4j to be healthy..."
        RETRIES=0
        while [[ $RETRIES -lt 30 ]]; do
            HEALTHY=$(docker inspect --format='{{.State.Health.Status}}' mirofish-neo4j 2>/dev/null || echo "")
            [[ "$HEALTHY" == "healthy" ]] && break
            sleep 5
            RETRIES=$((RETRIES + 1))
        done
        if [[ "$HEALTHY" == "healthy" ]]; then
            ok "Neo4j is healthy"
        else
            warn "Neo4j may not be fully ready yet (timeout after $((RETRIES * 5))s)"
        fi
    fi
    cd - >/dev/null
fi

# ============================================================================
# 7. Pull Ollama models
# ============================================================================
step "7/8 Pulling Ollama models"

MODELS_NEEDED=("$MODEL" "nomic-embed-text")

if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    for MODEL_NAME in "${MODELS_NEEDED[@]}"; do
        if ollama list 2>/dev/null | grep -q "$MODEL_NAME"; then
            ok "Model already present: $MODEL_NAME"
        else
            info "Pulling $MODEL_NAME (this may take a while)..."
            ollama pull "$MODEL_NAME" 2>&1 | tail -3 | while read -r line; do info "$line"; done
            ok "Model pulled: $MODEL_NAME"
        fi
    done
else
    warn "Ollama not listening on port 11434"
    info "If using Docker: docker exec mirofish-ollama ollama pull $MODEL"
    info "If using Docker: docker exec mirofish-ollama ollama pull nomic-embed-text"
fi

# ============================================================================
# 8. Smoke test
# ============================================================================
if [[ "$SKIP_SMOKE_TEST" != "true" ]]; then
    step "8/8 Running smoke test"

    info "Starting backend for smoke test..."
    cd "$BACKEND_DIR"
    "$VENV_PYTHON" -m flask --app app run --port 5001 &>/dev/null &
    BACKEND_PID=$!
    cd - >/dev/null

    info "Waiting for backend..."
    RETRIES=0
    while [[ $RETRIES -lt 20 ]]; do
        if curl -s http://localhost:5001/health >/dev/null 2>&1; then break; fi
        sleep 2
        RETRIES=$((RETRIES + 1))
    done

    if [[ $RETRIES -lt 20 ]]; then
        ok "Backend is running"

        SMOKE_SCRIPT="$REPO_PATH/scripts/linux/smoke_test_swarmbook.sh"
        if [[ -f "$SMOKE_SCRIPT" ]]; then
            bash "$SMOKE_SCRIPT" http://localhost:5001 2>&1 | while read -r line; do info "$line"; done
            ok "Smoke test passed"
        fi
    else
        warn "Backend did not start in time"
    fi

    kill $BACKEND_PID 2>/dev/null || true
else
    step "8/8 Smoke test skipped"
fi

# ============================================================================
# Done
# ============================================================================
step "Installation Complete"
echo ""
echo -e "  ${GREEN}Start:${NC}    ./scripts/linux/start_swarmbook.sh"
echo -e "  ${GREEN}Stop:${NC}     ./scripts/linux/stop_swarmbook.sh"
echo -e "  ${GREEN}Health:${NC}   ./scripts/linux/check_prereqs.sh --docker"
echo -e "  ${GREEN}Docker:${NC}   docker compose --profile gpu up -d  (or --profile cpu)"
echo ""
echo -e "  ${CYAN}Frontend:${NC} http://localhost:5173"
echo -e "  ${CYAN}Backend:${NC}  http://localhost:5001"
echo -e "  ${CYAN}Neo4j:${NC}    http://localhost:7474"
echo ""

if [[ "$QUIET" != "true" ]]; then
    read -p "Press Enter to exit" -r
fi
