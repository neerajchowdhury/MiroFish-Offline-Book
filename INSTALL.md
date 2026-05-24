# MiroFish-Offline — Complete Installation & Transfer Guide

<div align="center">

**Fully local, zero-cloud multi-agent swarm intelligence engine**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=node.js)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Optional-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)

</div>

---

## Table of Contents

1. [What is MiroFish-Offline?](#what-is-mirofish-offline)
2. [Hardware Requirements](#hardware-requirements)
3. [Quick Start — One Command Install](#quick-start--one-command-install)
4. [Transfer to Another Laptop](#transfer-to-another-laptop)
5. [Manual Installation (Step by Step)](#manual-installation-step-by-step)
6. [Docker Installation](#docker-installation)
7. [Configuration Reference](#configuration-reference)
8. [Backup & Restore](#backup--restore)
9. [Starting & Stopping](#starting--stopping)
10. [Verification & Smoke Tests](#verification--smoke-tests)
11. [Troubleshooting](#troubleshooting)
12. [Project Structure](#project-structure)
13. [Architecture Overview](#architecture-overview)

---

## What is MiroFish-Offline?

MiroFish-Offline is a **fully local** multi-agent swarm intelligence engine that simulates public opinion, market sentiment, and social dynamics. Upload any document and it generates hundreds of AI agents with unique personalities that simulate public reaction on social media — posts, arguments, opinion shifts — hour by hour.

**Swarmbook** is an additive module that lets authors stress-test manuscripts before publication by generating synthetic reader personas and simulating their reactions across platforms (Goodreads, BookTok, Reddit, etc.).

| Feature | Original MiroFish | MiroFish-Offline |
|---|---|---|
| UI Language | Chinese | **English** |
| Graph Storage | Zep Cloud | **Neo4j CE (local)** |
| LLM | DashScope/OpenAI | **Ollama (local)** |
| Embeddings | Cloud API | **nomic-embed-text (local)** |
| Cloud Dependencies | Required | **Zero** |

---

## Hardware Requirements

| Component | Minimum | Recommended | Notes |
|---|---|---|---|
| RAM | 16 GB | 32 GB | 32b model needs ~20GB VRAM |
| VRAM (GPU) | 10 GB (14b model) | 24 GB (32b model) | NVIDIA recommended |
| Disk | 20 GB | 50 GB | Models take ~20GB |
| CPU | 4 cores | 8+ cores | CPU-only works but slower |

**Lighter setups:** Use `qwen2.5:14b` (8GB VRAM) or `qwen2.5:7b` (4GB VRAM) for less powerful hardware.

---

## Quick Start — One Command Install

The fastest way to get running. This single command handles everything: prerequisites check, dependency installation, service setup, model downloads, and verification.

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1
```

### Linux / macOS

```bash
bash install/install.sh
```

### Options

| Flag | Description | Default |
|---|---|---|
| `--repo-path "D:\Path"` | Custom install location | Current directory |
| `--skip-docker` | Skip Docker service setup | false |
| `--skip-smoke-test` | Skip post-install verification | false |
| `--model qwen2.5:14b` | Override LLM model | `qwen2.5:32b` |
| `--quiet` | Non-interactive mode | false |

### What the installer does

1. **Checks prerequisites** — Python 3.11+, Node.js 18+, Git
2. **Validates repository** — Clones if missing, validates if present
3. **Creates Python venv** — Installs all backend dependencies
4. **Installs frontend** — npm ci for Vue 3 + Vite
5. **Configures environment** — Creates `.env` with random `SECRET_KEY`
6. **Starts services** — Docker Compose for Neo4j + Ollama (GPU or CPU)
7. **Pulls models** — Downloads LLM and embedding models
8. **Runs smoke test** — Verifies full pipeline works end-to-end

---

## Transfer to Another Laptop

Moving MiroFish-Offline to a new machine is straightforward. Choose the method that fits your needs.

### Method A: Full Reinstall (Recommended)

Cleanest approach. The new laptop gets a fresh install with your data restored.

**On the source laptop:**
```powershell
# Windows
powershell -ExecutionPolicy Bypass -File .\install\backup_restore.ps1 -Action Backup -BackupDir "D:\MiroFishBackup"

# Linux/macOS
tar czf mirofish_backup.tar.gz backend/uploads/ configs/book_sim/ .env
```

**Transfer the backup** via USB drive, network share, or cloud storage.

**On the destination laptop:**
```powershell
# 1. Run the installer (handles all dependencies)
powershell -ExecutionPolicy Bypass -File .\install\install.ps1

# 2. Restore your data
powershell -ExecutionPolicy Bypass -File .\install\backup_restore.ps1 -Action Restore -BackupDir "D:\MiroFishBackup"
```

### Method B: Direct Clone

For identical environments (same OS, same Python/Node versions).

```bash
# On source: compress everything
tar czf mirofish-full.tar.gz \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='backend/.venv' \
  --exclude='backend/uploads' \
  --exclude='__pycache__' \
  .

# On destination: extract and install
tar xzf mirofish-full.tar.gz
cd MiroFish-Offline-Book
bash install/install.sh --skip-docker  # if you have existing services
```

### Method C: Docker Image (Portable)

Build a self-contained image with all dependencies baked in.

```bash
# On source
docker compose build
docker save mirofish-offline-mirofish > mirofish-image.tar
docker save neo4j:5.18-community > neo4j-image.tar
docker save ollama/ollama:latest > ollama-image.tar

# Transfer .tar files to destination

# On destination
docker load < mirofish-image.tar
docker load < neo4j-image.tar
docker load < ollama-image.tar
docker compose up -d
```

---

## Manual Installation (Step by Step)

If you prefer full control over each step.

### Step 1: Install Prerequisites

**Windows:**
```powershell
# Python 3.11+ (from Microsoft Store or python.org)
winget install Python.Python.3.11

# Node.js 18+
winget install OpenJS.NodeJS.LTS

# Git
winget install Git.Git
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm git curl
```

**macOS:**
```bash
brew install python@3.11 node git
```

### Step 2: Clone Repository

```bash
git clone https://github.com/nikmcfly/MiroFish-Offline-Book.git
cd MiroFish-Offline-Book
```

### Step 3: Set Up Python Environment

```bash
cd backend
python3 -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cd ..
```

### Step 4: Set Up Frontend

```bash
npm ci
cd frontend && npm ci && cd ..
```

### Step 5: Configure Environment

```bash
cp .env.example .env

# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Paste the output into .env as SECRET_KEY=...
```

### Step 6: Start Services

See [Docker Installation](#docker-installation) or [Manual Services](#manual-services) below.

---

## Docker Installation

Docker is the recommended way to run Neo4j and Ollama.

### GPU Mode (NVIDIA)

Requires: NVIDIA GPU + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

```bash
docker compose --profile gpu up -d
```

### CPU Mode (All Systems)

Works on any machine but LLM inference is significantly slower.

```bash
docker compose --profile cpu up -d
```

### Pull Models

```bash
# Docker GPU
docker exec mirofish-ollama ollama pull qwen2.5:32b
docker exec mirofish-ollama ollama pull nomic-embed-text

# Docker CPU
docker exec mirofish-ollama-cpu ollama pull qwen2.5:7b
docker exec mirofish-ollama-cpu ollama pull nomic-embed-text
```

### Verify Services

```bash
docker compose ps
# Should show: mirofish-neo4j (healthy), mirofish-ollama (running)
```

### Manual Services (No Docker)

**Neo4j:**
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mirofish \
  neo4j:5.18-community
```

**Ollama:**
```bash
# Linux/macOS
ollama serve &
ollama pull qwen2.5:32b
ollama pull nomic-embed-text

# Windows: install from https://ollama.com/download
ollama pull qwen2.5:32b
ollama pull nomic-embed-text
```

---

## Configuration Reference

All settings live in `.env` (copied from `.env.example`).

### Core Settings

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(auto-generated)* | Flask session secret — must be 64 hex chars |
| `FLASK_DEBUG` | `True` | Set to `False` in production |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated allowed origins |

### LLM Settings

| Variable | Default | Description |
|---|---|---|
| `LLM_API_KEY` | `ollama` | Any non-empty value for Ollama |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | OpenAI-compatible API endpoint |
| `LLM_MODEL_NAME` | `qwen2.5:32b` | Model to use for generation |

### Neo4j Settings

| Variable | Default | Description |
|---|---|---|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j Bolt protocol URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `mirofish` | Neo4j password |

### Embedding Settings

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `EMBEDDING_BASE_URL` | `http://localhost:11434` | Ollama base URL for embeddings |

### Cloud Providers (Optional)

Only used in `hybrid_safe` or `cloud_quality` privacy modes.

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_BASE_URL` | Gemini API base URL |
| `NVIDIA_API_KEY` | NVIDIA NIM API key |

---

## Backup & Restore

### Windows

```powershell
# Backup
powershell -ExecutionPolicy Bypass -File .\install\backup_restore.ps1 -Action Backup -BackupDir "D:\MiroFishBackup"

# Restore
powershell -ExecutionPolicy Bypass -File .\install\backup_restore.ps1 -Action Restore -BackupDir "D:\MiroFishBackup"
```

### Linux/macOS

```bash
# Backup
tar czf mirofish_backup_$(date +%Y%m%d).tar.gz \
  backend/uploads/ configs/book_sim/ .env

# Restore
tar xzf mirofish_backup_*.tar.gz -C /path/to/MiroFish-Offline-Book/
```

### What Gets Backed Up

| Item | Description |
|---|---|
| `backend/uploads/book_sim_cache/` | Cached evidence packs and simulations |
| `backend/uploads/simulations/` | Legacy OASIS simulation data |
| `backend/uploads/reports/` | Generated reports |
| `backend/uploads/projects/` | Project metadata |
| `configs/book_sim/` | Custom YAML configurations |
| `.env` | Environment configuration (contains secrets) |
| Neo4j dump | Full database export (if Docker running) |

---

## Starting & Stopping

### Windows

```powershell
# Start
.\scripts\windows\start_swarmbook.ps1

# Stop
.\scripts\windows\stop_swarmbook.ps1

# Check prerequisites
.\scripts\windows\check_prereqs.ps1 -CheckDocker

# Smoke test
.\scripts\windows\smoke_test_swarmbook.ps1
```

### Linux/macOS

```bash
# Start
bash scripts/linux/start_swarmbook.sh

# Stop
bash scripts/linux/stop_swarmbook.sh

# Check prerequisites
bash scripts/linux/check_prereqs.sh --docker

# Smoke test
bash scripts/linux/smoke_test_swarmbook.sh
```

### Docker

```bash
# Start all services
docker compose --profile gpu up -d   # or --profile cpu

# Stop all services
docker compose down

# View logs
docker compose logs -f
```

### Ports

| Service | Port | URL |
|---|---|---|
| Frontend (dev) | 5173 | http://localhost:5173 |
| Backend API | 5001 | http://localhost:5001 |
| Neo4j Browser | 7474 | http://localhost:7474 |
| Neo4j Bolt | 7687 | bolt://localhost:7687 |
| Ollama API | 11434 | http://localhost:11434 |

---

## Verification & Smoke Tests

After installation, verify everything works:

### 1. Prerequisite Check

```powershell
# Windows
.\scripts\windows\check_prereqs.ps1 -CheckDocker

# Linux/macOS
bash scripts/linux/check_prereqs.sh --docker
```

### 2. Health Endpoint

```bash
curl http://localhost:5001/health
# Expected: {"status":"ok","service":"MiroFish-Offline Backend"}

curl http://localhost:5001/api/book-sim/health
# Expected: {"success":true,"data":{"router":{"ok":true},...}}
```

### 3. Full Smoke Test

Runs a complete pipeline: create project → build evidence pack → simulate → chat with persona.

```powershell
# Windows
.\scripts\windows\smoke_test_swarmbook.ps1

# Linux/macOS
bash scripts/linux/smoke_test_swarmbook.sh
```

### 4. Unit Tests

```bash
cd backend
pytest tests/ -v
# Expected: 162+ tests pass
```

### 5. Neo4j Connection

```bash
# Via browser
open http://localhost:7474
# Login: neo4j / mirofish

# Via Bolt (Python)
python -c "from neo4j import GraphDatabase; d=GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','mirofish')); d.verify_connectivity(); print('OK')"
```

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: neo4j` | Run `pip install -r requirements.txt` in backend/.venv |
| `Ollama connection refused` | Ensure Ollama is running: `ollama serve` or `docker compose up -d` |
| `Neo4j not healthy` | Wait 30s, then `docker compose restart neo4j` |
| `Port 5001 already in use` | Change port: `start_swarmbook.ps1 -BackendPort 5002` |
| `Python version too old` | Install Python 3.11+ from python.org |
| `npm ci fails` | Delete `node_modules` and `package-lock.json`, then retry |
| `GPU not detected` | Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/), use `--profile cpu` as fallback |
| `SECRET_KEY not set` | Run `python -c "import secrets; print(secrets.token_hex(32))"` and paste into `.env` |
| `CORS error in browser` | Add your frontend URL to `CORS_ORIGINS` in `.env` |

### Log Locations

| Component | Location |
|---|---|
| Backend logs | `backend/logs/` |
| Flask startup | Console output |
| Neo4j logs | `docker logs mirofish-neo4j` |
| Ollama logs | `docker logs mirofish-ollama` |
| Smoke test | `backend/install_smoke.log` |

### Clean Slate Reset

```bash
# Stop everything
docker compose down
.\scripts\windows\stop_swarmbook.ps1  # or bash scripts/linux/stop_swarmbook.sh

# Clear cached data
rm -rf backend/uploads/book_sim_cache/
rm -rf backend/uploads/simulations/
rm -rf backend/uploads/reports/
rm -rf backend/uploads/projects/

# Remove Docker volumes (destroys all Neo4j data)
docker compose down -v

# Reinstall
bash install/install.sh
```

---

## Project Structure

```
MiroFish-Offline-Book/
├── install/                          # One-command installers
│   ├── install.ps1                   #   Windows installer
│   ├── install.sh                    #   Linux/macOS installer
│   └── backup_restore.ps1            #   Backup & restore utility
│
├── scripts/
│   ├── windows/                      # Windows management scripts
│   │   ├── check_prereqs.ps1         #   Prerequisite checker
│   │   ├── start_swarmbook.ps1       #   Start services
│   │   ├── stop_swarmbook.ps1        #   Stop services
│   │   └── smoke_test_swarmbook.ps1  #   End-to-end smoke test
│   └── linux/                        # Linux/macOS equivalents
│       ├── check_prereqs.sh
│       ├── start_swarmbook.sh
│       ├── stop_swarmbook.sh
│       └── smoke_test_swarmbook.sh
│
├── backend/                          # Flask API (Python 3.11+)
│   ├── app/
│   │   ├── __init__.py               #   App factory, CORS, teardown
│   │   ├── config.py                 #   Config from .env
│   │   ├── api/                      #   REST API blueprints
│   │   │   ├── _legacy_error_handler.py  # Shared error handling
│   │   │   ├── book_sim.py           #   Swarmbook endpoints
│   │   │   ├── simulation/           #   Legacy OASIS endpoints (split)
│   │   │   ├── graph.py              #   Graph CRUD endpoints
│   │   │   └── report.py             #   Report endpoints
│   │   ├── book_sim/                 #   Swarmbook module
│   │   │   ├── models.py             #   Typed dataclasses
│   │   │   ├── privacy_guard.py      #   System-wide privacy enforcement
│   │   │   ├── validators.py         #   Input validation
│   │   │   ├── provider_router.py    #   LLM provider routing
│   │   │   ├── providers/            #   Ollama, Gemini, NVIDIA adapters
│   │   │   ├── simulation/           #   3-pass simulation pipeline
│   │   │   ├── scoring/              #   7 scoring modules
│   │   │   └── ...
│   │   ├── storage/                  #   Neo4j graph storage
│   │   └── services/                 #   Legacy simulation services
│   ├── tests/                        # 32 test files, 162+ tests
│   ├── run.py                        # Entry point
│   └── requirements.txt              # Python dependencies
│
├── frontend/                         # Vue 3 + Vite UI
│   ├── src/
│   │   ├── views/swarmbook/          #   Swarmbook screens
│   │   └── api/bookSim.js            #   API client
│   └── dist/                         #   Built output
│
├── configs/book_sim/                 # YAML configs
│   ├── model_routes.yaml             #   Provider route definitions
│   ├── privacy_modes.yaml            #   Privacy mode rules
│   ├── reader_archetypes.yaml        #   Synthetic reader templates
│   ├── platform_styles.yaml          #   Platform output formats
│   ├── scoring_weights.yaml          #   Score weighting config
│   └── local_profiles.yaml           #   Hardware profiles
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # System architecture
│   ├── SWARMBOOK_CONTEXT.md          # Swarmbook background
│   ├── SWARMBOOK_PHASE_STATUS.md     # Development phase status
│   ├── SWARMBOOK_CHANGELOG.md        # Change history
│   └── SWARMBOOK_DECISIONS.md        # Design decisions
│
├── docker-compose.yml                # Docker service definitions
├── Dockerfile                        # Container build definition
├── package.json                      # Root npm scripts
└── .env.example                      # Environment template
```

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3 + Vite)                    │
│  Legacy MiroFish UI (/) + Swarmbook UI (/swarmbook/*)        │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼───────────────────────────────────────┐
│                    Flask Backend (Python 3.11)                │
│                                                              │
│  Legacy Routes:          Swarmbook Routes (additive):        │
│  /api/graph/*            /api/book-sim/projects              │
│  /api/simulation/*       /api/book-sim/evidence-packs        │
│  /api/report/*           /api/book-sim/simulate              │
│                          /api/book-sim/personas/<id>/chat    │
│                          /api/book-sim/compare               │
│                          /api/book-sim/health                │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                    Service / Storage Layer                    │
│                                                              │
│  Legacy:                 Swarmbook (book_sim):               │
│  GraphStorage (abstract)  ProviderRouter (+ PrivacyGuard)    │
│  Neo4jStorage             EvidencePackBuilder                │
│  SearchService            SimulationOrchestrator             │
│  EmbeddingService         ScoringEngine (7 modules)          │
│  NERExtractor             ReportBuilder                      │
│  EntityReader             PersonaInterrogator                │
│  ReportAgent              DraftComparator                    │
│  SimulationManager        BookGraphPersistence              │
│  OasisProfileGenerator    RuntimeStore (atomic file-backed)  │
│                          LocalArtifactCache (thread-safe)    │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                    External Services                          │
│                                                              │
│  Neo4j CE 5.18 (graph DB)  Ollama (local LLM)               │
│  [Optional] Gemini API     [Optional] NVIDIA NIM API         │
└───────────────────────────────────────────────────────────────┘
```

### Privacy Modes

| Mode | Behavior |
|---|---|
| `local_only` | No external API calls. Only Ollama permitted. Enforced by PrivacyGuard. |
| `hybrid_safe` | Only derived/compact artifacts may be sent to cloud providers. |
| `cloud_quality` | Full evidence packs may be sent to cloud providers for higher quality. |

### Key Design Decisions

- **Additive architecture** — Swarmbook lives under `book_sim/` without modifying legacy code
- **Evidence-first design** — Manuscripts are compressed into reusable structured artifacts
- **Deterministic simulation** — Same seed + evidence pack produces identical results
- **Atomic file writes** — Temp file + rename prevents corruption from crashes
- **Thread-safe cache** — Per-key locking for concurrent access safety
- **System-wide privacy** — PrivacyGuard singleton ensures `local_only` is never bypassed

---

## License

AGPL-3.0 — same as the original MiroFish project. See [LICENSE](./LICENSE).

## Credits

This is a modified fork of [MiroFish](https://github.com/666ghj/MiroFish) by [666ghj](https://github.com/666ghj), originally supported by [Shanda Group](https://www.shanda.com/). The simulation engine is powered by [OASIS](https://github.com/camel-ai/oasis) from the CAMEL-AI team.
