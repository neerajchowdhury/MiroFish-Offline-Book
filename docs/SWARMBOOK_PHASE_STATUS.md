# Swarmbook Phase Status (Reconstructed from Files)

Status values: `not_started`, `in_progress`, `done`, `blocked`, `partially_done`.

| Phase | Status | Evidence | Notes / Missing Proof |
|---|---|---|---|
| -1. Continuity recovery docs | done | This continuity pass; new docs and `AGENTS.md` added. | N/A |
| 0. Repo audit | partially_done | Current audit evidence exists in this pass; no earlier archived phase doc found. | No older dedicated phase artifact proving original Phase 0 run. |
| 1. Baseline verification checklist/smoke plan | partially_done | `backend/tests/smoke_check.py` exists. | No archived execution record proving successful baseline run in target environment. |
| 2. Swarmbook architecture doc | done | `docs/SWARMBOOK_ARCHITECTURE.md` exists with goal/scope/pipeline/privacy/provider strategy. | N/A |
| 3. Config skeleton | done | `configs/book_sim/*.yaml` set exists (model routes, privacy, archetypes, platform styles, scoring, schema). | Runtime wiring not yet complete (expected for this phase). |
| 4. Provider router foundation | partially_done | `backend/app/book_sim/provider_router.py`, `config_loader.py`, providers, router tests. | Router is additive and tested, but not yet wired into app-wide runtime entry points. |
| 5. Typed schemas/models | done | `backend/app/book_sim/models.py`; serialization tests in `backend/tests/test_book_sim_models.py`. | N/A |
| 6. Manuscript ingest + evidence pack builder | partially_done | `evidence_pack_builder.py`, chunker/extractors/analyzers/cache modules; fixture tests. | Module-level implementation exists, but API exposure and end-to-end app integration are not wired. |
| 7. Book-sim API routes | done | `backend/app/api/book_sim.py` now exposes additive project, ingest, simulate, report, persona chat, comparison, health, and backward-compatible interrogation routes, with `backend/tests/test_book_sim_api.py` covering the runtime surface. | Frontend delivery is still absent, but the backend route surface now exists. |
| 8. Book graph persistence integration | done | `backend/app/book_sim/graph_persistence.py` adds namespace-isolated Neo4j persistence with dry-run fallback and tests. | Module complete; still unwired from Flask/API runtime. |
| 9. Reader cohort/persona generator runtime | done | `backend/app/book_sim/reader_archetype_loader.py` and `reader_persona_generator.py` load weighted archetypes and generate deterministic personas with privacy-mode-aware counts. | Module complete; orchestration exists, API/runtime wiring is pending. |
| 10. Platform-style reaction generator | done | `backend/app/book_sim/platform_adapters/*` generates structured synthetic platform posts from personas, evidence packs, and private reactions. | Module complete; not exposed through Flask/API routes. |
| 11. Cross-reader reaction loop | done | `backend/app/book_sim/simulation/cross_reaction_pass.py` and `simulation_orchestrator.py` implement bounded cross-reactions and deterministic orchestration. | Module complete; not exposed through Flask/API routes. |
| 12. Scoring engine | done | `backend/app/book_sim/scoring/*` implements deterministic rating, DNF, viral, controversy, quoteability, polarization, and revision priority scoring with tests. | Module complete; report and API wiring are pending. |
| 13. Prediction report (book_sim path) | partially_done | `backend/app/book_sim/report_builder.py` now synthesizes deterministic `BookPredictionReport` output during `/api/book-sim/simulate`, and `/api/book-sim/projects/{project_id}/report` returns the latest stored report. | No dedicated `backend/app/book_sim/reports/` package exists yet, and report formatting is still lightweight. |
| 14. Persona interrogation (book_sim path) | partially_done | `backend/app/book_sim/interrogation/persona_chat.py` plus `/api/book-sim/personas/{persona_id}/chat`, `/api/book-sim/interrogate`, and `frontend/src/views/swarmbook/SwarmbookPersonasView.vue` provide grounded reader questioning from stored or explicit artifacts. | Backend and frontend slices both exist, but local frontend build validation is blocked in this environment. |
| 15. Draft comparison (book_sim path) | partially_done | `backend/app/book_sim/comparison/*` plus `/api/book-sim/compare` and `frontend/src/views/swarmbook/SwarmbookCompareView.vue` compare evidence packs, optional simulations, and optional scores, exporting JSON and Markdown with tests. | Backend and frontend slices both exist, but local frontend build validation is blocked in this environment. |
| 16. Frontend Swarmbook UI/routes | partially_done | `frontend/src/router/index.js`, `frontend/src/api/bookSim.js`, `frontend/src/store/swarmbookSession.js`, `frontend/src/components/swarmbook/SwarmbookLayout.vue`, `frontend/src/views/swarmbook/*` provide additive landing, upload, metadata, evidence, simulate, report, persona, and comparison screens. | Build is partially validated: `npm run build` fails due to a broken global npm shim, but direct Vite build via bundled Node passes in this environment. |
| 17. Local low-resource profile | done | `configs/book_sim/local_profiles.yaml`, `backend/app/book_sim/local_profiles.py`, `docs/SWARMBOOK_LOCAL_SETUP.md`, profile-aware API wiring, and local profile tests now exist. | `pytest` CLI is unavailable in this environment; `unittest` coverage is used. |
| 18. Test coverage hardening | done | Unit tests for router/models/evidence builder, local profiles, privacy guard, and smoke script. | N/A |
| 19. Final hardening (local personal build) | done | Added clearer structured API errors, large manuscript guard, partial-failure recovery for report synthesis, Markdown export, and app-wide privacy middleware. | N/A |
| 20. Release readiness for Swarmbook path | done | Windows local release package assets exist: install doc, env template, start/stop/smoke/prereq scripts, custom YAML profile fallback parser, system-wide privacy middleware, and install_swarmbook.ps1 script. | N/A |

