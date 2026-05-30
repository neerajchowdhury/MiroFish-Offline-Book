# Swarmbook Studio / MiroFish Installation & Packaging Audit

This document audits the current codebase of Swarmbook Studio / MiroFish-Offline to establish a robust portable packaging and clean installation plan on Windows.

---

## 1. Current App Stack
- **Frontend**: Vue 3 + Vite. Main dev entry on port `5173`. Production compilation outputs minified assets to `frontend/dist/`.
- **Backend**: Flask API server (Python 3.11). Standard development entry via `run.py` on port `5001`. Supports both local python dependencies and system paths.
- **Runtimes required**: Node.js (>= 18.0.0) for frontend development/building, Python (>= 3.11) for backend API orchestration.

---

## 2. Current Launch Flow
- Invoking `scripts/windows/start_swarmbook.ps1` runs Flask backend (`python -m flask --app app run --port 5001`) and Vite frontend dev server (`npm run dev -- --port 5173`) in background processes via `Start-Process -WindowStyle Hidden`.
- Process IDs are stored in `.swarmbook_pids/backend.pid` and `.swarmbook_pids/frontend.pid`.
- Terminating services is handled by `scripts/windows/stop_swarmbook.ps1`, which reads these PID files and calls `Stop-Process`.

---

## 3. Current Build Flow
- Frontend is compiled via Vite: `cd frontend && npm run build` which writes assets to `frontend/dist`.
- Backend has no compilation step; it runs directly from the Python virtual environment (`backend/.venv`) via `uv run` or standard interpreter.

---

## 4. Current Runtime Dependencies
- **Backend**: Specified in `backend/requirements.txt` (Flask, Flask-CORS, PyYAML, python-dotenv, neo4j, openai, etc.).
- **Frontend**: Specified in `frontend/package.json` (Vue, Vue-Router, Axios, pdfmake, docx, html2canvas, file-saver).

---

## 5. Required External Services
- **Ollama** (Local LLM service listening on `localhost:11434`). Hosts models: `qwen2.5:7b-instruct` and `nomic-embed-text`.
- **Neo4j CE** (Local graph database listening on `bolt://localhost:7687` with username/password `neo4j/mirofish`).

---

## 6. Current Config/Env Handling
- Environment variables are loaded from `.env` in the root and `backend/.env`.
- Base template is `.env.swarmbook.example` or `.env.example`.
- Key configurations:
  - `LLM_BASE_URL` and `LLM_MODEL_NAME` for Ollama.
  - `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` for Neo4j.
  - `GEMINI_API_KEY` and `NVIDIA_API_KEY` for optional cloud models.
  - `SECRET_KEY` for Flask session security.

---

## 7. Current Data Persistence Locations
- Cached evidence packs, simulation runs, and reports: `backend/uploads/book_sim_cache/`, `backend/uploads/simulations/`, `backend/uploads/reports/`, and `backend/uploads/projects/`.
- Local project history tracking: Stored in the browser's `localStorage` (frontend).
- Graph persistence: neo4j volume/database instance.

---

## 8. Packaging Risks
- **Absolute Paths**: Startup and verification scripts must not reference hardcoded paths (e.g. `D:\SW\MiroFish-Offline-Book`) and must use relative paths based on `$PSScriptRoot`.
- **Environment Conflicts**: Python Virtual Environment (`.venv`) compiled on the developer's machine carries absolute virtualenv shebangs and is non-portable between laptops with different python install paths. The portable release should configure a local virtualenv or build script upon extraction.
- **Port Availability**: If port `5001` or `5173` is occupied, start scripts should fail gracefully with a descriptive error.
- **Exposure of Keys**: Ensure the builder script excludes `.env` or custom configuration keys from the packaged zip.

---

## 9. Recommended Installer & Packaging Strategy
1. **Portable Release Folder structure**:
   - `start-swarmbook.bat` & `start-swarmbook.ps1` (Main launchers)
   - `stop-swarmbook.bat` & `stop-swarmbook.ps1` (Graceful shutdown)
   - `check-system.bat` & `check-system.ps1` (Prerequisite validation)
   - `docs/` (Offline markdown guides)
   - `README_INSTALL.md` (Self-contained start instruction)
   - `backend/` and `frontend/` (Excluding dev-only files, cache files, and `.git`)
2. **Release Automation**:
   - Create a clean script `scripts/build-release.ps1` to clean, build, compile, gather files, generate release manifest, and create the portable `.zip` output.
3. **Setup Wizard / Script**:
   - Build a reliable automated `first-run` interactive script that detects/provisions runtimes (Python/Node) via `winget`, configures `.env`, pre-pulls Ollama models, sets up virtualenv, and compiles Vite frontend.
4. **Lightweight Desktop Installer**:
   - Use a clean PowerShell-based wrapper/installer that creates Desktop/Start menu shortcuts, validates environment, installs required files to a chosen target path, and provides uninstall shortcuts/guidelines.

---

## 10. Exact Files to Create or Modify
- [NEW] `README_INSTALL.md` (Root documentation)
- [NEW] `scripts/build-release.ps1` (Automate building and packaging)
- [NEW] `scripts/package-portable.ps1` (Pack clean files into target ZIP)
- [NEW] `scripts/verify-release.ps1` (Validate release artifact checksum/structure)
- [NEW] `scripts/clean-release.ps1` (Remove release leftovers)
- [NEW] `scripts/windows/check-system.bat` (Batch wrapper for checks)
- [NEW] `scripts/windows/start-swarmbook.bat` (Batch wrapper for start)
- [NEW] `scripts/windows/stop-swarmbook.bat` (Batch wrapper for stop)
- [NEW] `scripts/windows/open-logs.bat` (Batch utility to view logs)
- [NEW] `scripts/windows/reset-local-cache.bat` (Utility to safely clear cached simulations)
- [MODIFY] `scripts/windows/install_swarmbook.ps1` (Harden first-run setup logic)
