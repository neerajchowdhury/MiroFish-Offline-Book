<template>
  <SwarmbookAppShell
    active-route="SwarmbookHome"
    :project-id="session.projectId"
    title="Swarmbook Studio"
    subtitle="Predict reader reactions and identify manuscript pacing or style friction points before publication."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <!-- Hero Section -->
    <header class="dashboard-hero">
      <div class="hero-content">
        <h1>Predict reader reactions before you publish.</h1>
        <p class="hero-subtext">
          Upload your manuscript draft, configure a cohort of simulated reader personas, run platform reaction stress tests, and review detailed predicted scorecard spreads.
        </p>
        <div class="hero-ctas">
          <button class="primary-btn lg" @click="startNewSimulationWizard" @keydown.enter="startNewSimulationWizard">
            🚀 Start New Simulation
          </button>
          <button class="ghost-btn lg" @click="toggleOpenProjectForm" @keydown.enter="toggleOpenProjectForm">
            📂 Open Existing Project
          </button>
        </div>

        <!-- Inline Open Project Input Form -->
        <transition name="fade">
          <div v-if="isOpenProjectFormOpen" class="open-project-bar">
            <input
              v-model="openProjectIdInput"
              type="text"
              placeholder="Enter Project ID (e.g. proj_4f9a3c...)"
              @keydown.enter="openProjectById(openProjectIdInput)"
            />
            <button class="primary-btn" :disabled="!openProjectIdInput.trim()" @click="openProjectById(openProjectIdInput)">
              Open
            </button>
          </div>
        </transition>
      </div>
    </header>

    <!-- Local Trust Strip -->
    <section class="trust-strip">
      <div class="trust-item">
        <span class="icon">🛡️</span>
        <div class="text">
          <h3>Local-First Ingest</h3>
          <p>Runs directly on your workstation hardware target.</p>
        </div>
      </div>
      <div class="trust-item">
        <span class="icon">🔒</span>
        <div class="text">
          <h3>Private Mode Enforced</h3>
          <p>Data stays local under the system-wide local_only guard.</p>
        </div>
      </div>
      <div class="trust-item">
        <span class="icon">👥</span>
        <div class="text">
          <h3>Zero Social Scraping</h3>
          <p>Structured reader cohorts are fully simulated.</p>
        </div>
      </div>
      <div class="trust-item">
        <span class="icon">📝</span>
        <div class="text">
          <h3>Evidence-Grounded</h3>
          <p>Reactions reference specific chapters and claims.</p>
        </div>
      </div>
    </section>

    <!-- Main Dashboard Body Grid -->
    <div class="dashboard-grid">
      <!-- Left Main Section: Recent Projects & Quick Actions -->
      <main class="dashboard-main-col">
        <!-- Recent Projects Section -->
        <section class="dashboard-card">
          <header class="card-header-row">
            <h2>Recent Active Manuscripts</h2>
            <button class="text-link-btn" v-if="recentProjects.length" @click="clearRecentProjects">Clear History</button>
          </header>

          <div v-if="recentProjects.length === 0" class="empty-projects-state">
            <div class="empty-icon">📁</div>
            <h3>No manuscripts found in local history</h3>
            <p>Fill out the project setup form on the right to start your first reader simulation.</p>
          </div>

          <div v-else class="projects-list-grid">
            <article v-for="project in recentProjects" :key="project.project_id" class="project-card-item">
              <div class="card-meta">
                <span class="project-id-badge">{{ truncateId(project.project_id) }}</span>
                <span class="date">{{ formatDate(project.created_at) }}</span>
              </div>
              <h3 class="project-title">{{ project.title || project.name }}</h3>
              <p class="project-author">by {{ project.author_name || 'Unknown Author' }}</p>
              
              <div class="card-footer-tags">
                <span class="tag-badge" :class="project.privacy_mode">{{ project.privacy_mode }}</span>
                <span class="tag-badge profile">{{ project.profile_name }}</span>
              </div>

              <div class="card-actions">
                <button class="ghost-btn sm" @click="resumeProject(project)">
                  Open Simulation
                </button>
              </div>
            </article>
          </div>
        </section>

        <!-- Quick Ingest Actions Section -->
        <section class="dashboard-card">
          <h2>Quick Actions</h2>
          <div class="quick-actions-row">
            <button class="action-card" @click="openQuickBlurbModal">
              <span class="action-icon">✍️</span>
              <div class="action-desc">
                <h4>Test a Blurb</h4>
                <p>Run a quick stress-test with only a marketing blurb context.</p>
              </div>
            </button>
            <button class="action-card" @click="triggerUploadShortcut">
              <span class="action-icon">📂</span>
              <div class="action-desc">
                <h4>Upload Manuscript</h4>
                <p>Upload a plain text or Markdown draft file directly.</p>
              </div>
            </button>
            <button class="action-card" @click="triggerCompareShortcut">
              <span class="action-icon">⚖️</span>
              <div class="action-desc">
                <h4>Compare Drafts</h4>
                <p>Compare two versions side-by-side.</p>
              </div>
            </button>
          </div>
        </section>
      </main>

      <!-- Right Column: Project Setup Form & Status -->
      <aside class="dashboard-side-col">
        <!-- New Project Form Card -->
        <section class="dashboard-card form-card" ref="newProjectForm">
          <h2>New Simulation Setup</h2>
          <div class="form-grid">
            <label class="field-label">
              <span>Project reference name</span>
              <input v-model="form.projectName" type="text" placeholder="e.g. spring_thriller_draft" />
            </label>
            <label class="field-label">
              <span>Book title</span>
              <input v-model="form.title" type="text" placeholder="e.g. The Quiet Passenger" />
            </label>
            <label class="field-label">
              <span>Author name</span>
              <input v-model="form.authorName" type="text" placeholder="e.g. Jane Doe" />
            </label>
            <label class="field-label">
              <span>Hardware resource profile</span>
              <select v-model="form.localProfile" @change="applyProfileDefaults(form.localProfile)">
                <option v-for="profile in profileOptions" :key="profile.profile_name" :value="profile.profile_name">
                  {{ profile.profile_name }}
                </option>
              </select>
            </label>
            <label class="field-label">
              <span>Privacy mode</span>
              <select v-model="form.privacyMode">
                <option value="local_only">local_only (strictly offline)</option>
                <option value="hybrid_safe">hybrid_safe (embeddings cloud)</option>
                <option value="cloud_quality">cloud_quality (advanced models)</option>
              </select>
            </label>
          </div>

          <div v-if="selectedProfileWarnings.length" class="warning-block">
            <h3>Profile resource warnings:</h3>
            <ul>
              <li v-for="warning in selectedProfileWarnings" :key="warning.code + warning.message">
                {{ warning.message }}
              </li>
            </ul>
          </div>

          <div class="action-row">
            <button class="primary-btn block-btn" :disabled="submitting || !canCreate" @click="createProject">
              {{ submitting ? 'Creating Project...' : 'Setup Simulation Project' }}
            </button>
            <button class="ghost-btn block-btn" @click="resetSession">Clear Form</button>
          </div>
        </section>

        <!-- System Readiness Panel Card -->
        <section class="dashboard-card">
          <h2>System Readiness</h2>
          <ul class="readiness-list">
            <li>
              <div class="readiness-item">
                <span class="name">Ollama (Local LLM)</span>
                <span class="status-badge" :class="healthStatusTone(healthSummary.ollama)">
                  {{ healthSummary.ollama }}
                </span>
              </div>
            </li>
            <li>
              <div class="readiness-item">
                <span class="name">Neo4j (Knowledge Graph)</span>
                <span class="status-badge" :class="healthStatusTone(healthSummary.neo4j)">
                  {{ healthSummary.neo4j }}
                </span>
              </div>
            </li>
            <li>
              <div class="readiness-item">
                <span class="name">Gemini (Optional Cloud)</span>
                <span class="status-badge" :class="healthStatusTone(healthSummary.gemini)">
                  {{ healthSummary.gemini }}
                </span>
              </div>
            </li>
            <li>
              <div class="readiness-item">
                <span class="name">NVIDIA (Optional Cloud)</span>
                <span class="status-badge" :class="healthStatusTone(healthSummary.nvidia)">
                  {{ healthSummary.nvidia }}
                </span>
              </div>
            </li>
          </ul>
          <p class="muted-note">
            If keys are missing for Gemini or NVIDIA, simulations will fall back to Ollama in local_only/hybrid_safe mode.
          </p>
        </section>
      </aside>
    </div>

    <!-- Quick Blurb Test Modal -->
    <div v-if="isBlurbModalOpen" class="blurb-modal" role="dialog" aria-modal="true" aria-labelledby="blurb-title">
      <div class="modal-backdrop" @click="closeQuickBlurbModal"></div>
      <div class="modal-card">
        <header class="modal-header">
          <h2 id="blurb-title">Quick Blurb Stress Test</h2>
          <button class="close-btn" @click="closeQuickBlurbModal">&times;</button>
        </header>
        <div class="modal-body">
          <p class="hint-text">
            Test how simulated cohorts respond to your blurb without uploading the full manuscript draft.
          </p>
          <label class="field-label">
            <span>Book Title</span>
            <input v-model="blurbForm.title" type="text" placeholder="e.g. My Speculative Thriller" />
          </label>
          <label class="field-label">
            <span>Author name</span>
            <input v-model="blurbForm.author" type="text" placeholder="Jane Doe" />
          </label>
          <label class="field-label">
            <span>Paste Blurb Text</span>
            <textarea
              v-model="blurbForm.blurb"
              rows="6"
              placeholder="Paste your book blurb description here..."
            ></textarea>
          </label>
        </div>
        <footer class="modal-footer">
          <button class="ghost-btn" @click="closeQuickBlurbModal">Cancel</button>
          <button
            class="primary-btn"
            :disabled="!blurbForm.title.trim() || !blurbForm.blurb.trim() || submitting"
            @click="submitQuickBlurb"
          >
            {{ submitting ? 'Testing...' : 'Initialize Test' }}
          </button>
        </footer>
      </div>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { createBookSimProject, getBookSimHealth, createEvidencePack, getBookSimReport } from '../../api/bookSim'
