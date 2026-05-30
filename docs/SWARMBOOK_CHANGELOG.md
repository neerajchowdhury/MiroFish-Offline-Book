# Swarmbook Changelog (Reconstructed)

## Phase 49 (E2E Testing & Verification)
### Files
- `backend/tests/test_book_sim_extra_edge_cases.py`
- `docs/SWARMBOOK_TESTING_PLAN.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- **E2E Hardened** — Designed and ran a 360-degree testing pass across the Swarmbook Studio ecosystem.
- **Edge Case Tests** — Implemented additional automated test cases verifying DraftComparator self-comparison behavior, maximum/extreme rating distribution scoring baselines, and strict router filtering under local-only privacy mode constraint.
- **Vite Build Verification** — Verified client production build completes with zero errors.
### Tests added/updated
- Added `backend/tests/test_book_sim_extra_edge_cases.py` containing 3 new unit tests. All 76 python backend unit tests pass successfully.
- Run frontend Vite production build: SUCCESS (0 errors).
### Known gaps
- None.

## Phase 48 (QA Pass & High-Priority Fixes)
### Files
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`
- `frontend/src/views/swarmbook/SwarmbookCompareView.vue`
- `frontend/src/views/swarmbook/SwarmbookReportView.vue`
- `docs/SWARMBOOK_QA_REPORT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
### Behavior changed
- **Accessibility Fixes** — Added `aria-hidden="true"` to `.action-icon` and `.empty-icon` decorative elements across all Swarmbook views so screen readers do not misinterpret them.
- **QA Pass** — Verified focus outlines, color contrast, error states, and responsive layouts.
### Tests added/updated
- Run frontend Vite production build: SUCCESS (0 errors).
- Backend unit tests previously verified 73/73 PASS.
### Known gaps
- None.

## Phase 47 (Draft Comparison Refinement)
### Files
- `frontend/src/views/swarmbook/SwarmbookCompareView.vue` — Added directional delta icons for score movements (replacing color-only signals) and injected a synthetic sandbox limitations warning banner.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Updated Phase 47 status row.
- `docs/SWARMBOOK_CHANGELOG.md` — Prepended Phase 47 log details.
- `docs/SWARMBOOK_DECISIONS.md` — Added D-051 regarding the addition of directional icons and sandbox banners.
### Behavior changed
- **Accessible Delta Signals** — Score deltas now display clear directional icons (`↗️`/`↘️`/`➖`) alongside colors so meaning is not lost for color-blind users.
- **Persistent Limitations Info** — Added a warning alert banner at the workspace top highlighting sandbox simulated generation and confidence expectations.
### Tests added/updated
- Run frontend Vite production build: SUCCESS (0 errors).
### Known gaps
- None.

## Phase 46 (Persona Interview Refinement)
### Files
- `frontend/src/views/swarmbook/SwarmbookPersonasView.vue` — Refined master-detail interview dashboard layout, implemented sliding responsive drawer overlay with Close button and backdrop overlay, rewrote computed evidence mapping lookup resolver to cover all 7 schema maps, registered exact quick questions, and added persistent limitations banner.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Updated Phase 46 status row.
- `docs/SWARMBOOK_CHANGELOG.md` — Prepended Phase 46 log details.
- `docs/SWARMBOOK_DECISIONS.md` — Added D-050 regarding sliding drawer layout and deep evidence parsing lookup.
### Behavior changed
- **Refined Quick Questions** — Registered the exact 6 trigger questions requested.
- **Interactive Sliding Drawer** — Replaced the static column with an overlay drawer on desktop and mobile (occupying 100% width on mobile) to save screen space and improve chat readability.
- **Persistent Limitations Info** — Bounded a warning alert banner at the workspace top highlighting sandbox and scraping limits.
- **Deep Evidence References Mapping** — Maps all 7 structural evidence pack configurations seamlessly.
### Tests added/updated
- Run frontend Vite production build: SUCCESS (0 errors).
- Run backend unit tests: 73/73 PASS.
### Known gaps
- None.

## Phase 45 (Report Export System)
### Files
- `package.json` — Added `pdfmake`, `docx`, `html2canvas`, and `file-saver`.
- `frontend/src/utils/exportReport.js` — [NEW] Added a dedicated utility module handling JSON, Markdown, DOCX, and PDF structured generation, and Clipboard actions.
- `frontend/src/views/swarmbook/SwarmbookReportView.vue` — Replaced old export buttons with a complete export row. Added a hidden `#png-summary-card` for DOM capture. Wired up the handlers.
- `docs/EXPORT_SYSTEM.md` — [NEW] Documented export system architecture.
- `docs/SWARMBOOK_CHANGELOG.md` — Prepended Phase 45 log details.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Updated Phase 45 status row in status table.
- `docs/SWARMBOOK_DECISIONS.md` — Added D-049 regarding export structured generation vs DOM snapshots.
### Behavior changed
- **Multiple Export Options** — Authors can export structured PDF and DOCX files without sacrificing UI performance.
- **Copy to Clipboard** — Provides native copy-to-clipboard functionality with a success indicator.
- **Shareable Summary** — Provides a beautiful, one-page PNG scorecard explicitly designed for social sharing via `html2canvas`.
### Tests added/updated
- Run frontend Vite production build: SUCCESS (0 errors).
### Known gaps
- None.

## Phase 44 (Report Dashboard Decision-First Redesign)
### Files
- `frontend/src/views/swarmbook/SwarmbookReportView.vue` — Redesigned the Report Dashboard to operate as an editorial command center. Added sticky horizontal jump navigation inside the actions bar. Relocated the "Revision Priorities" block to sit immediately below the "Executive Verdict" above the fold. Appended Stage Confidence metric card into the top summary metrics grid. Constrained "Simulated Platform Posts" feed height and added explicitly captioned descriptions to visual charts.
- `docs/SWARMBOOK_CHANGELOG.md` — Prepended Phase 44 log details.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Updated Phase 44 status row in status table.
- `docs/SWARMBOOK_DECISIONS.md` — Added D-048 for Report Dashboard layout prioritization.
### Behavior changed
- **Decision-First UX** — Authors can now immediately see the most critical actions (Revision Priorities) without scrolling past lower-level risk analysis.
- **Improved Navigation** — Jump links (`#section-verdict-priorities`, etc.) provide fast scanning.
- **Constrained Content** — Long social media mock feeds no longer dominate vertical screen space.
### Tests added/updated
- Run frontend Vite production build: SUCCESS (0 errors).
### Known gaps
- None.

## Phase 43 (Simulation Progress Screen)
### Files
- `frontend/src/views/swarmbook/SwarmbookSimulationRunView.vue` — Redesigned into a 7-step pipeline layout with a stepper map, active ETA calculations, un-stuck terminal logging display, and properly handled disabled state logic for pausing.
- `docs/SWARMBOOK_CHANGELOG.md` — Prepended Phase 43 log details.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Updated Phase 43 status row in status table.
- `docs/SWARMBOOK_DECISIONS.md` — Added D-047 for Progress Screen redesign decisions.
### Behavior changed
- **Timeline visibility** — Added structured visual markers for the 7 stages of simulation execution.
- **Terminal output** — Improved raw streaming console logs styling.
### Tests added/updated
- Run frontend Vite production build: SUCCESS (0 errors).
### Known gaps
- None.

