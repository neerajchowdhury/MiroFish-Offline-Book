# Swarmbook automated local installation tool (Windows 11)
#
# Optimized and robust script:
# - Performs prerequisite checks
# - Safely offers to install missing core tools (Git, Python, Node, Ollama) via winget
# - Provisions the Python virtual environment (.venv) and installs pip dependencies
# - Provisions frontend Node dependencies using npm ci/install
# - Configures uncommitted environment template files (.env)
# - Validates local Ollama models and pulls target model if missing
# - Generates a Desktop shortcut for easy one-click launching
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\install_swarmbook.ps1
#
# Options:
#   -AutoInstallPrereqs  Automatically install missing prereqs via winget without prompt
#   -SkipFrontend        Skip setting up frontend node modules
#   -OllamaModel         Specifies target Ollama model to pull (default: qwen2.5:7b-instruct)
#   -CreateShortcut      Automatically create a Desktop launch shortcut without prompt

[CmdletBinding()]
param(
  [switch]$AutoInstallPrereqs,
  [switch]$SkipFrontend,
  [string]$OllamaModel = "qwen2.5:7b-instruct",
  [switch]$CreateShortcut
)

$ErrorActionPreference = 'Stop'

function Write-Section([string]$Title) {
  Write-Host ''
  Write-Host ('=' * 78) -ForegroundColor Cyan
  Write-Host $Title -ForegroundColor White
  Write-Host ('=' * 78) -ForegroundColor Cyan
}

function Test-Command([string]$Name) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  return $null -ne $cmd
}

function Reload-Path {
  # Dynamically reloads machine/user PATH variables in the current session
  $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
  $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
  $env:Path = "$machinePath;$userPath"
}

# Determine repo root path
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..\..')).Path

Write-Section "Swarmbook Windows Installation Tool"
Write-Host "Target workstation target profile: Windows 11, 16 GB RAM, 6 GB VRAM"
Write-Host "Repository location: $repoRoot"

# 1) Administrative rights advice
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  Write-Host "Notice: Execution is running as user. winget package installations may trigger Windows UAC prompts." -ForegroundColor Yellow
}

# 2) Prerequisites check and setup
Write-Section "1) Checking / Installing Core Prerequisites"
$wingetOk = Test-Command 'winget'

function Install-Prereq([string]$FriendlyName, [string]$CommandName, [string]$WingetId) {
  Write-Host "Checking for $FriendlyName ($CommandName)..." -NoNewline
  
  # Reload path to check if it was installed in a previous run/process
  Reload-Path
  if (Test-Command $CommandName) {
    Write-Host " Already Installed." -ForegroundColor Green
    return $true
  }
  Write-Host " Missing." -ForegroundColor Yellow

  if (-not $wingetOk) {
    Write-Host "  Error: winget package manager is unavailable. Please install $FriendlyName manually." -ForegroundColor Red
    return $false
  }

  $install = $false
  if ($AutoInstallPrereqs) {
    $install = $true
  } else {
    $choice = Read-Host "  Would you like to install $FriendlyName via winget? (Y/N)"
    if ($choice.Trim().ToUpper() -eq 'Y') {
      $install = $true
    }
  }

  if ($install) {
    Write-Host "  Installing $FriendlyName using winget ($WingetId)..."
    try {
      $proc = Start-Process -FilePath "winget" -ArgumentList @("install", "--id", $WingetId, "--silent", "--accept-source-agreements", "--accept-package-agreements") -NoNewWindow -PassThru -Wait
      if ($proc.ExitCode -eq 0) {
        Write-Host "  Successfully installed $FriendlyName. System path will reload." -ForegroundColor Green
        Reload-Path
        return $true
      } else {
        Write-Host "  winget returned error code: $($proc.ExitCode) during $FriendlyName setup." -ForegroundColor Red
        return $false
      }
    } catch {
      Write-Host "  Failed to invoke winget installer: $($_.Exception.Message)" -ForegroundColor Red
      return $false
    }
  }
  return $false
}

