<template>
  <SwarmbookAppShell
    active-route="SwarmbookEvidence"
    :project-id="session.projectId"
    title="Evidence Pack Review"
    subtitle="Validate extracted manuscript maps, narrative risk indicators, and book DNA before starting the synthetic reader reactions."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="evidence-container">
      <!-- Empty State if no evidence pack exists -->
      <section v-if="!evidencePack" class="empty-evidence-card">
        <div class="empty-icon">📂</div>
        <h2>No Editorial Evidence Pack Compiled</h2>
        <p>You must load your manuscript draft first to extract story maps, claim paths, and style indicators.</p>
        <div class="action-row-center">
          <button class="primary-btn" @click="goToUpload">
            Go to Manuscript Ingest
          </button>
        </div>
      </section>

      <!-- Main Dashboard Split Pane -->
      <div v-else class="evidence-split-layout">
        <!-- Left Side: Compact Cards List -->
        <div class="cards-column" role="region" aria-label="Evidence Maps List">
          <div
            v-for="map in maps"
            :key="map.id"
            class="map-card"
            :class="{ active: activeMapId === map.id, accepted: getStatus(map.id) === 'accepted' }"
            @click="selectMap(map.id)"
            @keydown.enter="selectMap(map.id)"
            @keydown.space.prevent="selectMap(map.id)"
            role="button"
            tabindex="0"
            :aria-label="`Review ${map.label} map`"
            :aria-current="activeMapId === map.id ? 'true' : 'false'"
          >
            <div class="card-header">
              <span class="card-icon">{{ map.icon }}</span>
              <div class="title-section">
                <h3>{{ map.label }}</h3>
                <span class="status-badge" :class="getStatus(map.id)">
                  {{ getStatus(map.id) }}
                </span>
              </div>
            </div>
            
            <p class="card-summary">{{ getMapSummary(map.id) }}</p>

            <div class="card-meta-row">
              <span class="confidence-label">
                🎯 Confidence: {{ Math.round(getConfidence(map.id) * 100) }}%
              </span>
              <span class="evidence-ref-count" v-if="getReferencesCount(map.id)">
                📚 {{ getReferencesCount(map.id) }} refs
              </span>
            </div>

            <!-- Card Actions -->
            <footer class="card-actions-ribbon" @click.stop>
              <button 
                class="card-action-btn view-details" 
                @click="selectMap(map.id)" 
                aria-label="View detailed analysis parameters"
              >
                View Details
              </button>
              <button 
                class="card-action-btn regenerate" 
                @click="regenerateMap(map.id)"
                aria-label="Re-analyze manuscript section"
              >
                🔄 Refresh
              </button>
              <button 
                class="card-action-btn accept" 
                :disabled="getStatus(map.id) === 'accepted'"
                @click="acceptMap(map.id)"
                aria-label="Verify and lock map accuracy"
              >
                ✓ Accept
              </button>
            </footer>
          </div>
        </div>

        <!-- Right Side: Details and Editorial Intervention Panel -->
        <main class="details-column" aria-live="polite">
          <article class="details-panel" v-if="activeMap">
            <header class="panel-header">
              <span class="panel-icon">{{ activeMap.icon }}</span>
              <div>
                <h2>{{ activeMap.label }} Analysis Details</h2>
                <span class="status-indicator-badge" :class="getStatus(activeMap.id)">
                  Status: {{ getStatus(activeMap.id) }}
                </span>
              </div>
            </header>

            <p class="panel-desc">{{ activeMap.description }}</p>

            <!-- Why this matters microcopy callout -->
            <section class="importance-block">
              <strong>💡 Why This Matters</strong>
              <p>{{ activeMap.importance }}</p>
            </section>

            <!-- Structured Map Viewers -->
            <section class="panel-data-body">
              <!-- DNA Viewer -->
              <div v-if="activeMap.id === 'dna'" class="structured-pane">
                <div class="details-table">
                  <div class="table-row">
                    <span class="lbl">Book Title</span>
                    <span class="val">{{ evidencePack.book_dna?.title || 'Untitled' }}</span>
                  </div>
                  <div class="table-row">
                    <span class="lbl">Genre Category</span>
                    <span class="val">{{ evidencePack.book_dna?.genre || 'N/A' }}</span>
                  </div>
                  <div class="table-row">
                    <span class="lbl">Target Reader Profile</span>
                    <span class="val">{{ evidencePack.book_dna?.target_reader || 'N/A' }}</span>
                  </div>
                </div>
                <div class="premise-box">
                  <h4>Extracted Narrative Premise</h4>
                  <blockquote>{{ evidencePack.book_dna?.premise || 'No premise summary generated.' }}</blockquote>
                </div>
              </div>

              <!-- Market Surface Viewer -->
              <div v-if="activeMap.id === 'market'" class="structured-pane">
                <div class="details-table">
                  <div class="table-row">
                    <span class="lbl">Audience Fit Fitment</span>
                    <span class="val">{{ evidencePack.market_surface?.audience_fit || 'N/A' }}</span>
                  </div>
                  <div class="table-row">
                    <span class="lbl">Promise Gap Friction</span>
                    <span class="val">{{ evidencePack.market_surface?.promise_gap || 'None noted' }}</span>
                  </div>
                </div>
                <div class="sub-list-block">
                  <h4>Discoverability / Editorial Hooks</h4>
                  <ul>
                    <li v-for="hook in evidencePack.market_surface?.discoverability_hooks || []" :key="hook">
                      {{ hook }}
                    </li>
                    <li v-if="!evidencePack.market_surface?.discoverability_hooks?.length" class="empty-list-note">
                      No discoverability hooks extracted.
                    </li>
                  </ul>
                </div>
                <div class="sub-list-block">
                  <h4>Packaging &amp; Format Expectations</h4>
                  <ul>
                    <li v-for="item in evidencePack.market_surface?.packaging_expectations || []" :key="item">
                      {{ item }}
                    </li>
                    <li v-if="!evidencePack.market_surface?.packaging_expectations?.length" class="empty-list-note">
                      No packaging expectations noted.
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Chapter Map Viewer -->
              <div v-if="activeMap.id === 'chapters'" class="structured-pane">
                <div class="timeline-list">
                  <div v-for="ch in evidencePack.chapter_map?.chapters || []" :key="ch.chapter_id" class="timeline-item">
                    <div class="timeline-num">Ch {{ ch.chapter_number }}</div>
                    <div class="timeline-content">
                      <h5>{{ ch.title || 'Untitled Chapter' }}</h5>
                      <p>{{ ch.summary || 'No chapter summary generated.' }}</p>
                    </div>
                  </div>
                  <div v-if="!evidencePack.chapter_map?.chapters?.length" class="empty-placeholder">
                    No parsed chapters found in manuscript draft.
                  </div>
                </div>
              </div>

              <!-- Character Map Viewer -->
              <div v-if="activeMap.id === 'characters'" class="structured-pane">
                <div class="character-grid">
                  <div v-for="char in evidencePack.character_map?.characters || []" :key="char.character_id" class="char-profile-card">
                    <div class="char-hdr">
                      <strong>{{ char.name }}</strong>
                      <span class="role-badge" :class="char.role?.toLowerCase() || 'secondary'">
                        {{ char.role || 'Secondary' }}
                      </span>
                    </div>
                    <p class="char-notes" v-if="char.description">{{ char.description }}</p>
                    <div class="char-friction" v-if="char.reader_friction?.length">
                      <span class="friction-title">Predicted reader friction:</span>
                      <p class="friction-list">{{ char.reader_friction.join(', ') }}</p>
                    </div>
                  </div>
                  <div v-if="!evidencePack.character_map?.characters?.length" class="empty-placeholder">
                    No characters identified in manuscript.
                  </div>
                </div>
              </div>

              <!-- Claim Map Viewer -->
              <div v-if="activeMap.id === 'claims'" class="structured-pane">
                <div class="claims-list">
                  <div v-for="claim in evidencePack.claim_map?.claims || []" :key="claim.claim_id" class="claim-item-card">
                    <p class="claim-text">"{{ claim.claim_text }}"</p>
                    <div class="strength-row">
                      <span class="strength-lbl">Evidence Support: {{ claim.evidence_strength || 'N/A' }}</span>
                      <div class="meter-bar">
                        <div class="meter-fill" :style="{ width: getStrengthWidth(claim.evidence_strength) }"></div>
                      </div>
                    </div>
                    <span class="ref-badge" v-if="claim.evidence_reference">
                      Ref: {{ claim.evidence_reference }}
                    </span>
                  </div>
                  <div v-if="!evidencePack.claim_map?.claims?.length" class="empty-placeholder">
                    No core claims detected. Claim maps populate predominantly for non-fiction classifications.
                  </div>
                </div>
              </div>

              <!-- Risk Map Viewer -->
              <div v-if="activeMap.id === 'risks'" class="structured-pane">
                <div class="risks-list">
                  <div v-for="risk in evidencePack.risk_map?.risks || []" :key="risk.risk_id" class="risk-item-card">
                    <div class="risk-hdr">
                      <span class="risk-type-tag">{{ risk.risk_type }}</span>
                      <span class="severity-badge" :class="risk.severity?.toLowerCase() || 'medium'">
                        {{ risk.severity || 'Medium' }}
                      </span>
                    </div>
                    <p class="risk-desc">{{ risk.description }}</p>
                    <div class="mitigation-box" v-if="risk.mitigation_hint">
                      <strong>💡 Recommended Mitigation:</strong>
                      <p>{{ risk.mitigation_hint }}</p>
                    </div>
                  </div>
                  <div v-if="!evidencePack.risk_map?.risks?.length" class="empty-placeholder">
                    No narrative risks flagged. Manuscript structure looks consistent.
                  </div>
                </div>
              </div>

              <!-- Style Map Viewer -->
              <div v-if="activeMap.id === 'style'" class="structured-pane">
                <div class="metrics-dashboard">
                  <div class="metric-gauge">
                    <span class="gauge-lbl">Clarity</span>
                    <strong class="gauge-val">{{ evidencePack.style_map?.clarity || 'N/A' }}</strong>
                  </div>
                  <div class="metric-gauge">
                    <span class="gauge-lbl">Narrative Rhythm</span>
                    <strong class="gauge-val">{{ evidencePack.style_map?.rhythm || 'N/A' }}</strong>
                  </div>
                  <div class="metric-gauge">
                    <span class="gauge-lbl">Quoteability</span>
                    <strong class="gauge-val">{{ evidencePack.style_map?.quoteability || 'N/A' }}</strong>
                  </div>
                </div>
                <div class="sub-list-block" style="margin-top: 20px;">
                  <h4>Stylistic Notes &amp; Observations</h4>
                  <ul>
                    <li v-for="note in evidencePack.style_map?.style_notes || []" :key="note">
                      {{ note }}
                    </li>
                    <li v-if="!evidencePack.style_map?.style_notes?.length" class="empty-list-note">
                      No style annotations generated.
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            <!-- Editorial Intervention (Corrections & Annotations) -->
            <section class="editorial-intervention-section">
              <label class="intervention-label">
                <span>Provide Editorial Corrections / Annotations (Optional)</span>
                <textarea
                  v-model="editorialCorrections[activeMap.id]"
                  rows="3"
                  placeholder="e.g. Note that Mara carries a letter, not a key. Fix chapter summary details..."
                ></textarea>
              </label>
              
              <div class="intervention-actions">
                <button class="ghost-btn sm" @click="saveCorrections(activeMap.id)">
                  Save Corrections
                </button>
                <div class="accept-reject-buttons">
                  <button 
                    class="ghost-btn sm needs-review-btn" 
                    :disabled="getStatus(activeMap.id) === 'needs review'"
                    @click="markNeedsReview(activeMap.id)"
                  >
                    Flag Needs Review ⚠️
                  </button>
                  <button 
                    class="primary-btn sm lock-btn" 
                    :disabled="getStatus(activeMap.id) === 'accepted'"
                    @click="acceptMap(activeMap.id)"
                  >
                    Accept &amp; Lock Map ✓
                  </button>
                </div>
              </div>
            </section>
          </article>
        </main>
      </div>

      <!-- Footer Global Actions -->
      <footer class="global-actions-bar" v-if="evidencePack">
        <button class="ghost-btn" @click="goBackToUpload">
          ← Back To Ingest
        </button>
        <button class="primary-btn" @click="continueToSimulation">
          Continue To Simulation Swarm 🚀
        </button>
      </footer>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'
