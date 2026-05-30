<template>
  <SwarmbookAppShell
    active-route="SwarmbookUpload"
    :project-id="session.projectId"
    title="Upload Manuscript"
    subtitle="Load your draft (PDF, DOCX, TXT, or MD) to segment chapters and generate structured editorial evidence packs."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="upload-container">
      <section class="upload-card">
        <h2>Manuscript File</h2>
        <p class="section-hint">
          Your file is processed entirely on this workstation.
          Nothing is transmitted unless you switch to Cloud Quality mode.
        </p>

        <!-- Error Banner -->
        <div v-if="uploadError" class="error-banner" role="alert" aria-live="polite">
          <span class="error-badge">{{ uploadErrorCode || 'Upload Error' }}</span>
          <p>{{ uploadError }}</p>
          <button class="clear-err-btn" @click="dismissError" aria-label="Dismiss error">&times;</button>
        </div>

        <!-- Drag & Drop Zone -->
        <div
          class="drop-zone"
          :class="{
            'is-dragover': dragOver,
            'has-file': manuscript.filename,
            'is-uploading': uploading,
          }"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="onFileDrop"
          @click="!uploading && triggerFileBrowser()"
          @keydown.enter="!uploading && triggerFileBrowser()"
          @keydown.space.prevent="!uploading && triggerFileBrowser()"
          role="button"
          tabindex="0"
          :aria-label="manuscript.filename
            ? `Selected: ${manuscript.filename}. Click to replace.`
            : 'Drag and drop manuscript file here, or click to browse'"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".txt,.md,.markdown,.pdf,.docx"
            class="hidden-input"
            @change="onFileSelect"
          />

          <!-- Empty State -->
          <div class="drop-zone-content" v-if="!manuscript.filename && !uploading">
            <span class="upload-icon" aria-hidden="true">📂</span>
            <h3>Drag &amp; drop your manuscript</h3>
            <p class="browse-link">or click to browse local files</p>
            <ul class="formats-list" aria-label="Supported file formats">
              <li v-for="fmt in FORMATS_META" :key="fmt.ext" class="format-chip">
                <span class="fmt-ext">{{ fmt.ext }}</span>
                <span class="fmt-label">{{ fmt.label }}</span>
              </li>
            </ul>
            <p class="size-limit-note">Maximum: {{ fmtBytes(MAX_FILE_BYTES) }}</p>
          </div>

          <!-- Upload Progress -->
          <div class="uploading-state" v-else-if="uploading">
            <span class="spin-icon" aria-hidden="true">⏳</span>
            <p class="uploading-label">Parsing <strong>{{ pendingFilename }}</strong>…</p>
            <div class="progress-bar-track" role="progressbar" aria-label="Upload progress">
              <div class="progress-bar-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <p class="uploading-sub">{{ uploadProgressLabel }}</p>
          </div>

          <!-- File Selected State -->
          <div class="selected-file-display" v-else>
            <span class="file-icon" :aria-label="fileFormatLabel">{{ fileFormatEmoji }}</span>
            <div class="file-details">
              <h3>{{ manuscript.filename }}</h3>
              <div class="file-meta-tags">
                <span class="meta-tag">{{ fmtBytes(manuscriptSize) }}</span>
                <span class="meta-tag fmt-badge">{{ fileFormatLabel }}</span>
                <span class="meta-tag word-badge" v-if="wordCount">
                  {{ wordCount.toLocaleString() }} words
                </span>
                <span class="meta-tag section-badge" v-if="sectionCount > 0">
                  {{ sectionCount }} {{ sectionCount === 1 ? 'section' : 'sections' }} detected
                </span>
              </div>
              <p class="replace-hint">Click or drag to replace</p>
            </div>
          </div>
        </div>

        <!-- File Metadata Panel (shown after successful parse) -->
        <transition name="panel-slide">
          <div class="file-meta-panel" v-if="manuscript.filename && !uploading">

            <!-- Processing Estimate -->
            <div class="meta-row">
              <span class="meta-row-icon" aria-hidden="true">⏱</span>
              <div>
                <strong class="meta-row-label">Evidence Pack Build Time</strong>
                <p class="meta-row-text">Approx. {{ processingEstimate }} on a typical local workstation (Ollama extraction loops).</p>
              </div>
            </div>

            <!-- Section breakdown (if detected) -->
            <div class="meta-row" v-if="sectionCount > 0">
              <span class="meta-row-icon" aria-hidden="true">📑</span>
              <div>
                <strong class="meta-row-label">Detected Structure</strong>
                <p class="meta-row-text">{{ sectionCount }} chapter / section heading{{ sectionCount === 1 ? '' : 's' }} found. The evidence builder will use these as editorial anchor points.</p>
              </div>
            </div>

            <!-- Privacy Mode Strip -->
            <div class="privacy-strip" :class="privacyMode">
              <span class="privacy-icon" aria-hidden="true">{{ privacyIcon }}</span>
              <div class="privacy-content">
                <strong class="privacy-mode-label">{{ privacyModeLabel }}</strong>
                <p class="privacy-desc">{{ privacyModeDesc }}</p>
              </div>
              <span class="privacy-badge" :class="privacyMode">{{ privacyMode }}</span>
            </div>

            <!-- Actions Row -->
            <div class="file-actions-row">
              <button
                class="action-btn danger-btn"
                @click="clearFile"
                aria-label="Remove uploaded manuscript file"
              >
                🗑 Remove File
              </button>
              <button
                class="action-btn replace-btn"
                @click="triggerFileBrowser"
                aria-label="Replace with a different file"
              >
                🔄 Replace File
              </button>
            </div>
          </div>
        </transition>

        <!-- Collapsible Manual Paste -->
        <div class="paste-collapse-container">
          <button
            class="collapse-trigger-btn"
            @click="showPasteArea = !showPasteArea"
            :aria-expanded="showPasteArea"
            aria-controls="paste-textarea-section"
          >
            {{ showPasteArea ? '▼ Hide Manual Paste' : '▶ Or Paste Manuscript Content Manually' }}
          </button>

          <transition name="slide-fade">
            <div id="paste-textarea-section" v-show="showPasteArea" class="paste-textarea-wrapper">
              <label class="textarea-label">
                <span>Paste Draft Text</span>
                <textarea
                  v-model="manuscript.text"
                  rows="12"
                  placeholder="Paste raw manuscript chapters here…"
                  @input="onPasteInput"
                ></textarea>
              </label>
              <div class="paste-stats" v-if="manuscript.text">
                <span>{{ manuscript.text.length.toLocaleString() }} characters</span>
                <span>{{ pasteWordCount.toLocaleString() }} words</span>
                <span class="warn-label" v-if="manuscript.text.length > 500000">
                  ⚠ Large — consider a shorter excerpt for stable local processing
                </span>
              </div>
            </div>
          </transition>
        </div>

        <!-- Navigation Footer -->
        <footer class="action-footer">
          <button class="ghost-btn" @click="router.push({ name: 'SwarmbookHome' })">
            ← Back to Project
          </button>
          <button
            class="primary-btn"
            :disabled="!canProceed || !!loadingMessage"
            @click="generateEvidencePack"
          >
            Generate Evidence Pack 🚀
          </button>
        </footer>
      </section>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'
