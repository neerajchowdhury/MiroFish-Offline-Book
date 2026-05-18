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
| 14. Persona interrogation (book_sim path) | partially_done | `backend/app/book_sim/interrogation/persona_chat.py` plus `/api/book-sim/personas/{persona_id}/chat` and `/api/book-sim/interrogate` answer grounded reader questions from stored or explicit Swarmbook artifacts. | Backend slice is runtime-wired, but no frontend interrogation flow exists yet. |
| 15. Draft comparison (book_sim path) | partially_done | `backend/app/book_sim/comparison/*` plus `/api/book-sim/compare` compare evidence packs, optional simulations, and optional scores, exporting JSON and Markdown with tests. | Backend slice is runtime-wired, but no frontend comparison flow exists yet. |
| 16. Frontend Swarmbook UI/routes | not_started | No Swarmbook route in `frontend/src/router/index.js`. | Pending frontend slice. Not safe yet because the backend runtime exists but there is still no frontend delivery path. |
| 17. Artifact persistence/replay hardening | partially_done | `LocalArtifactCache` exists with content-hash JSON caching; Swarmbook graph persistence now adds namespace-isolated upserts. | No versioned invalidation/replay controls yet. |
| 18. Test coverage hardening | partially_done | Unit tests for router/models/evidence builder plus smoke script. | No CI proof here; runtime integration tests not present. |
| 19. Privacy/compliance enforcement hardening | partially_done | Router forces local provider when `privacy_mode=local_only`. | No global policy enforcement across all future stages/API boundaries yet. |
| 20. Release readiness for Swarmbook path | not_started | No end-to-end book_sim API/UI run path available yet. | Should follow Phases 9-19 completion. |

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
- Phase 14 is safe at the bounded backend-runtime level, but not safe to call fully complete because frontend wiring is still absent.

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
- Phase 15 is safe at the bounded backend-runtime level, but not safe to call fully complete because frontend wiring is still absent.

## Consolidation Audit (After Phase 12)
- Phase 7 is now done at the backend-route level because the additive `book_sim` blueprint exposes the full runtime surface.
- Phases 8-12 are truly done at module level and tested.
- No `backend/app/book_sim/reports/` package exists yet, so report synthesis currently lives in a runtime helper rather than a dedicated report package.
- `local_only` route enforcement is present in `BookSimProviderRouter.select_route`, but enforcement is still router-scoped rather than app-wide policy middleware.
- Evidence references are preserved through evidence pack, simulation artifacts, scoring outputs, report synthesis, and interrogation responses.
