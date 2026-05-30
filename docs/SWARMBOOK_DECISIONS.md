# Swarmbook Decisions (Reconstructed)

## D-052
- Date: `2026-05-29`
- Decision: Add `test_book_sim_extra_edge_cases.py` unit tests testing DraftComparator self-comparison, extreme scoring boundaries, and privacy router filter constraint.
- Rationale: Hardens the E2E verification loop, validating edge case values against theoretical baselines (e.g. empty maps vs max rating) and confirming local privacy policy routing holds securely.
- Trade-off: None. The changes are purely additive.
- Files affected: `backend/tests/test_book_sim_extra_edge_cases.py`

## D-051
- Date: `2026-05-29`
- Decision: Refine the Draft Comparison screen to use directional text icons for deltas and display a Known Limitations banner.
- Rationale: Ensures color is not the only signal for score movement, satisfying WCAG accessibility standards, and maintains transparency about synthetic simulation confidence levels.
- Trade-off: None. The changes are purely additive.
- Files affected: `frontend/src/views/swarmbook/SwarmbookCompareView.vue`

## D-050
- Date: `2026-05-29`
- Decision: Refine the Persona Interview screen to use a slide-over Evidence Drawer overlay layout, mapping all 7 schemas dynamically, registering exact quick questions wording, and rendering a persistent Known Limitations sandbox warning.
- Rationale: A sliding drawer saves horizontal workspace space on smaller desktop/tablet displays and provides a full-viewport sheet overlay on mobile for improved readability. Explicitly mapping all 7 schema maps ensures grounded references can be fully inspected, and a warning banner prevents users from mistaking synthetic signals for real platform scraper outputs.
- Trade-off: Drawer transition CSS increases the stylesheet footprint, but drastically improves the master-detail flow and responsiveness of the screen.
- Files affected: `frontend/src/views/swarmbook/SwarmbookPersonasView.vue`

## D-049
- Date: `2026-05-29`
- Decision: Adopt structured document generation libraries (`pdfmake`, `docx`) for PDF and Word exports rather than capturing DOM snapshots (with the exception of a targeted PNG Shareable Summary Card via `html2canvas`).
- Rationale: Structured generation guarantees professional text selection, pagination, formatting, and editability, which screenshot-to-PDF strategies fail to provide.
- Trade-off: Adding new visualization components to the report dashboard requires manual mapping inside the `exportReport.js` utility, increasing maintenance overhead for the sake of higher export quality.
- Files affected: `frontend/src/utils/exportReport.js`, `frontend/package.json`

## D-048
- Date: `2026-05-29`
- Decision: Restructure the Report Dashboard to position Executive Verdict and Revision Priorities explicitly above the fold, while using jump-navigation to access deeper charts.
- Rationale: A "decision-first" UX ensures authors can rapidly identify what needs fixing without scrolling past dense simulated social media reactions.
- Trade-off: Requires manual CSS overrides for sticky navigation and slightly increases top-level information density.
- Files affected: `frontend/src/views/swarmbook/SwarmbookReportView.vue`

## D-047
- Date: `2026-05-29`
- Decision: Restructure the Simulation Run view using a 7-step stepper and terminal styling without implementing an active background polling architecture.
- Rationale: The backend `/api/book-sim/simulate` endpoint is synchronous, meaning the client cannot legitimately pause/resume or fetch real-time progressive logs without a heavy architectural rewrite to use websockets or background jobs.
- Trade-off: The UI must spoof progress or rely on the single synchronous response for now, rendering the "Pause" button functionally disabled.
- Files affected: `frontend/src/views/swarmbook/SwarmbookSimulationRunView.vue`

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

