<template>
  <SwarmbookAppShell
    active-route="SwarmbookUpload"
    :project-id="session.projectId"
    title="Upload Manuscript"
    subtitle="Load your draft manuscript (PDF, DOCX, TXT, or MD) to segment chapters and generate structured editorial evidence packs."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="upload-container">
      <section class="upload-card">
        <h2>Manuscript File Selection</h2>
        <p class="section-hint">Select your book file. Processing runs locally on your workstation to maintain strict data privacy.</p>

        <!-- Form Error Banner -->
        <div v-if="uploadError" class="error-banner" role="alert" aria-live="polite">
          <span class="error-badge">Upload Error</span>
          <p>{{ uploadError }}</p>
          <button class="clear-err-btn" @click="uploadError = ''" aria-label="Dismiss error">&times;</button>
        </div>

        <!-- Drag & Drop Area -->
        <div
          class="drop-zone"
          :class="{ 'is-dragover': dragOver, 'has-file': manuscript.filename }"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="onFileDrop"
          @click="triggerFileBrowser"
          @keydown.enter="triggerFileBrowser"
          @keydown.space.prevent="triggerFileBrowser"
          role="button"
          tabindex="0"
          aria-label="Drag and drop manuscript file here, or click to browse local files"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".txt,.md,.markdown,.pdf,.docx"
            class="hidden-input"
            @change="onFileSelect"
          />
          
          <div class="drop-zone-content" v-if="!manuscript.filename">
            <span class="upload-icon">📂</span>
            <h3>Drag &amp; drop manuscript here</h3>
            <p class="browse-link">or click to browse local folders</p>
            <span class="formats-label">Supported formats: PDF, DOCX, TXT, MD</span>
          </div>

          <div class="selected-file-display" v-else>
            <span class="file-icon">📄</span>
            <div class="file-details">
              <h3>{{ manuscript.filename }}</h3>
              <p class="file-meta">
                <span class="meta-tag">{{ formatBytes(manuscriptSize) }}</span>
                <span class="meta-tag" v-if="manuscriptType">{{ manuscriptType }}</span>
                <span class="meta-tag word-badge" v-if="wordCount">{{ wordCount.toLocaleString() }} words</span>
              </p>
            </div>
          </div>
        </div>

        <!-- File Details & Warnings (Visible only when file is selected) -->
        <div class="file-meta-panel" v-if="manuscript.filename">
          <div class="meta-section">
            <h4>Estimated Processing Time</h4>
            <p class="meta-text">~30 to 60 seconds on average local workstations (Ollama extraction loops).</p>
          </div>

          <div class="meta-section">
            <h4>Privacy Enforcement</h4>
            <div class="privacy-status-badge" :class="privacyMode">
              <span class="badge-icon">🔒</span>
              <div>
                <strong>{{ privacyMode }} mode active</strong>
                <p v-if="privacyMode === 'local_only'">Strictly offline. No manuscript content leaves your machine.</p>
                <p v-else-if="privacyMode === 'hybrid_safe'">Manuscript content is analyzed locally; embeddings map to secure offline structures.</p>
                <p v-else>Full cloud quality reasoning enabled. Safe encrypted processing is active.</p>
              </div>
            </div>
          </div>

          <div class="remove-action-row">
            <button class="remove-btn" @click="clearFile" aria-label="Remove uploaded manuscript file">
              ❌ Remove File
            </button>
          </div>
        </div>

        <!-- Collapsible Paste Manually option -->
        <div class="paste-collapse-container">
          <button 
            class="collapse-trigger-btn" 
            @click="showPasteArea = !showPasteArea"
            :aria-expanded="showPasteArea"
            aria-controls="paste-textarea-section"
          >
            {{ showPasteArea ? '▼ Hide Manual Paste Option' : '▶ Or Paste Manuscript Content Manually' }}
          </button>

          <transition name="slide-fade">
            <div id="paste-textarea-section" v-show="showPasteArea" class="paste-textarea-wrapper">
              <label class="textarea-label">
                <span>Paste Draft Text Content</span>
                <textarea
                  v-model="manuscript.text"
                  rows="12"
                  placeholder="Paste raw manuscript chapters here..."
                  @input="onPasteInput"
                ></textarea>
              </label>
              <div class="paste-stats" v-if="manuscript.text">
                <span>{{ manuscript.text.length.toLocaleString() }} characters</span>
                <span class="warn-label" v-if="manuscript.text.length > 500000">
                  ⚠️ Large content: Consider using a shorter excerpt for stable local processing.
                </span>
              </div>
            </div>
          </transition>
        </div>

        <!-- Navigation Action Buttons -->
        <footer class="action-footer">
          <button class="ghost-btn" @click="router.push({ name: 'SwarmbookHome' })">
            ← Back To Project
          </button>
          <button 
            class="primary-btn" 
            :disabled="!manuscript.text.trim() || loadingMessage" 
            @click="generateEvidencePack"
          >
            Generate Evidence Packs 🚀
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

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())

