<template>
  <SwarmbookAppShell
    active-route="SwarmbookReport"
    :project-id="session.projectId"
    title="Report"
    subtitle=""
    :error-message="error"
    :loading-message="loadingMessage"
  >

    <!-- =====================================================================
         STICKY REPORT BAR
    ====================================================================== -->
    <div class="report-bar sticky-report-bar" v-if="report" role="banner" aria-label="Report header bar">
      <div class="report-bar-identity">
        <span class="report-bar-title">{{ report.title || report.project_id || 'Untitled Project' }}</span>
        <span class="report-bar-meta">
          <span class="meta-chip" :class="report.privacy_mode">🔒 {{ formatPrivacyMode(report.privacy_mode) }}</span>
          <span class="meta-chip draft">📄 {{ report.draft_id || 'Draft v1' }}</span>
          <span class="meta-chip confidence">🎯 {{ Math.round((report.confidence || 0) * 100) }}% Confidence</span>
          <span class="meta-chip" v-if="session.metadata?.contentType">{{ session.metadata.contentType.replace(/_/g,' ') }}</span>
        </span>
      </div>
      <div class="report-bar-actions">
        <button class="rb-btn" @click="router.push({ name: 'SwarmbookPersonas', params: { projectId: session.projectId } })" aria-label="Go to Persona Interrogation">💬 Ask Readers</button>
        <button class="rb-btn" @click="router.push({ name: 'SwarmbookCompare', params: { projectId: session.projectId } })" aria-label="Go to Draft Comparison">🔄 Compare</button>
        <button class="rb-btn rb-primary" @click="activeTab = 'exports'" aria-label="Open exports tab">📤 Export</button>
      </div>
    </div>

    <!-- =====================================================================
         ABOVE-FOLD COMMAND CENTER
    ====================================================================== -->
    <section v-if="report" class="command-center" aria-label="Publishing Command Center">
      <!-- Row 1: 6 metric cards -->
      <div class="cc-metrics-grid">

        <article class="cc-card cc-readiness" :class="readinessTone" aria-label="Publishing Readiness">
          <span class="cc-label">Publishing Readiness</span>
          <div class="cc-score">
            <strong>{{ readinessScore }}%</strong>
            <span class="cc-badge" :class="readinessTone">{{ readinessLabel }}</span>
          </div>
          <div class="cc-bar"><div class="cc-bar-fill" :style="{ width: readinessScore + '%' }"></div></div>
        </article>

        <article class="cc-card" aria-label="Predicted Rating">
          <span class="cc-label">Predicted Rating</span>
          <div class="cc-score">
            <strong>{{ formatNumber(report.scorecard?.rating_distribution?.predicted_mean_rating) }} ★</strong>
          </div>
          <span class="cc-sub">Range {{ formatNumber(report.scorecard?.rating_distribution?.confidence_band?.low) }}–{{ formatNumber(report.scorecard?.rating_distribution?.confidence_band?.high) }} ({{ report.scorecard?.rating_distribution?.confidence_band?.label || 'moderate' }})</span>
        </article>

        <article class="cc-card" :class="{ 'cc-warn': dnfRiskValue >= 0.4 }" aria-label="DNF Abandonment Risk">
          <span class="cc-label">DNF Risk</span>
          <div class="cc-score">
            <strong>{{ Math.round(dnfRiskValue * 100) }}%</strong>
            <span class="cc-badge" :class="getDnfRiskTone(dnfRiskValue)">{{ getDnfRiskLabel(dnfRiskValue) }}</span>
          </div>
          <span class="cc-sub">Band {{ Math.round((report.scorecard?.dnf?.confidence_band?.low||0)*100) }}–{{ Math.round((report.scorecard?.dnf?.confidence_band?.high||0)*100) }}%</span>
        </article>

        <article class="cc-card" :class="{ 'cc-alert': controversyRiskValue >= 0.6 }" aria-label="Controversy Risk">
          <span class="cc-label">Controversy Risk</span>
          <div class="cc-score">
            <strong>{{ Math.round(controversyRiskValue * 100) }}%</strong>
            <span class="cc-badge" :class="getControversyRiskTone(controversyRiskValue)">{{ getControversyRiskLabel(controversyRiskValue) }}</span>
          </div>
          <span class="cc-sub">Band {{ Math.round((report.scorecard?.controversy?.confidence_band?.low||0)*100) }}–{{ Math.round((report.scorecard?.controversy?.confidence_band?.high||0)*100) }}%</span>
        </article>

        <article class="cc-card" aria-label="Viral and Quoteability">
          <span class="cc-label">Viral / Quoteability</span>
          <div class="cc-score">
            <strong>{{ maxViralScore }}%</strong>
            <span class="cc-sub-inline">{{ maxViralPlatformName }}</span>
          </div>
          <span class="cc-sub">Quoteability {{ Math.round(quoteabilityScoreValue * 100) }}%</span>
        </article>

        <article class="cc-card cc-priority" :class="{ 'cc-alert': topPriorityScore >= 0.6 }" aria-label="Top Revision Priority">
          <span class="cc-label">Top Revision Priority</span>
          <div class="cc-score">
            <strong class="cc-priority-name">{{ topPriorityItemName }}</strong>
          </div>
          <span class="cc-sub" :class="getPriorityClass(topPriorityScore)">{{ getPriorityLabel(topPriorityScore) }} — {{ Math.round(topPriorityScore * 100) }}%</span>
        </article>
      </div>

      <!-- Row 2: Executive Verdict + Top 3 Improvement Moves -->
      <div class="cc-verdict-row">
        <article class="cc-verdict-card" aria-label="Executive Verdict">
          <div class="cc-eyebrow">EXECUTIVE VERDICT</div>
          <blockquote class="cc-verdict-text">{{ report.summary || 'No summary available.' }}</blockquote>
          <div class="cc-verdict-badges">
            <span class="meta-chip" :class="report.privacy_mode">🔒 {{ formatPrivacyMode(report.privacy_mode) }}</span>
            <span class="meta-chip confidence">🎯 Stage Confidence: {{ Math.round((report.confidence || 0) * 100) }}%</span>
            <span class="meta-chip draft" v-if="report.draft_id">📄 {{ report.draft_id }} (v{{ report.version || '1.0' }})</span>
          </div>
        </article>

        <article class="cc-moves-card" aria-label="Top 3 Improvement Moves">
          <div class="cc-eyebrow">TOP 3 IMPROVEMENT MOVES</div>
          <ol class="cc-moves-list" v-if="topRevisionItems.length">
            <li v-for="(item, idx) in topRevisionItems.slice(0, 3)" :key="item.item_id" class="cc-move-item">
              <span class="cc-move-num">{{ idx + 1 }}</span>
              <div class="cc-move-body">
                <strong>{{ item.item_type.toUpperCase() }}: <code>{{ item.item_id }}</code></strong>
                <p>{{ item.reasons[0] }}</p>
                <span class="priority-label-pill" :class="getPriorityClass(item.priority_score)">{{ getPriorityLabel(item.priority_score) }}</span>
              </div>
            </li>
          </ol>
          <p v-else class="cc-empty-note">No revision priorities available yet.</p>
          <button class="cc-see-more-btn" @click="activeTab = 'revision'" aria-label="View full Revision Plan tab">View full Revision Plan →</button>
        </article>
      </div>
    </section>

    <!-- =====================================================================
         MAIN TABBED INTERFACE
    ====================================================================== -->
    <div v-if="report" class="report-tabs-shell">

      <!-- Tab Nav -->
      <nav class="tab-nav" role="tablist" aria-label="Report sections">
        <button
          v-for="tab in reportTabs"
          :key="tab.id"
          class="tab-nav-btn"
          :class="{ active: activeTab === tab.id }"
          role="tab"
          :aria-selected="activeTab === tab.id"
          :id="'tab-' + tab.id"
          :aria-controls="'panel-' + tab.id"
          @click="activeTab = tab.id"
          @keydown.arrow-right.prevent="focusNextTab(tab.id)"
          @keydown.arrow-left.prevent="focusPrevTab(tab.id)"
          @keydown.home.prevent="activeTab = reportTabs[0].id"
          @keydown.end.prevent="activeTab = reportTabs[reportTabs.length - 1].id"
        >
          <span class="tab-icon" aria-hidden="true">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </nav>

      <!-- ======================================================= -->
      <!-- TAB: Overview                                           -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'overview'"
        role="tabpanel"
        id="panel-overview"
        aria-labelledby="tab-overview"
        class="tab-panel"
      >
        <!-- Star Rating Spread -->
        <div class="panel-grid-2">
          <article class="panel-card">
            <div class="card-eyebrow">SECTION 01</div>
            <h2>Star Rating Spread</h2>
            <div class="rating-overall-header">
              <div class="big-stars">{{ formatNumber(report.scorecard?.rating_distribution?.predicted_mean_rating) }} ★</div>
              <p class="muted-p">Blended estimate: persona reactions (65%) + manuscript style (35%)</p>
            </div>
            <div class="star-histogram" role="img" aria-label="Star Rating Distribution">
              <div class="histogram-row" v-for="star in [5, 4, 3, 2, 1]" :key="star">
                <span class="star-text-label">{{ star }}★</span>
                <div class="bar-track">
                  <div class="bar-fill" :class="'bar-star-' + star" :style="{ width: getStarPercentage(star) + '%' }"></div>
                </div>
                <span class="star-pct">{{ getStarPercentage(star) }}%</span>
              </div>
            </div>
            <div class="sub-components-box">
              <h3>Rating Driver Breakdown</h3>
              <div class="drivers-row">
                <div class="driver-pill" v-for="(val, name) in report.scorecard?.rating_distribution?.component_scores || {}" :key="name">
                  <span class="label">{{ formatRadarLabel(name) }}</span>
                  <strong :class="getComponentScoreTone(val)">{{ Math.round(val * 100) }}%</strong>
                </div>
              </div>
            </div>
          </article>

          <!-- Reader Segment Map -->
          <article class="panel-card">
            <div class="card-eyebrow">SECTION 02</div>
            <h2>Reader Segment Map</h2>
            <div class="table-container">
              <table class="segments-table">
                <thead>
                  <tr>
                    <th>Segment</th>
                    <th>Rating</th>
                    <th>Rec %</th>
                    <th>Signal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="seg in report.segment_insights || []" :key="seg.segment">
                    <td><code>{{ seg.segment }}</code></td>
                    <td><strong>{{ formatNumber(seg.rating_mean) }} ★</strong></td>
                    <td>{{ seg.recommendation_mean !== null ? Math.round(seg.recommendation_mean * 100) + '%' : 'N/A' }}</td>
                    <td><span class="signal-badge" :class="seg.signal">{{ seg.signal?.toUpperCase() }}</span></td>
                  </tr>
                  <tr v-if="!report.segment_insights?.length">
                    <td colspan="4" class="empty-table-cell">No segment data available.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </article>
        </div>

        <!-- Quoteability + Viral side-by-side -->
        <div class="panel-grid-2">
          <article class="panel-card">
            <div class="card-eyebrow">QUOTEABILITY MAP</div>
            <h2>Quoteability</h2>
            <div class="readiness-card" :class="quoteabilityScoreValue >= 0.6 ? 'ready' : 'mixed'">
              <div class="cc-score"><strong>{{ Math.round(quoteabilityScoreValue * 100) }}%</strong></div>
              <div class="cc-bar"><div class="cc-bar-fill" :style="{ width: quoteabilityScoreValue * 100 + '%' }"></div></div>
            </div>
            <div class="radar-card-grid margin-top-md">
              <div class="radar-bar-item" v-for="(val, name) in report.scorecard?.quoteability?.component_scores || {}" :key="name">
                <div class="radar-bar-header">
                  <span class="label">{{ formatRadarLabel(name) }}</span>
                  <strong>{{ Math.round(val * 100) }}%</strong>
                </div>
                <div class="radar-bar-track"><div class="radar-bar-fill" :class="getRiskLevelTone(val)" :style="{ width: val*100+'%' }"></div></div>
              </div>
            </div>
          </article>

          <article class="panel-card">
            <div class="card-eyebrow">VIRAL POTENTIAL</div>
            <h2>Platform Virality</h2>
            <div class="viral-platform-chart">
              <div class="platform-bar-row" v-for="(val, platform) in report.scorecard?.viral?.platform_scores || {}" :key="platform">
                <span class="platform-name-label">{{ formatPlatformLabel(platform) }}</span>
                <div class="platform-bar-track">
                  <div class="platform-bar-fill" :class="'platform-color-' + platform" :style="{ width: val*100+'%' }"></div>
                </div>
                <span class="platform-pct">{{ Math.round(val * 100) }}%</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- ======================================================= -->
      <!-- TAB: Development Editor Board                           -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'editors'"
        role="tabpanel"
        id="panel-editors"
        aria-labelledby="tab-editors"
        class="tab-panel"
      >
        <div class="panel-intro">
          <h2>Development Editor Board</h2>
          <p class="muted-p">Archetypal editorial lenses — each offers a structured diagnosis based on the simulation evidence pack. All scores are synthesized from the scorecard data.</p>
        </div>

        <div class="editors-grid">
          <article
            class="editor-card"
            v-for="editor in editorBoard"
            :key="editor.role"
          >
            <div class="editor-card-header">
              <span class="editor-icon" aria-hidden="true">{{ editor.icon }}</span>
              <div>
                <div class="editor-role">{{ editor.role }}</div>
                <div class="editor-score-row">
                  <div class="editor-score-bar">
                    <div class="editor-score-fill" :class="editor.scoreTone" :style="{ width: editor.score + '%' }"></div>
                  </div>
                  <span class="editor-score-val" :class="'text-' + editor.scoreTone">{{ editor.score }}%</span>
                </div>
              </div>
            </div>
            <div class="editor-card-body">
              <div class="editor-field">
                <span class="editor-field-label">Top Concern</span>
                <p class="editor-field-value concern">{{ editor.topConcern }}</p>
              </div>
              <div class="editor-field">
                <span class="editor-field-label">Why It Matters</span>
                <p class="editor-field-value">{{ editor.whyItMatters }}</p>
              </div>
              <div class="editor-field editor-field-row">
                <div>
                  <span class="editor-field-label">Affected Section</span>
                  <code class="editor-section-tag">{{ editor.affectedSection }}</code>
                </div>
                <div>
                  <span class="editor-field-label">Confidence</span>
                  <span class="editor-conf-badge">{{ editor.confidence }}</span>
                </div>
              </div>
              <div class="editor-field">
                <span class="editor-field-label">Recommended Fix</span>
                <p class="editor-field-value fix">{{ editor.recommendedFix }}</p>
              </div>
              <div class="editor-field">
                <span class="editor-field-label">Expected Effect</span>
                <p class="editor-field-value effect">{{ editor.expectedEffect }}</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- ======================================================= -->
      <!-- TAB: Revision Plan                                      -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'revision'"
        role="tabpanel"
        id="panel-revision"
        aria-labelledby="tab-revision"
        class="tab-panel"
      >
        <div class="panel-intro">
          <h2>Revision Plan</h2>
          <p class="muted-p">Ranked hotspots ordered by predicted revision impact. Expand any item for details.</p>
          <button class="ghost-btn" @click="showAllRevision = !showAllRevision" aria-label="Toggle showing all revision items">
            {{ showAllRevision ? 'Show Top 5 Only' : 'Show All Items' }}
          </button>
        </div>

        <div class="revision-list" v-if="report.scorecard?.revision_priority?.ranked_items?.length">
          <article
            class="revision-item"
            v-for="(item, idx) in visibleRevisionItems"
            :key="item.item_id"
            :class="'item-priority-' + getPriorityClass(item.priority_score)"
          >
            <div
              class="revision-item-header"
              @click="toggleRevisionExpand(item.item_id)"
              @keydown.enter="toggleRevisionExpand(item.item_id)"
              @keydown.space.prevent="toggleRevisionExpand(item.item_id)"
              role="button"
              tabindex="0"
              :aria-expanded="expandedRevisionItems.includes(item.item_id)"
              :aria-controls="'revision-detail-' + item.item_id"
            >
              <div class="revision-header-left">
                <span class="revision-rank">#{{ idx + 1 }}</span>
                <span class="priority-label-pill" :class="getPriorityClass(item.priority_score)">{{ getPriorityLabel(item.priority_score) }}</span>
                <span class="item-type-badge">{{ item.item_type }}</span>
                <strong class="revision-target"><code>{{ item.item_id }}</code></strong>
              </div>
              <div class="revision-header-right">
                <div class="revision-impact-chips">
                  <span class="impact-chip">Priority {{ Math.round(item.priority_score * 100) }}%</span>
                </div>
                <span class="expand-chevron" :class="{ open: expandedRevisionItems.includes(item.item_id) }">›</span>
              </div>
            </div>

            <!-- Collapsed preview: show first reason -->
            <div class="revision-preview" v-if="!expandedRevisionItems.includes(item.item_id)">
              <span class="revision-issue-preview">{{ item.reasons[0] }}</span>
            </div>

            <!-- Expanded detail -->
            <div
              class="revision-detail"
              :id="'revision-detail-' + item.item_id"
              v-if="expandedRevisionItems.includes(item.item_id)"
            >
              <div class="revision-detail-grid">
                <div class="rd-field">
                  <span class="rd-label">Issue</span>
                  <ul class="reasons-bullet-list">
                    <li v-for="reason in item.reasons" :key="reason">{{ reason }}</li>
                  </ul>
                </div>
                <div class="rd-field">
                  <span class="rd-label">Affected Section</span>
                  <code class="rd-value">{{ item.item_id }}</code>
                </div>
                <div class="rd-field">
                  <span class="rd-label">Evidence Links</span>
                  <div class="evidence-pills-row">
                    <span class="evidence-pill" v-for="ref in item.evidence_refs || []" :key="ref">#{{ ref }}</span>
                    <span class="muted-note" v-if="!item.evidence_refs?.length">No evidence refs</span>
                  </div>
                </div>
                <div class="rd-field">
                  <span class="rd-label">Expected Score Movement</span>
                  <p class="rd-value">Addressing this item is expected to reduce DNF pressure and improve predicted rating band.</p>
                </div>
              </div>
            </div>
          </article>
        </div>
        <p v-else class="muted-note text-center">No revision priorities were generated. Run a simulation to generate this data.</p>
      </section>

      <!-- ======================================================= -->
      <!-- TAB: Reader Reactions                                   -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'reactions'"
        role="tabpanel"
        id="panel-reactions"
        aria-labelledby="tab-reactions"
        class="tab-panel"
      >
        <div class="panel-intro">
          <h2>Simulated Reader Reactions</h2>
          <p class="muted-p">Platform-specific posts generated by synthetic reader personas. Filter by platform.</p>
        </div>

        <div class="tab-row-container">
          <div class="tab-row" role="tablist" aria-label="Filter by platform">
            <button
              v-for="plat in ['all', 'goodreads', 'booktok', 'reddit', 'bookstagram', 'x', 'newsletter', 'bookclub']"
              :key="plat"
              class="tab-btn"
              :class="{ active: activePlatformTab === plat }"
              role="tab"
              :aria-selected="activePlatformTab === plat"
              @click="activePlatformTab = plat"
            >
              {{ formatPlatformTabName(plat) }}
              <span class="tab-count-badge" v-if="getPlatformPostCount(plat) > 0">{{ getPlatformPostCount(plat) }}</span>
            </button>
          </div>
        </div>

        <div class="feed-container" v-if="filteredPosts.length">
          <article
            class="mock-post-card"
            v-for="post in filteredPosts"
            :key="post.post_id"
            :class="'mock-post-' + post.platform"
          >
            <header class="post-header">
              <div class="user-info">
                <span class="avatar" aria-hidden="true">👤</span>
                <div class="user-meta">
                  <strong class="display-name">{{ getPersonaDisplayName(post.persona_id) }}</strong>
                  <span class="handle">@{{ post.persona_id }}</span>
                </div>
              </div>
              <span class="post-platform-tag" :class="post.platform">{{ post.platform?.toUpperCase() }}</span>
            </header>
            <div class="post-body">
              <div class="post-stars-row" v-if="post.rating && post.platform === 'goodreads'">
                <span class="star-rating">{{ '★'.repeat(Math.round(post.rating)) }}{{ '☆'.repeat(5 - Math.round(post.rating)) }}</span>
                <span class="rating-value">({{ post.rating }} / 5)</span>
              </div>
              <div class="subreddit-tag" v-if="post.platform === 'reddit'">r/books • Posted by u/{{ post.persona_id }}</div>
              <p class="post-text">{{ post.body || 'No reaction text.' }}</p>
              <div class="tiktok-video-mock" v-if="post.platform === 'booktok'">
                <div class="video-overlay">
                  <span>📹 Play Video Hook</span>
                  <span class="hook-text" v-if="post.payload?.hook_line">"{{ post.payload.hook_line }}"</span>
                </div>
              </div>
              <div class="post-hashtags" v-if="post.hashtags?.length">
                <span v-for="tag in post.hashtags" :key="tag" class="tag">#{{ tag }}</span>
              </div>
            </div>
            <footer class="post-footer">
              <div class="metric">❤️ <strong>{{ Math.round((post.engagement_prediction || 0.5) * 100) }}</strong></div>
              <div class="metric" v-if="post.payload?.hot_take"><span class="hot-take-label">🌶️ HOT TAKE</span></div>
              <div class="metric" v-if="post.payload?.viral_trigger"><span class="viral-trigger-label">⚡ VIRAL</span></div>
            </footer>
          </article>
        </div>
        <p v-else class="muted-note text-center padding-xl">No simulated posts for this platform filter.</p>
      </section>

      <!-- ======================================================= -->
      <!-- TAB: Risks                                              -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'risks'"
        role="tabpanel"
        id="panel-risks"
        aria-labelledby="tab-risks"
        class="tab-panel"
      >
        <div class="panel-intro">
          <h2>Risk Analysis</h2>
          <p class="muted-p">Grouped DNF abandonment analysis, controversy radar, chapter pressure points, caveats, and confidence limits.</p>
        </div>

        <div class="panel-grid-2">
          <!-- DNF Drivers -->
          <article class="panel-card">
            <div class="card-eyebrow">ABANDONMENT</div>
            <h2>DNF Abandonment Drivers</h2>
            <p class="muted-p margin-bottom-lg">Key drivers computed from pacing penalties, early drag, and style mismatches.</p>
            <div class="dnf-drivers-list">
              <div class="dnf-driver-row" v-for="(val, name) in report.scorecard?.dnf?.component_scores || {}" :key="name">
                <div class="dnf-driver-header">
                  <span class="label">{{ formatRadarLabel(name) }}</span>
                  <strong :class="getDnfDriverTone(val)">{{ Math.round(val * 100) }}% Risk</strong>
                </div>
                <div class="dnf-driver-track">
                  <div class="dnf-driver-fill" :class="getDnfDriverTone(val)" :style="{ width: val*100+'%' }"></div>
                </div>
              </div>
            </div>
          </article>

          <!-- Chapter Pressure Timeline -->
          <article class="panel-card">
            <div class="card-eyebrow">TIMELINE</div>
            <h2>Chapter Pressure Points</h2>
            <p class="muted-p margin-bottom-lg">Chapters with the highest abandonment risk, sorted by DNF pressure.</p>
            <div class="timeline" v-if="report.scorecard?.dnf?.chapter_points?.length">
              <div
                class="timeline-item"
                v-for="point in report.scorecard.dnf.chapter_points"
                :key="point.section_id"
                :class="{ 'high-pressure': point.dnf_points >= 0.4 }"
              >
                <div class="timeline-marker">
                  <span class="marker-num">{{ point.chapter_number || 'Ch' }}</span>
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <h3>Chapter {{ point.chapter_number }}</h3>
                    <span class="dnf-value-badge" :class="getDnfRiskTone(point.dnf_points)">{{ Math.round(point.dnf_points * 100) }}% DNF</span>
                  </div>
                  <p class="timeline-reason">{{ point.reason }}</p>
                </div>
              </div>
            </div>
            <p v-else class="muted-note text-center">No chapter pressure points recorded.</p>
          </article>
        </div>

        <!-- Controversy Radar -->
        <article class="panel-card margin-bottom-lg">
          <div class="card-eyebrow">SECTION 05</div>
          <h2>Controversy Radar</h2>
          <p class="muted-p margin-bottom-lg">Backlash risk by axis — synthesized from claim hazard, moral disagreement, ideological tension, and packaging mismatch signals.</p>
          <div class="panel-grid-2">
            <div class="radar-card-grid">
              <div class="radar-bar-item" v-for="(val, name) in report.scorecard?.controversy?.radar || {}" :key="name">
                <div class="radar-bar-header">
                  <span class="label">{{ formatRadarLabel(name) }}</span>
                  <strong>{{ Math.round(val * 100) }}%</strong>
                </div>
                <div class="radar-bar-track">
                  <div class="radar-bar-fill" :class="getRiskLevelTone(val)" :style="{ width: val*100+'%' }"></div>
                </div>
              </div>
            </div>
            <div>
              <div class="hotspots-box" v-if="report.scorecard?.controversy?.hotspots?.length">
                <h3>Flagged Backlash Hotspots</h3>
                <ul class="hotspots-list">
                  <li v-for="spot in report.scorecard.controversy.hotspots" :key="spot">⚠️ <code>{{ spot }}</code></li>
                </ul>
              </div>
              <!-- Author Risk Notes -->
              <div class="warning-box margin-top-md">
                <h3>Top Backlash Risks</h3>
                <ul class="bullets-list-warning">
                  <li v-for="item in report.top_risks || []" :key="item">{{ item }}</li>
                  <li v-if="!report.top_risks?.length" class="muted-note">No risks detected.</li>
                </ul>
              </div>
              <!-- Caveats -->
              <div class="uncertainty-box margin-top-md" v-if="report.uncertainty_notes?.length">
                <h3>Confidence Caveats</h3>
                <ul class="bullets-list-styled">
                  <li v-for="item in report.uncertainty_notes" :key="item">{{ item }}</li>
                </ul>
              </div>
            </div>
          </div>
        </article>

        <!-- Simulation Limitations Banner -->
        <section class="limitations-info-banner">
          <div class="info-icon" aria-hidden="true">ℹ️</div>
          <div class="info-content">
            <h3>Known Simulation Limitations</h3>
            <p>This report is synthesized from a deterministic simulation using synthetic personas. It is designed for manuscript stress testing, not absolute market validation. No real social platforms were contacted. Local models run completely offline to preserve privacy.</p>
          </div>
        </section>
      </section>

      <!-- ======================================================= -->
      <!-- TAB: Quoteability & Marketing                           -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'marketing'"
        role="tabpanel"
        id="panel-marketing"
        aria-labelledby="tab-marketing"
        class="tab-panel"
      >
        <div class="panel-intro">
          <h2>Quoteability & Marketing</h2>
          <p class="muted-p">Highlight-worthy excerpts, discoverability hooks, and top strengths for positioning.</p>
        </div>

        <div class="panel-grid-2">
          <!-- Quote Candidates -->
          <article class="panel-card">
            <div class="card-eyebrow">HIGHLIGHTS</div>
            <h2>Excerpt Share Candidates</h2>
            <p class="muted-p margin-bottom-lg">Lines with highest organic screenshot & share probability.</p>
            <div class="quotes-list-container" v-if="report.scorecard?.quoteability?.quote_candidates?.length">
              <blockquote class="pull-quote-card" v-for="candidate in report.scorecard.quoteability.quote_candidates" :key="candidate.text">
                <p>"{{ candidate.text }}"</p>
                <cite>Source: {{ candidate.source }}</cite>
              </blockquote>
            </div>
            <p v-else class="muted-note text-center">No quote candidates extracted.</p>
          </article>

          <!-- Marketing Hooks & Strengths -->
          <article class="panel-card">
            <div class="card-eyebrow">POSITIONING</div>
            <h2>Marketing Hooks & Strengths</h2>
            <div class="hooks-box">
              <h3>Top Strengths</h3>
              <ul class="bullets-list-styled">
                <li v-for="item in report.top_strengths || []" :key="item">{{ item }}</li>
                <li v-if="!report.top_strengths?.length" class="muted-note">No top strengths recorded.</li>
              </ul>
            </div>
            <div class="hooks-box margin-top-md" v-if="session.evidencePack?.market_surface?.discoverability_hooks?.length">
              <h3>Discoverability Hooks</h3>
              <div class="hooks-pills-row">
                <span class="hook-pill" v-for="hook in session.evidencePack.market_surface.discoverability_hooks" :key="hook">🎯 {{ hook }}</span>
              </div>
            </div>

            <!-- Polarization -->
            <div class="margin-top-md" v-if="report.scorecard?.polarization">
              <h3 class="sub-section-heading">Polarization Score</h3>
              <div class="cc-score">
                <strong>{{ Math.round((report.scorecard.polarization.polarization_score || 0) * 100) }}%</strong>
              </div>
              <div class="drivers-row margin-top-md">
                <div class="driver-pill" v-for="(val, name) in report.scorecard.polarization.component_scores || {}" :key="name">
                  <span class="label">{{ formatRadarLabel(name) }}</span>
                  <strong :class="getComponentScoreTone(val)">{{ Math.round(val * 100) }}%</strong>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- ======================================================= -->
      <!-- TAB: Evidence                                           -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'evidence'"
        role="tabpanel"
        id="panel-evidence"
        aria-labelledby="tab-evidence"
        class="tab-panel"
      >
        <div class="panel-intro">
          <h2>Evidence Pack</h2>
          <p class="muted-p">Summary of compiled manuscript maps and DNA used to generate this simulation.</p>
        </div>

        <div v-if="session.evidencePack" class="evidence-grid">
          <!-- Book DNA -->
          <article class="panel-card">
            <div class="card-eyebrow">BOOK DNA</div>
            <h2>Book DNA</h2>
            <div class="evidence-field-list">
              <div class="evidence-kv"><span class="ev-key">Title</span><span class="ev-val">{{ session.evidencePack.book_dna?.title || 'N/A' }}</span></div>
              <div class="evidence-kv"><span class="ev-key">Genre</span><span class="ev-val">{{ session.evidencePack.book_dna?.genre || 'N/A' }}</span></div>
              <div class="evidence-kv"><span class="ev-key">Target Reader</span><span class="ev-val">{{ session.evidencePack.book_dna?.target_reader || 'N/A' }}</span></div>
            </div>
            <blockquote class="ev-premise" v-if="session.evidencePack.book_dna?.premise">{{ session.evidencePack.book_dna.premise }}</blockquote>
          </article>

          <!-- Chapter Map -->
          <article class="panel-card">
            <div class="card-eyebrow">CHAPTER MAP</div>
            <h2>Chapters</h2>
            <p class="muted-p">{{ session.evidencePack.chapter_map?.chapters?.length || 0 }} chapters parsed.</p>
            <ul class="ev-chapter-list">
              <li v-for="ch in (session.evidencePack.chapter_map?.chapters || []).slice(0, 10)" :key="ch.chapter_id">
                <strong>Ch {{ ch.chapter_number }}: {{ ch.title || 'Untitled' }}</strong>
                <span v-if="ch.summary" class="ev-ch-summary">{{ ch.summary }}</span>
              </li>
              <li v-if="(session.evidencePack.chapter_map?.chapters?.length || 0) > 10" class="muted-note">... and {{ session.evidencePack.chapter_map.chapters.length - 10 }} more</li>
            </ul>
          </article>

          <!-- Character Map -->
          <article class="panel-card">
            <div class="card-eyebrow">CHARACTER MAP</div>
            <h2>Characters</h2>
            <p class="muted-p">{{ session.evidencePack.character_map?.characters?.length || 0 }} characters identified.</p>
            <ul class="ev-chapter-list">
              <li v-for="char in (session.evidencePack.character_map?.characters || []).slice(0, 8)" :key="char.character_id">
                <strong>{{ char.name }} <span class="item-type-badge">{{ char.role || 'Secondary' }}</span></strong>
                <span v-if="char.reader_friction?.length" class="ev-ch-summary">Frictions: {{ char.reader_friction.join(', ') }}</span>
              </li>
            </ul>
          </article>

          <!-- Style Map -->
          <article class="panel-card">
            <div class="card-eyebrow">STYLE MAP</div>
            <h2>Style Calibration</h2>
            <div class="evidence-field-list" v-if="session.evidencePack.style_map">
              <div class="evidence-kv"><span class="ev-key">Clarity</span><span class="ev-val">{{ session.evidencePack.style_map.clarity ?? 'N/A' }}</span></div>
              <div class="evidence-kv"><span class="ev-key">Rhythm</span><span class="ev-val">{{ session.evidencePack.style_map.rhythm ?? 'N/A' }}</span></div>
              <div class="evidence-kv"><span class="ev-key">Quoteability</span><span class="ev-val">{{ session.evidencePack.style_map.quoteability ?? 'N/A' }}</span></div>
            </div>
            <p v-else class="muted-note">Style map not available.</p>
          </article>

          <!-- Risk Map -->
          <article class="panel-card">
            <div class="card-eyebrow">RISK MAP</div>
            <h2>Narrative Risks</h2>
            <p class="muted-p">{{ session.evidencePack.risk_map?.risks?.length || 0 }} risks detected.</p>
            <ul class="ev-chapter-list">
              <li v-for="risk in (session.evidencePack.risk_map?.risks || []).slice(0, 8)" :key="risk.risk_id">
                <strong class="risk-badge">{{ risk.risk_type }}</strong>
                <span class="ev-ch-summary">{{ risk.description || risk.mitigation_hint }}</span>
              </li>
            </ul>
          </article>
        </div>

        <div v-else class="empty-state-card">
          <div class="empty-icon" aria-hidden="true">📦</div>
          <h2>No Evidence Pack Available</h2>
          <p>Evidence pack data is stored in session. Upload a manuscript and run the evidence extraction step first.</p>
        </div>

        <!-- Collapsible Raw JSON -->
        <div class="advanced-collapse margin-top-md">
          <button class="collapse-trigger-btn" @click="showRawJson = !showRawJson" :aria-expanded="showRawJson">
            {{ showRawJson ? '▼ Hide Raw Evidence JSON' : '▶ Show Raw Evidence JSON (Advanced)' }}
          </button>
          <pre v-if="showRawJson" class="raw-json-block">{{ JSON.stringify(session.evidencePack, null, 2) }}</pre>
        </div>
      </section>

      <!-- ======================================================= -->
      <!-- TAB: Exports                                            -->
      <!-- ======================================================= -->
      <section
        v-show="activeTab === 'exports'"
        role="tabpanel"
        id="panel-exports"
        aria-labelledby="tab-exports"
        class="tab-panel"
      >
        <div class="panel-intro">
          <h2>Exports</h2>
          <p class="muted-p">Download the full report in multiple formats. All exports run locally — no manuscript data is sent externally.</p>
        </div>

        <div class="export-grid">
          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">📄</div>
            <div class="export-card-info">
              <h3>PDF Report</h3>
              <p>Structured PDF via pdfmake. Includes executive verdict, scorecard metrics, and revision priorities.</p>
              <span class="export-note">Runs fully client-side.</span>
            </div>
            <button class="primary-btn" @click="handleExport('pdf')" aria-label="Export PDF report">Download PDF</button>
          </article>

          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">📝</div>
            <div class="export-card-info">
              <h3>DOCX Report</h3>
              <p>Editable Word document with headings, revision priorities, and limitations statement.</p>
              <span class="export-note">Runs fully client-side.</span>
            </div>
            <button class="primary-btn" @click="handleExport('docx')" aria-label="Export DOCX report">Download DOCX</button>
          </article>

          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">⬇️</div>
            <div class="export-card-info">
              <h3>Markdown</h3>
              <p>Plain Markdown file suitable for version-controlled manuscript notes or editorial briefs.</p>
              <span class="export-note">Runs fully client-side.</span>
            </div>
            <button class="primary-btn" @click="handleExport('markdown')" aria-label="Export Markdown">Download MD</button>
          </article>

          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">📥</div>
            <div class="export-card-info">
              <h3>Raw JSON</h3>
              <p>Full report payload including all scorecard data, segment insights, and metadata.</p>
              <span class="export-note">Machine-readable format.</span>
            </div>
            <button class="ghost-btn" @click="handleExport('json')" aria-label="Export JSON">Download JSON</button>
          </article>

          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">🖼️</div>
            <div class="export-card-info">
              <h3>Summary Card (PNG)</h3>
              <p>A shareable visual scorecard card — captured from the live DOM. Ideal for social sharing.</p>
              <span class="export-note">Uses html2canvas.</span>
            </div>
            <button class="ghost-btn" @click="handleExport('png')" aria-label="Export PNG summary card">Download PNG</button>
          </article>

          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">📋</div>
            <div class="export-card-info">
              <h3>Copy Markdown</h3>
              <p>Copy the formatted Markdown summary directly to clipboard for pasting into editors.</p>
              <span class="export-note">Browser clipboard API.</span>
            </div>
            <button class="ghost-btn" :class="{ 'text-ready': copySuccess }" @click="handleCopy" aria-label="Copy Markdown to clipboard">
              {{ copySuccess ? '✅ Copied!' : 'Copy to Clipboard' }}
            </button>
          </article>

          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">💬</div>
            <div class="export-card-info">
              <h3>Copy Executive Summary</h3>
              <p>Copy the executive verdict, confidence score, and key metrics as plain text. Great for pasting into a writing journal or Notion.</p>
              <span class="export-note">Browser clipboard API.</span>
            </div>
            <button class="ghost-btn" :class="{ 'text-ready': copyExecSuccess }" @click="handleCopyExec" aria-label="Copy executive summary to clipboard">
              {{ copyExecSuccess ? '✅ Copied!' : 'Copy Executive Summary' }}
            </button>
          </article>

          <article class="export-card">
            <div class="export-card-icon" aria-hidden="true">✏️</div>
            <div class="export-card-info">
              <h3>Copy Revision Plan</h3>
              <p>Copy the full ranked revision checklist as a numbered plain-text list. Paste directly into your manuscript notes.</p>
              <span class="export-note">Browser clipboard API.</span>
            </div>
            <button class="ghost-btn" :class="{ 'text-ready': copyRevSuccess }" @click="handleCopyRevision" aria-label="Copy revision plan to clipboard">
              {{ copyRevSuccess ? '✅ Copied!' : 'Copy Revision Plan' }}
            </button>
          </article>
        </div>

        <!-- Export disclaimer -->
        <div class="limitations-info-banner margin-top-md">
          <div class="info-icon" aria-hidden="true">🔒</div>
          <div class="info-content">
            <h3>Privacy-Safe Exports</h3>
            <p>All export operations run entirely within your browser or local Node environment. No manuscript content, report data, or scorecard results are transmitted to any external server during export. This is guaranteed by design for <code>local_only</code> and <code>hybrid_safe</code> modes.</p>
          </div>
        </div>
      </section>

    </div>

    <!-- =====================================================================
         EMPTY STATE (no report)
    ====================================================================== -->
    <section v-if="!report && !loading" class="empty-state-card">
      <div class="empty-icon" aria-hidden="true">📊</div>
      <h2>No Swarmbook Report Available</h2>
      <p>You have not generated a report for this project yet. Run a reader simulation to generate predictions, scorecard profiles, and revision guidelines.</p>
      <div class="empty-actions">
        <button
          class="primary-btn"
          @click="router.push({ name: 'SwarmbookSimulation', params: { projectId: session.projectId } })"
          aria-label="Go to Reader Swarm Setup"
        >
          Setup &amp; Run Reader Swarm
        </button>
        <button
          class="ghost-btn"
          @click="loadDemoMock"
          aria-label="Load offline demo report for validation"
        >
          Load Demo Report (Offline Mock)
        </button>
      </div>
    </section>

    <!-- Hidden PNG summary card (for html2canvas capture) -->
    <div id="png-summary-card" class="png-summary-capture-card" v-if="report">
      <div class="png-card-header">
        <h1>{{ report.title || report.project_id }}</h1>
        <p>Swarmbook Scorecard • {{ getFormatDate() }}</p>
      </div>
      <div class="png-card-verdict">
        <h2>Verdict: {{ readinessLabel }}</h2>
        <p>{{ report.summary }}</p>
      </div>
      <div class="png-card-metrics">
        <div class="png-metric"><span>Ready</span><strong>{{ readinessScore }}%</strong></div>
        <div class="png-metric"><span>Rating</span><strong>{{ formatNumber(report.scorecard?.rating_distribution?.predicted_mean_rating) }} ★</strong></div>
        <div class="png-metric"><span>DNF Risk</span><strong>{{ Math.round(dnfRiskValue * 100) }}%</strong></div>
        <div class="png-metric"><span>Confidence</span><strong>{{ Math.round((report.confidence || 0) * 100) }}%</strong></div>
      </div>
      <div class="png-card-priorities" v-if="report.scorecard?.revision_priority?.ranked_items?.length">
        <h3>Top Revision Priority</h3>
        <p><strong>{{ topPriorityItemName }}</strong>: {{ report.scorecard.revision_priority.ranked_items[0].reasons.join(', ') }}</p>
      </div>
    </div>

  </SwarmbookAppShell>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import html2canvas from 'html2canvas'
