<template>
  <div class="swarmbook-shell">
    <!-- Top Brand & Navigation Header -->
    <header class="shell-header">
      <div class="brand-zone">
        <button class="menu-toggle" @click="toggleSidebar" aria-label="Toggle Navigation Menu">
          <span class="bar"></span>
          <span class="bar"></span>
          <span class="bar"></span>
        </button>
        <div class="brand-group" @click="goToHome" role="button" tabindex="0" @keydown.enter="goToHome">
          <span class="logo-icon">📖</span>
          <div class="logo-text">
            <span class="brand-title">SWARMBOOK STUDIO</span>
            <span class="brand-tagline">Book Reaction Simulator</span>
          </div>
        </div>
      </div>

      <!-- Top Primary Navigation Links -->
      <nav class="top-nav" aria-label="Main Navigation">
        <button class="nav-btn" :class="{ active: activeRoute === 'SwarmbookHome' }" @click="goToProjects" @keydown.enter="goToProjects">
          Projects
        </button>
        <button class="nav-btn" :class="{ active: activeRoute === 'SwarmbookUpload' }" @click="startNewSimulation" @keydown.enter="startNewSimulation">
          New Simulation
        </button>
        <button class="nav-btn" :class="{ active: isRouteActive('SwarmbookReport') }" :disabled="!projectId" @click="goToReport" @keydown.enter="goToReport">
          Reports
        </button>
        <button class="nav-btn" :class="{ active: isRouteActive('SwarmbookPersonas') }" :disabled="!projectId || !hasSimulation" @click="goToPersonas" @keydown.enter="goToPersonas">
          Personas
        </button>
        <button class="nav-btn" :class="{ active: isRouteActive('SwarmbookCompare') }" :disabled="!projectId" @click="goToCompare" @keydown.enter="goToCompare">
          Compare Drafts
        </button>
        <button class="nav-btn settings-trigger" :class="{ active: isRouteActive('SwarmbookSettings') }" @click="goToSettings" @keydown.enter="goToSettings">
          <span>⚙</span> Settings
        </button>
      </nav>

      <!-- Return Pathway to MiroFish UI -->
      <div class="header-actions">
        <button class="exit-btn" @click="exitToMiroFish" @keydown.enter="exitToMiroFish">
          Exit to MiroFish <span class="arrow">↗</span>
        </button>
      </div>
    </header>

    <div class="shell-container">
      <!-- Left Sidebar: Progress Steps and System Status Area -->
      <aside class="shell-sidebar" :class="{ 'sidebar-open': isSidebarOpen }">
        <div class="sidebar-scroll">
          <nav class="workflow-steps" aria-label="Workflow Steps">
            <div class="nav-header">WORKFLOW SEQUENCE</div>
            <router-link
              v-for="step in steps"
              :key="step.name"
              class="step-link"
              :class="{ active: activeRoute === step.name, disabled: step.disabled }"
              :to="step.disabled ? '#' : step.to"
              @click.native="step.disabled ? $event.preventDefault() : null"
            >
              <span class="step-num">{{ step.index }}</span>
              <span class="step-label">{{ step.label }}</span>
              <span v-if="activeRoute === step.name" class="active-dot"></span>
            </router-link>
          </nav>

          <!-- Persistent System Status Indicator Area -->
          <div class="system-status-panel">
            <div class="panel-title">SYSTEM STATUS</div>
            <ul class="status-list">
              <li>
                <span class="status-name">Ollama</span>
                <div class="status-indicator">
                  <span class="pulse-dot" :class="statusTone(healthSummary.ollama)"></span>
                  <span class="status-val">{{ healthSummary.ollama }}</span>
                </div>
              </li>
              <li>
                <span class="status-name">Neo4j</span>
                <div class="status-indicator">
                  <span class="pulse-dot" :class="statusTone(healthSummary.neo4j)"></span>
                  <span class="status-val">{{ healthSummary.neo4j }}</span>
                </div>
              </li>
              <li>
                <span class="status-name">Privacy Mode</span>
                <div class="privacy-badge" :class="session.metadata.privacyMode">
                  <span class="icon">🔒</span>
                  <span class="mode-text">{{ session.metadata.privacyMode }}</span>
                </div>
              </li>
              <li>
                <span class="status-name">Active Profile</span>
                <div class="profile-badge">
                  <span class="profile-val">{{ session.metadata.localProfile || 'None' }}</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </aside>

      <!-- Backdrop for mobile sidebar collapse -->
      <div v-if="isSidebarOpen" class="sidebar-backdrop" @click="closeSidebar"></div>

      <!-- Main Layout Workspace Area -->
      <main class="shell-main" id="main-content">
        <header class="workspace-header">
          <p v-if="eyebrow" class="workspace-eyebrow">{{ eyebrow }}</p>
          <h1 class="workspace-title">{{ title }}</h1>
          <p v-if="subtitle" class="workspace-subtitle">{{ subtitle }}</p>
        </header>

        <!-- Loading / Notification Banners -->
        <div v-if="errorMessage" class="shell-banner error-banner" role="alert">
          <span class="banner-title">Error</span>
          <p>{{ errorMessage }}</p>
        </div>
        <div v-if="loadingMessage" class="shell-banner loading-banner">
          <span class="banner-title pulsing">Loading</span>
          <p>{{ loadingMessage }}</p>
        </div>

        <!-- Render View Inner Contents -->
        <div class="workspace-content">
          <slot />
        </div>
      </main>
    </div>

    <!-- Settings Modal Removed: Redirected to SwarmbookSettingsView route -->
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getBookSimHealth } from '../../api/bookSim'
import { getSwarmbookSession, clearSwarmbookSession } from '../../store/swarmbookSession'

