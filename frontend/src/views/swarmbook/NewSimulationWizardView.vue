<template>
  <SwarmbookAppShell
    active-route="SwarmbookUpload"
    :project-id="session.projectId"
    title="Manuscript Simulation Wizard"
    subtitle="Configure book metadata, load manuscript content, analyze editorial evidence, set up reader cohorts, and trigger predictions."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <div class="wizard-container">
      <!-- Wizard Progress Stepper Ribbon -->
      <nav class="wizard-stepper" aria-label="Wizard Steps Progress">
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
          @keydown.enter="jumpToStep(step.num)"
          @keydown.space.prevent="jumpToStep(step.num)"
        >
          <span class="step-num-circle">{{ step.num }}</span>
          <span class="step-lbl">{{ step.label }}</span>
          <span class="chevron" v-if="step.num < 5">›</span>
        </div>
      </nav>

      <!-- Main Step Panel Card -->
      <div class="wizard-card">
        <!-- Form Errors Summary Banner -->
        <div v-if="validationErrors.length" class="validation-alert" role="alert" aria-live="polite">
          <span class="alert-hdr">Validation Errors</span>
          <ul>
            <li v-for="err in validationErrors" :key="err">{{ err }}</li>
          </ul>
        </div>

        <!-- STEP 1: BOOK BASICS -->
        <section v-if="currentStep === 1" class="wizard-step-section">
          <h2>Step 01 / Book Editorial Basics</h2>
          <p class="step-hint">Set the editorial context to guide the agent ontology generation.</p>

          <div class="step1-layout">
            <!-- Left Side: Form Fields -->
            <div class="form-fields-col">
              <div class="form-grid">
                <label class="field-group">
                  <span class="label-text">Content Type <span class="req">*</span></span>
                  <select v-model="form.contentType">
                    <option value="full_manuscript">Full manuscript</option>
                    <option value="novel">Novel</option>
                    <option value="novella">Novella</option>
                    <option value="short_story">Short story</option>
                    <option value="article_essay">Article / essay</option>
                    <option value="newsletter">Newsletter</option>
                    <option value="book_proposal">Book proposal</option>
                    <option value="blurb_synopsis">Blurb / synopsis</option>
                    <option value="chapter_sample">Chapter sample</option>
                    <option value="research_pack">Research / evidence pack</option>
                  </select>
                  <span class="microcopy">Select the format of the draft content you are testing.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.projectName }">
                  <span class="label-text">Project Reference Name <span class="req">*</span></span>
                  <input
                    v-model="form.projectName"
                    type="text"
                    placeholder="e.g. spring_thriller_draft"
                    aria-required="true"
                    @input="clearValidationError('projectName')"
                  />
                  <span class="microcopy">Internal project directory name. Use lowercase, numbers, or underscores.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.title }">
                  <span class="label-text">Content Title <span class="req">*</span></span>
                  <input
                    v-model="form.title"
                    type="text"
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
                    placeholder="e.g. Jane Doe"
                    aria-required="true"
                    @input="clearValidationError('authorName')"
                  />
                  <span class="microcopy">Author name or pen name.</span>
                </label>

                <label class="field-group">
                  <span class="label-text">Book Classification <span class="req">*</span></span>
                  <select v-model="form.bookType">
                    <option value="fiction">Fiction</option>
                    <option value="non-fiction">Non-Fiction</option>
                    <option value="mixed">Mixed Structure</option>
                  </select>
                  <span class="microcopy">Fiction evaluates narrative friction; Non-Fiction audits claims support.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.genre }">
                  <span class="label-text">Genre / Category <span class="req">*</span></span>
                  <input
                    v-model="form.genre"
                    type="text"
                    placeholder="e.g. Speculative Thriller"
                    aria-required="true"
                    @input="clearValidationError('genre')"
                  />
                  <span class="microcopy">Aids in targeting appropriate platform reviewers.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.targetReader }">
                  <span class="label-text">Target Reader <span class="req">*</span></span>
                  <input
                    v-model="form.targetReader"
                    type="text"
                    placeholder="e.g. Fans of high-concept slow-burn suspense"
                    aria-required="true"
                    @input="clearValidationError('targetReader')"
                  />
                  <span class="microcopy">Shapes the primary cohort archetypes.</span>
                </label>

                <label class="field-group" :class="{ 'has-error': activeValidationFields.testGoal }">
                  <span class="label-text">Test Goal <span class="req">*</span></span>
                  <input
                    v-model="form.testGoal"
                    type="text"
                    placeholder="e.g. Evaluate pacing in Chapter 2 and controversy risks"
                    aria-required="true"
                    @input="clearValidationError('testGoal')"
                  />
                  <span class="microcopy">Focuses simulated reader feedback on what you want tested.</span>
                </label>

                <label class="field-group">
                  <span class="label-text">Privacy Mode <span class="req">*</span></span>
                  <select v-model="form.privacyMode">
                    <option value="local_only">local_only (strictly offline execution)</option>
                    <option value="hybrid_safe">hybrid_safe (local run, cloud embeddings)</option>
                    <option value="cloud_quality">cloud_quality (advanced cloud reasoning)</option>
                  </select>
                </label>

                <label class="field-group">
                  <span class="label-text">Simulation Profile <span class="req">*</span></span>
                  <select v-model="form.localProfile" @change="onProfileChange">
                    <option v-for="profile in profileOptions" :key="profile.profile_name" :value="profile.profile_name">
                      {{ profile.profile_name }}
                    </option>
                  </select>
                  <span class="microcopy">Determines reader swarm size and warning constraints.</span>
                </label>
              </div>

              <label class="field-group textarea-group" :class="{ 'has-error': activeValidationFields.blurb }">
                <span class="label-text">Marketing Description / Blurb <span class="req">*</span></span>
                <textarea
                  v-model="form.blurb"
                  rows="4"
                  placeholder="Provide the jacket blurb or summary..."
                  aria-required="true"
                  @input="clearValidationError('blurb')"
                ></textarea>
                <span class="microcopy">Initial synopsis used to establish reader hooks.</span>
              </label>

              <!-- Collapsible Optional Metadata Fields -->
              <div class="optional-fields-container">
                <button 
                  type="button"
                  class="collapse-trigger-btn" 
                  @click="showOptionalBasics = !showOptionalBasics"
                  :aria-expanded="showOptionalBasics"
                  style="background: transparent; border: none; color: #ff4500; font-size: 0.82rem; font-weight: 600; cursor: pointer; padding: 4px 0; margin-top: 12px;"
                >
                  {{ showOptionalBasics ? '▼ Hide Optional Metadata' : '▶ Show Optional Metadata (Subtitle, Comps, Cover Brief)' }}
                </button>

                <div v-show="showOptionalBasics" class="optional-fields-grid" style="margin-top: 12px; display: flex; flex-direction: column; gap: 14px;">
                  <label class="field-group">
                    <span class="label-text">Book Subtitle</span>
                    <input v-model="form.subtitle" type="text" placeholder="e.g. A Novel of Pacing and Suspense" />
                  </label>

                  <label class="field-group">
                    <span class="label-text">Comp Titles</span>
                    <input v-model="form.compTitles" type="text" placeholder="e.g. Title A by Author X, Title B" />
                    <span class="microcopy">Comma-separated comparable works to calibrate reader expectations.</span>
                  </label>

                  <label class="field-group textarea-group" style="margin-top: 0;">
                    <span class="label-text">Cover Package Brief</span>
                    <textarea v-model="form.coverBrief" rows="3" placeholder="Describe mood, colors, typography ideas..."></textarea>
                  </label>
                </div>
              </div>
            </div>

            <!-- Right Side: Live Accuracy assessment checklist -->
            <aside class="checklist-col">
              <div class="sb-card accuracy-card" style="height: 100%; display: flex; flex-direction: column;">
                <h3>Simulation Fidelity Rating</h3>
                <p class="checklist-hint" style="font-size: 0.78rem; color: #64748b; margin: 0 0 16px 0;">Live evaluation of how setup options impact synthetic cohort prediction accuracy:</p>
                
                <ul class="accuracy-list-stack" style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 16px; flex: 1;">
                  <li class="accuracy-item-row" style="display: flex; gap: 12px; align-items: flex-start;">
                    <span class="status-indicator-badge" style="font-size: 1.2rem; line-height: 1;">{{ accuracyChecks.contentType.icon }}</span>
                    <div>
                      <strong style="font-size: 0.85rem; color: #0f172a; display: block;">Format Depth: {{ accuracyChecks.contentType.label }}</strong>
                      <span style="font-size: 0.72rem; color: #64748b; line-height: 1.3; display: block; margin-top: 2px;">{{ accuracyChecks.contentType.desc }}</span>
                    </div>
                  </li>

                  <li class="accuracy-item-row" style="display: flex; gap: 12px; align-items: flex-start;">
                    <span class="status-indicator-badge" style="font-size: 1.2rem; line-height: 1;">{{ accuracyChecks.metaCompleteness.icon }}</span>
                    <div>
                      <strong style="font-size: 0.85rem; color: #0f172a; display: block;">Synopsis Detail: {{ accuracyChecks.metaCompleteness.label }}</strong>
                      <span style="font-size: 0.72rem; color: #64748b; line-height: 1.3; display: block; margin-top: 2px;">{{ accuracyChecks.metaCompleteness.desc }}</span>
                    </div>
                  </li>

                  <li class="accuracy-item-row" style="display: flex; gap: 12px; align-items: flex-start;">
                    <span class="status-indicator-badge" style="font-size: 1.2rem; line-height: 1;">{{ accuracyChecks.profileAccuracy.icon }}</span>
                    <div>
                      <strong style="font-size: 0.85rem; color: #0f172a; display: block;">Cohort Resolution: {{ accuracyChecks.profileAccuracy.label }}</strong>
                      <span style="font-size: 0.72rem; color: #64748b; line-height: 1.3; display: block; margin-top: 2px;">{{ accuracyChecks.profileAccuracy.desc }}</span>
                    </div>
                  </li>

                  <li class="accuracy-item-row" style="display: flex; gap: 12px; align-items: flex-start;">
                    <span class="status-indicator-badge" style="font-size: 1.2rem; line-height: 1;">{{ accuracyChecks.privacyAccuracy.icon }}</span>
                    <div>
                      <strong style="font-size: 0.85rem; color: #0f172a; display: block;">Cognitive Reasoning: {{ accuracyChecks.privacyAccuracy.label }}</strong>
                      <span style="font-size: 0.72rem; color: #64748b; line-height: 1.3; display: block; margin-top: 2px;">{{ accuracyChecks.privacyAccuracy.desc }}</span>
                    </div>
                  </li>
                </ul>

                <div class="score-progress-box" style="margin-top: 24px; padding-top: var(--sb-space-4); border-top: 1px solid var(--sb-border-color);">
                  <div class="score-label-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px;">Fidelity Score</span>
                    <strong :style="{ color: accuracyChecks.scoreColor }" style="font-size: 0.95rem; font-weight: 800;">{{ accuracyChecks.scoreLabel }} ({{ accuracyChecks.score }}%)</strong>
                  </div>
                  <div class="fidelity-bar-rail" style="height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; width: 100%;">
                    <div class="fidelity-bar-fill" :style="{ width: accuracyChecks.score + '%', background: accuracyChecks.scoreColor }" style="height: 100%; transition: width 0.3s ease;"></div>
                  </div>
                </div>
              </div>
            </aside>
          </div>
        </section>

        <!-- STEP 2: UPLOAD MANUSCRIPT -->
        <section v-if="currentStep === 2" class="wizard-step-section">
          <h2>Step 02 / Upload Manuscript</h2>
          <p class="step-hint">Select your manuscript draft file (PDF, DOCX, TXT, or MD) to parse chapters locally.</p>

          <!-- Form Error Banner -->
          <div v-if="uploadError" class="validation-alert" role="alert" aria-live="polite">
            <span class="alert-hdr">Upload Error</span>
            <p>{{ uploadError }}</p>
            <button class="clear-err-btn" @click="uploadError = ''" style="background: transparent; border: none; color: #ef4444; font-size: 1.2rem; cursor: pointer; float: right;" aria-label="Dismiss error">&times;</button>
          </div>

          <!-- Drag & Drop Area -->
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
              <span class="upload-icon">📂</span>
              <h3>Drag &amp; drop manuscript here</h3>
              <p class="browse-link" style="color: #ff4500; font-weight: 600; margin: 4px 0 0 0;">or click to browse local folders</p>
              <span class="formats-label" style="display: block; font-size: 0.72rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 10px;">Supported formats: PDF, DOCX, TXT, MD</span>
            </div>

            <div class="selected-file-display" v-else style="display: flex; align-items: center; gap: 16px; text-align: left; width: 100%;">
              <span class="file-icon" style="font-size: 2.5rem;">📄</span>
              <div class="file-details">
                <h3 style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0 0 6px 0; word-break: break-all;">{{ form.manuscriptFilename }}</h3>
                <p class="file-meta" style="display: flex; gap: 8px; flex-wrap: wrap; margin: 0;">
                  <span class="meta-tag" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 4px; font-weight: 600;">{{ formatBytes(form.manuscriptSizeBytes) }}</span>
                  <span class="meta-tag" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 4px; font-weight: 600;" v-if="form.manuscriptMimeType">{{ form.manuscriptMimeType }}</span>
                  <span class="meta-tag word-badge" style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; font-weight: 600;" v-if="form.manuscriptWordCount">{{ form.manuscriptWordCount.toLocaleString() }} words</span>
                </p>
              </div>
            </div>
          </div>

          <!-- File Details & Warnings (Visible only when file is selected) -->
          <div class="file-meta-panel" v-if="form.manuscriptFilename" style="margin-top: 20px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 16px; text-align: left;">
            <div class="meta-section">
              <h4 style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase; margin: 0 0 4px 0; letter-spacing: 0.5px;">Estimated Processing Time</h4>
              <p class="meta-text" style="font-size: 0.85rem; color: #64748b; margin: 0;">~30 to 60 seconds on average local workstations (Ollama extraction loops).</p>
            </div>

            <div class="meta-section">
              <h4 style="font-size: 0.8rem; font-weight: 700; color: #475569; text-transform: uppercase; margin: 0 0 4px 0; letter-spacing: 0.5px;">Privacy Enforcement</h4>
              <div class="privacy-status-badge" :class="form.privacyMode" style="display: flex; gap: 12px; align-items: flex-start; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-top: 6px;">
                <span class="badge-icon" style="font-size: 1.2rem; line-height: 1;">🔒</span>
                <div>
                  <strong style="font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">{{ form.privacyMode }} mode active</strong>
                  <p style="font-size: 0.78rem; color: #64748b; margin: 2px 0 0 0; line-height: 1.4;" v-if="form.privacyMode === 'local_only'">Strictly offline. No manuscript content leaves your machine.</p>
                  <p style="font-size: 0.78rem; color: #64748b; margin: 2px 0 0 0; line-height: 1.4;" v-else-if="form.privacyMode === 'hybrid_safe'">Manuscript content is analyzed locally; embeddings map to secure offline structures.</p>
                  <p style="font-size: 0.78rem; color: #64748b; margin: 2px 0 0 0; line-height: 1.4;" v-else>Full cloud quality reasoning enabled. Safe encrypted processing is active.</p>
                </div>
              </div>
            </div>

            <div class="remove-action-row" style="display: flex; justify-content: flex-end;">
              <button class="remove-btn" @click.stop="clearFile" style="background: transparent; border: none; color: #ef4444; font-size: 0.82rem; font-weight: 600; cursor: pointer; padding: 4px 8px; border-radius: 4px;" aria-label="Remove uploaded manuscript file">
                ❌ Remove File
              </button>
            </div>
          </div>

          <!-- Collapsible Paste Manually option -->
          <div class="paste-collapse-container" style="margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 20px; text-align: left;">
            <button 
              type="button"
              class="collapse-trigger-btn" 
              @click="showPasteArea = !showPasteArea"
              :aria-expanded="showPasteArea"
              aria-controls="wizard-paste-textarea"
              style="background: transparent; border: none; color: #64748b; font-size: 0.82rem; font-weight: 600; cursor: pointer; padding: 4px 0;"
            >
              {{ showPasteArea ? '▼ Hide Manual Paste Option' : '▶ Or Paste Manuscript Content Manually' }}
            </button>

            <div id="wizard-paste-textarea" v-show="showPasteArea" class="paste-textarea-wrapper" style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px;">
              <label class="field-group textarea-group" :class="{ 'has-error': activeValidationFields.manuscriptText }">
                <span class="label-text">Paste Draft Text Content</span>
                <textarea
                  v-model="form.manuscriptText"
                  rows="10"
                  placeholder="Paste raw manuscript chapters here..."
                  @input="onPasteInput"
                ></textarea>
              </label>
              <div class="char-count-row" style="display: flex; justify-content: space-between; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: #64748b; margin-top: 4px;">
                <span :class="{ 'warn-text': isManuscriptTooLarge }">
                  {{ form.manuscriptText.length.toLocaleString() }} characters
                </span>
                <span v-if="isManuscriptTooLarge" class="limit-warning" style="color: #b45309; font-weight: 600;">
                  ⚠️ Large draft: Consider an excerpt of 1-3 chapters for faster local processing.
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- STEP 3: EVIDENCE PACK PREVIEW -->
        <section v-if="currentStep === 3" class="wizard-step-section">
          <h2>Step 03 / Compiled Evidence Metrics</h2>
          <p class="step-hint">Review compiled manuscript maps and DNA before triggering simulated readers.</p>

          <div class="evidence-tabs" v-if="evidencePack">
            <div class="tabs-header">
              <button
                v-for="tab in evidenceTabs"
                :key="tab.id"
                class="tab-btn"
                :class="{ active: activeEvidenceTab === tab.id }"
                @click="activeEvidenceTab = tab.id"
              >
                {{ tab.label }}
              </button>
            </div>

            <!-- Tab Contents -->
            <div class="tab-body">
              <div v-if="activeEvidenceTab === 'dna'" class="tab-pane">
                <h3>Book DNA</h3>
                <div class="meta-display">
                  <p><strong>Title:</strong> {{ evidencePack.book_dna?.title }}</p>
                  <p><strong>Genre:</strong> {{ evidencePack.book_dna?.genre }}</p>
                  <p><strong>Target:</strong> {{ evidencePack.book_dna?.target_reader }}</p>
                  <p><strong>Premise Summary:</strong></p>
                  <blockquote class="premise-quote">{{ evidencePack.book_dna?.premise }}</blockquote>
                </div>
              </div>

              <div v-if="activeEvidenceTab === 'chapters'" class="tab-pane">
                <h3>Parsed Chapters</h3>
                <ul class="stepper-list">
                  <li v-for="ch in evidencePack.chapter_map?.chapters || []" :key="ch.chapter_id">
                    <strong>Ch {{ ch.chapter_number }}: {{ ch.title || 'Untitled' }}</strong>
                    <p>{{ ch.summary }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="activeEvidenceTab === 'characters'" class="tab-pane">
                <h3>Character Profiles</h3>
                <ul class="stepper-list">
                  <li v-for="char in evidencePack.character_map?.characters || []" :key="char.character_id">
                    <strong>{{ char.name }} ({{ char.role || 'Secondary' }})</strong>
                    <p>Frictions: {{ char.reader_friction?.join(', ') || 'None noted' }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="activeEvidenceTab === 'risks'" class="tab-pane">
                <h3>Discovered Narrative Risks</h3>
                <ul class="stepper-list">
                  <li v-for="risk in evidencePack.risk_map?.risks || []" :key="risk.risk_id">
                    <strong class="risk-badge">{{ risk.risk_type }}</strong>
                    <p>{{ risk.description || risk.mitigation_hint }}</p>
                  </li>
                </ul>
              </div>

              <div v-if="activeEvidenceTab === 'style'" class="tab-pane">
                <h3>Style Calibration</h3>
                <div class="meta-display">
                  <p><strong>Clarity Rating:</strong> {{ evidencePack.style_map?.clarity }}</p>
                  <p><strong>Narrative Rhythm:</strong> {{ evidencePack.style_map?.rhythm }}</p>
                  <p><strong>Quoteability Index:</strong> {{ evidencePack.style_map?.quoteability }}</p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>No evidence pack has been compiled. Click back and verify manuscript text.</p>
          </div>
        </section>

        <!-- STEP 4: READER SWARM CONFIG -->
        <section v-if="currentStep === 4" class="wizard-step-section">
          <h2>Step 04 / Reader Swarm Setup</h2>
          <p class="step-hint">Configure simulated reader cohorts, select platform surfaces, and define privacy and scale boundaries.</p>

          <!-- 4.1 Profile Selection -->
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
                  <span class="profile-icon">{{ profile.profile_name === 'local_tiny' ? '⚡' : profile.profile_name === 'hybrid_safe_default' ? '⚖️' : '🔮' }}</span>
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

          <!-- 4.2 Reader Count -->
          <div class="field-group">
            <label class="slider-label-row" for="wizard-reader-slider">
              <span class="label-text">Total Simulated Readers</span>
              <strong class="count-indicator">{{ form.personaCount }} personas</strong>
            </label>
            <div class="slider-wrapper">
              <input
                id="wizard-reader-slider"
                v-model.number="form.personaCount"
                type="range"
                min="2"
                max="80"
                class="premium-slider"
              />
              <div class="slider-marks">
                <span>2</span>
                <span>12 (Tiny)</span>
                <span>30 (Standard)</span>
                <span>60 (Deep)</span>
                <span>80</span>
              </div>
            </div>
            <span class="microcopy">Profile default: {{ selectedProfile?.max_personas || 30 }} personas. Slower hardware: target 12-20 readers.</span>
          </div>

          <!-- 4.3 Platforms Checklist -->
          <div class="field-group">
            <span class="label-text">Simulated Platforms Checklist <span class="req">*</span></span>
            <div class="platforms-checkbox-grid">
              <button
                v-for="platform in platformOptionsList"
                :key="platform"
                type="button"
                class="platform-pill-btn"
                :class="{ active: form.platforms.includes(platform) }"
                @click="togglePlatformCheckbox(platform)"
              >
                <span class="platform-icon">
                  {{ platform === 'goodreads' ? '📚' : platform === 'booktok' ? '🎵' : platform === 'reddit' ? '👽' : platform === 'bookstagram' ? '📸' : platform === 'x' ? '🐦' : platform === 'newsletter' ? '✉️' : '👥' }}
                </span>
                <span class="platform-name">
                  {{ platform === 'goodreads' ? 'Goodreads' : platform === 'booktok' ? 'BookTok' : platform === 'reddit' ? 'Reddit' : platform === 'bookstagram' ? 'Bookstagram' : platform === 'x' ? 'X (Twitter)' : platform === 'newsletter' ? 'Newsletter' : 'Book Club' }}
                </span>
              </button>
            </div>
          </div>

          <!-- 4.4 Reader Cohorts -->
          <div class="field-group">
            <span class="label-text">Active Reader Cohorts</span>
            <div class="cohorts-header-actions">
              <button type="button" class="action-link-btn" @click="disabledCohorts = []">Select All</button>
              <span class="bullet-divider">•</span>
              <button type="button" class="action-link-btn" @click="disabledCohorts = cohortOptions.map(c => c.id)">Clear All</button>
            </div>
            <div class="cohorts-selection-list">
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

          <!-- 4.5 Seed and Privacy Mode details -->
          <div class="form-grid">
            <label class="field-group">
              <span class="label-text">Deterministic Seed</span>
              <input v-model.number="form.simulationSeed" type="number" min="0" class="premium-input text-center" />
              <span class="microcopy">Ensures identical cohort reactions across draft iterations.</span>
            </label>

            <div class="field-group">
              <span class="label-text">Active Privacy Mode</span>
              <div class="privacy-status-block" :class="form.privacyMode" style="margin: 0; padding: 12px;">
                <span class="lock-symbol" style="font-size: 1.1rem; margin-right: 8px;">🔒</span>
                <span style="font-size: 0.85rem; font-weight: 700; text-transform: capitalize;">{{ form.privacyMode }}</span>
                <p class="privacy-explanation-text" style="font-size: 0.75rem; margin-top: 4px;">
                  {{ form.privacyMode === 'local_only' ? 'Strictly offline Ollama.' : form.privacyMode === 'hybrid_safe' ? 'Local run with cloud embeddings.' : 'Cloud model reasoning.' }}
                </p>
              </div>
            </div>
          </div>

          <!-- System Warnings Banner Stack -->
          <div v-if="(customWarnings.length || selectedProfileWarnings.length) && isProfileOrPrivacyChanged" class="alert-banners-stack" style="margin-top: 20px;">
            <div 
              v-for="warning in [...selectedProfileWarnings, ...customWarnings]" 
              :key="warning.code + warning.message" 
              class="setup-warning-banner"
            >
              <span class="warning-icon">⚠️</span>
              <p class="warning-message">{{ warning.message }}</p>
            </div>
          </div>
        </section>

        <!-- STEP 5: RUN SIMULATION SUMMARY -->
        <section v-if="currentStep === 5" class="wizard-step-section">
          <h2>Step 05 / Run Manuscript Stress Test</h2>
          <p class="step-hint">Review configuration parameters before triggering cohort reading pass.</p>

          <div class="summary-card">
            <h3>Stress Test Configuration</h3>
            <div class="summary-details">
              <div class="row">
                <span class="lbl">Content Title:</span>
                <span class="val">{{ form.title }}</span>
              </div>
              <div class="row">
                <span class="lbl">Content Type:</span>
                <span class="val" style="text-transform: capitalize;">{{ form.contentType?.replace('_', ' ') }}</span>
              </div>
              <div class="row">
                <span class="lbl">Test Goal:</span>
                <span class="val">{{ form.testGoal }}</span>
              </div>
              <div class="row">
                <span class="lbl">Author:</span>
                <span class="val">{{ form.authorName }}</span>
              </div>
              <div class="row">
                <span class="lbl">Simulation Profile:</span>
                <span class="val">{{ form.localProfile }}</span>
              </div>
              <div class="row">
                <span class="lbl">Privacy Mode:</span>
                <span class="val" style="text-transform: capitalize;">{{ form.privacyMode }}</span>
              </div>
              <div class="row">
                <span class="lbl">Swarm Cohort Size:</span>
                <span class="val">{{ form.personaCount }} simulated personas</span>
              </div>
              <div class="row">
                <span class="lbl">Platforms:</span>
                <span class="val" style="text-transform: capitalize;">{{ form.platforms.join(', ') }}</span>
              </div>
              <div class="row">
                <span class="lbl">Active Reader Cohorts:</span>
                <span class="val">{{ cohortOptions.length - disabledCohorts.length }} of {{ cohortOptions.length }} active</span>
              </div>
              <div class="row">
                <span class="lbl">Seed Parameter:</span>
                <span class="val">{{ form.simulationSeed }}</span>
              </div>
              <div class="row">
                <span class="lbl">Estimated Run Time:</span>
                <span class="val" style="color: #ff4500; font-weight: 700;">{{ formattedEstimatedTime }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Navigation Action Buttons -->
        <footer class="wizard-actions">
          <button class="ghost-btn" :disabled="currentStep === 1 || submitting" @click="prevStep">
            ← Back
          </button>
          <button class="primary-btn" :disabled="submitting" @click="nextStep">
            <span v-if="currentStep < 5">Next Step →</span>
            <span v-else>{{ submitting ? 'Running Simulation...' : 'Trigger Simulation 🚀' }}</span>
          </button>
        </footer>
      </div>
    </div>
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

const steps = [
  { num: 1, label: 'Basics' },
  { num: 2, label: 'Upload' },
  { num: 3, label: 'Evidence Map' },
  { num: 4, label: 'Reader Swarm' },
  { num: 5, label: 'Run' },
]

const evidenceTabs = [
  { id: 'dna', label: 'Book DNA' },
  { id: 'chapters', label: 'Chapters' },
  { id: 'characters', label: 'Characters' },
  { id: 'risks', label: 'Risks' },
  { id: 'style', label: 'Style Calibration' },
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

const accuracyChecks = computed(() => {
  const checks = {
    contentType: { label: 'Good', desc: '', status: 'ok', icon: '✅' },
    metaCompleteness: { label: 'Missing', desc: '', status: 'error', icon: '❌' },
    profileAccuracy: { label: 'Standard', desc: '', status: 'ok', icon: '✅' },
    privacyAccuracy: { label: 'Standard', desc: '', status: 'ok', icon: '✅' },
    score: 0,
    scoreLabel: 'Minimal',
    scoreColor: 'var(--sb-color-offline)',
  }

  // 1. Content Type
  const cType = form.contentType
  if (['full_manuscript', 'novel', 'novella'].includes(cType)) {
    checks.contentType = {
      label: 'Maximum Depth',
      desc: 'Full-length narrative structures allow complete cohort simulation.',
      status: 'ok',
      icon: '✅',
      value: 25,
    }
  } else if (['chapter_sample', 'research_pack', 'book_proposal'].includes(cType)) {
    checks.contentType = {
      label: 'High Depth',
      desc: 'Partial structure helps check pacing and key narrative themes.',
      status: 'info',
      icon: 'ℹ️',
      value: 20,
    }
  } else if (['short_story', 'article_essay', 'newsletter'].includes(cType)) {
    checks.contentType = {
      label: 'Medium Depth',
      desc: 'Shorter content has smaller platform reaction surface.',
      status: 'warn',
      icon: '⚠️',
      value: 15,
    }
  } else { // blurb_synopsis
    checks.contentType = {
      label: 'Jacket Only',
      desc: 'Jumps directly to hook feedback; no deeper pacing audits possible.',
      status: 'warn',
      icon: '⚠️',
      value: 10,
    }
  }

  // 2. Blurb Length
  const bLength = (form.blurb || '').trim().length
  if (bLength === 0) {
    checks.metaCompleteness = {
      label: 'Empty',
      desc: 'Jacket description is required to establish core hook context.',
      status: 'error',
      icon: '❌',
      value: 0,
    }
  } else if (bLength < 100) {
    checks.metaCompleteness = {
      label: 'Too Short',
      desc: 'Description under 100 chars limits initial persona hook calibration.',
      status: 'warn',
      icon: '⚠️',
      value: 10,
    }
  } else if (bLength < 300) {
    checks.metaCompleteness = {
      label: 'Acceptable',
      desc: 'Sufficient context, but richer synopsis will improve reader alignments.',
      status: 'info',
      icon: 'ℹ️',
      value: 20,
    }
  } else {
    checks.metaCompleteness = {
      label: 'Rich Synopsis',
      desc: 'Detailed premise gives simulated cohorts strong setup signals.',
      status: 'ok',
      icon: '✅',
      value: 25,
    }
  }

  // 3. Profile
  const prof = form.localProfile
  if (prof === 'cloud_quality') {
    checks.profileAccuracy = {
      label: 'High (60 Cohorts)',
      desc: 'Maximum statistical coverage for platforms and cohorts.',
      status: 'ok',
      icon: '✅',
      value: 25,
    }
  } else if (prof === 'hybrid_safe_default') {
    checks.profileAccuracy = {
      label: 'Balanced (30 Cohorts)',
      desc: 'Standard cohort set covers typical platform spreads.',
      status: 'ok',
      icon: '✅',
      value: 20,
    }
  } else { // local_tiny
    checks.profileAccuracy = {
      label: 'Minimal (12 Cohorts)',
      desc: 'Fast checkout, but reduced platform and feedback resolution.',
      status: 'warn',
      icon: '⚠️',
      value: 10,
    }
  }

  // 4. Privacy/Reasoning
  const priv = form.privacyMode
  if (priv === 'cloud_quality') {
    checks.privacyAccuracy = {
      label: 'Cloud Cognitive',
      desc: 'Advanced reasoning models capture nuanced subtext and stylistic friction.',
      status: 'ok',
      icon: '✅',
      value: 25,
    }
  } else if (priv === 'hybrid_safe') {
    checks.privacyAccuracy = {
      label: 'Hybrid Standard',
      desc: 'Combines local LLM simulation with cloud-calibrated embeddings.',
      status: 'info',
      icon: 'ℹ️',
      value: 20,
    }
  } else { // local_only
    checks.privacyAccuracy = {
      label: 'Local Only',
      desc: 'Workstation-limited offline models. Reduced stylistic subtext resolution.',
      status: 'warn',
      icon: '⚠️',
      value: 15,
    }
  }

  // Compute overall score
  checks.score = checks.contentType.value + checks.metaCompleteness.value + checks.profileAccuracy.value + checks.privacyAccuracy.value

  if (checks.score >= 85) {
    checks.scoreLabel = 'Production Grade'
    checks.scoreColor = 'var(--sb-color-ready)'
  } else if (checks.score >= 65) {
    checks.scoreLabel = 'High Fidelity'
    checks.scoreColor = 'var(--sb-color-info)'
  } else if (checks.score >= 45) {
    checks.scoreLabel = 'Medium Fidelity'
    checks.scoreColor = 'var(--sb-color-mixed)'
  } else {
    checks.scoreLabel = 'Low Fidelity'
    checks.scoreColor = 'var(--sb-color-offline)'
  }

  return checks
})

const estimatedTimeSec = computed(() => {
  const count = form.personaCount || 0
  let perPersona = 2.0
  if (form.localProfile === 'local_tiny') perPersona = 1.2
  else if (form.localProfile === 'hybrid_safe_default') perPersona = 2.8
  else if (form.localProfile === 'cloud_quality') perPersona = 4.5

  return Math.ceil(count * perPersona)
})

const formattedEstimatedTime = computed(() => {
  const sec = estimatedTimeSec.value
  if (sec < 60) return `~${sec} seconds`
  const min = Math.floor(sec / 60)
  const remainingSec = sec % 60
  if (remainingSec === 0) return `~${min} min`
  return `~${min} min ${remainingSec} sec`
})

const customWarnings = computed(() => {
  const list = []
  if (form.localProfile === 'cloud_quality') {
    list.push({
      code: 'heavy_cloud',
      message: 'Cloud Quality profile uploads manuscript chunks to external APIs. Ensure Gemini and NVIDIA keys are configured in your local environment.'
    })
  }
  if (form.personaCount > 40 && form.privacyMode === 'local_only') {
    list.push({
      code: 'high_local_load',
      message: 'Configuring more than 40 personas on a local profile may cause heavy CPU/GPU memory load on standard 16GB RAM workstations. Consider reducing reader count to 12-20.'
    })
  }
  return list
})

const form = reactive({
  // Step 1 Basics
  projectName: session.value.metadata.projectName || '',
  title: session.value.metadata.title || '',
  authorName: session.value.metadata.authorName || '',
  bookType: session.value.metadata.bookType || 'fiction',
  genre: session.value.metadata.genre || '',
  targetReader: session.value.metadata.targetReader || '',
  subtitle: session.value.metadata.subtitle || '',
  privacyMode: session.value.metadata.privacyMode || 'hybrid_safe',
  localProfile: session.value.metadata.localProfile || 'hybrid_safe_default',
  blurb: session.value.metadata.blurb || '',
  compTitles: session.value.metadata.compTitles || '',
  coverBrief: session.value.metadata.coverBrief || '',
  contentType: session.value.metadata.contentType || 'novel',
  testGoal: session.value.metadata.testGoal || '',
  // Step 2 Ingest
  manuscriptText: session.value.manuscript.text || '',
  manuscriptFilename: session.value.manuscript.filename || '',
  manuscriptLanguage: session.value.manuscript.language || 'en',
  manuscriptSizeBytes: session.value.manuscript.sizeBytes || 0,
  manuscriptMimeType: session.value.manuscript.mimeType || '',
  manuscriptWordCount: session.value.manuscript.wordCount || 0,
  // Step 4 Swarm Config
  platforms: [...(session.value.simulationConfig.platforms || ['goodreads', 'reddit', 'booktok'])],
  personaCount: session.value.simulationConfig.personaCount || 30,
  simulationSeed: session.value.simulationConfig.simulationSeed ?? 17,
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
  if (items.length) {
    return items
  }
  return [
    { profile_name: 'local_tiny', privacy_mode: 'local_only', max_personas: 12, platforms: ['goodreads', 'reddit', 'x'], computed_warnings: [] },
    { profile_name: 'hybrid_safe_default', privacy_mode: 'hybrid_safe', max_personas: 30, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x'], computed_warnings: [] },
    { profile_name: 'cloud_quality', privacy_mode: 'cloud_quality', max_personas: 60, platforms: ['goodreads', 'reddit', 'booktok', 'bookstagram', 'x', 'newsletter', 'bookclub'], computed_warnings: [] },
  ]
})

function canJumpTo(stepNum) {
  if (stepNum === 1) return true
  if (stepNum === 2) return !!(form.projectName && form.title && form.authorName && form.genre && form.targetReader && form.testGoal && form.blurb)
  if (stepNum === 3) return canJumpTo(2) && !!form.manuscriptText
  if (stepNum === 4) return canJumpTo(3) && !!evidencePack.value
  if (stepNum === 5) return canJumpTo(4) && form.platforms.length > 0
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
    },
    simulationConfig: {
      profileName: form.localProfile,
      personaCount: form.personaCount,
      platforms: form.platforms,
      privacyMode: form.privacyMode,
      simulationSeed: form.simulationSeed,
      disabledCohorts: [...disabledCohorts.value],
    },
  })
}

// Watch block for dynamic real-time autosave
watch(form, () => {
  saveState()
}, { deep: true })

function validateStep1() {
  validationErrors.value = []
  let ok = true

  const fields = [
    { key: 'projectName', label: 'Project reference name' },
    { key: 'title', label: 'Content title' },
    { key: 'authorName', label: 'Author name' },
    { key: 'genre', label: 'Genre / Category' },
    { key: 'targetReader', label: 'Target reader' },
    { key: 'testGoal', label: 'Test goal' },
    { key: 'blurb', label: 'Synopsis / Blurb description' },
  ]
  for (const f of fields) {
    if (!form[f.key] || !form[f.key].trim()) {
      activeValidationFields[f.key] = true
      validationErrors.value.push(`Missing required editorial field: ${f.label}`)
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
    validationErrors.value.push('Please load or paste your manuscript content.')
    return false
  }
  activeValidationFields.manuscriptText = false
  return true
}

function triggerFileBrowser() {
  fileInput.value?.click()
}

const uploadError = ref('')
const showPasteArea = ref(false)

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
  if (file) {
    handleFileUpload(file)
  }
}

function onFileDrop(event) {
  dragOver.value = false
  const file = event.dataTransfer.files?.[0]
  if (file) {
    handleFileUpload(file)
  }
}

async function handleFileUpload(file) {
  uploadError.value = ''
  error.value = ''
  
  // Extension check
  const allowed = ['.txt', '.md', '.markdown', '.pdf', '.docx']
  const matched = allowed.some(ext => file.name.toLowerCase().endsWith(ext))
  if (!matched) {
    uploadError.value = `Unsupported file format. Please upload a .pdf, .docx, .txt, or .md document.`
    return
  }

  // Pre-upload file size limit — shared constant (40 MB)
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
    
    saveState()
  } catch (err) {
    const apiError = err.response?.data
    if (apiError && apiError.error_code === 'file_too_large') {
      const details = apiError.details
      if (details.unit === 'characters') {
        uploadError.value = `File too large: parsed manuscript (${details.actual_size.toLocaleString()} characters) exceeds the maximum allowed limit of ${details.max_size.toLocaleString()} characters (Oversized by ${details.oversized_absolute.toLocaleString()} characters / ${details.oversized_percentage.toFixed(1)}%).`
      } else {
        uploadError.value = `File too large: file size (${formatBytes(details.actual_size)}) exceeds the maximum allowed limit of ${formatBytes(details.max_size)} (Oversized by ${formatBytes(details.oversized_absolute)} / ${details.oversized_percentage.toFixed(1)}%).`
      }
    } else {
      uploadError.value = apiError?.error || `Upload/parsing failed: ${err.message}`
    }
  } finally {
    loadingMessage.value = ''
  }
}

async function nextStep() {
  if (currentStep.value === 1) {
    if (validateStep1()) {
      saveState()
      currentStep.value = 2
    }
  } else if (currentStep.value === 2) {
    if (validateStep2()) {
      saveState()
      await buildEvidencePackStep()
    }
  } else if (currentStep.value === 3) {
    currentStep.value = 4
  } else if (currentStep.value === 4) {
    if (form.platforms.length === 0) {
      validationErrors.value = ['Please select at least one simulated channel.']
      return
    }
    validationErrors.value = []
    currentStep.value = 5
  } else if (currentStep.value === 5) {
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

async function buildEvidencePackStep() {
  submitting.value = true
  loadingMessage.value = 'Creating metadata and building editorial evidence packs...'
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

    currentStep.value = 3
  } catch (err) {
    error.value = err.message
  } finally {
    loadingMessage.value = ''
    submitting.value = false
  }
}

function runCohortSimulation() {
  saveState()
  router.push({ name: 'SwarmbookSimulationRun', params: { projectId: session.value.projectId } })
}

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
  // Sync exclusions from session
  const storedDisabled = session.value.simulationConfig?.disabledCohorts
  if (storedDisabled) {
    disabledCohorts.value = [...storedDisabled]
  }
  // Resume wizard at Step 2 or 3 if project is already active in session
  if (props.projectId && props.projectId !== 'new' && session.value.projectId === props.projectId) {
    if (session.value.evidencePack) {
      currentStep.value = 3
    } else if (session.value.manuscript?.text) {
      currentStep.value = 2
    }
  }
})
</script>

