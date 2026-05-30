<template>
  <div class="swarmbook-shell">

    <!-- ═══════════════════════════════════════════════
         TOP HEADER: Brand + Global Nav + MiroFish exit
         ═══════════════════════════════════════════════ -->
    <header class="shell-header" role="banner">
      <div class="brand-zone">
        <!-- Mobile hamburger -->
        <button
          class="menu-toggle"
          @click="toggleSidebar"
          :aria-expanded="isSidebarOpen"
          aria-controls="shell-sidebar"
          aria-label="Toggle navigation"
        >
          <span class="bar" :class="{ open: isSidebarOpen }"></span>
          <span class="bar" :class="{ open: isSidebarOpen }"></span>
          <span class="bar" :class="{ open: isSidebarOpen }"></span>
        </button>

        <!-- Brand -->
        <button class="brand-group" @click="goToHome" aria-label="Go to Swarmbook home">
          <span class="logo-icon" aria-hidden="true">📖</span>
          <div class="logo-text">
            <span class="brand-title">SWARMBOOK STUDIO</span>
            <span class="brand-tagline">Book Reaction Simulator</span>
          </div>
        </button>
      </div>

      <!-- Global Navigation (desktop) -->
      <nav class="top-nav" aria-label="Global navigation">
        <button
          id="nav-projects"
          class="nav-btn"
          :class="{ active: activeRoute === 'SwarmbookHome' }"
          :aria-current="activeRoute === 'SwarmbookHome' ? 'page' : undefined"
          @click="goToHome"
        >Projects</button>

        <button
          id="nav-new-test"
          class="nav-btn"
          :class="{ active: activeRoute === 'NewSimulationWizard' }"
          :aria-current="activeRoute === 'NewSimulationWizard' ? 'page' : undefined"
          @click="startNewTest"
        >New Test</button>

        <button
          id="nav-report"
          class="nav-btn"
          :class="{ active: activeRoute === 'SwarmbookReport' }"
          :aria-current="activeRoute === 'SwarmbookReport' ? 'page' : undefined"
          :disabled="!activeProjectId"
          :aria-disabled="!activeProjectId"
          @click="goToReport"
        >Report</button>

        <button
          id="nav-ask-readers"
          class="nav-btn"
          :class="{ active: activeRoute === 'SwarmbookPersonas' }"
          :aria-current="activeRoute === 'SwarmbookPersonas' ? 'page' : undefined"
          :disabled="!activeProjectId || !hasSimulation"
          :aria-disabled="!activeProjectId || !hasSimulation"
          @click="goToPersonas"
        >Ask Readers</button>

        <button
          id="nav-compare"
          class="nav-btn"
          :class="{ active: activeRoute === 'SwarmbookCompare' }"
          :aria-current="activeRoute === 'SwarmbookCompare' ? 'page' : undefined"
          :disabled="!activeProjectId"
          :aria-disabled="!activeProjectId"
          @click="goToCompare"
        >Compare</button>

        <button
          id="nav-settings"
          class="nav-btn nav-settings"
          :class="{ active: activeRoute === 'SwarmbookSettings' }"
          :aria-current="activeRoute === 'SwarmbookSettings' ? 'page' : undefined"
          @click="goToSettings"
        >
          <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
          </svg>
          Settings
        </button>

        <!-- Divider -->
        <span class="nav-divider" aria-hidden="true"></span>

        <!-- Original MiroFish — always visible, distinct styling -->
        <button
          id="nav-mirofish"
          class="nav-btn nav-mirofish"
          @click="exitToMiroFish"
          aria-label="Go to Original MiroFish application"
        >
          Original MiroFish
          <svg class="nav-icon-sm" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M8.636 3.5a.5.5 0 00-.5-.5H1.5A1.5 1.5 0 000 4.5v10A1.5 1.5 0 001.5 16h10a1.5 1.5 0 001.5-1.5V7.864a.5.5 0 00-1 0V14.5a.5.5 0 01-.5.5h-10a.5.5 0 01-.5-.5v-10a.5.5 0 01.5-.5h6.636a.5.5 0 00.5-.5z" clip-rule="evenodd"/>
            <path fill-rule="evenodd" d="M16 .5a.5.5 0 00-.5-.5h-5a.5.5 0 000 1h3.793L6.146 9.146a.5.5 0 10.708.708L15 1.707V5.5a.5.5 0 001 0v-5z" clip-rule="evenodd"/>
          </svg>
        </button>
      </nav>
    </header>

    <!-- ═══════════════════════════════════════════════
         STATUS STRIP — single source of truth for system/privacy status.
         Placed below header, above sidebar+content split.
         ═══════════════════════════════════════════════ -->
    <div class="status-strip" role="status" aria-label="System and privacy status">
      <!-- Ollama -->
      <div class="strip-item">
        <span class="pulse-dot" :class="statusTone(healthSummary.ollama)" aria-hidden="true"></span>
        <span class="strip-label">Ollama</span>
        <span class="strip-val" :class="statusTone(healthSummary.ollama)">{{ healthSummary.ollama }}</span>
      </div>
      <span class="strip-sep" aria-hidden="true">·</span>
      <!-- Neo4j -->
      <div class="strip-item">
        <span class="pulse-dot" :class="statusTone(healthSummary.neo4j)" aria-hidden="true"></span>
        <span class="strip-label">Neo4j</span>
        <span class="strip-val" :class="statusTone(healthSummary.neo4j)">{{ healthSummary.neo4j }}</span>
      </div>
      <span class="strip-sep" aria-hidden="true">·</span>
      <!-- Privacy -->
      <div class="strip-item">
        <span class="strip-icon" aria-hidden="true">🔒</span>
        <span class="strip-label">Privacy</span>
        <span class="strip-badge" :class="session.metadata.privacyMode || 'local_only'">
          {{ session.metadata.privacyMode || 'local_only' }}
        </span>
      </div>
      <span class="strip-sep" aria-hidden="true">·</span>
      <!-- Profile -->
      <div class="strip-item">
        <span class="strip-label">Profile</span>
        <span class="strip-profile">{{ session.metadata.localProfile || 'default' }}</span>
      </div>
      <!-- Active project pill (only if set) -->
      <template v-if="activeProjectId">
        <span class="strip-sep" aria-hidden="true">·</span>
        <div class="strip-item">
          <span class="strip-label">Project</span>
          <span class="strip-project-id">{{ truncateId(activeProjectId) }}</span>
        </div>
      </template>
    </div>

    <!-- ═══════════════════════════════════════════════
         BODY: Sidebar rail + Main content
         ═══════════════════════════════════════════════ -->
    <div class="shell-container">

      <!-- Sidebar backdrop (mobile) -->
      <div
        v-if="isSidebarOpen"
        class="sidebar-backdrop"
        @click="closeSidebar"
        aria-hidden="true"
      ></div>

      <!-- ── SIDEBAR / WORKFLOW RAIL ───────────────── -->
      <aside
        id="shell-sidebar"
        class="shell-sidebar"
        :class="{ 'sidebar-open': isSidebarOpen }"
        aria-label="Workflow navigation"
      >
        <div class="sidebar-inner">

          <!-- Mobile-only: global nav items at top of drawer -->
          <div class="sidebar-global-nav" aria-label="Global navigation (mobile)">
            <button class="sidebar-global-btn" @click="goToHome; closeSidebar()">
              <span class="sg-icon" aria-hidden="true">🏠</span> Projects
            </button>
            <button class="sidebar-global-btn" @click="startNewTest(); closeSidebar()">
              <span class="sg-icon" aria-hidden="true">✨</span> New Test
            </button>
            <button class="sidebar-global-btn" :disabled="!activeProjectId" @click="goToReport(); closeSidebar()">
              <span class="sg-icon" aria-hidden="true">📊</span> Report
            </button>
            <button class="sidebar-global-btn" :disabled="!activeProjectId || !hasSimulation" @click="goToPersonas(); closeSidebar()">
              <span class="sg-icon" aria-hidden="true">💬</span> Ask Readers
            </button>
            <button class="sidebar-global-btn" :disabled="!activeProjectId" @click="goToCompare(); closeSidebar()">
              <span class="sg-icon" aria-hidden="true">⚖️</span> Compare
            </button>
            <button class="sidebar-global-btn" @click="goToSettings(); closeSidebar()">
              <span class="sg-icon" aria-hidden="true">⚙️</span> Settings
            </button>
            <div class="sidebar-divider" aria-hidden="true"></div>
          </div>

          <!-- Workflow sequence label -->
          <div class="rail-section-label">WORKFLOW</div>

          <!-- Workflow steps nav -->
          <nav class="workflow-rail" aria-label="Workflow steps">
            <template v-for="(step, index) in workflowSteps" :key="step.name">
              <router-link
                :id="`step-${step.name}`"
                class="step-link"
                :class="{
                  'step-active': activeRoute === step.name,
                  'step-disabled': step.disabled
                }"
                :to="step.disabled ? { name: 'SwarmbookHome' } : step.to"
                :aria-current="activeRoute === step.name ? 'step' : undefined"
                :aria-disabled="step.disabled ? 'true' : undefined"
                :tabindex="step.disabled ? -1 : 0"
                @click.prevent="handleStepClick(step)"
              >
                <span class="step-accent" aria-hidden="true"></span>
                <span class="step-num" aria-hidden="true">{{ step.index }}</span>
                <span class="step-label">{{ step.label }}</span>
                <span v-if="step.badge" class="step-badge" aria-hidden="true">{{ step.badge }}</span>
              </router-link>
            </template>
          </nav>

          <!-- Sidebar footer: Settings + Original MiroFish -->
          <div class="sidebar-footer">
            <div class="sidebar-divider" aria-hidden="true"></div>
            <button
              class="sidebar-footer-btn"
              :class="{ 'footer-active': activeRoute === 'SwarmbookSettings' }"
              @click="goToSettings(); closeSidebar()"
              :aria-current="activeRoute === 'SwarmbookSettings' ? 'page' : undefined"
            >
              <svg class="footer-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
              </svg>
              Settings
            </button>

            <button
              class="sidebar-footer-btn mirofish-link"
              @click="exitToMiroFish"
              aria-label="Open Original MiroFish application"
            >
              <svg class="footer-icon" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M8.636 3.5a.5.5 0 00-.5-.5H1.5A1.5 1.5 0 000 4.5v10A1.5 1.5 0 001.5 16h10a1.5 1.5 0 001.5-1.5V7.864a.5.5 0 00-1 0V14.5a.5.5 0 01-.5.5h-10a.5.5 0 01-.5-.5v-10a.5.5 0 01.5-.5h6.636a.5.5 0 00.5-.5z" clip-rule="evenodd"/>
                <path fill-rule="evenodd" d="M16 .5a.5.5 0 00-.5-.5h-5a.5.5 0 000 1h3.793L6.146 9.146a.5.5 0 10.708.708L15 1.707V5.5a.5.5 0 001 0v-5z" clip-rule="evenodd"/>
              </svg>
              Original MiroFish
            </button>
          </div>
        </div>
      </aside>

      <!-- ── MAIN WORKSPACE ──────────────────────── -->
      <main class="shell-main" id="main-content" tabindex="-1">

        <!-- Skip-to-content anchor -->
        <a href="#main-content" class="skip-link">Skip to content</a>

        <!-- Page header -->
        <header class="workspace-header">
          <p v-if="eyebrow" class="workspace-eyebrow">{{ eyebrow }}</p>
          <h1 class="workspace-title">{{ title }}</h1>
          <p v-if="subtitle" class="workspace-subtitle">{{ subtitle }}</p>
        </header>

        <!-- Error / Loading banners -->
        <div v-if="errorMessage" class="shell-banner error-banner" role="alert" aria-live="assertive">
          <span class="banner-icon" aria-hidden="true">⚠</span>
          <div class="banner-body">
            <span class="banner-title">Error</span>
            <p>{{ errorMessage }}</p>
          </div>
        </div>
        <div v-if="loadingMessage" class="shell-banner loading-banner" aria-live="polite">
          <span class="banner-spinner" aria-hidden="true"></span>
          <div class="banner-body">
            <span class="banner-title">Loading</span>
            <p>{{ loadingMessage }}</p>
          </div>
        </div>

        <!-- View content slot -->
        <div class="workspace-content">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getBookSimHealth } from '../../api/bookSim'