import SwarmbookAppShell from '../../components/swarmbook/SwarmbookAppShell.vue'
import { getBookSimReport } from '../../api/bookSim'
import { getSwarmbookSession, updateSwarmbookSession } from '../../store/swarmbookSession'
import { generateJson, generateMarkdown, generateDocx, generatePdf, copyToClipboard, copyExecutiveSummary, copyRevisionPlan } from '../../utils/exportReport'

// =========================================================================
// Router & Session
// =========================================================================
const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const report = ref(session.value.report)
const loading = ref(false)
const loadingMessage = ref('')
const error = ref('')

watch(() => route.path, () => {
  session.value = getSwarmbookSession()
  report.value = session.value.report
})

// =========================================================================
// Tab state
// =========================================================================
const reportTabs = [
  { id: 'overview',  icon: '📊', label: 'Overview' },
  { id: 'editors',  icon: '🏛️', label: 'Development Editor Board' },
  { id: 'revision', icon: '✏️', label: 'Revision Plan' },
  { id: 'reactions',icon: '💬', label: 'Reader Reactions' },
  { id: 'risks',    icon: '⚠️', label: 'Risks' },
  { id: 'marketing',icon: '🎯', label: 'Quoteability & Marketing' },
  { id: 'evidence', icon: '📦', label: 'Evidence' },
  { id: 'exports',  icon: '📤', label: 'Exports' },
]
const activeTab = ref('overview')

