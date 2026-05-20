# Swarmbook Decisions (Reconstructed)

## D-001
- Date: `2026-05-17` (from checkpoint commit `08a3a7e`)
- Decision: Build Swarmbook as additive modules under `backend/app/book_sim` instead of rewriting legacy simulation.
- Rationale: Preserve existing MiroFish-Offline behavior and reduce migration risk.
- Trade-off: Temporary duplicate concepts between legacy simulation and Swarmbook path.
- Files affected: `backend/app/book_sim/*`

## D-002
- Date: `2026-05-17` (reconstructed from files)
- Decision: Keep model routing declarative in YAML (`model_routes.yaml`, `privacy_modes.yaml`).
- Rationale: Provider behavior can be changed without touching runtime code.
- Trade-off: Requires config validation discipline and startup/runtime checks.
- Files affected: `configs/book_sim/model_routes.yaml`, `configs/book_sim/privacy_modes.yaml`, `backend/app/book_sim/config_loader.py`

## D-003
- Date: `2026-05-17` (reconstructed from files)
- Decision: Introduce provider abstraction with a uniform contract (`generate_text`, `generate_json`, `embed_text`, `health_check`).
- Rationale: Keeps Gemini/NVIDIA/Ollama behind a shared interface and avoids hardcoded provider calls.
- Trade-off: Extra adapter surface and maintenance burden per provider.
- Files affected: `backend/app/book_sim/providers/base.py`, `backend/app/book_sim/providers/*.py`, `backend/app/book_sim/provider_router.py`

## D-004
- Date: `2026-05-17` (reconstructed from files)
- Decision: Enforce `local_only` at route-selection level by forcing `local_ollama`.
- Rationale: Minimum viable privacy guardrail before wider runtime integration.
- Trade-off: Enforcement is currently local to router logic, not yet end-to-end API policy.
- Files affected: `backend/app/book_sim/provider_router.py`, `backend/tests/test_book_sim_provider_router.py`

## D-005
- Date: `2026-05-17` (reconstructed from files)
- Decision: Use typed dataclasses with explicit JSON helpers for Swarmbook models.
- Rationale: Matches existing backend style and keeps models lightweight and serializable.
- Trade-off: Manual coercion/validation logic versus richer framework-level validation.
- Files affected: `backend/app/book_sim/models.py`, `backend/tests/test_book_sim_models.py`

## D-006
- Date: `2026-05-17` (reconstructed from files)
- Decision: Implement manuscript evidence-pack generation as a composable module pipeline.
- Rationale: Enables modular testing and reuse before API/UI wiring.
- Trade-off: Current extraction quality relies heavily on heuristics and optional model calls.
- Files affected: `backend/app/book_sim/evidence_pack_builder.py`, `backend/app/book_sim/*_extractor.py`, `backend/tests/test_book_sim_evidence_pack_builder.py`

## D-007
- Date: `2026-05-17` (reconstructed from files)
- Decision: Add local content-hash caching for intermediate evidence artifacts.
- Rationale: Avoid repeated expensive processing for unchanged manuscripts.
- Trade-off: Basic cache invalidation semantics; no advanced replay/version policies yet.
- Files affected: `backend/app/book_sim/local_cache.py`, `backend/app/book_sim/evidence_pack_builder.py`

## D-008
- Date: `2026-05-17` (reconstructed from files)
- Decision: Keep Swarmbook integration unwired from legacy Flask routes during foundation phases.
- Rationale: Lower blast radius while contracts stabilize.
- Trade-off: Feature exists in code/tests but is not reachable via application API/UI yet.
- Files affected: evidence by absence in `backend/app/api/*`, `backend/app/__init__.py`, `frontend/src/router/index.js`

## D-009
- Date: `2026-05-17` (reconstructed from files)
- Decision: Use simulated platform style config rather than live platform integrations/scraping.
- Rationale: Aligns with local-first safety and explicit non-scraping requirement.
- Trade-off: Simulations depend on synthetic style assumptions.
- Files affected: `configs/book_sim/platform_styles.yaml`, `configs/book_sim/reader_archetypes.yaml`

## D-010
- Date: `2026-05-17`
- Decision: Persist Swarmbook graph artifacts through a namespace-scoped additive Neo4j service with dry-run fallback.
- Rationale: Keeps Swarmbook writes isolated from legacy graph data and allows safe local validation when Neo4j is unavailable.
- Trade-off: Adds another persistence layer to maintain alongside the legacy graph abstraction.
- Files affected: `backend/app/book_sim/graph_persistence.py`, `backend/tests/test_book_sim_graph_persistence.py`

