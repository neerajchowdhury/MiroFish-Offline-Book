# Swarmbook Changelog (Reconstructed)

## Phase 2 (Architecture Documentation)
### Files
- `docs/SWARMBOOK_ARCHITECTURE.md`
### Behavior changed
- Added implementation blueprint only (no runtime code path change).
### Tests added
- None tied directly to architecture doc.
### Known gaps
- Architecture intent was documented, but continuity/status docs were not created at that time.

## Phase 3 (Configuration Skeleton)
### Files
- `configs/book_sim/model_routes.yaml`
- `configs/book_sim/privacy_modes.yaml`
- `configs/book_sim/reader_archetypes.yaml`
- `configs/book_sim/platform_styles.yaml`
- `configs/book_sim/scoring_weights.yaml`
- `configs/book_sim/evidence_pack_schema.yaml`
### Behavior changed
- Introduced declarative Swarmbook config surface for routes, privacy, archetypes, platform outputs, scoring, and schemas.
### Tests added
- Covered indirectly by router config-loading tests.
### Known gaps
- Configs are not yet consumed by a full end-to-end Swarmbook runtime pipeline.

## Phase 4 (Provider Router Foundation)
### Files
- `backend/app/book_sim/config_loader.py`
- `backend/app/book_sim/provider_router.py`
- `backend/app/book_sim/providers/base.py`
- `backend/app/book_sim/providers/ollama_provider.py`
- `backend/app/book_sim/providers/gemini_provider.py`
- `backend/app/book_sim/providers/nvidia_provider.py`
- `backend/tests/test_book_sim_provider_router.py`
- `.env.example` (optional provider env vars)
- `backend/pyproject.toml`, `backend/requirements.txt` (PyYAML support)
### Behavior changed
- Added additive model-router path for Ollama/Gemini/NVIDIA with privacy-aware route selection and health checks.
### Tests added
- Config loading, route selection, missing-key fallback, `local_only` fallback behavior.
### Known gaps
- Router not yet wired into existing app simulation/report/graph entry points.

## Phase 5 (Typed Schemas)
### Files
- `backend/app/book_sim/models.py`
- `backend/tests/test_book_sim_models.py`
### Behavior changed
- Added typed Swarmbook data model layer with JSON serialization/deserialization.
### Tests added
- Round-trip serialization tests for all declared models.
### Known gaps
- Models are not yet fully exercised through API/UI end-to-end flow.

## Phase 6 (Manuscript Ingest + Evidence Packs)
### Files
- `backend/app/book_sim/manuscript_chunker.py`
- `backend/app/book_sim/book_dna_extractor.py`
- `backend/app/book_sim/style_analyzer.py`
- `backend/app/book_sim/risk_detector.py`
- `backend/app/book_sim/nonfiction_claim_extractor.py`
- `backend/app/book_sim/character_mapper.py`
- `backend/app/book_sim/evidence_pack_builder.py`
- `backend/app/book_sim/local_cache.py`
- `backend/tests/test_book_sim_evidence_pack_builder.py`
- `backend/tests/fixtures/book_sim_fiction_sample.txt`
- `backend/tests/fixtures/book_sim_nonfiction_sample.txt`
### Behavior changed
- Added additive manuscript-to-evidence-pack pipeline with chapter detection, book type detection, optional router-backed synthesis, and content-hash caching.
### Tests added
- Fixture-based fiction/non-fiction evidence-pack generation tests with cache behavior checks.
### Known gaps
- No Swarmbook API endpoint or frontend route currently executes this pipeline.
- Privacy enforcement is stage-local (router-level), not yet global policy enforcement.

## Continuity Recovery Pass (Current)
### Files
- `AGENTS.md`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_PROMPT_LOG.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No production behavior changes; documentation-only continuity reconstruction.
### Tests added
- None (documentation pass).
### Known gaps
- Historical phase execution timestamps before commit `08a3a7e` remain partially reconstructed.

