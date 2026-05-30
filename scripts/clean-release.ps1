# clean-release.ps1
# Cleans up the generated release directory.

$releaseDir = "D:\SW\MiroFish_Release v2"
$zipFile = "D:\SW\MiroFish_Swarmbook_Portable_v0.1.zip"

Write-Host "=============================================================================="
Write-Host "Swarmbook Release Cleanup"
Write-Host "=============================================================================="

if (Test-Path $releaseDir) {
    Write-Host "Removing release output folder: $releaseDir" -ForegroundColor Yellow
    Remove-Item -Path $releaseDir -Recurse -Force -ErrorAction SilentlyContinue
}

if (Test-Path $zipFile) {
    Write-Host "Removing release ZIP package: $zipFile" -ForegroundColor Yellow
    Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue
}

Write-Host "Cleanup completed successfully." -ForegroundColor Green