## D-011
- Date: `2026-05-17`
- Decision: Generate reader personas from normalized YAML archetype templates with deterministic seeded sampling and optional router-backed enrichment.
- Rationale: Keeps persona generation local-first, testable, and reproducible while preserving a later path for higher-fidelity enrichment through the existing provider abstraction.
- Trade-off: The template-first runtime is deliberately synthetic and remains unwired from the broader simulation path until later phases.
- Files affected: `backend/app/book_sim/reader_archetype_loader.py`, `backend/app/book_sim/reader_persona_generator.py`, `backend/app/book_sim/models.py`, `backend/tests/test_book_sim_reader_persona_generator.py`

## D-012
- Date: `2026-05-17`
- Decision: Implement platform-native reaction generation through synthetic adapters plus a bounded multi-pass simulation engine.
- Rationale: Keeps platform output and cross-reader dynamics additive, deterministic, local-first, and tractable on a 16 GB Windows workstation.
- Trade-off: The system uses heuristic synthesis and bounded sampling instead of exhaustive many-to-many interactions.
- Files affected: `backend/app/book_sim/platform_adapters/*`, `backend/app/book_sim/simulation/*`, `backend/app/book_sim/models.py`, `backend/tests/test_book_sim_platform_adapters.py`, `backend/tests/test_book_sim_simulation_engine.py`

## D-013
- Date: `2026-05-17`
- Decision: Treat phases 8-12 as module-complete but keep phase 7 marked not-started until additive `book_sim` Flask routes are actually registered.
- Rationale: Prevent false readiness signals; module existence is not equivalent to runtime accessibility.
- Trade-off: Status reporting is stricter and may appear conservative versus implementation progress.
- Files affected: `docs/SWARMBOOK_PHASE_STATUS.md`, `backend/app/__init__.py` (absence of book_sim wiring)

## D-014
- Date: `2026-05-17`
- Decision: Block phase-13 readiness claims until `backend/app/book_sim/reports/` exists with both JSON and Markdown exports.
- Rationale: Report generation is a hard deliverable and currently absent; placeholders in models are insufficient.
- Trade-off: Requires explicit report module implementation and tests before claiming report-path functionality.
- Files affected: `backend/app/book_sim/models.py` (existing placeholders), missing `backend/app/book_sim/reports/*`

## D-015
- Date: `2026-05-17`
- Decision: Implement Swarmbook persona interrogation as a deterministic, template-first backend service over serialized `SimulationRun` and `EvidencePack` artifacts.
- Rationale: Keeps `local_only` safe, prevents hallucinated manuscript detail, and avoids coupling interrogation to the still-incomplete report and persistence phases.
- Trade-off: The current route requires the caller to provide serialized artifacts instead of resolving them from a stored simulation ID.
- Files affected: `backend/app/book_sim/interrogation/*`, `backend/app/api/book_sim.py`, `backend/tests/test_book_sim_persona_chat.py`

## D-016
- Date: `2026-05-17`
- Decision: Implement Swarmbook draft comparison as a deterministic backend module over evidence packs plus optional simulation runs and optional precomputed scores, with JSON and Markdown exports.
- Rationale: This keeps comparison additive and usable before report/API wiring lands, while still supporting unsimulated drafts through evidence-only plus scorecard fallback.
- Trade-off: The comparison slice is backend-only for now and does not resolve persisted artifacts or expose a route yet.
- Files affected: `backend/app/book_sim/comparison/*`, `backend/app/book_sim/models.py`, `backend/tests/test_book_sim_draft_comparator.py`

## D-017
- Date: `2026-05-18`
- Decision: Expose Swarmbook through additive `/api/book-sim/*` backend routes backed by a local JSON runtime store and deterministic runtime report synthesis.
- Rationale: This creates a bounded backend runtime path for project ingest, simulate-plus-report, persona chat, comparison, and health without disturbing legacy MiroFish routes or requiring a full frontend first.
- Trade-off: Runtime artifacts are file-backed and lightweight for now, and report synthesis still lives in `report_builder.py` instead of a dedicated `reports/` package.
- Files affected: `backend/app/api/book_sim.py`, `backend/app/book_sim/runtime_store.py`, `backend/app/book_sim/report_builder.py`, `backend/tests/test_book_sim_api.py`

