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
      <!-- Global Synthetic Sandbox Banner -->
      <section class="sandbox-warning-banner sb-card-inset" role="note">
        <span class="banner-icon" aria-hidden="true">🔒</span>
        <div class="banner-text">
          <strong>Synthetic Sandbox:</strong> Swarmbook Studio executes reader agents in an offline, synthetic simulation. No live social media accounts will be scraped or accessed, and no real posts will be created. All platform reactions, review threads, and feeds are simulated.
        </div>
      </section>

      <form @submit.prevent="runSimulation" class="setup-grid">
        <!-- Left Side: Configuration Controls -->
        <main class="config-column" role="region" aria-label="Swarm Configurations">
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
                  <div class="profile-header-left">
                    <span class="profile-icon" aria-hidden="true">{{ getProfileIcon(profile.profile_name) }}</span>
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
                  <span class="profile-model-tag" :class="profile.privacy_mode">
                    {{ getProfileRouteType(profile.profile_name) }}
                  </span>
                </div>
                <p class="profile-desc">{{ getProfileDesc(profile.profile_name) }}</p>
                <div class="profile-model-usage">
                  <strong>🤖 Model Engine:</strong> {{ getProfileModelUsage(profile.profile_name) }}
                </div>
                <div class="profile-meta-chips">
                  <span>👥 Target Cohort: {{ profile.max_personas }} readers</span>
                  <span>🌐 Simulated Platforms: {{ profile.platforms?.length || 0 }}</span>
                </div>
              </div>
            </div>
          </fieldset>

          <!-- Section 2: Reader Cohort Size Slider -->
          <fieldset class="setup-card">
            <legend class="card-title">2. Choose Reader Scale</legend>
            <p class="section-hint">Select the size of the simulated reader cohort. Larger cohorts offer higher feedback resolution but require more computing power.</p>
            
            <div class="slider-control-group">
              <div class="slider-label-row">
                <label for="reader-count-slider">Total Simulated Readers:</label>
                <strong class="count-indicator highlight-orange">{{ form.personaCount }} personas</strong>
              </div>
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
              
              <!-- Workstation Load Meter -->
              <div class="workstation-load-meter" :class="loadCategory">
                <span class="load-indicator-dot"></span>
                <span class="load-text">
                  <strong>Workstation Load: {{ loadLabel }}</strong> — {{ loadDescription }}
                </span>
              </div>
            </div>
          </fieldset>

          <!-- Section 3: Platform Selection Checklist -->
          <fieldset class="setup-card">
            <legend class="card-title">3. Simulated Platform Channels</legend>
            <p class="section-hint">Select social channels where simulated readers share reviews. (All posts are mock outputs inside the sandbox environment).</p>
            
            <div class="platforms-checkbox-grid">
              <button
                v-for="platform in platformOptions"
                :key="platform"
                type="button"
                class="platform-pill-btn"
                :class="{ active: form.platforms.includes(platform) }"
                @click="togglePlatform(platform)"
                :aria-pressed="form.platforms.includes(platform) ? 'true' : 'false'"
                :aria-label="`Toggle simulated ${getPlatformName(platform)} reactions`"
              >
                <span class="platform-icon" aria-hidden="true">{{ getPlatformIconSymbol(platform) }}</span>
                <div class="platform-pill-labels">
                  <span class="platform-name">{{ getPlatformName(platform) }}</span>
                  <span class="platform-sub-label">Simulated Only</span>
                </div>
              </button>
            </div>
            
            <div v-if="!form.platforms.length" class="inline-error-alert" role="alert">
              ⚠️ You must select at least one platform channel to simulate reviews.
            </div>
          </fieldset>

          <!-- Section 4: Reader Cohorts Checklist -->
          <fieldset class="setup-card">
            <legend class="card-title">4. Active Reader Segments</legend>
            <p class="section-hint">Select the cohorts generated to critique your draft. Cohorts are weighted and matched based on your Book DNA.</p>
            
            <div class="cohorts-header-actions">
              <button type="button" class="action-link-btn" @click="selectAllCohorts">Select All Cohorts</button>
              <span class="bullet-divider">•</span>
              <button type="button" class="action-link-btn" @click="clearAllCohorts">Exclude All</button>
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
                  <div class="cohort-title-row">
                    <span class="cohort-label">{{ cohort.label }}</span>
                    <span class="archetypes-list-hint">Archetypes: {{ cohort.archetypes.join(', ') }}</span>
                  </div>
                  <p class="cohort-desc">{{ cohort.description }}</p>
                  <blockquote class="cohort-typical-quote">
                    "{{ getCohortTypicalQuote(cohort.id) }}"
                  </blockquote>
                </div>
              </label>
            </div>
          </fieldset>

          <!-- Advanced Simulation Options (Collapsed by default) -->
          <details class="advanced-settings-details sb-card">
            <summary class="advanced-summary-title">⚙️ Advanced Simulation Tuning Parameters</summary>
            <div class="advanced-settings-body">
              <p class="section-hint">Tune specific pipeline properties. Modify only if customizing iteration passes.</p>
              
              <div class="advanced-form-grid">
                <!-- Seed Configuration -->
                <div class="advanced-field">
                  <label for="simulation-seed-input">
                    <span class="advanced-label-text">Deterministic Seed:</span>
                    <input
                      id="simulation-seed-input"
                      v-model.number="form.simulationSeed"
                      type="number"
                      min="0"
                      class="premium-input text-center"
                    />
                  </label>
                  <span class="advanced-hint-text">
                    Fixed seed compiles identical reader agents for repeatable draft stress-testing.
                  </span>
                </div>

                <!-- Parallel Jobs -->
                <div class="advanced-field">
                  <label for="local-parallel-jobs-input">
                    <span class="advanced-label-text">Max Parallel Workers:</span>
                    <input
                      id="local-parallel-jobs-input"
                      v-model.number="form.localParallelJobs"
                      type="number"
                      min="1"
                      max="8"
                      class="premium-input text-center"
                    />
                  </label>
                  <span class="advanced-hint-text">
                    Max threads to run. Set to 1 on local Ollama to avoid memory crashes.
                  </span>
                </div>

                <!-- Reaction Rounds -->
                <div class="advanced-field">
                  <label for="reaction-rounds-input">
                    <span class="advanced-label-text">Reaction Passes Count:</span>
                    <input
                      id="reaction-rounds-input"
                      v-model.number="form.reactionRounds"
                      type="number"
                      min="1"
                      max="5"
                      class="premium-input text-center"
                    />
                  </label>
                  <span class="advanced-hint-text">
                    Rounds of posts compiled before finishing report scoring.
                  </span>
                </div>

                <!-- Cross reaction shortlist posts -->
                <div class="advanced-field">
                  <label for="cross-reaction-posts-input">
                    <span class="advanced-label-text">Cross-Reaction Feed Cap:</span>
                    <input
                      id="cross-reaction-posts-input"
                      v-model.number="form.crossReactionPosts"
                      type="number"
                      min="1"
                      max="20"
                      class="premium-input text-center"
                    />
                  </label>
                  <span class="advanced-hint-text">
                    Shortlist size of peer posts each reader evaluates during feeds reaction passes.
                  </span>
                </div>
              </div>
            </div>
          </details>
        </main>

        <!-- Right Side: Status Summary and Running Dashboard -->
        <aside class="status-column" role="complementary" aria-label="System Readiness status">
          <!-- Section 5: Privacy Guard & Connection Status Matrix -->
          <div class="setup-card status-card">
            <h2 class="card-title-standalone">Privacy Policy &amp; Security Matrix</h2>
            
            <!-- Privacy Summary Block -->
            <div class="privacy-status-block" :class="form.privacyMode">
              <div class="privacy-header-row">
                <span class="lock-symbol" aria-hidden="true">🔒</span>
                <div>
                  <strong>Privacy Level: {{ getPrivacyLabel(form.privacyMode) }}</strong>
                  <span class="privacy-cost-tag">{{ getPrivacyCostLabel(form.privacyMode) }}</span>
                </div>
              </div>
              <p class="privacy-explanation-text">{{ getPrivacyExplanation(form.privacyMode) }}</p>
              <div class="leakage-assurance">
                <strong>Assurance:</strong> {{ getLeakageAssurance(form.privacyMode) }}
              </div>
            </div>

            <!-- Provider Connection Matrix -->
            <div class="connection-matrix">
              <h4>Active Server Pipelines</h4>
              <div class="matrix-grid">
                <div class="matrix-item">
                  <span class="svc-name">Ollama (Local LLM Core)</span>
                  <span class="svc-status" :class="healthSummary.ollama.toLowerCase()">
                    {{ healthSummary.ollama }}
                  </span>
                </div>
                <div class="matrix-item">
                  <span class="svc-name">Neo4j (Local Graph Database)</span>
                  <span class="svc-status" :class="healthSummary.neo4j.toLowerCase()">
                    {{ healthSummary.neo4j }}
                  </span>
                </div>
                <div class="matrix-item">
                  <span class="svc-name">Gemini Cloud API</span>
                  <span class="svc-status" :class="getProviderStatusClass('gemini_long_context')">
                    {{ getProviderStatusLabel('gemini_long_context') }}
                  </span>
                </div>
                <div class="matrix-item">
                  <span class="svc-name">NVIDIA NIM Endpoint</span>
                  <span class="svc-status" :class="getProviderStatusClass('nvidia_nim')">
                    {{ getProviderStatusLabel('nvidia_nim') }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 6: Dynamic Estimated Run Metrics -->
          <div class="setup-card run-dashboard-card">
            <h2 class="card-title-standalone">Pipeline Simulation Forecast</h2>
            
            <div class="metrics-row">
              <div class="metric-block">
                <span class="metric-lbl">ESTIMATED RUN TIME</span>
                <strong class="metric-val highlight-orange">{{ formattedEstimatedTime }}</strong>
              </div>
              <div class="metric-block">
                <span class="metric-lbl">SIMULATION SCALE</span>
                <strong class="metric-val">{{ form.personaCount }} agents</strong>
              </div>
            </div>

            <div class="simulation-detail-summary">
              <div class="summary-line">
                <span>Selected Profile:</span>
                <strong>{{ getProfileLabel(form.profileName) }}</strong>
              </div>
              <div class="summary-line">
                <span>Compute Mode:</span>
                <strong class="privacy-text-class">{{ getPrivacyLabel(form.privacyMode) }}</strong>
              </div>
              <div class="summary-line">
                <span>Model Engine:</span>
                <strong>{{ getProfileModelUsage(form.profileName) }}</strong>
              </div>
              <div class="summary-line">
                <span>Weighted Cohort Match:</span>
                <strong>Tastes matched to "{{ session.metadata?.genre || 'fiction' }}"</strong>
              </div>
            </div>

            <!-- Warning/Alert Banners -->
            <div v-if="customWarnings.length || selectedProfileWarnings.length" class="alert-banners-stack">
              <div 
                v-for="warning in [...selectedProfileWarnings, ...customWarnings]" 
                :key="warning.code + warning.message" 
                class="setup-warning-banner"
                role="alert"
              >
                <span class="warning-icon" aria-hidden="true">⚠️</span>
                <p class="warning-message">{{ warning.message }}</p>
              </div>
            </div>

            <!-- Active Trigger Action Button -->
            <div class="trigger-action-block">
              <button 
                type="submit" 
                class="sb-btn-primary run-simulation-btn" 
                :disabled="running || !canRun"
              >
                <span v-if="running" class="spinning-loader" aria-hidden="true"></span>
                <span>{{ running ? 'Spawning Cohorts...' : 'Run Simulation Swarm 🚀' }}</span>
              </button>
              
              <button 
                type="button" 
                class="sb-btn-ghost cancel-setup-btn" 
                @click="goBack"
                :disabled="running"
              >
                ← Back to Evidence
              </button>
            </div>
          </div>
        </aside>
      </form>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { getBookSimHealth } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())

