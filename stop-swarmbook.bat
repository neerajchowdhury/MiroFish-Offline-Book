@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows\stop_swarmbook.ps1 %*
pause