## D-018
- Date: `2026-05-18`
- Decision: Add Swarmbook frontend delivery as a separate `/swarmbook/*` Vue route family backed by a lightweight local session store instead of folding the new book workflow into the legacy process/simulation/report screens.
- Rationale: This preserves the existing MiroFish UI, keeps the Swarmbook blast radius narrow, and lets the new frontend bind directly to the additive `/api/book-sim/*` backend runtime.
- Trade-off: Some concepts now exist in both the legacy UI and the Swarmbook UI, and the frontend currently depends on local session state rather than a stronger client-side data layer.
- Files affected: `frontend/src/router/index.js`, `frontend/src/api/bookSim.js`, `frontend/src/store/swarmbookSession.js`, `frontend/src/components/swarmbook/SwarmbookLayout.vue`, `frontend/src/views/swarmbook/*`, `frontend/src/views/Home.vue`

## D-019
- Date: `2026-05-19`
- Decision: Mark Phase 17 as blocked/incomplete and block Phase 18 start until local-profile config and setup docs exist.
- Rationale: The required low-resource profile artifacts are missing (`configs/book_sim/local_profiles.yaml`, `docs/SWARMBOOK_LOCAL_SETUP.md`), so Phase 17 verification criteria cannot be met.
- Trade-off: Delivery sequencing remains strict and prevents premature progression to Phase 18.
- Files affected: `docs/SWARMBOOK_PHASE_STATUS.md`, `docs/SWARMBOOK_CHANGELOG.md`, `docs/SWARMBOOK_DECISIONS.md`, `docs/SWARMBOOK_HANDOFF_LATEST.md`

## D-020
- Date: `2026-05-19`
- Decision: Centralize Swarmbook low-resource defaults in `configs/book_sim/local_profiles.yaml` and enforce them through an additive local profile loader used by project creation, simulation defaults, and health reporting.
- Rationale: Phase 17 required explicit, auditable defaults for 16 GB RAM / 6 GB VRAM local usage with structured warnings and preserved `local_only` privacy behavior.
- Trade-off: Adds one more config surface and loader maintenance path, but keeps profile behavior deterministic and testable.
- Files affected: `configs/book_sim/local_profiles.yaml`, `backend/app/book_sim/local_profiles.py`, `backend/app/api/book_sim.py`, `backend/tests/test_book_sim_local_profiles.py`, `backend/tests/test_book_sim_api.py`, `docs/SWARMBOOK_LOCAL_SETUP.md`

## D-021
- Date: `2026-05-19`
- Decision: Treat the Phase 18 quality gate as passable in the current environment but keep Phase 19 blocked until privacy/compliance enforcement moves beyond router-scoped guards.
- Rationale: Backend Swarmbook tests pass, the report-builder path is covered, and the frontend bundle builds via direct Vite, but router-scoped `local_only` is still the only privacy boundary.
- Trade-off: Consolidation stays honest about the remaining risk instead of declaring release readiness prematurely.
- Files affected: `docs/SWARMBOOK_PHASE_STATUS.md`, `docs/SWARMBOOK_CHANGELOG.md`, `docs/SWARMBOOK_DECISIONS.md`, `docs/SWARMBOOK_OPEN_QUESTIONS.md`, `docs/SWARMBOOK_HANDOFF_LATEST.md`

## D-022
- Date: `2026-05-19`
- Decision: Add Phase 19 local hardening improvements without expanding product scope (error surfaces, size guards, partial-failure recovery, and Markdown export), and document limitations explicitly.
- Rationale: Local-first usage needs clearer failure modes (missing keys, missing runtimes), predictable ingestion limits for low-resource machines, and stable exports for sharing/review.
- Trade-off: Phase 19 improves UX and reliability but does not resolve the remaining architectural risk: privacy enforcement is still router-scoped and frontend packaging is not proven in this environment.
- Files affected: `backend/app/api/book_sim.py`, `backend/app/book_sim/report_markdown.py`, `frontend/src/api/index.js`, `docs/SWARMBOOK_LOCAL_SETUP.md`, `docs/SWARMBOOK_USAGE_GUIDE.md`, `docs/SWARMBOOK_LIMITATIONS.md`

## D-023
- Date: `2026-05-20`
- Decision: Add a constrained fallback parser for Swarmbook route/privacy YAML when PyYAML is absent.
- Rationale: The active local Python environment lacks PyYAML, but E2E validation still needs deterministic config/profile loading without installing dependencies.
- Trade-off: The fallback only supports the existing `model_routes.yaml` and `privacy_modes.yaml` shapes; PyYAML remains preferred when installed.
- Files affected: `backend/app/book_sim/config_loader.py`, `backend/tests/test_book_sim_e2e.py`