import { getSwarmbookSession, clearSwarmbookSession } from '../../store/swarmbookSession'

// ── Props ──────────────────────────────────────────────────────────
const props = defineProps({
  activeRoute: { type: String, required: true },
  title:       { type: String, required: true },
  subtitle:    { type: String, default: '' },
  eyebrow:     { type: String, default: 'Swarmbook Studio' },
  errorMessage:   { type: String, default: '' },
  loadingMessage: { type: String, default: '' },
  projectId:   { type: String, default: '' },
})

// ── State ──────────────────────────────────────────────────────────
const router = useRouter()
const route  = useRoute()
const session       = ref(getSwarmbookSession())
const health        = ref(null)
const isSidebarOpen = ref(false)
let healthInterval  = null

// ── Computed ───────────────────────────────────────────────────────
const hasSimulation = computed(() =>
  !!(session.value.simulationRun?.reader_personas?.length)
)

const activeProjectId = computed(() =>
  props.projectId || session.value.projectId || ''
)

const healthSummary = computed(() => {
  if (!health.value) return { ollama: 'Checking…', neo4j: 'Checking…' }
  return {
    ollama: health.value.ollama?.ok ? 'Connected' : 'Offline',
    neo4j:  health.value.neo4j?.ok  ? 'Connected' : 'Offline',
  }
})

