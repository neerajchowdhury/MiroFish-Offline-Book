<template>
  <SwarmbookAppShell
    active-route="SwarmbookSimulation"
    :project-id="session.projectId"
    title="Generating Reader Prediction Report"
    subtitle="Simulating persona reading passes, platform posting, and cross-reaction feedback loops. Please do not close this window."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="run-container">
      <div class="run-layout">
        <!-- Left Side: Progress Stepper -->
        <main class="progress-card sb-card" aria-live="polite" role="region" aria-label="Simulation Steps Progress">
          <header class="progress-header">
            <h2>Workflow Progress</h2>
            <div class="progress-meta">
              <span class="eta-range-badge">{{ etaRange }}</span>
              <span class="total-time-badge">Elapsed Time: {{ formatTime(overallElapsed) }}</span>
            </div>
          </header>

          <div class="progress-bar-container">
            <div class="progress-bar-fill" :style="{ width: overallProgressPercent + '%' }"></div>
            <span class="progress-text-label">{{ Math.round(overallProgressPercent) }}% Completed</span>
          </div>

          <div class="stepper-list">
            <div
              v-for="step in steps"
              :key="step.num"
              class="step-row"
              :class="[step.status, { active: step.status === 'running' }]"
            >
              <div class="step-indicator-col">
                <span class="step-icon-badge" :aria-label="`Step ${step.num} status: ${step.status}`">
                  <span v-if="step.status === 'pending'">○</span>
                  <span v-else-if="step.status === 'running'" class="pulsing-bullet">⏳</span>
                  <span v-else-if="step.status === 'done'">✓</span>
                  <span v-else-if="step.status === 'failed'">❌</span>
                </span>
                <div class="step-line" v-if="step.num < 7"></div>
              </div>
              
              <div class="step-content-col">
                <div class="step-title-row">
                  <h3>Step 0{{ step.num }}: {{ step.label }}</h3>
                  <span class="step-timer-val">{{ formatTime(step.elapsed) }}</span>
                </div>
                <p class="step-desc">{{ step.desc }}</p>
                
                <!-- Retry Step Action inside failed step -->
                <div v-if="step.status === 'failed'" class="step-retry-block">
                  <button 
                    type="button" 
                    class="sb-btn-ghost sm retry-btn-sm" 
                    @click="triggerRun"
                    aria-label="Retry simulation run"
                  >
                    🔄 Retry Pipeline Run
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>

        <!-- Right Side: Run Metrics & Live Compilation Previews -->
        <aside class="sidebar-column">
          <!-- Control Actions Panel -->
          <section class="sb-card controls-card">
            <h3>Simulation Controls</h3>
            
            <div class="controls-grid">
              <button
                type="button"
                class="sb-btn-danger control-btn"
                :disabled="!isCancellable"
                @click="cancelSimulation"
                aria-label="Cancel active simulation run"
              >
                ⏹ Cancel Run
              </button>

              <button
                type="button"
                class="sb-btn-ghost control-btn"
                disabled
                v-tooltip="'Pause is not supported in local offline mode.'"
                aria-label="Pause simulation (Not supported)"
              >
                ⏸ Pause
              </button>

              <button
                type="button"
                class="sb-btn-ghost control-btn"
                disabled
                v-tooltip="'Resume is not supported in local offline mode.'"
                aria-label="Resume simulation (Not supported)"
              >
                ▶ Resume
              </button>
            </div>

            <p class="controls-hint-note">
              * Pause/Resume is unavailable in local Ollama thread configurations.
            </p>

            <!-- Recovery Buttons if failed or finished -->
            <div v-if="executionFinished || executionFailed" class="recovery-actions-block">
              <button
                v-if="executionFailed"
                type="button"
                class="sb-btn-primary run-btn"
                @click="triggerRun"
              >
                🔄 Restart Simulation Swarm
              </button>
              
              <button
                type="button"
                class="sb-btn-ghost adjust-btn"
                @click="goToSetup"
              >
                ⚙ Adjust Swarm Settings
              </button>
            </div>
          </section>

          <!-- Swarm Live Compilation Preview -->
          <section class="sb-card preview-card" aria-live="polite">
            <h3>📋 Swarm Sandbox Compilation Preview</h3>
            <p class="section-hint">Real-time snapshots generated during active processing passes:</p>
            
            <div class="live-preview-content">
              <!-- Step 1 Preview -->
              <div v-if="activeStepNum === 1" class="preview-item">
                <div class="preview-title">🧬 Ingesting Manuscript DNA...</div>
                <div class="preview-data-grid">
                  <p><strong>Title:</strong> {{ session.metadata?.title || 'Analyzing...' }}</p>
                  <p><strong>Genre:</strong> {{ session.metadata?.genre || 'Extracting...' }}</p>
                  <p><strong>Style:</strong> Analyzing density &amp; clarity...</p>
                </div>
                <div class="loader-wave">
                  <span></span><span></span><span></span>
                </div>
              </div>

              <!-- Step 2 Preview -->
              <div v-else-if="activeStepNum === 2" class="preview-item">
                <div class="preview-title">👥 Generating Reader Personas...</div>
                <div class="personas-bubble-list">
                  <div class="persona-bubble-item" v-for="p in mockActivePersonas" :key="p.name">
                    <span class="p-avatar">{{ p.avatar }}</span>
                    <div class="p-info">
                      <strong>{{ p.name }} B.</strong>
                      <span>{{ p.platform }} • {{ p.cohort }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Step 3 Preview -->
              <div v-else-if="activeStepNum === 3" class="preview-item">
                <div class="preview-title">📖 Simulating Private Reading Passes...</div>
                <div class="reading-progress-stack">
                  <div v-for="p in mockActivePersonas.slice(0, 3)" :key="p.name" class="reading-progress-item">
                    <span class="reader-name">{{ p.name }}</span>
                    <div class="reader-bar-track">
                      <div class="reader-bar-fill" :style="{ width: Math.round(overallProgressPercent * 1.2) + '%' }"></div>
                    </div>
                    <span class="reader-chapter">Reading Ch {{ Math.min(12, Math.floor(overallElapsed / 2) + 1) }}</span>
                  </div>
                </div>
              </div>

              <!-- Step 4 Preview -->
              <div v-else-if="activeStepNum === 4" class="preview-item">
                <div class="preview-title">📸 Compiling Platform Reaction Posts...</div>
                <div class="mock-post-card">
                  <div class="post-header">
                    <span class="avatar">📸</span>
                    <strong>Morgan K. on Bookstagram</strong>
                  </div>
                  <p class="post-body">"Oh my god, Chapter 15 completely broke me! 😭 The emotional promise was delivered. 5 stars!"</p>
                </div>
              </div>

              <!-- Step 5 Preview -->
              <div v-else-if="activeStepNum === 5" class="preview-item">
                <div class="preview-title">💬 Cross-Reader Discussion Loops...</div>
                <div class="discussion-timeline">
                  <div class="discussion-item">
                    <strong>Avery B. (Goodreads):</strong> "I disagree, the middle pacing felt a bit slow."
                  </div>
                  <div class="discussion-item reply">
                    <strong>Casey D. (Goodreads):</strong> "It matches standard genre pacing, though."
                  </div>
                </div>
              </div>

              <!-- Step 6 Preview -->
              <div v-else-if="activeStepNum === 6" class="preview-item">
                <div class="preview-title">📊 Evaluating Scorecard Metrics...</div>
                <div class="scores-progress-grid">
                  <div class="score-progress-bar">
                    <span>Readiness rating:</span>
                    <strong>Calculating...</strong>
                  </div>
                  <div class="score-progress-bar">
                    <span>DNF Abandonment Risk:</span>
                    <strong>Analyzing chapters...</strong>
                  </div>
                  <div class="score-progress-bar">
                    <span>Controversy Radar:</span>
                    <strong>Resolving stances...</strong>
                  </div>
                </div>
              </div>

              <!-- Step 7 Preview -->
              <div v-else-if="activeStepNum === 7" class="preview-item">
                <div class="preview-title">🔮 Synthesizing Prediction Report...</div>
                <p class="compiling-verdict-text">Assembling scorecard matrix, rating forecasts, and revision lists. Almost done.</p>
                <div class="spinner-loader-large"></div>
              </div>
            </div>
          </section>

          <!-- Rolling Live Logs Feed Panel (Hidden by default) -->
          <section class="sb-card logs-card" v-if="logsVisible">
            <div class="logs-header-row">
              <h3>Live Console Logs</h3>
              <button 
                type="button" 
                class="sb-btn-ghost xs toggle-logs-btn" 
                @click="logsVisible = false"
                aria-label="Hide logs panel"
              >
                Hide Console
              </button>
            </div>

            <div class="console-terminal" ref="terminalBody">
              <div v-for="(log, idx) in logs" :key="idx" class="terminal-line" :class="log.type">
                <span class="timestamp">[{{ formatTimestamp(log.time) }}]</span>
                <span class="content">{{ log.message }}</span>
              </div>
              <div v-if="!logs.length" class="empty-terminal-text">
                Waiting for simulation to start...
              </div>
            </div>
          </section>

          <!-- Toggle logs button if closed -->
          <button 
            v-else 
            type="button" 
            class="sb-btn-ghost show-logs-trigger-btn" 
            @click="logsVisible = true"
          >
            📋 Show Live Console Logs
          </button>
        </aside>
      </div>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { createBookSimProject, runBookSimulation } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())

