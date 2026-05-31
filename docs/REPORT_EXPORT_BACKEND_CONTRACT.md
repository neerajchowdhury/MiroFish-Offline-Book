# Swarmbook Report Export — Backend Contract

## Current Status (Phase 51)

| Format | Status | Implementation | Notes |
|---|---|---|---|
| **PDF** | ✅ Working | `pdfmake` (client-side) | Structured PDF generated in-browser. No server call. |
| **DOCX** | ✅ Working | `docx` library (client-side) | Structured DOCX with headings/paragraphs. No server call. |
| **PNG Summary Card** | ✅ Working | `html2canvas` (client-side) | DOM capture of hidden `#png-summary-card`. No server call. |
| **Markdown** | ✅ Working | String builder (client-side) | Formatted `.md` file downloaded via `file-saver`. |
| **JSON** | ✅ Working | `JSON.stringify` (client-side) | Full report payload with meta disclaimer. |
| **Copy Markdown** | ✅ Working | Clipboard API (client-side) | Falls back to `execCommand('copy')`. |
| **Copy Executive Summary** | ✅ Working | Clipboard API (client-side) | Copies summary + key metrics as plain text. |
| **Copy Revision Plan** | ✅ Working | Clipboard API (client-side) | Copies ranked revision items as plain text. |

> **All exports are currently 100% client-side. No server endpoint is involved in any export operation.** This is guaranteed by design to preserve privacy in `local_only` and `hybrid_safe` modes.

---

## Architecture: Client-Side Export Flow

```
SwarmbookReportView.vue
    │
    ├── handleExport('pdf')       → exportReport.generatePdf(report, session)    → pdfMake → download
    ├── handleExport('docx')      → exportReport.generateDocx(report, session)   → docx → Packer → Blob → saveAs
    ├── handleExport('png')       → html2canvas('#png-summary-card') → canvas.toDataURL → download
    ├── handleExport('markdown')  → exportReport.generateMarkdown(report, session) → Blob → saveAs
    ├── handleExport('json')      → exportReport.generateJson(report, session)    → Blob → saveAs
    ├── handleCopy()              → exportReport.copyToClipboard(report, session) → navigator.clipboard
    ├── handleCopyExec()          → exportReport.copyExecutiveSummary(report)     → navigator.clipboard
    └── handleCopyRevision()      → exportReport.copyRevisionPlan(report)         → navigator.clipboard
```

---

## If You Add a Backend Export Endpoint in Future

This section documents the contract a future `/api/book-sim/projects/{project_id}/export` endpoint should follow.

### Route
```
POST /api/book-sim/projects/{project_id}/export
Content-Type: application/json
```

### Request Body
```json
{
  "format": "pdf" | "docx" | "markdown" | "json",
  "project_id": "string",
  "include_sections": ["verdict", "scorecard", "revision", "risks", "evidence"]
}
```

### Response
- For `pdf`, `docx`, `png`: `Content-Type: application/octet-stream`, `Content-Disposition: attachment; filename=...`
- For `markdown`, `json`: `Content-Type: text/plain` or `application/json`

### Privacy Guard
- If `privacy_mode === 'local_only'`, the server **MUST** reject the request with `HTTP 400` and `error_code: local_only_export_blocked`.
- The backend should never re-process manuscript content to generate export files unless the author has explicitly approved a cloud export.

### Error Codes
| Code | Meaning |
|---|---|
| `local_only_export_blocked` | Export server is disabled in `local_only` mode. |
| `report_not_found` | No report found for given `project_id`. |
| `export_format_unsupported` | Requested format not implemented on server. |

---

## Known Limitations of Current Client-Side Exports

| Limitation | Detail |
|---|---|
| PDF font support | `pdfmake` uses embedded VFS fonts. Custom fonts require pre-embedding in `vfs_fonts.js`. |
| PDF table styling | Tables in PDF use basic pdfmake table cells; no pixel-perfect CSS fidelity. |
| DOCX image support | The `docx` library supports image insertion, but scorecard charts are not yet embedded. |
| PNG DOM capture | `html2canvas` may miss CSS animations and custom fonts in some browser configurations. |
| PNG scaling | The card is captured at `scale: 2` (retina) but raw layout is 800px wide; very long reports are cropped. |
| Clipboard fallback | `execCommand('copy')` fallback is deprecated in some browsers; `navigator.clipboard.writeText` is the primary path. |

---

## Decision Log

| Decision | Rationale |
|---|---|
| All exports client-side | Privacy-first design: `local_only` mode must never transmit data to any server, including the local Flask app's file system. |
| pdfmake over jsPDF | pdfmake provides a structured document definition that separates content from layout, making future section customization simpler. |
| docx library over server-side pandoc | Zero server dependency, works offline, no executable path configuration required. |
| html2canvas over puppeteer | Puppeteer requires a Chromium binary which is impractical for a local personal tool. html2canvas runs in the same browser rendering context. |

---

*This document is part of the Swarmbook Studio Phase 51 deliverables.*
*Do not add fake export success states. If an export fails, surface the error clearly.*