const props = defineProps({
  activeRoute: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  eyebrow: {
    type: String,
    default: 'Swarmbook Studio',
  },
  errorMessage: {
    type: String,
    default: '',
  },
  loadingMessage: {
    type: String,
    default: '',
  },
  projectId: {
    type: String,
    default: '',
  },
})

const router = useRouter()
const route = useRoute()

const session = ref(getSwarmbookSession())
const health = ref(null)
const isSidebarOpen = ref(false)

const hasSimulation = computed(() => {
  return !!(session.value.simulationRun?.reader_personas?.length)
})

const activeProjectId = computed(() => {
  return props.projectId || session.value.projectId || ''
})

// Watch route changes to keep session up to date
watch(() => route.path, () => {
  session.value = getSwarmbookSession()
})

const steps = computed(() => {
  const pId = activeProjectId.value
  const projectRoute = (name) => {
    if (!pId) {
      return { name: 'SwarmbookHome' }
    }
    return { name, params: { projectId: pId } }
  }

  return [
    { index: '01', label: 'Project Setup', name: 'SwarmbookHome', to: { name: 'SwarmbookHome' }, disabled: false },
    { index: '02', label: 'Upload Manuscript', name: 'SwarmbookUpload', to: projectRoute('SwarmbookUpload'), disabled: !pId },
    { index: '03', label: 'Editorial Metadata', name: 'SwarmbookMetadata', to: projectRoute('SwarmbookMetadata'), disabled: !pId || !session.value.manuscript?.text },
    { index: '04', label: 'Evidence Pack', name: 'SwarmbookEvidence', to: projectRoute('SwarmbookEvidence'), disabled: !pId || !session.value.evidencePack },
    { index: '05', label: 'Simulate Config', name: 'SwarmbookSimulation', to: projectRoute('SwarmbookSimulation'), disabled: !pId || !session.value.evidencePack },
    { index: '06', label: 'Report Details', name: 'SwarmbookReport', to: projectRoute('SwarmbookReport'), disabled: !pId || !session.value.report },
    { index: '07', label: 'Persona Chat', name: 'SwarmbookPersonas', to: projectRoute('SwarmbookPersonas'), disabled: !pId || !hasSimulation.value },
    { index: '08', label: 'Compare Drafts', name: 'SwarmbookCompare', to: projectRoute('SwarmbookCompare'), disabled: !pId },
  ]
})

const healthSummary = computed(() => {
  if (!health.value) {
    return { ollama: 'Checking...', neo4j: 'Checking...' }
  }
  return {
    ollama: health.value.ollama?.ok ? 'Connected' : 'Offline',
    neo4j: health.value.neo4j?.ok ? 'Connected' : 'Offline',
  }
})

function isRouteActive(name) {
  return props.activeRoute === name
}

function statusTone(val) {
  if (val === 'Connected') return 'ready'
  if (val === 'Checking...') return 'loading'
  return 'offline'
}

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value
}

function closeSidebar() {
  isSidebarOpen.value = false
}

