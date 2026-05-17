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
