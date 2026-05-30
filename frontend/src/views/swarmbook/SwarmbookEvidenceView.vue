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
        <div class="empty-icon" aria-hidden="true">📂</div>
        <h2>No Editorial Evidence Pack Compiled</h2>
        <p>You must load your manuscript draft first to extract story maps, claim paths, and style indicators.</p>
        <div class="action-row-center">
          <button class="sb-btn-primary" @click="goToUpload">
            Go to Manuscript Ingest
          </button>
        </div>
      </section>

      <!-- Main Dashboard Grid Layout -->
      <div v-else class="evidence-dashboard-flow">
        <!-- Review Progress Panel -->
        <header class="review-status-strip sb-card">
          <div class="progress-info">
            <h3>Review Status</h3>
            <p>
              Reviewed: <strong>{{ reviewedCount }} of 7</strong> maps accepted.
              Critical maps reviewed: <strong>{{ criticalReviewedCount }} of {{ criticalPacks.length }}</strong>.
            </p>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-track">
              <div 
                class="progress-bar-fill" 
                :style="{ width: (reviewedCount / 7 * 100) + '%' }"
              ></div>
            </div>
          </div>
        </header>

        <!-- Unreviewed Critical Maps Blocking Warning Banner -->
        <section 
          v-if="isSimulationBlocked" 
          class="unreviewed-warning-banner"
          role="alert"
        >
          <span class="warning-icon" aria-hidden="true">⚠️</span>
          <div class="warning-text">
            <strong>Simulation Blocked:</strong> You have unreviewed critical evidence maps:
            <span class="critical-pack-list">{{ unreviewedCriticalNames.join(', ') }}</span>.
            Please open details and click <strong>Accept &amp; Lock Map</strong> to enable progression.
          </div>
        </section>

        <!-- Cards Grid Area -->
        <main class="evidence-grid" role="region" aria-label="Evidence Maps Catalog">
          <div
            v-for="map in maps"
            :key="map.id"
            class="map-card-item sb-card"
            :class="{ 
              active: activeMapId === map.id && isDrawerOpen, 
              accepted: getStatus(map.id) === 'accepted',
              'needs-review': getStatus(map.id) === 'needs review',
              'is-critical': isPackCritical(map.id)
            }"
            @click="openDetails(map.id)"
            @keydown.enter="openDetails(map.id)"
            @keydown.space.prevent="openDetails(map.id)"
            role="button"
            tabindex="0"
            :aria-label="`Review ${map.label} map`"
          >
            <div class="card-top-header">
              <div class="title-with-icon">
                <span class="card-icon" aria-hidden="true">{{ map.icon }}</span>
                <div class="label-box">
                  <h3>{{ map.label }}</h3>
                  <span class="critical-indicator" v-if="isPackCritical(map.id)">
                    Critical Pack
                  </span>
                </div>
              </div>
              <span class="sb-badge" :class="getStatusBadgeClass(map.id)">
                {{ getStatusLabel(map.id) }}
              </span>
            </div>
            
            <p class="card-summary">{{ getMapSummary(map.id) }}</p>

            <div class="card-confidence-row">
              <div class="confidence-stats">
                <span class="confidence-val">
                  Confidence: {{ Math.round(getConfidence(map.id) * 100) }}%
                </span>
                <span v-if="getConfidence(map.id) < 0.75" class="low-confidence-tag">
                  ⚠️ Low
                </span>
              </div>
              <div class="confidence-bar-track">
                <div 
                  class="confidence-bar-fill" 
                  :class="{ 'low-confidence': getConfidence(map.id) < 0.75 }"
                  :style="{ width: (getConfidence(map.id) * 100) + '%' }"
                ></div>
              </div>
            </div>

            <div class="card-refs-row">
              <span class="evidence-ref-count" v-if="getReferencesCount(map.id)">
                📚 {{ getReferencesCount(map.id) }} evidence refs
              </span>
              <span class="evidence-ref-count" v-else>
                📂 0 refs
              </span>
            </div>

            <!-- Card Actions -->
            <footer class="card-actions-row" @click.stop>
              <button 
                class="card-btn-ghost view-details" 
                @click="openDetails(map.id)" 
                aria-label="View detailed analysis parameters"
              >
                View Details
              </button>
              <button 
                class="card-btn-ghost regenerate" 
                :disabled="loadingMessage !== ''"
                @click="regenerateMap(map.id)"
                aria-label="Re-analyze manuscript section"
              >
                🔄 Refresh
              </button>
              <button 
                class="card-btn-ghost accept" 
                :disabled="getStatus(map.id) === 'accepted'"
                @click="acceptMap(map.id)"
                aria-label="Verify and lock map accuracy"
              >
                ✓ Accept
              </button>
            </footer>
          </div>
        </main>
      </div>

      <!-- Footer Global Actions -->
      <footer class="global-actions-bar" v-if="evidencePack">
        <button class="sb-btn-ghost" @click="goBackToUpload">
          ← Back To Ingest
        </button>
        <div class="proceed-wrapper">
          <span class="proceed-hint-label" v-if="isSimulationBlocked">
            Accept critical maps to enable simulation
          </span>
          <button 
            class="sb-btn-primary" 
            :disabled="isSimulationBlocked"
            @click="continueToSimulation"
          >
            Continue To Simulation Swarm 🚀
          </button>
        </div>
      </footer>

      <!-- Drawer Backdrop -->
      <div 
        v-if="isDrawerOpen" 
        class="drawer-backdrop" 
        @click="closeDrawer"
        role="presentation"
      ></div>

      <!-- Sliding Detail Drawer -->
      <div 
        class="detail-drawer" 
        :class="{ 'is-open': isDrawerOpen }"
        role="dialog"
        aria-modal="true"
        :aria-label="activeMap ? `${activeMap.label} Details` : 'Map Details'"
        tabindex="-1"
        ref="drawerRef"
      >
        <div class="drawer-inner" v-if="activeMap">
          <header class="drawer-header">
            <div class="drawer-header-left">
              <span class="drawer-icon" aria-hidden="true">{{ activeMap.icon }}</span>
              <div>
                <h2>{{ activeMap.label }} Details</h2>
                <div class="drawer-badges">
                  <span class="sb-badge" :class="getStatusBadgeClass(activeMap.id)">
                    {{ getStatusLabel(activeMap.id) }}
                  </span>
                  <span class="confidence-badge" :class="{ 'low-confidence-text': getConfidence(activeMap.id) < 0.75 }">
                    🎯 Confidence: {{ Math.round(getConfidence(activeMap.id) * 100) }}%
                    <span v-if="getConfidence(activeMap.id) < 0.75"> (⚠️ Low)</span>
                  </span>
                </div>
              </div>
            </div>
            <button 
              class="close-btn" 
              @click="closeDrawer" 
              aria-label="Close details drawer"
            >
              ✕
            </button>
          </header>

          <!-- Scrollable content -->
          <div class="drawer-content">
            <!-- Why This Matters -->
            <section class="drawer-section importance-card">
              <strong>💡 Why This Matters</strong>
              <p>{{ activeMap.importance }}</p>
            </section>

            <!-- Structured Data Display -->
            <section class="drawer-section structured-data-container">
              <h3>Extracted Structured Data</h3>
              
              <!-- DNA Structured View -->
              <div v-if="activeMap.id === 'dna'" class="structured-view">
                <div class="structured-row">
                  <span class="structured-label">Title</span>
                  <span class="structured-value">{{ evidencePack.book_dna?.title || 'Untitled' }}</span>
                </div>
                <div class="structured-row">
                  <span class="structured-label">Book Type</span>
                  <span class="structured-value">{{ evidencePack.book_dna?.book_type || 'N/A' }}</span>
                </div>
                <div class="structured-row">
                  <span class="structured-label">Genre</span>
                  <span class="structured-value">{{ evidencePack.book_dna?.genre || 'N/A' }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.book_dna?.subgenre">
                  <span class="structured-label">Subgenre</span>
                  <span class="structured-value">{{ evidencePack.book_dna.subgenre }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.book_dna?.tone">
                  <span class="structured-label">Tone</span>
                  <span class="structured-value">{{ evidencePack.book_dna.tone }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.book_dna?.reading_difficulty">
                  <span class="structured-label">Reading Difficulty</span>
                  <span class="structured-value">{{ evidencePack.book_dna.reading_difficulty }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.book_dna?.target_reader">
                  <span class="structured-label">Target Reader</span>
                  <span class="structured-value">{{ evidencePack.book_dna.target_reader }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.book_dna?.narrative_engine">
                  <span class="structured-label">Narrative Engine</span>
                  <span class="structured-value">{{ evidencePack.book_dna.narrative_engine }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.book_dna?.emotional_promise">
                  <span class="structured-label">Emotional Promise</span>
                  <span class="structured-value">{{ evidencePack.book_dna.emotional_promise }}</span>
                </div>
                
                <div class="drawer-sub-block" v-if="evidencePack.book_dna?.themes?.length">
                  <h4>Extracted Themes</h4>
                  <div class="tag-list">
                    <span v-for="theme in evidencePack.book_dna.themes" :key="theme" class="theme-tag">
                      #{{ theme }}
                    </span>
                  </div>
                </div>
                
                <div class="drawer-sub-block" v-if="evidencePack.book_dna?.comparable_titles?.length">
                  <h4>Comparable Titles</h4>
                  <div class="tag-list">
                    <span v-for="title in evidencePack.book_dna.comparable_titles" :key="title" class="comp-tag">
                      📖 {{ title }}
                    </span>
                  </div>
                </div>

                <div class="drawer-sub-block premise-quote-block" v-if="evidencePack.book_dna?.premise">
                  <h4>Core Narrative Premise</h4>
                  <blockquote>"{{ evidencePack.book_dna.premise }}"</blockquote>
                </div>
              </div>

              <!-- Market Surface Structured View -->
              <div v-if="activeMap.id === 'market'" class="structured-view">
                <div class="structured-row">
                  <span class="structured-label">Audience Fit</span>
                  <span class="structured-value">
                    <span class="sb-badge" :class="getAudienceFitBadgeClass(evidencePack.market_surface?.audience_fit)">
                      {{ evidencePack.market_surface?.audience_fit || 'Medium' }}
                    </span>
                  </span>
                </div>
                
                <div class="drawer-sub-block" v-if="evidencePack.market_surface?.target_segments?.length">
                  <h4>Target Reader Segments</h4>
                  <ul>
                    <li v-for="seg in evidencePack.market_surface.target_segments" :key="seg">
                      {{ seg }}
                    </li>
                  </ul>
                </div>
                
                <div class="drawer-sub-block" v-if="evidencePack.market_surface?.discoverability_hooks?.length">
                  <h4>Discoverability Hooks</h4>
                  <div class="tag-list">
                    <span v-for="hook in evidencePack.market_surface.discoverability_hooks" :key="hook" class="hook-tag">
                      🔑 {{ hook }}
                    </span>
                  </div>
                </div>
                
                <div class="drawer-sub-block" v-if="evidencePack.market_surface?.packaging_expectations?.length">
                  <h4>Packaging Expectations</h4>
                  <ul>
                    <li v-for="exp in evidencePack.market_surface.packaging_expectations" :key="exp">
                      {{ exp }}
                    </li>
                  </ul>
                </div>

                <div class="drawer-sub-block warning-callout-block" v-if="evidencePack.market_surface?.promise_gap">
                  <h4>Promise Gap / Friction Risk</h4>
                  <p>{{ evidencePack.market_surface.promise_gap }}</p>
                </div>
              </div>

              <!-- Chapter Map Structured View -->
              <div v-if="activeMap.id === 'chapters'" class="structured-view">
                <div class="structured-row">
                  <span class="structured-label">Total Chapters</span>
                  <span class="structured-value">{{ evidencePack.chapter_map?.total_chapters || evidencePack.chapter_map?.chapters?.length || 0 }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.chapter_map?.pacing_profile">
                  <span class="structured-label">Pacing Profile</span>
                  <span class="structured-value">{{ evidencePack.chapter_map.pacing_profile }}</span>
                </div>

                <div class="drawer-sub-block" v-if="evidencePack.chapter_map?.structural_notes?.length">
                  <h4>Structural Pacing Notes</h4>
                  <ul>
                    <li v-for="note in evidencePack.chapter_map.structural_notes" :key="note">
                      {{ note }}
                    </li>
                  </ul>
                </div>

                <div class="drawer-sub-block chapters-timeline-list">
                  <h4>Chapters Summary &amp; Pacing Map</h4>
                  <div class="timeline-accordion">
                    <details 
                      v-for="ch in evidencePack.chapter_map?.chapters || []" 
                      :key="ch.chapter_id"
                      class="timeline-ch-details"
                    >
                      <summary class="timeline-ch-summary">
                        <span class="ch-num">Ch {{ ch.chapter_number }}</span>
                        <strong class="ch-title">{{ ch.title || 'Untitled Chapter' }}</strong>
                        <span class="ch-pacing-badge" :class="ch.pacing?.toLowerCase()">{{ ch.pacing || 'Normal' }}</span>
                      </summary>
                      <div class="ch-details-expanded">
                        <p class="ch-desc">{{ ch.summary || 'No summary generated.' }}</p>
                        
                        <div class="ch-meta-grid">
                          <div v-if="ch.purpose">
                            <strong>🎯 Purpose:</strong>
                            <p>{{ ch.purpose }}</p>
                          </div>
                          <div v-if="ch.pacing_note">
                            <strong>⏳ Pacing Detail:</strong>
                            <p>{{ ch.pacing_note }}</p>
                          </div>
                        </div>

                        <div class="ch-list-sec" v-if="ch.key_beats?.length">
                          <strong>🔑 Key Beats:</strong>
                          <ul>
                            <li v-for="beat in ch.key_beats" :key="beat">{{ beat }}</li>
                          </ul>
                        </div>

                        <div class="ch-list-sec" v-if="ch.emotional_beats?.length">
                          <strong>❤️ Emotional Beats:</strong>
                          <ul>
                            <li v-for="beat in ch.emotional_beats" :key="beat">{{ beat }}</li>
                          </ul>
                        </div>

                        <div class="ch-list-sec" v-if="ch.turning_points?.length">
                          <strong>🔄 Turning Points:</strong>
                          <ul>
                            <li v-for="tp in ch.turning_points" :key="tp">{{ tp }}</li>
                          </ul>
                        </div>

                        <div class="ch-list-sec warning" v-if="ch.likely_reader_friction?.length">
                          <strong>⚠️ Predicted Empathy Friction:</strong>
                          <ul>
                            <li v-for="fric in ch.likely_reader_friction" :key="fric">{{ fric }}</li>
                          </ul>
                        </div>
                      </div>
                    </details>
                  </div>
                </div>
              </div>

              <!-- Character Map Structured View -->
              <div v-if="activeMap.id === 'characters'" class="structured-view">
                <div class="structured-row">
                  <span class="structured-label">Cast Size</span>
                  <span class="structured-value">{{ evidencePack.character_map?.cast_size || evidencePack.character_map?.characters?.length || 0 }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.character_map?.relationship_graph_summary">
                  <span class="structured-label">Relationship Graph Summary</span>
                  <span class="structured-value">{{ evidencePack.character_map.relationship_graph_summary }}</span>
                </div>

                <div class="drawer-sub-block character-details-list">
                  <h4>Identified Dramatis Personae</h4>
                  <div class="character-details-card-list">
                    <div 
                      v-for="char in evidencePack.character_map?.characters || []" 
                      :key="char.character_id"
                      class="character-details-card"
                    >
                      <div class="char-details-hdr">
                        <h4>{{ char.name }}</h4>
                        <span class="role-badge" :class="char.role?.toLowerCase() || 'secondary'">
                          {{ char.role || 'Secondary' }}
                        </span>
                      </div>
                      <p class="char-arc" v-if="char.arc_summary">
                        <strong>Arc:</strong> {{ char.arc_summary }}
                      </p>
                      <div class="char-attributes">
                        <div v-if="char.motivations?.length">
                          <strong>Motivations:</strong> {{ char.motivations.join(', ') }}
                        </div>
                        <div v-if="char.goals?.length">
                          <strong>Goals:</strong> {{ char.goals.join(', ') }}
                        </div>
                        <div v-if="char.conflicts?.length">
                          <strong>Conflicts:</strong> {{ char.conflicts.join(', ') }}
                        </div>
                        <div v-if="char.relationships && Object.keys(char.relationships).length">
                          <strong>Relationships:</strong>
                          <span class="rel-tag" v-for="(rel, partner) in char.relationships" :key="partner">
                            {{ partner }} ({{ rel }})
                          </span>
                        </div>
                      </div>
                      <div class="char-friction-warning" v-if="char.reader_friction?.length">
                        <strong>empathy Friction Points:</strong>
                        <ul>
                          <li v-for="fric in char.reader_friction" :key="fric">{{ fric }}</li>
                        </ul>
                      </div>
                    </div>
                    <div v-if="!evidencePack.character_map?.characters?.length" class="no-data-note">
                      No characters identified. This map applies primarily to fiction layouts.
                    </div>
                  </div>
                </div>
              </div>

              <!-- Claim Map Structured View -->
              <div v-if="activeMap.id === 'claims'" class="structured-view">
                <div class="structured-row" v-if="evidencePack.claim_map?.thesis_summary">
                  <span class="structured-label">Thesis Summary</span>
                  <span class="structured-value">{{ evidencePack.claim_map.thesis_summary }}</span>
                </div>
                <div class="structured-row" v-if="evidencePack.claim_map?.argument_strength_summary">
                  <span class="structured-label">Argument Strength Summary</span>
                  <span class="structured-value">{{ evidencePack.claim_map.argument_strength_summary }}</span>
                </div>

                <div class="drawer-sub-block claim-details-list">
                  <h4>Extracted Claims &amp; Evidence Support</h4>
                  <div class="claim-details-card-list">
                    <div 
                      v-for="claim in evidencePack.claim_map?.claims || []" 
                      :key="claim.claim_id"
                      class="claim-details-card"
                    >
                      <p class="claim-quote">"{{ claim.claim_text }}"</p>
                      <div class="claim-support-info">
                        <div class="support-field">
                          <span>Evidence Strength:</span>
                          <strong :class="claim.evidence_strength >= 0.7 ? 'strong' : claim.evidence_strength >= 0.4 ? 'medium' : 'weak'">
                            {{ Math.round((claim.evidence_strength || 0) * 100) }}%
                          </strong>
                        </div>
                        <div class="support-field" v-if="claim.support_type">
                          <span>Type:</span>
                          <strong>{{ claim.support_type }}</strong>
                        </div>
                      </div>

                      <div class="claim-details-sub" v-if="claim.evidence_items?.length">
                        <strong>📚 Listed Citations:</strong>
                        <ul>
                          <li v-for="item in claim.evidence_items" :key="item">{{ item }}</li>
                        </ul>
                      </div>

                      <div class="claim-details-sub" v-if="claim.factual_risk_flags?.length">
                        <strong>🚩 Factual Risk Flags:</strong>
                        <ul>
                          <li v-for="flag in claim.factual_risk_flags" :key="flag">{{ flag }}</li>
                        </ul>
                      </div>

                      <div class="claim-details-sub" v-if="claim.counterarguments?.length">
                        <strong>💬 Counterarguments:</strong>
                        <ul>
                          <li v-for="ca in claim.counterarguments" :key="ca">{{ ca }}</li>
                        </ul>
                      </div>
                    </div>
                    <div v-if="!evidencePack.claim_map?.claims?.length" class="no-data-note">
                      No claims identified. This map applies primarily to nonfiction layouts.
                    </div>
                  </div>
                </div>
              </div>

              <!-- Risk Map Structured View -->
              <div v-if="activeMap.id === 'risks'" class="structured-view">
                <div class="structured-row" v-if="evidencePack.risk_map?.risk_summary">
                  <span class="structured-label">General Risk Summary</span>
                  <span class="structured-value">{{ evidencePack.risk_map.risk_summary }}</span>
                </div>

                <div class="drawer-sub-block risk-details-list">
                  <h4>Active Risk Items Log</h4>
                  <div class="risk-details-card-list">
                    <div 
                      v-for="risk in evidencePack.risk_map?.risks || []" 
                      :key="risk.risk_id"
                      class="risk-details-card"
                    >
                      <div class="risk-details-hdr">
                        <span class="sb-badge sb-badge--error">{{ risk.risk_type }}</span>
                        <span class="severity-badge" :class="risk.severity?.toLowerCase()">
                          {{ risk.severity || 'Medium' }}
                        </span>
                      </div>
                      <p class="risk-desc">{{ risk.description }}</p>
                      <p class="risk-trigger" v-if="risk.trigger_text">
                        <strong>Trigger Text:</strong> <code>{{ risk.trigger_text }}</code>
                      </p>
                      <div class="risk-mitigation" v-if="risk.mitigation_hint">
                        <strong>💡 Suggested Revision Hint:</strong>
                        <p>{{ risk.mitigation_hint }}</p>
                      </div>
                    </div>
                    <div v-if="!evidencePack.risk_map?.risks?.length" class="no-data-note">
                      No active editorial risks detected in manuscript draft.
                    </div>
                  </div>
                </div>
              </div>

              <!-- Style Map Structured View -->
              <div v-if="activeMap.id === 'style'" class="structured-view">
                <div class="structured-row">
                  <span class="structured-label">Prose Density</span>
                  <span class="structured-value">{{ evidencePack.style_map?.prose_density || 'N/A' }}</span>
                </div>
                <div class="structured-row">
                  <span class="structured-label">Clarity</span>
                  <span class="structured-value">{{ evidencePack.style_map?.clarity || 'N/A' }}</span>
                </div>
                <div class="structured-row">
                  <span class="structured-label">Rhythm</span>
                  <span class="structured-value">{{ evidencePack.style_map?.rhythm || 'N/A' }}</span>
                </div>
                <div class="structured-row">
                  <span class="structured-label">Consistency</span>
                  <span class="structured-value">{{ evidencePack.style_map?.voice_consistency || 'N/A' }}</span>
                </div>
                <div class="structured-row">
                  <span class="structured-label">Quoteability</span>
                  <span class="structured-value">{{ evidencePack.style_map?.quoteability || 'N/A' }}</span>
                </div>
                <div class="structured-row">
                  <span class="structured-label">Accessibility</span>
                  <span class="structured-value">{{ evidencePack.style_map?.accessibility || 'N/A' }}</span>
                </div>

                <div class="drawer-sub-block" v-if="evidencePack.style_map?.style_notes?.length">
                  <h4>Stylistic Details &amp; Notes</h4>
                  <ul>
                    <li v-for="note in evidencePack.style_map.style_notes" :key="note">
                      {{ note }}
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            <!-- Source References Section -->
            <section class="drawer-section source-refs-section" v-if="activeMapSourceRefs.length">
              <h3>📚 Source Evidence References</h3>
              <p class="section-hint">Raw block markers extracted from manuscript processing caches:</p>
              <ul class="source-refs-list">
                <li v-for="ref in activeMapSourceRefs" :key="ref">
                  <code>{{ ref }}</code>
                </li>
              </ul>
            </section>

            <!-- Editorial Corrections Section -->
            <section class="drawer-section corrections-section">
              <h3>📝 Editorial Corrections &amp; Directives</h3>
              <p class="section-hint">Provide instructions or details to guide the reader swarm during the simulation run.</p>
              <textarea
                v-model="editorialCorrections[activeMap.id]"
                rows="3"
                placeholder="e.g. Note that Mara's motivation changes here. Adjust style guidelines..."
              ></textarea>
              <div class="corrections-actions">
                <button class="sb-btn-ghost sm" @click="saveCorrections(activeMap.id)">
                  Save Corrections
                </button>
              </div>
            </section>

            <!-- Advanced View Toggle -->
            <section class="drawer-section advanced-json-section">
              <details class="json-details">
                <summary class="json-summary">Advanced View (Raw Component JSON)</summary>
                <div class="json-content">
                  <pre><code class="raw-json-code">{{ JSON.stringify(getMapRawData(activeMap.id), null, 2) }}</code></pre>
                </div>
              </details>
            </section>
          </div>

          <!-- Drawer Footer Actions -->
          <footer class="drawer-footer">
            <button 
              class="sb-btn-ghost flag-needs-review" 
              :disabled="getStatus(activeMap.id) === 'needs review'"
              @click="markNeedsReview(activeMap.id)"
            >
              ⚠️ Flag Needs Review
            </button>
            <button 
              class="sb-btn-primary accept-lock" 
              :disabled="getStatus(activeMap.id) === 'accepted'"
              @click="acceptMap(activeMap.id)"
            >
              ✓ Accept &amp; Lock Map
            </button>
          </footer>
        </div>
      </div>
    </div>
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'
import { createEvidencePack } from '../../api/bookSim'

const router = useRouter()
const session = ref(getSwarmbookSession())

const evidencePack = computed(() => session.value.evidencePack)

const activeMapId = ref('dna')
const isDrawerOpen = ref(false)
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

// Review stats helpers
const reviewedCount = computed(() => {
  return Object.values(cardStates).filter(state => state.status === 'accepted').length
})

const criticalPacks = computed(() => {
  const type = session.value.metadata?.bookType || 'fiction'
  const list = ['dna', 'chapters']
  if (type === 'fiction') {
    list.push('characters')
  } else if (type === 'nonfiction') {
    list.push('claims')
  }
  return list
})

const criticalReviewedCount = computed(() => {
  return criticalPacks.value.filter(id => getStatus(id) === 'accepted').length
})

const unreviewedCriticalPacks = computed(() => {
  return criticalPacks.value.filter(id => getStatus(id) !== 'accepted')
})

const unreviewedCriticalNames = computed(() => {
  return unreviewedCriticalPacks.value.map(id => maps.find(m => m.id === id)?.label)
})

const isSimulationBlocked = computed(() => {
  return unreviewedCriticalPacks.value.length > 0
})

const activeMapSourceRefs = computed(() => {
  if (!evidencePack.value || !activeMap.value) return []
  const mapData = evidencePack.value[activeMap.value.field]
  return mapData?.evidence_refs || []
})

function isPackCritical(mapId) {
  return criticalPacks.value.includes(mapId)
}

function getStatus(mapId) {
  return cardStates[mapId]?.status || 'pending'
}

function getStatusLabel(mapId) {
  const status = getStatus(mapId)
  if (status === 'generated') return 'unreviewed'
  return status
}

function getStatusBadgeClass(mapId) {
  const status = getStatus(mapId)
  if (status === 'accepted') return 'sb-badge--ok'
  if (status === 'needs review') return 'sb-badge--warn'
  if (status === 'regenerating') return 'sb-badge--warn'
  return 'sb-badge--info' // unreviewed/generated
}

function getAudienceFitBadgeClass(fit) {
  const fitStr = String(fit || '').toLowerCase()
  if (fitStr.includes('high')) return 'sb-badge--ok'
  if (fitStr.includes('low')) return 'sb-badge--error'
  return 'sb-badge--warn'
}

function getConfidence(mapId) {
  if (evidencePack.value) {
    const mapField = maps.find(m => m.id === mapId)?.field
    const backendConfidence = evidencePack.value[mapField]?.confidence
    if (backendConfidence !== undefined && backendConfidence !== null) {
      return backendConfidence
    }
  }
  return cardStates[mapId]?.confidence || 0.85
}

function getReferencesCount(mapId) {
  if (!evidencePack.value) return 0
  const mapField = maps.find(m => m.id === mapId)?.field
  const refs = evidencePack.value[mapField]?.evidence_refs
  if (refs && Array.isArray(refs)) return refs.length
  
  if (mapId === 'chapters') return evidencePack.value.chapter_map?.chapters?.length || 0
  if (mapId === 'characters') return evidencePack.value.character_map?.characters?.length || 0
  if (mapId === 'claims') return evidencePack.value.claim_map?.claims?.length || 0
  if (mapId === 'risks') return evidencePack.value.risk_map?.risks?.length || 0
  return 0
}

function getMapSummary(mapId) {
  if (!evidencePack.value) return 'Pending extraction...'
  
  if (mapId === 'dna') {
    const dna = evidencePack.value.book_dna
    return dna?.spoilers_safe_summary || dna?.premise 
      ? truncateText(dna.spoilers_safe_summary || dna.premise, 110) 
      : 'Extracted title, subgenres, tone and outline indicators.'
  }
  if (mapId === 'market') {
    const mkt = evidencePack.value.market_surface
    return mkt?.positioning_summary 
      ? truncateText(mkt.positioning_summary, 110) 
      : 'Packaging guidelines and discoverability hook notes.'
  }
  if (mapId === 'chapters') {
    const count = evidencePack.value.chapter_map?.chapters?.length || 0
    const pacing = evidencePack.value.chapter_map?.pacing_profile || 'normal'
    return count > 0 
      ? `${count} chapters segmented. Pacing style resolves to "${pacing}".` 
      : 'No chapters parsed.'
  }
  if (mapId === 'characters') {
    const count = evidencePack.value.character_map?.characters?.length || 0
    return count > 0 
      ? `${count} story character profiles and relationship links mapped.` 
      : 'No character records detected. Primarily maps for fiction.'
  }
  if (mapId === 'claims') {
    const count = evidencePack.value.claim_map?.claims?.length || 0
    return count > 0 
      ? `${count} core claims with supporting assertions detected.` 
      : 'No nonfiction claims identified. Primarily maps for nonfiction.'
  }
  if (mapId === 'risks') {
    const count = evidencePack.value.risk_map?.risks?.length || 0
    const summary = evidencePack.value.risk_map?.risk_summary
    if (count > 0) {
      return truncateText(`${count} issues flagged. ${summary || ''}`, 110)
    }
    return 'No pacing, ideological, or factual risks flagged.'
  }
  if (mapId === 'style') {
    const st = evidencePack.value.style_map
    if (!st) return 'Clarity and rhythm indexes.'
    return `Density: ${st.prose_density || 'medium'}. Clarity: ${st.clarity || 'medium'}. Rhythm: ${st.rhythm || 'regular'}.`
  }
  return 'Ready'
}

function getMapRawData(mapId) {
  if (!evidencePack.value) return null
  const mapField = maps.find(m => m.id === mapId)?.field
  return evidencePack.value[mapField] || null
}

function openDetails(mapId) {
  activeMapId.value = mapId
  isDrawerOpen.value = true
}

function closeDrawer() {
  isDrawerOpen.value = false
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
    alert(`Editorial corrections saved for ${maps.find(m => m.id === mapId).label}! These custom notes will guide simulated reader reactions.`)
  }
}

async function regenerateMap(mapId) {
  if (!session.value.manuscript?.text) {
    error.value = 'Manuscript text is missing from session. Cannot regenerate map analysis.'
    return
  }
  
  loadingMessage.value = `Regenerating ${maps.find(m => m.id === mapId).label} mapping details...`
  error.value = ''
  cardStates[mapId].status = 'regenerating'
  
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
    cardStates[mapId].status = 'generated'
  } finally {
    loadingMessage.value = ''
  }
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

// Drawer Escape Key Listener
const handleKeydown = (e) => {
  if (e.key === 'Escape' && isDrawerOpen.value) {
    closeDrawer()
  }
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
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.evidence-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--sb-space-4);
  position: relative;
}

/* Empty State */
.empty-evidence-card {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-xl);
  padding: var(--sb-space-12);
  text-align: center;
  max-width: 500px;
  margin: var(--sb-space-10) auto;
  box-shadow: var(--sb-shadow-sm);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--sb-space-4);
}

.empty-evidence-card h2 {
  font-size: var(--sb-text-lg);
  margin: 0 0 var(--sb-space-2) 0;
  color: var(--sb-text-heading);
}

.empty-evidence-card p {
  font-size: var(--sb-text-base);
  color: var(--sb-text-muted);
  margin: 0 0 var(--sb-space-6) 0;
  line-height: var(--sb-leading-relaxed);
}

.action-row-center {
  display: flex;
  justify-content: center;
}

/* Dashboard Flow */
.evidence-dashboard-flow {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-6);
  margin-bottom: var(--sb-space-8);
}

/* Review Status Strip */
.review-status-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--sb-space-6);
  padding: var(--sb-space-5) var(--sb-space-6);
  background: var(--sb-bg-card);
}

.progress-info h3 {
  font-size: var(--sb-text-base);
  font-weight: var(--sb-weight-bold);
  margin: 0 0 var(--sb-space-1) 0;
  color: var(--sb-text-heading);
}

.progress-info p {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-muted);
  margin: 0;
}

