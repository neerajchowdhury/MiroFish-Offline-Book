# Swarmbook Handoff (Latest)

## 1) Current Objective
Resume from the additive frontend-and-backend runtime slice: Swarmbook has `/api/book-sim/*` backend routes plus `/swarmbook/*` Vue screens, and the next clean work is report-layer hardening into a dedicated package plus fixing the machine-level npm shim path.

## 2) Last Completed / Partially Completed Phase
- Last checkpoint commit: `08a3a7e` (`2026-05-17`) "swarmbook: checkpoint after phase 6 implementation".
- Practical status:
  - Done: Phase 2, Phase 3, Phase 5, Phase 7, Phase 8, Phase 9, Phase 10, Phase 11, Phase 12.
  - Partially done: Phase 1, Phase 4, Phase 6, Phase 13, Phase 14, Phase 15, Phase 16, Phase 17, Phase 18, Phase 19.

## 3) Current Repository State
- Branch: `feature/swarmbook-phase6-recovery`
- Working tree status at start of this pass: dirty with additive Swarmbook backend, frontend, and continuity-doc updates pending commit.
- Swarmbook modules/config/tests now include bounded backend routes for project creation, evidence-pack ingest, simulate-plus-report, persona chat, draft comparison, health, and the legacy-compatible interrogation route.
- Swarmbook frontend flow now exists under `/swarmbook/*` with landing, upload, metadata, evidence preview, simulation, report, persona, and comparison screens.

## 4) Files/Modules Implemented So Far
- Architecture: `docs/SWARMBOOK_ARCHITECTURE.md`
- Configs: `configs/book_sim/*.yaml`
- Router/providers: `backend/app/book_sim/config_loader.py`, `provider_router.py`, `providers/*`
- Models: `backend/app/book_sim/models.py`
- Evidence pipeline: `backend/app/book_sim/manuscript_chunker.py`, `book_dna_extractor.py`, `style_analyzer.py`, `risk_detector.py`, `nonfiction_claim_extractor.py`, `character_mapper.py`, `evidence_pack_builder.py`, `local_cache.py`
- Runtime storage/reporting: `backend/app/book_sim/runtime_store.py`, `report_builder.py`
- Graph persistence: `backend/app/book_sim/graph_persistence.py`
- Persona generation: `backend/app/book_sim/reader_archetype_loader.py`, `reader_persona_generator.py`
- Platform adapters: `backend/app/book_sim/platform_adapters/*`
- Simulation engine: `backend/app/book_sim/simulation/*`
- Scoring: `backend/app/book_sim/scoring/*`
- Interrogation: `backend/app/book_sim/interrogation/*`
- Comparison: `backend/app/book_sim/comparison/*`
- Swarmbook API slice: `backend/app/api/book_sim.py`
- Swarmbook frontend API/store/layout:
  - `frontend/src/api/bookSim.js`
  - `frontend/src/store/swarmbookSession.js`
  - `frontend/src/components/swarmbook/SwarmbookLayout.vue`
- Swarmbook frontend screens:
  - `frontend/src/views/swarmbook/*`
  - `frontend/src/router/index.js`
  - `frontend/src/views/Home.vue` (entry link only)
