@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows\start_swarmbook.ps1 %*
pause
