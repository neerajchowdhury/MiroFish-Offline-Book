# build-release.ps1
# Prepares the application for release by compiling assets and running verification tests.

$ErrorActionPreference = 'Stop'

# Determine repo root
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..')).Path

Write-Host "=============================================================================="
Write-Host "Swarmbook Release Builder"
Write-Host "=============================================================================="
Write-Host "Repo root: $repoRoot"

# 1. Clean previous release artifacts
$cleanScript = Join-Path $scriptDir "clean-release.ps1"
if (Test-Path $cleanScript) {
    powershell -NoProfile -ExecutionPolicy Bypass -File $cleanScript
}

# 2. Compile frontend assets
Write-Host "`n[1/3] Compiling frontend static production assets..." -ForegroundColor Cyan
$frontendDir = Join-Path $repoRoot "frontend"
Set-Location $frontendDir
$npmCmd = "npm.cmd"
if (-not (Get-Command $npmCmd -ErrorAction SilentlyContinue)) {
    $npmCmd = "npm"
}
$proc = Start-Process -FilePath $npmCmd -ArgumentList @("run", "build") -NoNewWindow -PassThru -Wait
if ($proc.ExitCode -ne 0) {
    throw "Frontend Vite compilation failed."
}
Write-Host "Frontend compiled successfully." -ForegroundColor Green

# 3. Run unit tests
Write-Host "`n[2/3] Running backend verification tests..." -ForegroundColor Cyan
Set-Location $repoRoot
$pythonExe = Join-Path $repoRoot "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}
$procTests = Start-Process -FilePath $pythonExe -ArgumentList @("-m", "unittest", "discover", "-s", "backend/tests", "-p", "test_book_sim_*.py") -NoNewWindow -PassThru -Wait
if ($procTests.ExitCode -ne 0) {
    throw "Backend unit tests failed."
}
Write-Host "All backend unit tests passed successfully." -ForegroundColor Green

Write-Host "`n[3/3] Build completed successfully." -ForegroundColor Green