// Full workflow steps spec (11 items from the request)
const workflowSteps = computed(() => {
  const pId = activeProjectId.value
  const projectRoute = (name) =>
    pId ? { name, params: { projectId: pId } } : { name: 'SwarmbookHome' }

  const hasManuscript  = !!(session.value.manuscript?.text)
  const hasEvidence    = !!(session.value.evidencePack)
  const hasReport      = !!(session.value.report)
  const hasSimRun      = hasSimulation.value

  return [
    {
      index: '01', label: 'Projects',      name: 'SwarmbookHome',
      to: { name: 'SwarmbookHome' }, disabled: false,
    },
    {
      index: '02', label: 'New Test',      name: 'NewSimulationWizard',
      to: { name: 'NewSimulationWizard' }, disabled: false,
    },
    {
      index: '03', label: 'Upload',        name: 'SwarmbookUpload',
      to: projectRoute('SwarmbookUpload'), disabled: !pId,
    },
    {
      index: '04', label: 'Evidence Packs', name: 'SwarmbookEvidence',
      to: projectRoute('SwarmbookEvidence'), disabled: !pId || !hasEvidence,
    },
    {
      index: '05', label: 'Reader Swarm',  name: 'SwarmbookSimulation',
      to: projectRoute('SwarmbookSimulation'), disabled: !pId || !hasEvidence,
    },
    {
      index: '06', label: 'Run',           name: 'SwarmbookSimulationRun',
      to: projectRoute('SwarmbookSimulationRun'), disabled: !pId || !hasEvidence,
    },
    {
      index: '07', label: 'Report',        name: 'SwarmbookReport',
      to: projectRoute('SwarmbookReport'), disabled: !pId || !hasReport,
    },
    {
      index: '08', label: 'Ask Readers',   name: 'SwarmbookPersonas',
      to: projectRoute('SwarmbookPersonas'), disabled: !pId || !hasSimRun,
    },
    {
      index: '09', label: 'Compare Drafts', name: 'SwarmbookCompare',
      to: projectRoute('SwarmbookCompare'), disabled: !pId,
    },
  ]
})

