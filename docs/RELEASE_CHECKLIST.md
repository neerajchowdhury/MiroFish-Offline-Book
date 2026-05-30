# Swarmbook Studio - Release Checklist

This document details the checklist to follow before building a production-ready release of Swarmbook Studio.

---

## 1. Pre-Release Checklist
- [ ] Verify all 76 unit tests pass:
  ```powershell
  python -m unittest discover -s backend/tests -p "test_book_sim_*.py"
  ```
- [ ] Audit `.env` variables to ensure no production keys or credentials are hardcoded.
- [ ] Confirm `local_only` mode strictly routes models to offline Ollama endpoints.

---

## 2. Execution Run
- [ ] Execute clean build:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
  ```
- [ ] Create portable package ZIP:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\package-portable.ps1
  ```
- [ ] Verify packaged files:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\verify-release.ps1
  ```