## Phase 7 (Book Graph Integration)
### Files
- `backend/app/book_sim/graph_persistence.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_graph_persistence.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Added additive Swarmbook graph persistence with namespace-scoped, idempotent Neo4j upserts.
- Added dry-run fallback when Neo4j is unavailable.
- Persisted evidence-pack nodes for Book, Draft, Chapter, Character, Theme, Claim, Evidence, Risk, StyleSignal, and MarketSurface.
- Prepared simulation-artifact persistence for ReaderPersona, PrivateReaction, PlatformPost, CrossReaction, and Report without enabling platform adapters.
### Tests added
- Dry-run namespace test.
- Neo4j write-shape test using a fake driver/session.
- Simulation artifact persistence test.
### Known gaps
- No Flask route wiring yet for the new persistence service.
- No reader persona or platform adapter runtime was introduced in this phase.

## Phase 7 Audit
### Files
- `docs/SWARMBOOK_PHASE_STATUS.md`
### Behavior changed
- Confirmed the Phase 7 persistence layer is additive, namespaced, idempotent, and dry-run capable.
- Confirmed legacy MiroFish graph behavior remains in place.
### Tests added
- None. Audit relied on existing Phase 7 tests and code inspection.
### Known gaps
- Phase 8 is not safe yet because the persistence service is not wired into any runtime/API entry point.

## Phase 9 (Reader Archetypes + Persona Generation)
### Files
- `backend/app/book_sim/models.py`
- `backend/app/book_sim/reader_archetype_loader.py`
- `backend/app/book_sim/reader_persona_generator.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_reader_persona_generator.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Added archetype loading from `configs/book_sim/reader_archetypes.yaml` with normalized weights, book-type suitability, and privacy constraints.
- Added deterministic persona generation with seed support, privacy-mode-aware default counts, and override support.
- Kept persona creation template-first; optional LLM enrichment remains off by default and respects privacy mode routing.
### Tests added
- Archetype loader normalization test.
- Deterministic same-seed persona generation test.
- Local-only persona count/privacy constraint test.
- Override and filtering test.
- Optional LLM enrichment stays unused by default test.
### Known gaps
- Persona generation is not yet wired into the Swarmbook simulation runner or API routes.
- Optional LLM enrichment is implemented but not yet covered by a route-selection-specific integration test.

## Phase 9 Audit
### Files
- `docs/SWARMBOOK_PHASE_STATUS.md`
### Behavior changed
- Confirmed reader archetypes load from config and persona generation remains deterministic with a fixed seed.
- Confirmed `local_only` uses a smaller default cohort than `hybrid_safe`.
- Confirmed persona outputs include the required audience-shaping fields and remain simulation-only.
### Tests added
- None. Audit relied on existing unit tests and code inspection.
### Known gaps
- Persona generation is still not wired into a Swarmbook API route or simulation runner, so the next phase should not assume end-to-end runtime readiness.

## Phase 10 Audit
### Files
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Confirmed no `backend/app/book_sim/platform_adapters/` package exists yet.
- Confirmed `platform_styles.yaml` is the only platform-style source currently present for the next phase.
- Confirmed there are no real scraping or platform API calls in the current repository state.
### Tests added
- None. Audit relied on repository inspection.
### Known gaps
- Phase 10 remains not safe because the adapter layer does not exist yet.

