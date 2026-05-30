<template>
  <SwarmbookAppShell
    active-route="SwarmbookHome"
    :project-id="session.projectId"
    eyebrow="SWARMBOOK STUDIO"
    title="Launch Console"
    subtitle="Predict reader reactions and identify manuscript pacing or style friction points before publication."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <!-- Console Actions Bar -->
    <div class="console-actions-bar">
      <div class="cta-row">
        <button class="sb-btn-primary" @click="startNewSimulationWizard" @keydown.enter="startNewSimulationWizard">
          🚀 Start New Test
        </button>
        <button class="sb-btn-ghost" @click="toggleOpenProjectForm" @keydown.enter="toggleOpenProjectForm" :aria-expanded="isOpenProjectFormOpen">
          📂 Open Existing Project <span class="arrow">{{ isOpenProjectFormOpen ? '▲' : '▼' }}</span>
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
            aria-label="Enter Project ID"
          />
          <button class="sb-btn-primary" :disabled="!openProjectIdInput.trim()" @click="openProjectById(openProjectIdInput)">
            Open
          </button>
        </div>
      </transition>
    </div>

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

          <!-- Empty State -->
          <div v-if="recentProjects.length === 0" class="empty-projects-state">
            <div class="empty-icon" aria-hidden="true">📁</div>
            <h3>No manuscripts found in local history</h3>
            <p>Launch a new simulation test to begin stress-testing your manuscript draft.</p>
            <button class="sb-btn-primary sb-mt-4" @click="startNewSimulationWizard">
              Start your first test →
            </button>
          </div>

          <!-- Project List -->
          <div v-else class="projects-list-grid">
            <article v-for="project in recentProjects" :key="project.project_id" class="project-card-item">
              <div class="card-meta">
                <span class="project-id-badge">{{ truncateId(project.project_id) }}</span>
                <span class="date">{{ formatDate(project.created_at) }}</span>
              </div>
              <h3 class="project-title" :title="project.title || project.name">{{ project.title || project.name }}</h3>
              <p class="project-author">by {{ project.author_name || 'Unknown Author' }}</p>
              
              <div class="card-footer-tags">
                <span class="sb-badge" :class="'sb-badge--privacy-' + (project.privacy_mode || 'local_only')">
                  {{ project.privacy_mode }}
                </span>
                <span class="sb-badge sb-badge--info">{{ project.profile_name }}</span>
              </div>

              <div class="card-actions">
                <button class="sb-btn-ghost sm sb-w-full" @click="resumeProject(project)">
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
              <span class="action-icon" aria-hidden="true">✍️</span>
              <div class="action-desc">
                <h4>Test Blurb</h4>
                <p>Run stress-test with only a marketing blurb context.</p>
              </div>
            </button>
            <button class="action-card" @click="triggerUploadShortcut">
              <span class="action-icon" aria-hidden="true">📂</span>
              <div class="action-desc">
                <h4>Upload Manuscript</h4>
                <p>Upload a plain text or Markdown draft file directly.</p>
              </div>
            </button>
            <button class="action-card" @click="triggerCompareShortcut">
              <span class="action-icon" aria-hidden="true">⚖️</span>
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

          <!-- ProfileWarnings - Collapsed/hidden if profile is default -->
          <div v-if="selectedProfileWarnings.length && !isProfileDefault" class="warning-block">
            <h3>Profile resource warnings:</h3>
            <ul>
              <li v-for="warning in selectedProfileWarnings" :key="warning.code + warning.message">
                {{ warning.message }}
              </li>
            </ul>
          </div>

          <div class="action-row">
            <button class="sb-btn-primary block-btn" :disabled="submitting || !canCreate" @click="createProject">
              {{ submitting ? 'Creating...' : 'Setup Project' }}
            </button>
            <button class="sb-btn-ghost block-btn" @click="resetSession">Clear</button>
          </div>
        </section>

        <!-- System Readiness Panel Card (Gemini & NVIDIA only to avoid duplicates) -->
        <section class="dashboard-card status-card">
          <h2>Optional Cloud Providers</h2>
          <ul class="readiness-list">
            <li>
              <div class="readiness-item">
                <span class="name">Gemini (Advanced long-context)</span>
                <span class="sb-badge" :class="healthStatusTone(healthSummary.gemini) === 'ok' ? 'sb-badge--ok' : 'sb-badge--warn'">
                  {{ healthSummary.gemini }}
                </span>
              </div>
            </li>
            <li>
              <div class="readiness-item">
                <span class="name">NVIDIA (Secondary / Fallback)</span>
                <span class="sb-badge" :class="healthStatusTone(healthSummary.nvidia) === 'ok' ? 'sb-badge--ok' : 'sb-badge--warn'">
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

    <!-- Local Trust Strip (Compact at bottom) -->
    <footer class="console-trust-footer">
      <span class="trust-badge">🛡️ Local-First Ingest</span>
      <span class="trust-badge">🔒 Private Mode Enforced</span>
      <span class="trust-badge">👥 Zero Social Scraping</span>
      <span class="trust-badge">📝 Evidence-Grounded</span>
    </footer>

    <!-- Quick Blurb Test Modal -->
    <div v-if="isBlurbModalOpen" class="blurb-modal" role="dialog" aria-modal="true" aria-labelledby="blurb-title">
      <div class="modal-backdrop" @click="closeQuickBlurbModal"></div>
      <div class="modal-card">
        <header class="modal-header">
          <h2 id="blurb-title">Quick Blurb Stress Test</h2>
          <button class="close-btn" @click="closeQuickBlurbModal" aria-label="Close modal">&times;</button>
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
          <button class="sb-btn-ghost" @click="closeQuickBlurbModal">Cancel</button>
          <button
            class="sb-btn-primary"
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

