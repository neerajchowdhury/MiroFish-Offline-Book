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
