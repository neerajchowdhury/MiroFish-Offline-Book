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
| 8. Book graph persistence integration | not_started | No dedicated book graph service wired to existing graph storage path. | Pending graph integration stage. |
| 9. Reader cohort/persona generator runtime | not_started | Models/config exist, but no runtime persona factory service exposed. | Pending implementation. |
| 10. Platform-style reaction generator | not_started | Platform style config exists only. | Pending service implementation. |
| 11. Cross-reader reaction loop | not_started | `CrossReaction` model exists only. | Pending service/runtime implementation. |
| 12. Scoring engine | not_started | `scoring_weights.yaml` exists only. | Pending executable scoring module. |
| 13. Prediction report (book_sim path) | not_started | `BookPredictionReport` model exists only. | Existing `/api/report` is legacy simulation path, not Swarmbook-specific flow. |
| 14. Persona interrogation (book_sim path) | not_started | Legacy simulation interview endpoints exist. | No Swarmbook interrogation wiring. |
| 15. Draft comparison (book_sim path) | not_started | `DraftComparisonReport` model exists only. | No comparison service/pipeline wiring. |
| 16. Frontend Swarmbook UI/routes | not_started | No Swarmbook route in `frontend/src/router/index.js`. | Pending frontend slice. |
| 17. Artifact persistence/replay hardening | partially_done | `LocalArtifactCache` exists with content-hash JSON caching. | No versioned invalidation/replay controls yet. |
| 18. Test coverage hardening | partially_done | Unit tests for router/models/evidence builder plus smoke script. | No CI proof here; runtime integration tests not present. |
| 19. Privacy/compliance enforcement hardening | partially_done | Router forces local provider when `privacy_mode=local_only`. | No global policy enforcement across all future stages/API boundaries yet. |
| 20. Release readiness for Swarmbook path | not_started | No end-to-end book_sim API/UI run path available yet. | Should follow Phases 7-19 completion. |
