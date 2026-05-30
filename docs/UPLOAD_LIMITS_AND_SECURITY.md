# Upload Limits and Security

> Last updated: 2026-05-29 — Phase 40

---

## Current Limits

| Layer | Setting | Value | Location |
|---|---|---|---|
| Flask ceiling | `MAX_CONTENT_LENGTH` | **200 MB** | `backend/app/config.py` |
| App file limit | `BOOK_SIM_MAX_FILE_BYTES` | **40 MB** | `backend/app/api/book_sim.py` |
| App char limit | `MAX_MANUSCRIPT_CHARS_DEFAULT` | **500,000 chars** | `backend/app/api/book_sim.py` |
| Frontend limit | `MAX_FILE_BYTES` | **40 MB** | `frontend/src/config/uploadLimits.js` |

> **40 MB = 4× the original 10 MB limit** applied in Phase 40.

### Limit Hierarchy

```
Browser (client-side gate, immediate feedback)
  └─ 40 MB check before sending → friendly size error shown inline
Flask MAX_CONTENT_LENGTH (hard ceiling)
  └─ 200 MB — ensures Flask never rejects before our handler runs
     ↓
parse_file() handler
  ├─ 1. Extension allow-list check
  ├─ 2. 40 MB raw byte size check (BOOK_SIM_MAX_FILE_BYTES)
  ├─ 3. File-signature (magic byte) validation
  ├─ 4. UUID temp-file write → text extraction → temp-file delete
  └─ 5. 500,000 character limit on extracted text
```

---

## Security Controls

### 1. Never Trust the Original Filename

- The original filename is stored **only for display/error messages**.
- Temporary files are written as `{uuid4().hex}{ext}` — the original name is never used as a filesystem path component.
- Code: `temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")`

### 2. Extension Allow-list

Only these extensions are accepted:

| Extension | Format |
|---|---|
| `.pdf` | Adobe PDF |
| `.docx` | Word Document (ZIP container) |
| `.txt` | Plain text |
| `.md` / `.markdown` | Markdown |

Any other extension returns `HTTP 400 unsupported_file`.

### 3. File-Signature (Magic Byte) Validation

For binary formats, the raw file bytes are checked against known magic byte headers:

| Format | Expected header |
|---|---|
| `.pdf` | `%PDF-` |
| `.docx` | `PK\x03\x04` (ZIP local file header) |

If the content does not match, the file is rejected with `HTTP 400 invalid_file_signature`. This prevents extension-spoofing attacks (e.g., a `.exe` renamed to `.pdf`).

Text formats (`.txt`, `.md`, `.markdown`) have no fixed magic bytes and are accepted by extension only; they are further constrained by the character limit after extraction.

### 4. No Embedded Content Execution

- PDF text is extracted via PyMuPDF (`fitz`) — page text only; no JavaScript, no embedded scripts.
- DOCX text is extracted via `zipfile` + `xml.etree.ElementTree` — XML text nodes only; macros, embedded OLE objects, and scripts are never touched.
- No `subprocess`, `eval`, or `exec` is used in the extraction path.

### 5. local_only Privacy Guard

The `parse_file` endpoint accepts an optional `privacy_mode` form field. The endpoint documents the mode in its response. The extraction itself is **CPU-local** in all modes — no content is sent to any external provider. Future code paths that route to external providers **must** re-check `privacy_mode == "local_only"` and raise an error before any external call.

### 6. Temp File Cleanup

Temp files are written inside `temp_uploads/` (inside the workspace, outside web root) and deleted in a `finally` block whether extraction succeeds or fails.

---

## Frontend Single Source of Truth

`frontend/src/config/uploadLimits.js` exports:

```js
export const MAX_FILE_BYTES = 40 * 1024 * 1024     // 40 MB
export const ALLOWED_EXTENSIONS = ['.txt', '.md', '.markdown', '.pdf', '.docx']
export function formatBytes(bytes) { ... }
export function estimateProcessingTime(bytes) { ... }
```

Both `SwarmbookUploadView.vue` and `NewSimulationWizardView.vue` import from this file. Neither view hardcodes a size value.

---

## API — Limits Info Endpoint

```
GET /api/book_sim/limits
```

Returns:

```json
{
  "success": true,
  "data": {
    "max_file_bytes": 41943040,
    "max_manuscript_chars": 500000,
    "allowed_extensions": [".docx", ".markdown", ".md", ".pdf", ".txt"]
  }
}
```

---

## Changing Limits in the Future

1. Update `BOOK_SIM_MAX_FILE_BYTES` in `backend/app/api/book_sim.py`.
2. Update `MAX_FILE_BYTES` in `frontend/src/config/uploadLimits.js` to the same value.
3. Ensure `MAX_CONTENT_LENGTH` in `backend/app/config.py` remains at least 5× the app limit.
4. Update this document and `docs/SWARMBOOK_CHANGELOG.md`.

---

## Error Codes

| `error_code` | Trigger | HTTP |
|---|---|---|
| `unsupported_file` | Extension not in allow-list | 400 |
| `file_too_large` | Raw bytes > 40 MB, or extracted chars > 500,000 | 400 |
| `invalid_file_signature` | Magic bytes don't match extension | 400 |
| `parsing_failed` | Text extraction raised an exception | 400 |
| `validation_error` | Missing file, bad privacy_mode, etc. | 400 |