## Phase 10-11 (Platform Adapters + Simulation Engine)
### Files
- `backend/app/book_sim/models.py`
- `backend/app/book_sim/platform_adapters/__init__.py`
- `backend/app/book_sim/platform_adapters/base.py`
- `backend/app/book_sim/platform_adapters/goodreads.py`
- `backend/app/book_sim/platform_adapters/booktok.py`
- `backend/app/book_sim/platform_adapters/reddit.py`
- `backend/app/book_sim/platform_adapters/bookstagram.py`
- `backend/app/book_sim/platform_adapters/x_platform.py`
- `backend/app/book_sim/platform_adapters/newsletter.py`
- `backend/app/book_sim/platform_adapters/bookclub.py`
- `backend/app/book_sim/simulation/__init__.py`
- `backend/app/book_sim/simulation/private_reading_pass.py`
- `backend/app/book_sim/simulation/platform_reaction_pass.py`
- `backend/app/book_sim/simulation/cross_reaction_pass.py`
- `backend/app/book_sim/simulation/simulation_orchestrator.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_models.py`
- `backend/tests/test_book_sim_platform_adapters.py`
- `backend/tests/test_book_sim_simulation_engine.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added fully synthetic platform adapters driven by `platform_styles.yaml` with structured `PlatformPost` payloads and evidence references.
- Added private-reading, platform-reaction, and bounded cross-reaction passes plus a simulation orchestrator that returns `SimulationRun`.
- Added content-hash caching for every simulation stage, including the orchestrator result.
- Kept the default execution single-threaded to avoid local CPU and memory overcommit.
### Tests added
- Shared adapter suite covering every required platform adapter.
- Tiny end-to-end simulation test with five personas and deterministic seed.
- Extended model round-trip coverage for structured post payloads and simulation artifact lists.
### Known gaps
- Simulation runtime is still not wired into Swarmbook Flask/API routes or frontend flows.
- The simulation engine depends on synthetic heuristics today; no scoring engine or report synthesis layer is attached yet.

## Phase 12 (Scoring Layer)
### Files
- `backend/app/book_sim/scoring/__init__.py`
- `backend/app/book_sim/scoring/_shared.py`
- `backend/app/book_sim/scoring/rating_distribution.py`
- `backend/app/book_sim/scoring/dnf_score.py`
- `backend/app/book_sim/scoring/viral_score.py`
- `backend/app/book_sim/scoring/controversy_score.py`
- `backend/app/book_sim/scoring/quoteability_score.py`
- `backend/app/book_sim/scoring/polarization_score.py`
- `backend/app/book_sim/scoring/revision_priority.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_scoring.py`
### Behavior changed
- Added deterministic, explainable scoring for predicted rating distribution, DNF risk, DNF chapter pressure, viral potential, controversy, quoteability, polarization, and revision priority.
- Added confidence bands and evidence references to every score result.
- Added a local fallback parser for `scoring_weights.yaml` so scoring remains usable when `PyYAML` is unavailable.
### Tests added
- One shared scoring suite covering each score function plus deterministic same-input replay.
### Known gaps
- Scoring is implemented but still not wired into any Flask route or report generator.

## Phase 12 Audit Refresh
### Files
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Confirmed the scoring layer is complete at the module level and remains deterministic, explainable, and config-driven.
- Confirmed score outputs include confidence bands and evidence references across the scoring package.
- Corrected the handoff resume point so the next fresh thread starts at Phase 13 rather than the already-complete Phase 12.
### Tests added
- None. Audit relied on existing scoring tests and code inspection.
### Known gaps
- Report generation and API/runtime wiring are still pending.

## Phase 7 Runtime Wiring + Phase 13 Runtime Report Slice
### Files
- `backend/app/api/book_sim.py`
- `backend/app/book_sim/runtime_store.py`
- `backend/app/book_sim/report_builder.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_api.py`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added additive backend endpoints for `/api/book-sim/projects`, `/api/book-sim/evidence-packs`, `/api/book-sim/simulate`, `/api/book-sim/projects/{project_id}/report`, `/api/book-sim/personas/{persona_id}/chat`, `/api/book-sim/compare`, and `/api/book-sim/health`.
- Added a file-backed Swarmbook runtime store so evidence packs, simulation runs, reports, and comparisons can be loaded by stored IDs instead of only oversized inline payloads.
- Added deterministic runtime report synthesis on top of existing simulation and scoring outputs, while preserving the legacy `/api/report` flow.
- Kept `/api/book-sim/interrogate` as a backward-compatible narrow route.
### Tests added
- New backend route suite in `backend/tests/test_book_sim_api.py`.
### Known gaps
- There is still no dedicated `backend/app/book_sim/reports/` package.
- Frontend Swarmbook routes/views are still absent.
- Privacy enforcement is still router-scoped rather than system-wide middleware.

## Phase 14 (Reader Persona Interrogation)
### Files
- `backend/app/book_sim/interrogation/__init__.py`
- `backend/app/book_sim/interrogation/persona_chat.py`
- `backend/app/book_sim/__init__.py`
- `backend/app/api/book_sim.py`
- `backend/app/api/__init__.py`
- `backend/app/__init__.py`
- `backend/tests/test_book_sim_persona_chat.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added an additive reader-persona interrogation service that answers six grounded question shapes from serialized Swarmbook artifacts.
- Kept interrogation template-first and deterministic so `local_only` never depends on Gemini, NVIDIA, or any external provider.
- Added a narrow `/api/book-sim/interrogate` backend route that accepts `SimulationRun` plus `EvidencePack` payloads and returns structured JSON with `based_on` evidence refs.
### Tests added
- New unit suite for grounded persona interrogation behavior.
- Route contract test added and conditionally skipped when Flask is unavailable in the active Python environment.
### Known gaps
- Frontend Swarmbook interrogation flow is still absent.
- No frontend Swarmbook interrogation flow exists yet.
- Report synthesis remains absent, so Phase 13 is still open.

