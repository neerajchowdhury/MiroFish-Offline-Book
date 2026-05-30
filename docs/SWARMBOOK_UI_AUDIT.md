# Swarmbook UI Audit

## 1. Current Route Map
The frontend currently supports two distinct routing pathways:
- **Legacy MiroFish Routes**: `/`, `/process/:projectId`, `/simulation/:simulationId`, `/simulation/:simulationId/start`, `/report/:reportId`, `/interaction/:reportId`
- **Swarmbook Routes**: `/swarmbook`, `/swarmbook/wizard/:projectId?`, `/swarmbook/settings/:projectId?`, and the project suite: `/swarmbook/project/:projectId/*` (upload, metadata, evidence, simulate, run, report, personas, compare).

## 2. Current Component Map
- **Layouts**: `SwarmbookLayout.vue` handles shared Swarmbook shell navigation.
- **Views**: 
  - `SwarmbookHomeView.vue` (Dashboard)
  - `NewSimulationWizardView.vue` (Guided setup)
  - `SwarmbookUploadView.vue` (Ingestion)
  - `SwarmbookMetadataView.vue` (Project config)
  - `SwarmbookEvidenceView.vue` (DNA, risks, claims map)
  - `SwarmbookSimulationView.vue` (Swarm setup)
  - `SwarmbookSimulationRunView.vue` (Execution terminal)
  - `SwarmbookReportView.vue` (Prediction results dashboard)
  - `SwarmbookPersonasView.vue` (Reader interview workbench)
  - `SwarmbookCompareView.vue` (Draft comparison)
  - `SwarmbookSettingsView.vue` (Global config & diagnostics)

## 3. Current Styling System
- **Approach**: Vanilla CSS using CSS custom properties (variables) injected globally in `App.vue`. No Tailwind or utility framework is present.
- **Design Language**: SaaS-grade "premium" styling targeting WCAG 2.2 AA.
- **Key Variables**: `--sb-bg-base`, `--sb-bg-card`, `--sb-text-main`, `--sb-text-muted`, `--sb-focus-outline`.
- **Interactions**: Animated micro-interactions, distinct focus rings (`2px solid #ff4500`), and semantic signal colors (Ready/Mixed/Offline/Brand).

## 4. Current Upload Limit and Enforcement
- **Enforcement Location**: Backend endpoint `/api/book-sim/parse-file` in `backend/app/api/book_sim.py`.
- **Limits**:
  - Raw file size limit: 10 MB.
  - Parsed manuscript character limit: 500,000 characters (`MAX_MANUSCRIPT_CHARS_DEFAULT`).

## 5. Current Report Data Shape
The `BookPredictionReport` class dictates the data structure, composed of:
- `summary`: High-level 1-sentence verdict.
- `audience_response`: Persona counts, post counts, mean rating.
- `scorecard`: Nested scores for rating distribution, DNF, controversy, quoteability, polarization, viral potential, and revision priority.
- `segment_insights`: Cohort-specific reactions.
- `top_risks` / `top_strengths`: Highlighted lists.
- `revision_priorities`: Top 5 ranked items needing change.
- `evidence_refs`: Traceability artifacts.
- `confidence`: Arithmetic mean of component confidences.

## 6. Current Export Capability
- **Backend Modules**: Markdown generation via `report_markdown.py` and JSON serialization natively via dataclass helpers.
- **Frontend**: Local file exporters in `SwarmbookReportView.vue` and `SwarmbookCompareView.vue` allow downloading raw JSON and rendered Markdown. PDF export is explicitly disabled/warning-only.

## 7. Backend Risks
- **Persistence limits**: `BookSimRuntimeStore` currently relies on a purely file-backed `LocalArtifactCache`. This does not support complex concurrent writes safely on Windows if traffic scales.
- **Provider instability**: `local_only` requires an active Ollama instance; if unavailable or out of memory, the whole pipeline breaks abruptly despite graceful API error wrapping.

## 8. Frontend Risks
- **Build toolchain**: A global `npm-cli.js` shim is broken on this host, forcing direct `vite.js` execution to build.
- **Memory overhead**: Loading enormous `SimulationRun` outputs with hundreds of posts into Vue's reactive state simultaneously might cause browser jank on low-end devices.

## 9. Exact Files Likely to Change in Later Phases
Since Phase 35 is complete, future architectural updates would likely touch:
- `backend/app/book_sim/runtime_store.py` (if moving to a SQL/Neo4j unified DB).
- `frontend/src/views/swarmbook/*.vue` (if adding new features or unifying the legacy flow).
- `backend/app/api/book_sim.py` (for any new endpoints).

## 10. Recommended Implementation Order
*All 35 listed project phases are currently marked `done`.* If further work is required:
1. **Toolchain repair**: Fix the local `npm` environment to restore standard dependency management.
2. **Backend Persistence Upgrade**: Move the `LocalArtifactCache` into a transactional database layer.
3. **Legacy Migration**: Port the legacy MiroFish flow components into the new CSS-variable system to eliminate UX fragmentation.