.progress-bar-container {
  flex: 1;
  max-width: 400px;
}

.progress-bar-track {
  height: 8px;
  background: var(--sb-surface-secondary);
  border-radius: var(--sb-radius-full);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--sb-color-ready);
  border-radius: var(--sb-radius-full);
  transition: width 0.3s ease;
}

/* Critical Warning Banner */
.unreviewed-warning-banner {
  display: flex;
  align-items: flex-start;
  gap: var(--sb-space-4);
  background: var(--sb-status-warn-bg);
  border: 1px solid var(--sb-color-mixed);
  border-radius: var(--sb-radius-lg);
  padding: var(--sb-space-4) var(--sb-space-5);
}

.warning-icon {
  font-size: 1.25rem;
  line-height: 1.2;
}

.warning-text {
  font-size: var(--sb-text-sm);
  color: var(--sb-status-warn-text);
  line-height: var(--sb-leading-normal);
}

.critical-pack-list {
  font-weight: var(--sb-weight-bold);
  text-decoration: underline;
}

/* Cards Grid */
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--sb-space-5);
}

.map-card-item {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-xl);
  padding: var(--sb-space-5);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  position: relative;
  overflow: hidden;
}

.map-card-item:hover,
.map-card-item:focus-visible {
  border-color: var(--sb-color-brand);
  box-shadow: var(--sb-shadow-md);
  transform: translateY(-2px);
}