const error = ref('')
const loadingMessage = ref('')
const running = ref(false)
const health = ref(null)

const platformOptions = ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub']

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
  reactionRounds: session.value.simulationConfig.reactionRounds ?? 2,
  crossReactionPosts: session.value.simulationConfig.crossReactionPosts ?? 8,
  localParallelJobs: session.value.simulationConfig.localParallelJobs ?? 1,
})

const profileOptions = computed(() => {
  return health.value?.profiles?.items || [
    { profile_name: 'local_tiny', privacy_mode: 'local_only', max_personas: 12, platforms: ['goodreads', 'reddit', 'x'], computed_warnings: [], reaction_rounds: 1, cross_reaction_posts: 4, local_parallel_jobs: 1 },
    { profile_name: 'hybrid_safe_default', privacy_mode: 'hybrid_safe', max_personas: 30, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x'], computed_warnings: [], reaction_rounds: 2, cross_reaction_posts: 8, local_parallel_jobs: 1 },
    { profile_name: 'cloud_quality', privacy_mode: 'cloud_quality', max_personas: 60, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub'], computed_warnings: [], reaction_rounds: 3, cross_reaction_posts: 12, local_parallel_jobs: 2 },
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

// Workstation scale computation rules
const loadCategory = computed(() => {
  const count = form.personaCount
  if (count <= 20) return 'safe'
  if (count <= 40) return 'standard'
  return 'heavy'
})

const loadLabel = computed(() => {
  if (loadCategory.value === 'safe') return 'Safe / Efficient'
  if (loadCategory.value === 'standard') return 'Standard Weight'
  return 'Heavy compute'
})

const loadDescription = computed(() => {
  if (loadCategory.value === 'safe') {
    return 'Low memory footprint. Optimized for CPU-local Ollama on standard 16GB RAM workstations.'
  }
  if (loadCategory.value === 'standard') {
    return 'Moderate load. Ensure graphics acceleration (6GB VRAM) is active for local Ollama speed.'
  }
  return 'High resource usage. Local Ollama may crawl or crash. Cloud model profiles recommended.'
})

const customWarnings = computed(() => {
  const list = []
  if (form.profileName === 'cloud_quality') {
    list.push({
      code: 'heavy_cloud',
      message: 'Cloud Quality profile uploads text chunks to external APIs. Ensure Gemini and NVIDIA NIM keys are configured.'
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
    
    // Efficient default: cap personaCount to 16 under local_only to prevent 16GB memory overflow
    if (form.privacyMode === 'local_only') {
      form.personaCount = Math.min(16, selected.max_personas || 12)
    } else {
      form.personaCount = selected.max_personas || form.personaCount
    }
    
    form.platforms = (selected.platforms || []).map((p) => String(p).toLowerCase())
    form.reactionRounds = selected.reaction_rounds ?? form.reactionRounds
    form.crossReactionPosts = selected.cross_reaction_posts ?? form.crossReactionPosts
    form.localParallelJobs = selected.local_parallel_jobs ?? form.localParallelJobs
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
  if (name === 'local_tiny') return 'Draft Quality Profile'
  if (name === 'hybrid_safe_default') return 'Standard Stress Test Profile'
  if (name === 'cloud_quality') return 'Deep Analytics Profile'
  return name
}

function getProfileIcon(name) {
  if (name === 'local_tiny') return '⚡'
  if (name === 'hybrid_safe_default') return '⚖️'
  if (name === 'cloud_quality') return '🔮'
  return '⚙️'
}

function getProfileRouteType(name) {
  if (name === 'local_tiny') return 'CPU Local'
  if (name === 'hybrid_safe_default') return 'GPU Accelerated'
  if (name === 'cloud_quality') return 'Cloud Core'
  return 'Custom'
}

function getProfileModelUsage(name) {
  if (name === 'local_tiny') return 'Ollama (llama3:8b-instruct-fp16) - Low Precision'
  if (name === 'hybrid_safe_default') return 'Ollama (llama3:8b-instruct-fp16) - Full local pass'
  if (name === 'cloud_quality') return 'Cloud API (Gemini 1.5 Pro / Flash & NVIDIA NIM)'
  return 'Custom configured route'
}

function getProfileDesc(name) {
  if (name === 'local_tiny') return 'Runs fast on local CPU/GPU using tiny model. Best for quick drafts and checking basics.'
  if (name === 'hybrid_safe_default') return 'Standard 30-persona stress test running entirely on local Ollama server.'
  if (name === 'cloud_quality') return 'Multi-agent reader swarm using Gemini & NVIDIA APIs for high-resolution text analysis.'
  return 'Custom simulation profile configuration.'
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

function getCohortTypicalQuote(cohortId) {
  const quotes = {
    harsh: 'Avery (Harsh): "The narrative engine felt unearned, and the pacing collapsed in the middle chapters."',
    loyalists: 'Casey (Loyalist): "It delivered on all classic subgenre expectations, though the climax was highly predictable."',
    amplifiers: 'Morgan (Amplifier): "Oh my god, Chapter 15 had me in tears! I shared so many highlight quotes on BookTok."',
    skeptics: 'Celeste (Skeptic): "The logic of the plot hinges on a premise that makes no sense upon reflection."',
    casual: 'Robin (Casual): "An easy weekend read. Nice flow, clean prose, and simple characters."',
    literary: 'Skye (Literary): "Rich prose style with delicate thematic subtext, though casual readers may find it dense."',
    evidence_skeptics: 'Priya (Evidence Skeptic): "The central claim lacks rigorous empirical evidence. Safe conclusions but weak citations."'
  }
  return quotes[cohortId] || 'Simulated reader response quote.'
}

function getPrivacyLabel(mode) {
  if (mode === 'local_only') return 'Local Only'
  if (mode === 'hybrid_safe') return 'Hybrid Safe'
  if (mode === 'cloud_quality') return 'Cloud Quality'
  return mode
}

function getPrivacyCostLabel(mode) {
  if (mode === 'local_only') return '$0.00 Cost / 100% Private'
  if (mode === 'hybrid_safe') return 'Free / Cloud Metadata'
  if (mode === 'cloud_quality') return 'API charges apply'
  return ''
}

function getPrivacyExplanation(mode) {
  if (mode === 'local_only') return 'No data leaves your device. Entire simulation runs locally on your Ollama server.'
  if (mode === 'hybrid_safe') return 'Mixes local processing with safe cloud APIs for metadata check. Safe from text-leakage.'
  if (mode === 'cloud_quality') return 'Uploads text chunks to advanced cloud models for maximum analytical detail.'
  return ''
}

function getLeakageAssurance(mode) {
  if (mode === 'local_only') return '100% Safe. No external API queries or text transmissions compile.'
  if (mode === 'hybrid_safe') return 'Text is masked. Safe from text leakage or cloud training runs.'
  return 'Manuscript snippets sent to external AI servers.'
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
      reactionRounds: form.reactionRounds,
      crossReactionPosts: form.crossReactionPosts,
      localParallelJobs: form.localParallelJobs,
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
  padding: 0 var(--sb-space-4) var(--sb-space-10) var(--sb-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-5);
}

/* Sandbox Banner */
.sandbox-warning-banner {
  display: flex;
  align-items: flex-start;
  gap: var(--sb-space-4);
  background: var(--sb-status-info-bg);
  border: 1px solid var(--sb-border-color);
  border-left: 5px solid var(--sb-color-info);
  border-radius: var(--sb-radius-lg);
  padding: var(--sb-space-4) var(--sb-space-5);
}

.banner-icon {
  font-size: 1.4rem;
  line-height: 1;
}

.banner-text {
  font-size: var(--sb-text-sm);
  color: var(--sb-status-info-text);
  line-height: var(--sb-leading-relaxed);
}

.setup-grid {
  display: grid;
  grid-template-columns: 1.25fr 0.75fr;
  gap: var(--sb-space-6);
}

/* Card layout basics */
.setup-card {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-xl);
  padding: var(--sb-space-6);
  margin-bottom: var(--sb-space-6);
  box-shadow: var(--sb-shadow-sm);
  width: 100%;
}

fieldset.setup-card {
  border: 1px solid var(--sb-border-color);
  margin: 0 0 var(--sb-space-6) 0;
}

.card-title {
  font-size: var(--sb-text-base);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  padding: 0 var(--sb-space-2);
  margin-bottom: var(--sb-space-1);
}

.card-title-standalone {
  font-size: var(--sb-text-base);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0 0 var(--sb-space-4) 0;
}

.section-hint {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  margin: 0 0 var(--sb-space-4) 0;
  line-height: var(--sb-leading-normal);
}

/* Section 1: Profile selections */
.profile-cards-grid {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.profile-selection-card {
  border: 2px solid var(--sb-border-color);
  border-radius: var(--sb-radius-lg);
  padding: var(--sb-space-4);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.profile-selection-card:hover {
  border-color: var(--sb-border-hover);
  background: var(--sb-surface-primary);
}

.profile-selection-card:focus-visible {
  outline: var(--sb-focus-ring);
  border-color: var(--sb-color-brand);
}

.profile-selection-card.active {
  border-color: var(--sb-color-brand);
  background: #fffaf7;
  box-shadow: 0 0 0 1px var(--sb-color-brand);
}

.profile-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--sb-space-3);
  margin-bottom: var(--sb-space-2);
}

.profile-header-left {
  display: flex;
  gap: var(--sb-space-3);
  align-items: center;
}

.profile-icon {
  font-size: 1.6rem;
  line-height: 1;
}

.profile-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--sb-space-2);
}

.profile-title-row h3 {
  font-size: var(--sb-text-md);
  font-weight: var(--sb-weight-bold);
  margin: 0;
  color: var(--sb-text-heading);
}

.recommendation-badge {
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  background: #ffebdf;
  color: var(--sb-color-brand-hover);
  padding: 1px 6px;
  border-radius: var(--sb-radius-full);
  text-transform: uppercase;
}

.profile-model-tag {
  font-family: var(--sb-font-mono);
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  padding: 2px 6px;
  border-radius: var(--sb-radius-sm);
  text-transform: uppercase;
  background: var(--sb-surface-secondary);
  color: var(--sb-text-muted);
}

.profile-desc {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-body);
  line-height: var(--sb-leading-relaxed);
  margin: 0 0 var(--sb-space-2) 0;
}

.profile-model-usage {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  background: var(--sb-surface-secondary);
  padding: var(--sb-space-2);
  border-radius: var(--sb-radius-sm);
  margin-bottom: var(--sb-space-2);
  border-left: 3px solid var(--sb-border-hover);
}

.profile-meta-chips {
  display: flex;
  gap: var(--sb-space-4);
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  font-weight: var(--sb-weight-semibold);
}

/* Section 2: Reader Count range slider */
.slider-control-group {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.slider-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-semibold);
  color: var(--sb-text-muted);
}

.count-indicator {
  font-size: var(--sb-text-xl);
  font-weight: var(--sb-weight-extrabold);
}

.highlight-orange {
  color: var(--sb-color-brand);
}

.slider-wrapper {
  margin-bottom: var(--sb-space-2);
}

.premium-slider {
  width: 100%;
  height: 6px;
  background: var(--sb-border-color);
  border-radius: var(--sb-radius-full);
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.premium-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--sb-color-brand);
  cursor: pointer;
  transition: transform 0.1s;
}

.premium-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.premium-slider:focus-visible::-webkit-slider-thumb {
  box-shadow: var(--sb-shadow-focus);
}

.slider-marks {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: var(--sb-text-hint);
  font-weight: var(--sb-weight-bold);
  padding: 4px 2px 0 2px;
}

/* Workstation load meter */
.workstation-load-meter {
  display: flex;
  align-items: center;
  gap: var(--sb-space-3);
  background: var(--sb-surface-primary);
  padding: var(--sb-space-3) var(--sb-space-4);
  border-radius: var(--sb-radius-md);
  border: 1px solid var(--sb-border-color);
}

.load-indicator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.workstation-load-meter.safe .load-indicator-dot { background: var(--sb-color-ready); }
.workstation-load-meter.standard .load-indicator-dot { background: var(--sb-color-mixed); }
.workstation-load-meter.heavy .load-indicator-dot { background: var(--sb-color-offline); }

.load-text {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  line-height: var(--sb-leading-normal);
}

/* Section 3: Platforms selection buttons */
.platforms-checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--sb-space-3);
}

.platform-pill-btn {
  display: flex;
  align-items: center;
  gap: var(--sb-space-3);
  padding: var(--sb-space-3) var(--sb-space-4);
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-hover);
  border-radius: var(--sb-radius-md);
  cursor: pointer;
  font: inherit;
  transition: all 0.15s;
  text-align: left;
}

.platform-pill-btn:hover {
  border-color: var(--sb-border-hover);
  background: var(--sb-surface-primary);
}

.platform-pill-btn.active {
  border-color: var(--sb-color-brand);
  background: #fff5ef;
  box-shadow: 0 0 0 1px var(--sb-color-brand);
}

.platform-pill-btn.active .platform-name {
  color: var(--sb-color-brand-hover);
}

.platform-pill-btn:focus-visible {
  outline: var(--sb-focus-ring);
}

.platform-icon {
  font-size: 1.3rem;
}

.platform-pill-labels {
  display: flex;
  flex-direction: column;
}

.platform-name {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
}

.platform-sub-label {
  font-size: 0.65rem;
  color: var(--sb-text-hint);
  font-weight: var(--sb-weight-semibold);
  text-transform: uppercase;
}

/* Section 4: Cohort checklist */
.cohorts-header-actions {
  display: flex;
  gap: var(--sb-space-2);
  align-items: center;
  margin-bottom: var(--sb-space-3);
  font-size: var(--sb-text-xs);
}

.action-link-btn {
  background: transparent;
  border: none;
  color: var(--sb-color-brand);
  font-weight: var(--sb-weight-bold);
  cursor: pointer;
  padding: 2px 4px;
  font: inherit;
  font-size: var(--sb-text-xs);
  outline: none;
}

.action-link-btn:hover {
  text-decoration: underline;
}

.bullet-divider {
  color: var(--sb-border-hover);
}

.cohorts-selection-list {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.cohort-checkbox-card {
  display: flex;
  gap: var(--sb-space-4);
  align-items: flex-start;
  padding: var(--sb-space-4);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-lg);
  background: var(--sb-surface-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.cohort-checkbox-card:hover {
  border-color: var(--sb-border-hover);
}

.cohort-checkbox-card.checked {
  border-color: var(--sb-color-brand);
  background: var(--sb-bg-card);
  box-shadow: var(--sb-shadow-sm);
}

.premium-checkbox {
  width: 18px;
  height: 18px;
  border-radius: var(--sb-radius-sm);
  border: 2px solid var(--sb-border-hover);
  accent-color: var(--sb-color-brand);
  margin-top: 3px;
}

.cohort-text-block {
  flex: 1;
}

.cohort-title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
  gap: var(--sb-space-2);
  margin-bottom: var(--sb-space-1);
}

.cohort-label {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
}

.archetypes-list-hint {
  font-family: var(--sb-font-mono);
  font-size: 0.65rem;
  color: var(--sb-text-hint);
  font-weight: var(--sb-weight-semibold);
}

.cohort-desc {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  margin: 0 0 var(--sb-space-2) 0;
  line-height: var(--sb-leading-normal);
}

.cohort-typical-quote {
  margin: 0;
  padding-left: var(--sb-space-3);
  border-left: 2px solid var(--sb-border-hover);
  font-style: italic;
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  line-height: var(--sb-leading-normal);
}

/* Collapsed Advanced settings block */
.advanced-settings-details {
  border: 1px solid var(--sb-border-color);
  background: var(--sb-bg-card);
  padding: 0 !important;
  overflow: hidden;
}

.advanced-summary-title {
  padding: var(--sb-space-4) var(--sb-space-6);
  cursor: pointer;
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-muted);
  user-select: none;
  outline: none;
}

.advanced-summary-title:hover {
  background: var(--sb-surface-primary);
  color: var(--sb-text-main);
}

.advanced-summary-title::-webkit-details-marker {
  color: var(--sb-color-brand);
}

.advanced-settings-body {
  padding: var(--sb-space-6);
  border-top: 1px solid var(--sb-border-color);
  background: var(--sb-surface-primary);
}

.advanced-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--sb-space-5);
}

