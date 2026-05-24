# ============================================================================
# MiroFish-Offline — Backup & Restore Utility (Windows PowerShell)
# ============================================================================
# Backs up or restores all user data: projects, evidence packs, simulations,
# reports, Neo4j data, and configuration.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\install\backup_restore.ps1 -Action Backup -BackupDir "D:\MiroFishBackup"
#   powershell -ExecutionPolicy Bypass -File .\install\backup_restore.ps1 -Action Restore -BackupDir "D:\MiroFishBackup"
# ============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Backup', 'Restore')]
    [string]$Action,

    [Parameter(Mandatory=$true)]
    [string]$BackupDir,

    [string]$RepoPath = ""
)

$ErrorActionPreference = 'Stop'

if (-not $RepoPath) {
    $RepoPath = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupPath = Join-Path $BackupDir "mirofish_backup_$timestamp"

function Write-Step { param($m) Write-Host "`n>>> $m" -ForegroundColor Cyan }
function Write-Ok   { param($m) Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Info { param($m) Write-Host "  -> $m" -ForegroundColor Gray }

if ($Action -eq 'Backup') {
    Write-Step "Backing up MiroFish-Offline data"
    Write-Info "Source: $RepoPath"
    Write-Info "Target: $backupPath"

    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

    # Backup user data directories
    $dataDirs = @(
        @{ src = 'backend\uploads\book_sim_cache'; name = 'book_sim_cache' },
        @{ src = 'backend\uploads\simulations';    name = 'simulations' },
        @{ src = 'backend\uploads\reports';         name = 'reports' },
        @{ src = 'backend\uploads\projects';        name = 'projects' },
        @{ src = 'configs\book_sim';                name = 'configs_book_sim' },
    )

    foreach ($dir in $dataDirs) {
        $srcPath = Join-Path $RepoPath $dir.src
        if (Test-Path $srcPath) {
            $destPath = Join-Path $backupPath $dir.name
            Copy-Item -Path $srcPath -Destination $destPath -Recurse -Force
            $items = (Get-ChildItem -Path $srcPath -Recurse).Count
            Write-Ok "$($dir.name): $items items backed up"
        } else {
            Write-Info "$($dir.name): not found (skipped)"
        }
    }

    # Backup .env (without secrets note)
    $envFile = Join-Path $RepoPath '.env'
    if (Test-Path $envFile) {
        Copy-Item $envFile (Join-Path $backupPath 'env_backup.txt')
        Write-Ok ".env backed up (contains secrets — handle with care)"
    }

    # Export Neo4j data if Docker is running
    try {
        $neo4jRunning = docker inspect --format='{{.State.Running}}' mirofish-neo4j 2>$null
        if ($neo4jRunning -eq 'true') {
            Write-Info "Exporting Neo4j database dump..."
            $dumpPath = Join-Path $backupPath 'neo4j_dump'
            New-Item -ItemType Directory -Path $dumpPath -Force | Out-Null
            docker exec mirofish-neo4j neo4j-admin database dump neo4j --to-path=/data/dump 2>$null
            docker cp mirofish-neo4j:/data/dump $dumpPath 2>$null
            Write-Ok "Neo4j dump exported"
        }
    } catch {
        Write-Info "Neo4j dump skipped (Docker not running or neo4j-admin unavailable)"
    }

    # Create manifest
    $manifest = @{
        backup_date   = (Get-Date).ToString('o')
        repo_path     = $RepoPath
        version       = (Get-Content (Join-Path $RepoPath 'package.json') | ConvertFrom-Json).version
        data_dirs     = $dataDirs | Where-Object { Test-Path (Join-Path $RepoPath $_.src) } | ForEach-Object { $_.name }
    }
    $manifest | ConvertTo-Json -Depth 3 | Set-Content (Join-Path $backupPath 'manifest.json')

    Write-Step "Backup Complete"
    Write-Ok "Backup saved to: $backupPath"
    $size = "{0:N2} MB" -f ((Get-ChildItem $backupPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB)
    Write-Info "Total size: $size"

} elseif ($Action -eq 'Restore') {
    Write-Step "Restoring MiroFish-Offline data"
    Write-Info "Source: $backupPath"
    Write-Info "Target: $RepoPath"

    if (-not (Test-Path $backupPath)) {
        Write-Error "Backup directory not found: $backupPath"
        exit 1
    }

    # Restore user data directories
    $dataDirs = @(
        @{ dest = 'backend\uploads\book_sim_cache'; name = 'book_sim_cache' },
        @{ dest = 'backend\uploads\simulations';    name = 'simulations' },
        @{ dest = 'backend\uploads\reports';         name = 'reports' },
        @{ dest = 'backend\uploads\projects';        name = 'projects' },
        @{ dest = 'configs\book_sim';                name = 'configs_book_sim' },
    )

    foreach ($dir in $dataDirs) {
        $srcPath = Join-Path $backupPath $dir.name
        $destPath = Join-Path $RepoPath $dir.dest
        if (Test-Path $srcPath) {
            if (Test-Path $destPath) {
                Write-Info "$($dir.name): already exists, merging..."
            }
            Copy-Item -Path $srcPath -Destination $destPath -Recurse -Force
            Write-Ok "$($dir.name): restored"
        } else {
            Write-Info "$($dir.name): not in backup (skipped)"
        }
    }

    # Restore .env
    $envBackup = Join-Path $backupPath 'env_backup.txt'
    if (Test-Path $envBackup) {
        Copy-Item $envBackup (Join-Path $RepoPath '.env') -Force
        Write-Ok ".env restored"
    }

    # Restore Neo4j dump if available
    $neo4jDump = Join-Path $backupPath 'neo4j_dump'
    if (Test-Path $neo4jDump) {
        Write-Info "Neo4j dump found — manual restore required:"
        Write-Info "  1. Stop Neo4j: docker stop mirofish-neo4j"
        Write-Info "  2. Copy dump: docker cp $neo4jDump mirofish-neo4j:/data/dump"
        Write-Info "  3. Restore: docker exec mirofish-neo4j neo4j-admin database load neo4j --from-path=/data/dump --overwrite-destination=true"
        Write-Info "  4. Start Neo4j: docker start mirofish-neo4j"
    }

    Write-Step "Restore Complete"
    Write-Ok "Data restored to: $RepoPath"
    Write-Info "Restart services to apply changes."
}