.map-card-item:focus-visible {
  outline: var(--sb-focus-ring);
  outline-offset: var(--sb-focus-offset);
}

.map-card-item.active {
  border-color: var(--sb-color-brand);
  background: #fffbf9;
  box-shadow: 0 0 0 1px var(--sb-color-brand), var(--sb-shadow-md);
}

.map-card-item.accepted {
  border-left: 5px solid var(--sb-color-ready);
}

.map-card-item.needs-review {
  border-left: 5px solid var(--sb-color-mixed);
}

.map-card-item.is-critical:not(.accepted) {
  border-right: 3px dashed var(--sb-color-mixed);
}

.card-top-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--sb-space-2);
  margin-bottom: var(--sb-space-3);
}

.title-with-icon {
  display: flex;
  gap: var(--sb-space-3);
  align-items: center;
}

.card-icon {
  font-size: 1.6rem;
  line-height: 1;
}

.label-box {
  display: flex;
  flex-direction: column;
}

.label-box h3 {
  font-size: var(--sb-text-md);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0;
}

.critical-indicator {
  font-size: 0.65rem;
  color: var(--sb-text-muted);
  font-weight: var(--sb-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-top: 1px;
}

.card-summary {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-body);
  line-height: var(--sb-leading-normal);
  margin: 0 0 var(--sb-space-4) 0;
  flex: 1;
}