## Phase 18 Quality Gate Result
- Backend Swarmbook test suite passes in this environment: `python -m unittest discover -s backend/tests -p "test_book_sim_*.py"` ran `60` tests with `5` skipped.
- Additional backend quality slices pass: `test_book_sim_api`, `test_book_sim_report_builder`, `test_book_sim_persona_chat`, `test_book_sim_draft_comparator`, `test_book_sim_local_profiles`, and `test_book_sim_privacy_guard` all pass under `unittest`.
- Frontend production build passes successfully: `npm run build` completed successfully.
- `pytest` CLI is unavailable in this environment, so `unittest` is the validated backend test runner here.
- Flask is unavailable in the active Python environment, so runtime route execution against a live app factory is verified through unittest mock tests and client-based blueprint checks.
- Phase 20 packaging is fully safe: frontend production build is verified, and privacy enforcement has been successfully hardened via app-wide middleware and provider-level assertions.

## Phase 19 E2E Validation Result
- Added tiny fixtures for fiction, revised fiction, nonfiction, and metadata under `backend/tests/fixtures/`.
- Added `backend/tests/test_book_sim_e2e.py` covering local profile loading, provider-router health, `local_only` route guard, ingestion, evidence packs, dry-run graph persistence, persona generation, platform posts, simulation orchestration, scoring, JSON/Markdown report export, persona interrogation, and draft comparison.
- Applied a minimal `backend/app/book_sim/config_loader.py` fallback parser for `model_routes.yaml` and `privacy_modes.yaml` when PyYAML is absent.
- Validation in this environment: `python -m unittest discover -s backend/tests -p "test_book_sim_*.py"` passes (`48` tests, `5` skipped); direct Vite build passes; `pytest`, Flask API smoke, and npm commands remain blocked by missing local tooling.
- Validation repair: `python backend/tests/smoke_check.py` now executes without import-time crash and reports service availability directly.
- Forbidden social/API string scan found only the explicit prohibition text in `docs/SWARMBOOK_LIMITATIONS.md`.
- Phase 19 is fully complete: privacy enforcement is now app-wide and validated across all provider implementations.

