# Swarmbook Studio Clean Installation Guide (Windows 11)

This guide documents the procedures for performing a clean, local installation of Swarmbook Studio on a new Windows 11 laptop. It covers both the **Automated Installer Path** and the **Manual Developer Path**.

---

## 1. System Requirements & Prerequisites

### Minimum Hardware Profile
* **OS**: Windows 11 (64-bit)
* **RAM**: 16 GB or higher
* **GPU**: NVIDIA Graphics Card with at least 6 GB of VRAM (for local Ollama LLM execution)

### Target Local Services
* **Ollama**: Local LLM runner (hosting `qwen2.5:7b-instruct` and `nomic-embed-text`)
* **Neo4j**: Graph database persistence (running locally on port `7687` or via Docker Compose)

---

## 2. Clean Installation Steps

Follow these steps to download and set up the application from scratch.

### Step 1: Clone the Repository
Open a terminal (PowerShell or Command Prompt) and clone the codebase:
```powershell
git clone <repository-url> MiroFish-Offline-Book
cd MiroFish-Offline-Book
```

### Step 2: Run the Automated Installer (Recommended)
Swarmbook includes an optimized PowerShell script that automates prerequisite installations, environment configurations, virtual environments, node package building, and model downloads.

Run the installer from the root workspace directory:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\install_swarmbook.ps1
```

> [!NOTE]
> * **Administrative Privileges**: The installer will offer to relaunch itself as an Administrator if it detects missing prerequisites. Relaunching in admin mode allows `winget` to install core tools silently.
> * **Interactive Configurations**: During installation, the script will prompt you if you want to configure database credentials or enter Gemini/NVIDIA API keys.
> * **Ollama Model Preloading**: The script will check if the Ollama service is running. If active, it will automatically download both `qwen2.5:7b-instruct` and `nomic-embed-text` models.
> * **Desktop Shortcuts**: The installer will offer to create "Start Swarmbook" and "Stop Swarmbook" shortcuts on your Desktop for easy service management.

---

## 3. Alternative Path: Manual Installation

If you prefer to set up your environment manually or do not want to use the automated installer script, follow these commands:

### A. Install Core Tools
Install the required runtimes using `winget` or manual downloads:
```powershell
winget install --id Git.Git --silent --accept-source-agreements --accept-package-agreements
winget install --id Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements
winget install --id OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
winget install --id Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements
```
*Restart your terminal afterwards to update the environment variables.*

### B. Provision the Backend
1. Navigate to the backend directory and create a virtualenv:
   ```powershell
   cd .\backend
   python -m venv .venv
   ```
2. Activate the virtual environment and upgrade package utilities:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip setuptools wheel
   ```
3. Install the python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### C. Provision the Frontend
1. Navigate to the frontend directory:
   ```powershell
   cd ..\frontend
   ```
2. Install NodeJS packages and compile the production bundle:
   ```powershell
   npm ci
   npm run build
   ```

### D. Setup Environment Variables
1. From the project root, copy the environment template file:
   ```powershell
   Copy-Item .env.swarmbook.example .env
   Copy-Item .env.swarmbook.example backend\.env
   ```
2. Open the `.env` files in a text editor and update configuration keys:
   * Set `NEO4J_PASSWORD` to your local Neo4j instance password.
   * Add optional `GEMINI_API_KEY` or `NVIDIA_API_KEY` if you want cloud hybrid routes.

### E. Preload Ollama Models
Ensure Ollama is running, then pull the required models:
```powershell
ollama pull qwen2.5:7b-instruct
ollama pull nomic-embed-text
```

---

## 4. Running the Application

### Launching Services
To launch the application backend server (Flask) and frontend dev server (Vite):
* **Method A**: Double-click the **Start Swarmbook** shortcut on your Desktop.
* **Method B**: From the workspace root, run the start script:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_swarmbook.ps1
  ```
The servers run in background processes. Browse to:
* **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
* **Backend API Console**: [http://localhost:5001](http://localhost:5001)

### Stopping Services
To terminate the background services:
* **Method A**: Double-click the **Stop Swarmbook** shortcut on your Desktop.
* **Method B**: From the workspace root, run:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\windows\stop_swarmbook.ps1
  ```

### Verifying Installation Integrity (Smoke Check)
Run the automated verification suite to test service status:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\smoke_test_swarmbook.ps1
```

---

## 5. Troubleshooting Guide

### Port Conflicts (5001 or 5173 in use)
If the default ports are already bound, you can override ports at start:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_swarmbook.ps1 -BackendPort 5002 -FrontendPort 5174
```

### Ollama Connection Refused
* Ensure the Ollama tray icon is running in your taskbar.
* Verify model health by loading:
  ```powershell
  Invoke-RestMethod http://localhost:11434/api/tags
  ```

### Neo4j Graph Persistent Failures
If Neo4j is offline or credentials are bad, Swarmbook runs in a **dry-run recovery mode**. Project data and reports will survive in the local cache, but graph relationship queries will be disabled. 
* To start Neo4j in a local container, install Docker Desktop and run:
  ```powershell
  docker compose up -d
  ```

### Large Manuscript Upload Failures
The manuscript ingestion API has a safety guard capping uploads at 500,000 characters to prevent system overcommit on low-resource machines. If you upload a massive draft, you will see a safety warning. Consider segmenting the draft or increasing limits in `.env` settings.