function focusNextTab(currentId) {
  const idx = reportTabs.findIndex(t => t.id === currentId)
  const next = reportTabs[(idx + 1) % reportTabs.length]
  activeTab.value = next.id
  document.getElementById('tab-' + next.id)?.focus()
}
function focusPrevTab(currentId) {
  const idx = reportTabs.findIndex(t => t.id === currentId)
  const prev = reportTabs[(idx - 1 + reportTabs.length) % reportTabs.length]
  activeTab.value = prev.id
  document.getElementById('tab-' + prev.id)?.focus()
}

// =========================================================================
// Platform reactions tab filter
// =========================================================================
const activePlatformTab = ref('all')
const platformPosts = computed(() => session.value.simulationRun?.platform_posts || [])
const filteredPosts = computed(() => {
  if (activePlatformTab.value === 'all') return platformPosts.value
  return platformPosts.value.filter(p => p.platform === activePlatformTab.value)
})
const personaNames = computed(() => {
  const r = {}
  for (const p of session.value.simulationRun?.reader_personas || []) r[p.persona_id] = p.display_name
  return r
})
function getPersonaDisplayName(id) { return personaNames.value[id] || id }
function getPlatformPostCount(platform) {
  if (platform === 'all') return platformPosts.value.length
  return platformPosts.value.filter(p => p.platform === platform).length
}