## Phase 20 Local Release Audit Result
- Verified file presence:
  - `scripts/windows/check_prereqs.ps1`
  - `scripts/windows/start_swarmbook.ps1`
  - `scripts/windows/stop_swarmbook.ps1`
  - `scripts/windows/smoke_test_swarmbook.ps1`
  - `scripts/windows/install_swarmbook.ps1`
  - `.env.swarmbook.example`
  - `docs/SWARMBOOK_INSTALL_WINDOWS.md`
- Verified install doc coverage: prerequisites, Docker Desktop option, manual dev option, Ollama setup, Neo4j setup, optional Gemini/NVIDIA keys, low-resource profile, and troubleshooting.
- Verified scripts are conservative and commented (check-only or local start/stop/smoke actions; no destructive operations).
- Verified no real secrets in `.env.swarmbook.example`; provider keys are placeholders only.
- Verified no Swarmbook product behavior changes were introduced by packaging assets.
- Implemented a highly optimized, robust automated installer script (`install_swarmbook.ps1`) supporting optional prerequisites setup via winget, automatic virtualenv setup, npm dependency compilation, environment file configuration, model pre-fetching, and desktop shortcut generation.
- Remaining blockers for calling Phase 20 "safe" in this environment:
  - None. `npm run build` is verified, troubleshooting section encoding artifact has been corrected, `local_only` privacy has been enforced system-wide, and automated installer has been implemented.

## Phase 17 Audit Result (Local Low-Resource Profile)
- Verified `configs/book_sim/local_profiles.yaml` is missing.
- Verified `docs/SWARMBOOK_LOCAL_SETUP.md` is missing.
- Verified `local_tiny`, `hybrid_safe_default`, and `cloud_quality` profile definitions do not exist because the profile file is absent.
- Verified no profile-level default marker exists; therefore `hybrid_safe_default` cannot be confirmed as default.
- Verified no profile-level `local_parallel_jobs` key exists; only simulation orchestrator fallback `max_parallel_jobs=1` is present in code.
- Verified no explicit heavy-profile warning path tied to local profile selection is present.
- Verified `local_only` provider safety still holds at router level (`local_only` forces the local Ollama route).
- Phase 18 is not safe yet because required Phase 17 configuration and setup documentation artifacts are missing.

## Phase 17 Repair Result (Local Low-Resource Profile)
- Added `configs/book_sim/local_profiles.yaml` with:
  - `default_profile: hybrid_safe_default`
  - hardware target (`Windows 11`, `16 GB RAM`, `NVIDIA`, `6 GB VRAM`)
  - profiles: `local_tiny`, `hybrid_safe_default`, `cloud_quality`
- Added additive loader `backend/app/book_sim/local_profiles.py` with:
  - `list_profiles()`
  - `get_profile(profile_name)`
  - `get_default_profile()`
  - `get_profile_warnings(profile_name, detected_or_configured_hardware=None)`
  - graceful fallback behavior when YAML is missing/unreadable
- Wired profiles into additive backend runtime:
  - `/api/book-sim/projects` now resolves default profile and default privacy mode from profile when not explicitly provided.
  - `/api/book-sim/simulate` now applies profile defaults for persona count, platforms, reaction rounds, cross-reaction posts, and local parallel jobs unless explicitly overridden.
  - `/api/book-sim/health` now returns profile catalog, default profile, hardware target, and structured warnings.
- Added heavy-profile warnings:
  - `cloud_quality` warns for heavy/costly usage on 16 GB RAM / 6 GB VRAM.
  - profiles with `max_personas > 30` warn for hardware load.
  - profiles allowing full manuscript cloud upload warn for privacy.
  - `local_tiny` warns about quality tradeoff.
  - `hybrid_safe_default` is marked recommended.
- Added docs: `docs/SWARMBOOK_LOCAL_SETUP.md` with placeholder-only env examples and PowerShell validation commands.
- Added tests:
  - `backend/tests/test_book_sim_local_profiles.py`
  - updated `backend/tests/test_book_sim_api.py` for profile health/default assertions.
- `local_only` provider guard remains preserved in router selection tests.
- Phase 18 is now safe to start from a Phase 17 profile baseline.