import { parseManuscriptFile, createEvidencePack } from '../../api/bookSim'
import {
  MAX_FILE_BYTES,
  ALLOWED_EXTENSIONS,
  formatBytes as fmtBytes,
  estimateProcessingTime,
} from '../../config/uploadLimits'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())

const manuscript = reactive({
  text: session.value.manuscript?.text || '',
  filename: session.value.manuscript?.filename || '',
  language: session.value.manuscript?.language || 'en',
})
const manuscriptSize = ref(session.value.manuscript?.sizeBytes || 0)
const wordCount = ref(session.value.manuscript?.wordCount || 0)
const sectionCount = ref(session.value.manuscript?.sectionCount || 0)

const fileInput = ref(null)
const error = ref('')
const uploadError = ref('')
const uploadErrorCode = ref('')
const loadingMessage = ref('')
const dragOver = ref(false)
const showPasteArea = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadProgressLabel = ref('Reading file…')
const pendingFilename = ref('')

// ─── Privacy ──────────────────────────────────────────────────────────────────
const privacyMode = computed(() => session.value.metadata?.privacyMode || 'hybrid_safe')

const privacyModeLabel = computed(() => ({
  local_only: '🔒 Local Only — strictly offline',
  hybrid_safe: '🔐 Hybrid Safe — local extract, safe cloud reasoning',
  cloud_quality: '☁️ Cloud Quality — full cloud reasoning',
}[privacyMode.value] ?? privacyMode.value))

