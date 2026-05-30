/**
 * Upload limits shared configuration.
 * These values mirror the backend BOOK_SIM_MAX_FILE_BYTES constant in book_sim.py.
 * Update both when changing limits.
 */

/** Maximum file size in bytes for manuscript uploads (40 MB = 4× original 10 MB limit). */
export const MAX_FILE_BYTES = 40 * 1024 * 1024

/** Supported file extensions for manuscript upload. */
export const ALLOWED_EXTENSIONS = ['.txt', '.md', '.markdown', '.pdf', '.docx']

/** Human-readable label for allowed formats. */
export const ALLOWED_FORMATS_LABEL = 'PDF, DOCX, TXT, MD'

/**
 * Format a byte count as a human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

/**
 * Estimate processing time in a human-friendly string based on file size.
 * @param {number} bytes
 * @returns {string}
 */
export function estimateProcessingTime(bytes) {
  if (!bytes) return 'a few seconds'
  const mb = bytes / (1024 * 1024)
  if (mb < 1) return '< 10 seconds'
  if (mb < 5) return '~15–30 seconds'
  if (mb < 15) return '~30–60 seconds'
  if (mb < 30) return '~1–2 minutes'
  return '~2–4 minutes'
}
