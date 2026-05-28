# Swarmbook automated local installation tool (Windows 11)
#
# Optimized and robust script:
# - Performs prerequisite checks
# - Safely offers to install missing core tools (Git, Python, Node, Ollama) via winget
# - Provisions the Python virtual environment (.venv) and installs pip dependencies
# - Provisions frontend Node dependencies using npm ci/install and compiles production assets
# - Configures uncommitted environment template files (.env) and prompts for overrides
# - Validates local Ollama models and pulls target models if missing
# - Generates Desktop shortcuts for easy one-click launching and stopping
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\install_swarmbook.ps1
#
# Options:
#   -AutoInstallPrereqs  Automatically install missing prereqs via winget without prompt
#   -SkipFrontend        Skip setting up frontend node modules
#   -OllamaModel         Specifies target Ollama model to pull (default: qwen2.5:7b-instruct)
#   -OllamaEmbedModel    Specifies target Ollama embedding model to pull (default: nomic-embed-text)
#   -CreateShortcut      Automatically create Desktop launch shortcuts without prompt
#   -NoElevation         Skip checking for administrative rights elevation

[CmdletBinding()]
param(
  [switch]$AutoInstallPrereqs,
  [switch]$SkipFrontend,
  [string]$OllamaModel = "qwen2.5:7b-instruct",
  [string]$OllamaEmbedModel = "nomic-embed-text",
  [switch]$CreateShortcut,
  [switch]$NoElevation
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
  $combined = "$machinePath;$userPath"
  
  # Inject default Windows installation paths if they aren't registered yet
  $extraPaths = @(
    "C:\Program Files\Git\cmd",
    "C:\Program Files\nodejs",
    "$env:LOCALAPPDATA\Programs\Python\Python311",
    "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts",
    "$env:LOCALAPPDATA\Programs\Ollama"
  )
  foreach ($p in $extraPaths) {
    if ((Test-Path $p) -and ($combined -notlike "*$p*")) {
      $combined = "$combined;$p"
    }
  }
  $env:Path = $combined
}

# Determine repo root path
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..\..')).Path

Write-Section "Swarmbook Windows Installation Tool"
Write-Host "Target workstation profile: Windows 11, 16 GB RAM, 6 GB VRAM"
Write-Host "Repository location: $repoRoot"

