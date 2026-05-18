<template>
  <SwarmbookLayout
    active-route="SwarmbookHome"
    :project-id="session.projectId"
    title="Swarmbook Project"
    subtitle="Start a local-first manuscript stress test without disturbing the existing MiroFish graph and simulation flow."
    :status-text="healthStatus"
    :status-tone="healthTone"
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <section class="grid">
      <div class="card">
        <h2>New Project</h2>
        <div class="field-grid">
          <label>
            <span>Project name</span>
            <input v-model="form.projectName" type="text" placeholder="Spring thriller draft" />
          </label>
          <label>
            <span>Title</span>
            <input v-model="form.title" type="text" placeholder="Book title" />
          </label>
          <label>
            <span>Author</span>
            <input v-model="form.authorName" type="text" placeholder="Author name" />
          </label>
          <label>
            <span>Privacy mode</span>
            <select v-model="form.privacyMode">
              <option value="local_only">local_only</option>
              <option value="hybrid_safe">hybrid_safe</option>
              <option value="cloud_quality">cloud_quality</option>
            </select>
          </label>
        </div>
        <div class="action-row">
          <button class="primary-btn" :disabled="submitting || !canCreate" @click="createProject">
            {{ submitting ? 'Creating project...' : 'Create Swarmbook Project' }}
          </button>
          <button class="ghost-btn" @click="resetSession">Clear Session</button>
        </div>
      </div>

      <div class="card">
        <h2>Runtime Health</h2>
        <ul class="health-list">
          <li>
            <strong>Router</strong>
            <span>{{ healthSummary.router }}</span>
          </li>
          <li>
            <strong>Neo4j</strong>
            <span>{{ healthSummary.neo4j }}</span>
          </li>
          <li>
            <strong>Ollama</strong>
            <span>{{ healthSummary.ollama }}</span>
          </li>
        </ul>
        <p class="muted">
          Missing Gemini or NVIDIA keys should not block local-first use. The backend reports provider health instead of crashing.
        </p>
      </div>
    </section>

    <section v-if="session.projectId" class="card">
      <h2>Current Session</h2>
      <div class="session-grid">
        <div>
          <span class="label">Project ID</span>
          <p>{{ session.projectId }}</p>
        </div>
        <div>
          <span class="label">Title</span>
          <p>{{ session.metadata.title || session.project?.title || 'Not set yet' }}</p>
        </div>
        <div>
          <span class="label">Privacy</span>
          <p>{{ session.metadata.privacyMode }}</p>
        </div>
      </div>
      <div class="action-row">
        <button class="primary-btn" @click="router.push({ name: 'SwarmbookUpload', params: { projectId: session.projectId } })">
          Continue To Manuscript Input
        </button>
      </div>
    </section>
  </SwarmbookLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import SwarmbookLayout from '../../components/swarmbook/SwarmbookLayout.vue'
import { createBookSimProject, getBookSimHealth } from '../../api/bookSim'
import {
  clearSwarmbookSession,
  getSwarmbookSession,
  updateSwarmbookSession,
} from '../../store/swarmbookSession'

const router = useRouter()
const session = ref(getSwarmbookSession())
const form = reactive({
  projectName: session.value.metadata.projectName,
  title: session.value.metadata.title,
  authorName: session.value.metadata.authorName,
  privacyMode: session.value.metadata.privacyMode || 'local_only',
})
const health = ref(null)
const error = ref('')
const loadingMessage = ref('')
const submitting = ref(false)

const canCreate = computed(() => form.projectName.trim() !== '')

const healthStatus = computed(() => {
  if (!health.value) {
    return 'Checking health'
  }
  return health.value.router?.ok ? 'Backend ready' : 'Backend degraded'
})

const healthTone = computed(() => {
  if (!health.value) {
    return 'loading'
  }
  return health.value.router?.ok ? 'ready' : 'error'
})

const healthSummary = computed(() => {
  const payload = health.value || {}
  return {
    router: payload.router?.ok ? 'Configured' : payload.router?.error || 'Unavailable',
    neo4j: payload.neo4j?.ok ? 'Connected' : payload.neo4j?.error || 'Unavailable',
    ollama: payload.ollama?.ok ? 'Reachable' : payload.ollama?.error || 'Unavailable',
  }
})

async function loadHealth() {
  loadingMessage.value = 'Loading backend health...'
  error.value = ''
  try {
    const response = await getBookSimHealth()
    health.value = response.data
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loadingMessage.value = ''
  }
}

async function createProject() {
  submitting.value = true
  error.value = ''
  try {
    const response = await createBookSimProject({
      project_id: session.value.projectId || undefined,
      name: form.projectName,
      title: form.title,
      author_name: form.authorName,
      privacy_mode: form.privacyMode,
      metadata: {
        project_name: form.projectName,
      },
    })
    session.value = updateSwarmbookSession({
      projectId: response.data.project_id,
      project: response.data,
      metadata: {
        ...session.value.metadata,
        projectName: form.projectName,
        title: form.title,
        authorName: form.authorName,
        privacyMode: form.privacyMode,
      },
    })
    router.push({ name: 'SwarmbookUpload', params: { projectId: response.data.project_id } })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    submitting.value = false
  }
}

function resetSession() {
  clearSwarmbookSession()
  session.value = getSwarmbookSession()
  form.projectName = ''
  form.title = ''
  form.authorName = ''
  form.privacyMode = 'local_only'
  error.value = ''
}

onMounted(() => {
  loadHealth()
})
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}

.card {
  border: 1px solid #e5e5e5;
  padding: 20px;
  background: #ffffff;
}

.card h2 {
  font-size: 1.2rem;
  margin-bottom: 16px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

label span,
.label {
  display: block;
  font-size: 0.8rem;
  color: #666666;
  margin-bottom: 6px;
  font-family: 'JetBrains Mono', monospace;
}

input,
select {
  width: 100%;
  padding: 12px;
  border: 1px solid #d9d9d9;
  font: inherit;
}

.action-row {
  display: flex;
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
  color: #000000;
}

.health-list {
  list-style: none;
  display: grid;
  gap: 12px;
}

.health-list li {
  border-bottom: 1px solid #efefef;
  padding-bottom: 12px;
}

.health-list strong {
  display: block;
  margin-bottom: 4px;
}

.muted {
  color: #666666;
  line-height: 1.6;
  margin-top: 16px;
}

.session-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 900px) {
  .grid,
  .field-grid,
  .session-grid {
    grid-template-columns: 1fr;
  }
}
</style>