.advanced-field {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-1);
}

.advanced-field label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--sb-space-3);
}

.advanced-label-text {
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-muted);
}

.advanced-hint-text {
  font-size: 0.68rem;
  color: var(--sb-text-hint);
  line-height: var(--sb-leading-normal);
}

/* Sidebar Column Styles */
.status-column {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-6);
}

/* Privacy Panel colors override */
.privacy-status-block {
  border-radius: var(--sb-radius-lg);
  padding: var(--sb-space-4);
  margin-bottom: var(--sb-space-5);
  border-left: 5px solid var(--sb-border-hover);
}

.privacy-status-block.local_only {
  background: var(--sb-privacy-local-bg);
  border-color: var(--sb-color-ready);
}

.privacy-status-block.hybrid_safe {
  background: var(--sb-privacy-hybrid-bg);
  border-color: var(--sb-color-mixed);
}

.privacy-status-block.cloud_quality {
  background: var(--sb-privacy-cloud-bg);
  border-color: var(--sb-color-info);
}

.privacy-header-row {
  display: flex;
  gap: var(--sb-space-3);
  align-items: flex-start;
  margin-bottom: var(--sb-space-2);
}

.lock-symbol {
  font-size: 1.4rem;
}

.privacy-header-row strong {
  display: block;
  font-size: var(--sb-text-sm);
  color: var(--sb-text-heading);
}

