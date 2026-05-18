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
            <span>Number of personas</span>
            <input v-model.number="form.personaCount" type="number" min="2" max="48" />
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
import { createBookSimProject, runBookSimulation } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const form = reactive({
  personaCount: session.value.simulationConfig.personaCount || 12,
  platforms: [...(session.value.simulationConfig.platforms || ['goodreads', 'reddit', 'booktok'])],
  privacyMode: session.value.simulationConfig.privacyMode || session.value.metadata.privacyMode || 'local_only',
  simulationSeed: session.value.simulationConfig.simulationSeed ?? 17,
})
const error = ref('')
const loadingMessage = ref('')
const running = ref(false)

const platformOptions = ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x']
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
      privacy_mode: form.privacyMode,
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

    const response = await runBookSimulation({
      project_id: session.value.projectId,
      evidence_pack_id: session.value.evidencePack.pack_id,
      simulation_seed: form.simulationSeed,
      persona_overrides: {
        cohort_size: form.personaCount,
        force_platforms: form.platforms,
      },
    })

    session.value = updateSwarmbookSession({
      simulationConfig: {
        personaCount: form.personaCount,
        platforms: [...form.platforms],
        privacyMode: form.privacyMode,
        simulationSeed: form.simulationSeed,
      },
      metadata: {
        privacyMode: form.privacyMode,
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