// ── Watchers ───────────────────────────────────────────────────────
watch(() => route.path, () => {
  session.value = getSwarmbookSession()
  // Close mobile sidebar on navigation
  closeSidebar()
})

// ── Helpers ────────────────────────────────────────────────────────
function statusTone(val) {
  if (val === 'Connected') return 'ready'
  if (val === 'Checking…') return 'loading'
  return 'offline'
}

function truncateId(val) {
  if (!val) return ''
  return val.replace('proj_', '').slice(0, 8).toUpperCase()
}

function handleStepClick(step) {
  if (step.disabled) return
  router.push(step.to)
}

// ── Navigation actions ─────────────────────────────────────────────
function goToHome()      { router.push({ name: 'SwarmbookHome' }) }
function goToSettings()  { router.push({ name: 'SwarmbookSettings', params: { projectId: activeProjectId.value || undefined } }) }
function goToReport()    { if (activeProjectId.value) router.push({ name: 'SwarmbookReport',  params: { projectId: activeProjectId.value } }) }
function goToPersonas()  { if (activeProjectId.value && hasSimulation.value) router.push({ name: 'SwarmbookPersonas', params: { projectId: activeProjectId.value } }) }
function goToCompare()   { if (activeProjectId.value) router.push({ name: 'SwarmbookCompare', params: { projectId: activeProjectId.value } }) }
function exitToMiroFish(){ router.push('/') }

function startNewTest() {
  clearSwarmbookSession()
  session.value = getSwarmbookSession()
  router.push({ name: 'NewSimulationWizard' })
}

// ── Sidebar ────────────────────────────────────────────────────────
function toggleSidebar() { isSidebarOpen.value = !isSidebarOpen.value }
function closeSidebar()  { isSidebarOpen.value = false }

// Close sidebar on Escape
function onKeydown(e) {
  if (e.key === 'Escape' && isSidebarOpen.value) closeSidebar()
}

