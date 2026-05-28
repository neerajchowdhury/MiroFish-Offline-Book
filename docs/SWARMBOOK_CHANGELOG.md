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

## Phase 19 (Final Hardening Pass: Local Personal Build)
### Files
- `backend/app/api/book_sim.py`
- `backend/app/book_sim/report_markdown.py`
- `frontend/src/api/index.js`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `docs/SWARMBOOK_LOCAL_SETUP.md`
- `docs/SWARMBOOK_USAGE_GUIDE.md`
- `docs/SWARMBOOK_LIMITATIONS.md`
- `backend/tests/test_book_sim_api.py`
### Behavior changed
- Improved Swarmbook API error clarity by returning structured JSON errors with stable `error_code` and optional `details` for runtime/provider failures.
- Guarded large manuscript ingestion (`max_manuscript_chars`, default `500000`) to keep low-resource local runs stable.
- Added partial-failure recovery: simulation artifacts are saved even if report synthesis fails, returning `error_code=partial_failure` with the stored `simulation_id`.
- Added Markdown export for prediction reports and returned it as `report_markdown` from `/api/book-sim/simulate`.
- Improved frontend error surfacing by carrying backend `error_code/details` through the Axios layer.
- Added a visible character-count warning on the Swarmbook upload screen for very large pastes.
### Tests added/updated
- Updated API test expectations to assert `report_markdown` is returned when Flask is available (`backend/tests/test_book_sim_api.py`).
### Known gaps
- Frontend production build is not provable in this environment (missing `node_modules` / npm shim issues).
- Privacy enforcement remains router-scoped (`local_only` forces `local_ollama`), not an app-wide policy boundary.
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

## Phase 18 Quality Gate
### Files
- `backend/tests/test_book_sim_report_builder.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was a validation and continuity-consolidation pass.
- Verified the Swarmbook backend test suite passes in this environment, including the new report-builder coverage.
- Verified the frontend Swarmbook bundle still builds successfully through direct Vite execution.
- Confirmed `npm run build` remains blocked by the local npm shim and `pytest` is unavailable here.
- Confirmed `Flask` is unavailable in the active Python environment, so live app-factory route execution remains unverified in this shell.
### Tests added
- `backend/tests/test_book_sim_report_builder.py`
### Known gaps
- Phase 19 is not safe yet because privacy/compliance hardening still lacks a global policy boundary beyond router-level enforcement.
- The repo still depends on direct Vite build as the frontend validation workaround in this environment.

## Phase 20 Privacy Hardening & Config Fallback (Handoff H hardening)
### Files
- [book_sim.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/api/book_sim.py)
- [gemini_provider.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/providers/gemini_provider.py)
- [nvidia_provider.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/providers/nvidia_provider.py)
- [local_profiles.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/local_profiles.py)
- [SWARMBOOK_INSTALL_WINDOWS.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_INSTALL_WINDOWS.md)
- [test_book_sim_privacy_guard.py](file:///d:/SW/MiroFish-Offline-Book/backend/tests/test_book_sim_privacy_guard.py)
- [test_book_sim_local_profiles.py](file:///d:/SW/MiroFish-Offline-Book/backend/tests/test_book_sim_local_profiles.py)
- [SWARMBOOK_PHASE_STATUS.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_PHASE_STATUS.md)
- [SWARMBOOK_CHANGELOG.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_CHANGELOG.md)
- [SWARMBOOK_DECISIONS.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_DECISIONS.md)
### Behavior changed
- Implemented blueprint-level Flask `before_request` middleware to parse and set the global `PrivacyGuard` mode to `local_only` (or other active mode) on all API requests.
- Added provider-level `PrivacyGuard` assertions to `GeminiProvider` and `NvidiaProvider` methods (`generate_text`, `generate_json`, `embed_text`) to raise `PrivacyViolationError` under `local_only` mode.
- Implemented a custom YAML-free parser in `local_profiles.py` to support loading local profile configurations without PyYAML.
- Fixed typo encoding artifacts (`wonâ€™t`) in `docs/SWARMBOOK_INSTALL_WINDOWS.md`.
### Tests added
- Added provider-level `PrivacyViolationError` tests in `test_book_sim_privacy_guard.py`.
- Added `test_yaml_free_parser_matches_yaml_parser` in `test_book_sim_local_profiles.py` comparing output with PyYAML.


## Phase 19 E2E Validation
### Files
- `backend/app/book_sim/config_loader.py`
- `backend/tests/test_book_sim_e2e.py`
- `backend/tests/fixtures/tiny_fiction_manuscript.txt`
- `backend/tests/fixtures/tiny_fiction_manuscript_revised.txt`
- `backend/tests/fixtures/tiny_nonfiction_manuscript.txt`
- `backend/tests/fixtures/tiny_metadata.json`
- `backend/tests/fixtures/tiny_metadata_nonfiction.json`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added a narrow PyYAML-free fallback parser for existing route/privacy configs so Swarmbook can validate in the active local Python environment.
- No product features were added; the new E2E test uses tiny synthetic fixtures and local-only deterministic runtime paths.
### Tests added/updated
- Added `backend/tests/test_book_sim_e2e.py` for tiny local-only pipeline and draft comparison validation.
### Known gaps
- Flask is unavailable in the active Python interpreter, so Flask test-client API smoke remains skipped.
- `pytest` and npm commands are unavailable/broken in this environment; `unittest` and direct Vite are the validated paths.
- Phase 19 remains partial until privacy enforcement is global rather than router-scoped.

## Phase 19 E2E Validation Repair (Import/Smoke Path)
### Files
- `backend/tests/smoke_check.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- `backend/tests/smoke_check.py` now falls back when `flask`/`python-dotenv` app imports are unavailable, so the smoke command runs and reports actual backend/frontend/Neo4j/Ollama status.
### Tests added/updated
- No new tests; re-ran targeted E2E and smoke commands.
### Known gaps
- Smoke checks can still fail when local services are not running or dependencies like `neo4j` client are not installed; this is runtime/environment, not Swarmbook logic.

