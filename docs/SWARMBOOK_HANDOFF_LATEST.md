# Swarmbook Handoff (Latest)

## 1) Current Objective
Stabilize continuity and project memory after scoring landed, while documenting what remains unwired before report and API phases.

## 2) Last Completed / Partially Completed Phase
- Last checkpoint commit: `08a3a7e` (`2026-05-17`) "swarmbook: checkpoint after phase 6 implementation".
- Practical status:
  - Done: Phase 2, Phase 3, Phase 5, Phase 8, Phase 9, Phase 10, Phase 11, Phase 12.
  - Partially done: Phase 1, Phase 4, Phase 6, Phase 17, Phase 18, Phase 19.

## 3) Current Repository State
- Branch: `feature/swarmbook-phase6-recovery`
- Working tree status at start of this pass: clean.
- Swarmbook modules/config/tests now include platform adapters and simulation passes, but no Swarmbook API/UI runtime wiring yet.

## 4) Files/Modules Implemented So Far
- Architecture: `docs/SWARMBOOK_ARCHITECTURE.md`
- Configs: `configs/book_sim/*.yaml`
- Router/providers: `backend/app/book_sim/config_loader.py`, `provider_router.py`, `providers/*`
- Models: `backend/app/book_sim/models.py`
- Evidence pipeline: `backend/app/book_sim/manuscript_chunker.py`, `book_dna_extractor.py`, `style_analyzer.py`, `risk_detector.py`, `nonfiction_claim_extractor.py`, `character_mapper.py`, `evidence_pack_builder.py`, `local_cache.py`
- Graph persistence: `backend/app/book_sim/graph_persistence.py`
- Persona generation: `backend/app/book_sim/reader_archetype_loader.py`, `reader_persona_generator.py`
- Platform adapters: `backend/app/book_sim/platform_adapters/*`
- Simulation engine: `backend/app/book_sim/simulation/*`
- Scoring: `backend/app/book_sim/scoring/*`
- Tests/fixtures: `backend/tests/test_book_sim_provider_router.py`, `backend/tests/test_book_sim_models.py`, `backend/tests/test_book_sim_evidence_pack_builder.py`, `backend/tests/fixtures/book_sim_*`
- Swarmbook tests: `backend/tests/test_book_sim_graph_persistence.py`, `backend/tests/test_book_sim_reader_persona_generator.py`, `backend/tests/test_book_sim_platform_adapters.py`, `backend/tests/test_book_sim_simulation_engine.py`
- Baseline smoke script: `backend/tests/smoke_check.py`

## 5) Important Design Decisions
- Additive architecture under `backend/app/book_sim`.
- YAML-driven routing/privacy config under `configs/book_sim`.
- Unified provider interface for Ollama/Gemini/NVIDIA.
- Dataclass-based typed models with explicit JSON helpers.
- Heuristic-first evidence extraction with optional router-backed synthesis.
- Content-hash JSON caching for evidence packs.
- Platform-native outputs are synthetic adapters only; no real platform APIs.
- Cross-reader reactions are bounded to a top-post shortlist plus 3-7 sampled posts per persona to control local resource cost.
- Scoring is deterministic, explainable, and uses a local fallback parser for `scoring_weights.yaml` when `PyYAML` is unavailable.

## 6) Tests Run and Status
- Executed in this pass:
  - `python -m unittest backend.tests.test_book_sim_platform_adapters backend.tests.test_book_sim_simulation_engine` -> pass (`2` tests)
  - `python -m unittest backend.tests.test_book_sim_models backend.tests.test_book_sim_reader_persona_generator backend.tests.test_book_sim_graph_persistence backend.tests.test_book_sim_evidence_pack_builder backend.tests.test_book_sim_provider_router` -> pass (`18` tests, `1` skipped)
  - `python -m unittest backend.tests.test_book_sim_scoring` -> pass (`8` tests)
  - `python -m py_compile backend/app/book_sim/platform_adapters/*.py backend/app/book_sim/simulation/*.py backend/tests/test_book_sim_platform_adapters.py backend/tests/test_book_sim_simulation_engine.py` -> pass
  - `python -m py_compile backend/app/book_sim/scoring/*.py backend/tests/test_book_sim_scoring.py` -> pass
- Known environment note:
  - `python -m compileall backend/app/book_sim ...` hit a Windows `__pycache__` permission error during `.pyc` rename even though the files themselves compile cleanly with `py_compile`.

## 7) Known Broken/Incomplete Areas
- Swarmbook APIs are not registered in Flask routes.
- Frontend has no Swarmbook routes/views.
- End-to-end manuscript->book_sim->report runtime path is not exposed.
- Privacy enforcement is not yet system-wide beyond router selection logic.
- Report synthesis is not yet implemented.

## 8) Exact Next Safe Phase
Phase 13 is safe at the module level.
1. Add an additive report synthesis layer under `backend/app/book_sim`.
2. Use the simulation and scoring outputs without changing legacy simulation.
3. Keep report generation deterministic and cacheable by content hash.
4. Add unit tests before any API wiring.

## 9) Exact Prompt for a Fresh Codex Thread
Use this prompt verbatim:

```text
You are working in my local clone of MiroFish-Offline.
Read these files first and follow them strictly:
1) AGENTS.md
2) docs/SWARMBOOK_CONTEXT.md
3) docs/SWARMBOOK_PHASE_STATUS.md
4) docs/SWARMBOOK_DECISIONS.md
5) docs/SWARMBOOK_CHANGELOG.md
6) docs/SWARMBOOK_OPEN_QUESTIONS.md
7) docs/SWARMBOOK_HANDOFF_LATEST.md

Task: Implement the Swarmbook report synthesis layer on top of the existing simulation and scoring outputs.
Requirements:
- Preserve existing MiroFish-Offline behavior.
- Use additive architecture under backend/app/book_sim.
- Do not delete files.
- Use the existing simulation and scoring outputs instead of rewriting the passes.
- Keep local_only mode from using external providers.
- Add/update unit tests for report synthesis behavior.
- Report changed files, commands run, tests passed/failed, and known gaps.
```

## 10) Files the Next Thread Must Read First
- `AGENTS.md`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_PROMPT_LOG.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`

## 11) Clean Resume Point
Use this prompt verbatim:

```text
You are working in my local clone of MiroFish-Offline.
Read these files first and follow them strictly:
1) AGENTS.md
2) docs/SWARMBOOK_CONTEXT.md
3) docs/SWARMBOOK_PHASE_STATUS.md
4) docs/SWARMBOOK_DECISIONS.md
5) docs/SWARMBOOK_CHANGELOG.md
6) docs/SWARMBOOK_OPEN_QUESTIONS.md
7) docs/SWARMBOOK_HANDOFF_LATEST.md

Task: Start Phase 12 by creating the additive scoring layer only.
Requirements:
- Preserve existing MiroFish-Offline behavior.
- Use additive architecture under backend/app/book_sim.
- Do not delete files.
- Use the existing simulation outputs and keep scoring deterministic.
- Do not call real platform APIs or scraping services.
- Add tests for scoring inputs and outputs.
- Report changed files, commands run, tests passed/failed, and known gaps.
```

## 12) Latest Audit Note
- Phase 12 scoring audit passed at the module level.
- Verified deterministic scoring outputs, confidence bands, evidence refs, and test coverage for all score functions.
- Verified defaults remain intact: `hybrid_safe` persona count `30`, `local_only` persona count `16`, `cross_reaction_posts=8`, `max_reaction_rounds=2`, `max_parallel_jobs=1`.
- Phase 13 is the next safe module-level phase, but report/API wiring is still pending.