- Tests/fixtures: `backend/tests/test_book_sim_provider_router.py`, `backend/tests/test_book_sim_models.py`, `backend/tests/test_book_sim_evidence_pack_builder.py`, `backend/tests/fixtures/book_sim_*`
- Swarmbook tests: `backend/tests/test_book_sim_graph_persistence.py`, `backend/tests/test_book_sim_reader_persona_generator.py`, `backend/tests/test_book_sim_platform_adapters.py`, `backend/tests/test_book_sim_simulation_engine.py`
- Interrogation tests: `backend/tests/test_book_sim_persona_chat.py`
- Comparison tests: `backend/tests/test_book_sim_draft_comparator.py`
- API tests: `backend/tests/test_book_sim_api.py`
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
  - `npm run build` -> failed because the global `npm` shim points to a missing `npm-cli.js`
  - `C:\Users\neera\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\vite\bin\vite.js build` -> pass
  - `python -m py_compile backend/app/api/book_sim.py backend/app/book_sim/runtime_store.py backend/app/book_sim/report_builder.py backend/app/book_sim/__init__.py` -> pass
  - `python -m unittest backend.tests.test_book_sim_api backend.tests.test_book_sim_persona_chat backend.tests.test_book_sim_draft_comparator backend.tests.test_book_sim_scoring backend.tests.test_book_sim_simulation_engine backend.tests.test_book_sim_models backend.tests.test_book_sim_provider_router` -> pass (`25` tests, `4` skipped)
  - `python -m unittest backend.tests.test_book_sim_platform_adapters backend.tests.test_book_sim_simulation_engine` -> pass (`2` tests)
  - `python -m unittest backend.tests.test_book_sim_models backend.tests.test_book_sim_reader_persona_generator backend.tests.test_book_sim_graph_persistence backend.tests.test_book_sim_evidence_pack_builder backend.tests.test_book_sim_provider_router` -> pass (`18` tests, `1` skipped)
  - `python -m unittest backend.tests.test_book_sim_scoring` -> pass (`8` tests)
  - `python -m unittest backend.tests.test_book_sim_persona_chat` -> pass (`3` tests, `1` skipped because `flask` is unavailable in the active Python environment)
  - `python -m py_compile backend/app/book_sim/platform_adapters/*.py backend/app/book_sim/simulation/*.py backend/tests/test_book_sim_platform_adapters.py backend/tests/test_book_sim_simulation_engine.py` -> pass
  - `python -m py_compile backend/app/book_sim/scoring/*.py backend/tests/test_book_sim_scoring.py` -> pass
  - `python -m py_compile backend/app/book_sim/interrogation/__init__.py backend/app/book_sim/interrogation/persona_chat.py backend/app/api/book_sim.py` -> pass
  - `python -m unittest backend.tests.test_book_sim_persona_chat backend.tests.test_book_sim_provider_router` -> pass (`8` tests, `2` skipped because `flask` is unavailable in the active Python environment)
  - `python -m unittest backend.tests.test_book_sim_draft_comparator backend.tests.test_book_sim_models` -> pass (`4` tests)
  - `python -m unittest backend.tests.test_book_sim_draft_comparator backend.tests.test_book_sim_scoring backend.tests.test_book_sim_simulation_engine backend.tests.test_book_sim_models` -> pass (`13` tests)
  - `python -m py_compile backend/app/book_sim/comparison/__init__.py backend/app/book_sim/comparison/comparison_report.py backend/app/book_sim/comparison/draft_comparator.py backend/app/book_sim/models.py backend/app/book_sim/__init__.py` -> pass
- Known environment note:
  - `python -m compileall backend/app/book_sim ...` hit a Windows `__pycache__` permission error during `.pyc` rename even though the files themselves compile cleanly with `py_compile`.
  - `python -m py_compile ... backend/tests/test_book_sim_draft_comparator.py ...` hit the same Windows `__pycache__` rename permission problem for test `.pyc` output; app-module compiles still pass cleanly.

## 7) Known Broken/Incomplete Areas
- Frontend default package-manager invocation remains broken because the machine-level npm shim points to a missing `npm-cli.js`.
- The backend report layer exists only as `backend/app/book_sim/report_builder.py`; there is still no dedicated `backend/app/book_sim/reports/` package.
- Runtime artifacts are currently file-backed through the local cache tree rather than a stronger persistence/replay layer.
- Privacy enforcement is not yet system-wide beyond router selection logic.
- Legacy `/api/report` and the new `/api/book-sim/*` runtime remain separate paths.

## 13) True Phase State (7-15)
- Phase 7: done (bounded additive backend runtime routes exist under `/api/book-sim/*`).
- Phase 8: done at module level (graph persistence implemented + tested).
- Phase 9: done at module level (persona generation implemented + tested).
- Phase 10: done at module level (platform adapters implemented + tested).
- Phase 11: done at module level (bounded simulation engine implemented + tested).
- Phase 12: done at module level (scoring engine implemented + tested).
- Phase 13: partially done (runtime report synthesis and latest-report route exist, but no dedicated report package yet).
- Phase 14: partially done (grounded interrogation service + stored-artifact route path + frontend screen now exist, but frontend dependency validation is still blocked here).
- Phase 15: partially done (deterministic comparison module + backend route + stored-artifact lookup + tests exist; frontend screen now exists but has not been build-validated here).
- Phase 16: partially done (frontend Swarmbook route family and screens now exist, but dependency validation is blocked in this environment).