# 1) Administrative rights advice & Self-Elevation Check
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  if ($NoElevation) {
    Write-Host "Notice: Running in unprivileged mode. Winget installs may prompt for Windows UAC." -ForegroundColor Yellow
  } else {
    Write-Host "Elevated administrative privileges are highly recommended for automated winget installations." -ForegroundColor Yellow
    $choice = Read-Host "Would you like to relaunch this installer as Administrator? (Y/N)"
    if ($choice.Trim().ToUpper() -eq 'Y') {
      $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
      # Pass through parameters
      foreach ($key in $PSBoundParameters.Keys) {
        $val = $PSBoundParameters[$key]
        if ($val -is [switch]) {
          if ($val) { $arguments += " -$key" }
        } else {
          $arguments += " -$key `"$val`""
        }
      }
      Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -Verb RunAs
      Exit
    }
  }
}

# 2) Prerequisites check and setup
Write-Section "1) Checking / Installing Core Prerequisites"
Reload-Path
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
      # Execute winget install with retry support
      $retries = 3
      $success = $false
      while (-not $success -and $retries -gt 0) {
        $proc = Start-Process -FilePath "winget" -ArgumentList @("install", "--id", $WingetId, "--silent", "--accept-source-agreements", "--accept-package-agreements") -NoNewWindow -PassThru -Wait
        if ($proc.ExitCode -eq 0) {
          Write-Host "  Successfully installed $FriendlyName. System path will reload." -ForegroundColor Green
          Reload-Path
          $success = $true
        } else {
          $retries--
          Write-Host "  Winget installation returned exit code: $($proc.ExitCode). Retries left: $retries" -ForegroundColor Yellow
          if ($retries -gt 0) { Start-Sleep -Seconds 2 }
        }
      }
      return $success
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

  # Verify python version suitability
  $pythonVersion = (python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
  Write-Host "Detected Python version: $pythonVersion" -ForegroundColor Gray

  if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
  } else {
    Write-Host "Virtual environment (.venv) already exists."
  }

  $pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"
  $pipExe = Join-Path $backendDir ".venv\Scripts\pip.exe"

  if (Test-Path $pythonExe) {
    Write-Host "Upgrading local pip, setuptools, and wheel in virtual environment..."
    Start-Process -FilePath $pythonExe -ArgumentList @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel") -NoNewWindow -Wait
    
    Write-Host "Installing dependencies from requirements.txt..."
    $proc = Start-Process -FilePath $pipExe -ArgumentList @("install", "-r", "requirements.txt") -NoNewWindow -PassThru -Wait
    if ($proc.ExitCode -eq 0) {
      Write-Host "Backend dependencies installed successfully." -ForegroundColor Green
    } else {
      Write-Host "Pip returned exit code: $($proc.ExitCode) during package installation. Please inspect errors." -ForegroundColor Red
    }
  } else {
    Write-Host "Error: Virtual environment python executable not found at $pythonExe" -ForegroundColor Red
  }
}

# 4) Frontend setup
Write-Section "3) Setting Up Frontend Node Modules & Production Assets"
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
      Write-Host "Frontend packages installed successfully." -ForegroundColor Green
      
      # Compile production assets
      Write-Host "Compiling production frontend assets..."
      $procBuild = Start-Process -FilePath $npmCmd -ArgumentList @("run", "build") -NoNewWindow -PassThru -Wait
      if ($procBuild.ExitCode -eq 0) {
        Write-Host "Vite client built successfully." -ForegroundColor Green
      } else {
        Write-Host "Warning: Vite compiler failed. Make sure dependencies are correct." -ForegroundColor Yellow
      }
    } else {
      Write-Host "npm package installation failed with exit code: $($proc.ExitCode)" -ForegroundColor Red
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

  $copied = $false
  if (-not (Test-Path $rootEnv)) {
    Write-Host "Copying $envExample to .env..."
    Copy-Item $envExample $rootEnv
    $copied = $true
  } else {
    Write-Host "Root .env already exists."
  }

  if (-not (Test-Path $backendEnv)) {
    Write-Host "Copying $envExample to backend\.env..."
    Copy-Item $envExample $backendEnv
    $copied = $true
  } else {
    Write-Host "Backend .env already exists."
  }

  # Interactively prompt to configure values
  if ($copied -or (Test-Path $rootEnv)) {
    Write-Host "Do you want to configure your database and API credentials now? (Y/N)"
    $choice = Read-Host
    if ($choice.Trim().ToUpper() -eq 'Y') {
      $neoPass = Read-Host "Enter local Neo4j Database Password [mirofish]"
      if ([string]::IsNullOrWhiteSpace($neoPass)) { $neoPass = "mirofish" }
      
      $geminiKey = Read-Host "Enter Gemini API Key (Optional - press Enter to skip)"
      $nvidiaKey = Read-Host "Enter NVIDIA API Key (Optional - press Enter to skip)"
      
      $content = Get-Content $rootEnv
      $content = $content -replace '^NEO4J_PASSWORD=.*$', "NEO4J_PASSWORD=$neoPass"
      
      if ($geminiKey) {
        $content = $content -replace '^GEMINI_API_KEY=.*$', "GEMINI_API_KEY=$geminiKey"
      }
      if ($nvidiaKey) {
        $content = $content -replace '^NVIDIA_API_KEY=.*$', "NVIDIA_API_KEY=$nvidiaKey"
      }
      
      Set-Content $rootEnv $content
      Copy-Item $rootEnv $backendEnv -Force
      Write-Host "Local configuration variables updated." -ForegroundColor Green
    }
  }
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
  
  function Verify-And-Pull-Model([string]$TargetModel) {
    $modelPresent = $false
    $models = $tagsResponse.models | ForEach-Object { $_.name }
    if ($models -contains $TargetModel -or $models -contains "$TargetModel:latest") {
      $modelPresent = $true
      Write-Host "Model '$TargetModel' is already present locally." -ForegroundColor Green
    }

    if (-not $modelPresent) {
      $pullModel = $false
      if ($AutoInstallPrereqs) {
        $pullModel = $true
      } else {
        $choice = Read-Host "Model '$TargetModel' was not found. Do you want to download (pull) it now? (Y/N)"
        if ($choice.Trim().ToUpper() -eq 'Y') {
          $pullModel = $true
        }
      }

      if ($pullModel -and (Test-Command 'ollama')) {
        Write-Host "Pulling model '$TargetModel' from Ollama library..."
        try {
          Start-Process -FilePath "ollama" -ArgumentList @("pull", $TargetModel) -NoNewWindow -Wait
          Write-Host "Model '$TargetModel' pulled successfully." -ForegroundColor Green
        } catch {
          Write-Host "Failed to pull model: $($_.Exception.Message)" -ForegroundColor Red
        }
      }
    }
  }

  Verify-And-Pull-Model -TargetModel $OllamaModel
  Verify-And-Pull-Model -TargetModel $OllamaEmbedModel
} else {
  Write-Host "Ollama local API is not listening. If you installed it, please start the Ollama application." -ForegroundColor Yellow
}

# 7) Desktop Shortcuts
Write-Section "6) Creating Launcher Shortcuts"
$shortcutChoice = $false
if ($CreateShortcut) {
  $shortcutChoice = $true
} else {
  $choice = Read-Host "Would you like to create Desktop shortcuts to run Swarmbook? (Y/N)"
  if ($choice.Trim().ToUpper() -eq 'Y') {
    $shortcutChoice = $true
  }
}

if ($shortcutChoice) {
  try {
    $WshShell = New-Object -ComObject WScript.Shell
    $desktop = [System.Environment]::GetFolderPath("Desktop")
    
    # 1. Start Shortcut
    $startPath = Join-Path $desktop "Start Swarmbook.lnk"
    $startShortcut = $WshShell.CreateShortcut($startPath)
    $startScript = Join-Path $repoRoot "scripts\windows\start_swarmbook.ps1"
    $startShortcut.TargetPath = "powershell.exe"
    $startShortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$startScript`""
    $startShortcut.WorkingDirectory = $repoRoot
    $startShortcut.Description = "Launch Swarmbook backend and frontend services"
    $startShortcut.IconLocation = "powershell.exe,0"
    $startShortcut.Save()
    Write-Host "Created 'Start Swarmbook' desktop shortcut." -ForegroundColor Green

    # 2. Stop Shortcut
    $stopPath = Join-Path $desktop "Stop Swarmbook.lnk"
    $stopShortcut = $WshShell.CreateShortcut($stopPath)
    $stopScript = Join-Path $repoRoot "scripts\windows\stop_swarmbook.ps1"
    $stopShortcut.TargetPath = "powershell.exe"
    $stopShortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$stopScript`""
    $stopShortcut.WorkingDirectory = $repoRoot
    $stopShortcut.Description = "Gracefully stop running Swarmbook services"
    $stopShortcut.IconLocation = "powershell.exe,0"
    $stopShortcut.Save()
    Write-Host "Created 'Stop Swarmbook' desktop shortcut." -ForegroundColor Green
    
  } catch {
    Write-Host "Failed to generate Desktop shortcuts: $($_.Exception.Message)" -ForegroundColor Red
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