const privacyModeDesc = computed(() => ({
  local_only: 'No manuscript content leaves this machine under any condition.',
  hybrid_safe: 'Manuscript text is extracted locally. Anonymised semantic embeddings only are used for cloud reasoning.',
  cloud_quality: 'Full manuscript content may be sent to an encrypted cloud provider for deep reasoning.',
}[privacyMode.value] ?? ''))

const privacyIcon = computed(() => ({
  local_only: '🟢',
  hybrid_safe: '🟡',
  cloud_quality: '🔵',
}[privacyMode.value] ?? '⚪'))

// ─── Format metadata ──────────────────────────────────────────────────────────
const FORMATS_META = [
  { ext: '.pdf',  label: 'Adobe PDF',   emoji: '📕' },
  { ext: '.docx', label: 'Word Doc',    emoji: '📘' },
  { ext: '.md',   label: 'Markdown',    emoji: '📝' },
  { ext: '.txt',  label: 'Plain Text',  emoji: '📄' },
]

const fileExt = computed(() => {
  if (!manuscript.filename) return ''
  return manuscript.filename.split('.').pop()?.toLowerCase() || ''
})

const fileFormatEmoji = computed(() => {
  const m = FORMATS_META.find(f => f.ext === '.' + fileExt.value)
  return m ? m.emoji : '📄'
})

const fileFormatLabel = computed(() => {
  const m = FORMATS_META.find(f => f.ext === '.' + fileExt.value)
  return m ? m.label : fileExt.value.toUpperCase()
})

const processingEstimate = computed(() => estimateProcessingTime(manuscriptSize.value))

const canProceed = computed(() => manuscript.text.trim().length > 0)

const pasteWordCount = computed(() =>
  manuscript.text ? manuscript.text.split(/\s+/).filter(Boolean).length : 0
)