Install-Prereq -FriendlyName "Git CLI" -CommandName "git" -WingetId "Git.Git" | Out-Null
Install-Prereq -FriendlyName "Python 3.11" -CommandName "python" -WingetId "Python.Python.3.11" | Out-Null
Install-Prereq -FriendlyName "NodeJS LTS" -CommandName "node" -WingetId "OpenJS.NodeJS.LTS" | Out-Null
Install-Prereq -FriendlyName "Ollama Local Service" -CommandName "ollama" -WingetId "Ollama.Ollama" | Out-Null

# Reload PATH one final time after all installations
Reload-Path

# 3) Backend setup
Write-Section "2) Setting Up Python Virtual Environment"
if (-not (Test-Command 'python')) {
  Write-Host "Error: Python was not found on PATH. Skipping backend dependency installation." -ForegroundColor Red
} else {
  $backendDir = Join-Path $repoRoot "backend"
  Set-Location $backendDir

  if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
  } else {
    Write-Host "Virtual environment (.venv) already exists."
  }

  $pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"
  $pipExe = Join-Path $backendDir ".venv\Scripts\pip.exe"

  if (Test-Path $pythonExe) {
    Write-Host "Upgrading local pip..."
    Start-Process -FilePath $pythonExe -ArgumentList @("-m", "pip", "install", "--upgrade", "pip") -NoNewWindow -Wait
    
    Write-Host "Installing dependencies from requirements.txt..."
    $proc = Start-Process -FilePath $pipExe -ArgumentList @("install", "-r", "requirements.txt") -NoNewWindow -PassThru -Wait
    if ($proc.ExitCode -eq 0) {
      Write-Host "Backend dependencies installed successfully." -ForegroundColor Green
    } else {
      Write-Host "Pip returned exit code: $($proc.ExitCode) during package installation." -ForegroundColor Red
    }
  } else {
    Write-Host "Error: Virtual environment python executable not found at $pythonExe" -ForegroundColor Red
  }
}

# 4) Frontend setup
Write-Section "3) Setting Up Frontend Node Modules"
if ($SkipFrontend) {
  Write-Host "Skipping frontend setup as requested." -ForegroundColor Yellow
} elseif (-not (Test-Command 'node')) {
  Write-Host "Error: Node.js was not found on PATH. Skipping frontend setup." -ForegroundColor Red
} else {
  $frontendDir = Join-Path $repoRoot "frontend"
  Set-Location $frontendDir
  
  $npmCmd = "npm.cmd"
  if (-not (Test-Command $npmCmd)) {
    $npmCmd = "npm"
  }

  Write-Host "Installing frontend packages..."
  try {
    if (Test-Path "package-lock.json") {
      $proc = Start-Process -FilePath $npmCmd -ArgumentList @("ci") -NoNewWindow -PassThru -Wait
    } else {
      $proc = Start-Process -FilePath $npmCmd -ArgumentList @("install") -NoNewWindow -PassThru -Wait
    }
    if ($proc.ExitCode -eq 0) {
      Write-Host "Frontend dependencies setup completed." -ForegroundColor Green
    } else {
      Write-Host "npm installation failed with exit code: $($proc.ExitCode)" -ForegroundColor Red
    }
  } catch {
    Write-Host "Error running npm setup: $($_.Exception.Message)" -ForegroundColor Red
  }
}

# 5) Environment configurations
Write-Section "4) Configuring Local Environment Variables"
$envExample = Join-Path $repoRoot ".env.swarmbook.example"
if (-not (Test-Path $envExample)) {
  $envExample = Join-Path $repoRoot ".env.example"
}

if (Test-Path $envExample) {
  $rootEnv = Join-Path $repoRoot ".env"
  $backendEnv = Join-Path $repoRoot "backend\.env"

  if (-not (Test-Path $rootEnv)) {
    Write-Host "Copying $envExample to .env..."
    Copy-Item $envExample $rootEnv
  } else {
    Write-Host "Root .env already exists."
  }

  if (-not (Test-Path $backendEnv)) {
    Write-Host "Copying $envExample to backend\.env..."
    Copy-Item $envExample $backendEnv
  } else {
    Write-Host "Backend .env already exists."
  }
  Write-Host "Environment files successfully configured." -ForegroundColor Green
} else {
  Write-Host "Warning: No template environment example file (.env.swarmbook.example or .env.example) found." -ForegroundColor Yellow
}