/* Confidence Row inside Card */
.card-confidence-row {
  margin-bottom: var(--sb-space-3);
}

.confidence-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  margin-bottom: var(--sb-space-1);
}

.confidence-val {
  font-weight: var(--sb-weight-semibold);
}

.low-confidence-tag {
  color: var(--sb-risk-high);
  font-weight: var(--sb-weight-bold);
  text-transform: uppercase;
  font-size: 0.65rem;
  background: var(--sb-risk-high-bg);
  padding: 1px 4px;
  border-radius: var(--sb-radius-xs);
}

.confidence-bar-track {
  height: 5px;
  background: var(--sb-surface-secondary);
  border-radius: var(--sb-radius-full);
  overflow: hidden;
}

.confidence-bar-fill {
  height: 100%;
  background: var(--sb-color-info);
  border-radius: var(--sb-radius-full);
}

.confidence-bar-fill.low-confidence {
  background: var(--sb-risk-high);
}

.card-refs-row {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  margin-bottom: var(--sb-space-4);
}

/* Card Actions Footer Ribbon */
.card-actions-row {
  border-top: 1px solid var(--sb-border-color);
  padding-top: var(--sb-space-3);
  display: flex;
  justify-content: space-between;
  gap: var(--sb-space-2);
}

.card-btn-ghost {
  background: transparent;
  border: none;
  font-family: var(--sb-font-sans);
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-bold);
  cursor: pointer;
  padding: var(--sb-space-1) var(--sb-space-2);
  border-radius: var(--sb-radius-sm);
  transition: all 0.2s;
  outline: none;
}