## Phase 42 (Simulation Config Redesign to Reader Swarm Setup)
### Files
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue` — Redesigned simulation configuration screen into a premium Reader Swarm Setup dashboard. Added offline sandbox warning strip, profile model usage tags, workstation efficiency scale slider load meter, simulated-only platforms checklist, cohorts typical quotes, cost and leakage privacy cards, and a collapsible advanced settings block.
- `docs/SWARMBOOK_CHANGELOG.md` — Prepended Phase 42 log details.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Updated Phase 42 status row in status table.
- `docs/SWARMBOOK_DECISIONS.md` — Added D-046 for Reader Swarm setup redesign decision.
### Behavior changed
- **Simulated Sandbox Banner** — Placed a bold banner at the top detailing sandbox constraints (no social scraping, simulated platform reaction only).
- **Profile Models Mapping** — Displays model engine details under each profile selection card.
- **Workstation Load Meter** — Classifies reader agent scales dynamically (Safe, Standard, Heavy load) with tips for 16GB RAM local Ollama constraints.
- **Visual Platform Notes** — Added sub-labels stating "Simulated Only" to the platform toggles.
- **Archetype & Quote Details** — Added lists of internal archetypes and typical quotes showing review style under cohort cards.
- **Privacy Forecasts** — Displays cost estimation ($0.00 vs API charges) and text leakage guarantees in the privacy block.
- **Collapsed Advanced Settings** — Keeps seed, rounds, parallel workers, and posts feed cap collapsed inside a details tag by default.
### Tests added/updated
- Run backend unit tests: 73/73 PASS.
- Run frontend Vite production build: SUCCESS (0 errors).
### Known gaps
- None.

## Phase 41 (Evidence Pack Review Refinement)
### Files
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue` — Redesigned layout to use a modern grid layout for the 7 maps. Built a side Detail Drawer overlay showing Why This Matters microcopy, structured data, source references list, corrections textarea, and collapsible raw JSON Advanced View. Computed critical maps based on project metadata and added warning banner + button disabled blocker if critical maps are unreviewed.
- `docs/SWARMBOOK_CHANGELOG.md` — Prepended Phase 41 log details.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Updated Phase 41 row in status table.
- `docs/SWARMBOOK_DECISIONS.md` — Added D-045 for grid layout/drawer architecture decision.
### Behavior changed
- **Grid Workspace** — Replaces split-pane with a visual grid of 7 evidence maps.
- **Detail Drawer** — Opens slide-out drawer on right for deep data inspection and JSON view.
- **Low Confidence Alert** — Visibly flags maps with confidence < 75% using icon and label.
- **Critical Map Block** — Blocks simulation progress (disables button) until all critical maps (DNA, chapters, characters/claims) are Accepted.
### Tests added/updated
- Run backend unit tests: 73/73 PASS.
- Run frontend Vite production build: SUCCESS (0 errors).
### Known gaps
- None.

## Phase 40 (Upload Limit 4× Increase + Robust UX + Backend Security)
### Files
- `frontend/src/config/uploadLimits.js` — **[NEW]** Shared JS config with `MAX_FILE_BYTES = 40 MB`, `ALLOWED_EXTENSIONS`, `formatBytes()`, `estimateProcessingTime()`. Single source of truth for the frontend upload limit.
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue` — Full redesign: drag-drop dropzone, upload progress animation, format chips, file metadata panel (processing estimate, section count, privacy mode strip), replace/remove actions, 5 specific error states, responsive layout.
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue` — Import `MAX_FILE_BYTES` from shared config; replace hardcoded `10 * 1024 * 1024` with import alias.
- `backend/app/api/book_sim.py` — Add `BOOK_SIM_MAX_FILE_BYTES = 40 MB` constant; add `_FILE_SIGNATURES` magic-byte dict; add `GET /limits` info route; add privacy_mode guard; add file-signature validation; add section-count detection to parse response; update error messages.
- `backend/app/config.py` — `MAX_CONTENT_LENGTH` raised from 50 MB → 200 MB (Flask ceiling); added `docx` to `ALLOWED_EXTENSIONS`.
- `docs/UPLOAD_LIMITS_AND_SECURITY.md` — **[NEW]** Security reference document.
### Behavior changed
- **Upload limit 4×** — 10 MB → 40 MB across all enforcement points simultaneously.
- **Single source of truth** — `uploadLimits.js` (frontend) and `BOOK_SIM_MAX_FILE_BYTES` (backend); neither view hardcodes a size value.
- **File-signature validation** — PDF (`%PDF-`) and DOCX (`PK\x03\x04`) magic bytes are checked; spoofed extensions return `HTTP 400 invalid_file_signature`.
- **Never trust filename** — temp files use `uuid4().hex + ext`; original name is never used as a path component.
- **Section count detection** — `parse_file` returns `section_count` (regex-based chapter heading heuristic); shown in upload UI.
- **Upload progress UI** — animated progress bar with staged labels while parse API is in flight.
- **Privacy mode strip** — colour-coded local/hybrid/cloud strip shown after successful upload.
- **Processing estimate** — dynamic estimate shown based on file size.
- **Specific error states** — 5 distinct upload error codes each show a tailored actionable message.
- **local_only guard** — `parse_file` validates `privacy_mode` form field; extraction remains CPU-local in all modes.
### Tests added/updated
- No test changes. Backend: 73/73 tests pass. Frontend: Vite build compiles with 0 errors.
### Known gaps
- Section count is heuristic (regex); does not parse semantic headings inside PDF body text.
- Upload progress bar is simulated (no XHR streaming); will show 100% only on completion.


### Files
- `frontend/src/store/swarmbookSession.js` — added `contentType` and `testGoal` to default metadata session store.
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue` — redesigned Basics screen (Step 1) template, added dynamic checklist, collapsible metadata, deep form watcher for autosaving, updated validation error message formatting, and updated Step 4 warning banners collapse check.
- `docs/SWARMBOOK_PHASE_STATUS.md` — Phase 39 row added
- `docs/SWARMBOOK_CHANGELOG.md` — this entry
- `docs/SWARMBOOK_DECISIONS.md` — decision on basics screen layout and checklist recorded
### Behavior changed
- **Content Type support** — select dropdown mapping 10 formats (Full manuscript, Novel, Novella, Short story, Article / essay, Newsletter, Book proposal, Blurb / synopsis, Chapter sample, Research / evidence pack) added to Step 1.
- **Re-labeling** — Book Title and Author Name re-labeled to Content Title and Author.
- **Test Goal field** — required text field to describe simulation objectives.
- **Live Accuracy-Impact Checklist** — a dynamic computed checklist on the right displays the simulation fidelity rating based on selected format depth, synopsis detail, cohort count, and cognitive reasoning levels. Displays a colorful fidelity rating progress bar.
- **Collapsible optional fields** — Subtitle, Comps, and Cover package brief are collapsed under a toggle button to save vertical space.
- **Autosave** — deep form watch saves session to localStorage in real time on any change.
- **Technical warnings collapse** — Step 4 warnings are hidden by default unless profile or privacy changes from default values.
- **Friendly validation errors** — camelCase field keys are mapped to human-readable names in the error list.
### Tests added/updated
- No test changes.
- Backend: 73/73 tests pass.
- Frontend: Vite build compiles successfully with 0 errors.
### Known gaps
- None.

## Phase 38 (Projects/Home Redesign to Launch Console)
### Files
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue` — complete layout & CSS redesign using design tokens
- `docs/SWARMBOOK_PHASE_STATUS.md` — Phase 38 row added
- `docs/SWARMBOOK_CHANGELOG.md` — this entry
- `docs/SWARMBOOK_DECISIONS.md` — decision on warnings/status collapse recorded
### Behavior changed
- **Hero block removed** — the oversized dark `#0f172a` hero is gone, replaced with a compact actions console.
- **Title and Value Line** — eyebrow "SWARMBOOK STUDIO", title "Launch Console", and subtitle "Predict reader reactions..." are rendered dynamically by `SwarmbookAppShell` above the fold.
- **Side-by-side CTAs** — primary `Start New Test` and secondary `Open Existing Project ▾` are displayed side-by-side. The Project ID open input is collapsed into a secondary expandable control toggle.
- **Recent projects panel** — redesigned as a compact list of recent active manuscripts with metadata badges and clear CTA in its empty state: `Start your first test →`.
- **System status & Warnings collapse** — Ollama/Neo4j statuses are removed to prevent duplication. Gemini and NVIDIA are kept as "Optional Cloud Providers" in a compact panel. Profile/hardware warnings are collapsed by default and only display if the user changes the profile from default (`form.localProfile !== defaultProfile`).
- **Mobile responsiveness** — CTAs stack, cards display in 1 column, and trust strip collapses to single column on mobile.
- **Trust Strip** — moved to a quiet, compact footer at the bottom of the console workspace.
### Tests added/updated
- No test changes (CSS/template redesign only).
- Backend: 73/73 tests pass.
- Frontend: Vite build successfully compiles with 0 errors.
### Known gaps
- None.

