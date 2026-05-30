<template>
  <SwarmbookAppShell
    active-route="SwarmbookPersonas"
    :project-id="session.projectId"
    title="Persona Interview"
    subtitle="Question simulated readers individually to understand why they reacted the way they did, where they struggled, and what would make them recommend the book."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="interview-container">
      <!-- Drawer backdrop overlay -->
      <div 
        v-if="selectedEvidenceRef" 
        class="drawer-backdrop animate-fade-in" 
        @click="selectedEvidenceRef = ''"
        aria-hidden="true"
      ></div>

      <!-- 1. Left Sidebar: Persona Directory -->
      <aside class="persona-sidebar" aria-label="Simulated Readers Directory">
        <div class="search-box">
          <label for="search-input" class="sr-only">Search Simulated Readers</label>
          <input 
            id="search-input"
            type="text" 
            v-model="searchQuery" 
            placeholder="Search simulated readers..."
            aria-label="Search simulated readers by name or cohort"
          />
        </div>

        <div class="persona-directory-list" role="listbox" aria-label="Simulated Reader list">
          <button 
            v-for="p in filteredPersonas" 
            :key="p.persona_id"
            class="directory-item-btn"
            :class="{ active: selectedPersonaId === p.persona_id }"
            role="option"
            :aria-selected="selectedPersonaId === p.persona_id"
            @click="selectPersona(p.persona_id)"
          >
            <div class="item-header">
              <strong class="item-name">{{ p.display_name }}</strong>
              <span class="item-platform-tag" :class="p.platform_home">{{ p.platform_home.toUpperCase() }}</span>
            </div>
            <div class="item-cohort">{{ p.cohort || 'General Reader' }}</div>
            
            <div class="item-stats-row">
              <span class="item-stat-rating">
                ★ {{ getPersonaStats(p.persona_id).rating !== null ? getPersonaStats(p.persona_id).rating.toFixed(1) : 'DNF' }}
              </span>
              <span class="item-stat-dnf" :class="{ 'high-risk': getPersonaStats(p.persona_id).dnf_probability >= 0.4 }">
                DNF Prob: {{ Math.round((getPersonaStats(p.persona_id).dnf_probability || 0) * 100) }}%
              </span>
            </div>
          </button>
          <div v-if="!filteredPersonas.length" class="empty-list-note">
            No simulated readers found.
          </div>
        </div>
      </aside>

      <!-- Right Main Workspace Workspace -->
      <main class="interview-workspace" v-if="activePersona" aria-label="Interview Workspace">
        <!-- Known Limitations Warning Banner -->
        <div class="sandbox-limitations-banner" role="status">
          <span class="banner-icon" aria-hidden="true">⚠️</span>
          <div class="banner-content">
            <strong>Synthetic Simulation Sandbox:</strong> Responses are generated reader reactions based on manuscript evidence maps. This is not a real-market predictor, does not scrape live platforms, and operates strictly under privacy-mode compliance.
          </div>
        </div>

        <!-- 2. Selected Persona Profile Card -->
        <article class="persona-profile-card">
          <header class="profile-header">
            <div class="profile-avatar">👤</div>
            <div class="profile-meta">
              <h2>{{ activePersona.display_name }}</h2>
              <p class="profile-subheader">
                Platform: <strong>{{ formatPlatformLabel(activePersona.platform_home) }}</strong> • 
                Cohort: <strong>{{ activePersona.cohort || 'General Reader' }}</strong> • 
                Influence Score: <strong>{{ Math.round((activePersona.influence_weight || activePersona.influence_score || 0.5) * 100) }}%</strong>
              </p>
            </div>
          </header>

          <div class="profile-details-grid">
            <div class="detail-block">
              <span class="detail-label">Reader Taste (Favorite Genres)</span>
              <div class="tags-row">
                <span 
                  v-for="genre in (activePersona.favorite_genres || activePersona.reading_preferences || [])" 
                  :key="genre" 
                  class="tag genre-tag"
                >
                  📖 {{ genre }}
                </span>
              </div>
            </div>

            <div class="detail-block">
              <span class="detail-label">Disliked Patterns (DNF Triggers)</span>
              <div class="tags-row">
                <span 
                  v-for="trigger in (activePersona.disliked_patterns || activePersona.dnf_triggers || [])" 
                  :key="trigger" 
                  class="tag trigger-tag"
                >
                  ⚡ {{ trigger }}
                </span>
              </div>
            </div>

            <div class="detail-block">
              <span class="detail-label">Review Writing Style</span>
              <span class="review-style-text"><code>{{ activePersona.review_style }}</code></span>
            </div>
          </div>
        </article>

        <!-- 3. Chat Panel (Workspace Bubbles & Suggested Input) -->
        <section class="chat-workspace-panel" aria-label="Interactive Chat Workbench">
          <div class="chat-bubbles-timeline" ref="chatScrollContainer">
            <div 
              v-for="(msg, idx) in currentHistory" 
              :key="idx" 
              class="message-bubble-wrapper"
              :class="msg.sender"
            >
              <div class="message-bubble">
                <header class="message-sender-title" v-if="msg.sender === 'persona'">
                  {{ activePersona.display_name }} ({{ activePersona.platform_home.toUpperCase() }})
                </header>
                <header class="message-sender-title" v-else>
                  Author (You)
                </header>
                
                <p class="message-text">{{ msg.text }}</p>

                <!-- Grounded references indicators -->
                <div v-if="msg.basedOn?.length" class="message-based-on">
                  <span class="label">Based on citations:</span>
                  <div class="citation-pills-row">
                    <button 
                      v-for="refId in msg.basedOn" 
                      :key="refId" 
                      class="citation-pill"
                      :class="{ active: selectedEvidenceRef === refId }"
                      @click="selectEvidence(refId)"
                      :aria-label="'View evidence details for reference ' + refId"
                    >
                      #{{ refId }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="localLoading" class="message-bubble-wrapper persona">
              <div class="message-bubble loading-bubble">
                <span class="pulsing-text">Querying reader reactions...</span>
              </div>
            </div>
          </div>

          <!-- Suggested Questions Ribbon -->
          <div class="suggested-questions-box">
            <span class="label">Suggested Interview Questions:</span>
            <div class="shortcuts-row">
              <button 
                v-for="question in quickQuestions" 
                :key="question" 
                class="shortcut-question-btn"
                @click="triggerQuickQuestion(question)"
                :disabled="loading || localLoading"
                :aria-label="'Ask suggested question: ' + question"
              >
                {{ question }}
              </button>
            </div>
          </div>

          <!-- Message input workbench -->
          <form class="chat-input-bar" @submit.prevent="askPersona">
            <label for="question-input" class="sr-only">Type your question for the simulated reader</label>
            <textarea 
              id="question-input"
              v-model="questionText" 
              placeholder="Ask this simulated reader why they reacted a certain way..."
              rows="2"
              @keydown.enter.exact.prevent="askPersona"
              :disabled="loading || localLoading"
            ></textarea>
            <button 
              type="submit" 
              class="primary-btn submit-chat-btn" 
              :disabled="!canAsk || loading || localLoading"
              aria-label="Send question to simulated reader"
            >
              Ask Reader
            </button>
          </form>
        </section>
      </main>

      <!-- 4. Grounded Evidence Inspector Drawer -->
      <aside 
        class="evidence-drawer" 
        :class="{ open: !!selectedEvidenceRef }"
        aria-label="Grounded Evidence Drawer"
      >
        <div class="drawer-header">
          <h2>Evidence Inspector</h2>
          <button 
            type="button" 
            class="close-drawer-btn" 
            @click="selectedEvidenceRef = ''"
            aria-label="Close evidence drawer"
          >
            &times;
          </button>
        </div>
        <p class="panel-desc">View manuscript sections, claims, or pacing maps cited by simulated readers in their responses.</p>
        
        <div v-if="selectedEvidenceDetail" class="evidence-detail-card animate-fade-in">
          <span class="evidence-type-badge">{{ selectedEvidenceDetail.type }}</span>
          <h3>{{ selectedEvidenceDetail.title }}</h3>
          
          <div class="evidence-summary-box">
            <strong>Grounded content extract:</strong>
            <p>{{ selectedEvidenceDetail.summary }}</p>
          </div>

          <div class="evidence-meta-bullets">
            <div v-for="detail in selectedEvidenceDetail.details" :key="detail" class="meta-bullet">
              • {{ detail }}
            </div>
          </div>
        </div>
        <div v-else class="empty-evidence-box">
          <span class="box-icon">🔍</span>
          <p>Select a citation hashtag (e.g. #chapter_3) inside the chat reply bubble to inspect its editorial details.</p>
        </div>
      </aside>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { chatWithBookPersona } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const searchQuery = ref('')
const selectedPersonaId = ref('')
const questionText = ref('')
const loading = ref(false)
const localLoading = ref(false)
const error = ref('')
const selectedEvidenceRef = ref('')
const chatScrollContainer = ref(null)

// Sync session parameters on load
watch(() => route.path, () => {
  session.value = getSwarmbookSession()
  syncDefaultPersona()
})

const personas = computed(() => session.value.simulationRun?.reader_personas || [])

// ----------------------------------------------------
// Mock Roster Fallback (standalone/offline testing)
// ----------------------------------------------------
const MOCK_PERSONAS = [
  {
    persona_id: 'persona_aria',
    display_name: 'Aria Reed',
    platform_home: 'booktok',
    cohort: 'Emotional Amplifiers',
    favorite_genres: ['Romance', 'YA Fantasy'],
    disliked_patterns: ['Slow pacing', 'Boring dialogue'],
    review_style: 'emotional_confessional',
    influence_weight: 0.85
  },
  {
    persona_id: 'persona_devon',
    display_name: 'Devon M.',
    platform_home: 'goodreads',
    cohort: 'Genre Loyalists',
    favorite_genres: ['Sci-Fi', 'Techno Thriller'],
    disliked_patterns: ['Plot holes', 'Cardboard characters'],
    review_style: 'critical_balanced',
    influence_weight: 0.65
  },
  {
    persona_id: 'persona_skeptic',
    display_name: 'Skeptic Reader',
    platform_home: 'reddit',
    cohort: 'Evidence Skeptics',
    favorite_genres: ['Hard Sci-Fi', 'Non-fiction'],
    disliked_patterns: ['Fake physics', 'Preachy tone'],
    review_style: 'analytical_skeptical',
    influence_weight: 0.70
  },
  {
    persona_id: 'persona_leo',
    display_name: 'Leo Vance',
    platform_home: 'bookstagram',
    cohort: 'Aesthetic Curators',
    favorite_genres: ['Contemporary Fiction', 'Literary Fiction'],
    disliked_patterns: ['Poor prose', 'Melodrama'],
    review_style: 'aesthetic_curated',
    influence_weight: 0.80
  },
  {
    persona_id: 'persona_x',
    display_name: 'Critical X',
    platform_home: 'x',
    cohort: 'Harsh Reviewers',
    favorite_genres: ['Thriller', 'Satire'],
    disliked_patterns: ['Predictable endings', 'Infodumps'],
    review_style: 'punchy_polarized',
    influence_weight: 0.75
  }
]

const MOCK_REACTIONS = {
  persona_aria: { rating: 5.0, dnf_probability: 0.05 },
  persona_devon: { rating: 4.0, dnf_probability: 0.15 },
  persona_skeptic: { rating: 2.0, dnf_probability: 0.75 },
  persona_leo: { rating: 5.0, dnf_probability: 0.10 },
  persona_x: { rating: 3.0, dnf_probability: 0.40 }
}

const filteredPersonas = computed(() => {
  const list = personas.value.length ? personas.value : MOCK_PERSONAS
  if (!searchQuery.value.trim()) return list
  const query = searchQuery.value.toLowerCase()
  return list.filter(p => 
    p.display_name.toLowerCase().includes(query) || 
    (p.cohort || '').toLowerCase().includes(query) ||
    p.platform_home.toLowerCase().includes(query)
  )
})

const activePersona = computed(() => {
  const list = personas.value.length ? personas.value : MOCK_PERSONAS
  return list.find(p => p.persona_id === selectedPersonaId.value) || null
})

function getPersonaStats(personaId) {
  const run = session.value.simulationRun
  if (run?.private_reactions) {
    const reaction = run.private_reactions.find(r => r.persona_id === personaId)
    if (reaction) {
      return {
        rating: reaction.rating,
        dnf_probability: reaction.dnf_probability
      }
    }
  }
  return MOCK_REACTIONS[personaId] || { rating: null, dnf_probability: 0 }
}

// ----------------------------------------------------
// Chat Thread Histories Store
// ----------------------------------------------------
const chatHistories = ref({})

const currentHistory = computed(() => {
  if (!selectedPersonaId.value) return []
  if (!chatHistories.value[selectedPersonaId.value]) {
    const p = activePersona.value
    const name = p ? p.display_name : 'Reader'
    chatHistories.value[selectedPersonaId.value] = [
      {
        sender: 'persona',
        text: `Hello! I am ${name}. I finished reading the manuscript draft. Ask me why I rated it this way, where I felt DNF pressure, or what would make me raise my rating.`,
        basedOn: []
      }
    ]
  }
  return chatHistories.value[selectedPersonaId.value]
})

function selectPersona(id) {
  selectedPersonaId.value = id
  selectedEvidenceRef.value = ''
  scrollToBottom()
}

function syncDefaultPersona() {
  const list = filteredPersonas.value
  if (list.length && !selectedPersonaId.value) {
    selectedPersonaId.value = list[0].persona_id
  }
}

// ----------------------------------------------------
// Suggested Question Triggers
// ----------------------------------------------------
const quickQuestions = [
  'Why did you rate it this way?',
  'Where would you DNF?',
  'What would make you recommend it?',
  'What would increase your rating?',
  'What would your public review say?',
  'Which reader would love this?'
]

const canAsk = computed(() => Boolean(selectedPersonaId.value && questionText.value.trim()))

function triggerQuickQuestion(question) {
  questionText.value = question
  askPersona()
}

// Scroll chat log to bottom
function scrollToBottom() {
  nextTick(() => {
    if (chatScrollContainer.value) {
      chatScrollContainer.value.scrollTop = chatScrollContainer.value.scrollHeight
    }
  })
}

// ----------------------------------------------------
// Local Offline Query Resolver
// ----------------------------------------------------
function getLocalMockQueryResponse(personaId, question) {
  const p = activePersona.value
  const name = p ? p.display_name : 'Reader'
  const style = p ? p.review_style : 'generic'
  const stats = getPersonaStats(personaId)
  const ratingStr = stats.rating !== null ? `${stats.rating.toFixed(1)} stars` : 'N/A'
  const dnfPercent = `${Math.round((stats.dnf_probability || 0) * 100)}%`
  
  const q = question.toLowerCase()
  let answer = ''
  let based_on = []
  let signals = {}
  
  if (q.includes('dnf') || q.includes('finish') || q.includes('abandon')) {
    if (stats.dnf_probability >= 0.5) {
      answer = `I was in DNF territory (my abandonment probability reached ${dnfPercent}) because the pace sags dramatically in Chapter 3. The pacing drag points exceeded my patience threshold.`
    } else {
      answer = `I didn't feel strong DNF pressure (abandonment risk only ${dnfPercent}). The narrative pacing was enough to keep me engaged, even if Chapter 3 felt slightly slow.`
    }
    based_on = ['chapter_3', 'risk_pacing']
    signals = { dnf_probability: stats.dnf_probability }
  } else if (q.includes('raise') || q.includes('increase') || q.includes('higher') || q.includes('improve')) {
    answer = `My rating would rise if you tightened the pacing drag in the middle chapters (Chapter 3) and resolved character motivation contradictions. The overall prose density is strong but sags in the intermediate details.`
    based_on = ['chapter_3', 'style_prose', 'character_profile']
    signals = { target_improvements: ['pacing', 'character_motivation'] }
  } else if (q.includes('recommend')) {
    const recommendChance = stats.rating >= 4.0 ? '85%' : stats.rating >= 3.0 ? '55%' : '15%'
    answer = `My recommendation probability is around ${recommendChance}. I'd recommend it to fans of ${p.favorite_genres.join(' and ')}, but would warn them about ${p.disliked_patterns[0].toLowerCase()}.`
    based_on = ['market_surface', 'genre_suitability']
    signals = { recommendation_probability: stats.rating >= 4.0 ? 0.85 : 0.55 }
  } else if (q.includes('who') || q.includes('reader') || q.includes('love') || q.includes('hate')) {
    answer = `This book is a perfect fit for readers who love detailed worldbuilding and themes like ${p.favorite_genres[0]}. Casual readers who dislike ${p.disliked_patterns[0].toLowerCase()} might exit early.`
    based_on = ['market_surface', 'target_readers']
    signals = { target_segments: p.favorite_genres }
  } else if (q.includes('rate') || q.includes('rating') || q.includes('why')) {
    answer = `I landed at a rating of ${ratingStr} because I appreciated the overall theme and emotional payoff, but felt some friction around the pacing drag and tonal disruptions.`
    based_on = ['style_map', 'chapter_3']
    signals = { rating: stats.rating, sentiment: stats.rating >= 4.0 ? 'positive' : 'mixed' }
  } else if (q.includes('review') || q.includes('public')) {
    answer = `My public review would state: "Intriguing concept and strong prose styling, but sags in the intermediate chapters. Worth reading if you enjoy the genre, but needs pacing edits."`
    based_on = ['style_map', 'market_surface']
    signals = { review_style: style }
  } else {
    answer = `My general impression of the book is mixed. The premise has outstanding strengths, but the execution suffered from pacing drag and character motivation holes. Let me know if you want to discuss ratings or DNF triggers!`
    based_on = ['chapter_3', 'style_map']
    signals = { rating: stats.rating }
  }
  
  // Format based on review style
  if (style === 'emotional_confessional') {
    answer = `My gut reaction was this: ${answer}`
  } else if (style === 'analytical_skeptical') {
    answer = `My read is signal-based: ${answer}`
  } else if (style === 'aesthetic_curated') {
    answer = `The vibe matters here, and ${answer}`
  } else if (style === 'punchy_polarized') {
    answer = `Short version: ${answer}`
  } else if (style === 'critical_balanced') {
    answer = `From a critical perspective: ${answer}`
  }
  
  return {
    answer,
    based_on,
    signals,
    review_style: style
  }
}

// ----------------------------------------------------
// Chat execution
// ----------------------------------------------------
async function askPersona() {
  if (!canAsk.value) return
  const question = questionText.value.trim()
  const personaId = selectedPersonaId.value
  
  // 1. Add user question bubble
  currentHistory.value.push({
    sender: 'user',
    text: question,
    basedOn: []
  })
  
  questionText.value = ''
  scrollToBottom()
  
  // Determine if we should run mock offline or API
  const isMock = !session.value.projectId || session.value.projectId.startsWith('proj_demo_')
  
  if (isMock) {
    localLoading.value = true
    setTimeout(() => {
      const response = getLocalMockQueryResponse(personaId, question)
      currentHistory.value.push({
        sender: 'persona',
        text: response.answer,
        basedOn: response.based_on,
        signals: response.signals
      })
      localLoading.value = false
      scrollToBottom()
    }, 800)
  } else {
    loading.value = true
    localLoading.value = true
    error.value = ''
    try {
      const response = await chatWithBookPersona(personaId, {
        project_id: session.value.projectId,
        question: question
      })
      
      const res = response.data
      currentHistory.value.push({
        sender: 'persona',
        text: res.answer,
        basedOn: res.based_on || [],
        signals: res.signals || {}
      })
      
      // Update session chat logs
      updateSwarmbookSession({
        personaChat: {
          personaId: personaId,
          question: question,
          response: res
        }
      })
    } catch (requestError) {
      console.warn('API chat failed. Falling back to local offline query resolver.', requestError.message)
      // Graceful fallback to mock answer on API failure
      const response = getLocalMockQueryResponse(personaId, question)
      currentHistory.value.push({
        sender: 'persona',
        text: `(Offline Fallback) ${response.answer}`,
        basedOn: response.based_on,
        signals: response.signals
      })
    } finally {
      loading.value = false
      localLoading.value = false
      scrollToBottom()
    }
  }
}

// ----------------------------------------------------
// 4. Grounded Evidence Packs inspector lookups
// ----------------------------------------------------
const evidencePack = computed(() => session.value.evidencePack)

function selectEvidence(refId) {
  selectedEvidenceRef.value = refId
}

const selectedEvidenceDetail = computed(() => {
  const refId = selectedEvidenceRef.value
  if (!refId) return null
  
  const idLower = refId.toLowerCase()
  const pack = evidencePack.value
  
  if (pack) {
    // 1. Book DNA
    if (pack.book_dna && (idLower === 'book_dna' || idLower.includes('dna') || idLower.includes('premise'))) {
      const dna = pack.book_dna
      return {
        type: 'Book DNA',
        title: 'Book DNA Profile',
        summary: dna.premise || 'N/A',
        details: [
          `Genre: ${dna.genre || 'N/A'} (${dna.subgenre || 'N/A'})`,
          `Tone: ${dna.tone || 'N/A'}`,
          `Target Reader: ${dna.target_reader || 'N/A'}`,
          `Narrative Engine: ${dna.narrative_engine || 'N/A'}`,
          `Reading Difficulty: ${dna.reading_difficulty || 'N/A'}`
        ]
      }
    }

    // 2. Chapter Map
    if (pack.chapter_map?.chapters) {
      const chapter = pack.chapter_map.chapters.find(
        c => c.chapter_id?.toLowerCase() === idLower || 
             `chapter_${c.chapter_number}`.toLowerCase() === idLower ||
             `chapter_${c.chapter_id}`.toLowerCase() === idLower ||
             (c.title && c.title.toLowerCase().includes(idLower))
      )
      if (chapter) {
        return {
          type: 'Chapter Map',
          title: `Chapter ${chapter.chapter_number || chapter.chapter_id}${chapter.title ? ': ' + chapter.title : ''}`,
          summary: chapter.summary || chapter.beat_summary || 'N/A',
          details: [
            `Pacing Estimate: ${chapter.pacing || chapter.pacing_estimate || 'balanced'}`,
            `Stop Reading Risk: ${chapter.stop_reading_risk !== undefined ? Math.round(chapter.stop_reading_risk * 100) + '%' : 'N/A'}`,
            `Likely Reader Friction: ${chapter.likely_reader_friction?.join(', ') || chapter.confusion_hotspots?.join(', ') || 'none'}`
          ]
        }
      }
    }

    // 3. Character Map
    if (pack.character_map?.characters) {
      const char = pack.character_map.characters.find(
        c => c.character_id?.toLowerCase() === idLower || 
             (c.name && c.name.toLowerCase() === idLower) ||
             (c.name && idLower.includes(c.name.toLowerCase()))
      )
      if (char) {
        return {
          type: 'Character Map',
          title: `Character: ${char.name}`,
          summary: char.transformation_arc || 'N/A',
          details: [
            `Role: ${char.role || 'N/A'}`,
            `Goals: ${char.goals?.join(', ') || 'N/A'}`,
            `Conflicts: ${char.conflicts?.join(', ') || 'N/A'}`,
            `Attachment Potential: ${char.attachment_potential !== undefined ? Math.round(char.attachment_potential * 100) + '%' : 'N/A'}`
          ]
        }
      }
    }
    
    // 4. Claim Map
    if (pack.claim_map?.claims) {
      const claim = pack.claim_map.claims.find(
        c => c.claim_id?.toLowerCase() === idLower || idLower.includes(c.claim_id?.toLowerCase())
      )
      if (claim) {
        return {
          type: 'Claim Map',
          title: `Claim ${claim.claim_id}`,
          summary: claim.claim_text || 'N/A',
          details: [
            `Support Quality: ${claim.support_quality || 'moderate'}`,
            `Support Type: ${claim.support_type || 'N/A'}`,
            `Contradiction Risk: ${claim.contradiction_risk || 'low'}`,
            `Evidence Notes: ${claim.evidence_notes?.join(', ') || 'none'}`
          ]
        }
      }
    }
    
    // 5. Risk Map
    if (pack.risk_map?.risks) {
      const risk = pack.risk_map.risks.find(
        r => r.risk_id?.toLowerCase() === idLower || idLower.includes(r.risk_id?.toLowerCase())
      )
      if (risk) {
        return {
          type: 'Risk Map',
          title: `Risk: ${formatRadarLabel(risk.risk_type)}`,
          summary: risk.description || risk.trigger_text || 'N/A',
          details: [
            `Severity: ${risk.severity || 'moderate'}`,
            `Affected Segments: ${risk.affected_segments?.join(', ') || 'all'}`,
            `Editorial Mitigation: ${risk.mitigation_hint || 'N/A'}`
          ]
        }
      }
    }

    // 6. Style Map
    if (pack.style_map && (idLower === 'style_map' || idLower === 'style_prose' || idLower.includes('style'))) {
      const style = pack.style_map
      return {
        type: 'Style Map',
        title: 'Prose Style Analysis',
        summary: `Clarity: ${style.clarity || 'N/A'} • Density: ${style.density || 'N/A'}`,
        details: [
          `Rhythm: ${style.rhythm || 'N/A'}`,
          `Voice Consistency: ${style.voice_consistency || 'N/A'}`,
          `Quoteability: ${style.quoteability || 'N/A'}`,
          `Accessibility: ${style.accessibility || 'N/A'}`
        ]
      }
    }

    // 7. Market Surface
    if (pack.market_surface && (idLower === 'market_surface' || idLower === 'genre_suitability' || idLower.includes('market'))) {
      const market = pack.market_surface
      return {
        type: 'Market Surface',
        title: 'Market Surface Profile',
        summary: market.promise_gap || 'N/A',
        details: [
          `Target Segments: ${market.target_segments?.join(', ') || 'N/A'}`,
          `Discoverability Hooks: ${market.discoverability_hooks?.join(', ') || 'N/A'}`,
          `Comp Neighborhood: ${market.comp_title_neighborhood?.join(', ') || 'N/A'}`,
          `Positioning Notes: ${market.positioning_notes?.join(', ') || 'N/A'}`
        ]
      }
    }
  }
  
  // 8. Fallbacks for demo mock data
  if (idLower.includes('chapter_3')) {
    return {
      type: 'Chapter Map',
      title: 'Chapter 3: The Ascent',
      summary: 'The crew initiates the engine sequence. Pacing drops as characters engage in dense technical discussion of gravity physics.',
      details: ['Pacing: slow (physics infodump sags momentum)', 'Friction: technical jargon, slow start']
    }
  }
  if (idLower.includes('style_prose') || idLower.includes('style_map')) {
    return {
      type: 'Style Map',
      title: 'Prose Style analysis',
      summary: 'Prose is characterized by high image-making language and clear thematic rhythm, but suffers from density-driven comprehension blockages in expository segments.',
      details: ['Quoteability: High', 'Accessibility: Moderate', 'Clarity: Low-Moderate']
    }
  }
  if (idLower.includes('market_surface') || idLower.includes('genre_suitability')) {
    return {
      type: 'Market Surface',
      title: 'Target Audience Profile',
      summary: 'Positioned as high-concept speculative sci-fi. Strong discoverability hooks but carries a promise gap for casual drama readers.',
      details: ['Target segments: Hard SciFi, Speculative fiction fans', 'Promise gap: High']
    }
  }
  if (idLower.includes('risk_pacing') || idLower.includes('risk')) {
    return {
      type: 'Risk Map',
      title: 'Risk: Pacing Drag',
      summary: 'Pacing drag identified in early chapters, primarily driven by info-dumps and technical exposition.',
      details: ['Severity: Moderate', 'Mitigation: Trim physical description sequences by 20%']
    }
  }
  
  return {
    type: 'Evidence Reference',
    title: refId,
    summary: 'A reference citation marker logged by the reader during this reaction phase.',
    details: ['No deeper metadata is stored in the current workspace cache.']
  }
})

// ----------------------------------------------------
// UI formatting helpers
// ----------------------------------------------------
function formatPlatformLabel(platform) {
  if (!platform) return 'N/A'
  const mapping = {
    goodreads: 'Goodreads',
    booktok: 'BookTok',
    reddit: 'Reddit',
    bookstagram: 'Bookstagram',
    x: 'X / Twitter',
    newsletter: 'Newsletter',
    bookclub: 'Book Club'
  }
  return mapping[platform.toLowerCase()] || platform
}

function formatRadarLabel(key) {
  if (!key) return ''
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function ensureSession() {
  const pId = route.params.projectId
  if (pId && pId !== session.value.projectId) {
    session.value = updateSwarmbookSession({ projectId: pId })
  }
  syncDefaultPersona()
}

onMounted(() => {
  ensureSession()
})
</script>

<style scoped>
/* Redesigned Master-Detail UI Layout */

/* Interactive WCAG AA compliant focus outlines */
input:focus-visible,
textarea:focus-visible,
button:focus-visible,
.directory-item-btn:focus-visible,
.close-drawer-btn:focus-visible {
  outline: 2px solid #FF4500 !important;
  outline-offset: 2px !important;
}

.interview-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
  height: calc(100vh - 190px);
  min-height: 580px;
  overflow: hidden;
  position: relative; /* Container scope for sliding absolute drawer */
}

@media (max-width: 1100px) {
  .interview-container {
    grid-template-columns: 260px 1fr;
    height: auto;
    overflow: visible;
  }
}

@media (max-width: 800px) {
  .interview-container {
    grid-template-columns: 1fr;
    height: auto;
    overflow: visible;
  }
  .persona-sidebar {
    height: 320px;
    flex-shrink: 0;
  }
}

/* 1. Left Sidebar directory */
.persona-sidebar {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.search-box {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
}

.persona-directory-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.directory-item-btn {
  width: 100%;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  padding: 10px 12px;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: background 0.15s, border-color 0.15s;
  outline: none;
}

.directory-item-btn:hover {
  background: #f8fafc;
}

.directory-item-btn.active {
  background: #fff5ef;
  border-color: #ff4500;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 4px;
}

.item-name {
  font-size: 0.85rem;
  color: #0f172a;
}

.item-platform-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 1px 5px;
  border-radius: 3px;
}

.item-platform-tag.goodreads { background: #ecdcc9; color: #5c381c; }
.item-platform-tag.booktok { background: #000000; color: #ffffff; border: 1px solid #00f2fe; }
.item-platform-tag.reddit { background: #ffe9e0; color: #ff4500; }
.item-platform-tag.bookstagram { background: #fde2f3; color: #c13584; }
.item-platform-tag.x { background: #f1f5f9; color: #0f172a; }

.item-cohort {
  font-size: 0.72rem;
  color: #64748b;
  margin-bottom: 6px;
}

.item-stats-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
}

.item-stat-rating {
  color: #d97706;
}

.item-stat-dnf {
  color: #16a34a;
}

.item-stat-dnf.high-risk {
  color: #ef4444;
}

.empty-list-note {
  padding: 16px;
  font-style: italic;
  color: #94a3b8;
  text-align: center;
  font-size: 0.8rem;
}

/* Known Limitations Warning Banner */
.sandbox-limitations-banner {
  background: #fef3c7; /* Warm Amber */
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 0.78rem;
  color: #78350f;
  line-height: 1.4;
  flex-shrink: 0;
}

.banner-icon {
  font-size: 1rem;
  flex-shrink: 0;
  margin-top: 1px;
}

/* 2. Workspace details */
.interview-workspace {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* Profile details card */
.persona-profile-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 10px;
}

.profile-avatar {
  font-size: 1.5rem;
  background: #f1f5f9;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-meta h2 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
}

.profile-subheader {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 2px;
}

.profile-subheader strong {
  color: #334155;
}

.profile-details-grid {
  display: grid;
  grid-template-columns: 1.1fr 1.1fr 0.8fr;
  gap: 16px;
}

@media (max-width: 600px) {
  .profile-details-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

.detail-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.genre-tag {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.trigger-tag {
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #ffedd5;
}

.review-style-text {
  font-size: 0.75rem;
}

/* 3. Interactive Chat Panel */
.chat-workspace-panel {
  flex: 1;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-bubbles-timeline {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: #f8fafc;
}

.message-bubble-wrapper {
  display: flex;
  width: 100%;
}

.message-bubble-wrapper.user {
  justify-content: flex-end;
}

.message-bubble-wrapper.persona {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  font-size: 0.88rem;
  line-height: 1.45;
}

.user .message-bubble {
  background: #0f172a;
  color: #ffffff;
  border-top-right-radius: 2px;
}

.persona .message-bubble {
  background: #ffffff;
  color: #0f172a;
  border-top-left-radius: 2px;
  border: 1px solid #e2e8f0;
}

.loading-bubble {
  background: #f1f5f9 !important;
  color: #64748b !important;
  border: 1px dashed #cbd5e1 !important;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  font-weight: 600;
}

.pulsing-text {
  animation: loading-pulse 1.5s infinite;
}

@keyframes loading-pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.message-sender-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 6px;
  color: #94a3b8;
}

.user .message-sender-title {
  color: #cbd5e1;
}

.message-text {
  word-break: break-word;
}

.message-based-on {
  margin-top: 10px;
  border-top: 1px solid #e2e8f0;
  padding-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user .message-based-on {
  border-color: #334155;
}

.message-based-on .label {
  font-size: 0.68rem;
  font-weight: 600;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
}

.user .message-based-on .label {
  color: #94a3b8;
}

.citation-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.citation-pill {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
  outline: none;
}

.citation-pill:hover,
.citation-pill.active {
  background: #ff4500;
  color: #ffffff;
  border-color: #ff4500;
}

.user .citation-pill {
  background: #1e293b;
  border-color: #475569;
  color: #cbd5e1;
}

.user .citation-pill:hover {
  background: #ff4500;
  color: #ffffff;
}

/* Suggested questions panel */
.suggested-questions-row,
.suggested-questions-box {
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  padding: 10px 14px;
}

.suggested-questions-box .label {
  display: block;
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.shortcuts-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.shortcut-question-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 6px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
  outline: none;
}

.shortcut-question-btn:hover:not(:disabled) {
  background: #fff5ef;
  color: #ff4500;
  border-color: #ff4500;
}

.shortcut-question-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Chat Input Bar */
.chat-input-bar {
  display: flex;
  align-items: stretch;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  padding: 10px;
  gap: 10px;
}

.chat-input-bar textarea {
  flex: 1;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 8px 12px;
  font-family: inherit;
  font-size: 0.85rem;
  resize: none;
  outline: none;
  line-height: 1.4;
  height: 50px;
}

.submit-chat-btn {
  padding: 0 16px;
  height: 50px;
  flex-shrink: 0;
  font-size: 0.85rem;
}

/* 4. Sliding Evidence Inspector Drawer */
.evidence-drawer {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 320px;
  background: #ffffff;
  border-left: 1px solid #e2e8f0;
  box-shadow: -4px 0 12px rgba(15, 23, 42, 0.08);
  z-index: 100;
  transform: translateX(100%);
  transition: transform 0.3s ease-in-out;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.evidence-drawer.open {
  transform: translateX(0);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.drawer-header h2 {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.close-drawer-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 4px;
  line-height: 1;
  transition: background 0.15s, color 0.15s;
  outline: none;
}

.close-drawer-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.panel-desc {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.4;
  margin-bottom: 16px;
}

.evidence-detail-card {
  flex: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.evidence-type-badge {
  align-self: flex-start;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 800;
  background: #f59e0b;
  color: #ffffff;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.evidence-detail-card h3 {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
}

.evidence-summary-box {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 12px;
  font-size: 0.8rem;
  line-height: 1.45;
  color: #334155;
}

.evidence-summary-box strong {
  display: block;
  font-size: 0.68rem;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.evidence-meta-bullets {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-bullet {
  font-size: 0.78rem;
  color: #475569;
  line-height: 1.4;
}

.empty-evidence-box {
  flex: 1;
  border: 2px dashed #e2e8f0;
  border-radius: 6px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #94a3b8;
}

.box-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

.empty-evidence-box p {
  font-size: 0.78rem;
  line-height: 1.45;
}

/* Backdrop Overlay for Drawer */
.drawer-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.35);
  z-index: 90;
  backdrop-filter: blur(1px);
}

@media (max-width: 800px) {
  .drawer-backdrop {
    position: fixed;
    z-index: 999;
  }
  .evidence-drawer {
    width: 100%;
    position: fixed;
    top: 0;
    bottom: 0;
    right: 0;
    height: 100%;
    z-index: 1000;
  }
}

.animate-fade-in {
  animation: fade-in 0.2s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