<style scoped>
/* Scoped wizard UI style overrides */

.wizard-container {
  max-width: 960px;
  margin: 0 auto;
}

/* Stepper Ribbon style */
.wizard-stepper {
  display: flex;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 20px;
  margin-bottom: 24px;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stepper-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 600;
  transition: color 0.2s;
  outline: none;
}

.stepper-item:focus-visible {
  outline: 2px solid #ff4500;
  border-radius: 4px;
}

.stepper-item.active {
  color: #ff4500;
}

.stepper-item.completed {
  color: #10b981;
}

.stepper-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.step-num-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid currentColor;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
}

.chevron {
  font-size: 1.2rem;
  margin-left: 10px;
  color: #cbd5e1;
}

.wizard-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}

/* Steps design details */
.wizard-step-section h2 {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.step-hint {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0 0 24px 0;
}

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

.field-group.textarea-group {
  margin-top: 20px;
}

.field-group.has-error input,
.field-group.has-error textarea {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.label-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: #475569;
}

.req {
  color: #ef4444;
}

.microcopy {
  font-size: 0.72rem;
  color: #94a3b8;
  line-height: 1.4;
  margin-top: 2px;
}

/* Upload style */
.wizard-upload-zone {
  border: 2px dashed #cbd5e1;
  background: #f8fafc;
  padding: 32px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 24px;
}

.wizard-upload-zone:hover {
  border-color: #ff4500;
  background: #fff5ef;
}

.upload-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.wizard-upload-zone h3 {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 4px 0;
}

.wizard-upload-zone p {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
}

.hidden-input {
  display: none;
}

.char-count-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  margin-top: 6px;
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
}