// ── Health polling ─────────────────────────────────────────────────
async function loadHealth() {
  try {
    const res = await getBookSimHealth()
    health.value = res.data
  } catch {
    // silently degrade; status strip shows Offline
  }
}

onMounted(() => {
  loadHealth()
  healthInterval = setInterval(loadHealth, 30000)
  document.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  clearInterval(healthInterval)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
/* ═══════════════════════════════════════════════
   SHELL ROOT
   ═══════════════════════════════════════════════ */
.swarmbook-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--sb-surface-primary);
  color: var(--sb-text-main);
  font-family: var(--sb-font-sans);
}

/* ── Skip Link (a11y) ─────────────────────────── */
.skip-link {
  position: absolute;
  top: -100%;
  left: var(--sb-space-4);
  background: var(--sb-color-brand);
  color: #fff;
  padding: var(--sb-space-2) var(--sb-space-4);
  border-radius: var(--sb-radius-md);
  font-weight: var(--sb-weight-semibold);
  font-size: var(--sb-text-sm);
  z-index: 9999;
  text-decoration: none;
  transition: top 0.1s;
}
.skip-link:focus { top: var(--sb-space-2); }

/* ═══════════════════════════════════════════════
   TOP HEADER
   ═══════════════════════════════════════════════ */
.shell-header {
  height: 60px;
  background: var(--sb-surface-dark);
  color: var(--sb-text-on-dark);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--sb-space-4);
  border-bottom: 1px solid var(--sb-border-dark);
  position: sticky;
  top: 0;
  z-index: 200;
  gap: var(--sb-space-4);
  flex-shrink: 0;
}

/* Brand zone */
.brand-zone {
  display: flex;
  align-items: center;
  gap: var(--sb-space-3);
  flex-shrink: 0;
}

.brand-group {
  display: inline-flex;
  align-items: center;
  gap: var(--sb-space-2);
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: var(--sb-space-1) var(--sb-space-2);
  border-radius: var(--sb-radius-md);
  outline: none;
}
.brand-group:focus-visible { outline: var(--sb-focus-ring); outline-offset: 2px; }

.logo-icon { font-size: 1.4rem; line-height: 1; }

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-title {
  font-family: var(--sb-font-mono);
  font-weight: var(--sb-weight-extrabold);
  font-size: 0.88rem;
  letter-spacing: 1px;
}

.brand-tagline {
  font-size: 0.62rem;
  opacity: 0.65;
  letter-spacing: 0.4px;
}

/* Hamburger */
.menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: var(--sb-space-2);
  border-radius: var(--sb-radius-sm);
  outline: none;
  flex-shrink: 0;
}
.menu-toggle:focus-visible { outline: var(--sb-focus-ring); }

.bar {
  display: block;
  width: 18px;
  height: 2px;
  background: #ffffff;
  border-radius: 2px;
  transition: transform 0.22s ease, opacity 0.22s ease;
  transform-origin: center;
}
.bar.open:nth-child(1) { transform: translateY(6px) rotate(45deg); }
.bar.open:nth-child(2) { opacity: 0; transform: scaleX(0); }
.bar.open:nth-child(3) { transform: translateY(-6px) rotate(-45deg); }

/* Global top nav */
.top-nav {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  justify-content: flex-end;
  flex-wrap: nowrap;
  overflow: hidden;
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--sb-space-1);
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.65);
  padding: 6px 12px;
  font-family: var(--sb-font-sans);
  font-size: 0.82rem;
  font-weight: var(--sb-weight-semibold);
  cursor: pointer;
  border-radius: var(--sb-radius-md);
  transition: color 0.15s, background 0.15s;
  outline: none;
  white-space: nowrap;
  position: relative;
}

.nav-btn:hover:not(:disabled) {
  color: #ffffff;
  background: rgba(255,255,255,0.06);
}

.nav-btn.active {
  color: var(--sb-color-brand);
  background: rgba(255,69,0,0.12);
}

/* Active underline indicator */
.nav-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 12px;
  right: 12px;
  height: 2px;
  background: var(--sb-color-brand);
  border-radius: 2px 2px 0 0;
}

.nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  pointer-events: none;
}

.nav-btn:focus-visible {
  outline: var(--sb-focus-ring);
  outline-offset: 2px;
}

.nav-icon    { width: 14px; height: 14px; flex-shrink: 0; }
.nav-icon-sm { width: 11px; height: 11px; flex-shrink: 0; opacity: 0.7; }

