# Swarmbook Studio - Uninstall & Clean Deletion Guide

This guide documents how to safely and completely uninstall Swarmbook Studio from a Windows machine.

---

## 1. Terminate Background Services
Before deleting any files, ensure no services are running:
- Double-click **`stop-swarmbook.bat`** or run:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\windows\stop_swarmbook.ps1
  ```

---

## 2. Remove Shortcut Launchers
Delete shortcut files from your Desktop and Start Menu:
- `Start Swarmbook.lnk`
- `Stop Swarmbook.lnk`

---

## 3. Clean Cache & User Data
If you wish to remove all uploaded manuscripts, cached evidence packs, and generated HTML/JSON reports:
- Run **`reset-local-cache.bat`** to clear directories.
- Delete the project folders under `backend/uploads/`.

---

## 4. Delete Application Files
Simply delete the extracted portable directory.
If you deployed databases or services inside Docker:
- Stop and clean Docker volumes:
  ```powershell
  docker compose down -v
  ```
