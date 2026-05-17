# AGENTS

## Swarmbook Continuity Guardrails
- Preserve original MiroFish-Offline behavior unless a change is strictly required.
- Prefer additive implementation under `backend/app/book_sim` and `configs/book_sim`.
- Do not delete files as part of Swarmbook work.
- Before starting Swarmbook tasks, read:
  - `docs/SWARMBOOK_CONTEXT.md`
  - `docs/SWARMBOOK_PHASE_STATUS.md`
- After each phase, update:
  - `docs/SWARMBOOK_PHASE_STATUS.md`
  - `docs/SWARMBOOK_CHANGELOG.md`
  - `docs/SWARMBOOK_DECISIONS.md`
- Do not implement real scraping/integration for Goodreads, TikTok, Instagram, Reddit, Bookstagram, or X.
- `local_only` privacy mode must never call Gemini, NVIDIA, or any external provider.
- Run validation commands (or list exact commands if environment is unavailable) after edits.
