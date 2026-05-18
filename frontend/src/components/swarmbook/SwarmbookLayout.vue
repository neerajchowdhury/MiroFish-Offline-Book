<template>
  <div class="swarmbook-layout">
    <header class="swarmbook-header">
      <div class="brand-group">
        <button class="brand-button" @click="router.push('/')">MIROFISH OFFLINE</button>
        <span class="brand-divider">/</span>
        <button class="brand-button secondary" @click="router.push({ name: 'SwarmbookHome' })">SWARMBOOK</button>
      </div>
      <div class="status-pill" :class="statusTone">
        <span class="status-dot"></span>
        <span>{{ statusText }}</span>
      </div>
    </header>

    <nav class="swarmbook-steps">
      <router-link
        v-for="step in steps"
        :key="step.name"
        class="step-link"
        :class="{ active: activeRoute === step.name }"
        :to="step.to"
      >
        <span class="step-index">{{ step.index }}</span>
        <span class="step-label">{{ step.label }}</span>
      </router-link>
    </nav>

    <main class="swarmbook-main">
      <section class="hero-strip">
        <p class="eyebrow">{{ eyebrow }}</p>
        <h1>{{ title }}</h1>
        <p class="subtitle">{{ subtitle }}</p>
      </section>

      <section v-if="errorMessage" class="state-box error">
        <strong>Error</strong>
        <p>{{ errorMessage }}</p>
      </section>

      <section v-if="loadingMessage" class="state-box loading">
        <strong>Loading</strong>
        <p>{{ loadingMessage }}</p>
      </section>

      <slot />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

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
    default: 'Swarmbook Frontend',
  },
  statusText: {
    type: String,
    default: 'Ready',
  },
  statusTone: {
    type: String,
    default: 'ready',
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

const steps = computed(() => {
  const projectId = props.projectId || ''
  const projectRoute = (name) => {
    if (!projectId) {
      return { name: 'SwarmbookHome' }
    }
    return { name, params: { projectId } }
  }

  return [
    { index: '01', label: 'Project', name: 'SwarmbookHome', to: { name: 'SwarmbookHome' } },
    { index: '02', label: 'Upload', name: 'SwarmbookUpload', to: projectRoute('SwarmbookUpload') },
    { index: '03', label: 'Metadata', name: 'SwarmbookMetadata', to: projectRoute('SwarmbookMetadata') },
    { index: '04', label: 'Evidence', name: 'SwarmbookEvidence', to: projectRoute('SwarmbookEvidence') },
    { index: '05', label: 'Simulate', name: 'SwarmbookSimulation', to: projectRoute('SwarmbookSimulation') },
    { index: '06', label: 'Report', name: 'SwarmbookReport', to: projectRoute('SwarmbookReport') },
    { index: '07', label: 'Personas', name: 'SwarmbookPersonas', to: projectRoute('SwarmbookPersonas') },
    { index: '08', label: 'Compare', name: 'SwarmbookCompare', to: projectRoute('SwarmbookCompare') },
  ]
})
</script>

<style scoped>
.swarmbook-layout {
  min-height: 100vh;
  background: #ffffff;
  color: #111111;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
}

.swarmbook-header {
  height: 60px;
  background: #000000;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-button {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 1px;
}

.brand-button.secondary {
  font-weight: 600;
  opacity: 0.82;
}

.brand-divider {
  opacity: 0.5;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 8px 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #7bd389;
}

.status-pill.loading .status-dot {
  background: #ffb347;
}

.status-pill.error .status-dot {
  background: #ff6b6b;
}

.swarmbook-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 18px 28px 0;
  border-bottom: 1px solid #ececec;
}

.step-link {
  text-decoration: none;
  color: #555555;
  border: 1px solid #e4e4e4;
  padding: 10px 12px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.step-link.active {
  border-color: #000000;
  color: #000000;
  background: #fafafa;
}

.step-index {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
}

.step-label {
  font-size: 0.9rem;
  font-weight: 600;
}

.swarmbook-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 28px 56px;
}

.hero-strip {
  margin-bottom: 24px;
}

.hero-strip h1 {
  font-size: 2.4rem;
  line-height: 1.1;
  margin: 0 0 10px;
}

.eyebrow {
  font-family: 'JetBrains Mono', monospace;
  color: #ff4500;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.subtitle {
  color: #666666;
  max-width: 840px;
  line-height: 1.6;
}

.state-box {
  border: 1px solid #e3e3e3;
  padding: 14px 16px;
  margin-bottom: 18px;
}

.state-box.error {
  border-color: #efc3c3;
  background: #fff8f8;
}

.state-box.loading {
  border-color: #eadfb2;
  background: #fffdf4;
}

.state-box strong {
  display: block;
  margin-bottom: 6px;
}

@media (max-width: 900px) {
  .swarmbook-header {
    height: auto;
    padding: 14px 20px;
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }

  .swarmbook-steps {
    padding: 16px 20px 0;
  }

  .swarmbook-main {
    padding: 28px 20px 48px;
  }

  .hero-strip h1 {
    font-size: 1.9rem;
  }
}
</style>
