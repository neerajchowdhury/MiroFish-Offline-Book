<template>
  <SwarmbookAppShell
    active-route="SwarmbookSimulation"
    :project-id="session.projectId"
    title="Reader Swarm Setup"
    subtitle="Configure simulated reader cohorts, select platform surfaces, and define privacy and scale boundaries before starting the stress-testing loop."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="setup-container">
      <form @submit.prevent="runSimulation" class="setup-grid">
        <!-- Left Side: Configuration Controls -->
        <div class="config-column">
          <!-- Section 1: Simulation Profile Selection -->
          <fieldset class="setup-card">
            <legend class="card-title">1. Select Simulation Profile</legend>
            <p class="section-hint">Choose how detailed the reader simulation should be. Faster profiles use fewer resources.</p>
            
            <div class="profile-cards-grid" role="radiogroup" aria-label="Simulation Profiles">
              <div
                v-for="profile in profileOptions"
                :key="profile.profile_name"
                class="profile-selection-card"
                :class="{ active: form.profileName === profile.profile_name }"
                @click="selectProfile(profile.profile_name)"
                @keydown.enter="selectProfile(profile.profile_name)"
                @keydown.space.prevent="selectProfile(profile.profile_name)"
                role="radio"
                tabindex="0"
                :aria-checked="form.profileName === profile.profile_name ? 'true' : 'false'"
                :aria-label="getProfileLabel(profile.profile_name)"
              >
                <div class="profile-card-header">
                  <span class="profile-icon">{{ getProfileIcon(profile.profile_name) }}</span>
                  <div class="profile-title-row">
                    <h3>{{ getProfileLabel(profile.profile_name) }}</h3>
                    <span 
                      v-if="profile.profile_name === 'hybrid_safe_default'" 
                      class="recommendation-badge"
                    >
                      ★ Recommended
                    </span>
                  </div>
                </div>
                <p class="profile-desc">{{ getProfileDesc(profile.profile_name) }}</p>
                <div class="profile-meta-chips">
                  <span>👥 Default: {{ profile.max_personas }} readers</span>
                  <span>🌐 Platforms: {{ profile.platforms?.length || 0 }}</span>
                </div>
              </div>
            </div>
          </fieldset>

          <!-- Section 2: Reader Cohort Size -->
          <fieldset class="setup-card">
            <legend class="card-title">2. Choose Reader Count</legend>
            <p class="section-hint">Select the size of the simulated reader cohort. More readers provide higher polarization resolution.</p>
            
            <div class="slider-control-group">
              <label class="slider-label-row" for="reader-count-slider">
                <span>Total Simulated Readers:</span>
                <strong class="count-indicator">{{ form.personaCount }} personas</strong>
              </label>
              <div class="slider-wrapper">
                <input
                  id="reader-count-slider"
                  v-model.number="form.personaCount"
                  type="range"
                  min="2"
                  max="80"
                  class="premium-slider"
                  aria-valuemin="2"
                  aria-valuemax="80"
                  :aria-valuenow="form.personaCount"
                />
                <div class="slider-marks">
                  <span>2</span>
                  <span>12 (Tiny)</span>
                  <span>30 (Standard)</span>
                  <span>60 (Deep)</span>
                  <span>80</span>
                </div>
              </div>
              <span class="recommendation-helper">
                💡 Profile default: {{ selectedProfile?.max_personas || 30 }} personas. Slower workstations should target 12-20 readers.
              </span>
            </div>
          </fieldset>

          <!-- Section 3: Platform Selection Checklist -->
          <fieldset class="setup-card">
            <legend class="card-title">3. Simulated Platforms</legend>
            <p class="section-hint">Select social spaces where readers share reviews, hot-takes, and recommendations.</p>
            
            <div class="platforms-checkbox-grid">
              <button
                v-for="platform in platformOptions"
                :key="platform"
                type="button"
                class="platform-pill-btn"
                :class="{ active: form.platforms.includes(platform) }"
                @click="togglePlatform(platform)"
                :aria-pressed="form.platforms.includes(platform) ? 'true' : 'false'"
                :aria-label="`Toggle ${getPlatformName(platform)} platform`"
              >
                <span class="platform-icon">{{ getPlatformIconSymbol(platform) }}</span>
                <span class="platform-name">{{ getPlatformName(platform) }}</span>
              </button>
            </div>
            
            <div v-if="!form.platforms.length" class="inline-error-alert" role="alert">
              ⚠️ You must select at least one platform to simulate reactions.
            </div>
          </fieldset>

          <!-- Section 4: Reader Cohorts Checklist -->
          <fieldset class="setup-card">
            <legend class="card-title">4. Active Reader Cohorts</legend>
            <p class="section-hint">Select which reader personalities should be generated to read and critique your draft.</p>
            
            <div class="cohorts-header-actions">
              <button type="button" class="action-link-btn" @click="selectAllCohorts">Select All</button>
              <span class="bullet-divider">•</span>
              <button type="button" class="action-link-btn" @click="clearAllCohorts">Clear All</button>
            </div>

            <div class="cohorts-selection-list">
              <label 
                v-for="cohort in cohortOptions" 
                :key="cohort.id" 
                class="cohort-checkbox-card"
                :class="{ checked: isCohortEnabled(cohort.id) }"
              >
                <input 
                  type="checkbox" 
                  :checked="isCohortEnabled(cohort.id)"
                  @change="toggleCohort(cohort.id)"
                  class="premium-checkbox"
                />
                <div class="cohort-text-block">
                  <span class="cohort-label">{{ cohort.label }}</span>
                  <p class="cohort-desc">{{ cohort.description }}</p>
                </div>
              </label>
            </div>
          </fieldset>
        </div>

        <!-- Right Side: Status Summary and Running Dashboard -->
        <div class="status-column">
          <!-- Section 5: Privacy Guard & Connection Status Matrix -->
          <div class="setup-card status-card">
            <h2 class="card-title-standalone">Privacy &amp; Connection Status</h2>
            
            <!-- Privacy Summary Block -->
            <div class="privacy-status-block" :class="form.privacyMode">
              <div class="privacy-header-row">
                <span class="lock-symbol">🔒</span>
                <div>
                  <strong>Privacy Mode: {{ getPrivacyLabel(form.privacyMode) }}</strong>
                  <span class="privacy-cost-tag">{{ getPrivacyCostLabel(form.privacyMode) }}</span>
                </div>
              </div>
              <p class="privacy-explanation-text">{{ getPrivacyExplanation(form.privacyMode) }}</p>
            </div>

            <!-- Provider Connection Matrix -->
            <div class="connection-matrix">
              <h4>System Connection Status</h4>
              <div class="matrix-grid">
                <div class="matrix-item">
                  <span class="svc-name">Ollama (Local LLM)</span>
                  <span class="svc-status" :class="healthSummary.ollama.toLowerCase()">
                    {{ healthSummary.ollama }}
                  </span>
                </div>
                <div class="matrix-item">
                  <span class="svc-name">Neo4j (Graph Storage)</span>
                  <span class="svc-status" :class="healthSummary.neo4j.toLowerCase()">
                    {{ healthSummary.neo4j }}
                  </span>
                </div>
                <div class="matrix-item">
                  <span class="svc-name">Gemini (Cloud Model)</span>
                  <span class="svc-status" :class="getProviderStatusClass('gemini_long_context')">
                    {{ getProviderStatusLabel('gemini_long_context') }}
                  </span>
                </div>
                <div class="matrix-item">
                  <span class="svc-name">NVIDIA (Cloud Model)</span>
                  <span class="svc-status" :class="getProviderStatusClass('nvidia_nim')">
                    {{ getProviderStatusLabel('nvidia_nim') }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 6: Dynamic Estimated Run Metrics -->
          <div class="setup-card run-dashboard-card">
            <h2 class="card-title-standalone">Simulation Metrics</h2>
            
            <div class="metrics-row">
              <div class="metric-block">
                <span class="metric-lbl">ESTIMATED RUN TIME</span>
                <strong class="metric-val highlight">{{ formattedEstimatedTime }}</strong>
              </div>
              <div class="metric-block">
                <span class="metric-lbl">SIMULATION SCALE</span>
                <strong class="metric-val">{{ form.personaCount }} personas</strong>
              </div>
            </div>

            <!-- Seed Configuration -->
            <div class="seed-input-block">
              <label for="simulation-seed-input">
                <span class="seed-label-text">Deterministic Seed:</span>
                <input
                  id="simulation-seed-input"
                  v-model.number="form.simulationSeed"
                  type="number"
                  min="0"
                  class="premium-input text-center"
                />
              </label>
              <p class="seed-hint-text">
                Fixed seed ensures identical reader response cohorts are compiled for test iteration.
              </p>
            </div>

            <!-- Warning/Alert Banners -->
            <div v-if="customWarnings.length || selectedProfileWarnings.length" class="alert-banners-stack">
              <div 
                v-for="warning in [...selectedProfileWarnings, ...customWarnings]" 
                :key="warning.code + warning.message" 
                class="setup-warning-banner"
                role="alert"
              >
                <span class="warning-icon">⚠️</span>
                <p class="warning-message">{{ warning.message }}</p>
              </div>
            </div>

            <!-- Active Trigger Action Button -->
            <div class="trigger-action-block">
              <button 
                type="submit" 
                class="primary-btn run-simulation-btn" 
                :disabled="running || !canRun"
              >
                <span v-if="running" class="spinning-loader"></span>
                <span>{{ running ? 'Running Cohort Pass...' : 'Run Simulation Swarm 🚀' }}</span>
              </button>
              
              <button 
                type="button" 
                class="ghost-btn cancel-setup-btn" 
                @click="goBack"
                :disabled="running"
              >
                ← Back to Evidence
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { createBookSimProject, getBookSimHealth, runBookSimulation } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())

