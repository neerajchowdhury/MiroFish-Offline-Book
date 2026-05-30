# Swarmbook Studio - Portable Release Guide

This document describes the portable ZIP release format, directory structure, and runtime portability details.

---

## 1. Portable Release Folder Structure

A portable release package is prepared under `D:\SW\MiroFish_Release v2` and compressed to `D:\SW\MiroFish_Swarmbook_Portable_v0.1.zip`. The ZIP contains:

```
SwarmbookStudio_Portable/
├── start-swarmbook.bat       # Runs the PowerShell start utility
├── stop-swarmbook.bat        # Terminates background services
├── check-system.bat          # Performs system check
├── install-swarmbook.bat     # Triggers virtualenv creation and npm compile
├── open-logs.bat             # Opens backend logs directory
├── reset-local-cache.bat     # Clears local simulation caches
│
├── configs/                  # Scopes scoring and platform styles
├── backend/                  # Flask backend code
│   └── logs/                 # Self-contained log folder
├── frontend/                 # Frontend Vue code and minified assets
├── docs/                     # Markdown guides
└── README_INSTALL.md         # Fast start instructions
```

---

## 2. Portability Guardrails
- **No Hardcoded Absolute Paths**: All batch launchers and scripts reference relative paths via `$PSScriptRoot` or `%~dp0`.
- **Isolated User Data**: Cached manuscripts, evidence pack review cards, and JSON reports are stored in `backend/uploads/book_sim_cache/` inside the extracted portable folder, ensuring no leakage to global directory paths.
- **Port Checking**: Prevents duplicate executions by validating if port `5001` or `5173` is occupied before spawning servers.
