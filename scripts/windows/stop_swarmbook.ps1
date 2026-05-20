# Stop Swarmbook local processes (Windows 11)
#
# Conservative script:
# - Reads PIDs written by start_swarmbook.ps1 under .swarmbook_pids/
# - Attempts graceful stop; falls back to Stop-Process
# - Does not delete any project data or cached artifacts
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\stop_swarmbook.ps1

[CmdletBinding()]
param()

$ErrorActionPreference = 'SilentlyContinue'

function Resolve-RepoRoot {
  $here = Split-Path -Parent $PSCommandPath
  return (Resolve-Path (Join-Path $here '..\..')).Path
}

function Stop-ByPidFile([string]$PidFile, [string]$Name) {
  if (-not (Test-Path $PidFile)) {
    Write-Host "No $Name pid file found: $PidFile"
    return
  }

  $pidRaw = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
  if (-not $pidRaw) {
    Write-Host "$Name pid file is empty: $PidFile"
    return
  }

  $targetPid = 0
  if (-not [int]::TryParse($pidRaw, [ref]$targetPid)) {
    Write-Host "$Name pid file is invalid: $PidFile"
    return
  }

  $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
  if (-not $proc) {
    Write-Host "$Name is not running (pid $targetPid)."
    return
  }

  Write-Host "Stopping $Name (pid $targetPid)..."
  try {
    Stop-Process -Id $targetPid -ErrorAction Stop
    Write-Host "Stopped $Name."
  } catch {
    Write-Host "Failed to stop ${Name}: $($_.Exception.Message)"
  }
}

$repoRoot = Resolve-RepoRoot
$pidDir = Join-Path $repoRoot '.swarmbook_pids'

Stop-ByPidFile -PidFile (Join-Path $pidDir 'frontend.pid') -Name 'frontend'
Stop-ByPidFile -PidFile (Join-Path $pidDir 'backend.pid') -Name 'backend'

Write-Host ""
Write-Host "If ports are still busy, check: Get-NetTCPConnection -LocalPort 5001,5173 | Format-Table"
