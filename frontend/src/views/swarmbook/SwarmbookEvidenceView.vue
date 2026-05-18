<template>
  <SwarmbookLayout
    active-route="SwarmbookEvidence"
    :project-id="session.projectId"
    title="Evidence Pack Preview"
    subtitle="Review the additive evidence artifacts before running the synthetic reader simulation."
    status-text="Evidence ready"
    status-tone="ready"
    :error-message="error"
  >
    <section v-if="!evidencePack" class="card">
      <p>No evidence pack is stored in the current session yet.</p>
      <div class="action-row">
        <button class="ghost-btn" @click="router.push({ name: 'SwarmbookMetadata', params: { projectId: session.projectId } })">
          Back To Metadata
        </button>
      </div>
    </section>

    <template v-else>
      <section class="grid">
        <article class="card">
          <h2>Book DNA</h2>
          <p><strong>Title:</strong> {{ evidencePack.book_dna?.title || metadata.title }}</p>
          <p><strong>Genre:</strong> {{ evidencePack.book_dna?.genre || metadata.genre || 'N/A' }}</p>
          <p><strong>Premise:</strong> {{ evidencePack.book_dna?.premise || 'N/A' }}</p>
          <p><strong>Target reader:</strong> {{ evidencePack.book_dna?.target_reader || metadata.targetReader || 'N/A' }}</p>
        </article>

        <article class="card">
          <h2>Market Surface</h2>
          <p><strong>Audience fit:</strong> {{ evidencePack.market_surface?.audience_fit || 'N/A' }}</p>
          <p><strong>Hooks:</strong> {{ joinList(evidencePack.market_surface?.discoverability_hooks) }}</p>
          <p><strong>Packaging:</strong> {{ joinList(evidencePack.market_surface?.packaging_expectations) }}</p>
          <p><strong>Promise gap:</strong> {{ evidencePack.market_surface?.promise_gap || 'None noted' }}</p>
        </article>
      </section>

      <section class="grid">
        <article class="card">
          <h2>Chapter Map</h2>
          <ul class="list">
            <li v-for="chapter in evidencePack.chapter_map?.chapters || []" :key="chapter.chapter_id">
              <strong>Ch {{ chapter.chapter_number }}</strong>
              <span>{{ chapter.title || 'Untitled' }}</span>
              <p>{{ chapter.summary || 'No summary' }}</p>
            </li>
          </ul>
        </article>

        <article class="card">
          <h2>Character Map</h2>
          <ul class="list">
            <li v-for="character in evidencePack.character_map?.characters || []" :key="character.character_id">
              <strong>{{ character.name }}</strong>
              <span>{{ character.role || 'Unknown role' }}</span>
              <p>{{ joinList(character.reader_friction) }}</p>
            </li>
          </ul>
        </article>
      </section>

      <section class="grid">
        <article class="card">
          <h2>Claim Map</h2>
          <ul class="list">
            <li v-for="claim in evidencePack.claim_map?.claims || []" :key="claim.claim_id">
              <strong>{{ claim.claim_text }}</strong>
              <p>Support strength: {{ claim.evidence_strength ?? 'N/A' }}</p>
            </li>
          </ul>
        </article>

        <article class="card">
          <h2>Risk Map</h2>
          <ul class="list">
            <li v-for="risk in evidencePack.risk_map?.risks || []" :key="risk.risk_id">
              <strong>{{ risk.risk_type }}</strong>
              <p>{{ risk.description || risk.mitigation_hint || 'No detail' }}</p>
            </li>
          </ul>
        </article>
      </section>

      <section class="grid">
        <article class="card">
          <h2>Style Map</h2>
          <p><strong>Clarity:</strong> {{ evidencePack.style_map?.clarity || 'N/A' }}</p>
          <p><strong>Rhythm:</strong> {{ evidencePack.style_map?.rhythm || 'N/A' }}</p>
          <p><strong>Quoteability:</strong> {{ evidencePack.style_map?.quoteability || 'N/A' }}</p>
          <p><strong>Notes:</strong> {{ joinList(evidencePack.style_map?.style_notes) }}</p>
        </article>

        <article class="card">
          <h2>Session Metadata</h2>
          <p><strong>Book type:</strong> {{ metadata.bookType }}</p>
          <p><strong>Genre:</strong> {{ metadata.genre || 'N/A' }}</p>
          <p><strong>Comp titles:</strong> {{ metadata.compTitles || 'N/A' }}</p>
          <p><strong>Cover brief:</strong> {{ metadata.coverBrief || 'N/A' }}</p>
        </article>
      </section>

      <div class="action-row">
        <button class="ghost-btn" @click="router.push({ name: 'SwarmbookMetadata', params: { projectId: session.projectId } })">
          Back To Metadata
        </button>
        <button class="primary-btn" @click="router.push({ name: 'SwarmbookSimulation', params: { projectId: session.projectId } })">
          Continue To Simulation Controls
        </button>
      </div>
    </template>
  </SwarmbookLayout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import SwarmbookLayout from '../../components/swarmbook/SwarmbookLayout.vue'
import { getSwarmbookSession } from '../../store/swarmbookSession'

const router = useRouter()
const session = ref(getSwarmbookSession())
const error = ref('')

const evidencePack = computed(() => session.value.evidencePack)
const metadata = computed(() => session.value.metadata)

function joinList(value) {
  if (!value || value.length === 0) {
    return 'N/A'
  }
  return value.join(', ')
}
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 18px;
}

.card {
  border: 1px solid #e5e5e5;
  padding: 20px;
  background: #ffffff;
}

.card h2 {
  margin-bottom: 14px;
}

.card p {
  line-height: 1.6;
  margin-bottom: 10px;
}

.list {
  list-style: none;
  display: grid;
  gap: 12px;
}

.list li {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 12px;
}

.list strong,
.list span {
  display: block;
}

.action-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
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

.ghost-btn {
  background: #ffffff;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
