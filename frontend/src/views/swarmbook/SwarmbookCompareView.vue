<template>
  <SwarmbookLayout
    active-route="SwarmbookCompare"
    :project-id="session.projectId"
    title="Draft Comparison"
    subtitle="Compare the current Swarmbook project against another project using the backend comparison export without altering either draft."
    :status-text="loading ? 'Comparing drafts' : 'Comparison ready'"
    :status-tone="loading ? 'loading' : 'ready'"
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <section class="grid">
      <article class="card">
        <h2>Compare Drafts</h2>
        <div class="field-grid">
          <label>
            <span>Base project ID</span>
            <input v-model="form.baseProjectId" type="text" />
          </label>
          <label>
            <span>Compare project ID</span>
            <input v-model="form.compareProjectId" type="text" placeholder="Second project id" />
          </label>
          <label>
            <span>Simulation seed</span>
            <input v-model.number="form.simulationSeed" type="number" min="0" />
          </label>
        </div>
        <div class="action-row">
          <button class="ghost-btn" @click="router.push({ name: 'SwarmbookReport', params: { projectId: session.projectId } })">
            Back To Report
          </button>
          <button class="primary-btn" :disabled="loading || !canCompare" @click="runComparison">
            {{ loading ? 'Comparing...' : 'Run Comparison' }}
          </button>
        </div>
      </article>

      <article class="card" v-if="comparison">
        <h2>Comparison Summary</h2>
        <p>{{ comparison.report.summary }}</p>
        <p><strong>What improved:</strong> {{ joinList(comparison.report.what_improved) }}</p>
        <p><strong>What got worse:</strong> {{ joinList(comparison.report.what_got_worse) }}</p>
        <p><strong>Still blocks publishing:</strong> {{ joinList(comparison.report.still_blocking) }}</p>
      </article>
    </section>

    <section v-if="comparison" class="card markdown-card">
      <h2>Markdown Export</h2>
      <pre>{{ comparison.markdown }}</pre>
    </section>
  </SwarmbookLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookLayout from '../../components/swarmbook/SwarmbookLayout.vue'
import { compareBookDrafts } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const form = reactive({
  baseProjectId: session.value.projectId || '',
  compareProjectId: '',
  simulationSeed: session.value.simulationConfig.simulationSeed ?? 17,
})
const loading = ref(false)
const loadingMessage = ref('')
const error = ref('')
const comparison = computed(() => session.value.comparison)

const canCompare = computed(() => Boolean(form.baseProjectId.trim() && form.compareProjectId.trim()))

function ensureSession() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

async function runComparison() {
  loading.value = true
  loadingMessage.value = 'Comparing draft artifacts...'
  error.value = ''
  try {
    const response = await compareBookDrafts({
      project_id: form.baseProjectId,
      base_project_id: form.baseProjectId,
      compare_project_id: form.compareProjectId,
      simulation_seed: form.simulationSeed,
    })
    session.value = updateSwarmbookSession({
      comparison: response.data,
    })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
    loadingMessage.value = ''
  }
}

function joinList(value) {
  return value && value.length ? value.join(', ') : 'N/A'
}

onMounted(() => {
  ensureSession()
})
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 18px;
  margin-bottom: 18px;
}

.card {
  border: 1px solid #e5e5e5;
  padding: 20px;
  background: #ffffff;
}

.card h2 {
  margin-bottom: 14px;
}

.field-grid {
  display: grid;
  gap: 14px;
}

label span {
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

.markdown-card pre {
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', monospace;
  background: #fafafa;
  border: 1px solid #eeeeee;
  padding: 14px;
  overflow-x: auto;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