// =========================================================================
// Revision Plan expand/collapse
// =========================================================================
const showAllRevision = ref(false)
const expandedRevisionItems = ref([])
const topRevisionItems = computed(() => report.value?.scorecard?.revision_priority?.ranked_items || [])
const visibleRevisionItems = computed(() => {
  const items = topRevisionItems.value
  return showAllRevision.value ? items : items.slice(0, 5)
})
function toggleRevisionExpand(id) {
  if (expandedRevisionItems.value.includes(id)) {
    expandedRevisionItems.value = expandedRevisionItems.value.filter(x => x !== id)
  } else {
    expandedRevisionItems.value = [...expandedRevisionItems.value, id]
  }
}

// =========================================================================
// Evidence raw JSON toggle
// =========================================================================
const showRawJson = ref(false)

// =========================================================================
// Publishing Readiness Score
// =========================================================================
const readinessScore = computed(() => {
  if (!report.value) return 0
  const rating = Number(report.value.scorecard?.rating_distribution?.predicted_mean_rating) || 3.0
  const dnf = Number(report.value.scorecard?.dnf?.dnf_risk) || 0.5
  const controversy = Number(report.value.scorecard?.controversy?.controversy_risk) || 0.5
  const ratingContrib = ((rating - 1.0) / 4.0) * 50
  const dnfContrib = (1.0 - dnf) * 30
  const controversyContrib = (1.0 - controversy * 0.5) * 20
  return Math.round(Math.max(0, Math.min(100, ratingContrib + dnfContrib + controversyContrib)))
})
const readinessLabel = computed(() => {
  const s = readinessScore.value
  if (s >= 80) return 'Strong'
  if (s >= 60) return 'Good'
  return 'Revision Recommended'
})
const readinessTone = computed(() => {
  const s = readinessScore.value
  if (s >= 80) return 'ready'
  if (s >= 60) return 'mixed'
  return 'offline'
})

// =========================================================================
// Risk values
// =========================================================================
const dnfRiskValue = computed(() => Number(report.value?.scorecard?.dnf?.dnf_risk) || 0)
const controversyRiskValue = computed(() => Number(report.value?.scorecard?.controversy?.controversy_risk) || 0)
const quoteabilityScoreValue = computed(() => Number(report.value?.scorecard?.quoteability?.quoteability_score) || 0)

const maxViralScore = computed(() => {
  const scores = report.value?.scorecard?.viral?.platform_scores
  if (!scores) return 0
  const vals = Object.values(scores).map(v => Number(v)).filter(v => !isNaN(v))
  return vals.length ? Math.round(Math.max(...vals) * 100) : 0
})
const maxViralPlatformName = computed(() => {
  const scores = report.value?.scorecard?.viral?.platform_scores
  if (!scores) return 'N/A'
  let best = 'None', maxS = -1
  for (const [platform, val] of Object.entries(scores)) {
    if (val > maxS) { maxS = val; best = platform }
  }
  return formatPlatformLabel(best)
})
const topPriorityItem = computed(() => report.value?.scorecard?.revision_priority?.ranked_items?.[0])
const topPriorityItemName = computed(() => {
  if (!topPriorityItem.value) return 'None'
  return `${topPriorityItem.value.item_type.toUpperCase()}:${topPriorityItem.value.item_id}`
})
const topPriorityScore = computed(() => topPriorityItem.value?.priority_score || 0)

// =========================================================================
// Label helpers
// =========================================================================
function getDnfRiskLabel(val) {
  if (val <= 0.20) return 'Very Low'
  if (val <= 0.40) return 'Low'
  if (val <= 0.60) return 'Moderate'
  if (val <= 0.80) return 'High'
  return 'Critical'
}
function getDnfRiskTone(val) {
  if (val <= 0.40) return 'ready'
  if (val <= 0.60) return 'mixed'
  return 'offline'
}
function getControversyRiskLabel(val) {
  if (val <= 0.20) return 'Minimal'
  if (val <= 0.40) return 'Low'
  if (val <= 0.60) return 'Moderate'
  if (val <= 0.80) return 'High'
  return 'Critical Backlash'
}
function getControversyRiskTone(val) {
  if (val <= 0.40) return 'ready'
  if (val <= 0.60) return 'mixed'
  return 'offline'
}
function formatNumber(value) {
  const n = Number(value)
  return isNaN(n) ? 'N/A' : n.toFixed(2)
}
function formatPlatformLabel(platform) {
  if (!platform) return 'N/A'
  const m = { goodreads: 'Goodreads', booktok: 'BookTok', reddit: 'Reddit', bookstagram: 'Bookstagram', x: 'X/Twitter', newsletter: 'Newsletter', bookclub: 'Book Club' }
  return m[platform.toLowerCase()] || platform
}
function formatPlatformTabName(platform) {
  if (platform === 'all') return 'All Platforms'
  return formatPlatformLabel(platform)
}
function formatRadarLabel(key) {
  if (!key) return ''
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}
function formatPrivacyMode(mode) {
  if (!mode) return 'N/A'
  return mode.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}
function getStarPercentage(star) {
  if (!report.value?.scorecard?.rating_distribution?.distribution) return 0
  const val = report.value.scorecard.rating_distribution.distribution[`${star}_star`]
  return Math.round((Number(val) || 0) * 100)
}
function getComponentScoreTone(val) {
  if (val >= 0.75) return 'text-ready'
  if (val >= 0.50) return 'text-mixed'
  return 'text-offline'
}
function getDnfDriverTone(val) {
  if (val <= 0.25) return 'ready'
  if (val <= 0.50) return 'mixed'
  return 'offline'
}
function getRiskLevelTone(val) {
  if (val <= 0.35) return 'ready'
  if (val <= 0.65) return 'mixed'
  return 'offline'
}
function getPriorityClass(score) {
  if (score >= 0.75) return 'critical'
  if (score >= 0.55) return 'high'
  if (score >= 0.35) return 'medium'
  return 'low'
}
function getPriorityLabel(score) {
  if (score >= 0.75) return 'Critical'
  if (score >= 0.55) return 'High'
  if (score >= 0.35) return 'Medium'
  return 'Low'
}
function getFormatDate() {
  return new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
}