const manuscript = reactive({
  text: session.value.manuscript?.text || '',
  filename: session.value.manuscript?.filename || '',
  language: session.value.manuscript?.language || 'en',
})

const manuscriptSize = ref(session.value.manuscript?.sizeBytes || 0)
const manuscriptType = ref(session.value.manuscript?.mimeType || '')
const wordCount = ref(session.value.manuscript?.wordCount || 0)

const fileInput = ref(null)
const error = ref('')
const uploadError = ref('')
const loadingMessage = ref('')
const dragOver = ref(false)
const showPasteArea = ref(false)

const privacyMode = computed(() => session.value.metadata?.privacyMode || 'hybrid_safe')

function ensureProject() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

function triggerFileBrowser() {
  fileInput.value?.click()
}

function onFileSelect(event) {
  const selectedFile = event.target.files?.[0]
  if (selectedFile) {
    handleFileUpload(selectedFile)
  }
}

function onFileDrop(event) {
  dragOver.value = false
  const selectedFile = event.dataTransfer.files?.[0]
  if (selectedFile) {
    handleFileUpload(selectedFile)
  }
}

async function handleFileUpload(file) {
  uploadError.value = ''
  error.value = ''
  
  // 1. Extension validation
  const allowed = ['.txt', '.md', '.markdown', '.pdf', '.docx']
  const matched = allowed.some(ext => file.name.toLowerCase().endsWith(ext))
  if (!matched) {
    uploadError.value = `Unsupported file format. Please upload a .pdf, .docx, .txt, or .md document.`
    return
  }

  // 2. Pre-upload file size validation (10 MB Limit)
  const maxBytes = 10 * 1024 * 1024
  if (file.size > maxBytes) {
    const overBytes = file.size - maxBytes
    const overPercent = (overBytes / maxBytes) * 100
    uploadError.value = `File too large: "${file.name}" (${formatBytes(file.size)}) exceeds the maximum allowed limit of ${formatBytes(maxBytes)} (Oversized by ${formatBytes(overBytes)} / ${overPercent.toFixed(1)}%).`
    return
  }

  loadingMessage.value = `Uploading and parsing "${file.name}"...`
  try {
    const response = await parseManuscriptFile(file)
    const data = response.data.data || response.data
    
    manuscript.text = data.text
    manuscript.filename = data.filename
    manuscriptSize.value = data.size_bytes
    manuscriptType.value = data.mime_type
    wordCount.value = data.word_count
    
    saveSessionProgress()
  } catch (err) {
    const apiError = err.response?.data
    if (apiError && apiError.error_code === 'file_too_large') {
      const details = apiError.details
      if (details.unit === 'characters') {
        uploadError.value = `File too large: parsed manuscript (${details.actual_size.toLocaleString()} characters) exceeds the maximum allowed limit of ${details.max_size.toLocaleString()} characters (Oversized by ${details.oversized_absolute.toLocaleString()} characters / ${details.oversized_percentage.toFixed(1)}%).`
      } else {
        uploadError.value = `File too large: file size (${formatBytes(details.actual_size)}) exceeds the maximum allowed limit of ${formatBytes(details.max_size)} (Oversized by ${formatBytes(details.oversized_absolute)} / ${details.oversized_percentage.toFixed(1)}%).`
      }
    } else {
      uploadError.value = apiError?.error || `Upload/parsing failed: ${err.message}`
    }
  } finally {
    loadingMessage.value = ''
  }
}

function onPasteInput() {
  manuscript.filename = 'pasted_draft.txt'
  manuscriptSize.value = manuscript.text.length
  manuscriptType.value = 'text/plain'
  wordCount.value = manuscript.text.split(/\s+/).filter(Boolean).length
  saveSessionProgress()
}