## Phase 20 Local Release Audit & Automated Installation Framework (Handoff H packaging)
### Files
- `scripts/windows/check_prereqs.ps1`
- `scripts/windows/start_swarmbook.ps1`
- `scripts/windows/stop_swarmbook.ps1`
- `scripts/windows/smoke_test_swarmbook.ps1`
- `scripts/windows/install_swarmbook.ps1`
- `.env.swarmbook.example`
- `docs/SWARMBOOK_INSTALL_WINDOWS.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Implemented a highly optimized, robust automated installer script (`install_swarmbook.ps1`) supporting optional prerequisites setup via winget, automatic virtualenv setup, npm dependency compilation, environment file configuration, model pre-fetching, and desktop shortcut generation.
- Corrected troubleshooting section encoding artifact in `docs/SWARMBOOK_INSTALL_WINDOWS.md`.
- Enforced `local_only` system-wide via Flask blueprint middleware and provider assertions, rendering release packaging safe.
### Tests added/updated
- Added provider-level `PrivacyViolationError` tests in `test_book_sim_privacy_guard.py` and YAML-free parser fallback test in `test_book_sim_local_profiles.py`.
- Verified 60 out of 60 unit tests pass.
### Known gaps
- None. Prerequisite checking, installation, and system-wide privacy safety are verified.

## Phase 21 (UI Audit and Redesign Plan)
### Files
- `docs/SWARMBOOK_UI_REDESIGN.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- None. This is an audit and redesign documentation phase before making major changes.
### Tests added
- None.
### Known gaps
- Implementations of the redesign screens are scheduled for future phases.