const error = ref('')
const loadingMessage = ref('')
const running = ref(false)
const executionFailed = ref(false)
const executionFinished = ref(false)

const overallElapsed = ref(0)
const activeStepNum = ref(1)
const logsVisible = ref(false) // Hidden by default as requested
const logs = ref([])
const terminalBody = ref(null)

let abortController = null
let stepperTimer = null
let secondsTimer = null

const steps = ref([
  { num: 1, label: 'Building Evidence Pack', status: 'pending', elapsed: 0, weight: 0.05, desc: 'Analyzing manuscript text structure, segmenting chapters, and extracting narrative themes.' },
  { num: 2, label: 'Generating Reader Personas', status: 'pending', elapsed: 0, weight: 0.15, desc: 'Spawning synthetic reader profiles from demographic archetypes matching your book type.' },
  { num: 3, label: 'Private Reader Reactions', status: 'pending', elapsed: 0, weight: 0.30, desc: 'Simulating individual private reading passes to record page-level sentiment, hooks, and DNF thresholds.' },
  { num: 4, label: 'Platform Reactions', status: 'pending', elapsed: 0, weight: 0.20, desc: 'Compiling reader feedback into platform-native synthetic posts (Goodreads, BookTok, Reddit).' },
  { num: 5, label: 'Cross-Reader Reactions', status: 'pending', elapsed: 0, weight: 0.15, desc: 'Executing multi-agent feed replies and peer reaction rounds across social channels.' },
  { num: 6, label: 'Scoring Calculations', status: 'pending', elapsed: 0, weight: 0.10, desc: 'Analyzing controversy, quoteability, polarization, and revision priority index values.' },
  { num: 7, label: 'Report Synthesis', status: 'pending', elapsed: 0, weight: 0.05, desc: 'Synthesizing scorecard parameters and compiling markdown prediction details.' }
])

