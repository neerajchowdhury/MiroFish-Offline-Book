<template>
  <SwarmbookAppShell
    active-route="SwarmbookSettings"
    :project-id="projectId"
    title="Swarmbook Settings"
    subtitle="Configure the simulation privacy guardrails, workstation resource profiles, and verify local/cloud provider connection status."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <!-- Save Success Toast -->
    <transition name="fade">
      <div v-if="saveSuccess" class="toast-banner success" role="status" aria-live="polite">
        <span class="icon">✅</span> Swarmbook configurations saved and applied successfully.
      </div>
    </transition>

    <div class="settings-grid">
      <!-- Left Main Configurations -->
      <main class="settings-main-col" aria-label="Configuration Settings">
        
        <!-- 1. Privacy Mode Selection -->
        <section class="card settings-card" aria-labelledby="privacy-heading">
          <h2 id="privacy-heading">1. Simulation Privacy Guardrails</h2>
          <p class="section-desc">
            Enforces strict boundaries around data transmission. The selected privacy level determines model routing paths and blocks unauthorized cloud API requests.
          </p>

          <div class="privacy-cards-row" role="radiogroup" aria-labelledby="privacy-heading">
            <!-- local_only -->
            <button
              class="privacy-card-select"
              :class="{ selected: form.privacyMode === 'local_only' }"
              role="radio"
              :aria-checked="form.privacyMode === 'local_only'"
              @click="setPrivacyMode('local_only')"
              @keydown.enter="setPrivacyMode('local_only')"
            >
              <div class="card-header">
                <span class="badge local_only">🔒 local_only</span>
                <span class="shield-status">Strictly Offline</span>
              </div>
              <h3>Local Workstation Only</h3>
              <p class="explanation-text">
                <strong>Zero External Calls:</strong> Restricts all LLM processing to local Ollama and local Neo4j. Cloud keys are blocked. Best for confidential manuscripts.
              </p>
            </button>

            <!-- hybrid_safe -->
            <button
              class="privacy-card-select"
              :class="{ selected: form.privacyMode === 'hybrid_safe' }"
              role="radio"
              :aria-checked="form.privacyMode === 'hybrid_safe'"
              @click="setPrivacyMode('hybrid_safe')"
              @keydown.enter="setPrivacyMode('hybrid_safe')"
            >
              <div class="card-header">
                <span class="badge hybrid_safe">🛡️ hybrid_safe</span>
                <span class="shield-status">Metadata Cloud Only</span>
              </div>
              <h3>Grounded Hybrid Safe</h3>
              <p class="explanation-text">
                <strong>Summaries Only:</strong> Keeps the manuscript text offline. Cloud APIs are used only for metadata embeddings or synthesizing high-level story outline segments.
              </p>
            </button>

            <!-- cloud_quality -->
            <button
              class="privacy-card-select"
              :class="{ selected: form.privacyMode === 'cloud_quality' }"
              role="radio"
              :aria-checked="form.privacyMode === 'cloud_quality'"
              @click="setPrivacyMode('cloud_quality')"
              @keydown.enter="setPrivacyMode('cloud_quality')"
            >
              <div class="card-header">
                <span class="badge cloud_quality">✨ cloud_quality</span>
                <span class="shield-status">Advanced Quality</span>
              </div>
              <h3>Advanced Cloud Quality</h3>
              <p class="explanation-text">
                <strong>High Fidelity:</strong> Enables advanced Gemini long-context and NVIDIA NIM cloud model endpoints. Recommends full outline processing for maximum prediction depth.
              </p>
            </button>
          </div>
        </section>

        <!-- 2. Local Workstation Profiles -->
        <section class="card settings-card" aria-labelledby="profile-heading">
          <h2 id="profile-heading">2. Workstation Resource Profiles</h2>
          <p class="section-desc">
            Select a resource allocation profile. This optimizes the number of simulated personas and platform passes to match your local hardware specifications (16GB RAM recommendation).
          </p>

          <div class="profile-select-grid">
            <button
              v-for="profile in profileOptions"
              :key="profile.profile_name"
              class="profile-option-card"
              :class="{ selected: form.localProfile === profile.profile_name }"
              @click="selectLocalProfile(profile.profile_name)"
              @keydown.enter="selectLocalProfile(profile.profile_name)"
            >
              <div class="profile-card-header">
                <span class="profile-name-tag">{{ formatProfileName(profile.profile_name) }}</span>
                <span class="recommended-badge" v-if="profile.profile_name === 'hybrid_safe_default'">
                  ★ Recommended
                </span>
              </div>
              
              <div class="profile-specs">
                <div class="spec-row">
                  <span class="spec-label">Cohort size:</span>
                  <span class="spec-val">{{ profile.max_personas }} synthetic readers</span>
                </div>
                <div class="spec-row">
                  <span class="spec-label">Platforms:</span>
                  <span class="spec-val">{{ profile.platforms?.length || 0 }} platform adapters</span>
                </div>
                <div class="spec-row">
                  <span class="spec-label">Reaction Rounds:</span>
                  <span class="spec-val">{{ profile.reaction_rounds }} loops</span>
                </div>
              </div>

              <!-- Profile Warning details -->
              <div v-if="profile.profile_name === 'cloud_quality'" class="profile-warning info">
                ⚠️ Requires active internet connection and Gemini/NVIDIA API credentials.
              </div>
              <div v-if="profile.profile_name === 'local_tiny'" class="profile-warning info">
                ℹ️ Optimized for quick local tests. Star rating and DNF bands will have lower statistical sample size.
              </div>
            </button>
          </div>
        </section>

        <!-- Configuration Submit Actions -->
        <div class="action-footer">
          <button
            class="primary-btn lg-btn"
            @click="saveConfiguration"
            @keydown.enter="saveConfiguration"
            :disabled="saving"
          >
            {{ saving ? 'Saving Config...' : 'Apply & Save Settings' }}
          </button>
        </div>
      </main>

      <!-- Right Column: Providers Status & Diagnostics -->
      <aside class="settings-side-col" aria-label="System Diagnostics">
        
        <!-- 3. Model Providers & API Keys -->
        <section class="card settings-card" aria-labelledby="providers-heading">
          <h2 id="providers-heading">3. Provider Key Status</h2>
          <p class="section-desc">
            Status of the local shims and optional cloud model API keys configured in the workstation environment.
          </p>

          <div class="providers-list">
            <!-- Ollama -->
            <div class="provider-status-row">
              <div class="provider-meta">
                <span class="provider-icon">🦙</span>
                <div class="provider-info">
                  <h4>Ollama (Local LLM)</h4>
                  <p class="muted">Used for offline reading reactions</p>
                </div>
              </div>
              <span class="status-pill" :class="healthSummary.ollama === 'Connected' ? 'ready' : 'offline'">
                {{ healthSummary.ollama === 'Connected' ? 'Connected' : 'Offline' }}
              </span>
            </div>

            <!-- Neo4j -->
            <div class="provider-status-row">
              <div class="provider-meta">
                <span class="provider-icon">🕸️</span>
                <div class="provider-info">
                  <h4>Neo4j (Knowledge Graph)</h4>
                  <p class="muted">Tracks manuscript structural maps</p>
                </div>
              </div>
              <span class="status-pill" :class="healthSummary.neo4j === 'Connected' ? 'ready' : 'offline'">
                {{ healthSummary.neo4j === 'Connected' ? 'Connected' : 'Offline' }}
              </span>
            </div>

            <!-- Gemini -->
            <div class="provider-status-row">
              <div class="provider-meta">
                <span class="provider-icon">✦</span>
                <div class="provider-info">
                  <h4>Gemini API Key</h4>
                  <p class="muted">
                    <code>GEMINI_API_KEY</code> key check
                  </p>
                  <div class="key-obfuscator" v-if="healthSummary.gemini === 'Configured'">
                    <span class="bullet-key">••••••••••••••••••••••••••••••••</span>
                  </div>
                </div>
              </div>
              <span class="status-pill" :class="healthSummary.gemini === 'Configured' ? 'ready' : 'optional'">
                {{ healthSummary.gemini === 'Configured' ? 'Configured' : 'Missing' }}
              </span>
            </div>

            <!-- NVIDIA -->
            <div class="provider-status-row">
              <div class="provider-meta">
                <span class="provider-icon">🟢</span>
                <div class="provider-info">
                  <h4>NVIDIA NIM Key</h4>
                  <p class="muted">
                    <code>NVIDIA_API_KEY</code> key check
                  </p>
                  <div class="key-obfuscator" v-if="healthSummary.nvidia === 'Configured'">
                    <span class="bullet-key">••••••••••••••••••••••••••••••••</span>
                  </div>
                </div>
              </div>
              <span class="status-pill" :class="healthSummary.nvidia === 'Configured' ? 'ready' : 'optional'">
                {{ healthSummary.nvidia === 'Configured' ? 'Configured' : 'Missing' }}
              </span>
            </div>
          </div>
        </section>

        <!-- 4. Interactive Health Diagnostics -->
        <section class="card settings-card" aria-labelledby="diagnostics-heading">
          <div class="card-header-row">
            <h2 id="diagnostics-heading">4. Diagnostics Console</h2>
            <button
              class="primary-btn sm-btn"
              @click="runDiagnostics"
              @keydown.enter="runDiagnostics"
              :disabled="checking"
            >
              {{ checking ? 'Checking...' : 'Run Diagnostics' }}
            </button>
          </div>

          <p class="section-desc">
            Initiate an on-demand diagnostics sweep to verify host connection sockets.
          </p>

          <div class="diagnostics-console">
            <!-- Timeline steps -->
            <div class="console-timeline">
              <!-- Flask Backend API -->
              <div class="console-step" :class="diagnostics.backend.status">
                <span class="indicator"></span>
                <div class="step-desc">
                  <strong>Backend Flask API Connection</strong>
                  <p v-if="diagnostics.backend.status === 'ok'" class="msg text-ready">✓ Reachable: Swarmbook API blueprint active.</p>
                  <p v-else-if="diagnostics.backend.status === 'error'" class="msg text-offline">❌ Connection failed: Check if server is running.</p>
                  <p v-else class="msg text-muted">Pending connection check...</p>
                </div>
              </div>

              <!-- Ollama -->
              <div class="console-step" :class="diagnostics.ollama.status">
                <span class="indicator"></span>
                <div class="step-desc">
                  <strong>Local Ollama Service Socket</strong>
                  <p v-if="diagnostics.ollama.status === 'ok'" class="msg text-ready">✓ Connected: Socket responding. Model ready.</p>
                  <p v-else-if="diagnostics.ollama.status === 'error'" class="msg text-offline">❌ Offline: Servicing socket not reachable.</p>
                  <p v-else class="msg text-muted">Pending connection check...</p>
                </div>
              </div>

              <!-- Neo4j -->
              <div class="console-step" :class="diagnostics.neo4j.status">
                <span class="indicator"></span>
                <div class="step-desc">
                  <strong>Neo4j Database Connectivity</strong>
                  <p v-if="diagnostics.neo4j.status === 'ok'" class="msg text-ready">✓ Connected: Graph database active.</p>
                  <p v-else-if="diagnostics.neo4j.status === 'error'" class="msg text-offline">❌ Offline: Graph database driver connection failed.</p>
                  <p v-else class="msg text-muted">Pending connection check...</p>
                </div>
              </div>

              <!-- Optional Cloud Router -->
              <div class="console-step" :class="diagnostics.cloud.status">
                <span class="indicator"></span>
                <div class="step-desc">
                  <strong>Cloud Models Key Status</strong>
                  <p v-if="diagnostics.cloud.status === 'ok'" class="msg text-ready">✓ Active: Gemini/NVIDIA API key configuration detected.</p>
                  <p v-else-if="diagnostics.cloud.status === 'error'" class="msg text-mixed">ℹ️ Missing: Operating in offline mode.</p>
                  <p v-else class="msg text-muted">Pending keys status check...</p>
                </div>
              </div>
            </div>

            <!-- Troubleshooting panel if errors exist -->
            <div v-if="hasFailedDiagnostics" class="troubleshoot-box">
              <h4>🛠️ Troubleshooting Recommendations:</h4>
              <ul>
                <li v-if="diagnostics.backend.status === 'error'">
                  <strong>Flask Backend Offline:</strong> Ensure the local Python server is active. Start the backend by running <code>scripts/windows/start_swarmbook.ps1</code> in a PowerShell console.
                </li>
                <li v-if="diagnostics.ollama.status === 'error'">
                  <strong>Ollama Reachability:</strong> Make sure Ollama desktop client is active. Start it manually or run <code>ollama serve</code> in your shell.
                </li>
                <li v-if="diagnostics.neo4j.status === 'error'">
                  <strong>Neo4j Graph Database:</strong> Ensure the Neo4j docker container is running or run your host service instances. Check database configs if credentials changed.
                </li>
              </ul>
            </div>
          </div>
        </section>
      </aside>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { getBookSimHealth } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const projectId = computed(() => route.params.projectId || '')

