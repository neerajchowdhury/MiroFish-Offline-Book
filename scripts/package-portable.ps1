# package-portable.ps1
# Creates a portable ZIP packaging of Swarmbook Studio.

$ErrorActionPreference = 'Stop'

# Determine repo root
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..')).Path
$releaseDir = "D:\SW\MiroFish_Release v2"
$zipFile = "D:\SW\MiroFish_Swarmbook_Portable_v0.1.zip"

Write-Host "=============================================================================="
Write-Host "Swarmbook Portable Packager"
Write-Host "=============================================================================="
Write-Host "Repo root: $repoRoot"
Write-Host "Release target folder: $releaseDir"
Write-Host "Release ZIP package: $zipFile"

# 1. Run build-release first to compile and test
$buildScript = Join-Path $scriptDir "build-release.ps1"
if (Test-Path $buildScript) {
    powershell -NoProfile -ExecutionPolicy Bypass -File $buildScript
}

# 2. Re-create clean release output structure
if (-not (Test-Path $releaseDir)) {
    New-Item -ItemType Directory -Path $releaseDir | Out-Null
}

Write-Host "`nCopying required application files..." -ForegroundColor Cyan

# Helper to copy directory with custom filter exclusions
function Copy-Filtered-Dir([string]$Src, [string]$Dest, [string[]]$Exclude) {
    if (-not (Test-Path $Src)) { return }
    if (-not (Test-Path $Dest)) {
        New-Item -ItemType Directory -Path $Dest | Out-Null
    }
    
    Get-ChildItem -Path $Src | ForEach-Object {
        $name = $_.Name
        if ($Exclude -contains $name) {
            # Skip excluded files/folders
            return
        }
        
        $destPath = Join-Path $Dest $name
        if ($_.PsIsContainer) {
            Copy-Filtered-Dir -Src $_.FullName -Dest $destPath -Exclude $Exclude
        } else {
            Copy-Item -Path $_.FullName -Destination $destPath -Force
        }
    }
}

$rootExclusions = @(".git", ".github", ".codex", ".opencode", ".swarmbook_pids", "backend", "frontend", "install", "scripts", ".env", "node_modules", "temp_uploads", "logs", "__pycache__", ".pytest_cache", ".venv")
$backendExclusions = @(".venv", "__pycache__", ".pytest_cache", "logs", "temp_uploads", ".env", "tests")
$frontendExclusions = @("node_modules", ".pytest_cache", "dist-temp") # Keep dist

# Copy root files
Copy-Filtered-Dir -Src $repoRoot -Dest $releaseDir -Exclude $rootExclusions

# Copy modules
Copy-Filtered-Dir -Src (Join-Path $repoRoot "backend") -Dest (Join-Path $releaseDir "backend") -Exclude $backendExclusions
Copy-Filtered-Dir -Src (Join-Path $repoRoot "frontend") -Dest (Join-Path $releaseDir "frontend") -Exclude $frontendExclusions
Copy-Filtered-Dir -Src (Join-Path $repoRoot "scripts") -Dest (Join-Path $releaseDir "scripts") -Exclude @()
Copy-Filtered-Dir -Src (Join-Path $repoRoot "install") -Dest (Join-Path $releaseDir "install") -Exclude @()

# Ensure target directories exist inside release
New-Item -ItemType Directory -Path (Join-Path $releaseDir "backend\logs") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $releaseDir "backend\temp_uploads") -Force | Out-Null

# 3. Create release manifest
Write-Host "`nGenerating release manifest..." -ForegroundColor Cyan
$commitHash = "unknown"
try {
    $commitHash = (git rev-parse --short HEAD 2>$null).Trim()
} catch {}

$manifest = @{
    AppName = "Swarmbook Studio / MiroFish-Offline"
    Version = "0.1.0-portable"
    BuildDate = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    CommitHash = $commitHash
    PackageType = "Portable ZIP"
    RequiredDependencies = @("Python >= 3.11", "NodeJS >= 18.0.0", "Ollama >= 0.1.48", "Neo4j >= 5.18.0")
    KnownLimitations = "Local Ollama models and Neo4j instances must be started before full pipeline simulations. Privacy mode hybrid_safe/cloud_quality requires internet access; local_only works completely offline."
}

$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $releaseDir "release-manifest.json")

# 4. Generate SHA256 Checksums
Write-Host "Calculating SHA256 checksums..." -ForegroundColor Cyan
$checksums = Get-ChildItem -Path $releaseDir -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash
    # Get relative path
    $relative = $_.FullName.Substring($releaseDir.Length + 1)
    "$hash  $relative"
}
$checksums | Set-Content -Path (Join-Path $releaseDir "sha256sum.txt")

# 5. Compress to ZIP
Write-Host "`nCompressing release to: $zipFile" -ForegroundColor Cyan
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}
Compress-Archive -Path (Join-Path $releaseDir "*") -DestinationPath $zipFile

Write-Host "Portable release packaging complete!" -ForegroundColor Green