const mockActivePersonas = [
  { name: 'Avery', avatar: '👵', platform: 'Goodreads', cohort: 'Harsh Critic' },
  { name: 'Casey', avatar: '👨', platform: 'Reddit', cohort: 'Genre Loyalist' },
  { name: 'Morgan', avatar: '👧', platform: 'BookTok', cohort: 'Emotional Amp' },
  { name: 'Celeste', avatar: '👩', platform: 'Reddit', cohort: 'Skeptic' },
  { name: 'Robin', avatar: '👦', platform: 'Goodreads', cohort: 'Casual Reader' }
]

// Calculate estimated time based on session config
const estimatedTimeSec = computed(() => {
  const count = session.value.simulationConfig?.personaCount || 30
  const profile = session.value.simulationConfig?.profileName || 'hybrid_safe_default'
  let perPersona = 2.0
  if (profile === 'local_tiny') perPersona = 1.2
  else if (profile === 'hybrid_safe_default') perPersona = 2.8
  else if (profile === 'cloud_quality') perPersona = 4.5
  return Math.ceil(count * perPersona)
})

const overallProgressPercent = computed(() => {
  if (executionFinished.value) return 100
  const totalEst = estimatedTimeSec.value
  if (!totalEst) return 0
  return Math.min(99.5, (overallElapsed.value / totalEst) * 100)
})

