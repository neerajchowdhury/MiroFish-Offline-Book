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
| 7. Book-sim API routes | not_started | No `book_sim` blueprint under `backend/app/api` registration path. | Pending additive route layer. |
| 8. Book graph persistence integration | done | `backend/app/book_sim/graph_persistence.py` adds namespace-isolated Neo4j persistence with dry-run fallback and tests. | API/UI wiring is still pending, but persistence itself is in place. |
| 9. Reader cohort/persona generator runtime | done | `backend/app/book_sim/reader_archetype_loader.py` and `reader_persona_generator.py` load weighted archetypes and generate deterministic personas with privacy-mode-aware counts. | Runtime exists but is not yet wired into API/simulation orchestration. |
| 10. Platform-style reaction generator | done | `backend/app/book_sim/platform_adapters/*` generates structured synthetic platform posts from personas, evidence packs, and private reactions. | Runtime exists but is not yet wired into Flask/API routes. |
| 11. Cross-reader reaction loop | done | `backend/app/book_sim/simulation/cross_reaction_pass.py` bounds reactions to top-signal posts and updates reaction state without many-to-many explosion. | Runtime exists but is not yet wired into Flask/API routes. |
| 12. Scoring engine | not_started | `scoring_weights.yaml` exists only. | Pending executable scoring module. |
| 13. Prediction report (book_sim path) | not_started | `BookPredictionReport` model exists only. | Existing `/api/report` is legacy simulation path, not Swarmbook-specific flow. |
| 14. Persona interrogation (book_sim path) | not_started | Legacy simulation interview endpoints exist. | No Swarmbook interrogation wiring. |
| 15. Draft comparison (book_sim path) | not_started | `DraftComparisonReport` model exists only. | No comparison service/pipeline wiring. |
| 16. Frontend Swarmbook UI/routes | not_started | No Swarmbook route in `frontend/src/router/index.js`. | Pending frontend slice. |
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
- Phase 8 is not safe yet because there is still no API/runtime wiring for the new persistence service.

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