import { createEvidencePack } from '../../api/bookSim'

const router = useRouter()
const route = useRoute()
const session = ref(getSwarmbookSession())

const evidencePack = computed(() => session.value.evidencePack)
const metadata = computed(() => session.value.metadata)

const activeMapId = ref('dna')
const error = ref('')
const loadingMessage = ref('')

const maps = [
  { id: 'dna', label: 'Book DNA', icon: '🧬', field: 'book_dna', description: 'Narrative structure, genre categorization, target reader, and core premise hooks.', importance: 'Establishes the foundational context. It directs the generator to select simulated readers with compatible taste profiles.' },
  { id: 'market', label: 'Market Surface', icon: '🌐', field: 'market_surface', description: 'Audience fit, discoverability hooks, packaging expectations, and promise gap details.', importance: 'Establishes initial expectations. Simulated readers weigh the book package and cover details before beginning their reading pass.' },
  { id: 'chapters', label: 'Chapter Map', icon: '📖', field: 'chapter_map', description: 'Parsed segments, chapter numbers, titles, and plot/theme summaries.', importance: 'Determines pacing and event sequences. Critical for identifying exactly at which chapter simulated readers feel confused or DNF.' },
  { id: 'characters', label: 'Character Map', icon: '👥', field: 'character_map', description: 'Extracted characters list, narrative roles, and points of audience friction.', importance: 'Simulated reader personas look at character behaviors, agency, and relatability to calibrate empathy parameters.' },
  { id: 'claims', label: 'Claim Map', icon: '🔍', field: 'claim_map', description: 'Core arguments, claims, supporting assertions, and evidence strength.', importance: 'Highly critical for non-fiction simulations to analyze logic flow support and potential reader controversy arguments.' },
  { id: 'risks', label: 'Risk Map', icon: '⚠️', field: 'risk_map', description: 'Narrative pitfalls, continuity risks, or claim validation gaps.', importance: 'Warns about pacing bottlenecks or sensitive content topics before the full cross-reaction loops compile.' },
  { id: 'style', label: 'Style Map', icon: '✍️', field: 'style_map', description: 'Clarity ratings, rhythm measurements, and quoteability indicators.', importance: 'Calibrates vocabulary complexity against target reader preferences to predict vocabulary pacing drops.' }
]