const isProfileDefault = computed(() => {
  const def = health.value?.profiles?.default_profile || 'hybrid_safe_default'
  return form.localProfile === def
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
      author_name: project.author_name,
      localProfile: project.profile_name,
      privacyMode: project.privacy_mode,
    },
  })
  router.push({ name: 'SwarmbookUpload', params: { project_id: project.project_id } })
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
/* Scoped launch console styles */
.console-actions-bar {
  margin-bottom: var(--sb-space-4);
  background: var(--sb-surface-secondary);
  padding: var(--sb-space-3) var(--sb-space-4);
  border-radius: var(--sb-radius-lg);
  border: 1px solid var(--sb-border-color);
}
.cta-row {
  display: flex;
  gap: var(--sb-space-3);
  flex-wrap: wrap;
}
.open-project-bar {
  display: flex;
  gap: var(--sb-space-2);
  margin-top: var(--sb-space-3);
  max-width: 500px;
}
.open-project-bar input {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-sm);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: var(--sb-space-4);
}

.dashboard-main-col,
.dashboard-side-col {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-4);
}

.dashboard-card {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-xl);
  padding: var(--sb-space-4);
  box-shadow: var(--sb-shadow-sm);
}

.dashboard-card h2 {
  font-size: var(--sb-text-md);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0 0 var(--sb-space-3) 0;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sb-space-3);
}
.card-header-row h2 {
  margin: 0;
}

.text-link-btn {
  background: transparent;
  border: none;
  color: var(--sb-text-hint);
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-semibold);
  cursor: pointer;
  padding: var(--sb-space-1);
}
.text-link-btn:hover {
  color: var(--sb-color-brand);
}

/* Empty Project State */
.empty-projects-state {
  text-align: center;
  padding: var(--sb-space-6) var(--sb-space-4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sb-space-2);
}
.empty-icon {
  font-size: var(--sb-text-3xl);
}
.empty-projects-state h3 {
  font-size: var(--sb-text-md);
  font-weight: var(--sb-weight-bold);
  margin: 0;
}
.empty-projects-state p {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-hint);
  max-width: 320px;
  margin: 0;
}

/* Projects grid list */
.projects-list-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--sb-space-3);
  max-height: 250px;
  overflow-y: auto;
  padding-right: var(--sb-space-1);
}

.project-card-item {
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-md);
  padding: var(--sb-space-3);
  background: var(--sb-surface-primary);
  display: flex;
  flex-direction: column;
  transition: all 0.2s;
}
.project-card-item:hover {
  border-color: var(--sb-border-hover);
  background: var(--sb-bg-card);
}

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--sb-space-2);
  align-items: center;
}
.project-id-badge {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-bold);
  background: var(--sb-surface-secondary);
  color: var(--sb-text-body);
  padding: 2px var(--sb-space-2);
  border-radius: var(--sb-radius-sm);
}
.card-meta .date {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
}
.project-title {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0 0 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.project-author {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  margin: 0 0 var(--sb-space-3) 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-footer-tags {
  display: flex;
  gap: var(--sb-space-1);
  margin-bottom: var(--sb-space-3);
  flex-wrap: wrap;
}
.card-actions {
  margin-top: auto;
}

/* Quick Actions Cards */
.quick-actions-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--sb-space-3);
}