.card-btn-ghost.view-details {
  color: var(--sb-color-brand);
}

.card-btn-ghost.view-details:hover {
  background: var(--sb-color-brand-light);
}

.card-btn-ghost.regenerate {
  color: var(--sb-text-muted);
}

.card-btn-ghost.regenerate:hover:not(:disabled) {
  background: var(--sb-surface-secondary);
}

.card-btn-ghost.accept {
  color: var(--sb-color-ready);
}

.card-btn-ghost.accept:hover:not(:disabled) {
  background: var(--sb-risk-low-bg);
}

.card-btn-ghost:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.card-btn-ghost:focus-visible {
  outline: 2px solid currentColor;
}

/* Drawer Backdrop Overlay */
.drawer-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(2px);
  z-index: 999;
}

/* Sliding Detail Drawer */
.detail-drawer {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: 520px;
  max-width: 90vw;
  background: var(--sb-bg-card);
  border-left: 1px solid var(--sb-border-color);
  box-shadow: var(--sb-shadow-lg);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateX(100%);
  outline: none;
}

.detail-drawer.is-open {
  transform: translateX(0);
}

.drawer-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.drawer-header {
  padding: var(--sb-space-5) var(--sb-space-6);
  border-bottom: 1px solid var(--sb-border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--sb-bg-card);
}