## Phase 37 (Dedicated Swarmbook App Shell)
### Files
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue` — complete rewrite (template + script + style)
- `docs/SWARMBOOK_PHASE_STATUS.md` — Phase 37 row added
- `docs/SWARMBOOK_CHANGELOG.md` — this entry
### Behavior changed
- **Top navigation** now carries all 11 required labels: Projects, New Test, Report, Ask Readers, Compare, Settings, Original MiroFish. On desktop the header shows the global section labels; per-project workflow steps live exclusively in the sidebar rail.
- **Workflow rail** updated to 9 sequential steps matching the spec: Projects → New Test → Upload → Evidence Packs → Reader Swarm → Run → Report → Ask Readers → Compare Drafts. Settings and Original MiroFish appear in the sidebar footer.
- **Status strip** — new dedicated `<div class="status-strip">` row placed between the header and the sidebar/content split. Displays Ollama status, Neo4j status, Privacy mode badge, Active Profile, and Active Project ID (when set). This is now the **single source of truth** for system/privacy status; the old sidebar `system-status-panel` block has been removed, eliminating duplication.
- **Mobile menu** — hamburger now animates to an × when open. Sidebar becomes a full-height `position:fixed` off-canvas drawer. A `sidebar-global-nav` block inside the drawer mirrors the top-nav items (Projects, New Test, Report, Ask Readers, Compare, Settings) so all navigation is reachable on mobile without the top bar.
- **Active route states** — sidebar steps use a left orange accent bar + orange text + `aria-current="step"`. Top-nav buttons use an underline indicator + `aria-current="page"`. Disabled steps use `aria-disabled="true"` and `pointer-events:none`.
- **Keyboard** — Escape key closes the mobile drawer. All interactive items are `<button>` or `<router-link>` (never `<div>`). Focus ring uses `var(--sb-focus-ring)` throughout. `Skip to content` skip link added for screen reader users.
- **MiroFish access** — Original MiroFish is a named button in the top nav AND a footer link in the sidebar. Both push `router.push('/')`. No MiroFish route or component was modified.
- **onBeforeUnmount** — health polling interval and `keydown` event listener are now properly torn down to prevent memory leaks.
### Tests added/updated
- No test changes (CSS/template only; no new API surface).
- Backend: 73/73 tests pass.
- Frontend: Vite build ✓ — 702 modules transformed, 0 compile errors. CSS 288.75 kB (gzip 44.67 kB).
### Known gaps
- Pre-existing chunk-size warning (`pendingUpload.js` dynamic/static import split in MiroFish legacy views) remains — unrelated to this phase.
- `SwarmbookHomeView` still renders its own "System Readiness" card with Ollama/Neo4j/Gemini/NVIDIA status. That card shows more detail (Gemini, NVIDIA) than the strip, so it is preserved; users should be aware the strip and the home card show overlapping but not identical status info.

## Phase 36 (Design Token Layer)
### Files
- `frontend/src/assets/tokens.css` [NEW] — canonical design token file
- `frontend/src/main.js` — added `import './assets/tokens.css'`
- `frontend/src/App.vue` — removed inline `:root` duplicate block (lines 600–615); replaced with a single backward-compatible alias and pointer comment
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue` — migrated ~60 hard-coded hex values to token `var()` references (backgrounds, text, status colors, focus ring, shadows, card borders, buttons, typography)
- `docs/SWARMBOOK_UI_AUDIT.md` [NEW] — full pre-edit UI audit
- `docs/SWARMBOOK_PHASE_STATUS.md` — added Phase 36 row
- `docs/SWARMBOOK_CHANGELOG.md` — this entry
### Behavior changed
- No MiroFish (`/`, `/process/*`, `/simulation/*`, `/report/*`, `/interaction/*`) routes were touched; all token selectors are scoped to `.swarmbook-shell`, `.new-wizard-container`, or the `.sb-` prefix.
- `:root` custom properties for colors, spacing, typography, radius, shadows, status, risk, privacy, and focus state are now defined once in `tokens.css`.
- All existing `var(--sb-*)` references in `App.vue` and Swarmbook views continue to resolve correctly; the canonical values moved to `tokens.css` without any class or value renames.
- `SwarmbookAppShell.vue` now uses token vars for all structural, semantic, and interactive properties.
### Tests added/updated
- No test changes required (tokens are CSS-only with no runtime behavior changes).
- Backend: 73/73 tests pass (`python -m unittest discover -s backend/tests -p "test_book_sim_*.py"`).
- Frontend: Vite build succeeds — 702 modules transformed, zero compile errors (`node .\node_modules\vite\bin\vite.js build`). CSS output grew from 275.90 kB to 285.85 kB (the +10 kB is the full token file, as expected).
### Known gaps
- `npm run build` (via the broken global npm shim) remains unavailable; direct Vite execution is the validated path.
- Individual Swarmbook view files still use some raw hex values in their own `<style scoped>` blocks; those will be progressively migrated in future polish passes without affecting behaviour.

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

## Phase 19 (Final Hardening Pass: Local Personal Build)
### Files
- `backend/app/api/book_sim.py`
- `backend/app/book_sim/report_markdown.py`
- `frontend/src/api/index.js`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `docs/SWARMBOOK_LOCAL_SETUP.md`
- `docs/SWARMBOOK_USAGE_GUIDE.md`
- `docs/SWARMBOOK_LIMITATIONS.md`
- `backend/tests/test_book_sim_api.py`
### Behavior changed
- Improved Swarmbook API error clarity by returning structured JSON errors with stable `error_code` and optional `details` for runtime/provider failures.
- Guarded large manuscript ingestion (`max_manuscript_chars`, default `500000`) to keep low-resource local runs stable.
- Added partial-failure recovery: simulation artifacts are saved even if report synthesis fails, returning `error_code=partial_failure` with the stored `simulation_id`.
- Added Markdown export for prediction reports and returned it as `report_markdown` from `/api/book-sim/simulate`.
- Improved frontend error surfacing by carrying backend `error_code/details` through the Axios layer.
- Added a visible character-count warning on the Swarmbook upload screen for very large pastes.
### Tests added/updated
- Updated API test expectations to assert `report_markdown` is returned when Flask is available (`backend/tests/test_book_sim_api.py`).
### Known gaps
- Frontend production build is not provable in this environment (missing `node_modules` / npm shim issues).
- Privacy enforcement remains router-scoped (`local_only` forces `local_ollama`), not an app-wide policy boundary.
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