function clearFile() {
  manuscript.text = ''
  manuscript.filename = ''
  manuscriptSize.value = 0
  manuscriptType.value = ''
  wordCount.value = 0
  uploadError.value = ''
  saveSessionProgress()
}

function saveSessionProgress() {
  session.value = updateSwarmbookSession({
    manuscript: {
      text: manuscript.text,
      filename: manuscript.filename,
      language: manuscript.language,
      sizeBytes: manuscriptSize.value,
      mimeType: manuscriptType.value,
      wordCount: wordCount.value,
    },
  })
}

async function generateEvidencePack() {
  if (!manuscript.text.trim()) return

  loadingMessage.value = 'Generating editorial evidence pack details (Book DNA, maps, pacing)...'
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
        mimeType: manuscriptType.value,
        wordCount: wordCount.value,
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

function formatBytes(bytes) {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

onMounted(() => {
  ensureProject()
})
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.upload-card h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.section-hint {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0 0 24px 0;
}

/* Drop zone styling */
.drop-zone {
  border: 2px dashed #cbd5e1;
  background: #f8fafc;
  border-radius: 10px;
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  outline: none;
  position: relative;
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
}

.drop-zone.has-file {
  border-style: solid;
  border-color: #cbd5e1;
  background: #ffffff;
  padding: 24px;
  text-align: left;
}

.hidden-input {
  display: none;
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.drop-zone-content h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.browse-link {
  font-size: 0.88rem;
  color: #ff4500;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.formats-label {
  font-size: 0.75rem;
  color: #94a3b8;
  font-family: 'JetBrains Mono', monospace;
}

/* File Selected Display */
.selected-file-display {
  display: flex;
  align-items: center;
  gap: 16px;
}

.file-icon {
  font-size: 2.5rem;
}

.file-details h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px 0;
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

.meta-tag.word-badge {
  background: #e0f2fe;
  color: #0369a1;
}

/* File Metadata Panel */
.file-meta-panel {
  margin-top: 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.meta-section h4 {
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  margin: 0 0 4px 0;
  letter-spacing: 0.5px;
}

.meta-text {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
}

.privacy-status-badge {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  margin-top: 6px;
}

.privacy-status-badge.local_only {
  border-left: 4px solid #10b981;
}

.privacy-status-badge.hybrid_safe {
  border-left: 4px solid #f59e0b;
}

.privacy-status-badge.cloud_quality {
  border-left: 4px solid #3b82f6;
}

.badge-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.privacy-status-badge strong {
  font-size: 0.82rem;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
}

.privacy-status-badge p {
  font-size: 0.78rem;
  color: #64748b;
  margin: 2px 0 0 0;
  line-height: 1.4;
}

.remove-action-row {
  display: flex;
  justify-content: flex-end;
}

.remove-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.remove-btn:hover {
  background: #fef2f2;
}

.remove-btn:focus-visible {
  outline: 2px solid #ef4444;
}

/* Collapsible Manual Paste */
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

.collapse-trigger-btn:hover {
  color: #ff4500;
}

.collapse-trigger-btn:focus-visible {
  outline: 2px solid #ff4500;
  border-radius: 4px;
}

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
}

textarea:focus {
  border-color: #ff4500;
  box-shadow: 0 0 0 3px rgba(255, 69, 0, 0.1);
}

.paste-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
}

.warn-label {
  color: #b45309;
}

/* Action Footer */
.action-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.ghost-btn,
.primary-btn {
  padding: 12px 20px;
  font-size: 0.88rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.ghost-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
}

.ghost-btn:hover {
  background: #f8fafc;
  color: #0f172a;
}

.ghost-btn:focus-visible {
  outline: 2px solid #cbd5e1;
}

.primary-btn {
  background: #ff4500;
  border: 1px solid #ff4500;
  color: #ffffff;
}

.primary-btn:hover {
  background: #e03d00;
  border-color: #e03d00;
}

.primary-btn:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 2px;
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #cbd5e1;
  border-color: #cbd5e1;
}

/* Error Banner styling */
.error-banner {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #991b1b;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  position: relative;
}

.error-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  background: #fee2e2;
  color: #991b1b;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.error-banner p {
  font-size: 0.82rem;
  line-height: 1.4;
  margin: 0;
  flex: 1;
}

.clear-err-btn {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 4px;
}

/* Transitions */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
