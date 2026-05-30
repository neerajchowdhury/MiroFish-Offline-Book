@echo off
echo ==============================================================================
echo Swarmbook Studio - Local Cache Reset
echo ==============================================================================
echo This utility clears cached simulations and evidence pack artifacts.
echo Legacy MiroFish data and Neo4j database content will not be modified.
echo.
set /p confirm="Are you sure you want to clear the local upload cache? (Y/N): "
if /i "%confirm%"=="Y" (
    echo Resetting cache directories...
    rmdir /s /q "%~dp0backend\uploads\book_sim_cache" 2>nul
    mkdir "%~dp0backend\uploads\book_sim_cache" 2>nul
    echo Cache directories have been reset.
) else (
    echo Operation cancelled.
)
pause