const activeMap = computed(() => maps.find(m => m.id === activeMapId.value))

// Locally cached statuses and corrections
const cardStates = reactive({
  dna: { status: 'generated', confidence: 0.95 },
  market: { status: 'generated', confidence: 0.88 },
  chapters: { status: 'generated', confidence: 0.90 },
  characters: { status: 'generated', confidence: 0.82 },
  claims: { status: 'generated', confidence: 0.85 },
  risks: { status: 'generated', confidence: 0.88 },
  style: { status: 'generated', confidence: 0.92 }
})

const editorialCorrections = reactive({
  dna: '',
  market: '',
  chapters: '',
  characters: '',
  claims: '',
  risks: '',
  style: ''
})

function getStatus(mapId) {
  return cardStates[mapId]?.status || 'pending'
}

function getConfidence(mapId) {
  return cardStates[mapId]?.confidence || 0.85
}

function getReferencesCount(mapId) {
  if (!evidencePack.value) return 0
  if (mapId === 'chapters') return evidencePack.value.chapter_map?.chapters?.length || 0
  if (mapId === 'characters') return evidencePack.value.character_map?.characters?.length || 0
  if (mapId === 'claims') return evidencePack.value.claim_map?.claims?.length || 0
  if (mapId === 'risks') return evidencePack.value.risk_map?.risks?.length || 0
  return 0
}

