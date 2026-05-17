# Swarmbook Open Questions

## Wiring and Runtime
1. Is the provider router fully wired into runtime flows?
- Current answer: No. Router exists under `backend/app/book_sim`, and a narrow Swarmbook interrogation API path is registered, but the router is still not broadly wired into Swarmbook runtime flows.

2. Is `local_only` privacy mode fully enforced end-to-end?
- Current answer: Partially. Router-level selection forces local route, but there is no global policy boundary across all future stages/APIs.

3. Are evidence-pack outputs cached?
- Current answer: Yes, via `LocalArtifactCache` keyed by content hash in `EvidencePackBuilder`.
- Open point: cache invalidation/versioning strategy is minimal.

4. Do tests actually pass in this environment?
- Current answer: Requires explicit execution record per environment. See latest handoff/testing section.

5. Are backend Swarmbook APIs exposed?
- Current answer: Partially. `/api/book-sim/interrogate` exists, but the broader Swarmbook API surface is still absent.

6. Is UI wired for Swarmbook?
- Current answer: No Swarmbook route/view in `frontend/src/router/index.js`.

7. Does graph persistence exist for Swarmbook evidence/simulation artifacts?
- Current answer: Yes at module level (`backend/app/book_sim/graph_persistence.py`), but not wired through Flask runtime routes.

## Scope/Design Clarifications
8. Should Swarmbook phases continue with standalone API namespace (`/api/book-sim/*`) or extend existing simulation endpoints?
9. What is the minimum enforceable redaction policy for `hybrid_safe` before any cloud call?
10. What artifacts should be persisted to Neo4j versus file-based JSON only in early phases?
11. Which quality bar gates Phase 7 (hardening): unit tests only, or also local integration test plus manual UI walkthrough?

## Consolidation Follow-ups
12. Should phase status distinguish "module complete" vs "runtime wired" explicitly in every phase row?
- Current answer: Yes. Consolidation now uses that convention for phases 8-12.

13. Do Swarmbook JSON/Markdown report generators exist?
- Current answer: No. `backend/app/book_sim/reports/` is still missing.

14. Is Phase 13 safe to start?
- Current answer: Yes at module level, and it remains the next clean sequential phase even though Phase 14 now has a bounded backend interrogation slice.

15. Are any phase docs currently stale?
- Current answer: Yes. The context doc needed correction during the Phase 14 interrogation audit because it still claimed no `book_sim` blueprint or interrogation API existed.