.warn-text {
  color: #b45309;
  font-weight: 700;
}

.limit-warning {
  color: #b45309;
  font-weight: 600;
}

/* Tab details for step 3 */
.tabs-header {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.tab-btn {
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 10px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  outline: none;
}

.tab-btn.active {
  border-bottom-color: #ff4500;
  color: #ff4500;
}

.tab-body {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
  min-height: 250px;
}

.meta-display p {
  font-size: 0.88rem;
  line-height: 1.6;
  margin: 0 0 10px 0;
}

.premise-quote {
  border-left: 3px solid #cbd5e1;
  padding-left: 12px;
  margin: 10px 0;
  font-style: italic;
  color: #475569;
}

.stepper-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stepper-list li {
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 12px;
}

.stepper-list li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.stepper-list strong {
  font-size: 0.9rem;
  color: #0f172a;
  display: block;
  margin-bottom: 4px;
}

.risk-badge {
  background: #fee2e2;
  color: #991b1b;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  display: inline-block !important;
}

/* Checklist style */
.checkbox-group {
  margin-top: 20px;
}

.checkbox-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.pill-checkbox {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.pill-checkbox.active {
  background: #fff5ef;
  border-color: #ff4500;
  color: #ff4500;
}

.pill-checkbox:focus-visible {
  outline: 2px solid #ff4500;
}

/* Summary view step 5 */
.summary-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
}

.summary-card h3 {
  font-size: 1rem;
  margin: 0 0 16px 0;
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-details .row {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 10px;
  font-size: 0.88rem;
}

.summary-details .row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.summary-details .lbl {
  color: #64748b;
  font-weight: 500;
}

.summary-details .val {
  font-weight: 700;
  color: #0f172a;
}

/* Wizard buttons */
.wizard-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

/* Alert styles */
.validation-alert {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  color: #991b1b;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.alert-hdr {
  font-weight: 700;
  font-size: 0.88rem;
  display: block;
  margin-bottom: 6px;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
}

.validation-alert ul {
  margin: 0;
  padding-left: 20px;
  font-size: 0.8rem;
  line-height: 1.5;
}

/* Responsive grid */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .wizard-stepper {
    flex-wrap: wrap;
    gap: 10px;
  }
}

/* Swarm config step styling */
.profile-cards-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.profile-selection-card {
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  background: #ffffff;
  transition: all 0.2s ease-in-out;
  outline: none;
}

.profile-selection-card:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.profile-selection-card:focus-visible {
  outline: 2px solid #ff4500;
  border-color: #ff4500;
}

.profile-selection-card.active {
  border-color: #ff4500;
  background: #fffaf7;
}

.profile-card-header {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 6px;
}

.profile-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.profile-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex: 1;
  flex-wrap: wrap;
  gap: 6px;
}