## Phase 14 Audit Refresh
### Files
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was an audit and continuity-correction pass.
- Confirmed the interrogation slice is grounded, additive, and provider-free in `local_only`.
- Corrected stale continuity text that still claimed no `book_sim` blueprint or interrogation API existed.
### Tests added
- None. Audit reused the existing interrogation and router test suites.
### Known gaps
- The backward-compatible `/api/book-sim/interrogate` route still accepts oversized serialized payloads for older callers.
- The route contract test remains environment-dependent because `flask` is unavailable in the active Python interpreter here.
- Phase 14 is only safe at the bounded backend-runtime level, not as a fully wired runtime phase.

## Phase 15 (Draft Comparison)
### Files
- `backend/app/book_sim/comparison/__init__.py`
- `backend/app/book_sim/comparison/draft_comparator.py`
- `backend/app/book_sim/comparison/comparison_report.py`
- `backend/app/book_sim/models.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_draft_comparator.py`
- `backend/tests/test_book_sim_models.py`
- `backend/tests/fixtures/book_sim_compare_draft_a.txt`
- `backend/tests/fixtures/book_sim_compare_draft_b.txt`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added an additive draft-comparison module that compares two evidence packs plus optional simulation runs and optional precomputed scorecards.
- Added deterministic JSON and Markdown exports for comparison results.
- Added comparison coverage for book DNA, chapters, characters, claims, DNF/rating/controversy/viral/quoteability movement, reader segment movement, revision impact, improvements, regressions, and remaining blockers.
### Tests added
- New draft comparator unit suite using two tiny draft fixtures.
- Expanded model round-trip coverage for the richer `DraftComparisonReport`.
### Known gaps
- No frontend comparison flow exists yet.
- Phase 13 still lacks a dedicated report package, so the clean sequential path is now "finish and harden Phase 13" rather than "start from zero".

## Phase 16 (Frontend Swarmbook UI)
### Files
- `frontend/src/api/bookSim.js`
- `frontend/src/store/swarmbookSession.js`
- `frontend/src/components/swarmbook/SwarmbookLayout.vue`
- `frontend/src/router/index.js`
- `frontend/src/views/Home.vue`
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `frontend/src/views/swarmbook/SwarmbookMetadataView.vue`
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/SwarmbookReportView.vue`
- `frontend/src/views/swarmbook/SwarmbookPersonasView.vue`
- `frontend/src/views/swarmbook/SwarmbookCompareView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added an additive Swarmbook frontend flow under `/swarmbook/*` for project setup, manuscript input, metadata capture, evidence preview, simulation controls, report review, persona interrogation, and draft comparison.
- Kept the legacy MiroFish landing, process, simulation, report, and interaction routes intact.
- Added simple loading and error handling states across the new Swarmbook screens.
- Bound the new frontend flow to the existing additive `/api/book-sim/*` backend runtime surface.
### Tests added
- No frontend test framework exists in this repo today.
- Attempted frontend validation through `npm run build`, but the machine-level `npm` shim is broken.
- Verified frontend build succeeds through bundled runtime Node with direct Vite execution.
### Known gaps
- Frontend package-manager path is still broken for `npm run build`, so direct runtime-node Vite invocation remains the current workaround.
- The backend report layer still lives in `backend/app/book_sim/report_builder.py`, not a dedicated `reports/` package.