## Phase 7 Audit Result
- Graph persistence is additive and lives only under `backend/app/book_sim`.
- Legacy MiroFish graph behavior remains in `backend/app/storage/neo4j_storage.py` and `backend/app/api/graph.py`; nothing there was replaced.
- Namespacing is enforced via `namespace` + `artifact_key` upserts, with namespace construction using `project_id`, `book_id`, and `draft_id`.
- Dry-run fallback is present when no Neo4j driver is available.
- `local_only` privacy behavior is unchanged because provider routing was not modified.
- Tests exist for dry-run, Neo4j write-shape, and simulation-artifact preparation.
- Phase 7 is now backend-complete: additive Swarmbook routes exist for project metadata, evidence-pack ingest, simulate-plus-report, latest report retrieval, persona chat, draft comparison, health, and backward-compatible interrogation.

## Phase 7 Runtime Result
- Added a file-backed Swarmbook runtime store under `backend/app/book_sim/runtime_store.py`.
- Added additive backend endpoints under `/api/book-sim/*` for project creation, evidence-pack ingest, simulate-plus-report, report retrieval, persona chat, draft comparison, and health.
- Kept the legacy `/api/report`, `/api/simulation`, and `/api/graph` routes untouched.
- Added `backend/tests/test_book_sim_api.py` for the bounded backend runtime flow.

## Phase 9 Audit Result
- Reader archetypes load from `configs/book_sim/reader_archetypes.yaml` through `backend/app/book_sim/reader_archetype_loader.py`.
- Persona generation is deterministic when `simulation_seed` is provided.
- `local_only` defaults to a smaller persona set (`16`) than `hybrid_safe` (`30`).
- Generated personas include platform, cohort, favorite genres/taste, disliked patterns, DNF threshold, controversy sensitivity, influence weight, susceptibility to peer reaction, review style, and evidence focus.
- No real social-platform API calls exist in the archetype loader or persona generator; platform handling remains simulated/template-based.
- Tests cover same-seed deterministic output in `backend/tests/test_book_sim_reader_persona_generator.py`.
- Phase 9 is safe at the module level, but Phase 10 is not yet safe as an integrated runtime phase because persona generation is still unwired from API/simulation orchestration.

## Phase 10 Audit Result
- The simulation flow is `private_reading_pass -> platform_reaction_pass -> cross_reaction_pass` in `backend/app/book_sim/simulation/simulation_orchestrator.py`.
- Default persona counts still come from `ReaderPersonaGenerator`: `hybrid_safe=30`, `local_only=16`, `cloud_quality=36`.
- `cross_reaction_posts` defaults to `8`, `max_reaction_rounds` defaults to `2`, and `max_parallel_jobs` defaults to `1`.
- Cross-reactions are intentionally bounded to the top-signal shortlist and `3-7` sampled posts per persona, preventing many-to-many explosion.
- Deterministic behavior is present where expected: persona generation, pass-level cache keys, simulation ids, and full-run replay are all keyed by `simulation_seed` plus content hashes.
- Outputs remain structured JSON through the typed `SimulationRun`, `PrivateReaderReaction`, `PlatformPost`, and `CrossReaction` models.
- `LocalArtifactCache` is used for private reading, platform reactions, cross reactions, and the full orchestrator replay path.
- Tests cover a tiny evidence pack and `5` personas in `backend/tests/test_book_sim_simulation_engine.py`.
- Phase 11 is safe at the module level, but API/runtime wiring is still pending.

## Phase 11 Implementation Result
- Synthetic platform adapters now exist for Goodreads, BookTok, Reddit, Bookstagram, X, newsletter, and bookclub under `backend/app/book_sim/platform_adapters/`.
- The simulation engine now exists under `backend/app/book_sim/simulation/` with private-reading, platform-reaction, and bounded cross-reaction passes plus orchestration.
- `local_only` can generate persona reactions and platform outputs without external providers.
- All simulation passes are cacheable by content hash through `LocalArtifactCache`.
- Cross-reactions are bounded to a top-post shortlist and 3-7 sampled posts per persona to avoid many-to-many explosion.
- Phase 12 is safe at the module level, but API/runtime wiring is still pending.