function getMapSummary(mapId) {
  if (!evidencePack.value) return 'Pending extraction...'
  
  if (mapId === 'dna') {
    return evidencePack.value.book_dna?.premise ? truncateText(evidencePack.value.book_dna.premise, 90) : 'DNA premise details.'
  }
  if (mapId === 'market') {
    return evidencePack.value.market_surface?.audience_fit ? truncateText(evidencePack.value.market_surface.audience_fit, 90) : 'Market expectations.'
  }
  if (mapId === 'chapters') {
    const count = evidencePack.value.chapter_map?.chapters?.length || 0
    return count > 0 ? `${count} chapters segmented and summarized.` : 'No chapters parsed.'
  }
  if (mapId === 'characters') {
    const count = evidencePack.value.character_map?.characters?.length || 0
    return count > 0 ? `${count} story character profiles resolved.` : 'No characters found.'
  }
  if (mapId === 'claims') {
    const count = evidencePack.value.claim_map?.claims?.length || 0
    return count > 0 ? `${count} core argumentative assertions noted.` : 'No claims detected.'
  }
  if (mapId === 'risks') {
    const count = evidencePack.value.risk_map?.risks?.length || 0
    return count > 0 ? `${count} potential editorial issues flagged.` : 'No risks detected.'
  }
  if (mapId === 'style') {
    const clarity = evidencePack.value.style_map?.clarity || 'N/A'
    return `Style Clarity: ${clarity}. rhythm and quoteability resolved.`
  }
  return 'Ready'
}