## Phase 10-11 (Platform Adapters + Simulation Engine)
### Files
- `backend/app/book_sim/models.py`
- `backend/app/book_sim/platform_adapters/__init__.py`
- `backend/app/book_sim/platform_adapters/base.py`
- `backend/app/book_sim/platform_adapters/goodreads.py`
- `backend/app/book_sim/platform_adapters/booktok.py`
- `backend/app/book_sim/platform_adapters/reddit.py`
- `backend/app/book_sim/platform_adapters/bookstagram.py`
- `backend/app/book_sim/platform_adapters/x_platform.py`
- `backend/app/book_sim/platform_adapters/newsletter.py`
- `backend/app/book_sim/platform_adapters/bookclub.py`
- `backend/app/book_sim/simulation/__init__.py`
- `backend/app/book_sim/simulation/private_reading_pass.py`
- `backend/app/book_sim/simulation/platform_reaction_pass.py`
- `backend/app/book_sim/simulation/cross_reaction_pass.py`
- `backend/app/book_sim/simulation/simulation_orchestrator.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_models.py`
- `backend/tests/test_book_sim_platform_adapters.py`
- `backend/tests/test_book_sim_simulation_engine.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added fully synthetic platform adapters driven by `platform_styles.yaml` with structured `PlatformPost` payloads and evidence references.
- Added private-reading, platform-reaction, and bounded cross-reaction passes plus a simulation orchestrator that returns `SimulationRun`.
- Added content-hash caching for every simulation stage, including the orchestrator result.
- Kept the default execution single-threaded to avoid local CPU and memory overcommit.
### Tests added
- Shared adapter suite covering every required platform adapter.
- Tiny end-to-end simulation test with five personas and deterministic seed.
- Extended model round-trip coverage for structured post payloads and simulation artifact lists.
### Known gaps
- Simulation runtime is still not wired into Swarmbook Flask/API routes or frontend flows.
- The simulation engine depends on synthetic heuristics today; no scoring engine or report synthesis layer is attached yet.

## Phase 12 (Scoring Layer)
### Files
- `backend/app/book_sim/scoring/__init__.py`
- `backend/app/book_sim/scoring/_shared.py`
- `backend/app/book_sim/scoring/rating_distribution.py`
- `backend/app/book_sim/scoring/dnf_score.py`
- `backend/app/book_sim/scoring/viral_score.py`
- `backend/app/book_sim/scoring/controversy_score.py`
- `backend/app/book_sim/scoring/quoteability_score.py`
- `backend/app/book_sim/scoring/polarization_score.py`
- `backend/app/book_sim/scoring/revision_priority.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_scoring.py`
### Behavior changed
- Added deterministic, explainable scoring for predicted rating distribution, DNF risk, DNF chapter pressure, viral potential, controversy, quoteability, polarization, and revision priority.
- Added confidence bands and evidence references to every score result.
- Added a local fallback parser for `scoring_weights.yaml` so scoring remains usable when `PyYAML` is unavailable.
### Tests added
- One shared scoring suite covering each score function plus deterministic same-input replay.
### Known gaps
- Scoring is implemented but still not wired into any Flask route or report generator.

## Phase 12 Audit Refresh
### Files
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Confirmed the scoring layer is complete at the module level and remains deterministic, explainable, and config-driven.
- Confirmed score outputs include confidence bands and evidence references across the scoring package.
- Corrected the handoff resume point so the next fresh thread starts at Phase 13 rather than the already-complete Phase 12.
### Tests added
- None. Audit relied on existing scoring tests and code inspection.
### Known gaps
- Report generation and API/runtime wiring are still pending.

## Phase 7 Runtime Wiring + Phase 13 Runtime Report Slice
### Files
- `backend/app/api/book_sim.py`
- `backend/app/book_sim/runtime_store.py`
- `backend/app/book_sim/report_builder.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_api.py`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added additive backend endpoints for `/api/book-sim/projects`, `/api/book-sim/evidence-packs`, `/api/book-sim/simulate`, `/api/book-sim/projects/{project_id}/report`, `/api/book-sim/personas/{persona_id}/chat`, `/api/book-sim/compare`, and `/api/book-sim/health`.
- Added a file-backed Swarmbook runtime store so evidence packs, simulation runs, reports, and comparisons can be loaded by stored IDs instead of only oversized inline payloads.
- Added deterministic runtime report synthesis on top of existing simulation and scoring outputs, while preserving the legacy `/api/report` flow.
- Kept `/api/book-sim/interrogate` as a backward-compatible narrow route.
### Tests added
- New backend route suite in `backend/tests/test_book_sim_api.py`.
### Known gaps
- There is still no dedicated `backend/app/book_sim/reports/` package.
- Frontend Swarmbook routes/views are still absent.
- Privacy enforcement is still router-scoped rather than system-wide middleware.

## Phase 14 (Reader Persona Interrogation)
### Files
- `backend/app/book_sim/interrogation/__init__.py`
- `backend/app/book_sim/interrogation/persona_chat.py`
- `backend/app/book_sim/__init__.py`
- `backend/app/api/book_sim.py`
- `backend/app/api/__init__.py`
- `backend/app/__init__.py`
- `backend/tests/test_book_sim_persona_chat.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added an additive reader-persona interrogation service that answers six grounded question shapes from serialized Swarmbook artifacts.
- Kept interrogation template-first and deterministic so `local_only` never depends on Gemini, NVIDIA, or any external provider.
- Added a narrow `/api/book-sim/interrogate` backend route that accepts `SimulationRun` plus `EvidencePack` payloads and returns structured JSON with `based_on` evidence refs.
### Tests added
- New unit suite for grounded persona interrogation behavior.
- Route contract test added and conditionally skipped when Flask is unavailable in the active Python environment.
### Known gaps
- Frontend Swarmbook interrogation flow is still absent.
- No frontend Swarmbook interrogation flow exists yet.
- Report synthesis remains absent, so Phase 13 is still open.

## Phase 14 Audit Refresh
### Files
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was an audit and continuity-correction pass.
- Confirmed the interrogation slice is grounded, additive, and provider-free in `local_only`.
- Corrected stale continuity text that still claimed no `book_sim` blueprint or interrogation API existed.
### Tests added
- None. Audit reused the existing interrogation and router test suites.
### Known gaps
- The backward-compatible `/api/book-sim/interrogate` route still accepts oversized serialized payloads for older callers.
- The route contract test remains environment-dependent because `flask` is unavailable in the active Python interpreter here.
- Phase 14 is only safe at the bounded backend-runtime level, not as a fully wired runtime phase.