# 6) Ollama local model pulling
Write-Section "5) Validating Local Ollama Models"
$ollamaListening = $false
try {
  $tagsResponse = Invoke-RestMethod -Method Get -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction SilentlyContinue
  $ollamaListening = $true
} catch {
  # Ollama service not running
}

if ($ollamaListening) {
  Write-Host "Ollama service is up and running." -ForegroundColor Green
  $modelPresent = $false
  
  $models = $tagsResponse.models | ForEach-Object { $_.name }
  if ($models -contains $OllamaModel -or $models -contains "$OllamaModel:latest") {
    $modelPresent = $true
    Write-Host "Model '$OllamaModel' is already present locally." -ForegroundColor Green
  }

  if (-not $modelPresent) {
    $pullModel = $false
    if ($AutoInstallPrereqs) {
      $pullModel = $true
    } else {
      $choice = Read-Host "Model '$OllamaModel' was not found. Do you want to download (pull) it now? (Y/N)"
      if ($choice.Trim().ToUpper() -eq 'Y') {
        $pullModel = $true
      }
    }

    if ($pullModel -and (Test-Command 'ollama')) {
      Write-Host "Pulling model '$OllamaModel' from Ollama library..."
      try {
        Start-Process -FilePath "ollama" -ArgumentList @("pull", $OllamaModel) -NoNewWindow -Wait
        Write-Host "Model '$OllamaModel' pulled successfully." -ForegroundColor Green
      } catch {
        Write-Host "Failed to pull model: $($_.Exception.Message)" -ForegroundColor Red
      }
    }
  }
} else {
  Write-Host "Ollama local API is not listening. If you installed it, please start the Ollama application." -ForegroundColor Yellow
}

# 7) Desktop Shortcut
Write-Section "6) Creating Launcher Shortcut"
$shortcutChoice = $false
if ($CreateShortcut) {
  $shortcutChoice = $true
} else {
  $choice = Read-Host "Would you like to create a Desktop shortcut to run Swarmbook? (Y/N)"
  if ($choice.Trim().ToUpper() -eq 'Y') {
    $shortcutChoice = $true
  }
}

if ($shortcutChoice) {
  try {
    $WshShell = New-Object -ComObject WScript.Shell
    $desktop = [System.Environment]::GetFolderPath("Desktop")
    $shortcut = $WshShell.CreateShortcut(Join-Path $desktop "Start Swarmbook.lnk")
    
    $startScript = Join-Path $repoRoot "scripts\windows\start_swarmbook.ps1"
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$startScript`""
    $shortcut.WorkingDirectory = $repoRoot
    $shortcut.Description = "Launch Swarmbook backend and frontend services"
    $shortcut.IconLocation = "powershell.exe,0"
    $shortcut.Save()
    
    Write-Host "Shortcut 'Start Swarmbook.lnk' successfully created on Desktop." -ForegroundColor Green
  } catch {
    Write-Host "Failed to generate Desktop shortcut: $($_.Exception.Message)" -ForegroundColor Red
  }
}

# 8) Verification run
Write-Section "7) Verifying Setup Status"
Set-Location $repoRoot
$checkScript = Join-Path $repoRoot "scripts\windows\check_prereqs.ps1"
if (Test-Path $checkScript) {
  powershell -ExecutionPolicy Bypass -File $checkScript
} else {
  Write-Host "Verification check_prereqs.ps1 script not found." -ForegroundColor Yellow
}

Write-Section "Installation Run Completed"
Write-Host "To start the application, use the desktop shortcut or run:"
Write-Host "  .\\scripts\\windows\\start_swarmbook.ps1" -ForegroundColor Cyan
Write-Host ""
