<template>
  <SwarmbookLayout
    active-route="SwarmbookSimulation"
    :project-id="session.projectId"
    title="Simulation Controls"
    subtitle="Configure the reader cohort, platform surface, privacy mode, and deterministic seed before running the additive Swarmbook simulation pipeline."
    :status-text="running ? 'Simulation running' : 'Controls ready'"
    :status-tone="running ? 'loading' : 'ready'"
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <section class="grid">
      <article class="card">
        <h2>Run Settings</h2>
        <div class="field-grid">
          <label>
            <span>Local profile</span>
            <select v-model="form.profileName" @change="applyProfileDefaults(form.profileName)">
              <option v-for="profile in profileOptions" :key="profile.profile_name" :value="profile.profile_name">
                {{ profile.profile_name }}
              </option>
            </select>
          </label>
          <label>
            <span>Number of personas</span>
            <input v-model.number="form.personaCount" type="number" min="2" max="80" />
          </label>
          <label>
            <span>Simulation seed</span>
            <input v-model.number="form.simulationSeed" type="number" min="0" />
          </label>
        </div>

        <div class="stack">
          <span>Platforms to simulate</span>
          <div class="pill-row">
            <button
              v-for="platform in platformOptions"
              :key="platform"
              class="pill"
              :class="{ active: form.platforms.includes(platform) }"
              @click="togglePlatform(platform)"
            >
              {{ platform }}
            </button>
          </div>
        </div>

        <div class="stack">
          <span>Execution mode</span>
          <div class="pill-row">
            <button
              v-for="mode in privacyModes"
              :key="mode"
              class="pill"
              :class="{ active: form.privacyMode === mode }"
              @click="form.privacyMode = mode"
            >
              {{ mode }}
            </button>
          </div>
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
          <button class="ghost-btn" @click="router.push({ name: 'SwarmbookEvidence', params: { projectId: session.projectId } })">
            Back To Evidence
          </button>
          <button class="primary-btn" :disabled="running || !canRun" @click="runSimulation">
            {{ running ? 'Running simulation...' : 'Run Simulation' }}
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Current Inputs</h2>
        <div class="summary-grid">
          <div>
            <span class="label">Project ID</span>
            <p>{{ session.projectId || 'Missing' }}</p>
          </div>
          <div>
            <span class="label">Evidence Pack</span>
            <p>{{ session.evidencePack?.pack_id || 'Missing' }}</p>
          </div>
          <div>
            <span class="label">Book Type</span>
            <p>{{ session.metadata.bookType || 'Unknown' }}</p>
          </div>
          <div>
            <span class="label">Platforms</span>
            <p>{{ form.platforms.join(', ') }}</p>
          </div>
        </div>
      </article>
    </section>
  </SwarmbookLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookLayout from '../../components/swarmbook/SwarmbookLayout.vue'
import { createBookSimProject, getBookSimHealth, runBookSimulation } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const form = reactive({
  profileName: session.value.simulationConfig.profileName || session.value.metadata.localProfile || 'hybrid_safe_default',
  personaCount: session.value.simulationConfig.personaCount || 12,
  platforms: [...(session.value.simulationConfig.platforms || ['goodreads', 'reddit', 'booktok'])],
  privacyMode: session.value.simulationConfig.privacyMode || session.value.metadata.privacyMode || 'hybrid_safe',
  simulationSeed: session.value.simulationConfig.simulationSeed ?? 17,
})
const error = ref('')
const loadingMessage = ref('')
const running = ref(false)
const health = ref(null)

