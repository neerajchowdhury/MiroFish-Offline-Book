# Swarmbook Studio / MiroFish-Offline Start Guide

Welcome to Swarmbook Studio, a fully local, private-first manuscript stress-testing and simulation environment.

---

## Quick Start on Windows

### Step 1: Run the Setup Installer
To install prerequisites, build virtual environments, download Ollama models, and configure Desktop launch shortcuts:
1. Double-click the **`install-swarmbook.bat`** file at the project root.
2. Follow the interactive installer instructions.

### Step 2: Start Services
To launch the background backend and frontend Vite servers:
1. Double-click the **`start-swarmbook.bat`** script.
2. The installer will open your default browser to [http://localhost:5173/swarmbook](http://localhost:5173/swarmbook).

### Step 3: Run System Check
To verify status and connection to Ollama and Neo4j:
- Double-click **`check-system.bat`**.

### Step 4: Stop Services
To terminate all background processes safely:
- Double-click **`stop-swarmbook.bat`**.

---

## Utility Tools
- **`open-logs.bat`**: Opens the backend log directory in Windows Explorer.
- **`reset-local-cache.bat`**: Clears local cached simulation runs.

---

## Detailed Documentation
- [Windows Installation Guide](file:///d:/SW/MiroFish-Offline-Book/docs/INSTALL_WINDOWS.md)
- [Troubleshooting & Ports Guide](file:///d:/SW/MiroFish-Offline-Book/docs/TROUBLESHOOTING.md)
- [Uninstall & Deletion Guide](file:///d:/SW/MiroFish-Offline-Book/docs/UNINSTALL.md)