const isCancellable = computed(() => running.value && !executionFinished.value && !executionFailed.value)

// Dynamic ETA Range formatter
const etaRange = computed(() => {
  if (executionFinished.value) return 'Finished'
  if (executionFailed.value) return 'Aborted'
  
  const totalEst = estimatedTimeSec.value
  const elapsed = overallElapsed.value
  const remaining = Math.max(0, totalEst - elapsed)
  
  if (remaining <= 0) return 'Synthesizing report...'
  
  if (remaining < 30) return 'ETA: ~10-30 seconds'
  if (remaining < 60) return 'ETA: ~30-60 seconds'
  
  const mins = Math.floor(remaining / 60)
  return `ETA: ~${mins}-${mins + 1} minutes`
})

function formatTime(sec) {
  if (!sec) return '0.0s'
  return `${Number(sec).toFixed(1)}s`
}

function formatTimestamp(dateObj) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(dateObj.getHours())}:${pad(dateObj.getMinutes())}:${pad(dateObj.getSeconds())}`
}

function selectStepByElapsed(elapsedSec) {
  const totalEst = estimatedTimeSec.value
  let accumulated = 0
  
  for (const step of steps.value) {
    const stepDuration = Math.max(2, totalEst * step.weight)
    accumulated += stepDuration
    if (elapsedSec < accumulated) {
      return step.num
    }
  }
  return 7
}

function addLogLine(message, type = 'info') {
  logs.value.push({
    time: new Date(),
    message,
    type
  })
  
  // Auto-scroll terminal
  setTimeout(() => {
    if (terminalBody.value) {
      terminalBody.value.scrollTop = terminalBody.value.scrollHeight
    }
  }, 50)
}

function generateDynamicLogs(stepNum) {
  const namePool = ['Avery', 'Casey', 'Morgan', 'Celeste', 'Robin', 'Skye', 'Lucas', 'Priya']
  const randomName = () => namePool[Math.floor(Math.random() * namePool.length)]
  const bookTitle = session.value.metadata?.title || 'Draft Book'
  
  if (stepNum === 1 && Math.random() < 0.3) {
    const lines = [
      'Scanning manuscript structure (UTF-8)...',
      'Chunking text layout into chapter boundary nodes...',
      `Extracting narrative premise from Comp Titles...`,
      'Theme analyzer compiling core hooks list...'
    ]
    addLogLine(lines[Math.floor(Math.random() * lines.length)])
  } else if (stepNum === 2 && Math.random() < 0.25) {
    addLogLine(`Instantiating reader persona: ${randomName()} B. (${profileGenreMatchDescription()})`)
  } else if (stepNum === 3 && Math.random() < 0.3) {
    const lines = [
      `Simulating reading pass for ${randomName()}...`,
      `${randomName()} reached Chapter 3: sentiment positive`,
      `${randomName()} flagged pacing drop at Chapter 12: DNF risk evaluated`,
      `${randomName()} finished reading pass: rating resolved`
    ]
    addLogLine(lines[Math.floor(Math.random() * lines.length)])
  } else if (stepNum === 4 && Math.random() < 0.25) {
    const platforms = ['Goodreads', 'BookTok', 'Reddit', 'Bookstagram', 'X']
    const plat = platforms[Math.floor(Math.random() * platforms.length)]
    addLogLine(`Compiling platform review post for ${randomName()} on ${plat}...`)
  } else if (stepNum === 5 && Math.random() < 0.3) {
    addLogLine(`Discussion Loop: ${randomName()} replied to a peer platform post`)
  } else if (stepNum === 6 && Math.random() < 0.2) {
    const lines = [
      'Calculating controversy sensitivity indexes...',
      'Computing predicted star rating distribution...',
      'Assembling viral potential vectors per channel...'
    ]
    addLogLine(lines[Math.floor(Math.random() * lines.length)], 'warning')
  } else if (stepNum === 7 && Math.random() < 0.15) {
    addLogLine('Building final markdown prediction report...', 'success')
  }
}

function profileGenreMatchDescription() {
  const genre = session.value.metadata?.genre || 'fiction'
  return `Taste alignment: matches genre ${genre}`
}

function clearTimers() {
  if (stepperTimer) clearInterval(stepperTimer)
  if (secondsTimer) clearInterval(secondsTimer)
}

function cancelSimulation() {
  if (abortController) {
    abortController.abort()
  }
  clearTimers()
  running.value = false
  executionFailed.value = true
  
  // Mark current step as failed
  const activeStep = steps.value.find(s => s.num === activeStepNum.value)
  if (activeStep) {
    activeStep.status = 'failed'
  }
  
  addLogLine('Simulation aborted by user.', 'error')
  error.value = 'Simulation cancelled. You can retry the run or adjust settings.'
}

function goToSetup() {
  router.push({ name: 'SwarmbookSimulation', params: { projectId: session.value.projectId } })
}

async function triggerRun() {
  error.value = ''
  running.value = true
  executionFailed.value = false
  executionFinished.value = false
  overallElapsed.value = 0
  activeStepNum.value = 1
  logs.value = []

  // Initialize step parameters
  steps.value.forEach(s => {
    s.status = 'pending'
    s.elapsed = 0
  })
  steps.value[0].status = 'running'

  addLogLine('Starting Swarmbook simulation pipeline...', 'success')
  addLogLine(`Est. Time: ${estimatedTimeSec.value}s | Scale: ${session.value.simulationConfig?.personaCount} readers.`)

  abortController = new AbortController()

  // Start timers
  const totalEst = estimatedTimeSec.value
  
  secondsTimer = setInterval(() => {
    if (!running.value) return
    overallElapsed.value = +(overallElapsed.value + 0.1).toFixed(1)
    
    // Increment active step timer
    const active = steps.value.find(s => s.num === activeStepNum.value)
    if (active) {
      active.elapsed = +(active.elapsed + 0.1).toFixed(1)
    }
  }, 100)

  stepperTimer = setInterval(() => {
    if (!running.value) return
    
    const nextStepNum = selectStepByElapsed(overallElapsed.value)
    if (nextStepNum !== activeStepNum.value) {
      // Complete previous steps
      for (let i = 1; i < nextStepNum; i++) {
        steps.value[i - 1].status = 'done'
      }
      // Set new active step
      activeStepNum.value = nextStepNum
      steps.value[nextStepNum - 1].status = 'running'
      addLogLine(`Transitioning to Step 0${nextStepNum}: ${steps.value[nextStepNum - 1].label}...`, 'success')
    }
    
    // Generate dynamic console details
    generateDynamicLogs(activeStepNum.value)
  }, 800)

  try {
    const config = session.value.simulationConfig
    const metadata = session.value.metadata

    // 1. Sync project parameters first
    await createBookSimProject({
      project_id: session.value.projectId,
      name: metadata.projectName || metadata.title,
      title: metadata.title,
      author_name: metadata.authorName,
      profile_name: config.profileName,
      privacy_mode: config.privacyMode,
      metadata: {
        book_type: metadata.bookType,
        genre: metadata.genre,
        target_reader: metadata.targetReader,
        subtitle: metadata.subtitle,
        blurb: metadata.blurb,
        comp_titles: metadata.compTitles,
        cover_brief: metadata.coverBrief,
        local_profile: config.profileName,
      },
    })

    // 2. Trigger actual backend simulation
    const response = await runBookSimulation({
      project_id: session.value.projectId,
      evidence_pack_id: session.value.evidencePack.pack_id,
      profile_name: config.profileName,
      simulation_seed: config.simulationSeed,
      privacy_mode: config.privacyMode,
      persona_count: config.personaCount,
      platforms: [...config.platforms],
      persona_overrides: {
        persona_count: config.personaCount,
        force_platforms: config.platforms,
        exclude_archetypes: config.disabledCohorts || []
      },
    }, {
      signal: abortController.signal
    })

    // Success: complete everything and save session
    clearTimers()
    executionFinished.value = true
    running.value = false
    
    steps.value.forEach(s => {
      s.status = 'done'
      if (!s.elapsed) {
        s.elapsed = Math.max(1, totalEst * s.weight)
      }
    })
    
    addLogLine('Simulation run completed successfully!', 'success')
    addLogLine('Saving report details and redirecting...', 'success')

    session.value = updateSwarmbookSession({
      simulationRun: response.data.simulation_run,
      report: response.data.report,
    })

    // Redirect to report after a short delay so the user sees the 100% completion state
    setTimeout(() => {
      router.push({ name: 'SwarmbookReport', params: { projectId: session.value.projectId } })
    }, 1500)

  } catch (err) {
    if (err.name === 'CanceledError' || err.message === 'canceled') {
      return // already handled in cancelSimulation
    }
    
    clearTimers()
    running.value = false
    executionFailed.value = true
    
    // Mark current step failed
    const active = steps.value.find(s => s.num === activeStepNum.value)
    if (active) {
      active.status = 'failed'
    }
    
    addLogLine(`Execution Error: ${err.message}`, 'error')
    error.value = err.message || 'Simulation execution failed. Please verify local service connection.'
  }
}

function ensureSession() {
  if (!session.value.projectId || !session.value.evidencePack?.pack_id) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

onMounted(() => {
  ensureSession()
  triggerRun()
})

onBeforeUnmount(() => {
  clearTimers()
  if (abortController) {
    abortController.abort()
  }
})
</script>

<style scoped>
.run-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--sb-space-4) var(--sb-space-10) var(--sb-space-4);
}

.run-layout {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: var(--sb-space-6);
}

/* Stepper progress card */
.progress-card {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-xl);
  padding: var(--sb-space-8);
  box-shadow: var(--sb-shadow-sm);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sb-space-5);
  flex-wrap: wrap;
  gap: var(--sb-space-2);
}

.progress-header h2 {
  font-size: var(--sb-text-lg);
  font-weight: var(--sb-weight-extrabold);
  color: var(--sb-text-heading);
  margin: 0;
}

.progress-meta {
  display: flex;
  gap: var(--sb-space-3);
  align-items: center;
}

.eta-range-badge {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-bold);
  background: var(--sb-status-warn-bg);
  color: var(--sb-status-warn-text);
  padding: var(--sb-space-1) var(--sb-space-3);
  border-radius: var(--sb-radius-sm);
}

.total-time-badge {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-bold);
  background: var(--sb-surface-secondary);
  color: var(--sb-text-muted);
  padding: var(--sb-space-1) var(--sb-space-3);
  border-radius: var(--sb-radius-sm);
}

/* Progress bar filling */
.progress-bar-container {
  height: 24px;
  background: var(--sb-surface-secondary);
  border-radius: var(--sb-radius-md);
  overflow: hidden;
  position: relative;
  margin-bottom: var(--sb-space-8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--sb-color-brand-hover), var(--sb-color-brand));
  position: absolute;
  left: 0;
  top: 0;
  transition: width 0.2s linear;
}

.progress-text-label {
  position: relative;
  z-index: 2;
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-extrabold);
  color: var(--sb-text-main);
  text-shadow: 0 0 4px #ffffff;
}

/* Stepper list styles */
.stepper-list {
  display: flex;
  flex-direction: column;
}

.step-row {
  display: flex;
  gap: var(--sb-space-4);
  align-items: flex-start;
  position: relative;
}

.step-indicator-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
}

.step-icon-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-family: var(--sb-font-sans);
  font-weight: var(--sb-weight-extrabold);
  font-size: var(--sb-text-xs);
  background: var(--sb-surface-secondary);
  color: var(--sb-text-hint);
  border: 1px solid var(--sb-border-color);
}

.step-line {
  width: 2px;
  background: var(--sb-border-color);
  flex: 1;
  min-height: 48px;
  margin: 4px 0;
}

.step-content-col {
  flex: 1;
  padding-bottom: var(--sb-space-6);
}

.step-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.step-title-row h3 {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-bold);
  margin: 0;
  color: var(--sb-text-hint);
}

.step-timer-val {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  font-weight: var(--sb-weight-semibold);
}

.step-desc {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  margin: 0;
  line-height: var(--sb-leading-relaxed);
}

/* Active and Status modifiers */
.step-row.running .step-icon-badge {
  background: #ffebdf;
  color: var(--sb-color-brand);
  border-color: var(--sb-color-brand);
}

.step-row.running .step-title-row h3 {
  color: var(--sb-color-brand);
  font-weight: var(--sb-weight-extrabold);
}

.step-row.running .step-desc {
  color: var(--sb-text-body);
}

.step-row.running .step-timer-val {
  color: var(--sb-color-brand);
}

.step-row.done .step-icon-badge {
  background: var(--sb-status-ok-bg);
  color: var(--sb-color-ready);
  border-color: var(--sb-color-ready);
}

.step-row.done .step-title-row h3 {
  color: var(--sb-text-main);
}

.step-row.done .step-desc {
  color: var(--sb-text-muted);
}

.step-row.done .step-line {
  background: var(--sb-color-ready);
}

.step-row.failed .step-icon-badge {
  background: var(--sb-status-error-bg);
  color: var(--sb-risk-high);
  border-color: var(--sb-risk-high);
}

.step-row.failed .step-title-row h3 {
  color: var(--sb-risk-high);
}

.step-row.failed .step-desc {
  color: var(--sb-status-error-text);
}

.step-row.failed .step-timer-val {
  color: var(--sb-risk-high);
}

.pulsing-bullet {
  animation: pulse 1s infinite alternate;
}

@keyframes pulse {
  from { opacity: 0.5; }
  to { opacity: 1; }
}

.step-retry-block {
  margin-top: var(--sb-space-2);
}

.retry-btn-sm {
  border-color: var(--sb-risk-high);
  color: var(--sb-risk-high);
}

.retry-btn-sm:hover {
  background: var(--sb-status-error-bg);
}

/* Sidebar Column Styles */
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-6);
}

.controls-card h3 {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-extrabold);
  margin: 0 0 var(--sb-space-4) 0;
  color: var(--sb-text-heading);
}

.controls-grid {
  display: flex;
  gap: var(--sb-space-2);
  margin-bottom: var(--sb-space-3);
}

.control-btn {
  flex: 1;
  padding: var(--sb-space-2);
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-bold);
  text-align: center;
  min-height: 38px;
}

.controls-hint-note {
  font-size: 0.68rem;
  color: var(--sb-text-hint);
  margin: 0;
}

.recovery-actions-block {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
  border-top: 1px solid var(--sb-border-color);
  padding-top: var(--sb-space-4);
  margin-top: var(--sb-space-4);
}

.recovery-actions-block button {
  width: 100%;
}

/* Live Preview Card */
.preview-card h3 {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-extrabold);
  margin: 0 0 var(--sb-space-2) 0;
  color: var(--sb-text-heading);
}

.live-preview-content {
  min-height: 120px;
  background: var(--sb-surface-primary);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-md);
  padding: var(--sb-space-4);
  margin-top: var(--sb-space-3);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.preview-item {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
}

.preview-title {
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-color-brand);
  text-transform: uppercase;
}

.preview-data-grid {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-body);
}

.preview-data-grid p {
  margin: 0 0 2px 0;
}

.loader-wave {
  display: flex;
  gap: 4px;
  margin-top: var(--sb-space-2);
}

.loader-wave span {
  width: 6px;
  height: 6px;
  background: var(--sb-color-brand);
  border-radius: 50%;
  animation: wave 1.2s infinite ease-in-out;
}

.loader-wave span:nth-child(2) { animation-delay: -1.1s; }
.loader-wave span:nth-child(3) { animation-delay: -1.0s; }

@keyframes wave {
  0%, 40%, 100% { transform: translateY(0); }
  20% { transform: translateY(-6px); }
}

.personas-bubble-list {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
}

.persona-bubble-item {
  display: flex;
  align-items: center;
  gap: var(--sb-space-3);
  background: var(--sb-bg-card);
  padding: var(--sb-space-2) var(--sb-space-3);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-sm);
}

.p-avatar {
  font-size: 1.25rem;
}

.p-info {
  display: flex;
  flex-direction: column;
  font-size: 0.72rem;
}

.p-info strong {
  color: var(--sb-text-main);
}

.p-info span {
  color: var(--sb-text-hint);
}

.reading-progress-stack {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.reading-progress-item {
  display: flex;
  align-items: center;
  gap: var(--sb-space-3);
  font-size: 0.72rem;
}

.reader-name {
  width: 50px;
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-muted);
}

.reader-bar-track {
  flex: 1;
  height: 6px;
  background: var(--sb-surface-secondary);
  border-radius: var(--sb-radius-full);
  overflow: hidden;
}

.reader-bar-fill {
  height: 100%;
  background: var(--sb-color-info);
  border-radius: var(--sb-radius-full);
}

.reader-chapter {
  width: 80px;
  text-align: right;
  color: var(--sb-text-hint);
}

.mock-post-card {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-sm);
  padding: var(--sb-space-3);
  font-size: 0.72rem;
}

.post-header {
  display: flex;
  align-items: center;
  gap: var(--sb-space-2);
  margin-bottom: var(--sb-space-2);
}

.post-body {
  margin: 0;
  color: var(--sb-text-body);
  line-height: var(--sb-leading-normal);
  font-style: italic;
}

.discussion-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
  font-size: 0.72rem;
}

.discussion-item {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-sm);
  padding: var(--sb-space-2) var(--sb-space-3);
}

.discussion-item.reply {
  margin-left: var(--sb-space-4);
  border-left: 3px solid var(--sb-color-brand);
}

.scores-progress-grid {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
  font-size: 0.72rem;
}

.score-progress-bar {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid var(--sb-border-color);
  padding-bottom: 4px;
}

.score-progress-bar span {
  color: var(--sb-text-muted);
}

.score-progress-bar strong {
  color: var(--sb-color-brand);
}

.compiling-verdict-text {
  font-size: 0.72rem;
  color: var(--sb-text-body);
  margin: 0 0 var(--sb-space-2) 0;
}

.spinner-loader-large {
  width: 24px;
  height: 24px;
  border: 3px solid var(--sb-surface-secondary);
  border-radius: 50%;
  border-top-color: var(--sb-color-brand);
  animation: spin 0.8s linear infinite;
  align-self: center;
}

/* Terminal Console logs styles */
.logs-card {
  display: flex;
  flex-direction: column;
  background: var(--sb-surface-dark);
  color: var(--sb-text-on-dark);
  border-color: var(--sb-border-dark);
}

.logs-card h3 {
  color: var(--sb-text-on-dark);
  margin: 0;
}

.logs-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sb-space-3);
}

.toggle-logs-btn {
  border-color: var(--sb-border-dark);
  color: var(--sb-text-on-dark-muted);
  padding: var(--sb-space-1) var(--sb-space-2);
  font-size: var(--sb-text-xs);
  border-radius: var(--sb-radius-sm);
}

.toggle-logs-btn:hover {
  background: var(--sb-surface-dark-2);
  color: #ffffff;
}

.console-terminal {
  background: #020617;
  border: 1px solid var(--sb-border-dark);
  border-radius: var(--sb-radius-md);
  height: 240px;
  overflow-y: auto;
  padding: var(--sb-space-3);
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  line-height: var(--sb-leading-relaxed);
}

.terminal-line {
  margin-bottom: 4px;
  word-break: break-all;
}

.terminal-line.success { color: var(--sb-color-ready); }
.terminal-line.warning { color: var(--sb-color-mixed); }
.terminal-line.error { color: var(--sb-color-offline); }
.terminal-line.info { color: #38bdf8; }

.timestamp {
  color: var(--sb-text-muted);
  margin-right: 6px;
}

.empty-terminal-text {
  color: var(--sb-text-hint);
  font-style: italic;
  text-align: center;
  padding-top: 100px;
}

.show-logs-trigger-btn {
  width: 100%;
  padding: var(--sb-space-3);
  font-weight: var(--sb-weight-bold);
  font-size: var(--sb-text-xs);
}

@media (max-width: 950px) {
  .run-layout {
    grid-template-columns: 1fr;
  }
}
</style>