.action-card {
  display: flex;
  align-items: flex-start;
  gap: var(--sb-space-2);
  padding: var(--sb-space-3);
  background: var(--sb-surface-primary);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-md);
  text-align: left;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.action-card:hover {
  background: var(--sb-color-brand-light);
  border-color: var(--sb-color-brand);
}

.action-card:focus-visible {
  outline: var(--sb-focus-ring);
}

.action-icon {
  font-size: var(--sb-text-xl);
  line-height: 1;
}

.action-desc h4 {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-bold);
  margin: 0 0 2px 0;
  color: var(--sb-text-heading);
}

.action-desc p {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  margin: 0;
  line-height: var(--sb-leading-tight);
}

/* Form Design Details */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.field-label {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-1);
}

.field-label span {
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-semibold);
  color: var(--sb-text-muted);
}

.warning-block {
  margin-top: var(--sb-space-3);
  background: var(--sb-status-warn-bg);
  border: 1px solid var(--sb-border-hover);
  padding: var(--sb-space-3);
  border-radius: var(--sb-radius-md);
}

.warning-block h3 {
  font-size: var(--sb-text-xs);
  color: var(--sb-status-warn-text);
  font-weight: var(--sb-weight-bold);
  margin: 0 0 var(--sb-space-2) 0;
}

.warning-block ul {
  margin: 0;
  padding-left: var(--sb-space-4);
  font-size: var(--sb-text-xs);
  color: var(--sb-status-warn-text);
}

.action-row {
  display: flex;
  gap: var(--sb-space-2);
  margin-top: var(--sb-space-3);
}

.block-btn {
  flex: 1;
  min-height: 38px;
}

/* Readiness List */
.readiness-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
}

.readiness-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--sb-text-sm);
}

.readiness-item .name {
  color: var(--sb-text-body);
  font-weight: var(--sb-weight-medium);
}

/* Trust footer at very bottom */
.console-trust-footer {
  display: flex;
  justify-content: center;
  gap: var(--sb-space-6);
  margin-top: var(--sb-space-6);
  padding-top: var(--sb-space-4);
  border-top: 1px solid var(--sb-border-color);
  flex-wrap: wrap;
}
.trust-badge {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  font-weight: var(--sb-weight-medium);
  display: inline-flex;
  align-items: center;
  gap: var(--sb-space-1);
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

.blurb-modal .modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
}

.blurb-modal .modal-card {
  position: relative;
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-xl);
  max-width: 500px;
  width: 90%;
  box-shadow: var(--sb-shadow-lg);
  display: flex;
  flex-direction: column;
  z-index: 201;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--sb-space-4);
  border-bottom: 1px solid var(--sb-border-color);
}
.modal-header h2 {
  font-size: var(--sb-text-lg);
  font-weight: var(--sb-weight-bold);
  margin: 0;
  color: var(--sb-text-heading);
}
.close-btn {
  background: transparent;
  border: none;
  font-size: var(--sb-text-xl);
  color: var(--sb-text-hint);
  cursor: pointer;
  line-height: 1;
}
.close-btn:hover {
  color: var(--sb-color-brand);
}

.modal-body {
  padding: var(--sb-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
  max-height: 400px;
  overflow-y: auto;
}
.hint-text {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--sb-space-2);
  padding: var(--sb-space-4);
  border-top: 1px solid var(--sb-border-color);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

/* Responsive styles */
@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: var(--sb-space-4);
  }
  .projects-list-grid {
    grid-template-columns: 1fr;
    max-height: none;
  }
  .quick-actions-row {
    grid-template-columns: 1fr;
  }
  .cta-row {
    flex-direction: column;
    align-items: stretch;
  }
  .cta-row button {
    width: 100%;
  }
  .console-trust-footer {
    flex-direction: column;
    align-items: center;
    gap: var(--sb-space-2);
  }
}
</style>
