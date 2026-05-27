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
        <main class="progress-card" aria-live="polite" role="region" aria-label="Simulation Steps Progress">
          <header class="progress-header">
            <h2>Workflow Progress</h2>
            <span class="total-time-badge">Total Time: {{ formatTime(overallElapsed) }}</span>
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
                    class="ghost-btn sm retry-btn-sm" 
                    @click="triggerRun"
                    aria-label="Retry simulation run"
                  >
                    🔄 Retry Simulation Run
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>

        <!-- Right Side: Run Metrics & Logs Feed -->
        <aside class="sidebar-column">
          <!-- Control Actions Panel -->
          <section class="setup-card controls-card">
            <h3>Simulation Controls</h3>
            
            <div class="controls-grid">
              <button
                type="button"
                class="ghost-btn control-btn"
                :disabled="!isCancellable"
                @click="cancelSimulation"
                aria-label="Cancel active simulation run"
              >
                ⏹ Cancel
              </button>

              <button
                type="button"
                class="ghost-btn control-btn"
                disabled
                v-tooltip="'Pause/Resume is not supported in local offline mode.'"
                aria-label="Pause simulation (Not supported)"
              >
                ⏸ Pause
              </button>

              <button
                type="button"
                class="ghost-btn control-btn"
                disabled
                v-tooltip="'Pause/Resume is not supported in local offline mode.'"
                aria-label="Resume simulation (Not supported)"
              >
                ▶ Resume
              </button>
            </div>

            <!-- Recovery Buttons if failed or finished -->
            <div v-if="executionFinished || executionFailed" class="recovery-actions-block">
              <button
                v-if="executionFailed"
                type="button"
                class="primary-btn run-btn"
                @click="triggerRun"
              >
                🔄 Restart Simulation Swarm
              </button>
              
              <button
                type="button"
                class="ghost-btn adjust-btn"
                @click="goToSetup"
              >
                ⚙ Adjust Swarm Settings
              </button>
            </div>
          </section>

          <!-- Rolling Live Logs Feed Panel -->
          <section class="setup-card logs-card" v-if="logsVisible">
            <div class="logs-header-row">
              <h3>Live Console Logs</h3>
              <button 
                type="button" 
                class="ghost-btn xs toggle-logs-btn" 
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
            class="ghost-btn show-logs-trigger-btn" 
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
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
const executionFinished = ref(ref(false))

const overallElapsed = ref(0)
const activeStepNum = ref(1)
const logsVisible = ref(true)
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
    addLogLine(`Compiling synthetic ${plat} post artifact for ${randomName()}...`)
  } else if (stepNum === 5 && Math.random() < 0.3) {
    addLogLine(`Peer-interaction pass: ${randomName()} replied to a platform post`)
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
  padding-bottom: 40px;
}

.run-layout {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 24px;
}

/* Stepper progress card */
.progress-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-header h2 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.total-time-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 700;
  background: #f1f5f9;
  color: #475569;
  padding: 4px 10px;
  border-radius: 6px;
}

/* Progress bar filling */
.progress-bar-container {
  height: 24px;
  background: #f1f5f9;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6a00, #ff4500);
  position: absolute;
  left: 0;
  top: 0;
  transition: width 0.2s linear;
}

.progress-text-label {
  position: relative;
  z-index: 2;
  font-size: 0.78rem;
  font-weight: 800;
  color: #0f172a;
  text-shadow: 0 0 2px #ffffff;
}

/* Stepper list styles */
.stepper-list {
  display: flex;
  flex-direction: column;
}

.step-row {
  display: flex;
  gap: 16px;
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
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 800;
  font-size: 0.8rem;
  background: #f1f5f9;
  color: #94a3b8;
  border: 1px solid #e2e8f0;
}

.step-line {
  width: 2px;
  background: #e2e8f0;
  flex: 1;
  min-height: 48px;
  margin: 4px 0;
}

.step-content-col {
  flex: 1;
  padding-bottom: 24px;
}