## Phase 22 (SaaS-grade App Shell and Navigation)
### Files
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue`
- `frontend/src/views/swarmbook/*.vue` (8 views updated to import and use the new shell)
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Replaced the simple progress layout with a modern, SaaS-grade `SwarmbookAppShell` containing a top navigation header, exit pathway to the MiroFish landing page, responsive left workflow steps sidebar, persistent health status display for Ollama/Neo4j services, and interactive Settings modal overlay.
- Maintained backwards compatibility and kept original MiroFish landing page and graph processing views unchanged.
### Tests added
- None (verified clean production compile via Vite build command).
### Known gaps
- Settings drawer content is static and profile attributes are loaded from session state.

## Phase 23 (SaaS-grade Swarmbook Project Dashboard)
### Files
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Replaced the simple project creation form on the Swarmbook landing page with a comprehensive, premium, author-facing project dashboard.
- Added an author-facing hero headline ("Predict reader reactions before you publish") and explanation subtext.
- Added primary "New Simulation" and secondary "Open Existing Project" CTAs. Opening an existing project by ID attempts to resolve its latest report, routing directly to the report dashboard if ready, or to the manuscript upload flow as a fallback.
- Implemented localStorage-backed recent project history tracker (`mirofish_swarmbook_projects`), listing details of recently run manuscript stress tests.
- Formulated an author-focused local trust strip explaining privacy guarantees (Local-first, Private mode, No social scraping, Evidence-based reports).
- Created a system readiness panel displaying Ollama, Neo4j, Gemini, and NVIDIA statuses.
- Added quick action shortcuts, including an interactive "Test a Blurb" quick blurb stress test modal that creates a temporary project and routes directly to the evidence pack preview step.
### Tests added
- None (verified clean production compile via Vite build command).
### Known gaps
- "Compare Drafts" quick action shortcut relies on a project already being active in the session state.

## Phase 24 Guided New Simulation Wizard
### Files
- `frontend/src/router/index.js`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue`
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Added `NewSimulationWizardView` implementing a unified 5-step wizard for manuscript stress testing: Basics, Ingest, Evidence pack preview, Cohort configuration, and Run.
- Registered `/swarmbook/wizard/:projectId?` route mapped to the wizard component.
- Updated "New Simulation" header and landing page hero CTA to redirect to the new wizard route.
- Updated "Upload Manuscript" quick action to open the wizard, ensuring step-based setup.
- Enforced low-resource profile safety, character limit banners, active form validations, and keyboard navigation.
### Tests added/updated
- Validated compile sanity via Vite production build.
### Known gaps
- None.

## Phase 25 SaaS-grade Swarmbook Manuscript Upload
### Files
- `backend/app/utils/file_parser.py`
- `backend/app/api/book_sim.py`
- `backend/tests/test_book_sim_api.py`
- `frontend/src/api/bookSim.js`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Added native Word (`.docx`) text extraction to `FileParser` using zipfile and xml parsing.
- Exposed a new `/parse-file` API route for file uploads, returning size in bytes, character/word counts, MIME type, and extracted text.
- Redesigned manuscript upload screen (`SwarmbookUploadView.vue`) and step 2 of the wizard (`NewSimulationWizardView.vue`) to use a premium drag-and-drop file uploader.
- Replaced "Reality Seeds" naming with "Upload Manuscript" across the uploader interface.
- Showed estimated processing time (~30-60s) and privacy warnings in the file card based on selected privacy modes.
- Displayed detailed error messages (unsupported format, parsing failures, upload failures, and file/character limit oversized calculations).
- Showed "Generate Evidence Packs" as the primary next action button instead of generic routing steps.
### Tests added/updated
- Added `test_parse_file_route` in `test_book_sim_api.py` covering TXT uploads, unsupported formats, and character size limits.
- Verified 61 out of 61 unit tests pass.
### Known gaps
- None.

## Phase 26 (SaaS-grade Swarmbook Evidence Pack Review)
### Files
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
### Behavior changed
- Redesigned the Swarmbook Evidence Pack Review view (`SwarmbookEvidenceView.vue`) into a premium, SaaS-grade split-pane dashboard workspace.
- Added 7 narrative and analysis maps: Book DNA, Chapter Map, Character Map, Claim Map, Risk Map, Style Map, and Market Surface.
- Showed card-level metadata for each map including status (pending / generated / needs review / accepted), custom confidence levels, and references counts.
- Implemented card-level controls to view details, regenerate specific maps (triggering `/api/book-sim/evidence-packs` backend compilation), and accept/lock maps.
- Implemented details column on the right showing structured map data (e.g. DNA fields, timeline for chapters, character grid, metric gauges for style, claims, and risks), a "Why This Matters" educational microcopy banner, and editorial annotations text field to record user overrides.
- Supported accessible button labels, keyboard focus outline enhancements (`outline: 2px solid #ff4500` on focus-visible states), and responsive layout collapse.
### Tests added/updated
- Verified production compile of redesigned view through direct Vite compilation.
### Known gaps
- None.

## Phase 27 (SaaS-grade Swarmbook Reader Swarm Setup)
### Files
- `backend/app/api/book_sim.py`
- `backend/tests/test_book_sim_api.py`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
### Behavior changed
- Redesigned the simulation setup screen (`SwarmbookSimulationView.vue`) and Step 4 of the guided wizard (`NewSimulationWizardView.vue`) into a premium, SaaS-grade Reader Swarm Setup dashboard.
- Replaced developer/agent terminology with plain language reader metrics, platform toggles, and cohorts configurations.
- Implemented Simulation Profile selector cards (Draft, Balanced, Deep) with recommendation and hardware warning banners.
- Implemented Reader Count range controller with recommended scale indicators based on selected profile defaults.
- Implemented Platform checklist pill-buttons supporting Goodreads, BookTok, Reddit, Bookstagram, X, Newsletter, and Book Club.
- Implemented interactive Reader Cohorts checklist to toggle Harsh reviewers, Genre loyalists, Emotional amplifiers, Skeptics, Casual readers, Literary readers, and Non-fiction evidence skeptics, mapping unselected cohorts to under-the-hood exclusions.
- Implemented dynamic runtime time estimation and provider connection status matrix (Ollama, Neo4j, Gemini, NVIDIA).
- Extended backend `_persona_overrides` API helper to parse and enforce `exclude_archetypes` and `include_archetypes` parameters from request payload.
### Tests added/updated
- Added `test_simulate_with_cohort_exclusions` in `test_book_sim_api.py` verifying that excluded archetypes are successfully filtered out from generated reader persona swarms.
- Verified 62 out of 62 unit tests pass successfully.
### Known gaps
- None.

## Phase 28 (SaaS-grade Swarmbook Simulation Run Screen)
### Files
- `frontend/src/api/bookSim.js`
- `frontend/src/router/index.js`
- `frontend/src/views/swarmbook/SwarmbookSimulationRunView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
### Behavior changed
- Created a dedicated simulation run view screen (`SwarmbookSimulationRunView.vue`) at route `/swarmbook/project/:projectId/run` with a visual, multi-step progress stepper (7 steps), dynamic progress bar meter, and total run timer.
- Integrated a live terminal console logs feed displaying dynamic simulated milestones representing active pipeline tasks to prevent blank screen stare.
- Equipped control ribbon supporting Cancel action triggers bound to Axios `AbortController` request cancellation and disabled/mock pause and resume buttons.
- Handled error states, displaying a detailed failure message and providing immediate recovery buttons ("Retry Simulation Run" and "Adjust Settings").
- Updated standalone setup screen run button and wizard step 5 run button to redirect to the new runner screen.
- Modified `runBookSimulation` helper inside `bookSim.js` to accept Axios config parameter for Abort signals.
### Tests added/updated
- Verified client environment compile of new views using Vite build.
### Known gaps
- None.

## Phase 29 (SaaS-grade Swarmbook Report Dashboard)
### Files
- `frontend/src/views/swarmbook/SwarmbookReportView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Redesigned and rewrote `SwarmbookReportView.vue` as a premium SaaS-grade report dashboard.
- Implemented 6 top summary cards (Readiness percentage, Star predicted rating, DNF risk, Controversy risk, Max viral platform, and Top priority target).
- Implemented client-side Publishing Readiness score calculation formula blending rating distribution, DNF, and controversy risk.
- Implemented 13 detailed main sections including interactive CSS progress bars/histograms, a reader segments table, timeline DNF chapter timeline, platform virality scores, pull quotes quoteability highlights, tabbed simulated platform posts feed (Goodreads, BookTok, Reddit, X), marketing hooks, risks, caveats, and disclaimers.
- Added fully client-side local JSON and Markdown report export file downloading utilities.
- Implemented mock fallback data loader directly in empty state card to enable offline visual dashboard verification.
- Enforced WCAG 2.2 AA standards with explicit keyboard focus outlines (`2px solid #FF4500`) and aria-labels/roles.
### Tests added/updated
- Verified Vite production build checks run successfully with zero compile warnings.
- Confirmed all 62 python backend unit tests Discover green passes.
### Known gaps
- None.

## Phase 30 (SaaS-grade Swarmbook Persona Interview Screen)
### Files
- `frontend/src/views/swarmbook/SwarmbookPersonasView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Redesigned and rewrote `SwarmbookPersonasView.vue` as a master-detail Persona Interview screen.
- Implemented Left Sidebar directory listing active personas with platform branding, cohort name, predicted rating, and DNF probability statistics.
- Implemented Right Header profile card showing genres, DNF triggers, review style, and influence score.
- Implemented Interactive Chat Workbench displaying a rolling message history with user/persona styles, quick question triggers, and loading state indicators.
- Implemented Grounded Evidence panel cross-referencing active `evidencePack` to lookup and display detailed pacing timelines or claim text.
- Added fully offline fallback roster with 5 mock personas and a local query responder matching the 6 trigger shapes (Rating, DNF, Recommend, Raise, Audience, Triggers) to answer questions when backend or Neo4j/Ollama services are unavailable.
- Enforced WCAG 2.2 AA standards with clear focus outlines (`outline: 2px solid #FF4500`) and aria-labels/roles.
### Tests added/updated
- Verified Vite production build check and confirmed all 62 python backend unit tests Discover green passes.
- None.

## Phase 31 (SaaS-grade Swarmbook Draft Comparison Screen)
### Files
- `frontend/src/views/swarmbook/SwarmbookCompareView.vue`
### Behavior changed
- Redesigned and rewrote `SwarmbookCompareView.vue` as a premium SaaS-grade draft comparison workbench.
- Implemented recent project dropdown lists reading `mirofish_swarmbook_projects` from `localStorage` project history, alongside a toggle to manually enter project IDs.
- Implemented an Executive Delta Scorecard matrix comparing Publishing Readiness scores, predicted mean ratings, DNF abandonment risks, controversy risks, and quoteability metrics side-by-side with color-coded deltas.
- Implemented a 5-tab workspace panel:
  - **Priorities & Verdict**: Executive verdict summary, plus lists of improvements, regressions, publishing blockers, and a recommended revision checklist.
  - **DNA & Segments**: Table of Book DNA adaptations and a cohort rating/stance shift matrix.
  - **Pacing (Chapters)**: Detailed timeline/list of chapter deltas showing title, pacing changes (slow->balanced/fast), friction clearances, and summary shifts.
  - **Characters & Claims**: Fiction cast attachment/role adjustments and nonfiction claim/evidence deltas.
  - **Raw Export & Preview**: File downloaders for comparison JSON/Markdown, with preview area and copy-to-clipboard.
- Added a high-fidelity offline mock dataset comparing original and revised drafts to support offline Visual verify.
- Enforced WCAG 2.2 AA standards with clear focus outlines (`outline: 2px solid #FF4500`) and aria-labels/roles.
### Tests added/updated
- Verified Vite client production build check passes successfully.
- Verified all 62 python backend unit tests remain green.
### Known gaps
- None.

## Phase 32 (SaaS-grade Swarmbook Settings Screen)
### Files
- `frontend/src/views/swarmbook/SwarmbookSettingsView.vue`
- `frontend/src/router/index.js`
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue`
### Behavior changed
- Created a dedicated `SwarmbookSettingsView.vue` component at `/swarmbook/settings/:projectId?`.
- Refactored `SwarmbookAppShell.vue` settings navigation trigger to navigate to the new Settings view, and removed the old settings modal overlay markup.
- Implemented interactive Privacy Mode selection cards (enforcing `local_only`, `hybrid_safe`, `cloud_quality`) with safety warning and data flow explanations.
- Implemented local profile configurations (max personas count, platforms list, reaction loops).
- Implemented model provider key configuration status checks (exposing configured/missing labels with key secret obfuscation).
- Implemented on-demand health diagnostics sweep showing timeline checks and troubleshooting suggestions for Ollama and Neo4j socket connectivity.
- Wired configurations directly to localStorage session store updates.
- Added WCAG 2.2 AA compliant focus states (`outline: 2px solid #FF4500`) and ARIA roles.
### Tests added/updated
- Verified Vite client production build check compiles successfully.
- Verified all 62 python backend unit tests remain green.
### Known gaps
- None.

## Phase 33 (Swarmbook UI Visual Polish Pass)
### Files
- `frontend/src/App.vue`
### Behavior changed
- Injected global theme CSS variables and styling overrides into `App.vue`.
- Standardised typography hierarchy (Space Grotesk headers and JetBrains Mono fonts) across Swarmbook Studio.
- Standardised card layout styling (padding, borders, shadow accents, and hover transitions).
- Refined primary/ghost button sizing, margins, and hover colors.
- Polished table layouts with border-spacing, borders, headers background, and cells padding.
- Refined scrollbars and empty states for comparison views, dashboard listings, and reports.
- Enforced keyboard focus rings (`outline: 2px solid #FF4500; outline-offset: 2px`) globally on all interactive settings, uploader cards, selection tags, wizard steps, and input text areas.
### Tests added/updated
- Verified Vite client production build check compiles successfully.
- Verified all 62 python backend unit tests remain green.
### Known gaps
- None.

## Phase 34 (Swarmbook UI Accessibility and Responsive QA Pass)
### Files
- `frontend/src/App.vue`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`
- `docs/SWARMBOOK_LIMITATIONS.md`
### Behavior changed
- Added spacebar keydown selection listeners to custom interactive cards/elements (drag-and-drop zone, step buttons, simulation profile select cards, evidence map cards) to supplement standard enter keydown behaviors for keyboard/screenreader users.
- Added `aria-live="polite"` attributes to form validation alerts in the guided wizard.
- Scaled primary and ghost buttons to ensure touch target sizes satisfy a minimum of 44px in height.
- Overrode light grey `#94a3b8` text styles globally with the high-contrast slate `--sb-text-muted` (`#64748b`) variable inside the Swarmbook namespace, satisfying WCAG 2.2 AA text contrast compatibility.
- Appended accessibility limitations notes (drag-and-drop keyboard limits, scrolling console live log verbosity, structural tables/lists charts, and small screen boundaries) to `docs/SWARMBOOK_LIMITATIONS.md`.
- Added media query rules and `prefers-reduced-motion: reduce` styling rules to disable transitions and animation behaviors when system motion reduction preferences are active.
### Tests added/updated
- Verified Vite client production build compiles successfully with zero compile warnings.
- Verified all 62 python backend unit tests run successfully.
### Known gaps
- Drag-and-drop file upload actions are not keyboard navigable natively, though fully accessible keyboard browsing fallback is supported.
- Scrolling simulation log feeds can be verbose for screen readers when live alerts are active.

## Phase 35 (Complete 360-Degree Testing Suite Design & Implementation)
### Files
- `docs/SWARMBOOK_TESTING_PLAN.md`
- `backend/tests/test_book_sim_edge_cases.py`
### Behavior changed
- Designed a comprehensive Swarmbook Studio testing strategy, logging automated test metrics and manual QA verification checklists under `docs/SWARMBOOK_TESTING_PLAN.md`.
- Implemented edge-case unit and route integration tests in `backend/tests/test_book_sim_edge_cases.py`. Covered validator bounds (empty strings, out-of-range counts, bad privacy modes), manuscript ingestion boundaries (oversized pasted texts and empty inputs), and platform/interrogation model fallbacks.
- Mocked connection socket failures for Ollama, Neo4j, and Python Flask in diagnostic test suites, asserting health diagnostic timeline endpoints correctly catch SocketErrors and format clean failure payloads instead of raising unhandled server-side crashes.
### Tests added/updated
- Added 11 new automated test scenarios under `backend/tests/test_book_sim_edge_cases.py`.
- Verified all 73 backend unit tests pass successfully.
- Verified client environment compiles cleanly under Vite.
### Known gaps
- None.


