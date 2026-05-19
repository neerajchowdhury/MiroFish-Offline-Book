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
            <span>Local profile</span>
            <select v-model="form.localProfile" @change="applyProfileDefaults(form.localProfile)">
              <option v-for="profile in profileOptions" :key="profile.profile_name" :value="profile.profile_name">
                {{ profile.profile_name }}
              </option>
            </select>
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
        <div v-if="selectedProfileWarnings.length" class="warning-block">
          <h3>Profile warnings</h3>
          <ul>
            <li v-for="warning in selectedProfileWarnings" :key="warning.code + warning.message">
              {{ warning.message }}
            </li>
          </ul>
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
  localProfile: session.value.metadata.localProfile || session.value.simulationConfig.profileName || 'hybrid_safe_default',
  privacyMode: session.value.metadata.privacyMode || 'hybrid_safe',
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

const profileOptions = computed(() => {
  const items = health.value?.profiles?.items || []
  if (items.length) {
    return items
  }
  return [
    { profile_name: 'local_tiny', privacy_mode: 'local_only', max_personas: 12, platforms: ['goodreads', 'reddit', 'x'], reaction_rounds: 1, cross_reaction_posts: 4, local_parallel_jobs: 1, computed_warnings: [] },
    { profile_name: 'hybrid_safe_default', privacy_mode: 'hybrid_safe', max_personas: 30, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x'], reaction_rounds: 2, cross_reaction_posts: 8, local_parallel_jobs: 1, computed_warnings: [] },
    { profile_name: 'cloud_quality', privacy_mode: 'cloud_quality', max_personas: 60, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub'], reaction_rounds: 2, cross_reaction_posts: 12, local_parallel_jobs: 1, computed_warnings: [] },
  ]
})

const selectedProfile = computed(() => {
  return profileOptions.value.find((profile) => profile.profile_name === form.localProfile) || profileOptions.value[0] || null
})

const selectedProfileWarnings = computed(() => {
  return selectedProfile.value?.computed_warnings || []
})

function applyProfileDefaults(profileName) {
  const selected = profileOptions.value.find((profile) => profile.profile_name === profileName)
  if (!selected) {
    return
  }
  form.privacyMode = selected.privacy_mode || form.privacyMode
  session.value = updateSwarmbookSession({
    metadata: {
      ...session.value.metadata,
      localProfile: selected.profile_name,
      privacyMode: selected.privacy_mode || form.privacyMode,
    },
    simulationConfig: {
      ...session.value.simulationConfig,
      profileName: selected.profile_name,
      personaCount: selected.max_personas || session.value.simulationConfig.personaCount,
      platforms: selected.platforms?.map((platform) => String(platform).toLowerCase()) || session.value.simulationConfig.platforms,
      privacyMode: selected.privacy_mode || session.value.simulationConfig.privacyMode,
      profileWarnings: selected.computed_warnings || [],
    },
  })
}

async function loadHealth() {
  loadingMessage.value = 'Loading backend health...'
  error.value = ''
  try {
    const response = await getBookSimHealth()
    health.value = response.data
    const defaultProfile = response.data?.profiles?.default_profile
    if (!form.localProfile && defaultProfile) {
      form.localProfile = defaultProfile
    }
    applyProfileDefaults(form.localProfile || defaultProfile || 'hybrid_safe_default')
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
      profile_name: form.localProfile,
      privacy_mode: form.privacyMode,
      metadata: {
        project_name: form.projectName,
        local_profile: form.localProfile,
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
        localProfile: form.localProfile,
        privacyMode: form.privacyMode,
      },
      simulationConfig: {
        ...session.value.simulationConfig,
        profileName: form.localProfile,
        profileWarnings: selectedProfileWarnings.value,
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
  form.localProfile = 'hybrid_safe_default'
  form.privacyMode = 'hybrid_safe'
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

.warning-block {
  margin-top: 14px;
  border: 1px solid #f0d9a8;
  background: #fff9ea;
  padding: 12px;
}

.warning-block h3 {
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.warning-block ul {
  margin: 0;
  padding-left: 18px;
  color: #5e4a1f;
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