.nav-settings { color: rgba(255,255,255,0.5); }
.nav-settings:hover { color: #ffffff; }

.nav-divider {
  width: 1px;
  height: 20px;
  background: rgba(255,255,255,0.12);
  margin: 0 4px;
  flex-shrink: 0;
}

/* Original MiroFish button — distinct from regular nav */
.nav-mirofish {
  color: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.14);
  font-family: var(--sb-font-mono);
  font-size: 0.75rem;
}
.nav-mirofish:hover {
  color: var(--sb-color-brand);
  border-color: var(--sb-color-brand);
  background: rgba(255,69,0,0.08);
}

/* ═══════════════════════════════════════════════
   STATUS STRIP
   ═══════════════════════════════════════════════ */
.status-strip {
  height: 30px;
  background: var(--sb-surface-dark-2);
  border-bottom: 1px solid #0d1929;
  display: flex;
  align-items: center;
  gap: var(--sb-space-3);
  padding: 0 var(--sb-space-4);
  font-family: var(--sb-font-mono);
  font-size: 0.68rem;
  color: #94a3b8;
  overflow-x: auto;
  flex-shrink: 0;
  scrollbar-width: none;
}
.status-strip::-webkit-scrollbar { display: none; }

.strip-item {
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}

.strip-sep {
  color: #334155;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.strip-label {
  color: #475569;
  font-weight: var(--sb-weight-medium);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.strip-val {
  font-weight: var(--sb-weight-semibold);
  font-size: 0.68rem;
}
.strip-val.ready   { color: var(--sb-color-ready); }
.strip-val.loading { color: var(--sb-color-mixed); }
.strip-val.offline { color: var(--sb-color-offline); }

.strip-icon { font-size: 0.7rem; }

.strip-badge {
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  padding: 1px 5px;
  border-radius: var(--sb-radius-sm);
  text-transform: lowercase;
}
.strip-badge.local_only  { background: var(--sb-privacy-local-bg);  color: var(--sb-privacy-local-text);  }
.strip-badge.hybrid_safe { background: var(--sb-privacy-hybrid-bg); color: var(--sb-privacy-hybrid-text); }
.strip-badge.cloud_quality { background: var(--sb-privacy-cloud-bg); color: var(--sb-privacy-cloud-text); }

.strip-profile {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: var(--sb-weight-medium);
}

.strip-project-id {
  font-size: 0.68rem;
  font-weight: var(--sb-weight-bold);
  color: var(--sb-color-brand);
  letter-spacing: 0.5px;
}

/* Pulse dot (reused from tokens pattern) */
.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #334155;
  flex-shrink: 0;
}
.pulse-dot.ready {
  background: var(--sb-color-ready);
  box-shadow: 0 0 6px var(--sb-color-ready);
  animation: sb-pulse 2s infinite;
}
.pulse-dot.loading {
  background: var(--sb-color-mixed);
  animation: sb-pulse 2s infinite;
}
.pulse-dot.offline { background: var(--sb-color-offline); }

@keyframes sb-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.45; }
}

/* ═══════════════════════════════════════════════
   BODY CONTAINER
   ═══════════════════════════════════════════════ */
.shell-container {
  display: flex;
  flex: 1;
  min-height: 0; /* allow flex children to shrink */
  position: relative;
}

/* ─── Mobile backdrop ─────────────────────────── */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,0.45);
  backdrop-filter: blur(2px);
  z-index: 140;
}

/* ═══════════════════════════════════════════════
   SIDEBAR / WORKFLOW RAIL
   ═══════════════════════════════════════════════ */
.shell-sidebar {
  width: 240px;
  background: var(--sb-bg-card);
  border-right: 1px solid var(--sb-border-color);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 90px; /* 60px header + 30px status strip */
  height: calc(100vh - 90px);
  z-index: 150;
  flex-shrink: 0;
  transition: transform 0.28s ease;
  overflow: hidden;
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  padding: var(--sb-space-4) var(--sb-space-2) var(--sb-space-4);
  scrollbar-width: thin;
  scrollbar-color: var(--sb-border-color) transparent;
}
.sidebar-inner::-webkit-scrollbar { width: 4px; }
.sidebar-inner::-webkit-scrollbar-thumb { background: var(--sb-border-color); border-radius: 4px; }

/* Mobile-only global nav block (hidden on desktop) */
.sidebar-global-nav { display: none; }

/* Section labels */
.rail-section-label {
  font-family: var(--sb-font-mono);
  font-size: 0.62rem;
  color: #94a3b8;
  font-weight: var(--sb-weight-bold);
  letter-spacing: 1.2px;
  padding: 0 var(--sb-space-2) var(--sb-space-2);
  text-transform: uppercase;
}