.profile-title-row h3 {
  font-size: 0.95rem;
  font-weight: 800;
  margin: 0;
  color: #0f172a;
}

.recommendation-badge {
  font-size: 0.72rem;
  font-weight: 800;
  background: #ffebdf;
  color: #e63e00;
  padding: 2px 8px;
  border-radius: 9999px;
  text-transform: uppercase;
}

.profile-desc {
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.4;
  margin: 0 0 10px 0;
}

.profile-meta-chips {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.slider-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.count-indicator {
  font-size: 1.1rem;
  color: #ff4500;
  font-weight: 800;
}

.slider-wrapper {
  margin-bottom: 6px;
}

.premium-slider {
  width: 100%;
  height: 6px;
  background: #cbd5e1;
  border-radius: 9999px;
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.premium-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ff4500;
  cursor: pointer;
  transition: transform 0.1s;
}

.premium-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.premium-slider:focus-visible::-webkit-slider-thumb {
  box-shadow: 0 0 0 3px rgba(255, 69, 0, 0.4);
}

.slider-marks {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  padding: 4px 2px 0 2px;
}

.platforms-checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
}

.platform-pill-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
  transition: all 0.15s ease-in-out;
}

.platform-pill-btn:hover {
  border-color: #94a3b8;
  background: #f8fafc;
}