import {
  clearSwarmbookSession,
  getSwarmbookSession,
  updateSwarmbookSession,
} from '../../store/swarmbookSession'

const RECENT_PROJECTS_KEY = 'mirofish_swarmbook_projects'

const router = useRouter()
const session = ref(getSwarmbookSession())
const form = reactive({
  projectName: session.value.metadata.projectName || '',
  title: session.value.metadata.title || '',
  authorName: session.value.metadata.authorName || '',
  localProfile: session.value.metadata.localProfile || session.value.simulationConfig.profileName || 'hybrid_safe_default',
  privacyMode: session.value.metadata.privacyMode || 'hybrid_safe',
})

const health = ref(null)
const error = ref('')
const loadingMessage = ref('')
const submitting = ref(false)

const isOpenProjectFormOpen = ref(false)
const openProjectIdInput = ref('')
const newProjectForm = ref(null)

const recentProjects = ref([])

// Quick Blurb setup modal
const isBlurbModalOpen = ref(false)
const blurbForm = reactive({
  title: '',
  author: '',
  blurb: '',
})

const canCreate = computed(() => form.projectName.trim() !== '' && form.title.trim() !== '')

const healthSummary = computed(() => {
  const payload = health.value || {}
  return {
    router: payload.router?.ok ? 'Configured' : 'Offline',
    neo4j: payload.neo4j?.ok ? 'Connected' : 'Offline',
    ollama: payload.ollama?.ok ? 'Reachable' : 'Offline',
    gemini: payload.providers?.gemini_long_context?.ok ? 'Configured' : 'Optional',
    nvidia: payload.providers?.nvidia_nim?.ok ? 'Configured' : 'Optional',
  }
})

