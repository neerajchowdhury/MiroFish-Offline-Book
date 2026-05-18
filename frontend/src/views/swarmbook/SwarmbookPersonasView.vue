<template>
  <SwarmbookLayout
    active-route="SwarmbookPersonas"
    :project-id="session.projectId"
    title="Persona Interrogation"
    subtitle="Question one simulated reader at a time using the stored Swarmbook reactions, posts, cross-reactions, and evidence refs."
    :status-text="loading ? 'Interrogating persona' : 'Persona chat ready'"
    :status-tone="loading ? 'loading' : 'ready'"
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <section class="grid">
      <article class="card">
        <h2>Ask A Reader</h2>
        <label class="stack">
          <span>Persona</span>
          <select v-model="chat.personaId">
            <option disabled value="">Select a persona</option>
            <option v-for="persona in personas" :key="persona.persona_id" :value="persona.persona_id">
              {{ persona.display_name }} · {{ persona.platform_home }}
            </option>
          </select>
        </label>

        <div class="stack">
          <span>Shortcuts</span>
          <div class="pill-row">
            <button v-for="question in quickQuestions" :key="question" class="pill" @click="chat.question = question">
              {{ question }}
            </button>
          </div>
        </div>

        <label class="stack">
          <span>Question</span>
          <textarea v-model="chat.question" rows="7"></textarea>
        </label>

        <div class="action-row">
          <button class="ghost-btn" @click="router.push({ name: 'SwarmbookReport', params: { projectId: session.projectId } })">
            Back To Report
          </button>
          <button class="primary-btn" :disabled="loading || !canAsk" @click="askPersona">
            {{ loading ? 'Asking...' : 'Ask Persona' }}
          </button>
        </div>
      </article>

      <article class="card">
        <h2>Response</h2>
        <template v-if="chat.response">
          <p>{{ chat.response.answer || 'No answer returned.' }}</p>
          <p><strong>Based on:</strong> {{ joinList(chat.response.based_on) }}</p>
          <p><strong>Signals:</strong> {{ joinList(chat.response.signals) }}</p>
        </template>
        <p v-else>No response yet.</p>
      </article>
    </section>
  </SwarmbookLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SwarmbookLayout from '../../components/swarmbook/SwarmbookLayout.vue'
import { chatWithBookPersona } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const chat = reactive({
  personaId: session.value.personaChat.personaId || '',
  question: session.value.personaChat.question || 'Why did you rate this book this way?',
  response: session.value.personaChat.response || null,
})
const loading = ref(false)
const loadingMessage = ref('')
const error = ref('')

const personas = computed(() => session.value.simulationRun?.reader_personas || [])
const canAsk = computed(() => Boolean(chat.personaId && chat.question.trim() && session.value.projectId))
const quickQuestions = [
  'Why did you rate this book this way?',
  'Why did you DNF?',
  'What would make you raise your rating?',
  'Would you recommend this book?',
  'Which reader would love or hate it?',
  'What exactly triggered your reaction?',
]

function ensureSession() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId || personas.value.length === 0) {
    router.replace({ name: 'SwarmbookHome' })
  }
}

async function askPersona() {
  loading.value = true
  loadingMessage.value = 'Querying stored persona artifacts...'
  error.value = ''
  try {
    const response = await chatWithBookPersona(chat.personaId, {
      project_id: session.value.projectId,
      question: chat.question,
    })
    chat.response = response.data
    session.value = updateSwarmbookSession({
      personaChat: {
        personaId: chat.personaId,
        question: chat.question,
        response: response.data,
      },
    })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
    loadingMessage.value = ''
  }
}

function joinList(value) {
  return value && value.length ? value.join(', ') : 'N/A'
}

onMounted(() => {
  ensureSession()
})
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 18px;
}

.card {
  border: 1px solid #e5e5e5;
  padding: 20px;
  background: #ffffff;
}

.card h2 {
  margin-bottom: 14px;
}

.stack {
  display: block;
  margin-bottom: 16px;
}

.stack span {
  display: block;
  font-size: 0.8rem;
  color: #666666;
  margin-bottom: 6px;
  font-family: 'JetBrains Mono', monospace;
}

textarea,
select {
  width: 100%;
  border: 1px solid #d9d9d9;
  padding: 12px;
  font: inherit;
}

.pill-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pill {
  border: 1px solid #d7d7d7;
  background: #ffffff;
  padding: 10px 12px;
  cursor: pointer;
}

.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
  flex-wrap: wrap;
}

.primary-btn,
.ghost-btn {
  border: 1px solid #000000;
  padding: 12px 16px;
  cursor: pointer;
  font: inherit;
}

.primary-btn {
  background: #000000;
  color: #ffffff;
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ghost-btn {
  background: #ffffff;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
