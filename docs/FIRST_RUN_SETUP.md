# Swarmbook Studio - First-Run Setup Guide

This guide details the bootstrap processes that run upon the application's first launch on a target Windows machine.

---

## 1. Automated Setup Checkpoints
When you launch `install-swarmbook.bat` on a new laptop, the setup script executes these steps:

1. **System Path Validation**:
   - Reloads machine/user environment variables to confirm tool registrations.
2. **Dependency checks**:
   - Asserts Python (>= 3.11) and Node (>= 18.0.0) are present on system path. Offers silent setup via winget if missing.
3. **Python Virtual Environment Provisioning**:
   - Since Python virtual environments cannot be copied across machines due to absolute path bindings, the installer automatically detects the new machine's python executable, provisions a fresh local virtual environment (`backend/.venv`), and downloads pip dependencies.
4. **Static Assets Compiling**:
   - Compiles local frontend components via Vite.
5. **Config skeleton creation**:
   - Copies template config files to root and backend `.env`. Prompts user for local database password configuration.
6. **Ollama Model Preloading**:
   - Checks if Ollama API is active and pulls `qwen2.5:7b-instruct` and `nomic-embed-text` models automatically.