## Deep Consolidation (Post-Phase 12)
### Files
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was a continuity and wiring audit pass only.
- Corrected stale assumptions by confirming that phases 8-12 are module-complete while phase 7 API wiring is still not started.
- Confirmed no report-generation package exists yet under `backend/app/book_sim/reports/`, so JSON/Markdown report outputs are not available.
- Confirmed Swarmbook unit suites currently pass (`28` run, `1` skipped) in this environment.
### Tests added
- None. Consolidation reused existing test suites.
### Known gaps
- End-to-end Swarmbook runtime now exists at the backend route level, but the frontend remains unwired.
- Privacy guarantees are still router-scoped and not yet enforced through global policy middleware.
## Phase 10 Audit Refresh
- Audited the bounded Swarmbook simulation engine after implementation.
- Confirmed the private-reading -> platform-reaction -> cross-reaction flow, deterministic seed behavior, content-hash caching, structured JSON outputs, and low-resource defaults (`cross_reaction_posts=8`, `max_reaction_rounds=2`, `max_parallel_jobs=1`).
- Confirmed test coverage for a tiny evidence pack with a `5`-persona run in `backend/tests/test_book_sim_simulation_engine.py`.
- Recorded that Phase 11 is safe at the module level, with API/UI runtime wiring still pending.

## Phase 17 Audit (Local Low-Resource Profile)
### Files
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was an audit-only continuity update.
- Confirmed required Phase 17 artifacts are currently missing: `configs/book_sim/local_profiles.yaml` and `docs/SWARMBOOK_LOCAL_SETUP.md`.
- Confirmed profile requirements cannot be satisfied until those files are implemented (`local_tiny`, `hybrid_safe_default` default selection, `cloud_quality`, profile-level `local_parallel_jobs`, and heavy-profile warnings).
- Confirmed `local_only` still enforces local provider routing and does not call external providers via the existing router guard.
### Tests added
- None. Audit relied on repository inspection.
### Known gaps
- Phase 17 deliverables are incomplete.
- Phase 18 is not safe until Phase 17 profile config and setup documentation are implemented and verified.

## Phase 17 Repair (Local Low-Resource Profile)
### Files
- `configs/book_sim/local_profiles.yaml`
- `backend/app/book_sim/local_profiles.py`
- `backend/app/book_sim/__init__.py`
- `backend/app/api/book_sim.py`
- `backend/tests/test_book_sim_local_profiles.py`
- `backend/tests/test_book_sim_api.py`
- `frontend/src/store/swarmbookSession.js`
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `frontend/src/views/swarmbook/SwarmbookMetadataView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `docs/SWARMBOOK_LOCAL_SETUP.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
- `docs/SWARMBOOK_PROMPT_LOG.md`
### Behavior changed
- Added explicit local profile config with `local_tiny`, `hybrid_safe_default` (default), and `cloud_quality`.
- Added additive local profile loader with required-field validation and graceful fallback behavior.
- Wired profile defaults into additive `/api/book-sim/projects`, `/api/book-sim/simulate`, and `/api/book-sim/health`.
- Added structured heavy/privacy warnings for profile selection in backend health/profile payloads.
- Kept `local_only` provider guard unchanged; it still forces local route selection.
- Added frontend profile selection/warning visibility in existing Swarmbook home/simulation screens without changing legacy MiroFish routes.
### Tests added
- New loader/config tests in `backend/tests/test_book_sim_local_profiles.py`.
- Extended API health/default-profile assertions in `backend/tests/test_book_sim_api.py`.
### Known gaps
- `pytest` command is unavailable in the current environment (`pytest` CLI missing).
- `npm run build` remains blocked by machine-level npm shim; direct Vite build passes.
