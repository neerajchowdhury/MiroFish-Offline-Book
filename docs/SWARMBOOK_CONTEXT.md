# Swarmbook Context (Reconstructed)

## Goal
Transform MiroFish-Offline into a personal, local-first "simulate any book" tool that supports manuscript stress testing before publication.

## Merged MVP Scope (Target)
- Manuscript-to-report pipeline.
- Persona interrogation.
- Draft comparison.

## Target Runtime Profile
- OS: Windows 11.
- RAM target: 16 GB.
- GPU target: 6 GB NVIDIA GPU.
- Core local services: Neo4j + Ollama.

## Model Strategy
- Local Ollama: default for local processing, cheaper summarization, embeddings.
- Gemini: optional for higher quality long-context synthesis.
- NVIDIA/NIM-compatible endpoint: optional fallback/adversarial path.

## Privacy Modes
- `local_only`
- `hybrid_safe`
- `cloud_quality`

## Evidence-Pack Types
- Book DNA
- Chapter map
- Character map
- Claim map
- Risk map
- Style map
- Market surface

## Simulated Platform Styles
- Goodreads
- BookTok
- Reddit
- Bookstagram
- X
- newsletter
- bookclub

## Current Implemented Modules (From Repository State)

### Documentation and config
- `docs/SWARMBOOK_ARCHITECTURE.md`
- `configs/book_sim/model_routes.yaml`
- `configs/book_sim/privacy_modes.yaml`
- `configs/book_sim/reader_archetypes.yaml`
- `configs/book_sim/platform_styles.yaml`
- `configs/book_sim/scoring_weights.yaml`
- `configs/book_sim/evidence_pack_schema.yaml`

### Backend `book_sim` foundation
- Routing/config:
  - `backend/app/book_sim/config_loader.py`
  - `backend/app/book_sim/provider_router.py`
- Providers:
  - `backend/app/book_sim/providers/base.py`
  - `backend/app/book_sim/providers/ollama_provider.py`
  - `backend/app/book_sim/providers/gemini_provider.py`
  - `backend/app/book_sim/providers/nvidia_provider.py`
- Typed models:
  - `backend/app/book_sim/models.py`
- Ingest/evidence:
  - `backend/app/book_sim/manuscript_chunker.py`
  - `backend/app/book_sim/book_dna_extractor.py`
  - `backend/app/book_sim/style_analyzer.py`
  - `backend/app/book_sim/risk_detector.py`
  - `backend/app/book_sim/nonfiction_claim_extractor.py`
  - `backend/app/book_sim/character_mapper.py`
  - `backend/app/book_sim/evidence_pack_builder.py`
  - `backend/app/book_sim/local_cache.py`
- Graph persistence:
  - `backend/app/book_sim/graph_persistence.py`
- Reader/runtime:
  - `backend/app/book_sim/reader_archetype_loader.py`
  - `backend/app/book_sim/reader_persona_generator.py`
  - `backend/app/book_sim/platform_adapters/*`
  - `backend/app/book_sim/simulation/*`
- Runtime storage/reporting:
  - `backend/app/book_sim/runtime_store.py`
  - `backend/app/book_sim/report_builder.py`
- Interrogation:
  - `backend/app/book_sim/interrogation/*`
- Comparison:
  - `backend/app/book_sim/comparison/*`
- Scoring:
  - `backend/app/book_sim/scoring/*`

### Backend API wiring
- `backend/app/api/book_sim.py`
- Registered in Flask through `backend/app/api/__init__.py` and `backend/app/__init__.py`
- Current exposed routes:
  - `/api/book-sim/projects`
  - `/api/book-sim/evidence-packs`
  - `/api/book-sim/simulate`
  - `/api/book-sim/projects/<project_id>/report`
  - `/api/book-sim/personas/<persona_id>/chat`
  - `/api/book-sim/compare`
  - `/api/book-sim/health`
  - `/api/book-sim/interrogate` (backward-compatible narrow interrogation route)

### Tests and fixtures
- `backend/tests/test_book_sim_provider_router.py`
- `backend/tests/test_book_sim_models.py`
- `backend/tests/test_book_sim_evidence_pack_builder.py`
- `backend/tests/test_book_sim_graph_persistence.py`
- `backend/tests/test_book_sim_reader_persona_generator.py`
- `backend/tests/test_book_sim_platform_adapters.py`
- `backend/tests/test_book_sim_simulation_engine.py`
- `backend/tests/test_book_sim_persona_chat.py`
- `backend/tests/test_book_sim_draft_comparator.py`
- `backend/tests/test_book_sim_api.py`
- `backend/tests/fixtures/book_sim_fiction_sample.txt`
- `backend/tests/fixtures/book_sim_nonfiction_sample.txt`
- `backend/tests/fixtures/book_sim_compare_draft_a.txt`
- `backend/tests/fixtures/book_sim_compare_draft_b.txt`
- `backend/tests/smoke_check.py`

### Environment/dependency support
- `.env.example` includes optional Swarmbook keys (`OLLAMA_BASE_URL`, `GEMINI_API_KEY`, `NVIDIA_API_KEY`, `NVIDIA_BASE_URL`).
- `backend/pyproject.toml` and `backend/requirements.txt` include `PyYAML`.

## Current Missing Modules / Wiring
- No dedicated Swarmbook report package exists yet under `backend/app/book_sim/reports/`; runtime report synthesis currently lives in `backend/app/book_sim/report_builder.py`.
- Frontend Swarmbook routing exists under `frontend/src/router/index.js`; build validation now passes through bundled runtime Node + direct Vite invocation, while `npm run build` still fails due to a broken machine-level npm shim path.
- Privacy mode is partially enforced in router selection but not system-wide policy enforcement.

## Known Limitations (Current State)
- Current evidence extraction is largely heuristic with selective router use.
- Swarmbook now has a bounded backend runtime path plus an additive frontend flow under `/swarmbook/*`; frontend build validates through direct Vite execution, but normal `npm run build` remains broken by the local npm shim.
- Cache exists (`LocalArtifactCache`) but replay policy/version invalidation is minimal.
- External provider usage policy is not centrally audited across future stages.
- This system remains a synthetic stress-test approach, not market prediction certainty.
- Report artifacts are now generated through the runtime helper, but there is still no dedicated `backend/app/book_sim/reports/` package or richer report-synthesis layer.
