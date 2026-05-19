<template>
  <SwarmbookLayout
    active-route="SwarmbookUpload"
    :project-id="session.projectId"
    title="Manuscript Input"
    subtitle="Load draft text into the frontend session first. The current backend evidence endpoint expects text, so text input stays the source of truth."
    :status-text="statusText"
    :status-tone="statusTone"
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <section class="card">
      <h2>Upload Or Paste</h2>
      <div class="upload-box" @click="fileInput?.click()">
        <input ref="fileInput" type="file" accept=".txt,.md,.markdown,.pdf" class="hidden-input" @change="onFileSelect" />
        <p>{{ manuscript.filename || 'Click to load a .txt, .md, or .pdf file' }}</p>
        <span class="upload-note">Text files are loaded directly. For PDFs, paste extracted text below.</span>
      </div>
      <label class="stack">
        <span>Manuscript text</span>
        <textarea
          v-model="manuscript.text"
          rows="18"
          placeholder="Paste manuscript text here or load a plain-text file."
        ></textarea>
        <p class="hint">
          {{ manuscript.text.length.toLocaleString() }} characters
          <span v-if="tooLarge" class="hint-warn"> (Large paste: start with an excerpt for stable local runs.)</span>
        </p>
      </label>
      <div class="field-grid">
        <label>
          <span>Detected filename</span>
          <input v-model="manuscript.filename" type="text" placeholder="draft.md" />
        </label>
        <label>
          <span>Language</span>
          <input v-model="manuscript.language" type="text" placeholder="en" />
        </label>
      </div>
      <div class="action-row">
        <button class="ghost-btn" @click="router.push({ name: 'SwarmbookHome' })">Back To Project</button>
        <button class="primary-btn" :disabled="!manuscript.text.trim()" @click="continueToMetadata">Continue To Metadata</button>
      </div>
    </section>
  </SwarmbookLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookLayout from '../../components/swarmbook/SwarmbookLayout.vue'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const manuscript = reactive({
  ...session.value.manuscript,
})
const fileInput = ref(null)
const error = ref('')
const loadingMessage = ref('')
const statusText = 'Draft pending'
const statusTone = 'loading'
const tooLarge = computed(() => manuscript.text && manuscript.text.length > 500000)

function ensureProject() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

function onFileSelect(event) {
  const selectedFile = event.target.files?.[0]
  if (!selectedFile) {
    return
  }
  manuscript.filename = selectedFile.name
  error.value = ''

  if (selectedFile.name.toLowerCase().endsWith('.pdf')) {
    error.value = 'PDF selection is recorded, but the current frontend still needs pasted text for evidence generation.'
    return
  }

  loadingMessage.value = `Reading ${selectedFile.name}...`
  const reader = new FileReader()
  reader.onload = () => {
    manuscript.text = String(reader.result || '')
    loadingMessage.value = ''
  }
  reader.onerror = () => {
    loadingMessage.value = ''
    error.value = `Failed to read ${selectedFile.name}`
  }
  reader.readAsText(selectedFile)
}

function continueToMetadata() {
  session.value = updateSwarmbookSession({
    manuscript: {
      ...manuscript,
    },
  })
  router.push({ name: 'SwarmbookMetadata', params: { projectId: session.value.projectId } })
}

onMounted(() => {
  ensureProject()
})
</script>

<style scoped>
.card {
  border: 1px solid #e5e5e5;
  padding: 20px;
}

.card h2 {
  margin-bottom: 16px;
}

.upload-box {
  border: 1px dashed #bfbfbf;
  background: #fafafa;
  padding: 18px;
  cursor: pointer;
  margin-bottom: 16px;
}

.upload-note {
  display: block;
  color: #666666;
  margin-top: 8px;
  font-size: 0.85rem;
}

.hidden-input {
  display: none;
}

.stack {
  display: block;
  margin-bottom: 16px;
}

.stack span,
label span {
  display: block;
  font-size: 0.8rem;
  color: #666666;
  margin-bottom: 6px;
  font-family: 'JetBrains Mono', monospace;
}

textarea,
input {
  width: 100%;
  border: 1px solid #d9d9d9;
  padding: 12px;
  font: inherit;
}

.hint {
  margin-top: 8px;
  color: #666666;
  font-size: 0.85rem;
}

.hint-warn {
  color: #8a5b00;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
  flex-wrap: wrap;
}

.primary-btn,
.ghost-btn {
  border: 1px solid #000000;
  padding: 12px 16px;
  cursor: pointer;
  font: inherit;
}

.primary-btn {
  background: #000000;
  color: #ffffff;
}

.ghost-btn {
  background: #ffffff;
}

@media (max-width: 900px) {
  .field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