const session = ref(getSwarmbookSession())
const health = ref(null)
const error = ref('')
const loadingMessage = ref('')
const saving = ref(false)
const checking = ref(false)
const saveSuccess = ref(false)

const form = reactive({
  privacyMode: session.value.metadata.privacyMode || 'hybrid_safe',
  localProfile: session.value.metadata.localProfile || 'hybrid_safe_default',
})

const diagnostics = reactive({
  backend: { status: 'idle' },
  ollama: { status: 'idle' },
  neo4j: { status: 'idle' },
  cloud: { status: 'idle' },
})

const hasFailedDiagnostics = computed(() => {
  return diagnostics.backend.status === 'error' ||
         diagnostics.ollama.status === 'error' ||
         diagnostics.neo4j.status === 'error'
})

const healthSummary = computed(() => {
  if (!health.value) {
    return { ollama: 'Checking...', neo4j: 'Checking...', gemini: 'Checking...', nvidia: 'Checking...' }
  }
  return {
    ollama: health.value.ollama?.ok ? 'Connected' : 'Offline',
    neo4j: health.value.neo4j?.ok ? 'Connected' : 'Offline',
    gemini: health.value.providers?.gemini_long_context?.ok ? 'Configured' : 'Optional',
    nvidia: health.value.providers?.nvidia_nim?.ok ? 'Configured' : 'Optional',
  }
})