## 14) Unsafe Assumptions Found
- Assuming frontend availability is unsafe; only the backend runtime path is wired.
- Assuming report generation is "finished" is unsafe; `backend/app/book_sim/reports/` does not exist yet even though runtime report synthesis now does.
- Assuming privacy enforcement is global is unsafe; enforcement is router-scoped and not middleware-wide.
- Assuming the runtime store is production-grade persistence is unsafe; it is currently file-backed and lightweight by design.

## 15) Repair Tasks Before/Alongside Phase 13
1. Keep status language strict: "module complete" vs "runtime wired".
2. Extract the runtime report helper into `backend/app/book_sim/reports/*` with tests before claiming report-path completion.
3. Preserve `local_only` guarantees by keeping route selection and health checks behind `BookSimProviderRouter`.
4. Keep any further API additions additive and narrow; do not silently broaden the unfinished Swarmbook runtime surface.
5. Decide whether the file-backed runtime store should remain the primary early-phase persistence path or be replaced with a stronger artifact registry.

## 8) Exact Next Safe Phase
Phase 13 hardening is still the next clean sequential phase and remains safe.
1. Move the current runtime report synthesis into a dedicated `backend/app/book_sim/reports/*` package.
2. Keep using the existing simulation and scoring outputs without changing legacy simulation.
3. Preserve deterministic, local-first report generation and evidence propagation.
4. Add unit tests around the report builder/package boundary, then return to frontend build validation once dependencies are available.

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

Task: Harden the partially implemented Swarmbook report synthesis layer and move it into a dedicated reports package.
Requirements:
- Preserve existing MiroFish-Offline behavior.
- Use additive architecture under backend/app/book_sim.
- Do not delete files.
- Use the existing simulation and scoring outputs instead of rewriting the passes.
- Preserve the new `/api/book-sim/*` runtime behavior while refactoring the report layer.
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

Task: Continue Phase 13 by extracting the runtime report synthesis helper into a dedicated additive reports package only.
Requirements:
- Preserve existing MiroFish-Offline behavior.
- Use additive architecture under backend/app/book_sim.
- Do not delete files.
- Use the existing simulation and scoring outputs and keep report generation deterministic.
- Preserve the current `/api/book-sim/simulate` and `/api/book-sim/projects/{project_id}/report` behavior.
- Do not call real platform APIs or scraping services.
- Add tests for report inputs and outputs.
- Report changed files, commands run, tests passed/failed, and known gaps.
```

## 12) Latest Audit Note
- Phase 12 scoring audit passed at the module level.
- Verified deterministic scoring outputs, confidence bands, evidence refs, and test coverage for all score functions.
- Verified defaults remain intact: `hybrid_safe` persona count `30`, `local_only` persona count `16`, `cross_reaction_posts=8`, `max_reaction_rounds=2`, `max_parallel_jobs=1`.
- Phase 14 interrogation audit passed at the bounded backend-runtime level.
- Verified the interrogation slice loads persona, private reaction, platform posts, cross-reactions, and evidence refs from serialized artifacts or stored runtime artifacts; returns `based_on`; preserves review style without provider calls; and exposes both `/api/book-sim/interrogate` and `/api/book-sim/personas/{persona_id}/chat`.
- Phase 14 is safe only at that bounded backend-runtime level. It is not yet a fully wired runtime phase because frontend integration is still absent.
- Phase 15 comparison implementation and audit passed at the bounded backend-runtime level.
- Verified the comparison slice uses previous evidence packs, optional simulation outputs, and optional precomputed scores; exports deterministic JSON and Markdown; supports stored-artifact lookup through `/api/book-sim/compare`; and preserves `local_only` by avoiding provider calls.
- Phase 15 is safe only at that bounded backend-runtime level. It is not yet a fully wired runtime phase because frontend integration is still absent.
