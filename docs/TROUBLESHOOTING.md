# Swarmbook Studio - Troubleshooting & Logs Guide

This guide compiles steps to troubleshoot common issues when installing or running Swarmbook Studio.

---

## 1. Port Conflicts (5001 or 5173 in use)
If ports are already bound by other local services:
- Run the start script in a terminal with custom port arguments:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_swarmbook.ps1 -BackendPort 5002 -FrontendPort 5174
  ```

---

## 2. Ollama / Neo4j Connection Refused
- **Ollama**: Verify the Ollama icon is visible in your taskbar. Load `http://localhost:11434` in a browser; it should display "Ollama is running".
- **Neo4j**: If Neo4j credentials are invalid or database is offline, Swarmbook automatically switches to **dry-run fallback mode**. Cache, scoring, and UI review remain functional, but graph relationships database persistence is skipped. Verify connection in your terminal:
  ```powershell
  python -c "from neo4j import GraphDatabase; d=GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','mirofish')); d.verify_connectivity(); print('Connected')"
  ```

---

## 3. Reviewing Logs
- Run **`open-logs.bat`** to open the `backend/logs` directory.
- Flask backend logs trace API route hits and error exceptions.
- Neo4j database logs and Ollama generation stats can be checked via docker logs if containerized:
  ```powershell
  docker logs mirofish-neo4j
  docker logs mirofish-ollama
  ```