.drawer-header-left {
  display: flex;
  gap: var(--sb-space-4);
  align-items: center;
}

.drawer-icon {
  font-size: 2.2rem;
  line-height: 1;
}

.drawer-header h2 {
  font-size: var(--sb-text-lg);
  font-weight: var(--sb-weight-extrabold);
  color: var(--sb-text-heading);
  margin: 0 0 var(--sb-space-1) 0;
}

.drawer-badges {
  display: flex;
  gap: var(--sb-space-3);
  align-items: center;
}

.confidence-badge {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  font-weight: var(--sb-weight-semibold);
}

.confidence-badge.low-confidence-text {
  color: var(--sb-risk-high);
  font-weight: var(--sb-weight-bold);
}

.close-btn {
  background: transparent;
  border: none;
  font-size: var(--sb-text-lg);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-hint);
  cursor: pointer;
  padding: var(--sb-space-2);
  border-radius: var(--sb-radius-full);
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.close-btn:hover {
  background: var(--sb-surface-secondary);
  color: var(--sb-text-main);
}

/* Drawer Content */
.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--sb-space-6);
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-6);
}

.drawer-section {
  border-bottom: 1px solid var(--sb-border-color);
  padding-bottom: var(--sb-space-5);
}

.drawer-section:last-of-type {
  border-bottom: none;
}

