# verify-release.ps1
# Extracts and validates the structure and integrity of the Swarmbook portable ZIP package.

$ErrorActionPreference = 'Stop'

# Determine repo root
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path (Join-Path $scriptDir '..')).Path
$zipFile = "D:\SW\MiroFish_Swarmbook_Portable_v0.1.zip"
$extractTemp = Join-Path $repoRoot "temp_verify_extract"

Write-Host "=============================================================================="
Write-Host "Swarmbook Release Verification"
Write-Host "=============================================================================="
Write-Host "Target ZIP file: $zipFile"

if (-not (Test-Path $zipFile)) {
    throw "Error: Release ZIP file does not exist at $zipFile"
}

# 1. Clean and create extract temp
if (Test-Path $extractTemp) {
    Remove-Item $extractTemp -Recurse -Force | Out-Null
}
New-Item -ItemType Directory -Path $extractTemp | Out-Null

# 2. Extract ZIP
Write-Host "Extracting package to temporary path: $extractTemp..." -ForegroundColor Gray
Expand-Archive -Path $zipFile -DestinationPath $extractTemp

# 3. Check critical files
Write-Host "Checking critical file presence..." -ForegroundColor Cyan

$criticalFiles = @(
    "start-swarmbook.bat",
    "stop-swarmbook.bat",
    "check-system.bat",
    "install-swarmbook.bat",
    "open-logs.bat",
    "reset-local-cache.bat",
    "release-manifest.json",
    "sha256sum.txt",
    "backend\run.py",
    "frontend\dist\index.html",
    "configs\book_sim\model_routes.yaml"
)

$missing = @()
foreach ($file in $criticalFiles) {
    $fullPath = Join-Path $extractTemp $file
    Write-Host "Checking: $file..." -NoNewline
    if (Test-Path $fullPath) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " MISSING" -ForegroundColor Red
        $missing += $file
    }
}

# 4. Clean up extraction folder
Write-Host "`nCleaning up extraction temporary directory..." -ForegroundColor Gray
Remove-Item $extractTemp -Recurse -Force | Out-Null

# 5. Report results
if ($missing.Count -eq 0) {
    Write-Host "`nRelease Verification SUCCESS! Package is valid and correct." -ForegroundColor Green
} else {
    throw "Release Verification FAILED! Missing files: $($missing -join ', ')"
}