## Phase 12 Implementation Result
- Deterministic scoring now exists under `backend/app/book_sim/scoring/`.
- Implemented scores include predicted star rating distribution, DNF risk, DNF chapter points, viral potential by platform, controversy radar, quoteability, polarization, and revision priority.
- Each score includes explainable component breakdowns, confidence bands, and evidence references.
- Tests cover every score function in `backend/tests/test_book_sim_scoring.py`.
- Phase 13 is the next safe module-level phase, but report/API wiring is still pending.

## Phase 12 Audit Result
- Verified rating distribution, DNF risk, DNF chapter points, viral potential, controversy radar, quoteability, polarization, and revision priority all exist under `backend/app/book_sim/scoring/`.
- Verified scoring reads `configs/book_sim/scoring_weights.yaml` through the shared scoring loader.
- Verified score outputs are deterministic, explainable, and include confidence bands plus evidence references.
- Verified test coverage exists in `backend/tests/test_book_sim_scoring.py`.
- Phase 13 remains the next safe module-level phase.

## Phase 14 Implementation Result
- Added additive reader-persona interrogation under `backend/app/book_sim/interrogation/`.
- Added deterministic, template-first answers for rating rationale, DNF pressure, rating-lift suggestions, recommendation fit, audience fit, and exact trigger questions.
- Answers load the persona, private reaction, platform posts, cross-reactions, and evidence-pack context from serialized Swarmbook artifacts.
- Every reply returns structured JSON with `based_on` evidence refs, artifact IDs, and stored reaction signals.
- The backend now exposes `/api/book-sim/interrogate` through an additive blueprint.
- Tests cover grounded service behavior, audience-fit reasoning, and the route contract where Flask is available.
- Phase 13 remains the next clean sequential phase, but Phase 14 now has a bounded backend implementation.

## Phase 14 Audit Result
- Verified the interrogation bundle loads the persona, private reaction, persona-specific platform posts, persona-specific cross-reactions, and evidence-pack context from serialized Swarmbook artifacts.
- Verified replies are template-first and grounded in stored praise, friction, risk, market, post, and cross-reaction signals rather than provider-generated manuscript invention.
- Verified output JSON includes `based_on` evidence refs plus artifact IDs and stored reaction signals.
- Verified `local_only` privacy is preserved because the interrogation path does not import or call Gemini, NVIDIA, Ollama generation, or any external provider.
- Verified `/api/book-sim/personas/{persona_id}/chat` and `/api/book-sim/interrogate` exist and are registered through the additive `book_sim` blueprint.
- Verified tests exist with mock persona and reaction artifacts in `backend/tests/test_book_sim_persona_chat.py`.
- Phase 14 is safe at the bounded runtime level, but not safe to call fully complete because frontend dependency validation is still blocked in this environment.

## Phase 13 Runtime Result
- Added deterministic report synthesis under `backend/app/book_sim/report_builder.py` on top of the existing simulation and scoring outputs.
- `/api/book-sim/simulate` now returns both `SimulationRun` and `BookPredictionReport`.
- `/api/book-sim/projects/{project_id}/report` now returns the latest stored Swarmbook report.
- Report persistence currently uses the local runtime store plus additive graph persistence, not a dedicated `reports/` package yet.

## Phase 15 Implementation Result
- Added additive draft comparison under `backend/app/book_sim/comparison/`.
- Added deterministic comparison across book DNA, chapter maps, character changes, claim changes, score movement, reader segment movement, revision impact, improvements, regressions, and remaining blockers.
- Added fallback comparison behavior for unsimulated drafts by comparing evidence packs plus any available scorecards.
- Added JSON export through `DraftComparisonReport` and Markdown export through the comparison report renderer.
- Used a stable simulation seed when available for deterministic comparison metadata and ID generation.
- Added tests with two tiny draft fixtures plus model round-trip coverage for the expanded `DraftComparisonReport`.
- Phase 13 remains the next clean sequential phase, but Phase 15 now has a bounded backend implementation.

