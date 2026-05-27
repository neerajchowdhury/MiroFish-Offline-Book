<template>
  <router-view />
</template>

<script setup>
// Use Vue Router to manage pages
</script>

<style>
/* Global style reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #000000;
}

::-webkit-scrollbar-thumb:hover {
  background: #333333;
}

button {
  font-family: inherit;
}

/* ========== HOME PAGE STYLES ========== */

.home-container {
  min-height: 100vh;
  background: #FFFFFF;
  font-family: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  color: #000000;
}

.navbar {
  height: 60px;
  background: #000000;
  color: #FFFFFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
}

.nav-links {
  display: flex;
  align-items: center;
}

.github-link {
  color: #FFFFFF;
  text-decoration: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.2s;
}

.github-link:hover {
  opacity: 0.8;
}

.arrow {
  font-family: sans-serif;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 40px;
}

.hero-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 80px;
  position: relative;
}

.hero-left {
  flex: 1;
  padding-right: 60px;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
}

.orange-tag {
  background: #FF4500;
  color: #FFFFFF;
  padding: 4px 10px;
  font-weight: 700;
  letter-spacing: 1px;
  font-size: 0.75rem;
}

.version-text {
  color: #999;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.main-title {
  font-size: 4.5rem;
  line-height: 1.2;
  font-weight: 500;
  margin: 0 0 40px 0;
  letter-spacing: -2px;
  color: #000000;
}

.gradient-text {
  background: linear-gradient(90deg, #000000 0%, #444444 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-desc {
  font-size: 1.05rem;
  line-height: 1.8;
  color: #666666;
  max-width: 640px;
  margin-bottom: 50px;
  font-weight: 400;
  text-align: justify;
}

.hero-desc p {
  margin-bottom: 1.5rem;
}

.highlight-bold {
  color: #000000;
  font-weight: 700;
}

.highlight-orange {
  color: #FF4500;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}

.highlight-code {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 2px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
  color: #000000;
  font-weight: 600;
}

.slogan-text {
  font-size: 1.2rem;
  font-weight: 520;
  color: #000000;
  letter-spacing: 1px;
  border-left: 3px solid #FF4500;
  padding-left: 15px;
  margin-top: 20px;
}

.blinking-cursor {
  color: #FF4500;
  animation: blink 1s step-end infinite;
  font-weight: 700;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.decoration-square {
  width: 16px;
  height: 16px;
  background: #FF4500;
}

.hero-right {
  flex: 0.8;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
}

.logo-container {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding-right: 40px;
}

.hero-logo {
  max-width: 500px;
  width: 100%;
}

.scroll-down-btn {
  width: 40px;
  height: 40px;
  border: 1px solid #E5E5E5;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #FF4500;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.scroll-down-btn:hover {
  border-color: #FF4500;
}

.dashboard-section {
  display: flex;
  gap: 60px;
  border-top: 1px solid #E5E5E5;
  padding-top: 60px;
  align-items: flex-start;
}

.dashboard-section .left-panel,
.dashboard-section .right-panel {
  display: flex;
  flex-direction: column;
}

.left-panel {
  flex: 0.8;
}

.panel-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #999;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.status-dot {
  color: #FF4500;
  font-size: 0.8rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 520;
  margin: 0 0 15px 0;
}

.section-desc {
  color: #666666;
  margin-bottom: 25px;
  line-height: 1.6;
}

.metrics-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.metric-card {
  border: 1px solid #E5E5E5;
  padding: 20px 30px;
  min-width: 150px;
}

.metric-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.8rem;
  font-weight: 520;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 0.85rem;
  color: #999;
}

.steps-container {
  border: 1px solid #E5E5E5;
  padding: 30px;
  position: relative;
}

.steps-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.step-num {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #000000;
  opacity: 0.3;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 520;
  font-size: 1rem;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.85rem;
  color: #666666;
}

.right-panel {
  flex: 1.2;
}

.console-box {
  border: 1px solid #CCC;
  padding: 8px;
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
}

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #666;
}