.drawer-section h3 {
  font-size: var(--sb-text-base);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0 0 var(--sb-space-4) 0;
}

.section-hint {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-hint);
  margin: 0 0 var(--sb-space-3) 0;
}

/* Importance Card Callout */
.importance-card {
  background: #faf5ff;
  border: 1px solid #f3e8ff;
  border-left: 4px solid #a855f7;
  border-radius: var(--sb-radius-md);
  padding: var(--sb-space-4) var(--sb-space-5);
  margin-bottom: 0;
}

.importance-card strong {
  display: block;
  font-size: var(--sb-text-sm);
  color: #6b21a8;
  margin-bottom: var(--sb-space-1);
}

.importance-card p {
  font-size: var(--sb-text-sm);
  color: #581c87;
  margin: 0;
  line-height: var(--sb-leading-relaxed);
}

/* Structured View */
.structured-view {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-4);
}

.structured-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--sb-border-color);
  padding-bottom: var(--sb-space-2);
  gap: var(--sb-space-4);
}

.structured-row:last-child {
  border-bottom: none;
}

.structured-label {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-muted);
  font-weight: var(--sb-weight-semibold);
}

.structured-value {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-main);
  font-weight: var(--sb-weight-bold);
  text-align: right;
}

.drawer-sub-block {
  margin-top: var(--sb-space-4);
}

.drawer-sub-block h4 {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0 0 var(--sb-space-2) 0;
}

.drawer-sub-block ul {
  list-style: square;
  padding-left: var(--sb-space-5);
  font-size: var(--sb-text-sm);
  color: var(--sb-text-body);
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sb-space-2);
}

.theme-tag {
  font-family: var(--sb-font-mono);
  background: var(--sb-surface-secondary);
  color: var(--sb-text-muted);
  font-size: var(--sb-text-xs);
  padding: var(--sb-space-1) var(--sb-space-2);
  border-radius: var(--sb-radius-sm);
  font-weight: var(--sb-weight-semibold);
}

.comp-tag {
  background: var(--sb-status-info-bg);
  color: var(--sb-status-info-text);
  font-size: var(--sb-text-xs);
  padding: var(--sb-space-1) var(--sb-space-3);
  border-radius: var(--sb-radius-full);
  font-weight: var(--sb-weight-semibold);
}

.hook-tag {
  background: #fdf2f8;
  color: #9d174d;
  font-size: var(--sb-text-xs);
  padding: var(--sb-space-1) var(--sb-space-3);
  border-radius: var(--sb-radius-full);
  font-weight: var(--sb-weight-semibold);
}

.premise-quote-block blockquote {
  margin: 0;
  padding-left: var(--sb-space-4);
  border-left: 3px solid var(--sb-border-hover);
  font-style: italic;
  font-size: var(--sb-text-sm);
  color: var(--sb-text-body);
  line-height: var(--sb-leading-relaxed);
}

.warning-callout-block {
  background: var(--sb-status-warn-bg);
  border: 1px solid var(--sb-color-mixed);
  border-radius: var(--sb-radius-md);
  padding: var(--sb-space-3) var(--sb-space-4);
}

.warning-callout-block h4 {
  color: var(--sb-status-warn-text);
  margin-bottom: var(--sb-space-1);
}

.warning-callout-block p {
  font-size: var(--sb-text-sm);
  color: var(--sb-status-warn-text);
  margin: 0;
  line-height: var(--sb-leading-normal);
}

.no-data-note {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-hint);
  font-style: italic;
}

/* Chapter Timeline details */
.timeline-accordion {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.timeline-ch-details {
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-md);
  overflow: hidden;
  background: var(--sb-bg-card);
}

.timeline-ch-summary {
  display: flex;
  align-items: center;
  gap: var(--sb-space-3);
  padding: var(--sb-space-3) var(--sb-space-4);
  cursor: pointer;
  user-select: none;
  font-size: var(--sb-text-sm);
}

.timeline-ch-summary:hover {
  background: var(--sb-surface-secondary);
}

.timeline-ch-summary::-webkit-details-marker {
  display: none;
}

.ch-num {
  font-family: var(--sb-font-mono);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-color-brand);
}

.ch-title {
  flex: 1;
  color: var(--sb-text-heading);
}

.ch-pacing-badge {
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  text-transform: uppercase;
  padding: 1px 5px;
  border-radius: var(--sb-radius-sm);
}

.ch-pacing-badge.fast { background: #fee2e2; color: #b91c1c; }
.ch-pacing-badge.slow { background: #eff6ff; color: #1d4ed8; }
.ch-pacing-badge.medium,
.ch-pacing-badge.normal { background: var(--sb-status-ok-bg); color: var(--sb-status-ok-text); }

.ch-details-expanded {
  padding: var(--sb-space-4);
  border-top: 1px solid var(--sb-border-color);
  background: var(--sb-surface-primary);
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-3);
}

.ch-desc {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-body);
  line-height: var(--sb-leading-relaxed);
  margin: 0;
}

.ch-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sb-space-4);
  font-size: var(--sb-text-xs);
  border-bottom: 1px dashed var(--sb-border-color);
  padding-bottom: var(--sb-space-3);
}

.ch-meta-grid strong {
  color: var(--sb-text-heading);
  display: block;
  margin-bottom: 2px;
}

.ch-meta-grid p {
  margin: 0;
  color: var(--sb-text-muted);
}

