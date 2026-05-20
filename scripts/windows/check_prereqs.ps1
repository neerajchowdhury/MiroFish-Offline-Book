# Swarmbook prerequisite checker (Windows 11)
#
# Conservative script:
# - Does not install anything
# - Does not modify system settings
# - Only checks for common prerequisites and prints next-step hints
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\check_prereqs.ps1

[CmdletBinding()]
param(
  [switch]$CheckDocker
)

$ErrorActionPreference = 'Stop'

function Write-Section([string]$Title) {
  Write-Host ''
  Write-Host ('=' * 78)
  Write-Host $Title
  Write-Host ('=' * 78)
}

function Test-Command([string]$Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  return $null -ne $cmd
}

function Test-TcpPort([string]$HostName, [int]$Port) {
  try {
    $result = Test-NetConnection -ComputerName $HostName -Port $Port -WarningAction SilentlyContinue
    return [bool]$result.TcpTestSucceeded
  } catch {
    return $false
  }
}

Write-Section "Swarmbook Prereqs Check"

Write-Host "Repo root: $PSScriptRoot\..\.."
Write-Host "PowerShell: $($PSVersionTable.PSVersion)"

Write-Section "Core Tools"

$pythonOk = Test-Command 'python'
Write-Host ("python: " + ($(if ($pythonOk) { "OK" } else { "MISSING" })))
if ($pythonOk) { python --version }

$nodeOk = Test-Command 'node'
Write-Host ("node: " + ($(if ($nodeOk) { "OK" } else { "MISSING" })))
if ($nodeOk) { node --version }

$npmOk = Test-Command 'npm'
Write-Host ("npm: " + ($(if ($npmOk) { "OK" } else { "MISSING" })))
if ($npmOk) { npm --version }

Write-Section "Local Services (Optional But Recommended)"

$ollamaOk = Test-Command 'ollama'
Write-Host ("ollama cli: " + ($(if ($ollamaOk) { "OK" } else { "MISSING" })))
if ($ollamaOk) {
  try { ollama --version } catch { Write-Host "ollama version check failed: $($_.Exception.Message)" }
}

$ollamaPort = Test-TcpPort -HostName 'localhost' -Port 11434
Write-Host ("Ollama HTTP (http://localhost:11434): " + ($(if ($ollamaPort) { "OK" } else { "NOT LISTENING" })))

$neo4jBolt = Test-TcpPort -HostName 'localhost' -Port 7687
Write-Host ("Neo4j Bolt (bolt://localhost:7687): " + ($(if ($neo4jBolt) { "OK" } else { "NOT LISTENING" })))

$backendPort = Test-TcpPort -HostName 'localhost' -Port 5001
Write-Host ("Backend (http://localhost:5001): " + ($(if ($backendPort) { "LISTENING" } else { "NOT LISTENING" })))

$frontendPort = Test-TcpPort -HostName 'localhost' -Port 5173
Write-Host ("Frontend dev (http://localhost:5173): " + ($(if ($frontendPort) { "LISTENING" } else { "NOT LISTENING" })))

Write-Section "Docker Desktop (Optional)"

if ($CheckDocker) {
  $dockerOk = Test-Command 'docker'
  Write-Host ("docker: " + ($(if ($dockerOk) { "OK" } else { "MISSING" })))
  if ($dockerOk) {
    try {
      docker version | Out-Host
    } catch {
      Write-Host "docker version failed: $($_.Exception.Message)"
      Write-Host "Hint: ensure Docker Desktop is installed and running."
    }
  } else {
    Write-Host "Hint: install Docker Desktop if you prefer the containerized option."
  }
} else {
  Write-Host "Skipped docker checks. Re-run with -CheckDocker to validate Docker Desktop."
}

Write-Section "Next Steps"
Write-Host "1) Read: docs/SWARMBOOK_INSTALL_WINDOWS.md"
Write-Host "2) Start: .\\scripts\\windows\\start_swarmbook.ps1"
Write-Host "3) Smoke test: .\\scripts\\windows\\smoke_test_swarmbook.ps1"