// ─── File browser helpers ─────────────────────────────────────────────────────
function ensureProject() {
  if (!session.value.projectId) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

function triggerFileBrowser() {
  fileInput.value?.click()
}

function onFileSelect(event) {
  const file = event.target.files?.[0]
  if (file) handleFileUpload(file)
  // Reset input so re-selecting the same file fires change
  event.target.value = ''
}

function onFileDrop(event) {
  dragOver.value = false
  const file = event.dataTransfer.files?.[0]
  if (file) handleFileUpload(file)
}

function dismissError() {
  uploadError.value = ''
  uploadErrorCode.value = ''
}

// ─── Core upload handler ──────────────────────────────────────────────────────
async function handleFileUpload(file) {
  dismissError()
  error.value = ''

  // 1. Extension validation (client-side gate)
  const nameLower = file.name.toLowerCase()
  const matched = ALLOWED_EXTENSIONS.some(ext => nameLower.endsWith(ext))
  if (!matched) {
    uploadErrorCode.value = 'Unsupported Format'
    uploadError.value = `"${file.name}" is not a supported format. Please upload a PDF, DOCX, TXT, or MD document.`
    return
  }

  // 2. Size validation (client-side gate — 40 MB)
  if (file.size > MAX_FILE_BYTES) {
    const overBytes = file.size - MAX_FILE_BYTES
    const overPct = ((overBytes / MAX_FILE_BYTES) * 100).toFixed(1)
    uploadErrorCode.value = 'File Too Large'
    uploadError.value =
      `"${file.name}" is ${fmtBytes(file.size)} — ${fmtBytes(overBytes)} (${overPct}%) over the ${fmtBytes(MAX_FILE_BYTES)} limit. ` +
      `Try a shorter excerpt, or split into chapters.`
    return
  }

  // 3. Start upload UI
  uploading.value = true
  uploadProgress.value = 10
  pendingFilename.value = file.name
  uploadProgressLabel.value = 'Sending to local parser…'

  // Simulate staged progress while waiting for the API response
  const ticker = setInterval(() => {
    if (uploadProgress.value < 80) {
      uploadProgress.value += 8
      if (uploadProgress.value > 35) uploadProgressLabel.value = 'Extracting text…'
      if (uploadProgress.value > 60) uploadProgressLabel.value = 'Detecting sections…'
    }
  }, 400)

  try {
    const response = await parseManuscriptFile(file)
    const data = response.data?.data || response.data

    uploadProgress.value = 100
    uploadProgressLabel.value = 'Done!'

    manuscript.text = data.text
    manuscript.filename = data.filename
    manuscriptSize.value = data.size_bytes
    wordCount.value = data.word_count
    sectionCount.value = data.section_count ?? 0

    saveSessionProgress()
  } catch (err) {
    const apiError = err.response?.data
    const code = apiError?.error_code || 'upload_error'
    uploadErrorCode.value = codeToLabel(code)

    if (code === 'file_too_large') {
      const d = apiError.details || {}
      if (d.unit === 'characters') {
        uploadError.value =
          `Parsed manuscript (${(d.actual_size || 0).toLocaleString()} chars) exceeds the ${(d.max_size || 0).toLocaleString()}-character processing limit. ` +
          `Consider uploading a shorter draft or splitting chapters.`
      } else {
        uploadError.value =
          `Server rejected the file: ${fmtBytes(d.actual_size)} exceeds the ${fmtBytes(d.max_size)} limit.`
      }
    } else if (code === 'unsupported_file') {
      uploadError.value = `"${file.name}" is not a supported format. Allowed: ${(apiError.details?.supported || []).join(', ')}.`
    } else if (code === 'invalid_file_signature') {
      uploadError.value =
        `"${file.name}" appears to be a different file type than its extension suggests. ` +
        `Please use the original file without renaming.`
    } else if (code === 'parsing_failed') {
      uploadError.value =
        `Could not extract text from "${file.name}". ` +
        `The file may be encrypted, password-protected, or corrupted. ` +
        (apiError.details?.error ? `(${apiError.details.error})` : '')
    } else {
      uploadError.value = apiError?.error || `Upload failed: ${err.message}`
    }
  } finally {
    clearInterval(ticker)
    uploading.value = false
    uploadProgress.value = 0
    pendingFilename.value = ''
    uploadProgressLabel.value = 'Reading file…'
  }
}

function codeToLabel(code) {
  const map = {
    file_too_large: 'File Too Large',
    unsupported_file: 'Unsupported Format',
    invalid_file_signature: 'Invalid File',
    parsing_failed: 'Parse Error',
    validation_error: 'Validation Error',
  }
  return map[code] || 'Upload Error'
}

// ─── Manual paste ─────────────────────────────────────────────────────────────
function onPasteInput() {
  manuscript.filename = 'pasted_draft.txt'
  manuscriptSize.value = manuscript.text.length
  wordCount.value = manuscript.text.split(/\s+/).filter(Boolean).length
  sectionCount.value = 0
  saveSessionProgress()
}

// ─── Clear / replace ──────────────────────────────────────────────────────────
function clearFile() {
  manuscript.text = ''
  manuscript.filename = ''
  manuscriptSize.value = 0
  wordCount.value = 0
  sectionCount.value = 0
  dismissError()
  saveSessionProgress()
}

// ─── Session persistence ──────────────────────────────────────────────────────
function saveSessionProgress() {
  session.value = updateSwarmbookSession({
    manuscript: {
      text: manuscript.text,
      filename: manuscript.filename,
      language: manuscript.language,
      sizeBytes: manuscriptSize.value,
      wordCount: wordCount.value,
      sectionCount: sectionCount.value,
    },
  })
}

// ─── Evidence Pack generation ─────────────────────────────────────────────────
async function generateEvidencePack() {
  if (!canProceed.value) return

  loadingMessage.value = 'Generating editorial evidence pack (Book DNA, maps, pacing)…'
  error.value = ''

  try {
    const response = await createEvidencePack({
      project_id: session.value.projectId,
      title: session.value.metadata?.title || manuscript.filename || 'Untitled Draft',
      author_name: session.value.metadata?.authorName || 'Unknown Author',
      text: manuscript.text,
      filename: manuscript.filename || 'draft.txt',
      language: manuscript.language,
      metadata: {
        book_type: session.value.metadata?.bookType || 'fiction',
        genre: session.value.metadata?.genre || '',
        target_reader: session.value.metadata?.targetReader || '',
        subtitle: session.value.metadata?.subtitle || '',
        blurb: session.value.metadata?.blurb || '',
        comp_titles: session.value.metadata?.compTitles || '',
        cover_brief: session.value.metadata?.coverBrief || '',
        local_profile: session.value.metadata?.localProfile || 'hybrid_safe_default',
      },
    })

    const pack = response.data?.evidence_pack || response.data?.data?.evidence_pack
    session.value = updateSwarmbookSession({
      manuscript: {
        text: manuscript.text,
        filename: manuscript.filename,
        language: manuscript.language,
        sizeBytes: manuscriptSize.value,
        wordCount: wordCount.value,
        sectionCount: sectionCount.value,
      },
      evidencePack: pack,
    })

    router.push({ name: 'SwarmbookEvidence', params: { projectId: session.value.projectId } })
  } catch (err) {
    error.value = err.response?.data?.error || `Failed to generate evidence pack: ${err.message}`
  } finally {
    loadingMessage.value = ''
  }
}

onMounted(() => {
  ensureProject()
})
</script>

<style scoped>
/* ─── Layout ──────────────────────────────────────────────────────────────── */
.upload-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 36px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.upload-card h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.section-hint {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

/* ─── Drop Zone ───────────────────────────────────────────────────────────── */
.drop-zone {
  border: 2px dashed #cbd5e1;
  background: #f8fafc;
  border-radius: 12px;
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  outline: none;
  position: relative;
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover,
.drop-zone:focus-visible {
  border-color: #ff4500;
  background: #fffafa;
}

.drop-zone:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 2px;
}

.drop-zone.is-dragover {
  border-color: #ff4500;
  background: #fff5ef;
  transform: scale(1.01);
}

.drop-zone.has-file {
  border-style: solid;
  border-color: #c7d2fe;
  background: #f0f9ff;
  padding: 24px;
  text-align: left;
  justify-content: flex-start;
}

.drop-zone.is-uploading {
  cursor: wait;
  border-color: #ff4500;
  background: #fffafa;
}

.hidden-input {
  display: none;
}

/* ─── Empty State ─────────────────────────────────────────────────────────── */
.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  font-size: 2.8rem;
  line-height: 1;
}

.drop-zone-content h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.browse-link {
  font-size: 0.85rem;
  color: #ff4500;
  font-weight: 600;
  margin: 0;
}

.formats-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
  list-style: none;
  padding: 0;
  margin: 4px 0 0 0;
}