## D-024
- Date: `2026-05-24`
- Decision: Add app-wide `before_request` request filter hook on Flask blueprints to set system-wide `PrivacyGuard`, and enforce `local_only` checks inside `GeminiProvider` and `NvidiaProvider` generate/embed methods.
- Rationale: Close the gap where privacy enforcement was only router-scoped, ensuring provider-level safety even if router selection is bypassed.
- Trade-off: None. Ensures robust privacy compliance system-wide.
- Files affected: `backend/app/api/book_sim.py`, `backend/app/book_sim/providers/gemini_provider.py`, `backend/app/book_sim/providers/nvidia_provider.py`, `backend/tests/test_book_sim_privacy_guard.py`

## D-025
- Date: `2026-05-24`
- Decision: Implement custom YAML-free parser fallback in `local_profiles.py` for parsing `local_profiles.yaml` when PyYAML is missing.
- Rationale: Ensures that local profile custom configurations are loaded successfully even in python environments missing PyYAML dependency, mirroring route config fallbacks.
- Trade-off: None. Strengthens local-first fallback loading.
- Files affected: `backend/app/book_sim/local_profiles.py`, `backend/tests/test_book_sim_local_profiles.py`

## D-026
- Date: `2026-05-27`
- Decision: Create an automated Windows installation tool (`install_swarmbook.ps1`) under `scripts/windows/` incorporating dynamic PATH reloading, winget dependency installation, venv provisioning, npm packaging, configuration creation, model pre-fetching, and desktop shortcut generation.
- Rationale: High-fidelity, optimized installation automation for Windows 11 workstations to allow one-click installation on new laptops.
- Trade-off: None. Improves workstation portability and local release setup.
- Files affected: `scripts/windows/install_swarmbook.ps1`, `docs/SWARMBOOK_PHASE_STATUS.md`, `docs/SWARMBOOK_CHANGELOG.md`, `docs/SWARMBOOK_DECISIONS.md`

## D-027
- Date: `2026-05-27`
- Decision: Keep styling scoped to custom CSS in SFC style blocks or dedicated import files, ensuring WCAG 2.2 AA accessibility and local hardware privacy visibility.
- Rationale: Preserves existing CSS styling paradigms and keeps styling lightweight and modular while optimizing accessibility.
- Trade-off: No TailwindCSS utility styling framework is introduced.
- Files affected: `docs/SWARMBOOK_UI_REDESIGN.md`, `docs/SWARMBOOK_CHANGELOG.md`, `docs/SWARMBOOK_DECISIONS.md`

## D-028
- Date: `2026-05-27`
- Decision: Implement Settings as an interactive modal overlay within the SwarmbookAppShell rather than adding a separate route or view.
- Rationale: Promotes a premium, SaaS-grade user experience by allowing quick configurations and warnings to be checked immediately without losing active work progress context.
- Trade-off: Routing is simplified, but the settings layout logic is tightly coupled to the shell component structure.
- Files affected: `frontend/src/components/swarmbook/SwarmbookAppShell.vue`, `docs/SWARMBOOK_DECISIONS.md`

## D-029
- Date: `2026-05-27`
- Decision: Store Swarmbook project history locally in client localStorage (`mirofish_swarmbook_projects`) for immediate dashboard population.
- Rationale: Allows displaying recent projects to authors without introducing a list-projects database queries backend route or altering the additive filesystem database storage mechanism on the Python side.
- Trade-off: Project history list is browser-specific and will be cleared if client local storage is wiped.
- Files affected: `frontend/src/views/swarmbook/SwarmbookHomeView.vue`, `docs/SWARMBOOK_DECISIONS.md`

## D-030
- Date: `2026-05-27`
- Decision: Implement a unified 5-step "New Simulation Wizard" route (`NewSimulationWizard` at path `/swarmbook/wizard/:projectId?`) to replace disjointed metadata and upload views.
- Rationale: Author experience is significantly improved by providing a linear setup wizard (Basics -> Upload -> Evidence -> Reader Swarm -> Run) with active validation, character count safety warnings, dynamic localStorage state persistence, and direct redirection to the final scorecard report.
- Trade-off: Some duplication with standard separate upload/metadata steps, but routes are additive and preserve full access.
- Files affected: `frontend/src/router/index.js`, `frontend/src/views/swarmbook/NewSimulationWizardView.vue`, `frontend/src/components/swarmbook/SwarmbookAppShell.vue`, `frontend/src/views/swarmbook/SwarmbookHomeView.vue`