// =========================================================================
// Editor Board — derived from scorecard data
// =========================================================================
const editorBoard = computed(() => {
  if (!report.value) return []
  const sc = report.value.scorecard || {}
  const dnf = sc.dnf || {}
  const rat = sc.rating_distribution || {}
  const con = sc.controversy || {}
  const viral = sc.viral || {}
  const quote = sc.quoteability || {}
  const rev = sc.revision_priority || {}
  const topIssue = rev.ranked_items?.[0]
  const dnfRisk = Number(dnf.dnf_risk) || 0
  const contRisk = Number(con.controversy_risk) || 0
  const ratMean = Number(rat.predicted_mean_rating) || 3.5
  const quoteScore = Number(quote.quoteability_score) || 0.5
  const maxViral = Object.values(viral.platform_scores || {}).reduce((a, b) => Math.max(a, Number(b)), 0)

  const scoreTone = (s) => s >= 70 ? 'ready' : s >= 45 ? 'mixed' : 'offline'

  const editors = [
    {
      role: 'Structural Architect',
      icon: '🏗️',
      score: Math.round(100 - dnfRisk * 80),
      scoreTone: scoreTone(Math.round(100 - dnfRisk * 80)),
      topConcern: dnfRisk > 0.4
        ? `High DNF pressure (${Math.round(dnfRisk * 100)}%) indicates structural drag.`
        : 'Structure holds — low reader abandonment signal.',
      whyItMatters: 'Structural pacing is the primary determinant of whether readers complete the manuscript and recommend it to others.',
      affectedSection: topIssue?.item_id || 'chapter_1',
      recommendedFix: dnfRisk > 0.4
        ? 'Audit mid-section chapters for pacing drag. Tighten transitions and ensure each chapter ends on a micro-tension hook.'
        : 'Maintain current structure. Consider slight elevation of mid-act tension.',
      expectedEffect: dnfRisk > 0.4
        ? 'Structural tightening expected to reduce DNF risk by 10–20% and improve reader completion rate.'
        : 'No major structural intervention needed.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'Commercial Publishing Editor',
      icon: '💼',
      score: Math.round(((ratMean - 1) / 4) * 100),
      scoreTone: scoreTone(Math.round(((ratMean - 1) / 4) * 100)),
      topConcern: ratMean < 3.5
        ? `Predicted mean rating of ${formatNumber(ratMean)}★ is below commercial threshold.`
        : `Predicted mean rating of ${formatNumber(ratMean)}★ is commercially viable.`,
      whyItMatters: 'Commercial publishers target 4.0+ mean reader ratings for frontlist positioning. Below 3.5 indicates repositioning risk.',
      affectedSection: rat.component_scores ? Object.entries(rat.component_scores).sort((a, b) => a[1] - b[1])[0]?.[0] || 'overall' : 'overall',
      recommendedFix: ratMean < 3.5
        ? 'Strengthen the opening hook, tighten packaging language in the blurb, and ensure the first chapter delivers on the cover promise.'
        : 'Focus on differentiation hooks for sub-genre positioning.',
      expectedEffect: 'Each 0.1-star lift at scale translates to 5–8% improvement in review funnel conversion.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'Literary Voice Guardian',
      icon: '🖋️',
      score: Math.round(quoteScore * 100),
      scoreTone: scoreTone(Math.round(quoteScore * 100)),
      topConcern: quoteScore < 0.5
        ? 'Quoteability is low — few excerpt-worthy lines found in the simulation.'
        : `Quoteability score of ${Math.round(quoteScore * 100)}% — strong excerpt candidates detected.`,
      whyItMatters: 'Distinctive voice drives word-of-mouth, BookTok virality, and literary positioning. Quoteable prose is the primary organic marketing asset.',
      affectedSection: quote.quote_candidates?.[0]?.source || 'prose',
      recommendedFix: quoteScore < 0.5
        ? 'Identify 3–5 potential "signature lines" per chapter. Sharpen image-making language and emotional clarity.'
        : 'Highlight the top 3 quote candidates in ARC and early reader materials.',
      expectedEffect: 'Improving quoteability by 10% correlates with ~15% improvement in BookTok share potential.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'Evidence & Credibility Editor',
      icon: '🔬',
      score: Math.round(100 - (Number(con.radar?.claim_hazard || 0)) * 100),
      scoreTone: scoreTone(Math.round(100 - (Number(con.radar?.claim_hazard || 0)) * 100)),
      topConcern: (Number(con.radar?.claim_hazard || 0)) > 0.4
        ? `Claim hazard score of ${Math.round((Number(con.radar?.claim_hazard || 0)) * 100)}% — factual integrity is at risk.`
        : 'Claim hazard is low — factual content appears well-supported.',
      whyItMatters: 'Readers, critics, and algorithms flag unsupported claims. High claim hazard drives negative Reddit and Goodreads reviews.',
      affectedSection: 'nonfiction_claims',
      recommendedFix: (Number(con.radar?.claim_hazard || 0)) > 0.4
        ? 'Audit all factual assertions for citation support. Soften absolute language where evidence is weak.'
        : 'Maintain citation discipline. Add a brief methodology note for readers expecting rigour.',
      expectedEffect: 'Reducing claim hazard reduces controversy risk by approximately 0.1–0.2 points.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'Indian Cultural Context Editor',
      icon: '🪔',
      score: Math.round(100 - (Number(con.radar?.ideological_tension || 0)) * 60),
      scoreTone: scoreTone(Math.round(100 - (Number(con.radar?.ideological_tension || 0)) * 60)),
      topConcern: (Number(con.radar?.ideological_tension || 0)) > 0.5
        ? 'Elevated ideological tension detected — cultural representation may need review.'
        : 'Cultural signals within acceptable range for broad Indian readership.',
      whyItMatters: 'Indian readership and publishing markets have specific expectations around cultural authenticity, family values representation, and regional sensitivities.',
      affectedSection: 'cultural_framing',
      recommendedFix: (Number(con.radar?.ideological_tension || 0)) > 0.5
        ? 'Consult a sensitivity reader with regional Indian market experience. Review character dynamics for unintentional misrepresentation.'
        : 'Consider adding a cultural note or author reflection for non-Indian readers.',
      expectedEffect: 'Authentic cultural framing improves reception from Indian readership segments by 8–15%.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 80)}%`,
    },
    {
      role: 'Reader Psychology Editor',
      icon: '🧠',
      score: Math.round(100 - dnfRisk * 50 - contRisk * 30),
      scoreTone: scoreTone(Math.round(100 - dnfRisk * 50 - contRisk * 30)),
      topConcern: dnfRisk > 0.4
        ? 'Cognitive load and confusion markers spike reader disengagement mid-manuscript.'
        : 'Reader cognitive flow appears uninterrupted based on confusion and pacing metrics.',
      whyItMatters: 'Reader psychology determines whether a book is recommended or abandoned. Confusion, unmet expectations, and voice misalignment are silent DNF drivers.',
      affectedSection: Object.entries(dnf.component_scores || {}).sort((a, b) => b[1] - a[1])[0]?.[0] || 'chapter_3',
      recommendedFix: 'Ensure character motivations are transparent at key decision points. Reduce exposition blocks exceeding 3 consecutive paragraphs.',
      expectedEffect: 'Reducing confusion markers is expected to lift mean comprehension score by 5–10%.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'Developmental Psychology Editor',
      icon: '🎓',
      score: Math.round(Number(rat.component_scores?.character_attachment || 0.6) * 100),
      scoreTone: scoreTone(Math.round(Number(rat.component_scores?.character_attachment || 0.6) * 100)),
      topConcern: (Number(rat.component_scores?.character_attachment || 0.6)) < 0.6
        ? 'Character attachment score is low — readers may disengage from protagonist arc.'
        : `Character attachment at ${Math.round(Number(rat.component_scores?.character_attachment || 0.6) * 100)}% — strong reader identification signals.`,
      whyItMatters: 'Readers invest in characters before they invest in plot. Weak attachment is the second most common reason for book abandonment after pacing.',
      affectedSection: 'character_arc',
      recommendedFix: 'Ensure protagonist desire lines are established in Chapter 1. Add a visible internal wound or moral dilemma by Chapter 3.',
      expectedEffect: 'A 10% lift in character attachment corresponds to a 0.2-star improvement in predicted mean rating.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'Genre Positioning Editor',
      icon: '📚',
      score: Math.round(Number(rat.component_scores?.packaging_fit || 0.7) * 100),
      scoreTone: scoreTone(Math.round(Number(rat.component_scores?.packaging_fit || 0.7) * 100)),
      topConcern: (Number(rat.component_scores?.packaging_fit || 0.7)) < 0.6
        ? 'Packaging mismatch detected — cover promise may not align with interior experience.'
        : 'Genre fit is solid — reader expectations appear well-managed.',
      whyItMatters: 'Packaging mismatches drive one-star reviews from readers who expected a different book. This is the primary source of controversy-driven backlash.',
      affectedSection: 'blurb_cover',
      recommendedFix: 'Audit the opening chapter against the jacket blurb. Ensure the first page delivers on the genre promise within the first 500 words.',
      expectedEffect: 'Tighter genre positioning reduces packaging mismatch controversy by 0.1–0.2 points.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'DNF Risk Editor',
      icon: '🚨',
      score: Math.round((1 - dnfRisk) * 100),
      scoreTone: scoreTone(Math.round((1 - dnfRisk) * 100)),
      topConcern: dnfRisk > 0.4
        ? `DNF risk at ${Math.round(dnfRisk * 100)}% — multiple chapter abandonment points identified.`
        : `DNF risk at ${Math.round(dnfRisk * 100)}% — readers are unlikely to abandon before completion.`,
      whyItMatters: 'Did Not Finish rate directly impacts reviews, word-of-mouth, and algorithm ranking on reading platforms.',
      affectedSection: report.value.scorecard?.dnf?.chapter_points?.[0]?.section_id || 'chapter_flow',
      recommendedFix: dnfRisk > 0.4
        ? `Focus on Chapter ${report.value.scorecard?.dnf?.chapter_points?.[0]?.chapter_number || 3} — the highest abandonment pressure point. Add a chapter-end hook.`
        : 'Maintain current chapter-end tension architecture.',
      expectedEffect: 'Reducing DNF by 5% at scale is estimated to improve visibility on reading algorithm-curated lists by 10–15%.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
    {
      role: 'Virality & Quoteability Editor',
      icon: '⚡',
      score: Math.round(maxViral * 100),
      scoreTone: scoreTone(Math.round(maxViral * 100)),
      topConcern: maxViral < 0.5
        ? 'Viral potential is below threshold — limited organic spread predicted across all platforms.'
        : `Strongest viral signal on ${maxViralPlatformName.value} at ${Math.round(maxViral * 100)}%.`,
      whyItMatters: 'BookTok and Bookstagram virality now drive 30–50% of debut fiction discovery. Quoteability is the primary viral asset.',
      affectedSection: 'highlight_lines',
      recommendedFix: maxViral < 0.5
        ? 'Create 3 explicit "moment" chapters designed for social media clipping — emotionally intense, visually writeable, and under 300 words each.'
        : `Develop a launch strategy targeting ${maxViralPlatformName.value} specifically. Prepare quote assets and excerpt sets.`,
      expectedEffect: `A ${Math.round(maxViral * 100) + 10}%+ viral score on ${maxViralPlatformName.value} is achievable with targeted excerpt seeding.`,
      confidence: `${Math.round((report.value.confidence || 0.7) * 90)}%`,
    },
    {
      role: 'Sensitivity & Safety Editor',
      icon: '🛡️',
      score: Math.round(100 - (Number(con.radar?.character_behavior_challenge || 0)) * 80),
      scoreTone: scoreTone(Math.round(100 - (Number(con.radar?.character_behavior_challenge || 0)) * 80)),
      topConcern: (Number(con.radar?.character_behavior_challenge || 0)) > 0.5
        ? 'Character behavior patterns may raise sensitivity concerns in key reader segments.'
        : 'No significant character-level sensitivity flags detected.',
      whyItMatters: 'Sensitivity issues can suppress review volume from important cohorts and create reputational risk for the author in online communities.',
      affectedSection: 'character_dynamics',
      recommendedFix: (Number(con.radar?.character_behavior_challenge || 0)) > 0.5
        ? 'Commission a sensitivity read focusing on character dynamics, power relationships, and tonal register.'
        : 'Standard sensitivity review recommended before final submission.',
      expectedEffect: 'Addressing sensitivity flags reduces controversy risk by 0.05–0.15 points and improves reception from inclusivity-focused reader cohorts.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 85)}%`,
    },
    {
      role: 'Line-Level Compression Editor',
      icon: '✂️',
      score: Math.round(Number(rat.component_scores?.prose_quality || 0.7) * 100),
      scoreTone: scoreTone(Math.round(Number(rat.component_scores?.prose_quality || 0.7) * 100)),
      topConcern: (Number(rat.component_scores?.prose_quality || 0.7)) < 0.65
        ? 'Prose quality score is below threshold — compression and line editing are needed.'
        : `Prose quality at ${Math.round(Number(rat.component_scores?.prose_quality || 0.7) * 100)}% — line-level clarity is strong.`,
      whyItMatters: 'Prose clarity directly affects comprehension scores and DNF pressure. Dense or redundant prose drives reader fatigue.',
      affectedSection: 'prose_density',
      recommendedFix: (Number(rat.component_scores?.prose_quality || 0.7)) < 0.65
        ? 'Target a 10–15% word count reduction in exposition-heavy sections. Prioritise action verbs and eliminate adverb clusters.'
        : 'Focus on consistency — ensure voice remains uniform across chapters.',
      expectedEffect: '10% prose compression typically improves pacing score by 5–8 points and reduces length fatigue marker.',
      confidence: `${Math.round((report.value.confidence || 0.7) * 100)}%`,
    },
  ]
  return editors
})

// =========================================================================
// Export handler
// =========================================================================
const copySuccess = ref(false)
const copyExecSuccess = ref(false)
const copyRevSuccess = ref(false)

async function handleExport(type) {
  if (!report.value) return
  try {
    if (type === 'json') { generateJson(report.value, session.value) }
    else if (type === 'markdown') { generateMarkdown(report.value, session.value) }
    else if (type === 'docx') { await generateDocx(report.value, session.value) }
    else if (type === 'pdf') { generatePdf(report.value, session.value) }
    else if (type === 'png') {
      const element = document.getElementById('png-summary-card')
      if (element) {
        element.style.display = 'block'
        const canvas = await html2canvas(element, { scale: 2, backgroundColor: '#ffffff' })
        element.style.display = 'none'
        const dataUrl = canvas.toDataURL('image/png')
        const a = document.createElement('a')
        a.href = dataUrl
        a.download = `swarmbook_summary_${session.value.projectId || 'demo'}.png`
        a.click()
      }
    }
  } catch (err) {
    console.error(`Export failed [${type}]:`, err)
    alert(`Failed to export ${type.toUpperCase()}: ` + err.message)
  }
}

async function handleCopy() {
  if (!report.value) return
  try {
    await copyToClipboard(report.value, session.value)
    copySuccess.value = true
    setTimeout(() => { copySuccess.value = false }, 2000)
  } catch (err) {
    console.error('Clipboard copy failed:', err)
    alert('Failed to copy: ' + err.message)
  }
}

async function handleCopyExec() {
  if (!report.value) return
  try {
    await copyExecutiveSummary(report.value)
    copyExecSuccess.value = true
    setTimeout(() => { copyExecSuccess.value = false }, 2000)
  } catch (err) {
    console.error('Executive summary copy failed:', err)
    alert('Failed to copy executive summary: ' + err.message)
  }
}

async function handleCopyRevision() {
  if (!report.value) return
  try {
    await copyRevisionPlan(report.value)
    copyRevSuccess.value = true
    setTimeout(() => { copyRevSuccess.value = false }, 2000)
  } catch (err) {
    console.error('Revision plan copy failed:', err)
    alert('Failed to copy revision plan: ' + err.message)
  }
}

// =========================================================================
// Demo mock loader (preserved for diagnostic testing)
// =========================================================================
const MOCK_REPORT = {
  report_id: 'report_demo_123456',
  project_id: 'proj_demo_987',
  simulation_id: 'run_demo_789',
  privacy_mode: 'hybrid_safe',
  draft_id: 'draft_v1',
  version: '1.0.0',
  title: 'The Antigravity Paradox',
  summary: 'Predicted mean rating is 4.12 with DNF risk at 0.22. Best synthetic spread is on booktok, while the main blocker is chapter 3 which carries DNF pressure at 0.58.',
  confidence: 0.85,
  audience_response: {
    personas_count: 30, posts_count: 5, mean_rating: 4.12, recommendation_mean: 0.78,
    top_platforms: ['booktok', 'goodreads', 'bookstagram']
  },
  scorecard: {
    rating_distribution: {
      predicted_mean_rating: 4.12,
      distribution: { '1_star': 0.05, '2_star': 0.08, '3_star': 0.12, '4_star': 0.45, '5_star': 0.30 },
      confidence_band: { low: 3.85, mid: 4.12, high: 4.35, label: 'high' },
      component_scores: { comprehension: 0.88, emotional_payoff: 0.92, prose_quality: 0.85, pacing: 0.76, character_attachment: 0.90, packaging_fit: 0.82 },
      evidence_refs: ['doc_dna_1', 'style_map_1']
    },
    dnf: {
      dnf_risk: 0.22,
      confidence_band: { low: 0.15, mid: 0.22, high: 0.32, label: 'moderate' },
      component_scores: { opening_drag: 0.28, confusion: 0.18, pacing_drag: 0.32, unmet_expectation: 0.15, voice_misalignment: 0.20, length_fatigue: 0.25 },
      chapter_points: [
        { section_id: 'chapter_3', chapter_number: 3, dnf_points: 0.58, reason: 'Slow pacing; high reader friction around character decisions' },
        { section_id: 'chapter_1', chapter_number: 1, dnf_points: 0.35, reason: 'Dense worldbuilding introduction; confusion markers' },
        { section_id: 'chapter_7', chapter_number: 7, dnf_points: 0.24, reason: 'Pacing dip in intermediate act transition' }
      ]
    },
    controversy: {
      controversy_risk: 0.48,
      confidence_band: { low: 0.38, mid: 0.48, high: 0.58, label: 'moderate' },
      radar: { ideological_tension: 0.55, claim_hazard: 0.30, moral_disagreement: 0.62, tonal_disruption: 0.40, character_behavior_challenge: 0.50, packaging_mismatch: 0.32 },
      hotspots: ['claim:claim_ethics_v1', 'risk:moral_disagreement_ch3', 'packaging:audience_expectation_gap']
    },
    polarization: {
      polarization_score: 0.52,
      confidence_band: { low: 0.42, mid: 0.52, high: 0.62, label: 'moderate' },
      component_scores: { taste_split: 0.58, ideology_split: 0.62, prose_split: 0.35, ending_split: 0.70, genre_expectation_split: 0.40 },
      split_signals: ['wide_rating_spread', 'mixed_sentiment', 'reaction_backlash']
    },
    quoteability: {
      quoteability_score: 0.84,
      confidence_band: { low: 0.76, mid: 0.84, high: 0.90, label: 'high' },
      component_scores: { line_density: 0.88, image_making_language: 0.85, emotional_clarity: 0.82, repetition_resonance: 0.78, scene_peak_strength: 0.90, excerpt_friendly_structure: 0.80 },
      quote_candidates: [
        { text: 'In the shadow of the gravity well, we learned that falling was just another form of flight.', source: 'chapter_3' },
        { text: 'Nothing is heavier than the weight of a secret left unshared among the stars.', source: 'chapter_1' },
        { text: 'They promised us we would break the orbit, but we only succeeded in breaking ourselves.', source: 'reaction_rec_3' }
      ]
    },
    viral: {
      platform_scores: { goodreads: 0.72, booktok: 0.88, reddit: 0.55, bookstagram: 0.82, x: 0.60, newsletter: 0.65, bookclub: 0.78 },
      top_platforms: ['booktok', 'bookstagram', 'bookclub'],
      confidence_band: { low: 0.78, mid: 0.85, high: 0.92, label: 'high' },
      component_scores: { emotional_spike: 0.88, trope_visibility: 0.75, novelty: 0.82, controversy: 0.48, quoteability: 0.84, concise_explainability: 0.70 }
    },
    revision_priority: {
      ranked_items: [
        { item_id: 'chapter_3', item_type: 'chapter', priority_score: 0.78, reasons: ['High DNF points (0.58)', 'Slow pacing', 'Negative sentiment spikes'], evidence_refs: ['chapter_3_summary'] },
        { item_id: 'claim_ethics_v1', item_type: 'claim', priority_score: 0.62, reasons: ['Moral disagreement (0.62)', 'Polarizing Reddit reviews'], evidence_refs: ['nonfiction_claims'] },
        { item_id: 'style_prose', item_type: 'style', priority_score: 0.45, reasons: ['Low clarity score', 'Dampened reader rating'], evidence_refs: ['style_map'] }
      ]
    }
  },
  segment_insights: [
    { segment: 'Goodreads:Goodreads', rating_mean: 3.92, recommendation_mean: 0.68, signal: 'positive', sample_personas: ['Casey L.', 'Devon M.'], sentiments: ['solid pacing', 'liked worldbuilding'] },
    { segment: 'BookTok:BookTok', rating_mean: 4.54, recommendation_mean: 0.92, signal: 'positive', sample_personas: ['Aria Reed', 'Leo Vance'], sentiments: ['obsessed with quotes', 'emotional ending'] },
    { segment: 'Reddit:Reddit', rating_mean: 3.12, recommendation_mean: 0.42, signal: 'mixed', sample_personas: ['Skeptic Reader', 'Hard SciFi Guy'], sentiments: ['contested physics claims', 'slow start'] }
  ],
  top_risks: [
    'Chapter 3 pacing is slow, risking initial drop-off.',
    'Claims regarding physics viability in chapter 4 feel weak and polarize Reddit.',
    'Ambiguous ending in chapter 12 leaves casual readers unsatisfied.'
  ],
  top_strengths: [
    'Prose quoteability is exceptional, especially on BookTok.',
    'High character attachment potential for the main protagonist.',
    'Vivid imagery and strong emotional peaks drive high engagement.'
  ],
  revision_priorities: ['chapter:chapter_3 (0.78)', 'claim:claim_ethics_v1 (0.62)', 'style:style_prose (0.45)'],
  uncertainty_notes: [
    'Outputs are synthetic stress-test signals, not a guarantee of market behavior.',
    'Prediction confidence is lower for the hard science components due to mixed reader interest.'
  ]
}

const MOCK_PLATFORM_POSTS = [
  { post_id: 'post_1', persona_id: 'persona_aria', platform: 'booktok', round_number: 1, rating: 5.0, body: 'OMG guys, "The Antigravity Paradox" has the most beautiful prose! #booktok #mustread', hashtags: ['booktok', 'mustread'], payload: { hook_line: 'OMG guys', viral_trigger: true } },
  { post_id: 'post_2', persona_id: 'persona_devon', platform: 'goodreads', round_number: 1, rating: 4.0, body: 'A solid sci-fi read. Pacing in chapter 3 was sluggish, but the ending pays off.', shelf_tags: ['scifi', 'goodreads-challenge'] },
  { post_id: 'post_3', persona_id: 'persona_skeptic', platform: 'reddit', round_number: 1, rating: 2.0, body: 'The physics claims in chapter 4 make zero sense. Pacing drags in chapter 3. 2/5 stars.', payload: { hot_take: true } },
  { post_id: 'post_4', persona_id: 'persona_leo', platform: 'bookstagram', round_number: 1, rating: 5.0, body: 'Just finished this masterpiece. Highly recommend it to all book clubs! 🌌✨', hashtags: ['bookstagram', 'aesthetic'] },
  { post_id: 'post_5', persona_id: 'persona_x', platform: 'x', round_number: 1, rating: 3.0, body: 'Controversial take: great ambition, weak physics. Debate incoming. 🧵', payload: { hot_take: true } }
]

function loadDemoMock() {
  report.value = MOCK_REPORT
  const mock = { run_id: 'run_demo_789', platform_posts: MOCK_PLATFORM_POSTS, reader_personas: [
    { persona_id: 'persona_aria', display_name: 'Aria Reed' },
    { persona_id: 'persona_devon', display_name: 'Devon M.' },
    { persona_id: 'persona_skeptic', display_name: 'Skeptic Reader' },
    { persona_id: 'persona_leo', display_name: 'Leo Vance' },
    { persona_id: 'persona_x', display_name: 'Critical X' }
  ]}
  session.value = updateSwarmbookSession({ projectId: 'proj_demo_987', report: MOCK_REPORT, simulationRun: mock })
}

// =========================================================================
// API Loader
// =========================================================================
async function ensureReport() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId) {
    if (route.params.projectId) {
      session.value = updateSwarmbookSession({ projectId: route.params.projectId })
    } else {
      router.replace({ name: 'SwarmbookHome' })
      return
    }
  }
  if (report.value) return
  loading.value = true
  loadingMessage.value = 'Loading latest report from backend...'
  error.value = ''
  try {
    const response = await getBookSimReport(session.value.projectId)
    if (response.data) {
      report.value = response.data
      session.value = updateSwarmbookSession({ report: response.data })
    }
  } catch (requestError) {
    console.warn('Report fetch failed (expected if server is down):', requestError.message)
  } finally {
    loading.value = false
    loadingMessage.value = ''
  }
}

