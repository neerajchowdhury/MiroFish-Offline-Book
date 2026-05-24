# ============================================================================
# MiroFish-Offline — Master Installer (Windows PowerShell)
# ============================================================================
# Frictionless one-command setup for Windows 10/11.
#
# What it does:
#   1. Checks prerequisites (Python, Node.js, Git, Docker optional)
#   2. Clones or validates the repository
#   3. Creates Python virtual environment and installs all dependencies
#   4. Installs Node.js frontend dependencies
#   5. Sets up .env from .env.example
#   6. Offers Docker-based (Neo4j + Ollama) or manual service setup
#   7. Pulls required Ollama models
#   8. Runs a smoke test to verify everything works
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\install\install.ps1
#
# Options:
#   -RepoPath "D:\MiroFish"          # Where to install (default: current dir)
#   -SkipDocker                       # Skip Docker setup (use existing services)
#   -SkipSmokeTest                    # Skip post-install smoke test
#   -Model "qwen2.5:14b"             # Override default LLM model
#   -Quiet                            # Non-interactive, accept all defaults
# ============================================================================

[CmdletBinding()]
param(
    [string]$RepoPath = "",
    [switch]$SkipDocker,
    [switch]$SkipSmokeTest,
    [string]$Model = "qwen2.5:32b",
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ============================================================================
# Color helpers
# ============================================================================
function Write-Ok    { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn  { param($m) Write-Host "  [!!] $m" -ForegroundColor Yellow }
function Write-Err   { param($m) Write-Host "  [ERR] $m" -ForegroundColor Red }
function Write-Step  { param($m) Write-Host "`n>>> $m" -ForegroundColor Cyan }
function Write-Info  { param($m) Write-Host "  -> $m" -ForegroundColor Gray }

# ============================================================================
# Resolve install target
# ============================================================================
if (-not $RepoPath) {
    $RepoPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}
$RepoPath = $RepoPath.TrimEnd('\')

Write-Step "MiroFish-Offline Installer"
Write-Info "Target: $RepoPath"

# ============================================================================
# 1. Prerequisite checks
# ============================================================================
Write-Step "1/8 Checking prerequisites"

function Test-Exe([string]$Name) {
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-TcpPort([string]$Host, [int]$Port) {
    try { (Test-NetConnection -ComputerName $Host -Port $Port -WarningAction SilentlyContinue).TcpTestSucceeded } catch { $false }
}

$reqs = @{
    python  = @{ min = "3.11"; check = { python --version 2>$null } }
    node    = @{ min = "18";   check = { node --version 2>$null } }
    npm     = @{ min = $null;  check = { npm --version 2>$null } }
    git     = @{ min = $null;  check = { git --version 2>$null } }
}

$allOk = $true
foreach ($tool in $reqs.Keys) {
    if (Test-Exe $tool) {
        $ver = & $reqs[$tool].check 2>$null | Select-Object -First 1
        Write-Ok "$tool : $ver"
    } else {
        Write-Err "$tool : NOT FOUND"
        $allOk = $false
    }
}

if (-not $allOk) {
    Write-Err "Missing prerequisites. Install them first:"
    Write-Info "  Python 3.11+ : https://www.python.org/downloads/"
    Write-Info "  Node.js 18+  : https://nodejs.org/"
    Write-Info "  Git          : https://git-scm.com/"
    if (-not $Quiet) { Read-Host "Press Enter to exit" }
    exit 1
}

# Python version check
$pyVer = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
$pyMajor, $pyMinor = $pyVer -split '\.'
if ([int]$pyMajor -lt 3 -or ([int]$pyMajor -eq 3 -and [int]$pyMinor -lt 11)) {
    Write-Err "Python $pyVer is too old. Need 3.11+."
    exit 1
} else {
    Write-Ok "Python $pyVer meets minimum 3.11"
}

# Docker check (optional)
$dockerAvailable = Test-Exe 'docker'
if ($dockerAvailable) {
    try {
        docker info >$null 2>&1
        Write-Ok "Docker : running"
    } catch {
        Write-Warn "Docker : installed but not running (start Docker Desktop)"
        $dockerAvailable = $false
    }
} else {
    Write-Warn "Docker : not installed (optional — needed for Neo4j/Ollama containers)"
}

# ============================================================================
# 2. Validate or clone repository
# ============================================================================
Write-Step "2/8 Validating repository"

if (Test-Path (Join-Path $RepoPath 'backend\run.py')) {
    Write-Ok "Repository already present at $RepoPath"
} else {
    Write-Info "Repository not found at $RepoPath"
    if ($Quiet -or (Read-Host "Clone from GitHub? (y/n)") -eq 'y') {
        $parent = Split-Path $RepoPath -Parent
        $name = Split-Path $RepoPath -Leaf
        Push-Location $parent
        git clone https://github.com/nikmcfly/MiroFish-Offline-Book.git $name
        Pop-Location
        Write-Ok "Repository cloned"
    } else {
        Write-Err "Cannot proceed without repository."
        exit 1
    }
}

# ============================================================================
# 3. Python virtual environment + dependencies
# ============================================================================
Write-Step "3/8 Setting up Python environment"

$backendDir = Join-Path $RepoPath 'backend'
$venvPython = Join-Path $backendDir '.venv\Scripts\python.exe'
$venvPip    = Join-Path $backendDir '.venv\Scripts\pip.exe'

if (Test-Path $venvPython) {
    Write-Ok "Virtual environment exists"
} else {
    Write-Info "Creating virtual environment..."
    Push-Location $backendDir
    python -m venv .venv
    Pop-Location
    Write-Ok "Virtual environment created"
}

Write-Info "Installing Python dependencies (this may take a few minutes)..."
Push-Location $backendDir
& $venvPython -m pip install --upgrade pip >$null 2>&1
& $venvPip install -r requirements.txt 2>&1 | ForEach-Object { Write-Info $_ }
Pop-Location
Write-Ok "Python dependencies installed"

# ============================================================================
# 4. Node.js frontend dependencies
# ============================================================================
Write-Step "4/8 Setting up frontend"

$frontendDir = Join-Path $RepoPath 'frontend'
if (Test-Path (Join-Path $frontendDir 'node_modules')) {
    Write-Ok "Frontend dependencies exist"
} else {
    Write-Info "Installing frontend dependencies..."
    Push-Location $frontendDir
    npm ci 2>&1 | Select-Object -Last 3 | ForEach-Object { Write-Info $_ }
    Pop-Location
    Write-Ok "Frontend dependencies installed"
}

# Root-level dev dependencies (concurrently)
if (-not (Test-Path (Join-Path $RepoPath 'node_modules\concurrently'))) {
    Write-Info "Installing root dev dependencies..."
    Push-Location $RepoPath
    npm ci 2>&1 | Select-Object -Last 2 | ForEach-Object { Write-Info $_ }
    Pop-Location
    Write-Ok "Root dependencies installed"
}

# ============================================================================
# 5. Environment configuration
# ============================================================================
Write-Step "5/8 Configuring environment"

$envFile = Join-Path $RepoPath '.env'
$envExample = Join-Path $RepoPath '.env.example'

if (Test-Path $envFile) {
    Write-Ok ".env already exists"
} elseif (Test-Path $envExample) {
    Copy-Item $envExample $envFile
    # Generate a random SECRET_KEY
    $secretKey = python -c "import secrets; print(secrets.token_hex(32))" 2>$null
    if ($secretKey) {
        $content = Get-Content $envFile -Raw
        $content = $content -replace 'SECRET_KEY=', "SECRET_KEY=$secretKey"
        Set-Content $envFile $content -NoNewline
    }
    Write-Ok ".env created from template with random SECRET_KEY"
} else {
    Write-Warn ".env.example not found — create .env manually"
}

# ============================================================================
# 6. Docker services (Neo4j + Ollama)
# ============================================================================
Write-Step "6/8 Setting up services"

if ($SkipDocker -or -not $dockerAvailable) {
    Write-Warn "Skipping Docker setup"
    Write-Info "Ensure Neo4j and Ollama are running manually:"
    Write-Info "  docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/mirofish neo4j:5.18-community"
    Write-Info "  ollama serve"
} else {
    Write-Info "Starting Docker Compose services..."
    Push-Location $RepoPath

    # Check if containers already running
    $running = docker compose ps --format json 2>$null | ConvertFrom-Json 2>$null
    if ($running -and $running.Count -gt 0) {
        Write-Ok "Docker services already running"
    } else {
        # Detect GPU availability
        $hasGpu = $false
        try {
            $nvidiaSmi = nvidia-smi 2>$null
            if ($nvidiaSmi) { $hasGpu = $true }
        } catch {}

        $profile = if ($hasGpu) { "gpu" } else { "cpu" }
        Write-Info "Using profile: $profile (GPU: $hasGpu)"

        docker compose --profile $profile up -d 2>&1 | ForEach-Object { Write-Info $_ }

        # Wait for Neo4j to be healthy
        Write-Info "Waiting for Neo4j to be healthy..."
        $retries = 0
        while ($retries -lt 30) {
            $healthy = docker inspect --format='{{.State.Health.Status}}' mirofish-neo4j 2>$null
            if ($healthy -eq 'healthy') { break }
            Start-Sleep -Seconds 5
            $retries++
        }
        if ($healthy -eq 'healthy') {
            Write-Ok "Neo4j is healthy"
        } else {
            Write-Warn "Neo4j may not be fully ready yet (timeout after $($retries * 5)s)"
        }
    }
    Pop-Location
}

# ============================================================================
# 7. Pull Ollama models
# ============================================================================
Write-Step "7/8 Pulling Ollama models"

$modelsNeeded = @($Model, "nomic-embed-text")
$ollamaPort = Test-TcpPort -HostName 'localhost' -Port 11434

if ($ollamaPort) {
    foreach ($modelName in $modelsNeeded) {
        # Check if model already pulled
        $existing = ollama list 2>$null
        if ($existing -match $modelName) {
            Write-Ok "Model already present: $modelName"
        } else {
            Write-Info "Pulling $modelName (this may take a while)..."
            ollama pull $modelName 2>&1 | ForEach-Object { Write-Info $_ }
            Write-Ok "Model pulled: $modelName"
        }
    }
} else {
    Write-Warn "Ollama not listening on port 11434"
    Write-Info "If using Docker: docker exec mirofish-ollama ollama pull $Model"
    Write-Info "If using Docker: docker exec mirofish-ollama ollama pull nomic-embed-text"
}

# ============================================================================
# 8. Smoke test
# ============================================================================
if (-not $SkipSmokeTest) {
    Write-Step "8/8 Running smoke test"

    # Start backend temporarily for smoke test
    Write-Info "Starting backend for smoke test..."
    Push-Location $backendDir
    $backendProc = Start-Process -FilePath $venvPython -ArgumentList @('-m', 'flask', '--app', 'app', 'run', '--port', '5001') -PassThru -WindowStyle Hidden -RedirectStandardError (Join-Path $backendDir 'install_smoke.log')
    Pop-Location

    # Wait for backend to start
    Write-Info "Waiting for backend..."
    $retries = 0
    while ($retries -lt 20) {
        try {
            $resp = Invoke-WebRequest -Uri 'http://localhost:5001/health' -TimeoutSec 2 -ErrorAction Stop
            if ($resp.StatusCode -eq 200) { break }
        } catch {}
        Start-Sleep -Seconds 2
        $retries++
    }

    if ($retries -lt 20) {
        Write-Ok "Backend is running"

        # Run the smoke test script
        $smokeScript = Join-Path $RepoPath 'scripts\windows\smoke_test_swarmbook.ps1'
        if (Test-Path $smokeScript) {
            try {
                & $smokeScript -BackendBaseUrl 'http://localhost:5001' 2>&1 | ForEach-Object { Write-Info $_ }
                Write-Ok "Smoke test passed"
            } catch {
                Write-Warn "Smoke test encountered issues (check logs)"
            }
        }
    } else {
        Write-Warn "Backend did not start in time"
    }

    # Stop backend
    Write-Info "Stopping backend..."
    Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
} else {
    Write-Step "8/8 Smoke test skipped"
}

# ============================================================================
# Done
# ============================================================================
Write-Step "Installation Complete"
Write-Host ""
Write-Host "  Start:    .\scripts\windows\start_swarmbook.ps1" -ForegroundColor Green
Write-Host "  Stop:     .\scripts\windows\stop_swarmbook.ps1" -ForegroundColor Green
Write-Host "  Health:   .\scripts\windows\check_prereqs.ps1 -CheckDocker" -ForegroundColor Green
Write-Host "  Docker:   docker compose --profile gpu up -d  (or --profile cpu)" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:5001" -ForegroundColor Cyan
Write-Host "  Neo4j:    http://localhost:7474" -ForegroundColor Cyan
Write-Host ""

if (-not $Quiet) { Read-Host "Press Enter to exit" }
