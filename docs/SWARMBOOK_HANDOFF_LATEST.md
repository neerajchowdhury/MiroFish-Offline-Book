# Swarmbook Handoff (Latest)

## 1) Current Objective
Stabilize continuity and project memory before the Phase 10 platform-adapter phase by documenting what is actually implemented and what still remains unwired.

## 2) Last Completed / Partially Completed Phase
- Last checkpoint commit: `08a3a7e` (`2026-05-17`) "swarmbook: checkpoint after phase 6 implementation".
- Practical status:
  - Done: Phase 2, Phase 3, Phase 5.
  - Partially done: Phase 1, Phase 4, Phase 6.

## 3) Current Repository State
- Branch: `feature/swarmbook-phase6-recovery`
- Working tree status at start of this pass: clean.
- Swarmbook modules/config/tests exist, but no platform adapter package or Swarmbook API/UI runtime wiring yet.

## 4) Files/Modules Implemented So Far
- Architecture: `docs/SWARMBOOK_ARCHITECTURE.md`
- Configs: `configs/book_sim/*.yaml`
- Router/providers: `backend/app/book_sim/config_loader.py`, `provider_router.py`, `providers/*`
- Models: `backend/app/book_sim/models.py`
- Evidence pipeline: `backend/app/book_sim/manuscript_chunker.py`, `book_dna_extractor.py`, `style_analyzer.py`, `risk_detector.py`, `nonfiction_claim_extractor.py`, `character_mapper.py`, `evidence_pack_builder.py`, `local_cache.py`
- Tests/fixtures: `backend/tests/test_book_sim_provider_router.py`, `backend/tests/test_book_sim_models.py`, `backend/tests/test_book_sim_evidence_pack_builder.py`, `backend/tests/fixtures/book_sim_*`
- Baseline smoke script: `backend/tests/smoke_check.py`

## 5) Important Design Decisions
- Additive architecture under `backend/app/book_sim`.
- YAML-driven routing/privacy config under `configs/book_sim`.
- Unified provider interface for Ollama/Gemini/NVIDIA.
- Dataclass-based typed models with explicit JSON helpers.
- Heuristic-first evidence extraction with optional router-backed synthesis.
- Content-hash JSON caching for evidence packs.

## 6) Tests Run and Status
- Executed in this pass:
  - `python -m compileall backend/app/book_sim` -> pass
  - `python -m unittest backend.tests.test_book_sim_provider_router` -> pass (`6` tests, `1` skipped)
  - `python -m unittest backend.tests.test_book_sim_models` -> pass (`2` tests)
  - `python -m unittest backend.tests.test_book_sim_evidence_pack_builder` -> pass (`2` tests)
  - `python backend/tests/smoke_check.py --help` -> fail (`ModuleNotFoundError: No module named 'flask'`) in current environment
- Minimum follow-up validation after backend deps install:
  - `python -m unittest backend.tests.test_book_sim_provider_router`
  - `python -m unittest backend.tests.test_book_sim_models`
  - `python -m unittest backend.tests.test_book_sim_evidence_pack_builder`
  - `python backend/tests/smoke_check.py --backend-url http://127.0.0.1:5001 --frontend-url http://127.0.0.1:3000 --ollama-url http://127.0.0.1:11434`

## 7) Known Broken/Incomplete Areas
- Swarmbook APIs are not registered in Flask routes.
- Frontend has no Swarmbook routes/views.
- End-to-end manuscript->book_sim->report runtime path is not exposed.
- Privacy enforcement is not yet system-wide beyond router selection logic.
- Book-graph persistence and scoring/reaction engines are not yet implemented.

## 8) Exact Next Safe Phase
Phase 10 is not safe yet.
1. Create the additive `backend/app/book_sim/platform_adapters/` package.
2. Add a shared adapter base plus one synthetic adapter per platform.
3. Keep output JSON structured and evidence-backed, with no real platform calls.
4. Add adapter tests before any orchestration wiring.

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

Task: Close Phase 6 gaps without starting Phase 7 yet.
Requirements:
- Preserve existing MiroFish-Offline behavior.
- Use additive architecture under backend/app/book_sim.
- Do not delete files.
- Wire Swarmbook API endpoints for manuscript ingest + evidence-pack generation only.
- Keep local_only mode from using external providers.
- Add/update tests for API-level evidence-pack flow.
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

Task: Start Phase 10 by creating the simulated platform adapter layer only.
Requirements:
- Preserve existing MiroFish-Offline behavior.
- Use additive architecture under backend/app/book_sim/platform_adapters.
- Do not delete files.
- Do not call real platform APIs or scraping services.
- Use platform_styles.yaml.
- Return structured PlatformPost JSON with evidence_refs.
- Add tests for each adapter or a shared adapter suite.
- Report changed files, commands run, tests passed/failed, and known gaps.
```