const profileOptions = computed(() => {
  const items = health.value?.profiles?.items || []
  if (items.length) {
    return items
  }
  return [
    { profile_name: 'local_tiny', privacy_mode: 'local_only', max_personas: 12, platforms: ['goodreads', 'reddit', 'x'], reaction_rounds: 1, cross_reaction_posts: 4, local_parallel_jobs: 1 },
    { profile_name: 'hybrid_safe_default', privacy_mode: 'hybrid_safe', max_personas: 30, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x'], reaction_rounds: 2, cross_reaction_posts: 8, local_parallel_jobs: 1 },
    { profile_name: 'cloud_quality', privacy_mode: 'cloud_quality', max_personas: 60, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub'], reaction_rounds: 2, cross_reaction_posts: 12, local_parallel_jobs: 1 },
  ]
})

function setPrivacyMode(mode) {
  form.privacyMode = mode
}

function selectLocalProfile(profileName) {
  form.localProfile = profileName
  const selected = profileOptions.value.find((p) => p.profile_name === profileName)
  if (selected && selected.privacy_mode) {
    form.privacyMode = selected.privacy_mode
  }
}

async function loadHealth() {
  try {
    const response = await getBookSimHealth()
    health.value = response.data
  } catch (err) {
    error.value = 'Failed to load backend system health state.'
  }
}

async function runDiagnostics() {
  checking.value = true
  diagnostics.backend.status = 'checking'
  diagnostics.ollama.status = 'checking'
  diagnostics.neo4j.status = 'checking'
  diagnostics.cloud.status = 'checking'

  try {
    const response = await getBookSimHealth()
    health.value = response.data
    
    // Evaluate backend
    diagnostics.backend.status = 'ok'
    
    // Evaluate Ollama
    diagnostics.ollama.status = response.data.ollama?.ok ? 'ok' : 'error'
    
    // Evaluate Neo4j
    diagnostics.neo4j.status = response.data.neo4j?.ok ? 'ok' : 'error'
    
    // Evaluate Cloud keys
    const geminiOk = response.data.providers?.gemini_long_context?.ok
    const nvidiaOk = response.data.providers?.nvidia_nim?.ok
    diagnostics.cloud.status = (geminiOk || nvidiaOk) ? 'ok' : 'error'
  } catch (err) {
    diagnostics.backend.status = 'error'
    diagnostics.ollama.status = 'error'
    diagnostics.neo4j.status = 'error'
    diagnostics.cloud.status = 'error'
  } finally {
    checking.value = false
  }
}

function saveConfiguration() {
  saving.value = true
  error.value = ''
  
  try {
    const selected = profileOptions.value.find((p) => p.profile_name === form.localProfile) || profileOptions.value[1]
    
    // Apply configurations to active session state
    session.value = updateSwarmbookSession({
      metadata: {
        ...session.value.metadata,
        privacyMode: form.privacyMode,
        localProfile: form.localProfile,
      },
      simulationConfig: {
        ...session.value.simulationConfig,
        profileName: form.localProfile,
        personaCount: selected.max_personas || session.value.simulationConfig.personaCount,
        platforms: selected.platforms?.map((platform) => String(platform).toLowerCase()) || session.value.simulationConfig.platforms,
        privacyMode: form.privacyMode || selected.privacy_mode,
      }
    })
    
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 4000)
  } catch (err) {
    error.value = 'Failed to save system configurations.'
  } finally {
    saving.value = false
  }
}

function formatProfileName(name) {
  if (!name) return ''
  return name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

onMounted(() => {
  loadHealth()
  // Automatically run the first diagnostic check on mount
  runDiagnostics()
})
</script>

<style scoped>
/* Settings grid structures */
.settings-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 20px;
  align-items: start;
}

.settings-main-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-side-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 84px;
}

