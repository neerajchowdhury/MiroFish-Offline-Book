<template>
  <SwarmbookAppShell
    active-route="SwarmbookUpload"
    :project-id="session.projectId"
    title="New Simulation Setup"
    subtitle="Six steps to predict reader reactions for your manuscript."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="wizard-container">

      <!-- ================================================================
           PROGRESS STEPPER RIBBON
      ================================================================= -->
      <nav class="wizard-stepper" aria-label="Setup progress">
        <div
          v-for="step in steps"
          :key="step.num"
          class="stepper-item"
          :class="{
            active: currentStep === step.num,
            completed: currentStep > step.num,
            disabled: currentStep < step.num && !canJumpTo(step.num)
          }"
          @click="jumpToStep(step.num)"
          role="button"
          :tabindex="canJumpTo(step.num) ? 0 : -1"
          :aria-current="currentStep === step.num ? 'step' : undefined"
          @keydown.enter="jumpToStep(step.num)"
          @keydown.space.prevent="jumpToStep(step.num)"
        >
          <span class="step-num-circle" :aria-hidden="true">
            <span v-if="currentStep > step.num">✓</span>
            <span v-else>{{ step.num }}</span>
          </span>
          <span class="step-lbl">{{ step.label }}</span>
          <span class="chevron" v-if="step.num < steps.length" aria-hidden="true">›</span>
        </div>
      </nav>

      <!-- ================================================================
           WIZARD CARD
      ================================================================= -->
      <div class="wizard-card">

        <!-- Validation error banner -->
        <div v-if="validationErrors.length" class="validation-alert" role="alert" aria-live="polite">
          <span class="alert-hdr">Please fix the following before continuing</span>
          <ul>
            <li v-for="err in validationErrors" :key="err">{{ err }}</li>
          </ul>
        </div>

        <!-- ============================================================
             STEP 1: PROJECT BASICS
             Question: What are we testing?
        ============================================================= -->
        <section v-if="currentStep === 1" class="wizard-step-section" aria-labelledby="step1-heading">
          <div class="step-question-header">
            <span class="step-eyebrow">Step 1 of 6</span>
            <h2 id="step1-heading">What are we testing?</h2>
            <p class="step-hint">Give this project a name and tell us what kind of content you're submitting for simulation.</p>
          </div>

          <div class="step1-layout">
            <div class="form-fields-col">
              <div class="form-grid">
                <label class="field-group">
                  <span class="label-text">Content Type <span class="req">*</span></span>
                  <select v-model="form.contentType" id="s1-contentType" aria-required="true">
                    <option value="full_manuscript">Full manuscript</option>
                    <option value="novel">Novel</option>
                    <option value="novella">Novella</option>
                    <option value="short_story">Short story</option>
                    <option value="article_essay">Article / Essay</option>
                    <option value="newsletter">Newsletter</option>
                    <option value="book_proposal">Book proposal</option>
                    <option value="blurb_synopsis">Blurb / Synopsis</option>
                    <option value="chapter_sample">Chapter sample</option>
                    <option value="research_pack">Research / Evidence pack</option>
                  </select>
                  <span class="microcopy">Select the format of the draft content you are testing.</span>
                </label>

                <label class="field-group">
                  <span class="label-text">Book Classification <span class="req">*</span></span>
                  <select v-model="form.bookType" id="s1-bookType" aria-required="true">
                    <option value="fiction">Fiction</option>
                    <option value="non-fiction">Non-Fiction</option>
                    <option value="mixed">Mixed Structure</option>
                  </select>
                  <span class="microcopy">Fiction evaluates narrative friction; Non-Fiction audits claim support.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.title }">
                  <span class="label-text">Content Title <span class="req">*</span></span>
                  <input
                    v-model="form.title"
                    type="text"
                    id="s1-title"
                    placeholder="e.g. The Quiet Passenger"
                    aria-required="true"
                    @input="clearValidationError('title')"
                  />
                  <span class="microcopy">Official title of the manuscript draft.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.authorName }">
                  <span class="label-text">Author <span class="req">*</span></span>
                  <input
                    v-model="form.authorName"
                    type="text"
                    id="s1-author"
                    placeholder="e.g. Jane Doe"
                    aria-required="true"
                    @input="clearValidationError('authorName')"
                  />
                  <span class="microcopy">Author name or pen name.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.genre }">
                  <span class="label-text">Genre / Category <span class="req">*</span></span>
                  <input
                    v-model="form.genre"
                    type="text"
                    id="s1-genre"
                    placeholder="e.g. Speculative Thriller"
                    aria-required="true"
                    @input="clearValidationError('genre')"
                  />
                  <span class="microcopy">Aids in targeting appropriate platform reviewers.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.projectName }">
                  <span class="label-text">Project Reference Name <span class="req">*</span></span>
                  <input
                    v-model="form.projectName"
                    type="text"
                    id="s1-project"
                    placeholder="e.g. spring_thriller_draft"
                    aria-required="true"
                    @input="clearValidationError('projectName')"
                  />
                  <span class="microcopy">Internal project directory name. Use lowercase, numbers, or underscores.</span>
                </label>
              </div>
            </div>

            <!-- Right: Fidelity checker -->
            <aside class="checklist-col" aria-label="Simulation fidelity rating">
              <div class="sb-card accuracy-card">
                <h3>Simulation Fidelity</h3>
                <p class="checklist-hint">Live assessment of setup accuracy impact:</p>
                <ul class="accuracy-list-stack">
                  <li class="accuracy-item-row">
                    <span class="status-indicator-badge" aria-hidden="true">{{ accuracyChecks.contentType.icon }}</span>
                    <div>
                      <strong>Format Depth: {{ accuracyChecks.contentType.label }}</strong>
                      <span>{{ accuracyChecks.contentType.desc }}</span>
                    </div>
                  </li>
                  <li class="accuracy-item-row">
                    <span class="status-indicator-badge" aria-hidden="true">{{ accuracyChecks.metaCompleteness.icon }}</span>
                    <div>
                      <strong>Synopsis Detail: {{ accuracyChecks.metaCompleteness.label }}</strong>
                      <span>{{ accuracyChecks.metaCompleteness.desc }}</span>
                    </div>
                  </li>
                  <li class="accuracy-item-row">
                    <span class="status-indicator-badge" aria-hidden="true">{{ accuracyChecks.profileAccuracy.icon }}</span>
                    <div>
                      <strong>Cohort Resolution: {{ accuracyChecks.profileAccuracy.label }}</strong>
                      <span>{{ accuracyChecks.profileAccuracy.desc }}</span>
                    </div>
                  </li>
                  <li class="accuracy-item-row">
                    <span class="status-indicator-badge" aria-hidden="true">{{ accuracyChecks.privacyAccuracy.icon }}</span>
                    <div>
                      <strong>Cognitive Reasoning: {{ accuracyChecks.privacyAccuracy.label }}</strong>
                      <span>{{ accuracyChecks.privacyAccuracy.desc }}</span>
                    </div>
                  </li>
                </ul>
                <div class="score-progress-box">
                  <div class="score-label-row">
                    <span class="fidelity-score-label">Fidelity Score</span>
                    <strong :style="{ color: accuracyChecks.scoreColor }">{{ accuracyChecks.scoreLabel }} ({{ accuracyChecks.score }}%)</strong>
                  </div>
                  <div class="fidelity-bar-rail">
                    <div class="fidelity-bar-fill" :style="{ width: accuracyChecks.score + '%', background: accuracyChecks.scoreColor }"></div>
                  </div>
                </div>
              </div>
            </aside>
          </div>

          <div class="what-next-helper">
            <span class="what-next-icon" aria-hidden="true">→</span>
            <span><strong>What happens next:</strong> You'll upload the manuscript file or paste content. No analysis runs yet.</span>
          </div>
        </section>

        <!-- ============================================================
             STEP 2: UPLOAD CONTENT
             Question: What should the system read?
        ============================================================= -->
        <section v-if="currentStep === 2" class="wizard-step-section" aria-labelledby="step2-heading">
          <div class="step-question-header">
            <span class="step-eyebrow">Step 2 of 6</span>
            <h2 id="step2-heading">What should the system read?</h2>
            <p class="step-hint">Upload your manuscript or paste the draft content. The system will extract text and detect structure — no simulation runs yet.</p>
          </div>

          <!-- Upload error -->
          <div v-if="uploadError" class="validation-alert" role="alert" aria-live="polite">
            <span class="alert-hdr">Upload Error</span>
            <p>{{ uploadError }}</p>
            <button class="clear-err-btn" @click="uploadError = ''" aria-label="Dismiss error">×</button>
          </div>

          <!-- Accepted formats info strip -->
          <div class="upload-info-strip">
            <span class="strip-item">📄 PDF</span>
            <span class="strip-item">📝 DOCX</span>
            <span class="strip-item">🗒️ TXT</span>
            <span class="strip-item">⬇️ MD</span>
            <span class="strip-divider">|</span>
            <span class="strip-item limit-info">Max 40 MB</span>
            <span class="strip-divider">|</span>
            <span class="strip-item privacy-note">🔒 {{ form.privacyMode }} — {{ form.privacyMode === 'local_only' ? 'Strictly offline' : form.privacyMode === 'hybrid_safe' ? 'Local analysis only' : 'Cloud reasoning active' }}</span>
          </div>

          <!-- Drop zone -->
          <div
            class="wizard-upload-zone"
            :class="{ 'is-dragover': dragOver, 'has-file': form.manuscriptFilename }"
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="onFileDrop"
            @click="triggerFileBrowser"
            @keydown.enter="triggerFileBrowser"
            @keydown.space.prevent="triggerFileBrowser"
            role="button"
            tabindex="0"
            aria-label="Drag and drop manuscript file here, or click to browse local files"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".txt,.md,.markdown,.pdf,.docx"
              class="hidden-input"
              @change="onFileSelect"
            />

            <div class="drop-zone-content" v-if="!form.manuscriptFilename">
              <span class="upload-icon" aria-hidden="true">📂</span>
              <h3>Drag &amp; drop manuscript here</h3>
              <p class="browse-link">or click to browse local folders</p>
              <span class="formats-label">PDF · DOCX · TXT · MD</span>
            </div>

            <div class="selected-file-display" v-else>
              <span class="file-icon" aria-hidden="true">📄</span>
              <div class="file-details">
                <h3>{{ form.manuscriptFilename }}</h3>
                <p class="file-meta">
                  <span class="meta-tag">{{ formatBytes(form.manuscriptSizeBytes) }}</span>
                  <span class="meta-tag" v-if="form.manuscriptMimeType">{{ form.manuscriptMimeType }}</span>
                  <span class="meta-tag word-badge" v-if="form.manuscriptWordCount">{{ form.manuscriptWordCount.toLocaleString() }} words</span>
                  <span class="meta-tag section-badge" v-if="form.sectionCount">{{ form.sectionCount }} sections detected</span>
                </p>
              </div>
              <button class="remove-btn" @click.stop="clearFile" aria-label="Remove uploaded file">✕ Remove</button>
            </div>
          </div>

          <!-- File metadata (shown after upload) -->
          <div class="file-meta-panel" v-if="form.manuscriptFilename">
            <div class="meta-col">
              <span class="meta-label">⏱ Processing Time</span>
              <span class="meta-value">~30–60 seconds on local hardware</span>
            </div>
            <div class="meta-col">
              <span class="meta-label">🔒 Privacy Mode</span>
              <span class="meta-value" :class="'privacy-badge-' + form.privacyMode">{{ form.privacyMode }}</span>
            </div>
          </div>

          <!-- Paste collapse -->
          <div class="paste-collapse-container">
            <button
              type="button"
              class="collapse-trigger-btn"
              @click="showPasteArea = !showPasteArea"
              :aria-expanded="showPasteArea"
              aria-controls="wizard-paste-textarea"
            >
              {{ showPasteArea ? '▼ Hide Manual Paste Option' : '▶ Or paste manuscript content manually' }}
            </button>

            <div id="wizard-paste-textarea" v-show="showPasteArea" class="paste-textarea-wrapper">
              <label class="field-group textarea-group" :class="{ 'has-error': activeValidationFields.manuscriptText }">
                <span class="label-text">Paste Draft Text Content</span>
                <textarea
                  v-model="form.manuscriptText"
                  rows="10"
                  placeholder="Paste raw manuscript chapters here..."
                  @input="onPasteInput"
                ></textarea>
              </label>
              <div class="char-count-row">
                <span :class="{ 'warn-text': isManuscriptTooLarge }">
                  {{ form.manuscriptText.length.toLocaleString() }} characters
                </span>
                <span v-if="isManuscriptTooLarge" class="limit-warning">
                  ⚠️ Very large — consider an excerpt of 1–3 chapters for faster local processing.
                </span>
              </div>
            </div>
          </div>

          <div class="what-next-helper">
            <span class="what-next-icon" aria-hidden="true">→</span>
            <span><strong>What happens next:</strong> The system extracts text, detects chapter structure, and prepares evidence packs. This takes 30–60 seconds. Simulation does <em>not</em> run yet.</span>
          </div>
        </section>

        <!-- ============================================================
             STEP 3: CONTENT INTENT
             Question: Who is this for and what should it achieve?
        ============================================================= -->
        <section v-if="currentStep === 3" class="wizard-step-section" aria-labelledby="step3-heading">
          <div class="step-question-header">
            <span class="step-eyebrow">Step 3 of 6</span>
            <h2 id="step3-heading">Who is this for and what should it achieve?</h2>
            <p class="step-hint">Help the simulation understand your intended reader and what you want tested. This shapes which cohort archetypes are activated.</p>
          </div>

          <div class="intent-layout">
            <div class="intent-fields-col">
              <label class="field-group" :class="{ 'has-error': activeValidationFields.targetReader }">
                <span class="label-text">Target Reader <span class="req">*</span></span>
                <input
                  v-model="form.targetReader"
                  type="text"
                  id="s3-targetReader"
                  placeholder="e.g. Fans of high-concept slow-burn suspense"
                  aria-required="true"
                  @input="clearValidationError('targetReader')"
                />
                <span class="microcopy">Shapes the primary cohort archetypes selected for simulation.</span>
              </label>

              <label class="field-group" :class="{ 'has-error': activeValidationFields.blurb }">
                <span class="label-text">Intended Promise / Jacket Blurb <span class="req">*</span></span>
                <textarea
                  v-model="form.blurb"
                  rows="5"
                  id="s3-blurb"
                  placeholder="Provide the jacket blurb or premise summary that defines what this work promises a reader..."
                  aria-required="true"
                  @input="clearValidationError('blurb')"
                ></textarea>
                <span class="microcopy">The hook promise used to calibrate initial reader expectations. Richer content = higher simulation fidelity.</span>
                <span class="char-hint" :class="{ 'char-hint-warn': form.blurb.length < 100, 'char-hint-ok': form.blurb.length >= 300 }">
                  {{ form.blurb.length }} characters
                  <span v-if="form.blurb.length < 100"> — aim for at least 100</span>
                  <span v-else-if="form.blurb.length < 300"> — rich description (300+) improves reader alignment</span>
                  <span v-else> — ✓ rich synopsis</span>
                </span>
              </label>

              <label class="field-group" :class="{ 'has-error': activeValidationFields.testGoal }">
                <span class="label-text">Test Goal <span class="req">*</span></span>
                <input
                  v-model="form.testGoal"
                  type="text"
                  id="s3-testGoal"
                  placeholder="e.g. Evaluate pacing in Chapter 2 and controversy risks around the ending"
                  aria-required="true"
                  @input="clearValidationError('testGoal')"
                />
                <span class="microcopy">Focuses simulated reader feedback on what you specifically want tested.</span>
              </label>

              <!-- Optional fields -->
              <div class="optional-fields-container">
                <button
                  type="button"
                  class="collapse-trigger-btn"
                  @click="showOptionalBasics = !showOptionalBasics"
                  :aria-expanded="showOptionalBasics"
                >
                  {{ showOptionalBasics ? '▼ Hide Optional Fields' : '▶ Optional: Comp Titles &amp; Market Notes' }}
                </button>

                <div v-show="showOptionalBasics" class="optional-fields-grid">
                  <label class="field-group">
                    <span class="label-text">Comp Titles</span>
                    <input v-model="form.compTitles" type="text" placeholder="e.g. Title A by Author X, Title B" />
                    <span class="microcopy">Comma-separated comparable works to calibrate reader expectations.</span>
                  </label>

                  <label class="field-group">
                    <span class="label-text">Market Positioning Notes</span>
                    <textarea v-model="form.coverBrief" rows="3" placeholder="Describe mood, target shelf, pitch positioning, competitive landscape..."></textarea>
                    <span class="microcopy">Helps genre-positioning and controversy scoring lens calibration.</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Right: blurb quality hint -->
            <aside class="intent-sidebar">
              <div class="sb-card intent-tip-card">
                <h3>📌 Why This Matters</h3>
                <ul class="intent-tip-list">
                  <li><strong>Target Reader</strong> — activates specific cohort archetypes from your reader swarm profile.</li>
                  <li><strong>Blurb</strong> — sets the reader expectation baseline before simulated readers open a single page.</li>
                  <li><strong>Test Goal</strong> — focuses the editor board lenses on your specific editorial question rather than a generic audit.</li>
                </ul>
                <div class="intent-confidence-strip" v-if="form.blurb.length >= 300 && form.targetReader && form.testGoal">
                  <span class="conf-dot ready"></span>
                  Intent context is rich — simulation fidelity is high.
                </div>
                <div class="intent-confidence-strip warn" v-else>
                  <span class="conf-dot warn"></span>
                  Complete all three fields for best results.
                </div>
              </div>
            </aside>
          </div>

          <div class="what-next-helper">
            <span class="what-next-icon" aria-hidden="true">→</span>
            <span><strong>What happens next:</strong> The system builds editorial evidence packs — Book DNA, chapter map, character map, style analysis, and risk flags. This uses your uploaded content and intent context.</span>
          </div>
        </section>

        <!-- ============================================================
             STEP 4: EVIDENCE REVIEW
             Question: Did the system understand your work correctly?
        ============================================================= -->
        <section v-if="currentStep === 4" class="wizard-step-section" aria-labelledby="step4-heading">
          <div class="step-question-header">
            <span class="step-eyebrow">Step 4 of 6</span>
            <h2 id="step4-heading">Did the system understand your work correctly?</h2>
            <p class="step-hint">Review the compiled evidence packs before simulation begins. You can still go back and adjust manuscript content or intent.</p>
          </div>

          <div v-if="evidencePack" class="evidence-review-area">
            <!-- Summary confidence strip -->
            <div class="evidence-summary-strip">
              <div class="es-item">
                <span class="es-label">Book DNA</span>
                <span class="es-status" :class="evidencePack.book_dna ? 'status-ok' : 'status-missing'">
                  {{ evidencePack.book_dna ? '✓ Extracted' : '✕ Missing' }}
                </span>
              </div>
              <div class="es-item">
                <span class="es-label">Chapters</span>
                <span class="es-status" :class="(evidencePack.chapter_map?.chapters?.length || 0) > 0 ? 'status-ok' : 'status-warn'">
                  {{ evidencePack.chapter_map?.chapters?.length || 0 }} detected
                </span>
              </div>
              <div class="es-item">
                <span class="es-label">Characters</span>
                <span class="es-status" :class="(evidencePack.character_map?.characters?.length || 0) > 0 ? 'status-ok' : 'status-warn'">
                  {{ evidencePack.character_map?.characters?.length || 0 }} profiled
                </span>
              </div>
              <div class="es-item">
                <span class="es-label">Risks</span>
                <span class="es-status" :class="(evidencePack.risk_map?.risks?.length || 0) > 0 ? 'status-warn' : 'status-ok'">
                  {{ evidencePack.risk_map?.risks?.length || 0 }} flagged
                </span>
              </div>
              <div class="es-item">
                <span class="es-label">Style</span>
                <span class="es-status" :class="evidencePack.style_map ? 'status-ok' : 'status-missing'">
                  {{ evidencePack.style_map ? '✓ Calibrated' : '✕ Missing' }}
                </span>
              </div>
            </div>

            <!-- Tab viewer -->
            <div class="evidence-tabs">
              <div class="tabs-header" role="tablist" aria-label="Evidence pack maps">
                <button
                  v-for="tab in evidenceTabs"
                  :key="tab.id"
                  class="tab-btn"
                  :class="{ active: activeEvidenceTab === tab.id }"
                  @click="activeEvidenceTab = tab.id"
                  role="tab"
                  :aria-selected="activeEvidenceTab === tab.id"
                  :id="'ev-tab-' + tab.id"
                  :aria-controls="'ev-panel-' + tab.id"
                >
                  {{ tab.label }}
                </button>
              </div>

              <div class="tab-body">
                <div v-if="activeEvidenceTab === 'dna'" role="tabpanel" :id="'ev-panel-dna'" :aria-labelledby="'ev-tab-dna'">
                  <h3>Book DNA</h3>
                  <div class="meta-display">
                    <p><strong>Title:</strong> {{ evidencePack.book_dna?.title || form.title }}</p>
                    <p><strong>Genre:</strong> {{ evidencePack.book_dna?.genre || form.genre }}</p>
                    <p><strong>Target:</strong> {{ evidencePack.book_dna?.target_reader || form.targetReader }}</p>
                    <p><strong>Premise Summary:</strong></p>
                    <blockquote class="premise-quote">{{ evidencePack.book_dna?.premise || form.blurb }}</blockquote>
                  </div>
                </div>

                <div v-if="activeEvidenceTab === 'chapters'" role="tabpanel" :id="'ev-panel-chapters'" :aria-labelledby="'ev-tab-chapters'">
                  <h3>Parsed Chapters</h3>
                  <p class="tab-empty-note" v-if="!(evidencePack.chapter_map?.chapters?.length)">No chapters detected. This is normal for very short content.</p>
                  <ul class="stepper-list">
                    <li v-for="ch in evidencePack.chapter_map?.chapters || []" :key="ch.chapter_id">
                      <strong>Ch {{ ch.chapter_number }}: {{ ch.title || 'Untitled' }}</strong>
                      <p>{{ ch.summary }}</p>
                    </li>
                  </ul>
                </div>

                <div v-if="activeEvidenceTab === 'characters'" role="tabpanel" :id="'ev-panel-characters'" :aria-labelledby="'ev-tab-characters'">
                  <h3>Character Profiles</h3>
                  <p class="tab-empty-note" v-if="!(evidencePack.character_map?.characters?.length)">No characters detected. Expected for non-fiction content.</p>
                  <ul class="stepper-list">
                    <li v-for="char in evidencePack.character_map?.characters || []" :key="char.character_id">
                      <strong>{{ char.name }} ({{ char.role || 'Secondary' }})</strong>
                      <p>Reader frictions: {{ char.reader_friction?.join(', ') || 'None noted' }}</p>
                    </li>
                  </ul>
                </div>

                <div v-if="activeEvidenceTab === 'risks'" role="tabpanel" :id="'ev-panel-risks'" :aria-labelledby="'ev-tab-risks'">
                  <h3>Discovered Narrative Risks</h3>
                  <p class="tab-empty-note" v-if="!(evidencePack.risk_map?.risks?.length)">No specific risks flagged — check the Report for scoring context.</p>
                  <ul class="stepper-list">
                    <li v-for="risk in evidencePack.risk_map?.risks || []" :key="risk.risk_id">
                      <strong class="risk-badge">{{ risk.risk_type }}</strong>
                      <p>{{ risk.description || risk.mitigation_hint }}</p>
                    </li>
                  </ul>
                </div>

                <div v-if="activeEvidenceTab === 'style'" role="tabpanel" :id="'ev-panel-style'" :aria-labelledby="'ev-tab-style'">
                  <h3>Style Calibration</h3>
                  <div class="meta-display">
                    <p><strong>Clarity Rating:</strong> {{ evidencePack.style_map?.clarity ?? 'N/A' }}</p>
                    <p><strong>Narrative Rhythm:</strong> {{ evidencePack.style_map?.rhythm ?? 'N/A' }}</p>
                    <p><strong>Quoteability Index:</strong> {{ evidencePack.style_map?.quoteability ?? 'N/A' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="evidence-actions-row">
              <button type="button" class="ghost-btn small-btn" @click="regenerateEvidence" :disabled="submitting">
                🔄 Regenerate Evidence Packs
              </button>
              <span class="evidence-accept-note">If the maps look correct, click Accept &amp; Configure Simulation below.</span>
            </div>
          </div>

          <div v-else class="empty-state-card">
            <div class="empty-icon" aria-hidden="true">🗂️</div>
            <p>No evidence pack compiled yet. Go back to step 2 or 3 and ensure content is loaded.</p>
          </div>

          <div class="what-next-helper">
            <span class="what-next-icon" aria-hidden="true">→</span>
            <span><strong>What happens next:</strong> You'll choose which reader types and editor lenses should test this. Simulation still has not run.</span>
          </div>
        </section>

        <!-- ============================================================
             STEP 5: SIMULATION SETUP
             Question: Which readers and editors should test this?
        ============================================================= -->
        <section v-if="currentStep === 5" class="wizard-step-section" aria-labelledby="step5-heading">
          <div class="step-question-header">
            <span class="step-eyebrow">Step 5 of 6</span>
            <h2 id="step5-heading">Which readers and editors should test this?</h2>
            <p class="step-hint">Configure your simulated reader swarm — personas, platforms, and model quality. The Development Editor Board runs automatically based on your selections.</p>
          </div>

          <!-- Profile Selection -->
          <div class="field-group">
            <span class="label-text">Simulation Profile</span>
            <div class="profile-cards-grid" role="radiogroup" aria-label="Simulation Profiles">
              <div
                v-for="profile in profileOptions"
                :key="profile.profile_name"
                class="profile-selection-card"
                :class="{ active: form.localProfile === profile.profile_name }"
                @click="form.localProfile = profile.profile_name; onProfileChange()"
                @keydown.enter="form.localProfile = profile.profile_name; onProfileChange()"
                @keydown.space.prevent="form.localProfile = profile.profile_name; onProfileChange()"
                role="radio"
                tabindex="0"
                :aria-checked="form.localProfile === profile.profile_name ? 'true' : 'false'"
              >
                <div class="profile-card-header">
                  <span class="profile-icon" aria-hidden="true">{{ profile.profile_name === 'local_tiny' ? '⚡' : profile.profile_name === 'hybrid_safe_default' ? '⚖️' : '🔮' }}</span>
                  <div class="profile-title-row">
                    <h3>{{ profile.profile_name === 'local_tiny' ? 'Draft Quality (Local Tiny)' : profile.profile_name === 'hybrid_safe_default' ? 'Standard Stress Test (Hybrid)' : 'Deep Analysis (Cloud)' }}</h3>
                    <span v-if="profile.profile_name === 'hybrid_safe_default'" class="recommendation-badge">★ Recommended</span>
                  </div>
                </div>
                <p class="profile-desc">
                  {{ profile.profile_name === 'local_tiny' ? 'Runs fast on local CPU/GPU using tiny model. Best for quick drafts.' : profile.profile_name === 'hybrid_safe_default' ? 'Runs a standard 30-reader cohort using local Ollama. Balanced and recommended.' : 'Deep multi-round simulation using advanced cloud models. May incur API costs.' }}
                </p>
                <div class="profile-meta-chips">
                  <span>👥 Default: {{ profile.max_personas }} readers</span>
                  <span>🌐 Platforms: {{ profile.platforms?.length || 0 }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Reader Count -->
          <div class="field-group">
            <label class="slider-label-row" for="wizard-reader-slider">
              <span class="label-text">Simulated Reader Count</span>
              <strong class="count-indicator">{{ form.personaCount }} readers</strong>
            </label>
            <div class="slider-wrapper">
              <input
                id="wizard-reader-slider"
                v-model.number="form.personaCount"
                type="range"
                min="2"
                max="80"
                class="premium-slider"
                :aria-valuenow="form.personaCount"
                aria-valuemin="2"
                aria-valuemax="80"
              />
              <div class="slider-marks" aria-hidden="true">
                <span>2</span>
                <span>12 (Tiny)</span>
                <span>30 (Standard)</span>
                <span>60 (Deep)</span>
                <span>80</span>
              </div>
            </div>
            <span class="microcopy">Profile default: {{ selectedProfile?.max_personas || 30 }} personas. For 16 GB RAM + Ollama, stay at 12–30.</span>
          </div>

          <!-- Platforms -->
          <div class="field-group">
            <span class="label-text">Simulated Platforms <span class="req">*</span></span>
            <div class="platforms-checkbox-grid" role="group" aria-label="Select simulated platforms">
              <button
                v-for="platform in platformOptionsList"
                :key="platform"
                type="button"
                class="platform-pill-btn"
                :class="{ active: form.platforms.includes(platform) }"
                :aria-pressed="form.platforms.includes(platform)"
                @click="togglePlatformCheckbox(platform)"
              >
                <span class="platform-icon" aria-hidden="true">
                  {{ platform === 'goodreads' ? '📚' : platform === 'booktok' ? '🎵' : platform === 'reddit' ? '👽' : platform === 'bookstagram' ? '📸' : platform === 'x' ? '🐦' : platform === 'newsletter' ? '✉️' : '👥' }}
                </span>
                <span class="platform-name">
                  {{ platform === 'goodreads' ? 'Goodreads' : platform === 'booktok' ? 'BookTok' : platform === 'reddit' ? 'Reddit' : platform === 'bookstagram' ? 'Bookstagram' : platform === 'x' ? 'X (Twitter)' : platform === 'newsletter' ? 'Newsletter' : 'Book Club' }}
                </span>
              </button>
            </div>
          </div>

          <!-- Dev Editor Board toggle -->
          <div class="field-group editor-board-toggle-row">
            <label class="editor-board-toggle" for="editor-board-check">
              <input
                type="checkbox"
                id="editor-board-check"
                v-model="form.editorBoardEnabled"
                class="premium-checkbox"
              />
              <div class="editor-board-label">
                <strong>Enable Development Editor Board</strong>
                <span class="microcopy">Runs 12 archetypal expert lenses (Structural Architect, Cultural Context Editor, DNF Risk Editor, etc.) over the simulation results. Adds ~15 seconds to processing.</span>
              </div>
            </label>
          </div>

          <!-- Advanced settings (collapsed) -->
          <div class="optional-fields-container">
            <button
              type="button"
              class="collapse-trigger-btn"
              @click="showAdvancedSwarm = !showAdvancedSwarm"
              :aria-expanded="showAdvancedSwarm"
            >
              {{ showAdvancedSwarm ? '▼ Hide Advanced Settings' : '▶ Advanced Settings (seed, cohorts, privacy)' }}
            </button>

            <div v-show="showAdvancedSwarm" class="advanced-settings-grid">
              <!-- Reader Cohorts -->
              <div class="field-group">
                <span class="label-text">Active Reader Cohorts</span>
                <div class="cohorts-header-actions">
                  <button type="button" class="action-link-btn" @click="disabledCohorts = []">Select All</button>
                  <span class="bullet-divider">•</span>
                  <button type="button" class="action-link-btn" @click="disabledCohorts = cohortOptions.map(c => c.id)">Clear All</button>
                </div>
                <div class="cohorts-selection-list" role="group" aria-label="Reader cohort selection">
                  <label
                    v-for="cohort in cohortOptions"
                    :key="cohort.id"
                    class="cohort-checkbox-card"
                    :class="{ checked: !disabledCohorts.includes(cohort.id) }"
                  >
                    <input
                      type="checkbox"
                      :checked="!disabledCohorts.includes(cohort.id)"
                      @change="toggleCohortExclusion(cohort.id)"
                      class="premium-checkbox"
                    />
                    <div class="cohort-text-block">
                      <span class="cohort-label">{{ cohort.label }}</span>
                      <p class="cohort-desc">{{ cohort.description }}</p>
                    </div>
                  </label>
                </div>
              </div>

              <!-- Seed + Privacy -->
              <div class="form-grid">
                <label class="field-group">
                  <span class="label-text">Deterministic Seed</span>
                  <input v-model.number="form.simulationSeed" type="number" min="0" class="premium-input text-center" />
                  <span class="microcopy">Same seed = identical cohort reactions across draft iterations.</span>
                </label>

                <div class="field-group">
                  <span class="label-text">Privacy Mode</span>
                  <select v-model="form.privacyMode">
                    <option value="local_only">local_only (strictly offline)</option>
                    <option value="hybrid_safe">hybrid_safe (local + cloud embeddings)</option>
                    <option value="cloud_quality">cloud_quality (advanced cloud reasoning)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Estimated time -->
          <div class="estimate-strip">
            <span class="estimate-label">Estimated run time:</span>
            <strong class="estimate-value">{{ formattedEstimatedTime }}</strong>
            <span class="estimate-hint">({{ form.personaCount }} readers × {{ form.localProfile }} profile)</span>
          </div>

          <!-- System warnings -->
          <div v-if="(customWarnings.length || selectedProfileWarnings.length) && isProfileOrPrivacyChanged" class="alert-banners-stack">
            <div
              v-for="warning in [...selectedProfileWarnings, ...customWarnings]"
              :key="warning.code + warning.message"
              class="setup-warning-banner"
              role="alert"
            >
              <span class="warning-icon" aria-hidden="true">⚠️</span>
              <p class="warning-message">{{ warning.message }}</p>
            </div>
          </div>

          <div class="what-next-helper">
            <span class="what-next-icon" aria-hidden="true">→</span>
            <span><strong>What happens next:</strong> You'll review a complete summary of everything that will run before the simulation starts. Nothing runs until you click Start Simulation.</span>
          </div>
        </section>

        <!-- ============================================================
             STEP 6: REVIEW & RUN
             Question: What will happen now?
        ============================================================= -->
        <section v-if="currentStep === 6" class="wizard-step-section" aria-labelledby="step6-heading">
          <div class="step-question-header">
            <span class="step-eyebrow">Step 6 of 6</span>
            <h2 id="step6-heading">What will happen now?</h2>
            <p class="step-hint">Review every parameter before starting. Once you click Start Simulation, the reader swarm begins reading your manuscript. This cannot be paused.</p>
          </div>

          <div class="run-plan-grid">
            <!-- Content summary -->
            <div class="sb-card run-plan-card">
              <h3>📄 Content</h3>
              <div class="summary-details">
                <div class="row"><span class="lbl">Title</span><span class="val">{{ form.title }}</span></div>
                <div class="row"><span class="lbl">Author</span><span class="val">{{ form.authorName }}</span></div>
                <div class="row"><span class="lbl">Type</span><span class="val">{{ form.contentType?.replace(/_/g, ' ') }}</span></div>
                <div class="row"><span class="lbl">Genre</span><span class="val">{{ form.genre }}</span></div>
                <div class="row"><span class="lbl">Test Goal</span><span class="val">{{ form.testGoal }}</span></div>
              </div>
            </div>

            <!-- Simulation config summary -->
            <div class="sb-card run-plan-card">
              <h3>⚙️ Simulation Configuration</h3>
              <div class="summary-details">
                <div class="row"><span class="lbl">Profile</span><span class="val">{{ form.localProfile }}</span></div>
                <div class="row"><span class="lbl">Privacy Mode</span><span class="val">{{ form.privacyMode }}</span></div>
                <div class="row"><span class="lbl">Reader Count</span><span class="val">{{ form.personaCount }} personas</span></div>
                <div class="row"><span class="lbl">Platforms</span><span class="val">{{ form.platforms.join(', ') }}</span></div>
                <div class="row"><span class="lbl">Active Cohorts</span><span class="val">{{ cohortOptions.length - disabledCohorts.length }} of {{ cohortOptions.length }}</span></div>
                <div class="row"><span class="lbl">Seed</span><span class="val font-mono">{{ form.simulationSeed }}</span></div>
              </div>
            </div>

            <!-- What will be generated -->
            <div class="sb-card run-plan-card output-card">
              <h3>📤 What Will Be Generated</h3>
              <ul class="output-list">
                <li>📊 Predicted rating distribution (mean, confidence band)</li>
                <li>🚫 DNF abandonment risk score + chapter pressure map</li>
                <li>🔥 Controversy risk + backlash scenario list</li>
                <li>⚡ Viral &amp; quoteability potential scores</li>
                <li>✏️ Revision priority ranking (scored &amp; evidence-linked)</li>
                <li>💬 Simulated platform posts per selected platform</li>
                <li v-if="form.editorBoardEnabled">🎭 Development Editor Board — 12 archetypal lenses</li>
                <li>📋 Full exportable report (PDF, DOCX, MD, JSON, PNG)</li>
              </ul>
            </div>

            <!-- Time and privacy -->
            <div class="sb-card run-plan-card timing-card">
              <h3>⏱ Time &amp; Privacy</h3>
              <div class="summary-details">
                <div class="row">
                  <span class="lbl">Estimated Run Time</span>
                  <span class="val time-val">{{ formattedEstimatedTime }}</span>
                </div>
                <div class="row">
                  <span class="lbl">Manuscript Leaves Machine?</span>
                  <span class="val" :class="{ 'val-safe': form.privacyMode === 'local_only', 'val-warn': form.privacyMode !== 'local_only' }">
                    {{ form.privacyMode === 'local_only' ? 'No — strictly offline' : form.privacyMode === 'hybrid_safe' ? 'Embeddings only — no raw text sent' : 'Cloud reasoning active — text excerpts may be sent' }}
                  </span>
                </div>
                <div class="row">
                  <span class="lbl">Editor Board</span>
                  <span class="val">{{ form.editorBoardEnabled ? 'Enabled (+~15s)' : 'Disabled' }}</span>
                </div>
              </div>
              <div class="privacy-run-badge" :class="form.privacyMode">
                🔒 {{ form.privacyMode }}
              </div>
            </div>
          </div>

          <div class="run-confirmation-banner">
            <span class="run-conf-icon" aria-hidden="true">🚀</span>
            <div>
              <strong>Ready to start?</strong>
              <p>Click Start Simulation below. You will be taken to the live progress screen. The simulation runs locally and typically completes in {{ formattedEstimatedTime }}.</p>
            </div>
          </div>
        </section>

        <!-- ============================================================
             NAVIGATION ACTIONS
        ============================================================= -->
        <footer class="wizard-actions">
          <button
            class="ghost-btn"
            :disabled="currentStep === 1 || submitting"
            @click="prevStep"
            aria-label="Go back to previous step"
          >
            ← Back
          </button>

          <div class="next-action-group">
            <button
              class="primary-btn next-btn"
              :disabled="submitting"
              @click="nextStep"
              :aria-label="nextButtonLabel"
            >
              <span v-if="submitting" class="loading-spinner" aria-hidden="true">⏳</span>
              <span>{{ nextButtonLabel }}</span>
            </button>
          </div>
        </footer>

      </div><!-- /wizard-card -->
    </div><!-- /wizard-container -->
  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { createBookSimProject, getBookSimHealth, createEvidencePack, runBookSimulation, parseManuscriptFile } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'
import { MAX_FILE_BYTES, ALLOWED_EXTENSIONS, formatBytes as fmtBytes, estimateProcessingTime } from '../../config/uploadLimits'

const props = defineProps({
  projectId: {
    type: String,
    default: '',
  },
})

const router = useRouter()
const route = useRoute()

const session = ref(getSwarmbookSession())
const currentStep = ref(1)
const error = ref('')
const loadingMessage = ref('')
const submitting = ref(false)
const health = ref(null)
const dragOver = ref(false)
const fileInput = ref(null)

const evidencePack = ref(session.value.evidencePack)
const activeEvidenceTab = ref('dna')
const showOptionalBasics = ref(false)
const showPasteArea = ref(false)
const showAdvancedSwarm = ref(false)

// 6-step wizard definition
const steps = [
  { num: 1, label: 'Basics' },
  { num: 2, label: 'Upload' },
  { num: 3, label: 'Intent' },
  { num: 4, label: 'Evidence' },
  { num: 5, label: 'Setup' },
  { num: 6, label: 'Review & Run' },
]

const evidenceTabs = [
  { id: 'dna', label: 'Book DNA' },
  { id: 'chapters', label: 'Chapters' },
  { id: 'characters', label: 'Characters' },
  { id: 'risks', label: 'Risks' },
  { id: 'style', label: 'Style' },
]

const platformOptionsList = ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub']

const cohortOptions = [
  { id: 'harsh', label: 'Harsh Reviewers', archetypes: ['goodreads_harsh_reviewer'], description: 'Critical, demanding reviewers who scrutinize pacing, character development, and plot holes.' },
  { id: 'loyalists', label: 'Genre Loyalists', archetypes: ['goodreads_genre_loyalist', 'reddit_genre_purist'], description: 'Highly committed to genre conventions, tropes, and familiar endings.' },
  { id: 'amplifiers', label: 'Emotional Amplifiers', archetypes: ['booktok_emotional_amplifier'], description: 'React confessionally to emotional arcs, heartbreaks, and shareable lines.' },
  { id: 'skeptics', label: 'Skeptics', archetypes: ['reddit_skeptic'], description: 'Analytical forum members checking internal logic, details, and unearned hype.' },
  { id: 'casual', label: 'Casual Readers', archetypes: ['casual_kindle_reader'], description: 'Pragmatic readers prioritizing clear stakes, easy flow, and readability.' },
  { id: 'literary', label: 'Literary Readers', archetypes: ['literary_reader'], description: 'Prize craft-conscious styles, voice, subtext, and thematic depth.' },
  { id: 'evidence_skeptics', label: 'Non-Fiction Evidence Skeptics', archetypes: ['nonfiction_evidence_skeptic'], description: 'Verify claim integrity, citations, methodology, and logic limits.' }
]

const disabledCohorts = ref([])

const excludeArchetypesList = computed(() => {
  const list = []
  cohortOptions.forEach(cohort => {
    if (disabledCohorts.value.includes(cohort.id)) {
      list.push(...cohort.archetypes)
    }
  })
  return list
})

const isProfileOrPrivacyChanged = computed(() => {
  const isDefaultProfile = form.localProfile === (health.value?.profiles?.default_profile || 'hybrid_safe_default')
  const isDefaultPrivacy = form.privacyMode === 'hybrid_safe'
  return !isDefaultProfile || !isDefaultPrivacy
})

// Dynamic next button label per step
const nextButtonLabel = computed(() => {
  const labels = {
    1: 'Save & Continue to Upload →',
    2: 'Analyze Content →',
    3: 'Build Evidence Packs →',
    4: 'Accept & Configure Simulation →',
    5: 'Review Run Plan →',
    6: submitting.value ? 'Starting Simulation...' : 'Start Simulation 🚀',
  }
  return labels[currentStep.value] || 'Next →'
})

const accuracyChecks = computed(() => {
  const checks = {
    contentType: { label: 'Good', desc: '', status: 'ok', icon: '✅', value: 15 },
    metaCompleteness: { label: 'Missing', desc: '', status: 'error', icon: '❌', value: 0 },
    profileAccuracy: { label: 'Standard', desc: '', status: 'ok', icon: '✅', value: 20 },
    privacyAccuracy: { label: 'Standard', desc: '', status: 'ok', icon: '✅', value: 20 },
    score: 0,
    scoreLabel: 'Minimal',
    scoreColor: 'var(--sb-color-offline)',
  }

  const cType = form.contentType
  if (['full_manuscript', 'novel', 'novella'].includes(cType)) {
    checks.contentType = { label: 'Maximum Depth', desc: 'Full-length narrative allows complete cohort simulation.', status: 'ok', icon: '✅', value: 25 }
  } else if (['chapter_sample', 'research_pack', 'book_proposal'].includes(cType)) {
    checks.contentType = { label: 'High Depth', desc: 'Partial structure checks pacing and key narrative themes.', status: 'info', icon: 'ℹ️', value: 20 }
  } else if (['short_story', 'article_essay', 'newsletter'].includes(cType)) {
    checks.contentType = { label: 'Medium Depth', desc: 'Shorter content has smaller platform reaction surface.', status: 'warn', icon: '⚠️', value: 15 }
  } else {
    checks.contentType = { label: 'Jacket Only', desc: 'Hook feedback only; no deeper pacing audits possible.', status: 'warn', icon: '⚠️', value: 10 }
  }

  const bLength = (form.blurb || '').trim().length
  if (bLength === 0) {
    checks.metaCompleteness = { label: 'Empty', desc: 'Jacket description is required for hook context.', status: 'error', icon: '❌', value: 0 }
  } else if (bLength < 100) {
    checks.metaCompleteness = { label: 'Too Short', desc: 'Under 100 chars limits persona hook calibration.', status: 'warn', icon: '⚠️', value: 10 }
  } else if (bLength < 300) {
    checks.metaCompleteness = { label: 'Acceptable', desc: 'Sufficient, but richer synopsis improves alignment.', status: 'info', icon: 'ℹ️', value: 20 }
  } else {
    checks.metaCompleteness = { label: 'Rich Synopsis', desc: 'Detailed premise gives cohorts strong setup signals.', status: 'ok', icon: '✅', value: 25 }
  }

  const prof = form.localProfile
  if (prof === 'cloud_quality') {
    checks.profileAccuracy = { label: 'High (60 Cohorts)', desc: 'Maximum statistical coverage for platforms and cohorts.', status: 'ok', icon: '✅', value: 25 }
  } else if (prof === 'hybrid_safe_default') {
    checks.profileAccuracy = { label: 'Balanced (30 Cohorts)', desc: 'Standard cohort set covers typical platform spreads.', status: 'ok', icon: '✅', value: 20 }
  } else {
    checks.profileAccuracy = { label: 'Minimal (12 Cohorts)', desc: 'Fast checkout, but reduced platform resolution.', status: 'warn', icon: '⚠️', value: 10 }
  }

  const priv = form.privacyMode
  if (priv === 'cloud_quality') {
    checks.privacyAccuracy = { label: 'Cloud Cognitive', desc: 'Advanced reasoning captures nuanced subtext.', status: 'ok', icon: '✅', value: 25 }
  } else if (priv === 'hybrid_safe') {
    checks.privacyAccuracy = { label: 'Hybrid Standard', desc: 'Local LLM + cloud-calibrated embeddings.', status: 'info', icon: 'ℹ️', value: 20 }
  } else {
    checks.privacyAccuracy = { label: 'Local Only', desc: 'Workstation-limited offline models.', status: 'warn', icon: '⚠️', value: 15 }
  }

  checks.score = checks.contentType.value + checks.metaCompleteness.value + checks.profileAccuracy.value + checks.privacyAccuracy.value

  if (checks.score >= 85) { checks.scoreLabel = 'Production Grade'; checks.scoreColor = 'var(--sb-color-ready)' }
  else if (checks.score >= 65) { checks.scoreLabel = 'High Fidelity'; checks.scoreColor = 'var(--sb-color-info)' }
  else if (checks.score >= 45) { checks.scoreLabel = 'Medium Fidelity'; checks.scoreColor = 'var(--sb-color-mixed)' }
  else { checks.scoreLabel = 'Low Fidelity'; checks.scoreColor = 'var(--sb-color-offline)' }

  return checks
})

const estimatedTimeSec = computed(() => {
  const count = form.personaCount || 0
  let perPersona = 2.0
  if (form.localProfile === 'local_tiny') perPersona = 1.2
  else if (form.localProfile === 'hybrid_safe_default') perPersona = 2.8
  else if (form.localProfile === 'cloud_quality') perPersona = 4.5
  if (form.editorBoardEnabled) return Math.ceil(count * perPersona + 15)
  return Math.ceil(count * perPersona)
})

const formattedEstimatedTime = computed(() => {
  const sec = estimatedTimeSec.value
  if (sec < 60) return `~${sec} seconds`
  const min = Math.floor(sec / 60)
  const rem = sec % 60
  if (rem === 0) return `~${min} min`
  return `~${min} min ${rem} sec`
})

const customWarnings = computed(() => {
  const list = []
  if (form.localProfile === 'cloud_quality') {
    list.push({ code: 'heavy_cloud', message: 'Cloud Quality profile uploads manuscript chunks to external APIs. Ensure Gemini and NVIDIA keys are configured.' })
  }
  if (form.personaCount > 40 && form.privacyMode === 'local_only') {
    list.push({ code: 'high_local_load', message: 'More than 40 personas on local mode may cause heavy CPU/GPU load on 16 GB RAM workstations. Consider reducing to 12–20.' })
  }
  return list
})

const form = reactive({
  // Step 1: Basics
  projectName: session.value.metadata.projectName || '',
  title: session.value.metadata.title || '',
  authorName: session.value.metadata.authorName || '',
  bookType: session.value.metadata.bookType || 'fiction',
  genre: session.value.metadata.genre || '',
  contentType: session.value.metadata.contentType || 'novel',
  // Step 2: Upload
  manuscriptText: session.value.manuscript.text || '',
  manuscriptFilename: session.value.manuscript.filename || '',
  manuscriptLanguage: session.value.manuscript.language || 'en',
  manuscriptSizeBytes: session.value.manuscript.sizeBytes || 0,
  manuscriptMimeType: session.value.manuscript.mimeType || '',
  manuscriptWordCount: session.value.manuscript.wordCount || 0,
  sectionCount: session.value.manuscript.sectionCount || 0,
  // Step 3: Intent
  targetReader: session.value.metadata.targetReader || '',
  blurb: session.value.metadata.blurb || '',
  testGoal: session.value.metadata.testGoal || '',
  compTitles: session.value.metadata.compTitles || '',
  coverBrief: session.value.metadata.coverBrief || '',
  subtitle: session.value.metadata.subtitle || '',
  // Step 5: Swarm Config
  privacyMode: session.value.metadata.privacyMode || 'hybrid_safe',
  localProfile: session.value.metadata.localProfile || 'hybrid_safe_default',
  platforms: [...(session.value.simulationConfig.platforms || ['goodreads', 'reddit', 'booktok'])],
  personaCount: session.value.simulationConfig.personaCount || 30,
  simulationSeed: session.value.simulationConfig.simulationSeed ?? 17,
  editorBoardEnabled: true,
})

const activeValidationFields = reactive({
  projectName: false,
  title: false,
  authorName: false,
  genre: false,
  targetReader: false,
  testGoal: false,
  blurb: false,
  manuscriptText: false,
})

const validationErrors = ref([])

const isManuscriptTooLarge = computed(() => form.manuscriptText && form.manuscriptText.length > 500000)

const profileOptions = computed(() => {
  const items = health.value?.profiles?.items || []
  if (items.length) return items
  return [
    { profile_name: 'local_tiny', privacy_mode: 'local_only', max_personas: 12, platforms: ['goodreads', 'reddit', 'x'], computed_warnings: [] },
    { profile_name: 'hybrid_safe_default', privacy_mode: 'hybrid_safe', max_personas: 30, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x'], computed_warnings: [] },
    { profile_name: 'cloud_quality', privacy_mode: 'cloud_quality', max_personas: 60, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub'], computed_warnings: [] },
  ]
})

const selectedProfile = computed(() => profileOptions.value.find(p => p.profile_name === form.localProfile))

const selectedProfileWarnings = computed(() => selectedProfile.value?.computed_warnings || [])

// =========================================================================
// Validation
// =========================================================================
function canJumpTo(stepNum) {
  if (stepNum === 1) return true
  if (stepNum === 2) return !!(form.projectName && form.title && form.authorName && form.genre)
  if (stepNum === 3) return canJumpTo(2) && !!(form.manuscriptText || form.manuscriptFilename)
  if (stepNum === 4) return canJumpTo(3) && !!(form.targetReader && form.testGoal && form.blurb)
  if (stepNum === 5) return canJumpTo(4) && !!evidencePack.value
  if (stepNum === 6) return canJumpTo(5) && form.platforms.length > 0
  return false
}

function jumpToStep(stepNum) {
  if (canJumpTo(stepNum)) {
    saveState()
    currentStep.value = stepNum
    validationErrors.value = []
  }
}

function clearValidationError(field) {
  activeValidationFields[field] = false
}

function validateStep1() {
  validationErrors.value = []
  let ok = true
  const fields = [
    { key: 'projectName', label: 'Project reference name' },
    { key: 'title', label: 'Content title' },
    { key: 'authorName', label: 'Author name' },
    { key: 'genre', label: 'Genre / Category' },
  ]
  for (const f of fields) {
    if (!form[f.key] || !form[f.key].trim()) {
      activeValidationFields[f.key] = true
      validationErrors.value.push(`Missing required field: ${f.label}`)
      ok = false
    } else {
      activeValidationFields[f.key] = false
    }
  }
  return ok
}

function validateStep2() {
  validationErrors.value = []
  if (!form.manuscriptText || !form.manuscriptText.trim()) {
    activeValidationFields.manuscriptText = true
    validationErrors.value.push('Please upload a manuscript file or paste content before continuing.')
    return false
  }
  activeValidationFields.manuscriptText = false
  return true
}

function validateStep3() {
  validationErrors.value = []
  let ok = true
  const fields = [
    { key: 'targetReader', label: 'Target reader' },
    { key: 'testGoal', label: 'Test goal' },
    { key: 'blurb', label: 'Intended promise / blurb' },
  ]
  for (const f of fields) {
    if (!form[f.key] || !form[f.key].trim()) {
      activeValidationFields[f.key] = true
      validationErrors.value.push(`Missing required field: ${f.label}`)
      ok = false
    } else {
      activeValidationFields[f.key] = false
    }
  }
  return ok
}

function validateStep5() {
  validationErrors.value = []
  if (form.platforms.length === 0) {
    validationErrors.value = ['Please select at least one simulated platform.']
    return false
  }
  return true
}

// =========================================================================
// Navigation
// =========================================================================
async function nextStep() {
  if (currentStep.value === 1) {
    if (validateStep1()) {
      saveState()
      currentStep.value = 2
    }
  } else if (currentStep.value === 2) {
    if (validateStep2()) {
      saveState()
      currentStep.value = 3
    }
  } else if (currentStep.value === 3) {
    if (validateStep3()) {
      saveState()
      await buildEvidencePackStep()
    }
  } else if (currentStep.value === 4) {
    saveState()
    currentStep.value = 5
  } else if (currentStep.value === 5) {
    if (validateStep5()) {
      saveState()
      currentStep.value = 6
    }
  } else if (currentStep.value === 6) {
    await runCohortSimulation()
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    saveState()
    currentStep.value -= 1
    validationErrors.value = []
  }
}

// =========================================================================
// State management
// =========================================================================
function saveState() {
  updateSwarmbookSession({
    metadata: {
      projectName: form.projectName,
      title: form.title,
      authorName: form.authorName,
      bookType: form.bookType,
      genre: form.genre,
      targetReader: form.targetReader,
      subtitle: form.subtitle,
      privacyMode: form.privacyMode,
      localProfile: form.localProfile,
      blurb: form.blurb,
      compTitles: form.compTitles,
      coverBrief: form.coverBrief,
      contentType: form.contentType,
      testGoal: form.testGoal,
    },
    manuscript: {
      text: form.manuscriptText,
      filename: form.manuscriptFilename,
      language: form.manuscriptLanguage,
      sizeBytes: form.manuscriptSizeBytes,
      mimeType: form.manuscriptMimeType,
      wordCount: form.manuscriptWordCount,
      sectionCount: form.sectionCount,
    },
    simulationConfig: {
      profileName: form.localProfile,
      personaCount: form.personaCount,
      platforms: form.platforms,
      privacyMode: form.privacyMode,
      simulationSeed: form.simulationSeed,
      disabledCohorts: [...disabledCohorts.value],
      editorBoardEnabled: form.editorBoardEnabled,
    },
  })
}

watch(form, () => { saveState() }, { deep: true })

// =========================================================================
// Upload handlers
// =========================================================================
const uploadError = ref('')

function formatBytes(bytes) {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function clearFile() {
  form.manuscriptText = ''
  form.manuscriptFilename = ''
  form.manuscriptSizeBytes = 0
  form.manuscriptMimeType = ''
  form.manuscriptWordCount = 0
  form.sectionCount = 0
  uploadError.value = ''
  saveState()
}

function onPasteInput() {
  form.manuscriptFilename = 'pasted_draft.txt'
  form.manuscriptSizeBytes = form.manuscriptText.length
  form.manuscriptMimeType = 'text/plain'
  form.manuscriptWordCount = form.manuscriptText.split(/\s+/).filter(Boolean).length
  saveState()
}

function onFileSelect(event) {
  const file = event.target.files?.[0]
  if (file) handleFileUpload(file)
}

function onFileDrop(event) {
  dragOver.value = false
  const file = event.dataTransfer.files?.[0]
  if (file) handleFileUpload(file)
}

function triggerFileBrowser() {
  fileInput.value?.click()
}

async function handleFileUpload(file) {
  uploadError.value = ''
  error.value = ''
  const allowed = ['.txt', '.md', '.markdown', '.pdf', '.docx']
  const matched = allowed.some(ext => file.name.toLowerCase().endsWith(ext))
  if (!matched) {
    uploadError.value = `Unsupported format. Please upload a .pdf, .docx, .txt, or .md file.`
    return
  }
  const maxBytes = MAX_FILE_BYTES
  if (file.size > maxBytes) {
    const overBytes = file.size - maxBytes
    const overPercent = (overBytes / maxBytes) * 100
    uploadError.value = `File too large: "${file.name}" (${fmtBytes(file.size)}) exceeds the ${fmtBytes(maxBytes)} limit. Oversized by ${fmtBytes(overBytes)} (${overPercent.toFixed(1)}%).`
    return
  }
  loadingMessage.value = `Uploading and parsing "${file.name}"...`
  try {
    const response = await parseManuscriptFile(file)
    const data = response.data.data || response.data
    form.manuscriptText = data.text
    form.manuscriptFilename = data.filename
    form.manuscriptSizeBytes = data.size_bytes
    form.manuscriptMimeType = data.mime_type
    form.manuscriptWordCount = data.word_count
    form.sectionCount = data.section_count || 0
    saveState()
  } catch (err) {
    const apiError = err.response?.data
    if (apiError && apiError.error_code === 'file_too_large') {
      const details = apiError.details
      if (details.unit === 'characters') {
        uploadError.value = `File too large: parsed manuscript (${details.actual_size.toLocaleString()} characters) exceeds ${details.max_size.toLocaleString()} chars.`
      } else {
        uploadError.value = `File too large: file size (${formatBytes(details.actual_size)}) exceeds ${formatBytes(details.max_size)}.`
      }
    } else {
      uploadError.value = apiError?.error || `Upload/parsing failed: ${err.message}`
    }
  } finally {
    loadingMessage.value = ''
  }
}

// =========================================================================
// Profile change
// =========================================================================
function onProfileChange() {
  const selected = profileOptions.value.find((profile) => profile.profile_name === form.localProfile)
  if (selected) {
    form.privacyMode = selected.privacy_mode || form.privacyMode
    form.personaCount = selected.max_personas || form.personaCount
    form.platforms = (selected.platforms || []).map(p => String(p).toLowerCase())
  }
  saveState()
}

function togglePlatformCheckbox(platform) {
  if (form.platforms.includes(platform)) {
    form.platforms = form.platforms.filter((p) => p !== platform)
  } else {
    form.platforms = [...form.platforms, platform]
  }
  saveState()
}

function toggleCohortExclusion(cohortId) {
  if (disabledCohorts.value.includes(cohortId)) {
    disabledCohorts.value = disabledCohorts.value.filter(id => id !== cohortId)
  } else {
    disabledCohorts.value = [...disabledCohorts.value, cohortId]
  }
  saveState()
}

// =========================================================================
// Evidence pack build
// =========================================================================
async function buildEvidencePackStep() {
  submitting.value = true
  loadingMessage.value = 'Creating project and building editorial evidence packs...'
  error.value = ''
  try {
    const projResponse = await createBookSimProject({
      project_id: session.value.projectId || undefined,
      name: form.projectName,
      title: form.title,
      author_name: form.authorName,
      profile_name: form.localProfile,
      privacy_mode: form.privacyMode,
      metadata: {
        book_type: form.bookType,
        genre: form.genre,
        target_reader: form.targetReader,
        subtitle: form.subtitle,
        blurb: form.blurb,
        comp_titles: form.compTitles,
        cover_brief: form.coverBrief,
        local_profile: form.localProfile,
        content_type: form.contentType,
        test_goal: form.testGoal,
      },
    })

    const epResponse = await createEvidencePack({
      project_id: projResponse.data.project_id,
      title: form.title,
      author_name: form.authorName,
      text: form.manuscriptText,
      filename: form.manuscriptFilename || 'draft.txt',
      language: form.manuscriptLanguage,
      metadata: {
        book_type: form.bookType,
        genre: form.genre,
        target_reader: form.targetReader,
        subtitle: form.subtitle,
        blurb: form.blurb,
        comp_titles: form.compTitles,
        cover_brief: form.coverBrief,
        content_type: form.contentType,
        test_goal: form.testGoal,
      },
    })

    evidencePack.value = epResponse.data.evidence_pack
    session.value = updateSwarmbookSession({
      projectId: projResponse.data.project_id,
      project: projResponse.data,
      evidencePack: epResponse.data.evidence_pack,
    })

    currentStep.value = 4
  } catch (err) {
    error.value = err.message
  } finally {
    loadingMessage.value = ''
    submitting.value = false
  }
}

async function regenerateEvidence() {
  if (!form.manuscriptText) return
  await buildEvidencePackStep()
}

// =========================================================================
// Run simulation
// =========================================================================
function runCohortSimulation() {
  saveState()
  router.push({ name: 'SwarmbookSimulationRun', params: { projectId: session.value.projectId } })
}

// =========================================================================
// Health check
// =========================================================================
async function loadHealth() {
  try {
    const response = await getBookSimHealth()
    health.value = response.data
  } catch (err) {
    console.warn('Wizard load health failed:', err)
  }
}

onMounted(() => {
  loadHealth()
  const storedDisabled = session.value.simulationConfig?.disabledCohorts
  if (storedDisabled) {
    disabledCohorts.value = [...storedDisabled]
  }
  // Resume wizard at appropriate step if project is already active
  if (props.projectId && props.projectId !== 'new' && session.value.projectId === props.projectId) {
    if (session.value.evidencePack) {
      currentStep.value = 4
    } else if (session.value.manuscript?.text && session.value.metadata?.targetReader) {
      currentStep.value = 3
    } else if (session.value.manuscript?.text) {
      currentStep.value = 2
    }
  }
})
</script>

<style scoped>
/* ====================================================================
   WIZARD CONTAINER
==================================================================== */
.wizard-container {
  max-width: 980px;
  margin: 0 auto;
}

/* ====================================================================
   STEPPER RIBBON
==================================================================== */
.wizard-stepper {
  display: flex;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 20px;
  margin-bottom: 24px;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  flex-wrap: wrap;
  gap: 8px;
}

.stepper-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #94a3b8;
  font-size: 0.82rem;
  font-weight: 600;
  transition: color 0.2s;
  outline: none;
  padding: 4px 2px;
  border-radius: 4px;
}
.stepper-item:focus-visible { outline: 2px solid #ff4500; }
.stepper-item.active { color: #ff4500; }
.stepper-item.completed { color: #10b981; }
.stepper-item.disabled { opacity: 0.45; cursor: not-allowed; }

.step-num-circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid currentColor;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  flex-shrink: 0;
}
.chevron { font-size: 1.1rem; color: #cbd5e1; }

/* ====================================================================
   WIZARD CARD
==================================================================== */
.wizard-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 36px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* ====================================================================
   STEP QUESTION HEADER
==================================================================== */
.step-question-header {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}
.step-eyebrow {
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #ff4500;
  display: block;
  margin-bottom: 6px;
  font-family: 'JetBrains Mono', monospace;
}
.wizard-step-section h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 8px 0;
  line-height: 1.2;
}
.step-hint {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

/* ====================================================================
   WHAT HAPPENS NEXT HELPER
==================================================================== */
.what-next-helper {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 24px;
  font-size: 0.85rem;
  color: #166534;
  line-height: 1.5;
}
.what-next-icon {
  font-size: 1rem;
  margin-top: 1px;
  flex-shrink: 0;
  color: #16a34a;
}

/* ====================================================================
   FORM FIELDS
==================================================================== */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field-group.textarea-group { margin-top: 0; }
.field-group.has-error input,
.field-group.has-error textarea,
.field-group.has-error select {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239,68,68,0.1);
}
.label-text {
  font-size: 0.83rem;
  font-weight: 700;
  color: #374151;
}
.req { color: #ef4444; }
.microcopy {
  font-size: 0.72rem;
  color: #94a3b8;
  line-height: 1.4;
  margin-top: 1px;
}
.char-hint { font-size: 0.72rem; color: #94a3b8; margin-top: 2px; }
.char-hint-warn { color: #b45309; }
.char-hint-ok { color: #16a34a; }

/* ====================================================================
   STEP 1 LAYOUT
==================================================================== */
.step1-layout {
  display: grid;
  grid-template-columns: 2.2fr 1fr;
  gap: var(--sb-space-6, 24px);
  align-items: stretch;
  margin-bottom: 24px;
}
.form-fields-col { display: flex; flex-direction: column; }
.checklist-col { display: flex; flex-direction: column; }
.accuracy-card {
  border: 1px solid var(--sb-border-color, #e2e8f0);
  border-radius: var(--sb-radius-xl, 12px);
  background: var(--sb-bg-card, #fff);
  padding: var(--sb-space-5, 20px);
  box-shadow: var(--sb-shadow-sm, 0 1px 3px rgba(0,0,0,0.05));
  height: 100%;
  display: flex;
  flex-direction: column;
}
.accuracy-card h3 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px 0;
}
.checklist-hint {
  font-size: 0.72rem;
  color: #64748b;
  margin: 0 0 16px 0;
}
.accuracy-list-stack {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
}
.accuracy-item-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.status-indicator-badge { font-size: 1.1rem; line-height: 1; flex-shrink: 0; }
.accuracy-item-row strong {
  font-size: 0.8rem;
  color: #0f172a;
  display: block;
  margin-bottom: 2px;
}
.accuracy-item-row span {
  font-size: 0.7rem;
  color: #64748b;
  line-height: 1.3;
  display: block;
}
.score-progress-box {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}
.score-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.fidelity-score-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.fidelity-bar-rail {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}
.fidelity-bar-fill {
  height: 100%;
  transition: width 0.3s ease;
}

/* ====================================================================
   STEP 2: UPLOAD
==================================================================== */
.upload-info-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 16px;
  margin-bottom: 18px;
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
}
.strip-item { display: flex; align-items: center; gap: 4px; }
.strip-divider { color: #cbd5e1; }
.limit-info { color: #b45309; font-family: 'JetBrains Mono', monospace; }
.privacy-note { color: #16a34a; }

.wizard-upload-zone {
  border: 2px dashed #cbd5e1;
  background: #f8fafc;
  padding: 36px;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 16px;
  outline: none;
}
.wizard-upload-zone:hover, .wizard-upload-zone:focus-visible { border-color: #ff4500; background: #fff5ef; }
.wizard-upload-zone:focus-visible { outline: 2px solid #ff4500; }
.wizard-upload-zone.is-dragover { border-color: #ff4500; background: #fff5ef; transform: scale(1.01); }
.wizard-upload-zone.has-file { border-color: #10b981; background: #f0fdf4; }
.drop-zone-content { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.upload-icon { font-size: 2.5rem; }
.wizard-upload-zone h3 { font-size: 1rem; font-weight: 700; margin: 0; }
.browse-link { color: #ff4500; font-weight: 600; margin: 0; font-size: 0.88rem; }
.formats-label { font-size: 0.72rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; }
.selected-file-display { display: flex; align-items: center; gap: 16px; text-align: left; }
.file-icon { font-size: 2.5rem; flex-shrink: 0; }
.file-details { flex: 1; }
.file-details h3 { font-size: 1rem; font-weight: 700; color: #0f172a; margin: 0 0 6px 0; word-break: break-all; }
.file-meta { display: flex; gap: 6px; flex-wrap: wrap; margin: 0; }
.meta-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  background: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.word-badge { background: #e0f2fe; color: #0369a1; }
.section-badge { background: #fef3c7; color: #92400e; }
.remove-btn {
  background: transparent;
  border: 1px solid #fca5a5;
  color: #ef4444;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  flex-shrink: 0;
  font-family: inherit;
}
.remove-btn:hover { background: #fee2e2; }
.hidden-input { display: none; }

.file-meta-panel {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 16px;
}
.meta-col { display: flex; flex-direction: column; gap: 4px; }
.meta-label { font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }
.meta-value { font-size: 0.85rem; color: #0f172a; font-weight: 600; }
.privacy-badge-local_only { color: #16a34a; }
.privacy-badge-hybrid_safe { color: #2563eb; }
.privacy-badge-cloud_quality { color: #d97706; }

.paste-collapse-container {
  margin-top: 20px;
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
}
.paste-textarea-wrapper { margin-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.char-count-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
  margin-top: 4px;
}
.warn-text { color: #b45309; font-weight: 700; }
.limit-warning { color: #b45309; font-weight: 600; }

/* ====================================================================
   STEP 3: INTENT LAYOUT
==================================================================== */
.intent-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}
.intent-fields-col { display: flex; flex-direction: column; gap: 20px; }
.intent-sidebar { display: flex; flex-direction: column; }
.intent-tip-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  position: sticky;
  top: 20px;
}
.intent-tip-card h3 { font-size: 0.9rem; font-weight: 700; margin: 0 0 12px 0; }
.intent-tip-list { list-style: none; padding: 0; margin: 0 0 16px 0; display: flex; flex-direction: column; gap: 10px; }
.intent-tip-list li { font-size: 0.8rem; color: #475569; line-height: 1.4; }
.intent-tip-list strong { color: #0f172a; }
.intent-confidence-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 8px 12px;
  border-radius: 6px;
  background: #f0fdf4;
  color: #166534;
}
.intent-confidence-strip.warn { background: #fffbeb; color: #92400e; }
.conf-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.conf-dot.ready { background: #16a34a; }
.conf-dot.warn { background: #d97706; }

/* ====================================================================
   STEP 4: EVIDENCE REVIEW
==================================================================== */
.evidence-summary-strip {
  display: flex;
  gap: 0;
  margin-bottom: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}
.es-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
}
.es-item:last-child { border-right: none; }
.es-label { font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; }
.es-status { font-size: 0.78rem; font-weight: 700; }
.status-ok { color: #16a34a; }
.status-warn { color: #d97706; }
.status-missing { color: #ef4444; }

.evidence-tabs { margin-bottom: 16px; }
.tabs-header { display: flex; gap: 4px; border-bottom: 1px solid #e2e8f0; margin-bottom: 20px; }
.tab-btn {
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 10px 16px;
  font-size: 0.83rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  outline: none;
  font-family: inherit;
  transition: color 0.2s;
}
.tab-btn.active { border-bottom-color: #ff4500; color: #ff4500; }
.tab-btn:focus-visible { outline: 2px solid #ff4500; border-radius: 4px; }
.tab-body { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; min-height: 200px; }
.tab-body h3 { font-size: 0.95rem; font-weight: 700; margin: 0 0 16px 0; }
.tab-empty-note { font-size: 0.85rem; color: #64748b; font-style: italic; }
.meta-display p { font-size: 0.88rem; line-height: 1.6; margin: 0 0 8px 0; }
.premise-quote { border-left: 3px solid #cbd5e1; padding-left: 12px; margin: 10px 0; font-style: italic; color: #475569; font-size: 0.88rem; }
.stepper-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 16px; }
.stepper-list li { border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; }
.stepper-list li:last-child { border-bottom: none; padding-bottom: 0; }
.stepper-list strong { font-size: 0.9rem; color: #0f172a; display: block; margin-bottom: 4px; }
.risk-badge {
  background: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 4px;
  font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; display: inline-block;
}
.evidence-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
  flex-wrap: wrap;
  gap: 8px;
}
.evidence-accept-note { font-size: 0.8rem; color: #64748b; }
.small-btn { font-size: 0.82rem; padding: 8px 14px; }

/* ====================================================================
   STEP 5: SIMULATION SETUP
==================================================================== */
.profile-cards-grid { display: flex; flex-direction: column; gap: 12px; margin-top: 8px; margin-bottom: 24px; }
.profile-selection-card {
  border: 2px solid #e2e8f0; border-radius: 10px; padding: 16px;
  cursor: pointer; background: #ffffff; transition: all 0.2s; outline: none;
}
.profile-selection-card:hover { border-color: #cbd5e1; background: #f8fafc; }
.profile-selection-card:focus-visible { outline: 2px solid #ff4500; }
.profile-selection-card.active { border-color: #ff4500; background: #fffaf7; }
.profile-card-header { display: flex; gap: 12px; align-items: center; margin-bottom: 6px; }
.profile-icon { font-size: 1.5rem; line-height: 1; }
.profile-title-row { display: flex; justify-content: space-between; align-items: center; flex: 1; flex-wrap: wrap; gap: 6px; }
.profile-title-row h3 { font-size: 0.95rem; font-weight: 800; margin: 0; color: #0f172a; }
.recommendation-badge { font-size: 0.72rem; font-weight: 800; background: #ffebdf; color: #e63e00; padding: 2px 8px; border-radius: 9999px; text-transform: uppercase; }
.profile-desc { font-size: 0.82rem; color: #475569; line-height: 1.4; margin: 0 0 10px 0; }
.profile-meta-chips { display: flex; gap: 12px; font-size: 0.75rem; color: #64748b; font-weight: 600; }

.slider-label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.count-indicator { font-size: 1.1rem; color: #ff4500; font-weight: 800; }
.slider-wrapper { margin-bottom: 6px; }
.premium-slider {
  width: 100%; height: 6px; background: #cbd5e1;
  border-radius: 9999px; outline: none; -webkit-appearance: none; cursor: pointer;
}
.premium-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%;
  background: #ff4500; cursor: pointer; transition: transform 0.1s;
}
.premium-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.premium-slider:focus-visible::-webkit-slider-thumb { box-shadow: 0 0 0 3px rgba(255,69,0,0.4); }
.slider-marks { display: flex; justify-content: space-between; font-size: 0.7rem; color: #94a3b8; font-weight: 700; padding: 4px 2px 0 2px; }

.platforms-checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
  margin-top: 8px;
  margin-bottom: 24px;
}
.platform-pill-btn {
  display: flex; align-items: center; gap: 10px; padding: 10px 14px;
  background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px;
  cursor: pointer; font: inherit; font-size: 0.85rem; font-weight: 600; color: #475569;
  transition: all 0.15s;
}
.platform-pill-btn:hover { border-color: #94a3b8; background: #f8fafc; }
.platform-pill-btn.active { border-color: #ff4500; background: #fff5ef; color: #e63e00; box-shadow: 0 0 0 1px #ff4500; }
.platform-pill-btn:focus-visible { outline: 2px solid #ff4500; }
.platform-icon { font-size: 1.1rem; }

.editor-board-toggle-row { margin: 20px 0; }
.editor-board-toggle {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 16px; border: 1px solid #e2e8f0; border-radius: 8px;
  cursor: pointer; background: #f8fafc; transition: border-color 0.2s;
}
.editor-board-toggle:hover { border-color: #ff4500; }
.editor-board-label { flex: 1; }
.editor-board-label strong { display: block; font-size: 0.88rem; color: #0f172a; margin-bottom: 4px; }

.advanced-settings-grid { margin-top: 16px; display: flex; flex-direction: column; gap: 24px; }
.cohorts-header-actions { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; font-size: 0.8rem; }
.action-link-btn {
  background: transparent; border: none; color: #ff4500;
  font-weight: 700; cursor: pointer; padding: 2px 4px; font: inherit; font-size: 0.8rem;
}
.action-link-btn:hover { text-decoration: underline; }
.bullet-divider { color: #cbd5e1; }
.cohorts-selection-list { display: flex; flex-direction: column; gap: 8px; }
.cohort-checkbox-card {
  display: flex; gap: 14px; align-items: flex-start; padding: 12px 14px;
  border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc;
  cursor: pointer; transition: border-color 0.2s;
}
.cohort-checkbox-card:hover { border-color: #cbd5e1; }
.cohort-checkbox-card.checked { border-color: #ff4500; background: #ffffff; }
.premium-checkbox { width: 18px; height: 18px; border-radius: 4px; accent-color: #ff4500; margin-top: 2px; flex-shrink: 0; }
.cohort-text-block { flex: 1; }
.cohort-label { display: block; font-size: 0.85rem; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
.cohort-desc { font-size: 0.78rem; color: #64748b; margin: 0; line-height: 1.3; }
.premium-input { border: 1px solid #cbd5e1; border-radius: 6px; padding: 7px 10px; font: inherit; font-size: 0.88rem; outline: none; width: 100%; }
.premium-input:focus { border-color: #ff4500; box-shadow: 0 0 0 1px #ff4500; }
.text-center { text-align: center; }

.estimate-strip {
  display: flex; align-items: center; gap: 10px;
  background: #fff7f5; border: 1px solid #ffd4c2; border-radius: 8px;
  padding: 12px 16px; margin: 20px 0; flex-wrap: wrap;
}
.estimate-label { font-size: 0.82rem; font-weight: 700; color: #475569; }
.estimate-value { font-size: 1.1rem; font-weight: 800; color: #ff4500; }
.estimate-hint { font-size: 0.75rem; color: #94a3b8; }

.alert-banners-stack { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
.setup-warning-banner { display: flex; gap: 10px; padding: 10px 12px; background: #fffbeb; border: 1px solid #fef3c7; border-radius: 6px; align-items: flex-start; }
.warning-icon { font-size: 1rem; margin-top: 1px; }
.warning-message { font-size: 0.78rem; color: #92400e; line-height: 1.3; margin: 0; }

/* ====================================================================
   STEP 6: REVIEW & RUN
==================================================================== */
.run-plan-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.run-plan-card {
  border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.run-plan-card h3 { font-size: 0.9rem; font-weight: 700; color: #0f172a; margin: 0 0 14px 0; }
.summary-details { display: flex; flex-direction: column; gap: 10px; }
.row { display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; font-size: 0.85rem; }
.row:last-child { border-bottom: none; padding-bottom: 0; }
.lbl { color: #64748b; font-weight: 500; flex-shrink: 0; }
.val { font-weight: 700; color: #0f172a; text-align: right; font-size: 0.85rem; }
.val-safe { color: #16a34a; }
.val-warn { color: #d97706; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.time-val { color: #ff4500; font-size: 1rem; }

.output-card .output-list {
  list-style: none; padding: 0; margin: 0;
  display: flex; flex-direction: column; gap: 8px;
}
.output-card .output-list li { font-size: 0.83rem; color: #374151; }

.privacy-run-badge {
  margin-top: 16px;
  font-size: 0.78rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  padding: 6px 12px;
  border-radius: 6px;
  display: inline-block;
}
.privacy-run-badge.local_only { background: #dcfce7; color: #166534; }
.privacy-run-badge.hybrid_safe { background: #dbeafe; color: #1e40af; }
.privacy-run-badge.cloud_quality { background: #fef3c7; color: #92400e; }

.run-confirmation-banner {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: linear-gradient(135deg, #fff7f5, #fff);
  border: 2px solid #ff4500;
  border-radius: 12px;
  padding: 20px 24px;
}
.run-conf-icon { font-size: 2rem; flex-shrink: 0; margin-top: 2px; }
.run-confirmation-banner strong { display: block; font-size: 1rem; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
.run-confirmation-banner p { font-size: 0.85rem; color: #475569; margin: 0; line-height: 1.5; }

/* ====================================================================
   WIZARD ACTIONS FOOTER
==================================================================== */
.wizard-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  gap: 12px;
}
.next-action-group { display: flex; align-items: center; gap: 8px; }
.next-btn { min-width: 200px; }

/* ====================================================================
   SHARED ELEMENTS
==================================================================== */
.validation-alert {
  background: #fef2f2; border: 1px solid #fca5a5;
  color: #991b1b; border-radius: 8px; padding: 16px; margin-bottom: 24px;
  position: relative;
}
.alert-hdr { font-weight: 700; font-size: 0.85rem; display: block; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.validation-alert ul { margin: 0; padding-left: 20px; font-size: 0.82rem; line-height: 1.5; }
.clear-err-btn {
  position: absolute; top: 12px; right: 14px;
  background: transparent; border: none; color: #ef4444;
  font-size: 1.1rem; cursor: pointer; line-height: 1;
}

.collapse-trigger-btn {
  background: transparent; border: none; color: #ff4500;
  font-size: 0.82rem; font-weight: 600; cursor: pointer;
  padding: 4px 0; font-family: inherit;
}
.collapse-trigger-btn:hover { text-decoration: underline; }
.collapse-trigger-btn:focus-visible { outline: 2px solid #ff4500; border-radius: 2px; }

.optional-fields-container { margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 12px; }
.optional-fields-grid { margin-top: 14px; display: flex; flex-direction: column; gap: 16px; }

.empty-state-card {
  text-align: center; padding: 40px 24px;
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
}
.empty-state-card .empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
.empty-state-card p { font-size: 0.88rem; color: #64748b; }

/* ====================================================================
   RESPONSIVE
==================================================================== */
@media (max-width: 900px) {
  .step1-layout { grid-template-columns: 1fr; }
  .intent-layout { grid-template-columns: 1fr; }
  .run-plan-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .wizard-stepper { flex-wrap: wrap; gap: 6px; }
  .step-lbl { display: none; }
  .wizard-card { padding: 20px 16px; }
  .evidence-summary-strip { flex-wrap: wrap; }
  .es-item { min-width: 80px; }
}

@media (prefers-reduced-motion: reduce) {
  .fidelity-bar-fill,
  .wizard-upload-zone,
  .profile-selection-card,
  .platform-pill-btn { transition: none; }
}
</style>