const error = ref('')
const loadingMessage = ref('')
const running = ref(false)
const health = ref(null)

const platformOptions = ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub']
const privacyModes = ['local_only', 'hybrid_safe', 'cloud_quality']

const cohortOptions = [
  { id: 'harsh', label: 'Harsh Reviewers', archetypes: ['goodreads_harsh_reviewer'], description: 'Critical, demanding reviewers who scrutinize pacing, character development, and plot holes.' },
  { id: 'loyalists', label: 'Genre Loyalists', archetypes: ['goodreads_genre_loyalist', 'reddit_genre_purist'], description: 'Highly committed to genre conventions, tropes, and familiar endings.' },
  { id: 'amplifiers', label: 'Emotional Amplifiers', archetypes: ['booktok_emotional_amplifier'], description: 'React confessionally to emotional arcs, heartbreaks, and shareable lines.' },
  { id: 'skeptics', label: 'Skeptics', archetypes: ['reddit_skeptic'], description: 'Analytical forum members checking internal logic, details, and unearned hype.' },
  { id: 'casual', label: 'Casual Readers', archetypes: ['casual_kindle_reader'], description: 'Pragmatic readers prioritizing clear stakes, easy flow, and readability.' },
  { id: 'literary', label: 'Literary Readers', archetypes: ['literary_reader'], description: 'Prize craft-conscious styles, voice, subtext, and thematic depth.' },
  { id: 'evidence_skeptics', label: 'Non-Fiction Evidence Skeptics', archetypes: ['nonfiction_evidence_skeptic'], description: 'Verify claim integrity, citations, methodology, and logic limits.' }
]