function goToSettings() {
  router.push({ name: 'SwarmbookSettings', params: { projectId: activeProjectId.value || undefined } })
}

function goToHome() {
  router.push({ name: 'SwarmbookHome' })
}

function goToProjects() {
  router.push({ name: 'SwarmbookHome' })
}

function startNewSimulation() {
  clearSwarmbookSession()
  session.value = getSwarmbookSession()
  router.push({ name: 'NewSimulationWizard' })
}

function goToReport() {
  if (activeProjectId.value) {
    router.push({ name: 'SwarmbookReport', params: { projectId: activeProjectId.value } })
  }
}

function goToPersonas() {
  if (activeProjectId.value && hasSimulation.value) {
    router.push({ name: 'SwarmbookPersonas', params: { projectId: activeProjectId.value } })
  }
}

function goToCompare() {
  if (activeProjectId.value) {
    router.push({ name: 'SwarmbookCompare', params: { projectId: activeProjectId.value } })
  }
}

function exitToMiroFish() {
  router.push('/')
}

async function loadHealth() {
  try {
    const response = await getBookSimHealth()
    health.value = response.data
  } catch (err) {
    console.warn('AppShell health load failed:', err)
  }
}

onMounted(() => {
  loadHealth()
  // Poll health status details every 30 seconds
  const interval = setInterval(loadHealth, 30000)
  return () => clearInterval(interval)
})
</script>

<style scoped>
/* Scoped custom styling targeting SaaS UX visual requirements */

.swarmbook-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  color: #0f172a;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, -apple-system, sans-serif;
}

/* Header visual details */
.shell-header {
  height: 64px;
  background: #0f172a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #1e293b;
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand-zone {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-toggle {
  display: none;
  flex-direction: column;
  gap: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.menu-toggle .bar {
  display: block;
  width: 20px;
  height: 2px;
  background: #ffffff;
  transition: all 0.2s;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  outline: none;
}

.brand-group:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 4px;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 0.95rem;
  letter-spacing: 1px;
}

.brand-tagline {
  font-size: 0.7rem;
  opacity: 0.7;
  letter-spacing: 0.5px;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  outline: none;
}

.nav-btn:hover:not(:disabled) {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.05);
}

.nav-btn.active {
  color: #ff4500;
  background: rgba(255, 69, 0, 0.1);
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-btn:focus-visible {
  outline: 2px solid #ff4500;
  border-radius: 4px;
}

.settings-trigger {
  color: #cbd5e1;
}

.exit-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #cbd5e1;
  padding: 8px 14px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'JetBrains Mono', monospace;
  outline: none;
}

.exit-btn:hover {
  background: #ffffff;
  color: #0f172a;
  border-color: #ffffff;
}

.exit-btn:focus-visible {
  outline: 2px solid #ff4500;
}

/* Sidebar and Main Container */
.shell-container {
  display: flex;
  flex: 1;
  position: relative;
}

.shell-sidebar {
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  z-index: 90;
  transition: transform 0.3s ease;
}

.sidebar-scroll {
  overflow-y: auto;
  flex: 1;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.workflow-steps {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 12px;
  padding-left: 8px;
}

.step-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 6px;
  text-decoration: none;
  color: #475569;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
  position: relative;
  outline: none;
}

.step-link:hover:not(.disabled) {
  background: #f1f5f9;
  color: #0f172a;
}

.step-link.active {
  background: #faf5ff;
  color: #7c3aed;
  background: #fff5ef;
  color: #ff4500;
}

.step-link.disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.step-link:focus-visible {
  outline: 2px solid #ff4500;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #94a3b8;
}

.step-link.active .step-num {
  color: #ff4500;
}

.active-dot {
  position: absolute;
  right: 12px;
  width: 6px;
  height: 6px;
  background: #ff4500;
  border-radius: 50%;
}

/* System Status Details */
.system-status-panel {
  margin-top: 32px;
  border-top: 1px solid #f1f5f9;
  padding-top: 20px;
}

.panel-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  letter-spacing: 1px;
  margin-bottom: 12px;
  padding-left: 8px;
}

.status-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
  padding: 0 8px;
}

.status-name {
  color: #64748b;
  font-weight: 500;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #cbd5e1;
}

.pulse-dot.ready {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
  animation: pulse 1.8s infinite;
}

.pulse-dot.loading {
  background: #f59e0b;
  box-shadow: 0 0 8px #f59e0b;
  animation: pulse 1.8s infinite;
}

