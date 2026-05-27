<template>
  <SwarmbookAppShell
    active-route="SwarmbookMetadata"
    :project-id="session.projectId"
    title="Metadata Form"
    subtitle="Set the editorial context before generating the evidence pack. These fields are stored in the project metadata while the current evidence endpoint ingests manuscript text."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <section class="card">
      <div class="field-grid">
          <label>
            <span>Fiction / non-fiction / mixed</span>
            <select v-model="metadata.bookType">
              <option value="fiction">fiction</option>
              <option value="non-fiction">non-fiction</option>
              <option value="mixed">mixed</option>
            </select>
          </label>
        <label>
          <span>Genre / category</span>
          <input v-model="metadata.genre" type="text" placeholder="Speculative thriller" />
        </label>
        <label>
          <span>Target reader</span>
          <input v-model="metadata.targetReader" type="text" placeholder="Book club suspense readers" />
        </label>
        <label>
          <span>Privacy mode</span>
          <select v-model="metadata.privacyMode">
            <option value="local_only">local_only</option>
            <option value="hybrid_safe">hybrid_safe</option>
            <option value="cloud_quality">cloud_quality</option>
          </select>
        </label>
        <label>
          <span>Title</span>
          <input v-model="metadata.title" type="text" placeholder="Book title" />
        </label>
        <label>
          <span>Subtitle</span>
          <input v-model="metadata.subtitle" type="text" placeholder="Optional subtitle" />
        </label>
      </div>

      <label class="stack">
        <span>Blurb</span>
        <textarea v-model="metadata.blurb" rows="5" placeholder="Short market-facing description"></textarea>
      </label>

      <label class="stack">
        <span>Comp titles</span>
        <textarea v-model="metadata.compTitles" rows="3" placeholder="Comma-separated or line-separated comps"></textarea>
      </label>

      <label class="stack">
        <span>Cover brief</span>
        <textarea v-model="metadata.coverBrief" rows="4" placeholder="Mood, imagery, and packaging expectations"></textarea>
      </label>

      <div class="action-row">
        <button class="ghost-btn" @click="goBack">Back To Manuscript</button>
        <button class="primary-btn" :disabled="submitting || !canSubmit" @click="generateEvidence">
          {{ submitting ? 'Building...' : 'Generate Evidence Pack' }}
        </button>
      </div>
    </section>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { createBookSimProject, createEvidencePack } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const metadata = reactive({
  ...session.value.metadata,
})
const error = ref('')
const loadingMessage = ref('')
const submitting = ref(false)

const canSubmit = computed(() => {
  return Boolean(session.value.manuscript.text.trim() && metadata.title.trim())
})

function ensureSession() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId || !session.value.manuscript.text.trim()) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

function goBack() {
  session.value = updateSwarmbookSession({ metadata: { ...metadata } })
  router.push({ name: 'SwarmbookUpload', params: { projectId: session.value.projectId } })
}

async function generateEvidence() {
  submitting.value = true
  loadingMessage.value = 'Saving project metadata and generating evidence...'
  error.value = ''
  try {
    const projectResponse = await createBookSimProject({
      project_id: session.value.projectId,
      name: metadata.projectName || metadata.title,
      title: metadata.title,
      author_name: metadata.authorName,
      profile_name: metadata.localProfile || session.value.simulationConfig.profileName || 'hybrid_safe_default',
      privacy_mode: metadata.privacyMode,
      metadata: {
        book_type: metadata.bookType,
        genre: metadata.genre,
        target_reader: metadata.targetReader,
        subtitle: metadata.subtitle,
        blurb: metadata.blurb,
        comp_titles: metadata.compTitles,
        cover_brief: metadata.coverBrief,
        local_profile: metadata.localProfile || session.value.simulationConfig.profileName || 'hybrid_safe_default',
      },
    })

    const evidenceResponse = await createEvidencePack({
      project_id: projectResponse.data.project_id,
      title: metadata.title,
      author_name: metadata.authorName,
      text: session.value.manuscript.text,
      filename: session.value.manuscript.filename,
      language: session.value.manuscript.language,
      metadata: {
        book_type: metadata.bookType,
        genre: metadata.genre,
        target_reader: metadata.targetReader,
        subtitle: metadata.subtitle,
        blurb: metadata.blurb,
        comp_titles: metadata.compTitles,
        cover_brief: metadata.coverBrief,
      },
    })

    session.value = updateSwarmbookSession({
      projectId: projectResponse.data.project_id,
      project: projectResponse.data,
      metadata: { ...metadata },
      evidencePack: evidenceResponse.data.evidence_pack,
    })

    router.push({ name: 'SwarmbookEvidence', params: { projectId: projectResponse.data.project_id } })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loadingMessage.value = ''
    submitting.value = false
  }
}

onMounted(() => {
  ensureSession()
})
</script>

<style scoped>
.card {
  border: 1px solid #e5e5e5;
  padding: 20px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.stack {
  display: block;
  margin-top: 14px;
}

label span {
  display: block;
  font-size: 0.8rem;
  color: #666666;
  margin-bottom: 6px;
  font-family: 'JetBrains Mono', monospace;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid #d9d9d9;
  padding: 12px;
  font: inherit;
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

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