const disabledCohorts = ref([])

const form = reactive({
  profileName: session.value.simulationConfig.profileName || session.value.metadata.localProfile || 'hybrid_safe_default',
  personaCount: session.value.simulationConfig.personaCount || 30,
  platforms: [...(session.value.simulationConfig.platforms || ['goodreads', 'reddit', 'booktok'])],
  privacyMode: session.value.simulationConfig.privacyMode || session.value.metadata.privacyMode || 'hybrid_safe',
  simulationSeed: session.value.simulationConfig.simulationSeed ?? 17,
})

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

const healthSummary = computed(() => {
  if (!health.value) {
    return { ollama: 'Checking...', neo4j: 'Checking...' }
  }
  return {
    ollama: health.value.ollama?.ok ? 'Connected' : 'Offline',
    neo4j: health.value.neo4j?.ok ? 'Connected' : 'Offline',
  }
})

const customWarnings = computed(() => {
  const list = []
  if (form.profileName === 'cloud_quality') {
    list.push({
      code: 'heavy_cloud',
      message: 'Cloud Quality profile uploads manuscript chunks to external APIs. Ensure Gemini and NVIDIA keys are configured in your local environment.'
    })
  }
  if (form.personaCount > 40 && form.privacyMode === 'local_only') {
    list.push({
      code: 'high_local_load',
      message: 'Configuring more than 40 personas on a local profile may cause heavy CPU/GPU memory load on standard 16GB RAM workstations. Consider reducing reader count to 12-20.'
    })
  }
  return list
})

const estimatedTimeSec = computed(() => {
  const count = form.personaCount || 0
  let perPersona = 2.0
  if (form.profileName === 'local_tiny') perPersona = 1.2
  else if (form.profileName === 'hybrid_safe_default') perPersona = 2.8
  else if (form.profileName === 'cloud_quality') perPersona = 4.5

  return Math.ceil(count * perPersona)
})

