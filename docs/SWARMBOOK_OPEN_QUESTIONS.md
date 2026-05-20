# Swarmbook Open Questions

## Wiring and Runtime
1. Is the provider router fully wired into runtime flows?
- Current answer: Partially. Router selection and provider health now participate in the additive `/api/book-sim/*` runtime path, but enforcement is still not global across every future API boundary.

2. Is `local_only` privacy mode fully enforced end-to-end?
- Current answer: Partially. Router-level selection forces local route, but there is no global policy boundary across all future stages/APIs.

3. Are evidence-pack outputs cached?
- Current answer: Yes, via `LocalArtifactCache` keyed by content hash in `EvidencePackBuilder`.
- Open point: cache invalidation/versioning strategy is minimal.

4. Do tests actually pass in this environment?
- Current answer: Yes for the validated local paths. `compileall`, Swarmbook `unittest` discovery, the tiny local-only E2E test, and direct Vite build pass; `pytest`, Flask API smoke, and npm remain blocked by missing/broken local tooling.

5. Are backend Swarmbook APIs exposed?
- Current answer: Yes at the bounded backend-runtime level. `/api/book-sim/*` now exposes project creation, evidence-pack ingest, simulate-plus-report, latest report retrieval, persona chat, draft comparison, health, and backward-compatible interrogation.

6. Is UI wired for Swarmbook?
- Current answer: Partially. Swarmbook routes/views now exist under `frontend/src/router/index.js` and `frontend/src/views/swarmbook/*`.
- Phase 16 safety: Partially. The frontend flow exists and direct Vite build passes, but default `npm run build` still fails due to a broken machine-level npm shim.

7. Does graph persistence exist for Swarmbook evidence/simulation artifacts?
- Current answer: Yes. The additive graph-persistence layer exists and is now called from the backend evidence-pack and simulate runtime routes, with dry-run fallback when Neo4j is unavailable.

8. Does draft comparison exist for Swarmbook?
- Current answer: Yes. It now exists as a backend module, a backend route with stored-artifact lookup, and a frontend comparison screen, but the frontend has not been build-validated in this environment yet.

## Scope/Design Clarifications
9. Should Swarmbook phases continue with standalone API namespace (`/api/book-sim/*`) or extend existing simulation endpoints?
10. What is the minimum enforceable redaction policy for `hybrid_safe` before any cloud call?
11. What artifacts should be persisted to Neo4j versus file-based JSON only in early phases?
12. Which quality bar gates Phase 7 (hardening): unit tests only, or also local integration test plus manual UI walkthrough?

## Consolidation Follow-ups
13. Should phase status distinguish "module complete" vs "runtime wired" explicitly in every phase row?
- Current answer: Yes. Consolidation now uses that convention for phases 8-12.

14. Do Swarmbook JSON/Markdown report generators exist?
- Current answer: Partially. Runtime report synthesis exists in `backend/app/book_sim/report_builder.py`, but a dedicated `backend/app/book_sim/reports/` package is still missing.

15. Is Phase 13 safe to start?
- Current answer: Phase 13 is already partially in progress through the runtime report helper. The next safe work is to harden and package it cleanly rather than starting from zero.

16. Are any phase docs currently stale?
- Current answer: Not after this continuity pass, assuming the docs stay aligned with the new backend runtime routes.

17. Is Phase 17 local low-resource profile implementation complete?
- Current answer: Yes. `configs/book_sim/local_profiles.yaml`, `backend/app/book_sim/local_profiles.py`, profile-aware API wiring, warnings, tests, and `docs/SWARMBOOK_LOCAL_SETUP.md` now exist.
- Caveat: `pytest` CLI is unavailable and `npm run build` remains blocked by the machine npm shim in this environment; validation used `unittest` plus direct Vite build.

18. Is Phase 19 safe?
- Current answer: Partially. Tiny local-only E2E validation passes and no real social/API usage was found, but Swarmbook still relies on router-scoped `local_only` privacy enforcement; there is no global middleware-level boundary yet.
- Related note: API smoke through Flask remains environment-blocked because Flask is unavailable in this interpreter.

19. Is Phase 20 packaging safe?
- Current answer: No. Direct Vite build passes, but npm is broken in this environment and privacy hardening is still router-scoped rather than a global policy.