## D-031
- Date: `2026-05-27`
- Decision: Add native standard-library `.docx` text extraction to `FileParser` and expose a new `/parse-file` endpoint.
- Rationale: Avoids requiring third-party python dependencies while maintaining support for Microsoft Word manuscript uploads alongside PDF, TXT, and MD formats. Exposing file parsing as a backend service allows offloading binary file processing from client-side JavaScript.
- Trade-off: Extraction uses a simple XML text crawler inside the DOCX ZIP archive structure, which ignores styling and image nodes (which is correct since we only require plain text).
- Files affected: `backend/app/utils/file_parser.py`, `backend/app/api/book_sim.py`, `backend/tests/test_book_sim_api.py`

## D-032
- Date: `2026-05-27`
- Decision: Redesign the Swarmbook Evidence view (`SwarmbookEvidenceView.vue`) into a premium split-pane dashboard instead of simple lists.
- Rationale: Promotes a premium, SaaS-grade workspace experience by displaying a list of 7 narrative maps on the left with status indicators, confidence scales, and references counts, while displaying detailed structured data and editorial annotation forms on the right.
- Trade-off: Complex template rendering and styling block, but improves accessibility, visual hierarchy, and allows authors to direct/customize persona simulation runs using editorial notes.
- Files affected: `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`

## D-033
- Date: `2026-05-27`
- Decision: Modify the backend `_persona_overrides` helper to parse `exclude_archetypes` and pass them to the persona generator overrides class.
- Rationale: Enables client-side custom reader cohort selections to be mapped directly to under-the-hood archetype exclusions dynamically at simulation time.
- Trade-off: None. The change is fully backwards compatible and tested.
- Files affected: `backend/app/api/book_sim.py`, `backend/tests/test_book_sim_api.py`

## D-034
- Date: `2026-05-27`
- Decision: Redesign standalone simulation view and wizard Step 4 into a premium Reader Swarm Setup dashboard.
- Rationale: Authors are shielded from low-level agent configuration details by being presented with plain-language simulation profiles, count controllers, platforms, active reader cohorts checklist, privacy cost explanation blocks, dynamic time estimations, and provider connection grids.
- Trade-off: Complex layout template styling code footprint, but drastically improves author setup experience.
- Files affected: `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`, `frontend/src/views/swarmbook/NewSimulationWizardView.vue`

## D-035
- Date: `2026-05-27`
- Decision: Centralize simulation execution progress visualization in a dedicated `/run` view route component (`SwarmbookSimulationRunView.vue`).
- Rationale: Decoupling setup forms from execution states simplifies views code and allows both standalone config pages and guided wizards to route directly to a uniform, high-fidelity progress tracking dashboard with abort controller bindings and scrolling logs.
- Trade-off: None. Promotes a premium, SaaS-grade UX sequence and isolates runtime Axios cancel actions.
- Files affected: `frontend/src/views/swarmbook/SwarmbookSimulationRunView.vue`, `frontend/src/router/index.js`, `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`, `frontend/src/views/swarmbook/NewSimulationWizardView.vue`

## D-036
- Date: `2026-05-27`
- Decision: Redesign `SwarmbookReportView.vue` into a SaaS-grade Report Dashboard displaying 6 summary cards, 13 detailed main panels, local exporters, and an offline mock loader.
- Rationale: Replaces the simple placeholder layout with an immersive, visual data suite that lets authors explore star spreads, DNF drag factors, controversy axes, platform reactions, and revision action lists. Using fully client-side exporters for JSON/Markdown and a disabled PDF warning adheres to local-first privacy and dependencies guidelines. Including an offline mock fallback loader makesvisual validation simple.
- Trade-off: Complex custom CSS implementation footprint (progress bars, timelines, mock social post feeds) to avoid introducing third-party chart package dependencies, but ensures low-resource workstation performance.
- Files affected: `frontend/src/views/swarmbook/SwarmbookReportView.vue`

