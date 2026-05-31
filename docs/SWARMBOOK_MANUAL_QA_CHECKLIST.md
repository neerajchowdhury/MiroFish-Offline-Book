# Swarmbook Manual QA Checklist

## 1. Setup Wizard Visual QA
- [ ] **Step 1:** Title field shows error if blank and user clicks Next.
- [ ] **Step 1:** Changing Content Type updates accurately.
- [ ] **Step 2:** File dropzone highlights on drag-over.
- [ ] **Step 2:** Word count / Section count populates after upload.
- [ ] **Step 3:** Intended promise box updates character count progressively.
- [ ] **Step 4:** Regenerate maps button has a loading state.
- [ ] **Step 5:** Reader count slider updates memory warning visually.
- [ ] **Step 5:** Development Editor Board toggle accurately reveals +15s warning.
- [ ] **Step 6:** All four summary cards populate accurately based on steps 1-5.

## 2. Report Command Center & Tabs QA
- [ ] **Sticky Bar:** Scrolls cleanly, export buttons remain clickable.
- [ ] **Above-the-fold KPIs:** Values populate correctly.
- [ ] **Overview Tab:** Summary scales properly.
- [ ] **Dev Editor Board Tab:** 12 cards align in a grid. Toggle logic expands context.
- [ ] **Revision Plan Tab:** Accordion items expand/collapse smoothly.
- [ ] **Reader Reactions Tab:** Scrolling feed does not jitter.
- [ ] **Risks / Quoteability / Evidence Tabs:** Sub-lists map securely.
- [ ] **Exports Tab:** Cards align correctly, hover states activate.

## 3. Upload Edge-Case QA
- [ ] Uploading a 0-byte `.txt` fails with error banner.
- [ ] Uploading a `.jpg` fails with "Unsupported format".
- [ ] Uploading a 50MB PDF triggers client-side size warning before uploading.

## 4. Export QA
- [ ] **Copy Executive Summary:** Clicking fires success toast and copies correct text to clipboard.
- [ ] **Copy Revision Plan:** Clicking fires success toast and copies formatted list to clipboard.
- [ ] **PDF/DOCX/PNG/JSON/MD:** Confirm client-side downloads trigger a browser save prompt.

## 5. Mobile & Responsive QA (390px)
- [ ] Home screen cards collapse into a single column.
- [ ] Wizard steps layout vertically, sidebar drops beneath main content.
- [ ] Report tabs turn into a scrollable horizontal strip or dropdown.
- [ ] Revision plan accordion titles do not overflow horizontal screen space.

## 6. Accessibility QA
- [ ] Pressing `Tab` repeatedly cycles through all visible interactive inputs on the Wizard.
- [ ] Focus outlines are clearly visible (e.g., blue ring) on all inputs and buttons.
- [ ] Export buttons trigger action when focused and `Space` or `Enter` is pressed.
- [ ] Simulated error states (e.g. invalid form) are communicated with an icon AND red text.

## 7. Privacy / Local-Only QA
- [ ] Set privacy mode to `local_only` in settings.
- [ ] Ensure the browser Network tab shows NO outbound requests to OpenAI/Anthropic/Google.
- [ ] Start backend with internet disconnected. Upload and simulate. Ensure failure happens locally or succeeds using local Ollama.

## 8. Original MiroFish QA
- [ ] Navigate to legacy route `/`.
- [ ] Confirm the old interface still works completely.
- [ ] Upload legacy project and run standard MiroFish to ensure backend router was not broken.

## 9. Error-State QA
- [ ] Disconnect backend server and click "Analyze Content" in wizard. Confirm "Network Error" appears rather than silent failure.
- [ ] Navigate to `/swarmbook/report/invalid-uuid`. Confirm redirect to Home or "Project Not Found" message.

## Final Release Smoke Test
- [ ] Restart local backend.
- [ ] Create New Test -> Upload -> Step through Wizard -> Generate.
- [ ] Confirm Report renders accurately with no console errors in frontend or backend.
