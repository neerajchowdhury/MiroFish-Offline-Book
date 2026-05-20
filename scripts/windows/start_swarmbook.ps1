# Start Swarmbook locally (Windows 11)
#
# Conservative script:
# - Starts backend (Flask) and frontend (Vite dev server) in background processes
# - Writes PID files under .swarmbook_pids/ so stop_swarmbook.ps1 can shut them down
# - Does not install dependencies. Run `npm ci` / pip installs yourself if needed.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\start_swarmbook.ps1
#
# Optional:
#   -BackendPort 5001 -FrontendPort 5173
#   -SkipFrontend (backend only)

[CmdletBinding()]
param(
  [int]$BackendPort = 5001,
  [int]$FrontendPort = 5173,
  [switch]$SkipFrontend
)

$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
  $here = Split-Path -Parent $PSCommandPath
  return (Resolve-Path (Join-Path $here '..\..')).Path
}

function Ensure-Dir([string]$Path) {
  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Write-Pid([string]$PidFile, [int]$ProcessId) {
  Set-Content -Path $PidFile -Value $ProcessId -Encoding ASCII
}

function Start-Background([string]$Name, [string]$WorkDir, [string]$Exe, [string[]]$ArgList, [string]$PidFile) {
  Write-Host "Starting $Name..."
  Write-Host "  cwd: $WorkDir"
  Write-Host "  cmd: $Exe $($ArgList -join ' ')"
  $proc = Start-Process -FilePath $Exe -ArgumentList $ArgList -WorkingDirectory $WorkDir -PassThru -WindowStyle Hidden
  Write-Pid -PidFile $PidFile -ProcessId $proc.Id
  Write-Host "  pid: $($proc.Id)"
}

$repoRoot = Resolve-RepoRoot
$pidDir = Join-Path $repoRoot '.swarmbook_pids'
Ensure-Dir $pidDir

$backendDir = Join-Path $repoRoot 'backend'
$frontendDir = Join-Path $repoRoot 'frontend'

# Prefer backend virtualenv python when available, fallback to PATH python.
$backendPython = Join-Path $backendDir '.venv\Scripts\python.exe'
if (-not (Test-Path $backendPython)) {
  $backendPython = 'python'
}

# On Windows, npm should be invoked via npm.cmd for Start-Process compatibility.
$npmExe = 'npm.cmd'

# Backend: flask app factory is in backend/app
$backendPid = Join-Path $pidDir 'backend.pid'
Start-Background `
  -Name 'backend' `
  -WorkDir $backendDir `
  -Exe $backendPython `
  -ArgList @('-m', 'flask', '--app', 'app', 'run', '--port', "$BackendPort") `
  -PidFile $backendPid

if (-not $SkipFrontend) {
  # Frontend: assumes dependencies are installed (npm ci).
  $frontendPid = Join-Path $pidDir 'frontend.pid'
  Start-Background `
    -Name 'frontend' `
    -WorkDir $frontendDir `
    -Exe $npmExe `
    -ArgList @('run', 'dev', '--', '--port', "$FrontendPort") `
    -PidFile $frontendPid
}

Write-Host ""
Write-Host "Swarmbook started."
Write-Host "Backend:  http://localhost:$BackendPort"
if (-not $SkipFrontend) { Write-Host "Frontend: http://localhost:$FrontendPort" }
Write-Host ""
Write-Host "Next: .\\scripts\\windows\\smoke_test_swarmbook.ps1 -BackendPort $BackendPort"