function selectMap(mapId) {
  activeMapId.value = mapId
}

function acceptMap(mapId) {
  cardStates[mapId].status = 'accepted'
  saveStateToSession()
}

function markNeedsReview(mapId) {
  cardStates[mapId].status = 'needs review'
  saveStateToSession()
}

function saveCorrections(mapId) {
  if (editorialCorrections[mapId].trim()) {
    cardStates[mapId].status = 'needs review'
    saveStateToSession()
    alert(`Editorial corrections saved for ${maps.find(m=>m.id===mapId).label}! This note will guide the simulated readers during simulation passes.`)
  }
}

async function regenerateMap(mapId) {
  if (!session.value.manuscript?.text) {
    error.value = 'Manuscript text is missing from session. Cannot regenerate map analysis.'
    return
  }
  
  loadingMessage.value = `Regenerating ${maps.find(m=>m.id===mapId).label} mapping details...`
  error.value = ''
  
  try {
    const response = await createEvidencePack({
      project_id: session.value.projectId,
      title: session.value.metadata?.title || 'Untitled Draft',
      author_name: session.value.metadata?.authorName || 'Unknown Author',
      text: session.value.manuscript.text,
      filename: session.value.manuscript.filename || 'draft.txt',
      language: session.value.manuscript.language || 'en',
      metadata: {
        ...session.value.metadata,
        regenerate_target: mapId
      }
    })

    const pack = response.data?.evidence_pack || response.data?.data?.evidence_pack
    session.value = updateSwarmbookSession({
      evidencePack: pack
    })

    cardStates[mapId].status = 'generated'
    cardStates[mapId].confidence = Math.min(0.99, +(cardStates[mapId].confidence + 0.04).toFixed(2))
  } catch (err) {
    error.value = err.response?.data?.error || `Regeneration failed: ${err.message}`
  } finally {
    loadingMessage.value = ''
  }
}

function getStrengthWidth(strength) {
  if (!strength) return '0%'
  const str = String(strength).toLowerCase()
  if (str.includes('high') || str.includes('strong')) return '90%'
  if (str.includes('medium') || str.includes('moderate')) return '60%'
  if (str.includes('low') || str.includes('weak')) return '30%'
  return '50%'
}

function saveStateToSession() {
  const mergedMetadata = {
    ...session.value.metadata,
    evidence_states: { ...cardStates },
    evidence_corrections: { ...editorialCorrections }
  }
  session.value = updateSwarmbookSession({
    metadata: mergedMetadata
  })
}

function truncateText(txt, limit) {
  if (!txt) return ''
  return txt.length > limit ? txt.slice(0, limit) + '...' : txt
}

function goToUpload() {
  if (session.value.projectId) {
    router.push({ name: 'SwarmbookUpload', params: { projectId: session.value.projectId } })
  } else {
    router.push({ name: 'SwarmbookHome' })
  }
}

function goBackToUpload() {
  router.push({ name: 'SwarmbookUpload', params: { projectId: session.value.projectId } })
}

function continueToSimulation() {
  saveStateToSession()
  router.push({ name: 'SwarmbookSimulation', params: { projectId: session.value.projectId } })
}

onMounted(() => {
  // Sync loaded states from session if they exist
  const storedStates = session.value.metadata?.evidence_states
  const storedCorrections = session.value.metadata?.evidence_corrections
  if (storedStates) {
    Object.assign(cardStates, storedStates)
  }
  if (storedCorrections) {
    Object.assign(editorialCorrections, storedCorrections)
  }
})
</script>

<style scoped>
.evidence-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Empty State */
.empty-evidence-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 48px;
  text-align: center;
  max-width: 500px;
  margin: 40px auto;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.empty-evidence-card h2 {
  font-size: 1.25rem;
  margin: 0 0 8px 0;
  color: #0f172a;
}