.upload-zone {
  border: 1px dashed #CCC;
  height: 200px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover {
  background: #F0F0F0;
  border-color: #999;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 40px;
  height: 40px;
  border: 1px solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: #999;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.upload-hint {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: #999;
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  padding: 8px 12px;
  border: 1px solid #EEE;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #EEE;
}

.console-divider span {
  padding: 0 15px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #BBB;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid #DDD;
  background: #FAFAFA;
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #AAA;
}

.start-engine-btn {
  width: 100%;
  background: #000000;
  color: #FFFFFF;
  border: none;
  padding: 20px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.start-engine-btn:not(:disabled) {
  background: #000000;
  border: 1px solid #000000;
  animation: pulse-border 2s infinite;
}

.start-engine-btn:hover:not(:disabled) {
  background: #FF4500;
  border-color: #FF4500;
  transform: translateY(-2px);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #E5E5E5;
  color: #999;
  cursor: not-allowed;
  transform: none;
  border: 1px solid #E5E5E5;
}

@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); }
  70% { box-shadow: 0 0 0 6px rgba(0, 0, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
}

@media (max-width: 1024px) {
  .dashboard-section {
    flex-direction: column;
  }
  .hero-section {
    flex-direction: column;
  }
  .hero-left {
    padding-right: 0;
    margin-bottom: 40px;
  }
  .hero-logo {
    max-width: 200px;
    margin-bottom: 20px;
  }
}

/* ========== SWARMBOOK PREMIUM REDESIGN THEME VARIABLES & OVERRIDES ========== */
:root {
  --sb-bg-base: #f8fafc;
  --sb-bg-card: #ffffff;
  --sb-border-color: #e2e8f0;
  --sb-border-hover: #cbd5e1;
  --sb-text-main: #0f172a;
  --sb-text-muted: #64748b;
  --sb-focus-outline: 2px solid #ff4500;
  
  /* Signal tones */
  --sb-color-ready: #10b981;
  --sb-color-mixed: #f59e0b;
  --sb-color-offline: #ef4444;
  --sb-color-brand: #ff4500;
}

/* Global inputs focus rings */
.swarmbook-shell select:focus-visible,
.swarmbook-shell input:focus-visible,
.swarmbook-shell textarea:focus-visible,
.swarmbook-shell button:focus-visible,
.new-wizard-container select:focus-visible,
.new-wizard-container input:focus-visible,
.new-wizard-container textarea:focus-visible,
.new-wizard-container button:focus-visible {
  outline: var(--sb-focus-outline) !important;
  outline-offset: 2px !important;
}

/* Premium Card Styles */
.swarmbook-shell .card,
.new-wizard-container .card,
.swarmbook-shell .dashboard-card {
  background: var(--sb-bg-card) !important;
  border: 1px solid var(--sb-border-color) !important;
  border-radius: 8px !important;
  padding: 24px !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
  transition: all 0.2s ease-in-out !important;
}

.swarmbook-shell .card:hover,
.new-wizard-container .card:hover,
.swarmbook-shell .dashboard-card:hover {
  border-color: var(--sb-border-hover) !important;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06) !important;
}

/* Typography polish */
.swarmbook-shell h1, .new-wizard-container h1 {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  font-weight: 800 !important;
  letter-spacing: -0.5px !important;
  color: var(--sb-text-main) !important;
}

.swarmbook-shell h2, .new-wizard-container h2 {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: -0.3px !important;
  color: var(--sb-text-main) !important;
  margin-top: 0;
}

.swarmbook-shell h3, .new-wizard-container h3 {
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  font-weight: 600 !important;
  color: var(--sb-text-main) !important;
}