.settings-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.settings-card h2 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.section-desc {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

/* Toast Success details */
.toast-banner {
  background: #d1fae5;
  border-left: 4px solid #10b981;
  color: #065f46;
  padding: 14px 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toast-banner.success {
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.1);
}

/* 1. Privacy cards row */
.privacy-cards-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.privacy-card-select {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  outline: none;
  font-family: inherit;
}

.privacy-card-select:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.privacy-card-select.selected {
  border-color: #ff4500;
  background: #fff5ef;
}

.privacy-card-select:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 2px;
}

.privacy-card-select .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.badge.local_only {
  background: #d1fae5;
  color: #065f46;
}

.badge.hybrid_safe {
  background: #fef3c7;
  color: #92400e;
}

.badge.cloud_quality {
  background: #dbeafe;
  color: #1e40af;
}

.shield-status {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 700;
  text-transform: uppercase;
  font-family: 'JetBrains Mono', monospace;
}

.privacy-card-select.selected .shield-status {
  color: #ff4500;
}

.privacy-card-select h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.explanation-text {
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

/* 2. Profiles setup grid */
.profile-select-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.profile-option-card {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
  font-family: inherit;
  display: flex;
  flex-direction: column;
}

.profile-option-card:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.profile-option-card.selected {
  border-color: #ff4500;
  background: #fff5ef;
}

.profile-option-card:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 2px;
}

