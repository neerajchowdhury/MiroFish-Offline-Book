<template>
  <SwarmbookLayout
    active-route="SwarmbookReport"
    :project-id="session.projectId"
    title="Report Dashboard"
    subtitle="Review the latest Swarmbook report, synthetic score spread, representative posts, and revision priorities for the current project."
    :status-text="loading ? 'Loading report' : 'Report ready'"
    :status-tone="loading ? 'loading' : 'ready'"
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <section v-if="report" class="stat-grid">
      <article class="stat-card">
        <span class="stat-label">Rating spread</span>
        <strong>{{ formatNumber(report.scorecard?.rating_distribution?.predicted_mean_rating) }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">DNF risk</span>
        <strong>{{ formatNumber(report.scorecard?.dnf?.dnf_risk) }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Controversy</span>
        <strong>{{ formatNumber(report.scorecard?.controversy?.controversy_risk) }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Viral potential</span>
        <strong>{{ viralMean }}</strong>
      </article>
    </section>

    <section v-if="report" class="grid">
      <article class="card">
        <h2>Summary</h2>
        <p>{{ report.summary || 'No summary available.' }}</p>

        <h3>Revision Priorities</h3>
        <ul class="list">
          <li v-for="item in report.revision_priorities || []" :key="item">{{ item }}</li>
        </ul>
      </article>

      <article class="card">
        <h2>Platform Posts</h2>
        <ul v-if="platformPosts.length" class="list">
          <li v-for="post in platformPosts" :key="post.post_id">
            <strong>{{ post.platform }} · {{ personaNames[post.persona_id] || post.persona_id }}</strong>
            <p>{{ post.body || 'No post body returned.' }}</p>
          </li>
        </ul>
        <p v-else>No platform posts are stored in the current frontend session.</p>
      </article>
    </section>

    <section v-if="report" class="grid">
      <article class="card">
        <h2>Risk + Strength Signals</h2>
        <p><strong>Top risks:</strong> {{ joinList(report.top_risks) }}</p>
        <p><strong>Top strengths:</strong> {{ joinList(report.top_strengths) }}</p>
        <p><strong>Uncertainty notes:</strong> {{ joinList(report.uncertainty_notes) }}</p>
      </article>

      <article class="card">
        <h2>Audience Response</h2>
        <p><strong>Personas:</strong> {{ report.audience_response?.personas_count ?? 'N/A' }}</p>
        <p><strong>Posts:</strong> {{ report.audience_response?.posts_count ?? 'N/A' }}</p>
        <p><strong>Recommendation mean:</strong> {{ formatNumber(report.audience_response?.recommendation_mean) }}</p>
        <p><strong>Top platforms:</strong> {{ joinList(report.audience_response?.top_platforms) }}</p>
      </article>
    </section>

    <section v-if="report" class="action-row">
      <button class="ghost-btn" @click="router.push({ name: 'SwarmbookPersonas', params: { projectId: session.projectId } })">
        Persona Interrogation
      </button>
      <button class="primary-btn" @click="router.push({ name: 'SwarmbookCompare', params: { projectId: session.projectId } })">
        Draft Comparison
      </button>
    </section>

    <section v-if="!report && !loading" class="card">
      <p>No Swarmbook report is available yet for this session.</p>
    </section>
  </SwarmbookLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookLayout from '../../components/swarmbook/SwarmbookLayout.vue'
import { getBookSimReport } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const report = ref(session.value.report)
const loading = ref(false)
const loadingMessage = ref('')
const error = ref('')

const platformPosts = computed(() => session.value.simulationRun?.platform_posts || [])
const personaNames = computed(() => {
  const result = {}
  for (const persona of session.value.simulationRun?.reader_personas || []) {
    result[persona.persona_id] = persona.display_name
  }
  return result
})

const viralMean = computed(() => {
  const scores = report.value?.scorecard?.viral?.platform_scores
  if (!scores) {
    return 'N/A'
  }
  const values = Object.values(scores).map((value) => Number(value)).filter((value) => !Number.isNaN(value))
  if (!values.length) {
    return 'N/A'
  }
  return formatNumber(values.reduce((sum, value) => sum + value, 0) / values.length)
})

async function ensureReport() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId) {
    router.replace({ name: 'SwarmbookHome' })
    return
  }

  if (report.value) {
    return
  }

  loading.value = true
  loadingMessage.value = 'Loading latest report from backend...'
  error.value = ''
  try {
    const response = await getBookSimReport(session.value.projectId)
    report.value = response.data
    session.value = updateSwarmbookSession({ report: response.data })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
    loadingMessage.value = ''
  }
}

function formatNumber(value) {
  const numeric = Number(value)
  return Number.isNaN(numeric) ? 'N/A' : numeric.toFixed(2)
}

function joinList(value) {
  return value && value.length ? value.join(', ') : 'N/A'
}

onMounted(() => {
  ensureReport()
})
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.stat-card,
.card {
  border: 1px solid #e5e5e5;
  background: #ffffff;
  padding: 18px;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #666666;
  margin-bottom: 8px;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
}

.stat-card strong {
  font-size: 1.6rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 18px;
}

.card h2,
.card h3 {
  margin-bottom: 12px;
}

.card p {
  line-height: 1.6;
  margin-bottom: 10px;
}

.list {
  list-style: none;
  display: grid;
  gap: 12px;
}

.list li {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
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
  .stat-grid,
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