.ch-list-sec {
  font-size: var(--sb-text-xs);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ch-list-sec strong {
  color: var(--sb-text-heading);
}

.ch-list-sec ul {
  list-style: square;
  margin: 0;
  padding-left: var(--sb-space-4);
  color: var(--sb-text-muted);
}

.ch-list-sec.warning strong {
  color: var(--sb-status-error-text);
}

.ch-list-sec.warning ul {
  color: var(--sb-status-error-text);
}

/* Character Details */
.character-details-card-list,
.claim-details-card-list,
.risk-details-card-list {
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-4);
}

.character-details-card,
.claim-details-card,
.risk-details-card {
  border: 1px solid var(--sb-border-color);
  background: var(--sb-surface-primary);
  border-radius: var(--sb-radius-lg);
  padding: var(--sb-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
}

.char-details-hdr,
.risk-details-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--sb-space-2);
}

.char-details-hdr h4 {
  font-size: var(--sb-text-base);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0;
}

.char-arc {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-body);
  margin: 0;
}

.char-attributes {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.char-attributes strong {
  color: var(--sb-text-heading);
}

.rel-tag {
  display: inline-block;
  background: var(--sb-surface-secondary);
  padding: 1px 4px;
  border-radius: var(--sb-radius-xs);
  margin-right: 4px;
}

.char-friction-warning {
  margin-top: var(--sb-space-2);
  border-top: 1px dashed var(--sb-border-color);
  padding-top: var(--sb-space-2);
  font-size: var(--sb-text-xs);
  color: var(--sb-status-warn-text);
}

.char-friction-warning ul {
  margin: 2px 0 0 0;
  padding-left: var(--sb-space-4);
}

/* Claim Details Cards */
.claim-quote {
  font-size: var(--sb-text-sm);
  font-weight: var(--sb-weight-semibold);
  font-style: italic;
  color: var(--sb-text-heading);
  margin: 0;
}

.claim-support-info {
  display: flex;
  gap: var(--sb-space-6);
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  border-bottom: 1px dashed var(--sb-border-color);
  padding-bottom: var(--sb-space-2);
}

.support-field strong.strong { color: var(--sb-color-ready); }
.support-field strong.medium { color: var(--sb-color-mixed); }
.support-field strong.weak { color: var(--sb-risk-high); }

.claim-details-sub {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
}

.claim-details-sub strong {
  color: var(--sb-text-heading);
  display: block;
  margin-bottom: 2px;
}

.claim-details-sub ul {
  margin: 0;
  padding-left: var(--sb-space-4);
}

/* Risk details */
.severity-badge {
  font-size: 0.65rem;
  font-weight: var(--sb-weight-bold);
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: var(--sb-radius-sm);
  color: #ffffff;
}

.severity-badge.high { background: var(--sb-risk-high); }
.severity-badge.medium { background: var(--sb-risk-medium); }
.severity-badge.low { background: var(--sb-color-ready); }

.risk-desc {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-body);
  margin: 0;
}

.risk-trigger {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  margin: 0;
}

.risk-mitigation {
  background: var(--sb-bg-card);
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-md);
  padding: var(--sb-space-3);
  font-size: var(--sb-text-xs);
  color: var(--sb-text-body);
  margin-top: var(--sb-space-2);
}

.risk-mitigation strong {
  color: var(--sb-status-error-text);
  display: block;
  margin-bottom: 2px;
}

.risk-mitigation p {
  margin: 0;
}

/* Source references */
.source-refs-list {
  list-style: square;
  padding-left: var(--sb-space-5);
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-2);
}

.source-refs-list code {
  background: var(--sb-surface-secondary);
  padding: 2px 6px;
  border-radius: var(--sb-radius-sm);
}

/* Corrections Textarea */
.corrections-section textarea {
  min-height: 80px;
}

.corrections-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--sb-space-3);
}

.corrections-actions button.sm {
  min-height: 36px;
  padding: var(--sb-space-1) var(--sb-space-4);
  font-size: var(--sb-text-xs);
}

/* Advanced JSON details */
.json-details {
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-md);
  background: var(--sb-surface-primary);
  overflow: hidden;
}

.json-summary {
  padding: var(--sb-space-3) var(--sb-space-4);
  cursor: pointer;
  font-size: var(--sb-text-xs);
  font-weight: var(--sb-weight-semibold);
  color: var(--sb-text-muted);
  user-select: none;
}

.json-summary:hover {
  background: var(--sb-surface-secondary);
}

.json-content {
  padding: var(--sb-space-4);
  border-top: 1px solid var(--sb-border-color);
  background: var(--sb-surface-dark);
}

.raw-json-code {
  font-family: var(--sb-font-mono);
  font-size: var(--sb-text-xs);
  color: #38bdf8; /* cyan */
  white-space: pre-wrap;
  word-break: break-all;
}

/* Drawer Footer */
.drawer-footer {
  padding: var(--sb-space-4) var(--sb-space-6);
  border-top: 1px solid var(--sb-border-color);
  background: var(--sb-surface-primary);
  display: flex;
  justify-content: flex-end;
  gap: var(--sb-space-3);
}

.drawer-footer button {
  min-height: 40px;
  font-size: var(--sb-text-xs);
}

.drawer-footer button.flag-needs-review {
  border-color: var(--sb-color-mixed);
  color: var(--sb-status-warn-text);
}

.drawer-footer button.flag-needs-review:hover:not(:disabled) {
  background: var(--sb-status-warn-bg);
}

.drawer-footer button.accept-lock {
  background: var(--sb-color-ready);
  border-color: var(--sb-color-ready);
  color: #ffffff;
}

.drawer-footer button.accept-lock:hover:not(:disabled) {
  background: #059669;
}

/* Global Footer Actions */
.global-actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--sb-border-color);
  padding-top: var(--sb-space-6);
  margin-top: var(--sb-space-6);
}

.proceed-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--sb-space-2);
}

.proceed-hint-label {
  font-size: var(--sb-text-xs);
  color: var(--sb-status-error-text);
  font-weight: var(--sb-weight-semibold);
}

@media (max-width: 640px) {
  .review-status-strip {
    flex-direction: column;
    align-items: flex-start;
  }
  .progress-bar-container {
    width: 100%;
    max-width: none;
  }
  .evidence-grid {
    grid-template-columns: 1fr;
  }
  .global-actions-bar {
    flex-direction: column;
    gap: var(--sb-space-4);
    align-items: stretch;
  }
  .proceed-wrapper {
    align-items: stretch;
  }
}
</style>