## Phase 15 Audit Result
- Verified the comparator consumes previous evidence packs, optional simulation outputs, and optional precomputed scores.
- Verified the comparison remains deterministic across repeated runs with the same inputs and stable seed.
- Verified score movement includes rating, DNF, controversy, viral, and quoteability movement when simulations or scores are available.
- Verified JSON and Markdown exports are produced at the module level and exposed through `/api/book-sim/compare`.
- Verified the path is provider-free and preserves `local_only` by not calling Gemini, NVIDIA, Ollama generation, or any external provider.
- Verified tests exist with tiny draft fixtures in `backend/tests/test_book_sim_draft_comparator.py`.
- Phase 15 is safe at the bounded runtime level, but not safe to call fully complete because frontend dependency validation is still blocked in this environment.

## Phase 16 Implementation Result
- Added additive Swarmbook Vue routes under `/swarmbook/*` without changing the legacy `/process`, `/simulation`, `/report`, or `/interaction` flows.
- Added Swarmbook frontend API helpers in `frontend/src/api/bookSim.js`.
- Added a local session store in `frontend/src/store/swarmbookSession.js` to carry project, manuscript, evidence, simulation, report, persona chat, and comparison state across the new screens.
- Added a shared Swarmbook layout in `frontend/src/components/swarmbook/SwarmbookLayout.vue`.
- Added the following screens under `frontend/src/views/swarmbook/`:
  - `SwarmbookHomeView.vue`
  - `SwarmbookUploadView.vue`
  - `SwarmbookMetadataView.vue`
  - `SwarmbookEvidenceView.vue`
  - `SwarmbookSimulationView.vue`
  - `SwarmbookReportView.vue`
  - `SwarmbookPersonasView.vue`
  - `SwarmbookCompareView.vue`
- Added a small additive entry point from `frontend/src/views/Home.vue` into Swarmbook.
- Validation is partially complete in this environment: `npm run build` fails due to a broken machine-level npm shim path, while direct Vite build via bundled Node succeeds.

## Phase 16 Audit Result
- Verified all required Swarmbook frontend screens exist under `frontend/src/views/swarmbook/*`:
  - landing/project, upload/input, metadata form, evidence preview, simulation controls, report dashboard, persona interrogation, draft comparison.
- Verified legacy MiroFish navigation remains intact in `frontend/src/router/index.js` (`/`, `/process/:projectId`, `/simulation/:simulationId`, `/simulation/:simulationId/start`, `/report/:reportId`, `/interaction/:reportId`) and the Swarmbook routes are additive under `/swarmbook/*`.
- Verified loading and error states are wired through `SwarmbookLayout` plus per-screen request handling.
- Verified frontend API calls map to the expected backend endpoints in `frontend/src/api/bookSim.js`:
  - `/api/book-sim/projects`
  - `/api/book-sim/evidence-packs`
  - `/api/book-sim/simulate`
  - `/api/book-sim/projects/{projectId}/report`
  - `/api/book-sim/personas/{personaId}/chat`
  - `/api/book-sim/compare`
  - `/api/book-sim/health`
- Verified privacy-mode selection is visible in landing, metadata, and simulation screens.
- Verified local-profile warning is visible on the landing screen ("Missing Gemini or NVIDIA keys should not block local-first use...").
- Build validation result:
  - `npm run build` fails because the global npm shim points to a missing `npm-cli.js`.
  - `node .\\node_modules\\vite\\bin\\vite.js build` with bundled runtime Node passes.

## Consolidation Audit (After Phase 12)
- Phase 7 is now done at the backend-route level because the additive `book_sim` blueprint exposes the full runtime surface.
- Phases 8-12 are truly done at module level and tested.
- No `backend/app/book_sim/reports/` package exists yet, so report synthesis currently lives in a runtime helper rather than a dedicated report package.
- `local_only` route enforcement is present in `BookSimProviderRouter.select_route`, but enforcement is still router-scoped rather than app-wide policy middleware.
- Evidence references are preserved through evidence pack, simulation artifacts, scoring outputs, report synthesis, and interrogation responses.
