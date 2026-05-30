# Swarmbook Studio - Windows Installation Guide

This document explains how to perform a clean installation of Swarmbook Studio/MiroFish-Offline on a Windows 11 machine.

---

## 1. System Requirements & Prerequisites
- **RAM**: 16 GB minimum (32 GB recommended).
- **GPU**: NVIDIA GPU with at least 6 GB of VRAM is highly recommended for running local models (Ollama).
- **Disk Space**: 20 GB minimum (models require ~10 GB to 30 GB).

---

## 2. Setup via Automated Installer (Recommended)
1. Double-click the **`install-swarmbook.bat`** file at the root.
2. The installer will:
   - Check if Git, Python 3.11, NodeJS, and Ollama are installed (installs them via `winget` if missing).
   - Create a Python Virtual Environment (`backend/.venv`) and install dependencies.
   - Install frontend Node packages (`npm ci`) and compile static files.
   - Configure local `.env` variables and prompt to configure keys.
   - Check Ollama status and pull `qwen2.5:7b-instruct` and `nomic-embed-text` models.
   - Generate "Start Swarmbook" and "Stop Swarmbook" Desktop shortcuts.

---

## 3. Alternative Setup: Manual Installation
If you prefer a manual developer setup:
1. **Install runtimes**:
   ```powershell
   winget install Git.Git
   winget install Python.Python.3.11
   winget install OpenJS.NodeJS.LTS
   winget install Ollama.Ollama
   ```
2. **Setup Backend**:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. **Setup Frontend**:
   ```powershell
   cd ../frontend
   npm ci
   npm run build
   ```
4. **Copy config**:
   ```powershell
   copy .env.swarmbook.example .env
   copy .env.swarmbook.example backend\.env
   ```
5. **Download models**:
   ```powershell
   ollama pull qwen2.5:7b-instruct
   ollama pull nomic-embed-text
   ```

---

## 4. Running the Application
- **Launch**: Double-click **`start-swarmbook.bat`** or desktop shortcut.
- **Stop**: Double-click **`stop-swarmbook.bat`** or desktop shortcut.
- **Check Status**: Double-click **`check-system.bat`** to run check-prereqs verification.