const formattedEstimatedTime = computed(() => {
  const sec = estimatedTimeSec.value
  if (sec < 60) return `~${sec} seconds`
  const min = Math.floor(sec / 60)
  const remainingSec = sec % 60
  if (remainingSec === 0) return `~${min} min`
  return `~${min} min ${remainingSec} sec`
})

const excludeArchetypesList = computed(() => {
  const list = []
  cohortOptions.forEach(cohort => {
    if (disabledCohorts.value.includes(cohort.id)) {
      list.push(...cohort.archetypes)
    }
  })
  return list
})

const canRun = computed(() => {
  return Boolean(
    session.value.projectId &&
    session.value.evidencePack?.pack_id &&
    form.platforms.length > 0
  )
})

function selectProfile(profileName) {
  form.profileName = profileName
  const selected = profileOptions.value.find((p) => p.profile_name === profileName)
  if (selected) {
    form.privacyMode = selected.privacy_mode || form.privacyMode
    form.personaCount = selected.max_personas || form.personaCount
    form.platforms = (selected.platforms || []).map((p) => String(p).toLowerCase())
  }
  saveStateToSession()
}

function togglePlatform(platform) {
  if (form.platforms.includes(platform)) {
    form.platforms = form.platforms.filter((p) => p !== platform)
  } else {
    form.platforms = [...form.platforms, platform]
  }
  saveStateToSession()
}

function isCohortEnabled(cohortId) {
  return !disabledCohorts.value.includes(cohortId)
}

function toggleCohort(cohortId) {
  if (disabledCohorts.value.includes(cohortId)) {
    disabledCohorts.value = disabledCohorts.value.filter(id => id !== cohortId)
  } else {
    disabledCohorts.value = [...disabledCohorts.value, cohortId]
  }
  saveStateToSession()
}

function selectAllCohorts() {
  disabledCohorts.value = []
  saveStateToSession()
}

function clearAllCohorts() {
  disabledCohorts.value = cohortOptions.map(c => c.id)
  saveStateToSession()
}

function getProfileLabel(name) {
  if (name === 'local_tiny') return 'Draft Quality (Local Tiny)'
  if (name === 'hybrid_safe_default') return 'Standard Stress Test (Hybrid)'
  if (name === 'cloud_quality') return 'Deep Analysis (Cloud)'
  return name
}

function getProfileIcon(name) {
  if (name === 'local_tiny') return '⚡'
  if (name === 'hybrid_safe_default') return '⚖️'
  if (name === 'cloud_quality') return '🔮'
  return '⚙️'
}

function getProfileDesc(name) {
  if (name === 'local_tiny') return 'Runs fast on local CPU/GPU using tiny model. Best for quick drafts and checking basics.'
  if (name === 'hybrid_safe_default') return 'Runs a standard 30-reader cohort using local Ollama. Balanced resource footprint.'
  if (name === 'cloud_quality') return 'Deep multi-round simulation using advanced cloud models. May incur API costs.'
  return 'Custom simulation profile.'
}

function getPlatformIconSymbol(platform) {
  const icons = {
    goodreads: '📚',
    booktok: '🎵',
    reddit: '👽',
    bookstagram: '📸',
    x: '🐦',
    newsletter: '✉️',
    bookclub: '👥'
  }
  return icons[platform] || '🌐'
}

function getPlatformName(platform) {
  const names = {
    goodreads: 'Goodreads',
    booktok: 'BookTok',
    reddit: 'Reddit',
    bookstagram: 'Bookstagram',
    x: 'X (Twitter)',
    newsletter: 'Newsletter',
    bookclub: 'Book Club'
  }
  return names[platform] || platform
}

function getPrivacyLabel(mode) {
  if (mode === 'local_only') return 'Local Only'
  if (mode === 'hybrid_safe') return 'Hybrid Safe'
  if (mode === 'cloud_quality') return 'Cloud Quality'
  return mode
}

function getPrivacyCostLabel(mode) {
  if (mode === 'local_only') return '0% Cost / 100% Private'
  if (mode === 'hybrid_safe') return 'Free / Safe indexing'
  if (mode === 'cloud_quality') return 'API usage charges apply'
  return ''
}

