# Swarmbook Local Setup (Phase 17)

## Purpose
Swarmbook local profiles provide safe defaults for local-first simulation on a personal workstation while preserving `local_only` privacy behavior.

## Hardware Target
- OS: Windows 11
- RAM: 16 GB
- GPU: NVIDIA
- VRAM: 6 GB

## Recommended Default
- `hybrid_safe_default`

## Profile Summary

| Profile | Privacy Mode | Personas | Platforms | Reaction Rounds | Cross-Reaction Posts | Local Parallel Jobs | Resource Level |
|---|---|---:|---|---:|---:|---:|---|
| `local_tiny` | `local_only` | 12 | Goodreads, Reddit, X | 1 | 4 | 1 | low |
| `hybrid_safe_default` | `hybrid_safe` | 30 | Goodreads, Reddit, BookTok, Bookstagram, X | 2 | 8 | 1 | medium |
| `cloud_quality` | `cloud_quality` | 60 | Goodreads, Reddit, BookTok, Bookstagram, X, newsletter, bookclub | 2 | 12 | 1 | high |

## Privacy Behavior
- `local_only`: provider router forces local Ollama route only; no Gemini/NVIDIA usage.
- `hybrid_safe`: local embeddings/chunk summaries stay local; cloud usage may be allowed for selected tasks.
- `cloud_quality`: cloud models allowed, including full manuscript/evidence upload according to profile settings.

## Recommended Ollama Usage (Low Resource)
- Keep one model loaded at a time for low-RAM systems.
- Prefer compact models for iterative runs.
- Suggested pattern:
  - fast local synthesis: a smaller instruct model
  - deeper local synthesis: a larger model only when needed

## Environment Variables (Placeholders Only)
Use placeholders only. Do not place real secrets in committed files.

```env
OLLAMA_BASE_URL=http://localhost:11434
GEMINI_API_KEY=your_gemini_key_here
NVIDIA_API_KEY=your_nvidia_key_here
NVIDIA_BASE_URL=your_nvidia_base_url_here
```

Warning: never commit real API keys.

## PowerShell Validation Commands

```powershell
# Verify local profile config exists
Test-Path .\configs\book_sim\local_profiles.yaml

# Verify backend imports
python -m compileall backend

# Run Swarmbook profile tests
python -m unittest backend.tests.test_book_sim_local_profiles backend.tests.test_book_sim_provider_router backend.tests.test_book_sim_api

# Optional frontend build (if frontend dependencies are available)
npm run build
```

## Troubleshooting

### Missing Ollama
- Symptom: `/api/book-sim/health` reports local Ollama unavailable.
- Fix: start Ollama and verify `OLLAMA_BASE_URL`.

### Missing Neo4j
- Symptom: `/api/book-sim/health` shows Neo4j not initialized/unavailable.
- Fix: start Neo4j locally or run with graph persistence fallback expectations.

### Missing API Keys
- Symptom: Gemini/NVIDIA health checks fail.
- Fix: keep running with `local_only`/`local_tiny` or set placeholder env vars to real local values in your local shell (never in committed docs).

### Slow Local Runs
- Symptom: long simulation time on 16 GB RAM / 6 GB VRAM.
- Fix: switch to `local_tiny`, keep `local_parallel_jobs=1`, reduce personas/platforms.

### Profile Config Missing
- Symptom: health endpoint reports profile load error.
- Fix: restore `configs/book_sim/local_profiles.yaml` and re-run validation.