.step-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.step-title-row h3 {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
  color: #64748b;
}

.step-timer-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 600;
}

.step-desc {
  font-size: 0.82rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.4;
}

/* Active and Status modifiers */
.step-row.running .step-icon-badge {
  background: #ffebdf;
  color: #ff4500;
  border-color: #ff4500;
}

.step-row.running .step-title-row h3 {
  color: #ff4500;
  font-weight: 800;
}

.step-row.running .step-desc {
  color: #475569;
}

.step-row.running .step-timer-val {
  color: #ff4500;
}

.step-row.done .step-icon-badge {
  background: #e6fbf3;
  color: #10b981;
  border-color: #10b981;
}

.step-row.done .step-title-row h3 {
  color: #0f172a;
}

.step-row.done .step-desc {
  color: #64748b;
}

.step-row.done .step-line {
  background: #10b981;
}

.step-row.failed .step-icon-badge {
  background: #fee2e2;
  color: #ef4444;
  border-color: #ef4444;
}

.step-row.failed .step-title-row h3 {
  color: #ef4444;
}

.step-row.failed .step-desc {
  color: #7f1d1d;
}

.step-row.failed .step-timer-val {
  color: #ef4444;
}

.pulsing-bullet {
  animation: pulse 1s infinite alternate;
}

@keyframes pulse {
  from { opacity: 0.5; }
  to { opacity: 1; }
}

.step-retry-block {
  margin-top: 8px;
}

.retry-btn-sm {
  border-color: #ef4444;
  color: #ef4444;
  font-weight: 700;
}

.retry-btn-sm:hover {
  background: #fee2e2;
}

/* Sidebar Columns Styles */
.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.setup-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.setup-card h3 {
  font-size: 0.95rem;
  font-weight: 800;
  margin: 0 0 16px 0;
  color: #0f172a;
}

.controls-grid {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.control-btn {
  flex: 1;
  padding: 10px;
  font-size: 0.8rem;
  font-weight: 700;
  text-align: center;
  border-radius: 8px;
}

.recovery-actions-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
  margin-top: 16px;
}

.recovery-actions-block button {
  width: 100%;
  padding: 12px;
  font-size: 0.85rem;
  font-weight: 700;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
}

.adjust-btn:hover {
  background: #f8fafc;
}

/* Terminal Console logs styles */
.logs-card {
  display: flex;
  flex-direction: column;
  background: #0f172a;
  color: #f1f5f9;
  border-color: #1e293b;
}

.logs-card h3 {
  color: #f1f5f9;
  margin: 0;
}

.logs-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.toggle-logs-btn {
  border-color: #334155;
  color: #94a3b8;
  padding: 4px 8px;
  font-size: 0.7rem;
  border-radius: 4px;
}

.toggle-logs-btn:hover {
  background: #1e293b;
  color: #ffffff;
}

.console-terminal {
  background: #020617;
  border: 1px solid #1e293b;
  border-radius: 6px;
  height: 320px;
  overflow-y: auto;
  padding: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  line-height: 1.4;
}

.terminal-line {
  margin-bottom: 6px;
  word-break: break-all;
}

.terminal-line.success { color: #10b981; }
.terminal-line.warning { color: #f59e0b; }
.terminal-line.error { color: #ef4444; }
.terminal-line.info { color: #38bdf8; }

.timestamp {
  color: #475569;
  margin-right: 6px;
}

.empty-terminal-text {
  color: #475569;
  font-style: italic;
  text-align: center;
  padding-top: 140px;
}

.show-logs-trigger-btn {
  width: 100%;
  padding: 12px;
  font-weight: 700;
  border-radius: 8px;
  font-size: 0.82rem;
  border-color: #cbd5e1;
}

.show-logs-trigger-btn:hover {
  background: #f8fafc;
}

@media (max-width: 950px) {
  .run-layout {
    grid-template-columns: 1fr;
  }
}
</style>