.platform-pill-btn.active {
  border-color: #ff4500;
  background: #fff5ef;
  color: #e63e00;
  box-shadow: 0 0 0 1px #ff4500;
}

.platform-pill-btn:focus-visible {
  outline: 2px solid #ff4500;
}

.platform-icon {
  font-size: 1.1rem;
}

.cohorts-header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.8rem;
}

.action-link-btn {
  background: transparent;
  border: none;
  color: #ff4500;
  font-weight: 700;
  cursor: pointer;
  padding: 2px 4px;
  font: inherit;
  font-size: 0.8rem;
}

.action-link-btn:hover {
  text-decoration: underline;
}

.bullet-divider {
  color: #cbd5e1;
}

.cohorts-selection-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cohort-checkbox-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  cursor: pointer;
  transition: border-color 0.2s;
}

.cohort-checkbox-card:hover {
  border-color: #cbd5e1;
}

.cohort-checkbox-card.checked {
  border-color: #ff4500;
  background: #ffffff;
}

.premium-checkbox {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid #cbd5e1;
  accent-color: #ff4500;
  margin-top: 2px;
}

.cohort-text-block {
  flex: 1;
}

.cohort-label {
  display: block;
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 3px;
}

.cohort-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin: 0;
  line-height: 1.3;
}

