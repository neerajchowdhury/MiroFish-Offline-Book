# Swarmbook Studio Report Screen and Setup Flow Redesign Audit

This audit reviews the current structure of the Swarmbook Studio report screen and setup/wizard flow, identifying UX problems, architectural constraints, and safest implementation strategies for future redesign steps.

---

## 1. Current Files & Components Involved

### Frontend View Components
- **Report View**: [SwarmbookReportView.vue](file:///d:/SW/MiroFish-Offline-Book/frontend/src/views/swarmbook/SwarmbookReportView.vue) (~2784 lines)
  - Monolithic screen containing the actions bar, metric summaries, executive summaries, rating histogram, reader segments grid, DNF abandonment timeline, controversy indicators, platform reaction feed, and quoteability highlight cards.
- **Wizard View**: [NewSimulationWizardView.vue](file:///d:/SW/MiroFish-Offline-Book/frontend/src/views/swarmbook/NewSimulationWizardView.vue) (~2198 lines)
  - Stepper wizard containing Step 1 (basics/metadata), Step 2 (drag-and-drop manuscript upload or paste option), Step 3 (compilation of evidence metrics), Step 4 (reader swarm and profile config), and Step 5 (stress test confirmation).
- **App Layout**: [SwarmbookAppShell.vue](file:///d:/SW/MiroFish-Offline-Book/frontend/src/components/swarmbook/SwarmbookAppShell.vue)
  - Common shell providing the navigation header, mobile sidebar, compact health status rail, and workspace wrappers.

### Utilities and Configurations
- **Export System**: [exportReport.js](file:///d:/SW/MiroFish-Offline-Book/frontend/src/utils/exportReport.js)
  - Integrates structured PDF (`pdfmake`), DOCX (`docx`), Markdown, JSON, Clipboard, and Canvas PNG screenshot captures.
- **Upload Configuration**: [uploadLimits.js](file:///d:/SW/MiroFish-Offline-Book/frontend/src/config/uploadLimits.js)
  - Specifies sizing thresholds, file type boundaries, and estimated parsing time logic.
- **Routing Configuration**: [index.js](file:///d:/SW/MiroFish-Offline-Book/frontend/src/router/index.js)
  - Defines Wizard (`/swarmbook/wizard/:projectId?`) and Report (`/swarmbook/project/:projectId/report`) URL mapping.

### Backend Routing and Modeling
- **API Surface**: [book_sim.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/api/book_sim.py)
  - Exposes project initialization, evidence upload/ingestion parsing, simulation triggering, and report generation endpoints.
- **Report Structures & Data Shape**: [models.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/models.py) & [report_builder.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/report_builder.py)
  - Prescribes schema targets: `BookPredictionReport`, `StarRatingDistribution`, `DnfRiskScorecard`, `ControversyScorecard`, `PlatformPost`, `SegmentInsight`, etc.

---

## 2. Current UX Problems

1. **Monolithic Codebases**:
   - Both `SwarmbookReportView.vue` and `NewSimulationWizardView.vue` are massive (2,000+ lines of code). They mix layout templates, reactive validation states, mock demo fallbacks, and local inline CSS styles. This increases regression risk.
2. **Dashboard Clutter & Information Density**:
   - The Report Dashboard renders 13 distinct detail panels on a single page. While sticky navigation links exist, users face excessive scroll fatigue.
3. **Disconnected Platform Filter**:
   - The platform reaction tabs under *Simulated Reader Reactions* only filter the mock post feed, leaving the metrics, ratings, and segment tables unfiltered.
4. **Wizard Progression Constraints**:
   - Clicking stepper ribbon tabs allows navigation only if basic fields are populated. However, explicit step validations are managed in the same massive component, making it difficult to debug.

---

## 3. Data Shape & Simulation Output Fields

From [models.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/models.py) and [report_builder.py](file:///d:/SW/MiroFish-Offline-Book/backend/app/book_sim/report_builder.py), a synthesized report payload contains:
- `report_id`, `project_id`, `simulation_id`, `privacy_mode`, `title`, `summary`, `confidence`
- `scorecard`:
  - `rating_distribution`: `predicted_mean_rating` (float), `distribution` (1 to 5 star probabilities), `confidence_band` (low/high margins), `component_scores` (comprehension, emotional_payoff, prose_quality, pacing, character_attachment, packaging_fit)
  - `dnf`: `dnf_risk` (float), `component_scores` (opening_drag, confusion, pacing_drag, unmet_expectation, voice_misalignment, length_fatigue), `chapter_points` (per-chapter list of DNF probability values and reasons)
  - `controversy`: `controversy_risk` (float), `radar` (ideological, claim_hazard, moral, tonal, character, packaging risks), `hotspots` (flagged keys)
  - `polarization`: `polarization_score` (float), `component_scores`, `split_signals`
  - `quoteability`: `quoteability_score` (float), `component_scores`, `quote_candidates` (array of text + source chapter keys)
  - `viral`: `platform_scores` (platform specific viral probability metrics), `top_platforms`, `component_scores`
  - `revision_priority`: `ranked_items` (items containing type, target id, priority score, and reasons)
- `segment_insights`: Array of platform segment names, predicted mean ratings, recommendation percentages, signals, and sample personas.

---

## 4. Export Capability & Feasibility

- **Does structured PDF/DOCX export already exist?**
  - **Yes.** [exportReport.js](file:///d:/SW/MiroFish-Offline-Book/frontend/src/utils/exportReport.js) contains implementations for PDF (`generatePdf` using client-side `pdfmake`) and DOCX (`generateDocx` using `docx`). It also offers Clipboard markdown replication, raw JSON download, and PNG capture of summary cards (`html2canvas`).
- **Recommended Export Approach**:
  - Keep exports purely client-side as currently written. It prevents CPU-intensive rendering round-trips to the backend and protects offline privacy limits (`local_only`). The design of PDF/DOCX templates should match the style tokens defined in `frontend/src/assets/tokens.css`.

---

## 5. Feasibility of Structural Redesigns

- **Can tabbed reports be added without breaking routes?**
  - **Yes.** The route configuration `/swarmbook/project/:projectId/report` matches a single component view (`SwarmbookReportView.vue`). Tabs can be controlled internally via Vue local component state variables (e.g. `activeReportTab: 'summary' | 'readability' | 'marketing'`). This changes which panels are rendered via `v-if`/`v-show` without altering index/router setup logic.
- **Wizard Step Validation**:
  - The validation rules are already wired inside `NewSimulationWizardView.vue`. However, moving towards a modular stepper where sub-forms are separated into lightweight child components would keep the parent wizard container thin.

---

## 6. Safest Implementation Sequence

1. **Refactor Phase (Zero Behavior Modification)**:
   - Extract child visual cards (e.g., `StarRatingSpread.vue`, `DnfRiskCard.vue`, `PlatformFeed.vue`) from `SwarmbookReportView.vue` into modular components to reduce file size.
2. **Wizard State Modularization**:
   - Split each wizard step form (basics, upload, setup) into dedicated files, passing values to the wizard orchestrator via Vue standard `v-model`.
3. **Tabbed Report Layering**:
   - Group the 13 panels in `SwarmbookReportView.vue` under sub-tabs (e.g. *Executive Verdict*, *DNF & Pacing*, *Platform Coverage*, *Revision Guidelines*).
4. **Token Verification**:
   - Run CSS token checks to ensure color-schemes align with `tokens.css` design system guidelines.

---

## 7. Risks & Guardrails

- **Regression Danger**: Replacing component structures may break mock data rendering or API loading routines in `ensureReport()`. Ensure `loadDemoMock()` is preserved for diagnostic checks.
- **Privacy Violation**: Redesign adjustments must never leak manuscript contents or route outside of local boundaries when `local_only` mode is selected. Keep processing strictly client-side/Ollama-first.
