# Swarmbook Usage Guide (Local-First)

Swarmbook is an additive, local-first simulation pipeline inside the MiroFish-Offline repo. It generates synthetic reader reactions, platform posts, and directional scoring from a manuscript draft and a deterministic seed.

## What You Need
- Windows 11, 16 GB RAM, NVIDIA GPU with ~6 GB VRAM (target baseline)
- Ollama running locally (for `local_only` and as a default local provider)
- Optional Neo4j running locally (graph persistence is additive; Swarmbook should still run if Neo4j is down)

## Quick Start (UI)
1. Open the app and go to the Swarmbook section.
2. Create a project (name, title, optional metadata).
3. Paste manuscript text (start with 1-3 chapters for fast iteration).
4. Generate an evidence pack.
5. Choose a local profile:
   - `local_tiny` for the safest fully local mode
   - `hybrid_safe_default` for recommended local defaults on 16 GB / 6 GB VRAM
   - `cloud_quality` only if you explicitly want cloud-enabled behavior and accept privacy/cost warnings
6. Run simulation and inspect the report dashboard.
7. Interrogate individual personas to understand ratings, DNF, and triggers.
8. Compare Draft A vs Draft B using evidence packs and optional simulation runs.

## Quick Start (API)
All endpoints are additive under `/api/book-sim/*`.

```powershell
# 1) Health check (shows provider availability, Neo4j status, and local profiles)
Invoke-RestMethod http://localhost:5001/api/book-sim/health

# 2) Create a project
$project = Invoke-RestMethod -Method Post http://localhost:5001/api/book-sim/projects -ContentType 'application/json' -Body (@{
  name = 'My Draft'
  privacy_mode = 'local_only'
  draft_id = 'draft_a'
  version = 'v1'
  metadata = @{ local_profile = 'local_tiny' }
} | ConvertTo-Json -Depth 10)

$projectId = $project.data.project_id

# 3) Create an evidence pack
$pack = Invoke-RestMethod -Method Post http://localhost:5001/api/book-sim/evidence-packs -ContentType 'application/json' -Body (@{
  project_id = $projectId
  title = 'My Draft Title'
  text = 'Chapter 1`nA small opening...'
} | ConvertTo-Json -Depth 10)

$packId = $pack.data.evidence_pack.pack_id

# 4) Run simulation
$sim = Invoke-RestMethod -Method Post http://localhost:5001/api/book-sim/simulate -ContentType 'application/json' -Body (@{
  project_id = $projectId
  evidence_pack_id = $packId
  profile_name = 'local_tiny'
  simulation_seed = 17
} | ConvertTo-Json -Depth 10)

$personaId = $sim.data.simulation_run.reader_personas[0].persona_id

# 5) Persona interrogation
Invoke-RestMethod -Method Post "http://localhost:5001/api/book-sim/personas/$personaId/chat" -ContentType 'application/json' -Body (@{
  project_id = $projectId
  question = 'Why did you rate this book this way?'
} | ConvertTo-Json -Depth 10)
```

## Operational Notes
- Determinism: set `simulation_seed` for stable comparisons across runs.
- Large manuscripts: start with smaller excerpts; expand once the pipeline is stable on your machine.
- Privacy modes:
  - `local_only`: the provider router forces local Ollama routes only.
  - `hybrid_safe`: may allow limited cloud tasks if configured and keys exist, but should keep full manuscript local by default.
  - `cloud_quality`: may allow full manuscript and evidence-pack cloud usage based on profile settings.