function healthStatusTone(statusVal) {
  if (['Connected', 'Reachable', 'Configured'].includes(statusVal)) return 'ok'
  if (statusVal === 'Checking...') return 'warn'
  return 'offline'
}

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
  try {
    const response = await getBookSimHealth()
    health.value = response.data
    const defaultProfile = response.data?.profiles?.default_profile
    if (!form.localProfile && defaultProfile) {
      form.localProfile = defaultProfile
    }
    applyProfileDefaults(form.localProfile || defaultProfile || 'hybrid_safe_default')
  } catch (requestError) {
    error.value = 'Failed to load backend health connection status.'
  }
}

// Local history registry helpers
function loadRecentProjects() {
  try {
    const raw = localStorage.getItem(RECENT_PROJECTS_KEY)
    recentProjects.value = raw ? JSON.parse(raw) : []
  } catch (err) {
    console.warn('Failed to load recent Swarmbook projects:', err)
  }
}

function addRecentProjectRecord(proj) {
  try {
    const list = [...recentProjects.value]
    const index = list.findIndex(item => item.project_id === proj.project_id)
    if (index !== -1) {
      list.splice(index, 1) // Remove old record to bubble up to top
    }
    list.unshift(proj)
    const trimmed = list.slice(0, 8) // Hold up to 8 projects
    localStorage.setItem(RECENT_PROJECTS_KEY, JSON.stringify(trimmed))
    recentProjects.value = trimmed
  } catch (err) {
    console.warn('Failed to save project record to history:', err)
  }
}

