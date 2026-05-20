# Swarmbook Prompt Log (Summarized)

This file captures concise summaries of the major Swarmbook build prompts already reflected in repository state.

## Phase 0 (Audit)
- Prompt summary: audit repository architecture (backend/frontend/routes/config/tests/docker/dev commands) and identify additive integration points for `book_sim`.
- Evidence in repo: no dedicated persisted phase document found; status reconstructed from current files.

## Phase 1 (Baseline Verification)
- Prompt summary: produce baseline checklist/smoke plan for backend/frontend/Neo4j/Ollama and tests.
- Evidence in repo: `backend/tests/smoke_check.py`.

## Phase 2 (Architecture Doc)
- Prompt summary: add Swarmbook transformation architecture document with pipeline, privacy modes, hybrid model strategy, additive module plan, and phased implementation.
- Evidence in repo: `docs/SWARMBOOK_ARCHITECTURE.md`.

## Phase 3 (Config Skeleton)
- Prompt summary: add Swarmbook config files for model routes, privacy modes, archetypes, platform styles, scoring, and evidence schemas.
- Evidence in repo: `configs/book_sim/*.yaml`.

## Phase 4 (Provider Router Foundation)
- Prompt summary: implement additive provider-router layer for Ollama/Gemini/NVIDIA with env-driven config and privacy-mode awareness; add tests.
- Evidence in repo: `backend/app/book_sim/config_loader.py`, `provider_router.py`, `providers/*`, `test_book_sim_provider_router.py`.

## Phase 5 (Typed Schemas)
- Prompt summary: add typed JSON-serializable models for Swarmbook artifacts and simulation/report objects; add serialization tests.
- Evidence in repo: `backend/app/book_sim/models.py`, `backend/tests/test_book_sim_models.py`.

## Phase 6 (Ingest + Evidence Packs)
- Prompt summary: implement manuscript ingestion/evidence-pack generation modules (chunking, DNA, style, risk, character, claim extraction, caching) with tiny fiction/non-fiction fixtures and tests.
- Evidence in repo: `backend/app/book_sim/*extractor*`, `manuscript_chunker.py`, `evidence_pack_builder.py`, `local_cache.py`, `test_book_sim_evidence_pack_builder.py`, fixtures.

## Continuity Recovery (Current)
- Prompt summary: reconstruct project memory from actual repo state and create continuity docs before proceeding to next phase.
- Evidence in repo: `AGENTS.md` and `docs/SWARMBOOK_*` continuity files in this pass.

## Phase 17 Repair (Local Low-Resource Profile)
- Prompt summary: implement missing local profile config + loader + warnings + docs + tests, wire defaults into additive backend/API/frontend without starting Phase 18 features.
- Evidence in repo:
  - `configs/book_sim/local_profiles.yaml`
  - `backend/app/book_sim/local_profiles.py`
  - `docs/SWARMBOOK_LOCAL_SETUP.md`
  - `backend/tests/test_book_sim_local_profiles.py`
  - profile-aware updates in `backend/app/api/book_sim.py`

## Phase 18 Quality Gate
- Prompt summary: run a full quality pass over Swarmbook, validate tests/builds/critical paths, and consolidate documentation without starting Phase 19.
- Evidence in repo:
  - `backend/tests/test_book_sim_report_builder.py`
  - `docs/SWARMBOOK_PHASE_STATUS.md`
  - `docs/SWARMBOOK_CHANGELOG.md`
  - `docs/SWARMBOOK_DECISIONS.md`
  - `docs/SWARMBOOK_OPEN_QUESTIONS.md`
  - `docs/SWARMBOOK_HANDOFF_LATEST.md`