/* Swarmbook buttons premium polish */
.swarmbook-shell .primary-btn,
.new-wizard-container .primary-btn {
  background: var(--sb-text-main) !important;
  color: #ffffff !important;
  border: 1px solid var(--sb-text-main) !important;
  padding: 12px 24px !important;
  min-height: 44px !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  transition: all 0.2s ease !important;
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  letter-spacing: 0.2px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.swarmbook-shell .primary-btn:hover:not(:disabled),
.new-wizard-container .primary-btn:hover:not(:disabled) {
  background: var(--sb-color-brand) !important;
  border-color: var(--sb-color-brand) !important;
}

.swarmbook-shell .ghost-btn,
.new-wizard-container .ghost-btn {
  background: transparent !important;
  color: var(--sb-text-muted) !important;
  border: 1px solid var(--sb-border-color) !important;
  padding: 12px 24px !important;
  min-height: 44px !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  transition: all 0.2s ease !important;
  font-family: 'Space Grotesk', system-ui, sans-serif !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.swarmbook-shell .ghost-btn:hover:not(:disabled),
.new-wizard-container .ghost-btn:hover:not(:disabled) {
  background: #f1f5f9 !important;
  border-color: var(--sb-border-hover) !important;
  color: var(--sb-text-main) !important;
}

/* Styled Table resets for premium visual look */
.swarmbook-shell table.styled-table,
.new-wizard-container table.styled-table {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 1px solid var(--sb-border-color) !important;
  border-radius: 6px !important;
  overflow: hidden !important;
}

.swarmbook-shell table.styled-table th,
.new-wizard-container table.styled-table th {
  background: #f8fafc !important;
  color: var(--sb-text-muted) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  padding: 12px 16px !important;
  border-bottom: 1px solid var(--sb-border-color) !important;
  font-weight: 700 !important;
}

.swarmbook-shell table.styled-table td,
.new-wizard-container table.styled-table td {
  padding: 14px 16px !important;
  border-bottom: 1px solid var(--sb-border-color) !important;
  font-size: 0.85rem !important;
  color: #334155 !important;
}

.swarmbook-shell table.styled-table tr:last-child td,
.new-wizard-container table.styled-table tr:last-child td {
  border-bottom: none !important;
}

/* Empty states layout polish */
.swarmbook-shell .empty-compare-state,
.swarmbook-shell .empty-projects-state,
.swarmbook-shell .empty-report-state {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 48px 24px !important;
  text-align: center !important;
  border: 1px dashed var(--sb-border-hover) !important;
  border-radius: 8px !important;
  background: #f8fafc !important;
}

/* Scrollbar styling overrides specifically inside Swarmbook UI */
.swarmbook-shell ::-webkit-scrollbar-thumb,
.new-wizard-container ::-webkit-scrollbar-thumb {
  background: #cbd5e1 !important;
  border-radius: 4px !important;
}

.swarmbook-shell ::-webkit-scrollbar-thumb:hover,
.new-wizard-container ::-webkit-scrollbar-thumb:hover {
  background: #94a3b8 !important;
}

/* Accessibility contrast overrides for secondary and hint text to satisfy WCAG 2.2 AA (4.5:1 ratio) */
.swarmbook-shell .microcopy,
.new-wizard-container .microcopy,
.swarmbook-shell .formats-label,
.new-wizard-container .formats-label,
.swarmbook-shell .slider-marks span,
.new-wizard-container .slider-marks span,
.swarmbook-shell .step-hint,
.new-wizard-container .step-hint,
.swarmbook-shell .section-hint,
.new-wizard-container .section-hint,
.swarmbook-shell .seed-hint-text,
.new-wizard-container .seed-hint-text,
.swarmbook-shell .action-desc,
.new-wizard-container .action-desc,
.swarmbook-shell .settings-hint,
.swarmbook-shell .persona-meta,
.swarmbook-shell .persona-chat-timestamp,
.swarmbook-shell .suggested-question-hint,
.swarmbook-shell .evidence-citation-meta,
.swarmbook-shell .project-meta,
.new-wizard-container .stepper-item:not(.active),
.swarmbook-shell .badge.hybrid_safe,
.swarmbook-shell .spec-label {
  color: var(--sb-text-muted) !important;
}

/* Enforce high-contrast dark color for other minor text roles */
.swarmbook-shell .formats-label {
  color: var(--sb-text-muted) !important;
}

/* Reduced motion preference support */
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-delay: -1ms !important;
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    background-attachment: scroll !important;
    scroll-behavior: auto !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
  }
}
</style>