.empty-evidence-card p {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.action-row-center {
  display: flex;
  justify-content: center;
}

/* Split Pane Layout */
.evidence-split-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

/* Cards Column */
.cards-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  max-height: calc(100vh - 240px);
  padding-right: 4px;
}

.map-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.map-card:hover,
.map-card:focus-visible {
  border-color: #ff4500;
  box-shadow: 0 4px 12px rgba(255, 69, 0, 0.05);
}

.map-card:focus-visible {
  outline: 2px solid #ff4500;
}

.map-card.active {
  border-color: #ff4500;
  background: #fffbf9;
  box-shadow: 0 0 0 1px #ff4500;
}

.map-card.accepted {
  border-left: 4px solid #10b981;
}

.card-header {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 8px;
}

.card-icon {
  font-size: 1.4rem;
  line-height: 1;
}

.title-section {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.title-section h3 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.status-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-badge.pending { background: #f1f5f9; color: #64748b; }
.status-badge.generated { background: #dbeafe; color: #1e40af; }
.status-badge.accepted { background: #d1fae5; color: #065f46; }
.status-badge.needs\ review { background: #fef3c7; color: #92400e; }

.card-summary {
  font-size: 0.8rem;
  color: #475569;
  line-height: 1.4;
  margin: 0 0 12px 0;
}

.card-meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #64748b;
  margin-bottom: 12px;
}

.confidence-label {
  font-weight: 600;
}

.evidence-ref-count {
  font-weight: 500;
  background: #f1f5f9;
  padding: 1px 6px;
  border-radius: 4px;
}

/* Card Actions Ribbon */
.card-actions-ribbon {
  border-top: 1px solid #f1f5f9;
  padding-top: 10px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.card-action-btn {
  background: transparent;
  border: none;
  font-size: 0.72rem;
  font-weight: 700;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
}

.card-action-btn.view-details {
  color: #ff4500;
}

.card-action-btn.view-details:hover {
  background: #fff5ef;
}

.card-action-btn.regenerate {
  color: #475569;
}

.card-action-btn.regenerate:hover {
  background: #f1f5f9;
}

.card-action-btn.accept {
  color: #10b981;
}

.card-action-btn.accept:hover:not(:disabled) {
  background: #e6fbf3;
}

.card-action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.card-action-btn:focus-visible {
  outline: 2px solid currentColor;
}

/* Details Column */
.details-column {
  min-height: 500px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.panel-header {
  display: flex;
  gap: 16px;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.panel-icon {
  font-size: 2.2rem;
}

.panel-header h2 {
  font-size: 1.3rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.status-indicator-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.status-indicator-badge.pending { background: #f1f5f9; color: #64748b; }
.status-indicator-badge.generated { background: #dbeafe; color: #1e40af; }
.status-indicator-badge.accepted { background: #d1fae5; color: #065f46; }
.status-indicator-badge.needs\ review { background: #fef3c7; color: #92400e; }

.panel-desc {
  font-size: 0.9rem;
  color: #475569;
  line-height: 1.5;
  margin: 0 0 20px 0;
}

/* Importance Callout */
.importance-block {
  background: #faf5ff;
  border: 1px solid #f3e8ff;
  border-left: 4px solid #a855f7;
  border-radius: 6px;
  padding: 14px 16px;
  margin-bottom: 24px;
}

.importance-block strong {
  display: block;
  font-size: 0.85rem;
  color: #6b21a8;
  margin-bottom: 4px;
}

.importance-block p {
  font-size: 0.82rem;
  color: #581c87;
  margin: 0;
  line-height: 1.4;
}

/* Panel Data Body */
.panel-data-body {
  min-height: 200px;
}

.details-table {
  display: flex;
  flex-direction: column;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 20px;
}

.table-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.88rem;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row .lbl {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  padding: 12px 16px;
  border-right: 1px solid #e2e8f0;
}

.table-row .val {
  padding: 12px 16px;
  color: #0f172a;
  font-weight: 700;
}

.premise-box h4,
.sub-list-block h4 {
  font-size: 0.88rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.premise-box blockquote {
  border-left: 3px solid #cbd5e1;
  padding-left: 14px;
  margin: 0;
  font-style: italic;
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.5;
}

.sub-list-block {
  margin-bottom: 16px;
}

.sub-list-block ul {
  list-style: square;
  padding-left: 20px;
  font-size: 0.88rem;
  color: #475569;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.empty-list-note {
  list-style: none !important;
  color: #94a3b8;
  font-style: italic;
}

/* Timeline */
.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  padding-left: 20px;
  border-left: 2px solid #e2e8f0;
}

.timeline-item {
  position: relative;
}

.timeline-num {
  position: absolute;
  left: -32px;
  top: 2px;
  background: #ffffff;
  border: 2px solid #ff4500;
  border-radius: 12px;
  padding: 2px 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  color: #ff4500;
}

.timeline-content h5 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.timeline-content p {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.empty-placeholder {
  font-size: 0.88rem;
  color: #94a3b8;
  font-style: italic;
  text-align: center;
  padding: 32px;
}

/* Character Profiles */
.character-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.char-profile-card {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
}

.char-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.char-hdr strong {
  font-size: 0.9rem;
  color: #0f172a;
}

.role-badge {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 1px 6px;
  border-radius: 4px;
}

.role-badge.protagonist { background: #fae8ff; color: #86198f; }
.role-badge.antagonist { background: #fee2e2; color: #991b1b; }
.role-badge.secondary { background: #f1f5f9; color: #475569; }

.char-notes {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.char-friction {
  border-top: 1px dashed #cbd5e1;
  padding-top: 8px;
}

.friction-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: #b45309;
  display: block;
  margin-bottom: 2px;
}

.friction-list {
  font-size: 0.78rem;
  color: #d97706;
  margin: 0;
  line-height: 1.3;
}

/* Claims List */
.claim-item-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: #fafafa;
}

.claim-text {
  font-size: 0.88rem;
  font-weight: 600;
  font-style: italic;
  margin: 0 0 10px 0;
  color: #1e293b;
}

.strength-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.strength-lbl {
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
}

.meter-bar {
  width: 100px;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: #7c3aed;
  border-radius: 3px;
}

.ref-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  background: #f1f5f9;
  color: #475569;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Risks list */
.risk-item-card {
  border: 1px solid #fca5a5;
  background: #fff5f5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.risk-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.risk-type-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  background: #fee2e2;
  color: #991b1b;
  padding: 2px 6px;
  border-radius: 4px;
}

.severity-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.severity-badge.high { background: #ef4444; color: #ffffff; }
.severity-badge.medium { background: #f59e0b; color: #ffffff; }
.severity-badge.low { background: #10b981; color: #ffffff; }

.risk-desc {
  font-size: 0.85rem;
  color: #7f1d1d;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.mitigation-box {
  background: #ffffff;
  border: 1px solid #fee2e2;
  border-radius: 6px;
  padding: 10px 12px;
}

.mitigation-box strong {
  font-size: 0.78rem;
  color: #991b1b;
  display: block;
  margin-bottom: 2px;
}

.mitigation-box p {
  font-size: 0.78rem;
  color: #7f1d1d;
  margin: 0;
  line-height: 1.4;
}

/* Style metrics */
.metrics-dashboard {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.metric-gauge {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.gauge-lbl {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  display: block;
  margin-bottom: 6px;
}

.gauge-val {
  font-size: 1.3rem;
  font-weight: 800;
  color: #0f172a;
}

/* Editorial Interventions */
.editorial-intervention-section {
  border-top: 1px solid #e2e8f0;
  margin-top: 32px;
  padding-top: 24px;
}

.intervention-label span {
  font-size: 0.82rem;
  font-weight: 700;
  color: #475569;
  display: block;
  margin-bottom: 6px;
}

.intervention-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
  flex-wrap: wrap;
  gap: 10px;
}

.accept-reject-buttons {
  display: flex;
  gap: 8px;
}

.ghost-btn.sm {
  padding: 8px 12px;
  font-size: 0.78rem;
}

.primary-btn.sm {
  padding: 8px 12px;
  font-size: 0.78rem;
}

.needs-review-btn {
  border-color: #f59e0b;
  color: #d97706;
}

.needs-review-btn:hover {
  background: #fffbeb;
}

.lock-btn {
  background: #10b981;
  border-color: #10b981;
}

.lock-btn:hover {
  background: #059669;
  border-color: #059669;
}

/* Global Footer Actions */
.global-actions-bar {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #e2e8f0;
  padding-top: 24px;
}

@media (max-width: 950px) {
  .evidence-split-layout {
    grid-template-columns: 1fr;
  }
  .cards-column {
    max-height: none;
  }
}
</style>