.privacy-cost-tag {
  font-family: var(--sb-font-mono);
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  text-transform: uppercase;
  display: inline-block;
  padding: 1px 6px;
  border-radius: var(--sb-radius-sm);
  background: rgba(0,0,0,0.06);
  margin-top: 2px;
}

.privacy-explanation-text {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-body);
  line-height: var(--sb-leading-relaxed);
  margin: 0 0 var(--sb-space-3) 0;
}

.leakage-assurance {
  font-size: 0.72rem;
  color: var(--sb-text-muted);
}

.leakage-assurance strong {
  color: var(--sb-text-heading);
}

.connection-matrix h4 {
  font-size: 0.72rem;
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-hint);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 var(--sb-space-3) 0;
}

.matrix-grid {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: var(--sb-border-color);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-lg);
  overflow: hidden;
}

.matrix-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--sb-space-3) var(--sb-space-4);
  font-size: var(--sb-text-xs);
  background: var(--sb-bg-card);
}

.svc-name {
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-muted);
}

.svc-status {
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: var(--sb-radius-sm);
}

.svc-status.online,
.svc-status.connected { background: var(--sb-status-ok-bg); color: var(--sb-status-ok-text); }
.svc-status.offline { background: var(--sb-status-error-bg); color: var(--sb-status-error-text); }
.svc-status.disabled,
.svc-status.bypassed { background: var(--sb-surface-secondary); color: var(--sb-text-hint); }
.svc-status.checking { background: var(--sb-status-warn-bg); color: var(--sb-status-warn-text); }