/* ── Workflow step links ─────────────────────── */
.workflow-rail {
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
}

.step-link {
  display: flex;
  align-items: center;
  gap: var(--sb-space-2);
  padding: 9px var(--sb-space-3);
  border-radius: var(--sb-radius-md);
  text-decoration: none;
  color: var(--sb-text-muted);
  font-size: 0.83rem;
  font-weight: var(--sb-weight-semibold);
  transition: background 0.15s, color 0.15s;
  position: relative;
  outline: none;
  cursor: pointer;
}

.step-link:hover:not(.step-disabled) {
  background: var(--sb-surface-secondary);
  color: var(--sb-text-main);
}

/* Active state: left accent bar */
.step-link.step-active {
  background: rgba(255,69,0,0.07);
  color: var(--sb-color-brand);
}

.step-accent {
  position: absolute;
  left: 0;
  top: 6px;
  bottom: 6px;
  width: 3px;
  border-radius: 0 2px 2px 0;
  background: transparent;
  transition: background 0.15s;
}
.step-link.step-active .step-accent { background: var(--sb-color-brand); }

.step-link.step-disabled {
  opacity: 0.38;
  cursor: not-allowed;
  pointer-events: none;
}

.step-link:focus-visible { outline: var(--sb-focus-ring); outline-offset: 1px; }

.step-num {
  font-family: var(--sb-font-mono);
  font-size: 0.62rem;
  color: #94a3b8;
  min-width: 20px;
  flex-shrink: 0;
}
.step-link.step-active .step-num { color: var(--sb-color-brand); opacity: 0.8; }

.step-label { flex: 1; line-height: 1.2; }

.step-badge {
  font-family: var(--sb-font-mono);
  font-size: 0.58rem;
  background: var(--sb-color-brand);
  color: #fff;
  padding: 1px 5px;
  border-radius: var(--sb-radius-full);
}

/* ── Sidebar footer ────────────────────────── */
.sidebar-footer {
  margin-top: auto;
  padding-top: var(--sb-space-2);
}

.sidebar-divider {
  height: 1px;
  background: var(--sb-border-color);
  margin: var(--sb-space-3) var(--sb-space-2);
}

.sidebar-footer-btn {
  display: flex;
  align-items: center;
  gap: var(--sb-space-2);
  width: 100%;
  background: transparent;
  border: none;
  color: var(--sb-text-muted);
  padding: 9px var(--sb-space-3);
  border-radius: var(--sb-radius-md);
  font-family: var(--sb-font-sans);
  font-size: 0.83rem;
  font-weight: var(--sb-weight-semibold);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  outline: none;
  text-align: left;
}
.sidebar-footer-btn:hover       { background: var(--sb-surface-secondary); color: var(--sb-text-main); }
.sidebar-footer-btn:focus-visible { outline: var(--sb-focus-ring); outline-offset: 1px; }
.sidebar-footer-btn.footer-active { color: var(--sb-color-brand); background: rgba(255,69,0,0.07); }

/* MiroFish link — special styling */
.mirofish-link { color: var(--sb-text-hint); }
.mirofish-link:hover {
  color: var(--sb-color-brand);
  background: rgba(255,69,0,0.06);
}

.footer-icon { width: 14px; height: 14px; flex-shrink: 0; }

/* ═══════════════════════════════════════════════
   MAIN WORKSPACE
   ═══════════════════════════════════════════════ */
.shell-main {
  flex: 1;
  padding: var(--sb-space-8) 40px 60px;
  overflow-y: auto;
  min-height: 0;
  max-width: 100%;
  outline: none; /* for programmatic focus (skip link) */
}

.workspace-header { margin-bottom: var(--sb-space-8); }

.workspace-eyebrow {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  color: var(--sb-color-brand);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: var(--sb-weight-bold);
  margin: 0 0 var(--sb-space-2);
}

.workspace-title {
  font-size: var(--sb-text-3xl);
  font-weight: var(--sb-weight-extrabold);
  color: var(--sb-text-heading);
  letter-spacing: -0.5px;
  line-height: var(--sb-leading-tight);
  margin: 0;
}

.workspace-subtitle {
  font-size: var(--sb-text-md);
  color: var(--sb-text-hint);
  margin-top: var(--sb-space-2);
  max-width: 780px;
  line-height: var(--sb-leading-relaxed);
}

