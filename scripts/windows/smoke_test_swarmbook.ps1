# Swarmbook smoke test (Windows 11)
#
# Runs a minimal local-first flow against the backend:
# - /api/book-sim/health
# - create project
# - create evidence pack (small sample text)
# - simulate (local_only)
# - persona chat
#
# This script DOES NOT call any real external providers. It uses local_only + route fallback.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\windows\smoke_test_swarmbook.ps1
#
# Optional:
#   -BackendBaseUrl http://localhost:5001

[CmdletBinding()]
param(
  [string]$BackendBaseUrl = "http://localhost:5001"
)

$ErrorActionPreference = 'Stop'

function Write-Section([string]$Title) {
  Write-Host ''
  Write-Host ('-' * 78)
  Write-Host $Title
  Write-Host ('-' * 78)
}

function Post-Json([string]$Url, [hashtable]$Body) {
  return Invoke-RestMethod -Method Post -Uri $Url -ContentType 'application/json' -Body ($Body | ConvertTo-Json -Depth 12)
}

Write-Section "Swarmbook Smoke Test"
Write-Host "Backend: $BackendBaseUrl"

Write-Section "1) Health"
$health = Invoke-RestMethod -Method Get -Uri "$BackendBaseUrl/api/book-sim/health"
if (-not $health.success) { throw "Health failed: $($health.error)" }
Write-Host "Health OK. Default profile: $($health.data.profiles.default_profile)"

Write-Section "2) Create Project"
$project = Post-Json "$BackendBaseUrl/api/book-sim/projects" @{
  name = "Smoke Test Project"
  privacy_mode = "local_only"
  draft_id = "draft_smoke"
  version = "v1"
  metadata = @{ local_profile = "local_tiny" }
}
if (-not $project.success) { throw "Project create failed: $($project.error)" }
$projectId = $project.data.project_id
Write-Host "Project OK: $projectId"

Write-Section "3) Create Evidence Pack"
$sampleText = @"
Chapter 1
Mara gets a letter that threatens her promotion if she misses tonight's meeting.

Chapter 2
At the town hall, she realizes her mentor has been hiding the truth about the budget.

Chapter 3
She must choose: protect the mentor or expose the truth and lose her job.
"@

$evidence = Post-Json "$BackendBaseUrl/api/book-sim/evidence-packs" @{
  project_id = $projectId
  title = "Smoke Test Draft"
  author_name = "Local Tester"
  text = $sampleText
}
if (-not $evidence.success) { throw "Evidence pack failed: $($evidence.error)" }
$packId = $evidence.data.evidence_pack.pack_id
Write-Host "Evidence pack OK: $packId"

Write-Section "4) Simulate"
$sim = Post-Json "$BackendBaseUrl/api/book-sim/simulate" @{
  project_id = $projectId
  evidence_pack_id = $packId
  profile_name = "local_tiny"
  privacy_mode = "local_only"
  simulation_seed = 17
  route_name = "gemini_fast" # should fallback to local_ollama due to local_only
}
if (-not $sim.success) { throw "Simulate failed: $($sim.error)" }
Write-Host "Sim OK. Selected route: $($sim.data.route_selection.selected_route)"

$personaId = $sim.data.simulation_run.reader_personas[0].persona_id
Write-Host "Persona sample: $personaId"

Write-Section "5) Persona Chat"
$chat = Post-Json "$BackendBaseUrl/api/book-sim/personas/$personaId/chat" @{
  project_id = $projectId
  question = "Why did you rate this book this way?"
}
if (-not $chat.success) { throw "Chat failed: $($chat.error)" }
Write-Host "Chat OK. based_on refs: $($chat.data.based_on.Count)"

Write-Section "Done"
Write-Host "Swarmbook smoke test completed successfully."

