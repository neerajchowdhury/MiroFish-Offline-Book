# Swarmbook Testing Audit

## 1. Existing Test Tools
### Backend
- **Framework**: Python `unittest` via `pytest` (or `python -m unittest`).
- **Scope**: Extensive unit and integration tests exist in `backend/tests/`.
- **Coverage**:
  - `test_book_sim_api.py` (API routing, ingestion, simulating)
  - `test_book_sim_edge_cases.py` and `test_book_sim_extra_edge_cases.py` (Validation, boundary conditions, parsing limits)
  - `test_book_sim_privacy_guard.py` (Route isolation and provider gating)
  - `test_book_sim_report_builder.py` (Report generation and mock data synthesis)

### Frontend
- **Framework**: **None.** `package.json` contains no unit or E2E testing framework.
- **Scope**: Zero automated tests.
- **Tooling**: Uses Vite and Vue 3.

## 2. Existing Test Gaps
- **Frontend State & Components**: Setup wizard validation states (character counts, field prerequisites, required fields blocking progression) are entirely untested via automation.
- **Frontend Export Logic**: Client-side parsing via `docx` and `pdfmake` has no verification against data shapes.
- **UI Render Fidelity**: Report tabs heavily rely on complex D3 graphs and conditional data structures without snapshot or component-level guarantees.
- **End-to-End Workflows**: The critical path of "Upload Document → Wait for Extraction → Configure Cohort → Launch Simulation → View Report" relies exclusively on manual validation.

## 3. Recommended Test Strategy
1. **Retain Backend Strategy**: Continue using `unittest` for all logic, privacy gating, and data shaping. The existing suite is healthy.
2. **Introduce Frontend Component Testing (Vitest)**: Because Vite is already the bundler, Vitest provides near-zero config component testing using `jsdom` and `@vue/test-utils`.
3. **Introduce Frontend E2E Testing (Playwright)**: An offline-compatible E2E test to navigate the wizard and verify critical UI paths without mocking the local backend.
4. **Implement Manual QA Checklist**: Edge cases involving screen reader compatibility, responsive scaling on custom dimensions, and visual contrast require human review using a tick-box approach.

## 4. Exact Files/Components Requiring Tests
- `frontend/src/views/swarmbook/NewSimulationWizardView.vue` (Step validation)
- `frontend/src/utils/exportReport.js` (Export string extraction)
- `frontend/src/views/swarmbook/SwarmbookReportView.vue` (Tab rendering logic)
- E2E flow across `SwarmbookHomeView` -> `Wizard` -> `Report`.

## 5. Frameworks Availability
- Playwright / Cypress / Vitest / Jest: **None exist.**
- Pytest: **Exists and active.**

## 6. What Should Be Automated Now
- Basic wizard progression validation (e.g., cannot proceed without Title).
- Clipboard string builders in `exportReport.js`.
- An end-to-end "Happy Path" through the app with a sample document.
- Backend edge case logic for oversized files (already automated, needs verification).

## 7. What Should Remain Manual QA
- Complex visual layout checks (e.g., Development Editor Board card alignment on mobile).
- Screen reader ARIA tabpanel navigation.
- Actual PDF/DOCX layout fidelity (checking if the generated document looks professional).
- Browser back/forward state retention during wizard interaction.

## 8. Risks and Assumptions
- **Playwright Installation Risk**: `npx playwright install` requires fetching browser binaries from the internet. If the environment is strictly offline or locked down, this may fail. If so, E2E tests will be skipped.
- **DOM Stability**: E2E tests are brittle if class names or ARIA attributes change rapidly during iteration.