function getPrivacyExplanation(mode) {
  if (mode === 'local_only') return 'No data leaves your device. Entire simulation runs locally on your Ollama server.'
  if (mode === 'hybrid_safe') return 'Mixes local processing with safe cloud APIs for metadata check. Safe from text-leakage.'
  if (mode === 'cloud_quality') return 'Uploads text chunks to advanced cloud models for maximum analytical detail.'
  return ''
}

function getProviderStatusLabel(routeKey) {
  if (!health.value || !health.value.providers) return 'Checking...'
  const prov = health.value.providers[routeKey]
  if (!prov) return 'Bypassed'
  return prov.ok ? 'Online' : 'Offline'
}

function getProviderStatusClass(routeKey) {
  if (!health.value || !health.value.providers) return 'checking'
  const prov = health.value.providers[routeKey]
  if (!prov) return 'bypassed'
  return prov.ok ? 'online' : 'offline'
}

function ensureSession() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId || !session.value.evidencePack?.pack_id) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

function saveStateToSession() {
  session.value = updateSwarmbookSession({
    metadata: {
      ...session.value.metadata,
      localProfile: form.profileName,
      privacyMode: form.privacyMode,
    },
    simulationConfig: {
      ...session.value.simulationConfig,
      profileName: form.profileName,
      personaCount: form.personaCount,
      platforms: [...form.platforms],
      privacyMode: form.privacyMode,
      simulationSeed: form.simulationSeed,
      profileWarnings: selectedProfileWarnings.value,
      disabledCohorts: [...disabledCohorts.value]
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
  } catch (err) {
    error.value = `Failed to fetch server status details: ${err.message}`
  }
}

function goBack() {
  router.push({ name: 'SwarmbookEvidence', params: { projectId: session.value.projectId } })
}

function runSimulation() {
  saveStateToSession()
  router.push({ name: 'SwarmbookSimulationRun', params: { projectId: session.value.projectId } })
}

onMounted(() => {
  ensureSession()
  loadProfiles()
  
  // Load exclusions from session if they exist
  const storedDisabled = session.value.simulationConfig?.disabledCohorts
  if (storedDisabled) {
    disabledCohorts.value = [...storedDisabled]
  }
})
</script>

<style scoped>
.setup-container {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.setup-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
}

/* Card layout basics */
.setup-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  width: 100%;
}

.setup-card:focus-within {
  border-color: #cbd5e1;
}

fieldset.setup-card {
  border: 1px solid #e2e8f0;
  margin: 0 0 24px 0;
}

.card-title {
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
  padding: 0 8px;
  margin-bottom: 8px;
}

.card-title-standalone {
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 12px 0;
}

.section-hint {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

/* Section 1: Profile selections */
.profile-cards-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-selection-card {
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  outline: none;
}

.profile-selection-card:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.profile-selection-card:focus-visible {
  outline: 2px solid #ff4500;
  border-color: #ff4500;
}

.profile-selection-card.active {
  border-color: #ff4500;
  background: #fffaf7;
}

.profile-card-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 6px;
}

.profile-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.profile-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
  flex-wrap: wrap;
  gap: 6px;
}

.profile-title-row h3 {
  font-size: 0.95rem;
  font-weight: 800;
  margin: 0;
  color: #0f172a;
}

.recommendation-badge {
  font-size: 0.72rem;
  font-weight: 800;
  background: #ffebdf;
  color: #e63e00;
  padding: 2px 8px;
  border-radius: 9999px;
  text-transform: uppercase;
}

.profile-desc {
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.4;
  margin: 0 0 10px 0;
}

.profile-meta-chips {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

/* Section 2: Reader Count range slider */
.slider-control-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.slider-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  font-weight: 600;
  color: #475569;
}

.count-indicator {
  font-size: 1.1rem;
  color: #ff4500;
  font-weight: 800;
}

.slider-wrapper {
  margin-bottom: 6px;
}

.premium-slider {
  width: 100%;
  height: 6px;
  background: #cbd5e1;
  border-radius: 9999px;
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.premium-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ff4500;
  cursor: pointer;
  transition: transform 0.1s;
}

.premium-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.premium-slider:focus-visible::-webkit-slider-thumb {
  box-shadow: 0 0 0 3px rgba(255, 69, 0, 0.4);
}

.slider-marks {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  padding: 4px 2px 0 2px;
}

.recommendation-helper {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.4;
  background: #f8fafc;
  padding: 10px 12px;
  border-radius: 6px;
}

/* Section 3: Platforms selection buttons */
.platforms-checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
}