## D-037
- Date: `2026-05-27`
- Decision: Redesign `SwarmbookPersonasView.vue` into a SaaS-grade master-detail Persona Interview screen with sidebar directories, messaging bubbler thread workflows, and grounded evidence detail inspector lookups.
- Rationale: Replaces the simple dropdown and text response boxes with a modern directory-based interface where authors can toggle simulated readers, inspect profile attributes (tastes, DNF triggers), view rolling message threads, ask suggested shortcuts, and drill down on grounded evidence pack citations.
- Trade-off: Complex layout template structure, but drastically enhances query flows and bridges reader reactions back to raw manuscript evidence pack entities.
- Files affected: `frontend/src/views/swarmbook/SwarmbookPersonasView.vue`

## D-038
- Date: `2026-05-27`
- Decision: Redesign `SwarmbookCompareView.vue` as a SaaS-grade Draft Comparison workspace featuring project history dropdown selectors, side-by-side executive scorecards with readiness and score deltas, tabbed structural change logs (DNA/segments, chapters, characters/claims), markdown export previews, and high-fidelity offline mock fallbacks.
- Rationale: Promotes a premium, SaaS-grade comparison experience. Reading `mirofish_swarmbook_projects` from `localStorage` simplifies project selection compared to copy-pasting raw UUID strings. Side-by-side delta scorecard and tabbed category inspectors drill down into details clearly. Compliant focus rings and ARIA attributes satisfy WCAG 2.2 AA standards, and high-fidelity mock data guarantees offline resilience.
- Trade-off: None. The changes are additive, isolated, and preserve existing MiroFish screens and backend routes.
- Files affected: `frontend/src/views/swarmbook/SwarmbookCompareView.vue`

## D-039
- Date: `2026-05-27`
- Decision: Create `SwarmbookSettingsView.vue` and register the route `/swarmbook/settings/:projectId?` to replace the static settings modal in `SwarmbookAppShell.vue`.
- Rationale: Standardizes configurations management as a first-class screen workspace, preventing UI blocking. Interactive diagnostics sweep and environmental key checks verify WS connections immediately. Obfuscated cloud key indicators and strict privacy selectors keep manuscript data offline securely under local_only mode.
- Trade-off: Routing is slightly more complex, but makes configurations easier to read, test, and troubleshoot.
- Files affected: `frontend/src/views/swarmbook/SwarmbookSettingsView.vue`, `frontend/src/router/index.js`, `frontend/src/components/swarmbook/SwarmbookAppShell.vue`

## D-040
- Date: `2026-05-27`
- Decision: Place shared visual polish styles and root variables in the global stylesheet block of `App.vue` (unifying typography, cards, buttons, scrollbars, focus outlines, tables, and empty states).
- Rationale: Storing variables and overrides at the root ensures visual consistency across all Swarmbook screens without duplicating styles or clashing with legacy MiroFish layouts.
- Trade-off: None. The style block only overrides classes active in Swarmbook screens.
- Files affected: `frontend/src/App.vue`

## D-041
- Date: `2026-05-27`
- Decision: Centralize text contrast variables overrides, button touch targets (min-height: 44px), and prefers-reduced-motion media query variables globally in `App.vue`, while adding spacebar event listeners to custom interactive div/selection controls.
- Rationale: This guarantees full WCAG 2.2 AA and responsive QA compliance across all Swarmbook views without duplicating inline styles or breaking the legacy MiroFish screens. Standard spacebar keydown listener supplements standard enter keydown behaviors for custom controls.
- Trade-off: Centralizing overrides in `App.vue` increases stylesheet code footprint slightly but improves consistency and compliance.
- Files affected: `frontend/src/App.vue`, `frontend/src/views/swarmbook/*.vue`

