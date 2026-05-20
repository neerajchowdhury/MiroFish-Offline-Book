# Swarmbook Install (Windows 11)

This guide prepares the repo for personal local installation on another Windows 11 laptop. It does not change app behavior; it documents conservative setup paths and uses local-first defaults.

## Prerequisites
- Windows 11
- Git
- Python 3.11+ (recommended) available as `python`
- Node.js 18+ (recommended) available as `node`
- npm available as `npm`

Optional but recommended for a smooth local-first experience:
- Ollama (local LLM runtime)
- Neo4j Desktop or Neo4j server (local graph persistence)
- Docker Desktop (if you want containerized services)

## Quick Checks
From repo root:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\check_prereqs.ps1
```

## Option A: Docker Desktop (Services in Containers)
Use Docker when you prefer not to install Neo4j manually.

1. Install Docker Desktop and ensure it is running.
2. From repo root, start docker services:
```powershell
docker compose up -d
```
3. Confirm Neo4j is listening on `bolt://localhost:7687`.

Notes:
- Ollama is typically installed natively on Windows. You can still use Docker for Neo4j only.
- Do not expose Neo4j to the public internet; keep it bound to localhost for personal use.

## Option B: Manual Dev (Recommended for Iteration)

### 1) Backend setup
```powershell
cd .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install python deps (choose one based on repo conventions)
pip install -r requirements.txt

# Optional (if present)
# pip install -r requirements-dev.txt
```

### 2) Frontend setup
```powershell
cd ..\frontend
npm ci
```

### 3) Environment variables
Use placeholders only in committed files:
- `.env.swarmbook.example` is provided as a template.

Recommended approach:
1. Copy `.env.swarmbook.example` to a local, uncommitted file and set values.
2. Or set env vars in your PowerShell session before running.

Never commit real API keys.

## Ollama Setup (Local-First)
1. Install Ollama for Windows.
2. Start Ollama (it typically runs as a background service).
3. Verify:
```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Suggested models for low-resource local runs:
- `llama3.1:8b-instruct`
- `qwen2.5:7b-instruct`

If you use embeddings (some legacy paths): `nomic-embed-text`.

## Neo4j Setup (Local)
Swarmbook uses Neo4j additively; the app should still run if Neo4j is down, but you lose persistence/graph features.

Default local config (see `.env.swarmbook.example`):
- `NEO4J_URI=bolt://localhost:7687`
- `NEO4J_USER=neo4j`
- `NEO4J_PASSWORD=mirofish`

Validation:
```powershell
Test-NetConnection localhost -Port 7687
```

## Optional Gemini/NVIDIA API Keys
These are optional. `local_only` mode must never use them.

Placeholders (do not commit real secrets):
```env
GEMINI_API_KEY=your_gemini_key_here
NVIDIA_API_KEY=your_nvidia_key_here
NVIDIA_BASE_URL=your_nvidia_base_url_here
```

If keys are missing, Swarmbook should degrade gracefully and continue with local routes where allowed.

## Recommended Low-Resource Profile
For Windows 11, 16 GB RAM, 6 GB NVIDIA VRAM:
- Default: `hybrid_safe_default`
- Safest fully local: `local_tiny` (`privacy_mode=local_only`)

Profile definitions live in:
- `configs/book_sim/local_profiles.yaml`

## Start / Stop (Scripts)
From repo root:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_swarmbook.ps1
```

Notes:
- The start script prefers `backend\.venv\Scripts\python.exe` when present.
- Frontend start uses `npm.cmd` (Windows-safe process launch).

Stop:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\stop_swarmbook.ps1
```

## Smoke Test (Scripts)
After starting the backend:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\smoke_test_swarmbook.ps1 -BackendBaseUrl http://localhost:5001
```

## Troubleshooting

### Backend won’t start
- Ensure venv is activated (if using manual dev).
- Run:
```powershell
python -m compileall backend
```

### Frontend won’t start
- Ensure Node/npm are installed and `npm ci` completed in `frontend/`.
- If port 5173 is in use, run:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_swarmbook.ps1 -FrontendPort 5174
```

### Ollama errors / not listening
- Confirm `OLLAMA_BASE_URL=http://localhost:11434`.
- Confirm:
```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

### Neo4j errors
- If Neo4j is down, the backend should still start; health endpoints will report Neo4j not initialized/unavailable.
- Start Neo4j and retry.

### Missing API keys
- Safe to ignore for `local_only` and `local_tiny`.
- Health endpoint shows provider availability:
```powershell
Invoke-RestMethod http://localhost:5001/api/book-sim/health
```

### Large manuscript paste fails
- The evidence endpoint guards very large text by default.
- Start with an excerpt (1-3 chapters), or pass `max_manuscript_chars` in the `/api/book-sim/evidence-packs` request.