/* Run metrics card */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--sb-space-4);
  margin-bottom: var(--sb-space-5);
}

.metric-block {
  border: 1px solid var(--sb-border-color);
  background: var(--sb-surface-primary);
  border-radius: var(--sb-radius-lg);
  padding: var(--sb-space-4);
  text-align: center;
}

.metric-lbl {
  display: block;
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-hint);
  letter-spacing: 0.5px;
  margin-bottom: var(--sb-space-1);
}

.metric-val {
  font-size: var(--sb-text-lg);
  font-weight: var(--sb-weight-extrabold);
  color: var(--sb-text-heading);
}

.metric-val.highlight-orange {
  color: var(--sb-color-brand);
}

.simulation-detail-summary {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
  margin-bottom: var(--sb-space-5);
  border-top: 1px solid var(--sb-border-color);
  padding-top: var(--sb-space-4);
  font-size: var(--sb-text-xs);
}

.summary-line {
  display: flex;
  justify-content: space-between;
}

.summary-line span {
  color: var(--sb-text-hint);
}

.summary-line strong {
  color: var(--sb-text-heading);
}

.privacy-text-class {
  color: var(--sb-color-brand);
}

.alert-banners-stack {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
  margin-bottom: var(--sb-space-5);
}

.setup-warning-banner {
  display: flex;
  gap: var(--sb-space-3);
  padding: var(--sb-space-3);
  background: var(--sb-status-warn-bg);
  border: 1px solid var(--sb-color-mixed);
  border-radius: var(--sb-radius-md);
  align-items: flex-start;
}

.warning-icon {
  font-size: 1rem;
  margin-top: 1px;
}

.warning-message {
  font-size: var(--sb-text-xs);
  color: var(--sb-status-warn-text);
  line-height: var(--sb-leading-normal);
  margin: 0;
}

.trigger-action-block {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.run-simulation-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--sb-space-3);
}

.run-simulation-btn:disabled {
  opacity: 0.65;
}

.cancel-setup-btn {
  text-align: center;
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