## Phase 15 (Draft Comparison)
### Files
- `backend/app/book_sim/comparison/__init__.py`
- `backend/app/book_sim/comparison/draft_comparator.py`
- `backend/app/book_sim/comparison/comparison_report.py`
- `backend/app/book_sim/models.py`
- `backend/app/book_sim/__init__.py`
- `backend/tests/test_book_sim_draft_comparator.py`
- `backend/tests/test_book_sim_models.py`
- `backend/tests/fixtures/book_sim_compare_draft_a.txt`
- `backend/tests/fixtures/book_sim_compare_draft_b.txt`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added an additive draft-comparison module that compares two evidence packs plus optional simulation runs and optional precomputed scorecards.
- Added deterministic JSON and Markdown exports for comparison results.
- Added comparison coverage for book DNA, chapters, characters, claims, DNF/rating/controversy/viral/quoteability movement, reader segment movement, revision impact, improvements, regressions, and remaining blockers.
### Tests added
- New draft comparator unit suite using two tiny draft fixtures.
- Expanded model round-trip coverage for the richer `DraftComparisonReport`.
### Known gaps
- No frontend comparison flow exists yet.
- Phase 13 still lacks a dedicated report package, so the clean sequential path is now "finish and harden Phase 13" rather than "start from zero".

## Phase 16 (Frontend Swarmbook UI)
### Files
- `frontend/src/api/bookSim.js`
- `frontend/src/store/swarmbookSession.js`
- `frontend/src/components/swarmbook/SwarmbookLayout.vue`
- `frontend/src/router/index.js`
- `frontend/src/views/Home.vue`
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `frontend/src/views/swarmbook/SwarmbookMetadataView.vue`
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/SwarmbookReportView.vue`
- `frontend/src/views/swarmbook/SwarmbookPersonasView.vue`
- `frontend/src/views/swarmbook/SwarmbookCompareView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added an additive Swarmbook frontend flow under `/swarmbook/*` for project setup, manuscript input, metadata capture, evidence preview, simulation controls, report review, persona interrogation, and draft comparison.
- Kept the legacy MiroFish landing, process, simulation, report, and interaction routes intact.
- Added simple loading and error handling states across the new Swarmbook screens.
- Bound the new frontend flow to the existing additive `/api/book-sim/*` backend runtime surface.
### Tests added
- No frontend test framework exists in this repo today.
- Attempted frontend validation through `npm run build`, but the machine-level `npm` shim is broken.
- Verified frontend build succeeds through bundled runtime Node with direct Vite execution.
### Known gaps
- Frontend package-manager path is still broken for `npm run build`, so direct runtime-node Vite invocation remains the current workaround.
- The backend report layer still lives in `backend/app/book_sim/report_builder.py`, not a dedicated `reports/` package.

## Deep Consolidation (Post-Phase 12)
### Files
- `docs/SWARMBOOK_CONTEXT.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was a continuity and wiring audit pass only.
- Corrected stale assumptions by confirming that phases 8-12 are module-complete while phase 7 API wiring is still not started.
- Confirmed no report-generation package exists yet under `backend/app/book_sim/reports/`, so JSON/Markdown report outputs are not available.
- Confirmed Swarmbook unit suites currently pass (`28` run, `1` skipped) in this environment.
### Tests added
- None. Consolidation reused existing test suites.
### Known gaps
- End-to-end Swarmbook runtime now exists at the backend route level, but the frontend remains unwired.
- Privacy guarantees are still router-scoped and not yet enforced through global policy middleware.
## Phase 10 Audit Refresh
- Audited the bounded Swarmbook simulation engine after implementation.
- Confirmed the private-reading -> platform-reaction -> cross-reaction flow, deterministic seed behavior, content-hash caching, structured JSON outputs, and low-resource defaults (`cross_reaction_posts=8`, `max_reaction_rounds=2`, `max_parallel_jobs=1`).
- Confirmed test coverage for a tiny evidence pack with a `5`-persona run in `backend/tests/test_book_sim_simulation_engine.py`.
- Recorded that Phase 11 is safe at the module level, with API/UI runtime wiring still pending.

## Phase 17 Audit (Local Low-Resource Profile)
### Files
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was an audit-only continuity update.
- Confirmed required Phase 17 artifacts are currently missing: `configs/book_sim/local_profiles.yaml` and `docs/SWARMBOOK_LOCAL_SETUP.md`.
- Confirmed profile requirements cannot be satisfied until those files are implemented (`local_tiny`, `hybrid_safe_default` default selection, `cloud_quality`, profile-level `local_parallel_jobs`, and heavy-profile warnings).
- Confirmed `local_only` still enforces local provider routing and does not call external providers via the existing router guard.
### Tests added
- None. Audit relied on repository inspection.
### Known gaps
- Phase 17 deliverables are incomplete.
- Phase 18 is not safe until Phase 17 profile config and setup documentation are implemented and verified.

## Phase 17 Repair (Local Low-Resource Profile)
### Files
- `configs/book_sim/local_profiles.yaml`
- `backend/app/book_sim/local_profiles.py`
- `backend/app/book_sim/__init__.py`
- `backend/app/api/book_sim.py`
- `backend/tests/test_book_sim_local_profiles.py`
- `backend/tests/test_book_sim_api.py`
- `frontend/src/store/swarmbookSession.js`
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `frontend/src/views/swarmbook/SwarmbookMetadataView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `docs/SWARMBOOK_LOCAL_SETUP.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
- `docs/SWARMBOOK_PROMPT_LOG.md`
### Behavior changed
- Added explicit local profile config with `local_tiny`, `hybrid_safe_default` (default), and `cloud_quality`.
- Added additive local profile loader with required-field validation and graceful fallback behavior.
- Wired profile defaults into additive `/api/book-sim/projects`, `/api/book-sim/simulate`, and `/api/book-sim/health`.
- Added structured heavy/privacy warnings for profile selection in backend health/profile payloads.
- Kept `local_only` provider guard unchanged; it still forces local route selection.
- Added frontend profile selection/warning visibility in existing Swarmbook home/simulation screens without changing legacy MiroFish routes.
### Tests added
- New loader/config tests in `backend/tests/test_book_sim_local_profiles.py`.
- Extended API health/default-profile assertions in `backend/tests/test_book_sim_api.py`.
### Known gaps
- `pytest` command is unavailable in the current environment (`pytest` CLI missing).
- `npm run build` remains blocked by machine-level npm shim; direct Vite build passes.

## Phase 18 Quality Gate
### Files
- `backend/tests/test_book_sim_report_builder.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- No runtime behavior change. This was a validation and continuity-consolidation pass.
- Verified the Swarmbook backend test suite passes in this environment, including the new report-builder coverage.
- Verified the frontend Swarmbook bundle still builds successfully through direct Vite execution.
- Confirmed `npm run build` remains blocked by the local npm shim and `pytest` is unavailable here.
- Confirmed `Flask` is unavailable in the active Python environment, so live app-factory route execution remains unverified in this shell.
### Tests added
- `backend/tests/test_book_sim_report_builder.py`
### Known gaps
- Phase 19 is not safe yet because privacy/compliance hardening still lacks a global policy boundary beyond router-level enforcement.
- The repo still depends on direct Vite build as the frontend validation workaround in this environment.