onMounted(() => { ensureReport() })
</script>

<style scoped>
/* ===========================================================================
   FOCUS STATES — WCAG 2.2 AA
=========================================================================== */
button:focus-visible,
a:focus-visible,
[role="tab"]:focus-visible,
[role="button"]:focus-visible,
[tabindex="0"]:focus-visible {
  outline: 2px solid #FF4500 !important;
  outline-offset: 3px !important;
}

/* ===========================================================================
   STICKY REPORT BAR
=========================================================================== */
.report-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 12px 20px;
  background: rgba(255,255,255,0.97);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 20px;
  backdrop-filter: blur(8px);
}
.sticky-report-bar {
  position: sticky;
  top: 0;
  z-index: 200;
}
.report-bar-identity {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}
.report-bar-title {
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.2px;
}
.report-bar-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.meta-chip {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
}
.meta-chip.local_only { background: #d1fae5; color: #065f46; border-color: #a7f3d0; }
.meta-chip.hybrid_safe { background: #fef3c7; color: #92400e; border-color: #fde68a; }
.meta-chip.cloud_quality { background: #dbeafe; color: #1e40af; border-color: #bfdbfe; }
.meta-chip.confidence { background: #faf5ff; color: #6b21a8; border-color: #f3e8ff; }
.meta-chip.draft { background: #f1f5f9; color: #334155; border-color: #e2e8f0; }

.report-bar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.rb-btn {
  background: #ffffff;
  color: #0f172a;
  border: 1px solid #cbd5e1;
  padding: 8px 14px;
  font-size: 0.82rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.rb-btn:hover { background: #f8fafc; border-color: #94a3b8; }
.rb-btn.rb-primary { background: #000; color: #fff; border-color: #000; }
.rb-btn.rb-primary:hover { background: #1e293b; }

/* ===========================================================================
   COMMAND CENTER
=========================================================================== */
.command-center {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 28px;
}

/* 6-card metrics row */
.cc-metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}

.cc-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 0.15s;
}
.cc-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.cc-card.cc-warn { border-top: 3px solid #f59e0b; }
.cc-card.cc-alert { border-top: 3px solid #ef4444; }
.cc-card.cc-readiness.ready { border-left: 4px solid #10b981; }
.cc-card.cc-readiness.mixed { border-left: 4px solid #f59e0b; }
.cc-card.cc-readiness.offline { border-left: 4px solid #ef4444; }

.cc-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #64748b;
}
.cc-score {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.cc-score strong {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}
.cc-priority-name {
  font-size: 1rem !important;
  font-family: 'JetBrains Mono', monospace;
  word-break: break-all;
}
.cc-sub {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.3;
}
.cc-sub-inline {
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  font-family: 'JetBrains Mono', monospace;
}
.cc-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}
.cc-badge.ready { background: #d1fae5; color: #065f46; }
.cc-badge.mixed { background: #fef3c7; color: #92400e; }
.cc-badge.offline { background: #fef2f2; color: #991b1b; }
.cc-bar {
  height: 5px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 4px;
}
.cc-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.cc-readiness.ready .cc-bar-fill { background: #10b981; }
.cc-readiness.mixed .cc-bar-fill { background: #f59e0b; }
.cc-readiness.offline .cc-bar-fill { background: #ef4444; }

/* Verdict + Moves row */
.cc-verdict-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 768px) {
  .cc-verdict-row { grid-template-columns: 1fr; }
}

.cc-verdict-card,
.cc-moves-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.cc-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 800;
  color: #FF4500;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}
.cc-verdict-text {
  font-size: 1rem;
  line-height: 1.65;
  color: #1e293b;
  border-left: 3px solid #000;
  padding-left: 16px;
  margin: 0;
  font-style: normal;
}
.cc-verdict-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Top 3 moves */
.cc-moves-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.cc-move-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.cc-move-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  font-weight: 800;
  color: #FF4500;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.cc-move-body strong {
  font-size: 0.88rem;
  color: #0f172a;
}
.cc-move-body p {
  font-size: 0.78rem;
  color: #475569;
  margin: 4px 0 6px;
  line-height: 1.4;
}
.cc-see-more-btn {
  background: transparent;
  border: none;
  color: #FF4500;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  align-self: flex-start;
}
.cc-empty-note {
  font-size: 0.82rem;
  color: #94a3b8;
  font-style: italic;
}

/* ===========================================================================
   MAIN TAB NAVIGATION
=========================================================================== */
.report-tabs-shell {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.tab-nav {
  display: flex;
  gap: 2px;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 0;
  overflow-x: auto;
  padding-bottom: 0;
  flex-wrap: nowrap;
  -webkit-overflow-scrolling: touch;
}

.tab-nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: 0.83rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
  border-radius: 4px 4px 0 0;
}
.tab-nav-btn:hover { color: #0f172a; background: #f8fafc; }
.tab-nav-btn.active {
  color: #000000;
  border-bottom-color: #FF4500;
  font-weight: 700;
}
.tab-icon { font-size: 1rem; }
.tab-label { font-size: 0.83rem; }

.tab-panel {
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ===========================================================================
   PANEL LAYOUT UTILITIES
=========================================================================== */
.panel-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 900px) {
  .panel-grid-2 { grid-template-columns: 1fr; }
}

.panel-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 22px 24px;
}

.panel-intro h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 6px;
}
.panel-intro .muted-p { margin-bottom: 12px; }

.card-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 800;
  color: #FF4500;
  letter-spacing: 1px;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.panel-card h2 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 14px;
}

.margin-bottom-lg { margin-bottom: 20px; }
.margin-top-md { margin-top: 16px; }
.muted-p { color: #64748b; font-size: 0.88rem; line-height: 1.4; }
.muted-note { color: #94a3b8; font-size: 0.82rem; font-style: italic; }
.text-center { text-align: center; }
.padding-xl { padding: 48px; }
.text-ready { color: #10b981; }
.text-mixed { color: #f59e0b; }
.text-offline { color: #ef4444; }

/* ===========================================================================
   BUTTONS
=========================================================================== */
.primary-btn {
  background: #000;
  color: #fff;
  border: 1px solid #000;
  padding: 9px 18px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}
.primary-btn:hover { background: #1e293b; }

.ghost-btn {
  background: #ffffff;
  color: #0f172a;
  border: 1px solid #cbd5e1;
  padding: 9px 18px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s, border-color 0.15s;
}
.ghost-btn:hover { background: #f8fafc; border-color: #94a3b8; }

.collapse-trigger-btn {
  background: transparent;
  border: none;
  color: #FF4500;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 0;
}

/* ===========================================================================
   STAR HISTOGRAM (Overview)
=========================================================================== */
.rating-overall-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 6px;
}
.big-stars {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
}
.star-histogram {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin-bottom: 20px;
}
.histogram-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.star-text-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  width: 36px;
  text-align: right;
}
.bar-track {
  flex: 1;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}
.bar-star-5 { background: #10b981; }
.bar-star-4 { background: #34d399; }
.bar-star-3 { background: #fbbf24; }
.bar-star-2 { background: #f97316; }
.bar-star-1 { background: #f43f5e; }
.star-pct {
  font-size: 0.78rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #1e293b;
  width: 36px;
}

/* Driver pills */
.sub-components-box {
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}
.sub-components-box h3,
.viral-drivers-box h3,
.hooks-box h3,
.warning-box h3,
.uncertainty-box h3,
.hotspots-box h3 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  text-transform: uppercase;
  color: #475569;
  margin-bottom: 10px;
  font-weight: 800;
}
.drivers-row { display: flex; flex-wrap: wrap; gap: 8px; }
.driver-pill {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 0.76rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.driver-pill .label { color: #64748b; }

/* Segments table */
.table-container { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 6px; }
.segments-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
.segments-table th {
  background: #f8fafc;
  color: #475569;
  font-weight: 700;
  padding: 10px 14px;
  border-bottom: 1px solid #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: left;
}
.segments-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}
.segments-table tr:last-child td { border-bottom: none; }
.empty-table-cell { text-align: center; padding: 28px !important; color: #94a3b8; font-style: italic; }

.signal-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 4px;
}
.signal-badge.positive { background: #d1fae5; color: #065f46; }
.signal-badge.mixed { background: #fef3c7; color: #92400e; }
.signal-badge.negative { background: #fef2f2; color: #991b1b; }

/* Viral platform chart */
.viral-platform-chart { display: flex; flex-direction: column; gap: 11px; }
.platform-bar-row { display: flex; align-items: center; gap: 10px; }
.platform-name-label { font-size: 0.76rem; font-weight: 600; color: #475569; width: 88px; text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.platform-bar-track { flex: 1; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden; }
.platform-bar-fill { height: 100%; border-radius: 4px; transition: width 0.4s ease; }
.platform-color-goodreads { background: #774c2a; }
.platform-color-booktok { background: #01f2ff; box-shadow: 0 0 4px #01f2ff; }
.platform-color-reddit { background: #ff4500; }
.platform-color-bookstagram { background: #c13584; }
.platform-color-x { background: #0f172a; }
.platform-color-newsletter { background: #3b82f6; }
.platform-color-bookclub { background: #10b981; }
.platform-pct { font-size: 0.76rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #1e293b; width: 34px; }

/* Radar bars */
.radar-card-grid { display: flex; flex-direction: column; gap: 12px; }
.radar-bar-item { display: flex; flex-direction: column; gap: 4px; }
.radar-bar-header { display: flex; justify-content: space-between; font-size: 0.78rem; }
.radar-bar-header .label { font-weight: 600; color: #334155; }
.radar-bar-header strong { font-family: 'JetBrains Mono', monospace; }
.radar-bar-track { height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.radar-bar-fill { height: 100%; border-radius: 3px; }
.radar-bar-fill.ready { background: #10b981; }
.radar-bar-fill.mixed { background: #f59e0b; }
.radar-bar-fill.offline { background: #ef4444; }

/* Readiness card mini */
.readiness-card.ready { border-left: 4px solid #10b981; padding: 12px; border-radius: 6px; background: #f0fdf4; }
.readiness-card.mixed { border-left: 4px solid #f59e0b; padding: 12px; border-radius: 6px; background: #fffbeb; }
.readiness-card.offline { border-left: 4px solid #ef4444; padding: 12px; border-radius: 6px; background: #fef2f2; }

/* ===========================================================================
   EDITOR BOARD
=========================================================================== */
.editors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 18px;
}
.editor-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.15s;
}
.editor-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.07); }

.editor-card-header {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 16px 18px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
.editor-icon {
  font-size: 1.6rem;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}
.editor-role {
  font-size: 0.9rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
  line-height: 1.2;
}
.editor-score-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.editor-score-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}
.editor-score-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}
.editor-score-fill.ready { background: #10b981; }
.editor-score-fill.mixed { background: #f59e0b; }
.editor-score-fill.offline { background: #ef4444; }
.editor-score-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  font-weight: 800;
  width: 36px;
  text-align: right;
}
.text-ready { color: #10b981; }
.text-mixed { color: #f59e0b; }
.text-offline { color: #ef4444; }

.editor-card-body {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.editor-field { display: flex; flex-direction: column; gap: 4px; }
.editor-field-row { flex-direction: row; gap: 24px; }
.editor-field-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
}
.editor-field-value {
  font-size: 0.83rem;
  color: #334155;
  line-height: 1.45;
  margin: 0;
}
.editor-field-value.concern { color: #7c3aed; font-weight: 600; }
.editor-field-value.fix { color: #1e3a8a; }
.editor-field-value.effect { color: #065f46; }
.editor-section-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  background: #f1f5f9;
  color: #475569;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}
.editor-conf-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  background: #faf5ff;
  color: #6b21a8;
  border: 1px solid #f3e8ff;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

/* ===========================================================================
   REVISION PLAN
=========================================================================== */
.revision-list { display: flex; flex-direction: column; gap: 10px; }

.revision-item {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}
.item-priority-critical { border-left: 4px solid #ef4444; }
.item-priority-high { border-left: 4px solid #f97316; }
.item-priority-medium { border-left: 4px solid #f59e0b; }
.item-priority-low { border-left: 4px solid #10b981; }

.revision-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  cursor: pointer;
  user-select: none;
  gap: 12px;
  flex-wrap: wrap;
}
.revision-item-header:hover { background: #f8fafc; }

.revision-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.revision-rank {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  font-weight: 800;
  color: #94a3b8;
  width: 28px;
}
.revision-target { font-size: 0.9rem; color: #0f172a; }

.revision-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.revision-impact-chips { display: flex; gap: 6px; }
.impact-chip {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  background: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
}
.expand-chevron {
  font-size: 1.2rem;
  color: #94a3b8;
  transition: transform 0.2s;
  display: inline-block;
}
.expand-chevron.open { transform: rotate(90deg); }

.revision-preview {
  padding: 0 18px 12px;
}
.revision-issue-preview {
  font-size: 0.82rem;
  color: #475569;
  font-style: italic;
}

.revision-detail {
  border-top: 1px solid #f1f5f9;
  padding: 16px 18px;
  background: #fafbfc;
}
.revision-detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 640px) {
  .revision-detail-grid { grid-template-columns: 1fr; }
}
.rd-field { display: flex; flex-direction: column; gap: 6px; }
.rd-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
}
.rd-value { font-size: 0.83rem; color: #334155; margin: 0; }

.evidence-pills-row { display: flex; gap: 6px; flex-wrap: wrap; }
.evidence-pill {
  background: #f1f5f9;
  color: #475569;
  padding: 2px 7px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
}

/* Priority pills */
.priority-label-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  font-weight: 800;
  padding: 3px 7px;
  border-radius: 4px;
  text-transform: uppercase;
  display: inline-block;
}
.priority-label-pill.critical { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
.priority-label-pill.high { background: #fff7ed; color: #f97316; border: 1px solid #ffedd5; }
.priority-label-pill.medium { background: #fef8e6; color: #d97706; border: 1px solid #fef3c7; }
.priority-label-pill.low { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }

.item-type-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 700;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

.reasons-bullet-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 4px; }
.reasons-bullet-list li { font-size: 0.82rem; color: #475569; padding-left: 14px; position: relative; }
.reasons-bullet-list li::before { content: '• '; color: #FF4500; position: absolute; left: 0; }

/* ===========================================================================
   READER REACTIONS TAB
=========================================================================== */
.tab-row-container { overflow-x: auto; margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; }
.tab-row { display: flex; gap: 4px; padding-bottom: 8px; }
.tab-btn {
  background: transparent;
  border: none;
  color: #64748b;
  padding: 8px 14px;
  font-size: 0.83rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s;
  white-space: nowrap;
}
.tab-btn:hover { background: #f1f5f9; color: #0f172a; }
.tab-btn.active { background: #000; color: #fff; }
.tab-count-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  background: rgba(255,69,0,0.15);
  color: #FF4500;
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 700;
}
.tab-btn.active .tab-count-badge { background: #fff; color: #000; }

.feed-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.mock-post-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  transition: transform 0.15s;
}
.mock-post-card:hover { transform: translateY(-2px); }

.post-header { display: flex; justify-content: space-between; align-items: center; }
.user-info { display: flex; align-items: center; gap: 10px; }
.avatar { font-size: 1.2rem; background: #f1f5f9; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.user-meta { display: flex; flex-direction: column; }
.display-name { font-size: 0.82rem; font-weight: 700; color: #1e293b; }
.handle { font-size: 0.7rem; color: #64748b; font-family: 'JetBrains Mono', monospace; }

.post-platform-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
}
.post-platform-tag.goodreads { background: #ecdcc9; color: #5c381c; }
.post-platform-tag.booktok { background: #000; color: #fff; border: 1px solid #00f2fe; }
.post-platform-tag.reddit { background: #ffe9e0; color: #ff4500; }
.post-platform-tag.bookstagram { background: #fde2f3; color: #c13584; }
.post-platform-tag.x { background: #f1f5f9; color: #0f172a; }
.post-platform-tag.newsletter { background: #eff6ff; color: #1e40af; }
.post-platform-tag.bookclub { background: #d1fae5; color: #065f46; }

.post-body { flex: 1; }
.post-stars-row { margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.star-rating { color: #fbbf24; font-size: 0.9rem; }
.rating-value { font-size: 0.72rem; color: #64748b; }
.subreddit-tag { font-size: 0.7rem; color: #475569; font-weight: 700; margin-bottom: 6px; }
.post-text { font-size: 0.85rem; line-height: 1.5; color: #334155; word-break: break-word; }

.tiktok-video-mock {
  height: 100px;
  background: #111113;
  border-radius: 6px;
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.78rem;
  position: relative;
  overflow: hidden;
  border: 1px solid #334155;
}
.video-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0,0,0,0.6);
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.hook-text { font-style: italic; font-size: 0.7rem; color: #cbd5e1; }

.post-hashtags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
.post-hashtags .tag { color: #3b82f6; font-size: 0.76rem; font-weight: 600; }
.mock-post-booktok .tag { color: #00f2fe; }

.post-footer { border-top: 1px solid #f1f5f9; padding-top: 8px; display: flex; gap: 10px; align-items: center; font-size: 0.76rem; color: #64748b; }
.hot-take-label { background: #fff7ed; color: #c2410c; font-weight: 800; font-size: 0.68rem; padding: 2px 5px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; }
.viral-trigger-label { background: #fef8e6; color: #b45309; font-weight: 800; font-size: 0.68rem; padding: 2px 5px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; }

.mock-post-booktok { background: #121214; border-color: #27272a; }
.mock-post-booktok .display-name { color: #f4f4f5; }
.mock-post-booktok .handle { color: #a1a1aa; }
.mock-post-booktok .post-text { color: #e4e4e7; }
.mock-post-booktok .post-footer { border-color: #27272a; color: #a1a1aa; }
.mock-post-booktok .avatar { background: #27272a; }

/* ===========================================================================
   RISKS TAB
=========================================================================== */
.dnf-drivers-list { display: flex; flex-direction: column; gap: 14px; }
.dnf-driver-row { display: flex; flex-direction: column; gap: 5px; }
.dnf-driver-header { display: flex; justify-content: space-between; font-size: 0.8rem; }
.dnf-driver-header .label { font-weight: 600; color: #334155; }
.dnf-driver-header strong { font-family: 'JetBrains Mono', monospace; font-weight: 700; }
.dnf-driver-track { height: 5px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.dnf-driver-fill { height: 100%; border-radius: 3px; }
.dnf-driver-fill.ready { background: #10b981; }
.dnf-driver-fill.mixed { background: #f59e0b; }
.dnf-driver-fill.offline { background: #ef4444; }

.timeline { display: flex; flex-direction: column; position: relative; padding-left: 24px; }
.timeline::before { content: ''; position: absolute; left: 11px; top: 8px; bottom: 8px; width: 2px; background: #e2e8f0; }
.timeline-item { position: relative; padding-bottom: 20px; }
.timeline-item:last-child { padding-bottom: 0; }
.timeline-marker { position: absolute; left: -24px; top: 2px; width: 24px; height: 24px; background: #fff; border: 2px solid #cbd5e1; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 2; }
.marker-num { font-size: 0.68rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #475569; }
.timeline-item.high-pressure .timeline-marker { border-color: #ef4444; background: #fef2f2; }
.timeline-item.high-pressure .marker-num { color: #ef4444; }
.timeline-content { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; margin-left: 12px; }
.timeline-item.high-pressure .timeline-content { border-left: 3px solid #ef4444; }
.timeline-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; flex-wrap: wrap; gap: 6px; }
.timeline-header h3 { font-size: 0.88rem; margin: 0; font-weight: 700; }
.dnf-value-badge { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 700; padding: 1px 6px; border-radius: 4px; }
.dnf-value-badge.ready { background: #d1fae5; color: #065f46; }
.dnf-value-badge.mixed { background: #fef3c7; color: #92400e; }
.dnf-value-badge.offline { background: #fef2f2; color: #991b1b; }
.timeline-reason { font-size: 0.78rem; color: #475569; line-height: 1.4; margin: 0; }

.hotspots-box { margin-top: 16px; border-top: 1px solid #f1f5f9; padding-top: 14px; }
.hotspots-list { list-style: none; display: flex; flex-wrap: wrap; gap: 6px; padding: 0; }
.hotspots-list li { font-size: 0.76rem; background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 3px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-weight: 600; }

.warning-box { background: #fffaf0; border: 1px solid #feebc8; padding: 14px; border-radius: 6px; }
.bullets-list-warning { list-style: none; padding: 0; margin: 0; display: grid; gap: 7px; }
.bullets-list-warning li { font-size: 0.85rem; color: #7b341e; line-height: 1.4; padding-left: 18px; position: relative; }
.bullets-list-warning li::before { content: '⚠️'; position: absolute; left: 0; font-size: 0.78rem; }

.uncertainty-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 6px; }
.bullets-list-styled { list-style: none; padding: 0; margin: 0; display: grid; gap: 7px; }
.bullets-list-styled li { font-size: 0.85rem; color: #334155; line-height: 1.4; padding-left: 18px; position: relative; }
.bullets-list-styled li::before { content: '✓'; color: #10b981; position: absolute; left: 0; font-weight: bold; }

.limitations-info-banner { background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 16px 18px; display: flex; gap: 14px; }
.limitations-info-banner .info-icon { font-size: 1.4rem; line-height: 1; flex-shrink: 0; }
.limitations-info-banner h3 { font-size: 0.9rem; font-weight: 700; color: #1e3a8a; margin-bottom: 5px; }
.limitations-info-banner p { font-size: 0.8rem; line-height: 1.5; color: #1e40af; margin: 0; }

/* ===========================================================================
   QUOTEABILITY & MARKETING
=========================================================================== */
.quotes-list-container { display: flex; flex-direction: column; gap: 14px; }
.pull-quote-card { background: #fafafb; border-left: 4px solid #FF4500; padding: 14px; border-radius: 0 6px 6px 0; position: relative; margin: 0; }
.pull-quote-card::before { content: '"'; font-size: 2.5rem; color: #e2e8f0; position: absolute; left: 8px; top: -8px; font-family: serif; line-height: 1; }
.pull-quote-card p { font-size: 0.9rem; line-height: 1.5; color: #1e293b; font-style: italic; position: relative; z-index: 2; margin-bottom: 6px; }
.pull-quote-card cite { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #64748b; display: block; font-style: normal; text-transform: uppercase; }

.hooks-box { background: #fafafb; padding: 14px; border-radius: 6px; border: 1px solid #e2e8f0; }
.hooks-pills-row { display: flex; flex-wrap: wrap; gap: 7px; }
.hook-pill { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; font-size: 0.76rem; padding: 4px 9px; border-radius: 4px; font-weight: 600; }
.sub-section-heading { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; color: #475569; margin-bottom: 8px; font-weight: 800; }

/* ===========================================================================
   EVIDENCE TAB
=========================================================================== */
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 18px;
}
.evidence-field-list { display: flex; flex-direction: column; gap: 10px; }
.evidence-kv { display: flex; flex-direction: column; gap: 2px; }
.ev-key { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; color: #64748b; }
.ev-val { font-size: 0.88rem; color: #1e293b; }
.ev-premise { font-size: 0.85rem; line-height: 1.5; color: #334155; border-left: 3px solid #e2e8f0; padding-left: 12px; margin: 12px 0 0; font-style: italic; }
.ev-chapter-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.ev-chapter-list li { font-size: 0.83rem; color: #1e293b; display: flex; flex-direction: column; gap: 3px; }
.ev-ch-summary { font-size: 0.78rem; color: #64748b; line-height: 1.35; }
.risk-badge { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #991b1b; background: #fef2f2; border: 1px solid #fecaca; padding: 2px 6px; border-radius: 4px; display: inline-block; }

.advanced-collapse { border-top: 1px solid #e2e8f0; padding-top: 14px; }
.raw-json-block {
  margin-top: 12px;
  background: #0f172a;
  color: #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  line-height: 1.5;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

/* ===========================================================================
   EXPORTS TAB
=========================================================================== */
.export-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.export-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.export-card-icon { font-size: 2rem; line-height: 1; }
.export-card-info { flex: 1; }
.export-card-info h3 { font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
.export-card-info p { font-size: 0.83rem; color: #475569; line-height: 1.45; margin-bottom: 6px; }
.export-note { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #94a3b8; font-weight: 600; }

/* ===========================================================================
   EMPTY STATE
=========================================================================== */
.empty-state-card {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 60px 40px;
  text-align: center;
  max-width: 560px;
  margin: 40px auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}
.empty-icon { font-size: 3rem; }
.empty-state-card h2 { font-size: 1.4rem; font-weight: 800; color: #0f172a; }
.empty-state-card p { font-size: 0.9rem; color: #64748b; line-height: 1.6; margin: 0; }
.empty-actions { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }

/* ===========================================================================
   PNG CAPTURE CARD (hidden)
=========================================================================== */
.png-summary-capture-card {
  display: none;
  width: 800px;
  padding: 40px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  color: #0f172a;
}
.png-card-header h1 { font-size: 2rem; font-weight: 800; margin-bottom: 8px; }
.png-card-header p { font-size: 1rem; color: #64748b; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; }
.png-card-verdict { margin: 24px 0; padding: 20px; background: #ffffff; border-radius: 8px; border-left: 4px solid #10b981; }
.png-card-verdict h2 { font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; color: #047857; }
.png-card-metrics { display: flex; justify-content: space-between; margin-bottom: 24px; }
.png-metric { background: #ffffff; padding: 16px; border-radius: 8px; text-align: center; flex: 1; margin: 0 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.png-metric span { display: block; font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
.png-metric strong { display: block; font-size: 1.4rem; font-weight: 800; }
.png-card-priorities { padding: 18px; background: #fee2e2; border-radius: 8px; border-left: 4px solid #ef4444; }
.png-card-priorities h3 { color: #b91c1c; font-size: 1rem; margin-bottom: 7px; }

/* ===========================================================================
   RESPONSIVE — mobile accordion-style tabs
=========================================================================== */
@media (max-width: 640px) {
  .tab-nav {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px;
    border-bottom: none;
    margin-bottom: 12px;
  }
  .tab-nav-btn {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    margin-bottom: 0;
    justify-content: center;
    font-size: 0.75rem;
    padding: 8px 10px;
  }
  .tab-nav-btn.active {
    border-color: #FF4500;
    background: #0f172a;
    color: #fff;
    border-bottom-color: #FF4500;
  }
  .cc-metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .editors-grid {
    grid-template-columns: 1fr;
  }
  .feed-container {
    grid-template-columns: 1fr;
  }
  .export-grid {
    grid-template-columns: 1fr;
  }
  .report-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  .report-bar-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (prefers-reduced-motion: reduce) {
  .cc-bar-fill, .bar-fill, .platform-bar-fill, .radar-bar-fill, .editor-score-fill,
  .mock-post-card, .expand-chevron { transition: none; }
}
</style>