.privacy-status-block {
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #cbd5e1;
}

.privacy-status-block.local_only {
  background: #ecfdf5;
  border-color: #10b981;
}

.privacy-status-block.hybrid_safe {
  background: #eff6ff;
  border-color: #3b82f6;
}

.privacy-status-block.cloud_quality {
  background: #fef3c7;
  border-color: #f59e0b;
}

.privacy-explanation-text {
  font-size: 0.8rem;
  color: #475569;
  line-height: 1.4;
  margin: 0;
}

.premium-input {
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 6px 10px;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  outline: none;
}

.premium-input:focus {
  border-color: #ff4500;
  box-shadow: 0 0 0 1px #ff4500;
}

.text-center {
  text-align: center;
}

.alert-banners-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setup-warning-banner {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 6px;
  align-items: flex-start;
}

.warning-icon {
  font-size: 1rem;
  margin-top: 1px;
}

.warning-message {
  font-size: 0.78rem;
  color: #92400e;
  line-height: 1.3;
  margin: 0;
}

/* Step 1 Launch Basics Custom Layout Styles */
.step1-layout {
  display: grid;
  grid-template-columns: 2.2fr 1fr;
  gap: var(--sb-space-6);
  align-items: stretch;
}

.form-fields-col {
  display: flex;
  flex-direction: column;
}