.pulse-dot.offline {
  background: #ef4444;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  70% { transform: scale(1); box-shadow: 0 0 0 5px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.status-val {
  color: #334155;
  font-weight: 600;
}

.privacy-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
}

.privacy-badge.local_only {
  background: #d1fae5;
  color: #065f46;
}

.privacy-badge.hybrid_safe {
  background: #fef3c7;
  color: #92400e;
}

.privacy-badge.cloud_quality {
  background: #dbeafe;
  color: #1e40af;
}

.profile-badge {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: #475569;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Workspace Main Workspace Area */
.shell-main {
  flex: 1;
  padding: 32px 40px 60px;
  overflow-y: auto;
  height: calc(100vh - 64px);
  max-width: 100%;
}

.workspace-header {
  margin-bottom: 28px;
}

.workspace-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #ff4500;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 700;
  margin-bottom: 6px;
}

.workspace-title {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
  line-height: 1.15;
  margin: 0;
}

.workspace-subtitle {
  font-size: 0.95rem;
  color: #64748b;
  margin-top: 6px;
  max-width: 800px;
  line-height: 1.5;
}

/* Banner details */
.shell-banner {
  border-left: 4px solid #ef4444;
  background: #fef2f2;
  padding: 16px;
  margin-bottom: 24px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.shell-banner.loading-banner {
  border-left-color: #3b82f6;
  background: #eff6ff;
}

.banner-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 700;
  color: #991b1b;
}

.loading-banner .banner-title {
  color: #1e3a8a;
}

.pulsing {
  animation: pulse-text 1.5s infinite;
}

@keyframes pulse-text {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.shell-banner p {
  font-size: 0.88rem;
  margin: 0;
  color: #7f1d1d;
}

.loading-banner p {
  color: #1e3a8a;
}

.workspace-content {
  margin-top: 10px;
}

/* Modal CSS details */
.settings-modal {
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

.modal-backdrop {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
}

.modal-card {
  position: relative;
  background: #ffffff;
  width: 100%;
  max-width: 540px;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
}

.close-btn:hover {
  color: #0f172a;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-section h3 {
  font-size: 0.85rem;
  font-family: 'JetBrains Mono', monospace;
  color: #ff4500;
  letter-spacing: 0.5px;
  margin: 0 0 12px 0;
  text-transform: uppercase;
}

.details-grid {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
}

.detail-row.flex-column {
  flex-direction: column;
  gap: 6px;
}

.detail-row .label {
  color: #64748b;
  font-weight: 500;
}

.detail-row .value {
  font-weight: 600;
  color: #0f172a;
  font-family: 'JetBrains Mono', monospace;
}

.pill-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.platform-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: lowercase;
}

.alert-block {
  display: flex;
  gap: 10px;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  color: #92400e;
  padding: 12px;
  border-radius: 6px;
  font-size: 0.82rem;
}

.alert-block p {
  margin: 0;
  line-height: 1.4;
}

.code-log pre {
  background: #0f172a;
  color: #38bdf8;
  padding: 14px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  margin: 0;
  overflow-x: auto;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}

.primary-btn {
  background: #ff4500;
  border: 1px solid #ff4500;
  color: #ffffff;
  padding: 10px 18px;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  outline: none;
}

.primary-btn:hover {
  background: #e03d00;
}

.primary-btn:focus-visible {
  outline: 2px solid #ff4500;
  outline-offset: 2px;
}

/* Mobile Responsive Adjustments */
@media (max-width: 900px) {
  .menu-toggle {
    display: flex;
  }

  .top-nav {
    display: none; /* Hide top nav links on tablet/mobile; moved inside collapsed rail */
  }

  .shell-sidebar {
    position: fixed;
    top: 64px;
    left: 0;
    transform: translateX(-100%);
    box-shadow: 10px 0 15px -3px rgba(0, 0, 0, 0.05);
  }

  .shell-sidebar.sidebar-open {
    transform: translateX(0);
  }

  .sidebar-backdrop {
    position: fixed;
    top: 64px;
    left: 0;
    width: 100%;
    height: calc(100vh - 64px);
    background: rgba(15, 23, 42, 0.4);
    z-index: 85;
  }

  .shell-main {
    padding: 24px 20px 48px;
    height: calc(100vh - 64px);
  }
}
</style>