## D-042
- Date: `2026-05-27`
- Decision: Implement a dedicated edge-case test suite (`test_book_sim_edge_cases.py`) and a comprehensive 360-degree testing plan (`SWARMBOOK_TESTING_PLAN.md`).
- Rationale: Fully validates error boundaries, parameter validations, socket diagnostics, ingestion limits, and fallback strategies of the manuscript simulation engine and Flask blueprints without modifying or risking regressions in existing test structures.
- Trade-off: None. The files are entirely additive and adhere to the Swarmbook continuity guardrails.
- Files affected: `backend/tests/test_book_sim_edge_cases.py`, `docs/SWARMBOOK_TESTING_PLAN.md`, `docs/SWARMBOOK_DECISIONS.md`

## D-043
- Date: `2026-05-29`
- Decision: Redesign Swarmbook Projects/Home page into a compact Launch Console. Remove oversized hero block, move project ID open into expandable toggle, remove duplicate Ollama/Neo4j status displays, and collapse profile warnings unless a non-default profile is selected.
- Rationale: Optimizes desktop real estate to fit 1366x768 layouts without scrolling, removes redundant status indicators to keep UI clean, and improves empty states with clear CTA actions.
- Trade-off: None. The changes remain fully additive and do not affect legacy MiroFish views.
- Files affected: `frontend/src/views/swarmbook/SwarmbookHomeView.vue`, `docs/SWARMBOOK_DECISIONS.md`

## D-044
- Date: `2026-05-29`
- Decision: Redesign the guided simulation wizard basics screen (Step 1). Add Content Type dropdown selector, Test Goal required field, collapsible optional metadata section, dynamic Live Accuracy Checklist card, and real-time autosave watch block.
- Rationale: Multi-format support allows testing blurbs, essays, proposals, and novels with tailored accuracy expectations visible to authors instantly. Collapsing optional fields reduces vertical footprint to improve scrolling efficiency. Autosaving ensures state is kept on page refresh/crashes.
- Trade-off: Incremental addition of schema metadata keys, but fully backwards-compatible and additive.
- Files affected: `frontend/src/store/swarmbookSession.js`, `frontend/src/views/swarmbook/NewSimulationWizardView.vue`, `docs/SWARMBOOK_DECISIONS.md`

## D-045
- Date: `2026-05-29`
- Decision: Redesign Swarmbook Evidence view (`SwarmbookEvidenceView.vue`) into a 7-card grid workspace. Replace split-pane with card grid, add slide-out Detail Drawer overlay, show collapsible raw JSON in Advanced View, flag low-confidence (< 75%) visually/textually, and block simulation progress until critical maps (DNA, chapters, characters/claims) are Accepted.
- Rationale: Grid simplifies map scanning and tracking. Detail Drawer overlay organizes structured sub-attributes and editorial annotations cleanly without cluttering the screen. Custom badge visual style/warning label satisfies accessibility goals, and blocking button states ensure valid simulations.
- Trade-off: None. The changes remain fully additive and do not affect legacy MiroFish views.
- Files affected: `frontend/src/views/swarmbook/SwarmbookEvidenceView.vue`, `docs/SWARMBOOK_DECISIONS.md`

## D-046
- Date: `2026-05-29`
- Decision: Redesign Swarmbook Simulation configuration screen (`SwarmbookSimulationView.vue`) into a premium Reader Swarm Setup screen. Add warning banner for offline sandbox, map model details per profile card, add load meter categorized scale for memory load, show cohort quotes/archetypes details, update privacy card details, and collapse advanced parameters.
- Rationale: Promotes clear understanding that the simulation is an offline sandbox (no scraping/live posting). Adding model usage info, load categories, and cohort descriptions clarifies "who is simulated" and CPU/VRAM load limitations on standard workstations, while collapsing advanced configurations declutters the workspace.
- Trade-off: None. The changes remain fully additive and do not affect legacy MiroFish views.
- Files affected: `frontend/src/views/swarmbook/SwarmbookSimulationView.vue`, `docs/SWARMBOOK_DECISIONS.md`

