@echo off
cd /d "%~dp0"
echo ==============================================================================
echo Swarmbook Studio - First Run Installation Setup
echo ==============================================================================
echo This installer will verify system prerequisites, set up python/nodejs environments,
echo download Ollama models, and configure Desktop launch shortcuts.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows\install_swarmbook.ps1 %*
pause