/* ─── Banners ─────────────────────────────────── */
.shell-banner {
  display: flex;
  align-items: flex-start;
  gap: var(--sb-space-3);
  padding: var(--sb-space-3) var(--sb-space-4);
  margin-bottom: var(--sb-space-5);
  border-radius: var(--sb-radius-lg);
  border-left: 4px solid var(--sb-color-offline);
  background: var(--sb-status-error-bg);
}

.shell-banner.loading-banner {
  border-left-color: var(--sb-color-info);
  background: var(--sb-status-info-bg);
}

.banner-icon {
  font-size: 1.1rem;
  line-height: 1;
  margin-top: 2px;
  flex-shrink: 0;
}

.banner-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(59,130,246,0.3);
  border-top-color: var(--sb-color-info);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
  margin-top: 2px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.banner-body { display: flex; flex-direction: column; gap: 2px; }

.banner-title {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: var(--sb-weight-bold);
  color: var(--sb-status-error-text);
}
.loading-banner .banner-title { color: var(--sb-status-info-text); }

.shell-banner p {
  font-size: var(--sb-text-base);
  margin: 0;
  color: #7f1d1d;
}
.loading-banner p { color: var(--sb-status-info-text); }

.workspace-content { margin-top: var(--sb-space-1); }

/* ── Primary button (used inside AppShell portal) */
.primary-btn {
  background: var(--sb-color-brand);
  border: 1px solid var(--sb-color-brand);
  color: #ffffff;
  padding: var(--sb-space-2) 18px;
  font-weight: var(--sb-weight-semibold);
  font-size: var(--sb-text-base);
  cursor: pointer;
  border-radius: var(--sb-radius-md);
  transition: all 0.2s;
  outline: none;
}
.primary-btn:hover        { background: var(--sb-color-brand-hover); }
.primary-btn:focus-visible { outline: var(--sb-focus-ring); outline-offset: var(--sb-focus-offset); }

/* ═══════════════════════════════════════════════
   RESPONSIVE — TABLET / MOBILE (≤900px)
   ═══════════════════════════════════════════════ */
@media (max-width: 900px) {
  /* Show hamburger */
  .menu-toggle { display: flex; }

  /* Hide full top-nav on mobile */
  .top-nav { display: none; }

  /* Sidebar becomes an off-canvas drawer */
  .shell-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    height: 100dvh;
    transform: translateX(-100%);
    box-shadow: 4px 0 24px rgba(0,0,0,0.15);
    z-index: 160;
  }

  .shell-sidebar.sidebar-open { transform: translateX(0); }

  /* Show global nav buttons inside the drawer */
  .sidebar-global-nav {
    display: flex;
    flex-direction: column;
    gap: 1px;
    margin-bottom: var(--sb-space-2);
  }

  .sidebar-global-btn {
    display: flex;
    align-items: center;
    gap: var(--sb-space-2);
    width: 100%;
    background: transparent;
    border: none;
    color: var(--sb-text-muted);
    padding: 10px var(--sb-space-3);
    border-radius: var(--sb-radius-md);
    font-family: var(--sb-font-sans);
    font-size: 0.9rem;
    font-weight: var(--sb-weight-semibold);
    cursor: pointer;
    text-align: left;
    outline: none;
  }
  .sidebar-global-btn:hover:not(:disabled) {
    background: var(--sb-surface-secondary);
    color: var(--sb-text-main);
  }
  .sidebar-global-btn:disabled { opacity: 0.35; cursor: not-allowed; }
  .sidebar-global-btn:focus-visible { outline: var(--sb-focus-ring); }

  .sg-icon { font-size: 1rem; width: 20px; text-align: center; }

  /* Status strip: compact on mobile */
  .status-strip {
    font-size: 0.62rem;
    padding: 0 var(--sb-space-3);
    gap: var(--sb-space-2);
  }
  .strip-label { display: none; }

  /* Main content: full width, smaller padding */
  .shell-main { padding: var(--sb-space-5) var(--sb-space-4) 60px; }

  .workspace-title { font-size: var(--sb-text-2xl); }
}

@media (max-width: 480px) {
  .shell-header { padding: 0 var(--sb-space-3); }
  .brand-tagline { display: none; }
  .status-strip { height: 26px; }
}

/* Reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .bar, .step-link, .nav-btn, .sidebar-footer-btn, .shell-sidebar { transition: none; }
  .banner-spinner, .pulse-dot.ready, .pulse-dot.loading { animation: none; }
}
</style>