const profileOptions = computed(() => {
  return health.value?.profiles?.items || [
    { profile_name: 'local_tiny', privacy_mode: 'local_only', max_personas: 12, platforms: ['goodreads', 'reddit', 'x'], computed_warnings: [] },
    { profile_name: 'hybrid_safe_default', privacy_mode: 'hybrid_safe', max_personas: 30, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x'], computed_warnings: [] },
    { profile_name: 'cloud_quality', privacy_mode: 'cloud_quality', max_personas: 60, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub'], computed_warnings: [] },
  ]
})

const selectedProfile = computed(() => {
  return profileOptions.value.find((profile) => profile.profile_name === form.profileName) || profileOptions.value[0] || null
})

const selectedProfileWarnings = computed(() => selectedProfile.value?.computed_warnings || [])

const platformOptions = ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub']
const privacyModes = ['local_only', 'hybrid_safe', 'cloud_quality']

const canRun = computed(() => {
  return Boolean(
    session.value.projectId &&
    session.value.evidencePack?.pack_id &&
    form.platforms.length > 0
  )
})

function ensureSession() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId || !session.value.evidencePack?.pack_id) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

function applyProfileDefaults(profileName) {
  const selected = profileOptions.value.find((profile) => profile.profile_name === profileName)
  if (!selected) {
    return
  }
  form.privacyMode = selected.privacy_mode || form.privacyMode
  form.personaCount = selected.max_personas || form.personaCount
  form.platforms = (selected.platforms || []).map((platform) => String(platform).toLowerCase())
  session.value = updateSwarmbookSession({
    metadata: {
      ...session.value.metadata,
      localProfile: selected.profile_name,
      privacyMode: selected.privacy_mode || form.privacyMode,
    },
    simulationConfig: {
      ...session.value.simulationConfig,
      profileName: selected.profile_name,
      personaCount: form.personaCount,
      platforms: [...form.platforms],
      privacyMode: form.privacyMode,
      profileWarnings: selected.computed_warnings || [],
    },
  })
}

async function loadProfiles() {
  try {
    const response = await getBookSimHealth()
    health.value = response.data
    if (!form.profileName && response.data?.profiles?.default_profile) {
      form.profileName = response.data.profiles.default_profile
    }
    applyProfileDefaults(form.profileName || response.data?.profiles?.default_profile || 'hybrid_safe_default')
  } catch (requestError) {
    error.value = requestError.message
  }
}

function togglePlatform(platform) {
  if (form.platforms.includes(platform)) {
    form.platforms = form.platforms.filter((item) => item !== platform)
    return
  }
  form.platforms = [...form.platforms, platform]
}

async function runSimulation() {
  running.value = true
  loadingMessage.value = 'Saving privacy mode and running simulation...'
  error.value = ''
  try {
    const metadata = session.value.metadata
    await createBookSimProject({
      project_id: session.value.projectId,
      name: metadata.projectName || metadata.title,
      title: metadata.title,
      author_name: metadata.authorName,
      profile_name: form.profileName,
      privacy_mode: form.privacyMode,
      metadata: {
        book_type: metadata.bookType,
        genre: metadata.genre,
        target_reader: metadata.targetReader,
        subtitle: metadata.subtitle,
        blurb: metadata.blurb,
        comp_titles: metadata.compTitles,
        cover_brief: metadata.coverBrief,
        local_profile: form.profileName,
      },
    })

    const response = await runBookSimulation({
      project_id: session.value.projectId,
      evidence_pack_id: session.value.evidencePack.pack_id,
      profile_name: form.profileName,
      simulation_seed: form.simulationSeed,
      persona_overrides: {
        persona_count: form.personaCount,
        force_platforms: form.platforms,
      },
    })

    session.value = updateSwarmbookSession({
      simulationConfig: {
        profileName: form.profileName,
        personaCount: form.personaCount,
        platforms: [...form.platforms],
        privacyMode: form.privacyMode,
        simulationSeed: form.simulationSeed,
        profileWarnings: selectedProfileWarnings.value,
      },
      metadata: {
        privacyMode: form.privacyMode,
        localProfile: form.profileName,
      },
      simulationRun: response.data.simulation_run,
      report: response.data.report,
    })

    router.push({ name: 'SwarmbookReport', params: { projectId: session.value.projectId } })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loadingMessage.value = ''
    running.value = false
  }
}

onMounted(() => {
  ensureSession()
  loadProfiles()
})
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 18px;
}

.card {
  border: 1px solid #e5e5e5;
  padding: 20px;
  background: #ffffff;
}

.card h2 {
  margin-bottom: 16px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.stack {
  margin-top: 16px;
}

.stack span,
label span,
.label {
  display: block;
  font-size: 0.8rem;
  color: #666666;
  margin-bottom: 6px;
  font-family: 'JetBrains Mono', monospace;
}

input {
  width: 100%;
  border: 1px solid #d9d9d9;
  padding: 12px;
  font: inherit;
}

select {
  width: 100%;
  border: 1px solid #d9d9d9;
  padding: 12px;
  font: inherit;
  background: #ffffff;
}

.pill-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pill {
  border: 1px solid #d7d7d7;
  background: #ffffff;
  padding: 10px 12px;
  cursor: pointer;
}

.pill.active {
  border-color: #000000;
  background: #fff5ef;
}

.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.warning-block {
  margin-top: 16px;
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

.summary-grid {
  display: grid;
  gap: 16px;
}

@media (max-width: 900px) {
  .grid,
  .field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