.profile-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.profile-name-tag {
  font-size: 0.9rem;
  font-weight: 700;
  color: #0f172a;
}

.recommended-badge {
  font-size: 0.68rem;
  font-weight: 700;
  color: #ff4500;
  text-transform: uppercase;
}

.profile-specs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
}

.spec-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.spec-label {
  color: #64748b;
}

.spec-val {
  font-weight: 600;
  color: #334155;
}

.profile-warning {
  font-size: 0.72rem;
  padding: 6px 10px;
  border-radius: 4px;
  margin-top: auto;
  line-height: 1.4;
}

.profile-warning.info {
  background: rgba(0, 0, 0, 0.03);
  color: #64748b;
  border-left: 2px solid #cbd5e1;
}

.profile-option-card.selected .profile-warning.info {
  background: rgba(255, 69, 0, 0.05);
  color: #a02b00;
  border-left-color: #ff4500;
}

/* Action actions button footer */
.action-footer {
  margin-top: 12px;
}

.primary-btn {
  background: #ff4500;
  color: #ffffff;
  border: 1px solid #ff4500;
  padding: 10px 18px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.primary-btn:hover:not(:disabled) {
  background: #e03d00;
  border-color: #e03d00;
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.primary-btn:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 2px;
}

.primary-btn.lg-btn {
  padding: 14px 28px;
  font-size: 1rem;
}

.primary-btn.sm-btn {
  padding: 6px 12px;
  font-size: 0.8rem;
}

/* Provider status row styles */
.providers-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.provider-status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 14px;
}