.format-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.75rem;
}

.fmt-ext {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #334155;
}

.fmt-label {
  color: #64748b;
}

.size-limit-note {
  font-size: 0.73rem;
  color: #94a3b8;
  font-family: 'JetBrains Mono', monospace;
  margin: 0;
}

/* ─── Upload Progress ─────────────────────────────────────────────────────── */
.uploading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
  max-width: 380px;
}

.spin-icon {
  font-size: 2rem;
  animation: spin 1.4s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

.uploading-label {
  font-size: 0.92rem;
  color: #0f172a;
  margin: 0;
}

.progress-bar-track {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 99px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff4500, #ff7043);
  border-radius: 99px;
  transition: width 0.3s ease;
}

.uploading-sub {
  font-size: 0.75rem;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
  margin: 0;
}

/* ─── File Selected Display ───────────────────────────────────────────────── */
.selected-file-display {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.file-icon {
  font-size: 2.8rem;
  line-height: 1;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-details h3 {
  font-size: 1.0rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.meta-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  background: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.fmt-badge {
  background: #ede9fe;
  color: #6d28d9;
}

.word-badge {
  background: #e0f2fe;
  color: #0369a1;
}

.section-badge {
  background: #dcfce7;
  color: #166534;
}

.replace-hint {
  font-size: 0.73rem;
  color: #94a3b8;
  margin: 8px 0 0 0;
}

/* ─── File Metadata Panel ─────────────────────────────────────────────────── */
.file-meta-panel {
  margin-top: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.meta-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.meta-row-icon {
  font-size: 1.2rem;
  line-height: 1.2;
  flex-shrink: 0;
  margin-top: 1px;
}

.meta-row-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #334155;
  display: block;
  margin-bottom: 2px;
}

.meta-row-text {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0;
  line-height: 1.45;
}

/* ─── Privacy Strip ───────────────────────────────────────────────────────── */
.privacy-strip {
  display: flex;
  gap: 12px;
  align-items: center;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #cbd5e1;
  border-radius: 8px;
  padding: 12px 16px;
}

.privacy-strip.local_only  { border-left-color: #10b981; }
.privacy-strip.hybrid_safe { border-left-color: #f59e0b; }
.privacy-strip.cloud_quality { border-left-color: #3b82f6; }

.privacy-icon {
  font-size: 1.1rem;
  line-height: 1;
  flex-shrink: 0;
}

.privacy-content {
  flex: 1;
  min-width: 0;
}

.privacy-mode-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #0f172a;
  display: block;
}

.privacy-desc {
  font-size: 0.76rem;
  color: #64748b;
  margin: 2px 0 0 0;
  line-height: 1.4;
}

.privacy-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.privacy-badge.local_only   { background: #d1fae5; color: #065f46; }
.privacy-badge.hybrid_safe  { background: #fef3c7; color: #92400e; }
.privacy-badge.cloud_quality { background: #dbeafe; color: #1e40af; }

/* ─── File Actions Row ────────────────────────────────────────────────────── */
.file-actions-row {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.action-btn {
  font-size: 0.82rem;
  font-weight: 600;
  padding: 7px 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  outline: none;
  border: 1px solid transparent;
}

.action-btn:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 2px;
}

.danger-btn {
  background: transparent;
  color: #ef4444;
  border-color: #fca5a5;
}

.danger-btn:hover {
  background: #fef2f2;
}

.replace-btn {
  background: transparent;
  color: #3b82f6;
  border-color: #93c5fd;
}

.replace-btn:hover {
  background: #eff6ff;
}

/* ─── Manual Paste Section ────────────────────────────────────────────────── */
.paste-collapse-container {
  margin-top: 24px;
  border-top: 1px solid #e2e8f0;
  padding-top: 20px;
}

.collapse-trigger-btn {
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  outline: none;
  padding: 4px 0;
}

.collapse-trigger-btn:hover   { color: #ff4500; }
.collapse-trigger-btn:focus-visible { outline: 2px solid #ff4500; border-radius: 4px; }

.paste-textarea-wrapper {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.textarea-label span {
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
  display: block;
  margin-bottom: 6px;
}

textarea {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 12px;
  font-family: inherit;
  font-size: 0.88rem;
  outline: none;
  box-sizing: border-box;
  resize: vertical;
}

textarea:focus {
  border-color: #ff4500;
  box-shadow: 0 0 0 3px rgba(255, 69, 0, 0.1);
}

.paste-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
}

.warn-label { color: #b45309; }

/* ─── Footer ──────────────────────────────────────────────────────────────── */
.action-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
  gap: 12px;
}

.ghost-btn,
.primary-btn {
  padding: 11px 20px;
  font-size: 0.88rem;
  font-weight: 600;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.ghost-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
}

.ghost-btn:hover { background: #f8fafc; color: #0f172a; }
.ghost-btn:focus-visible { outline: 2px solid #cbd5e1; }

.primary-btn {
  background: #ff4500;
  border: 1px solid #ff4500;
  color: #ffffff;
}

.primary-btn:hover { background: #e03d00; border-color: #e03d00; }
.primary-btn:focus-visible { outline: 2px solid #ff4500; outline-offset: 2px; }
.primary-btn:disabled { opacity: 0.45; cursor: not-allowed; background: #cbd5e1; border-color: #cbd5e1; }

/* ─── Error Banner ────────────────────────────────────────────────────────── */
.error-banner {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #991b1b;
  padding: 14px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.error-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  background: #fee2e2;
  color: #991b1b;
  padding: 2px 7px;
  border-radius: 4px;
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
}

.error-banner p {
  font-size: 0.82rem;
  line-height: 1.45;
  margin: 0;
  flex: 1;
}

.clear-err-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 1.15rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 4px;
  flex-shrink: 0;
}

/* ─── Transitions ─────────────────────────────────────────────────────────── */
.slide-fade-enter-active,
.slide-fade-leave-active { transition: all 0.2s ease-out; }
.slide-fade-enter-from,
.slide-fade-leave-to { opacity: 0; transform: translateY(-8px); }

.panel-slide-enter-active,
.panel-slide-leave-active { transition: all 0.25s ease-out; }
.panel-slide-enter-from,
.panel-slide-leave-to { opacity: 0; transform: translateY(-6px); }

/* ─── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 600px) {
  .upload-card { padding: 20px 16px; }
  .drop-zone { padding: 28px 16px; }
  .formats-list { gap: 6px; }
  .file-actions-row { justify-content: stretch; }
  .action-btn { flex: 1; text-align: center; }
  .action-footer { flex-direction: column; }
  .ghost-btn, .primary-btn { width: 100%; }
}
</style>