.checklist-col {
  display: flex;
  flex-direction: column;
}

.accuracy-card {
  border: 1px solid var(--sb-border-color);
  border-radius: var(--sb-radius-xl);
  background: var(--sb-bg-card);
  padding: var(--sb-space-5);
  box-shadow: var(--sb-shadow-sm);
}

.accuracy-card h3 {
  font-size: var(--sb-text-md);
  font-weight: var(--sb-weight-bold);
  color: var(--sb-text-heading);
  margin: 0 0 var(--sb-space-3) 0;
}

.accuracy-list-stack {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--sb-space-4);
}

.accuracy-item-row {
  display: flex;
  gap: var(--sb-space-3);
  align-items: flex-start;
}

.status-indicator-badge {
  font-size: var(--sb-text-xl);
  line-height: 1;
}

.accuracy-item-row strong {
  font-size: var(--sb-text-sm);
  color: var(--sb-text-heading);
  font-weight: var(--sb-weight-bold);
}

.accuracy-item-row span {
  font-size: var(--sb-text-xs);
  color: var(--sb-text-muted);
  line-height: var(--sb-leading-relaxed);
}

.score-progress-box {
  margin-top: auto;
  padding-top: var(--sb-space-4);
  border-top: 1px solid var(--sb-border-color);
}

.score-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sb-space-2);
}

.fidelity-bar-rail {
  height: 8px;
  background: var(--sb-surface-secondary);
  border-radius: var(--sb-radius-full);
  overflow: hidden;
}

.fidelity-bar-fill {
  height: 100%;
  border-radius: var(--sb-radius-full);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.optional-fields-container {
  margin-top: var(--sb-space-4);
  border-top: 1px solid var(--sb-border-color);
  padding-top: var(--sb-space-3);
}

@media (max-width: 900px) {
  .step1-layout {
    grid-template-columns: 1fr;
    gap: var(--sb-space-5);
  }
}
</style>