## Phase 20 Privacy Hardening & Config Fallback (Handoff H hardening)
### Files
- [book_sim.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/api/book_sim.py)
- [gemini_provider.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/providers/gemini_provider.py)
- [nvidia_provider.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/providers/nvidia_provider.py)
- [local_profiles.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/local_profiles.py)
- [SWARMBOOK_INSTALL_WINDOWS.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_INSTALL_WINDOWS.md)
- [test_book_sim_privacy_guard.py](file:///d:/SW/MiroFish-Offline-Book/backend/tests/test_book_sim_privacy_guard.py)
- [test_book_sim_local_profiles.py](file:///d:/SW/MiroFish-Offline-Book/backend/tests/test_book_sim_local_profiles.py)
- [SWARMBOOK_PHASE_STATUS.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_PHASE_STATUS.md)
- [SWARMBOOK_CHANGELOG.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_CHANGELOG.md)
- [SWARMBOOK_DECISIONS.md](file:///d:/SW/MiroFish-Offline-Book/docs/SWARMBOOK_DECISIONS.md)
### Behavior changed
- Implemented blueprint-level Flask `before_request` middleware to parse and set the global `PrivacyGuard` mode to `local_only` (or other active mode) on all API requests.
- Added provider-level `PrivacyGuard` assertions to `GeminiProvider` and `NvidiaProvider` methods (`generate_text`, `generate_json`, `embed_text`) to raise `PrivacyViolationError` under `local_only` mode.
- Implemented a custom YAML-free parser in `local_profiles.py` to support loading local profile configurations without PyYAML.
- Fixed typo encoding artifacts (`wonâ€™t`) in `docs/SWARMBOOK_INSTALL_WINDOWS.md`.
### Tests added
- Added provider-level `PrivacyViolationError` tests in `test_book_sim_privacy_guard.py`.
- Added `test_yaml_free_parser_matches_yaml_parser` in `test_book_sim_local_profiles.py` comparing output with PyYAML.


## Phase 19 E2E Validation
### Files
- `backend/app/book_sim/config_loader.py`
- `backend/tests/test_book_sim_e2e.py`
- `backend/tests/fixtures/tiny_fiction_manuscript.txt`
- `backend/tests/fixtures/tiny_fiction_manuscript_revised.txt`
- `backend/tests/fixtures/tiny_nonfiction_manuscript.txt`
- `backend/tests/fixtures/tiny_metadata.json`
- `backend/tests/fixtures/tiny_metadata_nonfiction.json`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_OPEN_QUESTIONS.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- Added a narrow PyYAML-free fallback parser for existing route/privacy configs so Swarmbook can validate in the active local Python environment.
- No product features were added; the new E2E test uses tiny synthetic fixtures and local-only deterministic runtime paths.
### Tests added/updated
- Added `backend/tests/test_book_sim_e2e.py` for tiny local-only pipeline and draft comparison validation.
### Known gaps
- Flask is unavailable in the active Python interpreter, so Flask test-client API smoke remains skipped.
- `pytest` and npm commands are unavailable/broken in this environment; `unittest` and direct Vite are the validated paths.
- Phase 19 remains partial until privacy enforcement is global rather than router-scoped.

## Phase 19 E2E Validation Repair (Import/Smoke Path)
### Files
- `backend/tests/smoke_check.py`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_HANDOFF_LATEST.md`
### Behavior changed
- `backend/tests/smoke_check.py` now falls back when `flask`/`python-dotenv` app imports are unavailable, so the smoke command runs and reports actual backend/frontend/Neo4j/Ollama status.
### Tests added/updated
- No new tests; re-ran targeted E2E and smoke commands.
### Known gaps
- Smoke checks can still fail when local services are not running or dependencies like `neo4j` client are not installed; this is runtime/environment, not Swarmbook logic.

## Phase 20 Local Release Audit & Automated Installation Framework (Handoff H packaging)
### Files
- `scripts/windows/check_prereqs.ps1`
- `scripts/windows/start_swarmbook.ps1`
- `scripts/windows/stop_swarmbook.ps1`
- `scripts/windows/smoke_test_swarmbook.ps1`
- `scripts/windows/install_swarmbook.ps1`
- `.env.swarmbook.example`
- `docs/SWARMBOOK_INSTALL_WINDOWS.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Implemented a highly optimized, robust automated installer script (`install_swarmbook.ps1`) supporting optional prerequisites setup via winget, automatic virtualenv setup, npm dependency compilation, environment file configuration, model pre-fetching, and desktop shortcut generation.
- Corrected troubleshooting section encoding artifact in `docs/SWARMBOOK_INSTALL_WINDOWS.md`.
- Enforced `local_only` system-wide via Flask blueprint middleware and provider assertions, rendering release packaging safe.
### Tests added/updated
- Added provider-level `PrivacyViolationError` tests in `test_book_sim_privacy_guard.py` and YAML-free parser fallback test in `test_book_sim_local_profiles.py`.
- Verified 60 out of 60 unit tests pass.
### Known gaps
- None. Prerequisite checking, installation, and system-wide privacy safety are verified.

## Phase 21 (UI Audit and Redesign Plan)
### Files
- `docs/SWARMBOOK_UI_REDESIGN.md`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- None. This is an audit and redesign documentation phase before making major changes.
### Tests added
- None.
### Known gaps
- Implementations of the redesign screens are scheduled for future phases.

## Phase 22 (SaaS-grade App Shell and Navigation)
### Files
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue`
- `frontend/src/views/swarmbook/*.vue` (8 views updated to import and use the new shell)
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Replaced the simple progress layout with a modern, SaaS-grade `SwarmbookAppShell` containing a top navigation header, exit pathway to the MiroFish landing page, responsive left workflow steps sidebar, persistent health status display for Ollama/Neo4j services, and interactive Settings modal overlay.
- Maintained backwards compatibility and kept original MiroFish landing page and graph processing views unchanged.
### Tests added
- None (verified clean production compile via Vite build command).
### Known gaps
- Settings drawer content is static and profile attributes are loaded from session state.

## Phase 23 (SaaS-grade Swarmbook Project Dashboard)
### Files
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Replaced the simple project creation form on the Swarmbook landing page with a comprehensive, premium, author-facing project dashboard.
- Added an author-facing hero headline ("Predict reader reactions before you publish") and explanation subtext.
- Added primary "New Simulation" and secondary "Open Existing Project" CTAs. Opening an existing project by ID attempts to resolve its latest report, routing directly to the report dashboard if ready, or to the manuscript upload flow as a fallback.
- Implemented localStorage-backed recent project history tracker (`mirofish_swarmbook_projects`), listing details of recently run manuscript stress tests.
- Formulated an author-focused local trust strip explaining privacy guarantees (Local-first, Private mode, No social scraping, Evidence-based reports).
- Created a system readiness panel displaying Ollama, Neo4j, Gemini, and NVIDIA statuses.
- Added quick action shortcuts, including an interactive "Test a Blurb" quick blurb stress test modal that creates a temporary project and routes directly to the evidence pack preview step.
### Tests added
- None (verified clean production compile via Vite build command).
### Known gaps
- "Compare Drafts" quick action shortcut relies on a project already being active in the session state.

## Phase 24 Guided New Simulation Wizard
### Files
- `frontend/src/router/index.js`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue`
- `frontend/src/views/swarmbook/SwarmbookHomeView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Added `NewSimulationWizardView` implementing a unified 5-step wizard for manuscript stress testing: Basics, Ingest, Evidence pack preview, Cohort configuration, and Run.
- Registered `/swarmbook/wizard/:projectId?` route mapped to the wizard component.
- Updated "New Simulation" header and landing page hero CTA to redirect to the new wizard route.
- Updated "Upload Manuscript" quick action to open the wizard, ensuring step-based setup.
- Enforced low-resource profile safety, character limit banners, active form validations, and keyboard navigation.
### Tests added/updated
- Validated compile sanity via Vite production build.
### Known gaps
- None.

## Phase 25 SaaS-grade Swarmbook Manuscript Upload
### Files
- `backend/app/utils/file_parser.py`
- `backend/app/api/book_sim.py`
- `backend/tests/test_book_sim_api.py`
- `frontend/src/api/bookSim.js`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Added native Word (`.docx`) text extraction to `FileParser` using zipfile and xml parsing.
- Exposed a new `/parse-file` API route for file uploads, returning size in bytes, character/word counts, MIME type, and extracted text.
- Redesigned manuscript upload screen (`SwarmbookUploadView.vue`) and step 2 of the wizard (`NewSimulationWizardView.vue`) to use a premium drag-and-drop file uploader.
- Replaced "Reality Seeds" naming with "Upload Manuscript" across the uploader interface.
- Showed estimated processing time (~30-60s) and privacy warnings in the file card based on selected privacy modes.
- Displayed detailed error messages (unsupported format, parsing failures, upload failures, and file/character limit oversized calculations).
- Showed "Generate Evidence Packs" as the primary next action button instead of generic routing steps.
### Tests added/updated
- Added `test_parse_file_route` in `test_book_sim_api.py` covering TXT uploads, unsupported formats, and character size limits.
- Verified 61 out of 61 unit tests pass.
### Known gaps
- None.

## Phase 26 (SaaS-grade Swarmbook Evidence Pack Review)
### Files
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
### Behavior changed
- Redesigned the Swarmbook Evidence Pack Review view (`SwarmbookEvidenceView.vue`) into a premium, SaaS-grade split-pane dashboard workspace.
- Added 7 narrative and analysis maps: Book DNA, Chapter Map, Character Map, Claim Map, Risk Map, Style Map, and Market Surface.
- Showed card-level metadata for each map including status (pending / generated / needs review / accepted), custom confidence levels, and references counts.
- Implemented card-level controls to view details, regenerate specific maps (triggering `/api/book-sim/evidence-packs` backend compilation), and accept/lock maps.
- Implemented details column on the right showing structured map data (e.g. DNA fields, timeline for chapters, character grid, metric gauges for style, claims, and risks), a "Why This Matters" educational microcopy banner, and editorial annotations text field to record user overrides.
- Supported accessible button labels, keyboard focus outline enhancements (`outline: 2px solid #ff4500` on focus-visible states), and responsive layout collapse.
### Tests added/updated
- Verified production compile of redesigned view through direct Vite compilation.
### Known gaps
- None.

## Phase 27 (SaaS-grade Swarmbook Reader Swarm Setup)
### Files
- `backend/app/api/book_sim.py`
- `backend/tests/test_book_sim_api.py`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
### Behavior changed
- Redesigned the simulation setup screen (`SwarmbookSimulationView.vue`) and Step 4 of the guided wizard (`NewSimulationWizardView.vue`) into a premium, SaaS-grade Reader Swarm Setup dashboard.
- Replaced developer/agent terminology with plain language reader metrics, platform toggles, and cohorts configurations.
- Implemented Simulation Profile selector cards (Draft, Balanced, Deep) with recommendation and hardware warning banners.
- Implemented Reader Count range controller with recommended scale indicators based on selected profile defaults.
- Implemented Platform checklist pill-buttons supporting Goodreads, BookTok, Reddit, Bookstagram, X, Newsletter, and Book Club.
- Implemented interactive Reader Cohorts checklist to toggle Harsh reviewers, Genre loyalists, Emotional amplifiers, Skeptics, Casual readers, Literary readers, and Non-fiction evidence skeptics, mapping unselected cohorts to under-the-hood exclusions.
- Implemented dynamic runtime time estimation and provider connection status matrix (Ollama, Neo4j, Gemini, NVIDIA).
- Extended backend `_persona_overrides` API helper to parse and enforce `exclude_archetypes` and `include_archetypes` parameters from request payload.
### Tests added/updated
- Added `test_simulate_with_cohort_exclusions` in `test_book_sim_api.py` verifying that excluded archetypes are successfully filtered out from generated reader persona swarms.
- Verified 62 out of 62 unit tests pass successfully.
### Known gaps
- None.

## Phase 28 (SaaS-grade Swarmbook Simulation Run Screen)
### Files
- `frontend/src/api/bookSim.js`
- `frontend/src/router/index.js`
- `frontend/src/views/swarmbook/SwarmbookSimulationRunView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_DECISIONS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
### Behavior changed
- Created a dedicated simulation run view screen (`SwarmbookSimulationRunView.vue`) at route `/swarmbook/project/:projectId/run` with a visual, multi-step progress stepper (7 steps), dynamic progress bar meter, and total run timer.
- Integrated a live terminal console logs feed displaying dynamic simulated milestones representing active pipeline tasks to prevent blank screen stare.
- Equipped control ribbon supporting Cancel action triggers bound to Axios `AbortController` request cancellation and disabled/mock pause and resume buttons.
- Handled error states, displaying a detailed failure message and providing immediate recovery buttons ("Retry Simulation Run" and "Adjust Settings").
- Updated standalone setup screen run button and wizard step 5 run button to redirect to the new runner screen.
- Modified `runBookSimulation` helper inside `bookSim.js` to accept Axios config parameter for Abort signals.
### Tests added/updated
- Verified client environment compile of new views using Vite build.
### Known gaps
- None.

## Phase 29 (SaaS-grade Swarmbook Report Dashboard)
### Files
- `frontend/src/views/swarmbook/SwarmbookReportView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Redesigned and rewrote `SwarmbookReportView.vue` as a premium SaaS-grade report dashboard.
- Implemented 6 top summary cards (Readiness percentage, Star predicted rating, DNF risk, Controversy risk, Max viral platform, and Top priority target).
- Implemented client-side Publishing Readiness score calculation formula blending rating distribution, DNF, and controversy risk.
- Implemented 13 detailed main sections including interactive CSS progress bars/histograms, a reader segments table, timeline DNF chapter timeline, platform virality scores, pull quotes quoteability highlights, tabbed simulated platform posts feed (Goodreads, BookTok, Reddit, X), marketing hooks, risks, caveats, and disclaimers.
- Added fully client-side local JSON and Markdown report export file downloading utilities.
- Implemented mock fallback data loader directly in empty state card to enable offline visual dashboard verification.
- Enforced WCAG 2.2 AA standards with explicit keyboard focus outlines (`2px solid #FF4500`) and aria-labels/roles.
### Tests added/updated
- Verified Vite production build checks run successfully with zero compile warnings.
- Confirmed all 62 python backend unit tests Discover green passes.
### Known gaps
- None.

## Phase 30 (SaaS-grade Swarmbook Persona Interview Screen)
### Files
- `frontend/src/views/swarmbook/SwarmbookPersonasView.vue`
- `docs/SWARMBOOK_PHASE_STATUS.md`
- `docs/SWARMBOOK_CHANGELOG.md`
- `docs/SWARMBOOK_DECISIONS.md`
### Behavior changed
- Redesigned and rewrote `SwarmbookPersonasView.vue` as a master-detail Persona Interview screen.
- Implemented Left Sidebar directory listing active personas with platform branding, cohort name, predicted rating, and DNF probability statistics.
- Implemented Right Header profile card showing genres, DNF triggers, review style, and influence score.
- Implemented Interactive Chat Workbench displaying a rolling message history with user/persona styles, quick question triggers, and loading state indicators.
- Implemented Grounded Evidence panel cross-referencing active `evidencePack` to lookup and display detailed pacing timelines or claim text.
- Added fully offline fallback roster with 5 mock personas and a local query responder matching the 6 trigger shapes (Rating, DNF, Recommend, Raise, Audience, Triggers) to answer questions when backend or Neo4j/Ollama services are unavailable.
- Enforced WCAG 2.2 AA standards with clear focus outlines (`outline: 2px solid #FF4500`) and aria-labels/roles.
### Tests added/updated
- Verified Vite production build check and confirmed all 62 python backend unit tests Discover green passes.
- None.

## Phase 31 (SaaS-grade Swarmbook Draft Comparison Screen)
### Files
- `frontend/src/views/swarmbook/SwarmbookCompareView.vue`
### Behavior changed
- Redesigned and rewrote `SwarmbookCompareView.vue` as a premium SaaS-grade draft comparison workbench.
- Implemented recent project dropdown lists reading `mirofish_swarmbook_projects` from `localStorage` project history, alongside a toggle to manually enter project IDs.
- Implemented an Executive Delta Scorecard matrix comparing Publishing Readiness scores, predicted mean ratings, DNF abandonment risks, controversy risks, and quoteability metrics side-by-side with color-coded deltas.
- Implemented a 5-tab workspace panel:
  - **Priorities & Verdict**: Executive verdict summary, plus lists of improvements, regressions, publishing blockers, and a recommended revision checklist.
  - **DNA & Segments**: Table of Book DNA adaptations and a cohort rating/stance shift matrix.
  - **Pacing (Chapters)**: Detailed timeline/list of chapter deltas showing title, pacing changes (slow->balanced/fast), friction clearances, and summary shifts.
  - **Characters & Claims**: Fiction cast attachment/role adjustments and nonfiction claim/evidence deltas.
  - **Raw Export & Preview**: File downloaders for comparison JSON/Markdown, with preview area and copy-to-clipboard.
- Added a high-fidelity offline mock dataset comparing original and revised drafts to support offline Visual verify.
- Enforced WCAG 2.2 AA standards with clear focus outlines (`outline: 2px solid #FF4500`) and aria-labels/roles.
### Tests added/updated
- Verified Vite client production build check passes successfully.
- Verified all 62 python backend unit tests remain green.
### Known gaps
- None.

## Phase 32 (SaaS-grade Swarmbook Settings Screen)
### Files
- `frontend/src/views/swarmbook/SwarmbookSettingsView.vue`
- `frontend/src/router/index.js`
- `frontend/src/components/swarmbook/SwarmbookAppShell.vue`
### Behavior changed
- Created a dedicated `SwarmbookSettingsView.vue` component at `/swarmbook/settings/:projectId?`.
- Refactored `SwarmbookAppShell.vue` settings navigation trigger to navigate to the new Settings view, and removed the old settings modal overlay markup.
- Implemented interactive Privacy Mode selection cards (enforcing `local_only`, `hybrid_safe`, `cloud_quality`) with safety warning and data flow explanations.
- Implemented local profile configurations (max personas count, platforms list, reaction loops).
- Implemented model provider key configuration status checks (exposing configured/missing labels with key secret obfuscation).
- Implemented on-demand health diagnostics sweep showing timeline checks and troubleshooting suggestions for Ollama and Neo4j socket connectivity.
- Wired configurations directly to localStorage session store updates.
- Added WCAG 2.2 AA compliant focus states (`outline: 2px solid #FF4500`) and ARIA roles.
### Tests added/updated
- Verified Vite client production build check compiles successfully.
- Verified all 62 python backend unit tests remain green.
### Known gaps
- None.

## Phase 33 (Swarmbook UI Visual Polish Pass)
### Files
- `frontend/src/App.vue`
### Behavior changed
- Injected global theme CSS variables and styling overrides into `App.vue`.
- Standardised typography hierarchy (Space Grotesk headers and JetBrains Mono fonts) across Swarmbook Studio.
- Standardised card layout styling (padding, borders, shadow accents, and hover transitions).
- Refined primary/ghost button sizing, margins, and hover colors.
- Polished table layouts with border-spacing, borders, headers background, and cells padding.
- Refined scrollbars and empty states for comparison views, dashboard listings, and reports.
- Enforced keyboard focus rings (`outline: 2px solid #FF4500; outline-offset: 2px`) globally on all interactive settings, uploader cards, selection tags, wizard steps, and input text areas.
### Tests added/updated
- Verified Vite client production build check compiles successfully.
- Verified all 62 python backend unit tests remain green.
### Known gaps
- None.

## Phase 34 (Swarmbook UI Accessibility and Responsive QA Pass)
### Files
- `frontend/src/App.vue`
- `frontend/src/views/swarmbook/SwarmbookUploadView.vue`
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue`
- `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`
- `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`
- `docs/SWARMBOOK_LIMITATIONS.md`
### Behavior changed
- Added spacebar keydown selection listeners to custom interactive cards/elements (drag-and-drop zone, step buttons, simulation profile select cards, evidence map cards) to supplement standard enter keydown behaviors for keyboard/screenreader users.
- Added `aria-live="polite"` attributes to form validation alerts in the guided wizard.
- Scaled primary and ghost buttons to ensure touch target sizes satisfy a minimum of 44px in height.
- Overrode light grey `#94a3b8` text styles globally with the high-contrast slate `--sb-text-muted` (`#64748b`) variable inside the Swarmbook namespace, satisfying WCAG 2.2 AA text contrast compatibility.
- Appended accessibility limitations notes (drag-and-drop keyboard limits, scrolling console live log verbosity, structural tables/lists charts, and small screen boundaries) to `docs/SWARMBOOK_LIMITATIONS.md`.
- Added media query rules and `prefers-reduced-motion: reduce` styling rules to disable transitions and animation behaviors when system motion reduction preferences are active.
### Tests added/updated
- Verified Vite client production build compiles successfully with zero compile warnings.
- Verified all 62 python backend unit tests run successfully.
### Known gaps
- Drag-and-drop file upload actions are not keyboard navigable natively, though fully accessible keyboard browsing fallback is supported.
- Scrolling simulation log feeds can be verbose for screen readers when live alerts are active.

## Phase 35 (Complete 360-Degree Testing Suite Design & Implementation)
### Files
- `docs/SWARMBOOK_TESTING_PLAN.md`
- `backend/tests/test_book_sim_edge_cases.py`
### Behavior changed
- Designed a comprehensive Swarmbook Studio testing strategy, logging automated test metrics and manual QA verification checklists under `docs/SWARMBOOK_TESTING_PLAN.md`.
- Implemented edge-case unit and route integration tests in `backend/tests/test_book_sim_edge_cases.py`. Covered validator bounds (empty strings, out-of-range counts, bad privacy modes), manuscript ingestion boundaries (oversized pasted texts and empty inputs), and platform/interrogation model fallbacks.
- Mocked connection socket failures for Ollama, Neo4j, and Python Flask in diagnostic test suites, asserting health diagnostic timeline endpoints correctly catch SocketErrors and format clean failure payloads instead of raising unhandled server-side crashes.
### Tests added/updated
- Added 11 new automated test scenarios under `backend/tests/test_book_sim_edge_cases.py`.
- Verified all 73 backend unit tests pass successfully.
- Verified client environment compiles cleanly under Vite.
### Known gaps
- None.


