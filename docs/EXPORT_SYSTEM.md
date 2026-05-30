# Swarmbook Export System

The Swarmbook Report Dashboard provides a comprehensive suite of export capabilities to accommodate different author and editor workflows.

## Export Formats & Tooling

To ensure high-quality output and maintain maintainability, the system prefers structured data generation over simple DOM snapshots.

1. **JSON (`exportJson`)**
   - **Purpose**: Machine-readable backups and API integrations.
   - **Mechanism**: Native `JSON.stringify` bundled with timestamp, project ID, and privacy disclaimers. 

2. **Markdown (`exportMarkdown`)**
   - **Purpose**: Easy text-based sharing and note-taking.
   - **Mechanism**: Custom string assembly in `frontend/src/utils/exportReport.js`.

3. **PDF (`exportPdf`)**
   - **Purpose**: Polished, professional sharing with agents/editors.
   - **Mechanism**: Uses `pdfmake` for strict document definition. It constructs a Cover Page, Executive Verdict, Revision Priorities, and Caveats without relying on browser rendering engines. This ensures page breaks and text wrapping are handled flawlessly.

4. **DOCX (`exportDocx`)**
   - **Purpose**: Editable editorial notes.
   - **Mechanism**: Uses `docx`. Generates native Word Paragraphs and TextRuns, providing a document that authors can physically edit, comment on, or send to beta readers.

5. **Summary Card PNG (`exportPng`)**
   - **Purpose**: Highly shareable, single-page scorecard for social media (e.g. Discord, X, Instagram).
   - **Mechanism**: Uses `html2canvas`. This is the *only* export that relies on DOM rendering. A dense, beautifully styled hidden `<div>` (`#png-summary-card`) is rendered on-the-fly and captured as an image buffer.

6. **Copy to Clipboard**
   - **Purpose**: Instant pasting into chat apps or LLMs.
   - **Mechanism**: Uses the native `navigator.clipboard` API with an invisible `<textarea>` fallback.

## Extending the Export System

When new scorecards or map components are added to `SwarmbookReportView.vue`, they must also be manually added to the export functions inside `frontend/src/utils/exportReport.js`.

1. To add a new metric to the PDF, push a new block to the `docDefinition.content` array.
2. To add a new metric to the DOCX, push a new `Paragraph` instance to the `children` array.
3. To add a new metric to the PNG summary card, update the HTML structure of the `#png-summary-card` hidden element directly within the Vue template.