function clearRecentProjects() {
  localStorage.removeItem(RECENT_PROJECTS_KEY)
  recentProjects.value = []
}

function truncateId(val) {
  if (!val) return ''
  return val.replace('proj_', '').slice(0, 8).toUpperCase()
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function scrollToNewProject() {
  newProjectForm.value?.scrollIntoView({ behavior: 'smooth' })
}

function startNewSimulationWizard() {
  clearSwarmbookSession()
  session.value = getSwarmbookSession()
  router.push({ name: 'NewSimulationWizard' })
}

function toggleOpenProjectForm() {
  isOpenProjectFormOpen.value = !isOpenProjectFormOpen.value
}

async function openProjectById(projectId) {
  if (!projectId.trim()) return
  loadingMessage.value = `Opening project ${projectId}...`
  error.value = ''
  try {
    const response = await getBookSimReport(projectId)
    // Project exists and has report
    session.value = updateSwarmbookSession({
      projectId: projectId,
      report: response.data,
    })
    router.push({ name: 'SwarmbookReport', params: { projectId: projectId } })
  } catch (err) {
    // Project exists but report is not synthesized, or invalid ID. Set ID anyway and try Ingest.
    session.value = updateSwarmbookSession({
      projectId: projectId,
    })
    router.push({ name: 'SwarmbookUpload', params: { projectId: projectId } })
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
    
    const projectRecord = {
      project_id: response.data.project_id,
      name: form.projectName,
      title: form.title,
      author_name: form.authorName,
      profile_name: form.localProfile,
      privacy_mode: form.privacyMode,
      created_at: new Date().toISOString(),
    }

    addRecentProjectRecord(projectRecord)

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

function resumeProject(project) {
  session.value = updateSwarmbookSession({
    projectId: project.project_id,
    metadata: {
      projectName: project.name,
      title: project.title,
      authorName: project.author_name,
      localProfile: project.profile_name,
      privacyMode: project.privacy_mode,
    },
  })
  router.push({ name: 'SwarmbookUpload', params: { projectId: project.project_id } })
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

// Quick action triggers
function openQuickBlurbModal() {
  blurbForm.title = ''
  blurbForm.author = ''
  blurbForm.blurb = ''
  isBlurbModalOpen.value = true
}

function closeQuickBlurbModal() {
  isBlurbModalOpen.value = false
}

async function submitQuickBlurb() {
  submitting.value = true
  error.value = ''
  try {
    const projResponse = await createBookSimProject({
      name: `Blurb Test: ${blurbForm.title}`,
      title: blurbForm.title,
      author_name: blurbForm.author,
      profile_name: 'local_tiny',
      privacy_mode: 'local_only',
      metadata: {
        blurb: blurbForm.blurb,
        book_type: 'fiction',
        local_profile: 'local_tiny',
      },
    })

    const projectRecord = {
      project_id: projResponse.data.project_id,
      name: `Blurb Test: ${blurbForm.title}`,
      title: blurbForm.title,
      author_name: blurbForm.author,
      profile_name: 'local_tiny',
      privacy_mode: 'local_only',
      created_at: new Date().toISOString(),
    }
    addRecentProjectRecord(projectRecord)

    const evidenceResponse = await createEvidencePack({
      project_id: projResponse.data.project_id,
      title: blurbForm.title,
      author_name: blurbForm.author,
      text: `Quick Blurb testing context. Premise:\n\n${blurbForm.blurb}`,
      filename: 'blurb.txt',
      metadata: {
        blurb: blurbForm.blurb,
        book_type: 'fiction',
      },
    })

    session.value = updateSwarmbookSession({
      projectId: projResponse.data.project_id,
      project: projResponse.data,
      manuscript: {
        text: `Quick Blurb testing context. Premise:\n\n${blurbForm.blurb}`,
        filename: 'blurb.txt',
      },
      metadata: {
        projectName: `Blurb Test: ${blurbForm.title}`,
        title: blurbForm.title,
        authorName: blurbForm.author,
        localProfile: 'local_tiny',
        privacyMode: 'local_only',
        blurb: blurbForm.blurb,
        bookType: 'fiction',
      },
      evidencePack: evidenceResponse.data.evidence_pack,
    })

    isBlurbModalOpen.value = false
    router.push({ name: 'SwarmbookEvidence', params: { projectId: projResponse.data.project_id } })
  } catch (err) {
    error.value = err.message
  } finally {
    submitting.value = false
  }
}

function triggerUploadShortcut() {
  if (session.value.projectId) {
    router.push({ name: 'NewSimulationWizard', params: { projectId: session.value.projectId } })
  } else {
    router.push({ name: 'NewSimulationWizard' })
  }
}

function triggerCompareShortcut() {
  if (session.value.projectId) {
    router.push({ name: 'SwarmbookCompare', params: { projectId: session.value.projectId } })
  } else {
    scrollToNewProject()
  }
}

onMounted(() => {
  loadHealth()
  loadRecentProjects()
})
</script>

<style scoped>
/* Scoped premium dashboard layout css styles */

.dashboard-hero {
  background: #0f172a;
  color: #ffffff;
  padding: 40px;
  border-radius: 12px;
  margin-bottom: 24px;
  border: 1px solid #1e293b;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.15);
}

.hero-content h1 {
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 12px 0;
  letter-spacing: -0.75px;
}

.hero-subtext {
  color: #94a3b8;
  font-size: 1.05rem;
  line-height: 1.6;
  max-width: 780px;
  margin: 0 0 24px 0;
}

.hero-ctas {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.primary-btn.lg,
.ghost-btn.lg {
  padding: 14px 24px;
  font-size: 0.95rem;
}

.ghost-btn.lg {
  border-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.ghost-btn.lg:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: #ffffff;
}

.open-project-bar {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  max-width: 500px;
  background: rgba(255, 255, 255, 0.05);
  padding: 8px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.open-project-bar input {
  flex: 1;
  background: transparent;
  border: none;
  color: #ffffff;
  padding: 8px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  outline: none;
}

/* Trust Strip */
.trust-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

.trust-item {
  display: flex;
  gap: 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 16px;
  border-radius: 8px;
}

.trust-item .icon {
  font-size: 1.5rem;
  line-height: 1;
}

.trust-item h3 {
  font-size: 0.85rem;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.trust-item p {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

/* Main Grid Layout */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
}

.dashboard-main-col,
.dashboard-side-col {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.dashboard-card h2 {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 18px 0;
  color: #0f172a;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.card-header-row h2 {
  margin: 0;
}

.text-link-btn {
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.text-link-btn:hover {
  color: #ff4500;
}

/* Empty Project State */
.empty-projects-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 14px;
}

.empty-projects-state h3 {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0 0 6px 0;
}

.empty-projects-state p {
  font-size: 0.8rem;
  color: #64748b;
  max-width: 320px;
  margin: 0 auto;
}

/* Projects grid list */
.projects-list-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.project-card-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.project-id-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  background: #e2e8f0;
  color: #334155;
  padding: 2px 6px;
  border-radius: 4px;
}

.card-meta .date {
  font-size: 0.72rem;
  color: #94a3b8;
}

.project-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.project-author {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0 0 12px 0;
}

.card-footer-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.tag-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.tag-badge.local_only { background: #d1fae5; color: #065f46; }
.tag-badge.hybrid_safe { background: #fef3c7; color: #92400e; }
.tag-badge.cloud_quality { background: #dbeafe; color: #1e40af; }
.tag-badge.profile { background: #f1f5f9; color: #475569; }

.card-actions {
  margin-top: auto;
}

.ghost-btn.sm {
  width: 100%;
  padding: 8px 12px;
  font-size: 0.78rem;
}

/* Quick Actions Cards */
.quick-actions-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.action-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.action-card:hover {
  background: #fff5ef;
  border-color: #ff4500;
}

.action-card:focus-visible {
  outline: 2px solid #ff4500;
}

.action-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.action-desc h4 {
  font-size: 0.85rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #0f172a;
}

.action-desc p {
  font-size: 0.72rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

/* Form Design Details */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label span {
  font-size: 0.8rem;
  font-weight: 600;
  color: #475569;
}

input,
select,
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
  color: #0f172a;
  font-family: inherit;
  font-size: 0.88rem;
  outline: none;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #ff4500;
  box-shadow: 0 0 0 3px rgba(255, 69, 0, 0.1);
}

.warning-block {
  margin-top: 14px;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  padding: 12px;
  border-radius: 6px;
}

.warning-block h3 {
  font-size: 0.78rem;
  color: #92400e;
  font-weight: 700;
  margin: 0 0 6px 0;
}

.warning-block ul {
  margin: 0;
  padding-left: 16px;
  font-size: 0.75rem;
  color: #b45309;
}

.action-row {
  display: flex;
  gap: 10px;
  margin-top: 18px;
}

.block-btn {
  flex: 1;
}

/* Readiness List */
.readiness-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.readiness-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.82rem;
}

.readiness-item .name {
  color: #475569;
  font-weight: 500;
}

.status-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.status-badge.ok { background: #d1fae5; color: #065f46; }
.status-badge.warn { background: #fef3c7; color: #92400e; }
.status-badge.offline { background: #fef2f2; color: #991b1b; }

.muted-note {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 16px;
  line-height: 1.4;
}

/* Modal style */
.blurb-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.blurb-modal .modal-card {
  max-width: 500px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

/* Responsive collapse */
@media (max-width: 1100px) {
  .trust-strip {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .projects-list-grid {
    grid-template-columns: 1fr;
  }
  .quick-actions-row {
    grid-template-columns: 1fr;
  }
  .trust-strip {
    grid-template-columns: 1fr;
  }
}
</style>