.platform-pill-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  transition: all 0.15s ease-in-out;
}

.platform-pill-btn:hover {
  border-color: #94a3b8;
  background: #f8fafc;
}

.platform-pill-btn.active {
  border-color: #ff4500;
  background: #fff5ef;
  color: #e63e00;
  box-shadow: 0 0 0 1px #ff4500;
}

.platform-pill-btn:focus-visible {
  outline: 2px solid #ff4500;
}

.platform-icon {
  font-size: 1.1rem;
}

.inline-error-alert {
  margin-top: 12px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #ef4444;
  background: #fee2e2;
  padding: 8px 12px;
  border-radius: 6px;
}

/* Section 4: Cohort cards list */
.cohorts-header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.8rem;
}

.action-link-btn {
  background: transparent;
  border: none;
  color: #ff4500;
  font-weight: 700;
  cursor: pointer;
  padding: 2px 4px;
  font: inherit;
  font-size: 0.8rem;
}

.action-link-btn:hover {
  text-decoration: underline;
}

.bullet-divider {
  color: #cbd5e1;
}

.cohorts-selection-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cohort-checkbox-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  cursor: pointer;
  transition: border-color 0.2s;
}

.cohort-checkbox-card:hover {
  border-color: #cbd5e1;
}

.cohort-checkbox-card.checked {
  border-color: #ff4500;
  background: #ffffff;
}

.premium-checkbox {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid #cbd5e1;
  accent-color: #ff4500;
  margin-top: 2px;
}

.cohort-text-block {
  flex: 1;
}

.cohort-label {
  display: block;
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 3px;
}

.cohort-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
  line-height: 1.3;
}

/* Status Column Styles */
.status-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.privacy-status-block {
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  border-left: 4px solid #cbd5e1;
}

.privacy-status-block.local_only {
  background: #ecfdf5;
  border-color: #10b981;
}

.privacy-status-block.hybrid_safe {
  background: #eff6ff;
  border-color: #3b82f6;
}

.privacy-status-block.cloud_quality {
  background: #fef3c7;
  border-color: #f59e0b;
}

.privacy-header-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 8px;
}

.lock-symbol {
  font-size: 1.4rem;
}

.privacy-header-row strong {
  display: block;
  font-size: 0.88rem;
  color: #0f172a;
}

.privacy-cost-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(0,0,0,0.06);
  margin-top: 2px;
}

.privacy-explanation-text {
  font-size: 0.8rem;
  color: #475569;
  line-height: 1.4;
  margin: 0;
}

.connection-matrix h4 {
  font-size: 0.82rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  margin: 0 0 10px 0;
}

.matrix-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.matrix-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  font-size: 0.82rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.matrix-item:last-child {
  border-bottom: none;
}

.svc-name {
  font-weight: 600;
  color: #475569;
}

.svc-status {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
}

.svc-status.online { background: #d1fae5; color: #065f46; }
.svc-status.connected { background: #d1fae5; color: #065f46; }
.svc-status.offline { background: #fee2e2; color: #991b1b; }
.svc-status.disabled { background: #f1f5f9; color: #64748b; }
.svc-status.bypassed { background: #f1f5f9; color: #64748b; }
.svc-status.checking { background: #fef3c7; color: #92400e; }

/* Dynamic estimated run metrics card */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.metric-block {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}

.metric-lbl {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.metric-val {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
}

.metric-val.highlight {
  color: #ff4500;
}

.seed-input-block {
  margin-bottom: 20px;
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
}

.seed-input-block label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.seed-label-text {
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
}

.premium-input {
  width: 90px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 6px 10px;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  outline: none;
}

.premium-input:focus {
  border-color: #ff4500;
  box-shadow: 0 0 0 1px #ff4500;
}

.text-center {
  text-align: center;
}

.seed-hint-text {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.3;
  margin: 6px 0 0 0;
}

.alert-banners-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.setup-warning-banner {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 6px;
  align-items: flex-start;
}

.warning-icon {
  font-size: 1rem;
  margin-top: 1px;
}

.warning-message {
  font-size: 0.78rem;
  color: #92400e;
  line-height: 1.3;
  margin: 0;
}

.trigger-action-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.run-simulation-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  border-radius: 8px;
}

.run-simulation-btn:disabled {
  opacity: 0.6;
}

.cancel-setup-btn {
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
}

.spinning-loader {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 950px) {
  .setup-grid {
    grid-template-columns: 1fr;
  }
}
</style>