.provider-status-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.provider-meta {
  display: flex;
  gap: 12px;
}

.provider-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}

.provider-info h4 {
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 2px 0;
}

.provider-info .muted {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.provider-info code {
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 0.72rem;
  color: #0f172a;
}

.key-obfuscator {
  margin-top: 4px;
}

.bullet-key {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #ff4500;
  letter-spacing: 0.5px;
}

.status-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.status-pill.ready {
  background: #d1fae5;
  color: #065f46;
}

.status-pill.optional {
  background: #f1f5f9;
  color: #64748b;
}

.status-pill.offline {
  background: #fef2f2;
  color: #991b1b;
}

/* Diagnostics console styles */
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.diagnostics-console {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.console-timeline {
  display: flex;
  flex-direction: column;
  position: relative;
  padding-left: 20px;
}

.console-timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: #e2e8f0;
}

.console-step {
  position: relative;
  padding-bottom: 16px;
}

.console-step:last-child {
  padding-bottom: 0;
}

.console-step .indicator {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #cbd5e1;
  border: 3px solid #ffffff;
  box-shadow: 0 0 0 1px #cbd5e1;
}

.console-step.checking .indicator {
  background: #f59e0b;
  box-shadow: 0 0 0 1px #f59e0b;
  animation: pulse-diagnostic 1.5s infinite;
}

.console-step.ok .indicator {
  background: #10b981;
  box-shadow: 0 0 0 1px #10b981;
}

.console-step.error .indicator {
  background: #ef4444;
  box-shadow: 0 0 0 1px #ef4444;
}

@keyframes pulse-diagnostic {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.step-desc {
  font-size: 0.82rem;
}

.step-desc strong {
  display: block;
  color: #334155;
  margin-bottom: 2px;
}

.step-desc .msg {
  margin: 0;
  font-size: 0.78rem;
}

.step-desc .text-muted {
  color: #94a3b8;
}

.troubleshoot-box {
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.troubleshoot-box h4 {
  margin: 0 0 8px 0;
  color: #92400e;
  font-weight: 700;
}

.troubleshoot-box ul {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #78350f;
}

.troubleshoot-box code {
  background: rgba(245, 158, 11, 0.1);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 0.72rem;
}

/* Animations transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

/* Responsive adjustment */
@media (max-width: 900px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  .settings-side-col {
    position: static;
  }
}
</style>
