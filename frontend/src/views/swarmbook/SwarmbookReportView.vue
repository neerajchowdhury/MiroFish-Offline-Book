<template>
  <SwarmbookAppShell
    active-route="SwarmbookReport"
    :project-id="session.projectId"
    title="Report Dashboard"
    subtitle="Review the latest Swarmbook report, synthetic scorecard spread, representative posts, and revision priorities for the current project."
    :error-message="error"
    :loading-message="loadingMessage"
  >
    <!-- Actions Bar (Exporters and Navigation) -->
    <div class="actions-bar sticky-nav" v-if="report">
      <nav class="jump-nav">
        <a href="#section-verdict-priorities">Verdict & Priorities</a>
        <a href="#section-rating-segments">Ratings & Segments</a>
        <a href="#section-risk-analysis">Risk Analysis</a>
        <a href="#section-reactions">Reactions</a>
      </nav>

      <div class="nav-links-row">
        <button 
          class="ghost-btn icon-btn" 
          @click="router.push({ name: 'SwarmbookPersonas', params: { projectId: session.projectId } })"
          aria-label="Navigate to Persona Interrogation Screen"
        >
          💬 Persona Interrogation
        </button>
        <button 
          class="primary-btn icon-btn" 
          @click="router.push({ name: 'SwarmbookCompare', params: { projectId: session.projectId } })"
          aria-label="Navigate to Draft Comparison Screen"
        >
          🔄 Draft Comparison
        </button>
      </div>

      <div class="export-actions-row">
        <button class="ghost-btn" @click="handleExport('pdf')" aria-label="Export structured PDF report">📄 PDF</button>
        <button class="ghost-btn" @click="handleExport('docx')" aria-label="Export editable DOCX report">📝 DOCX</button>
        <button class="ghost-btn" @click="handleExport('png')" aria-label="Export PNG summary card">🖼️ Summary Card</button>
        <button class="ghost-btn" @click="handleExport('markdown')" aria-label="Export Markdown file">⬇️ MD</button>
        <button 
          class="ghost-btn" 
          @click="handleCopy" 
          :class="{ 'text-ready': copySuccess }"
          aria-label="Copy Markdown to Clipboard"
        >
          {{ copySuccess ? '✅ Copied!' : '📋 Copy MD' }}
        </button>
        <button class="ghost-btn" @click="handleExport('json')" aria-label="Export raw JSON">📥 JSON</button>
      </div>
    </div>

    <!-- Redesigned Top Summary Cards Panel -->
    <section v-if="report" class="summary-grid" aria-label="Key Report Metrics">
      <!-- 1. Publishing Readiness Card -->
      <article class="summary-card readiness-card" :class="readinessTone">
        <span class="summary-label">Publishing Readiness</span>
        <div class="score-display">
          <strong>{{ readinessScore }}%</strong>
          <span class="status-indicator-text">{{ readinessLabel }}</span>
        </div>
        <div class="meter-bar">
          <div class="meter-fill" :style="{ width: readinessScore + '%' }"></div>
        </div>
      </article>

      <!-- 2. Predicted Rating Band Card -->
      <article class="summary-card">
        <span class="summary-label">Predicted Rating Band</span>
        <div class="score-display">
          <strong>{{ formatNumber(report.scorecard?.rating_distribution?.predicted_mean_rating) }} ★</strong>
        </div>
        <span class="band-label">
          Range: [{{ formatNumber(report.scorecard?.rating_distribution?.confidence_band?.low) }} - 
          {{ formatNumber(report.scorecard?.rating_distribution?.confidence_band?.high) }}] 
          ({{ report.scorecard?.rating_distribution?.confidence_band?.label || 'moderate' }} confidence)
        </span>
      </article>

      <!-- 3. DNF Risk Card -->
      <article class="summary-card" :class="{ 'warning-highlight': dnfRiskValue >= 0.4 }">
        <span class="summary-label">DNF Abandonment Risk</span>
        <div class="score-display">
          <strong>{{ Math.round(dnfRiskValue * 100) }}%</strong>
          <span class="status-indicator-text" :class="getDnfRiskTone(dnfRiskValue)">
            {{ getDnfRiskLabel(dnfRiskValue) }}
          </span>
        </div>
        <span class="band-label">
          Range: [{{ Math.round((report.scorecard?.dnf?.confidence_band?.low || 0) * 100) }}% - 
          {{ Math.round((report.scorecard?.dnf?.confidence_band?.high || 0) * 100) }}%]
        </span>
      </article>

      <!-- 4. Controversy Risk Card -->
      <article class="summary-card" :class="{ 'warning-highlight': controversyRiskValue >= 0.6 }">
        <span class="summary-label">Controversy Risk</span>
        <div class="score-display">
          <strong>{{ Math.round(controversyRiskValue * 100) }}%</strong>
          <span class="status-indicator-text" :class="getControversyRiskTone(controversyRiskValue)">
            {{ getControversyRiskLabel(controversyRiskValue) }}
          </span>
        </div>
        <span class="band-label">
          Range: [{{ Math.round((report.scorecard?.controversy?.confidence_band?.low || 0) * 100) }}% - 
          {{ Math.round((report.scorecard?.controversy?.confidence_band?.high || 0) * 100) }}%]
        </span>
      </article>

      <!-- 5. Viral Potential Card -->
      <article class="summary-card">
        <span class="summary-label">Max Viral Potential</span>
        <div class="score-display">
          <strong>{{ maxViralScore }}%</strong>
          <span class="status-indicator-text ready">{{ maxViralPlatformName }}</span>
        </div>
        <span class="band-label">Best platform match for organic spread.</span>
      </article>

      <!-- 6. Top Revision Priority Card -->
      <article class="summary-card" :class="{ 'error-highlight': topPriorityScore >= 0.6 }">
        <span class="summary-label">Top Revision Priority</span>
        <div class="score-display">
          <strong class="priority-title">{{ topPriorityItemName }}</strong>
        </div>
        <span class="band-label" :class="getPriorityClass(topPriorityScore)">
          Priority: {{ Math.round(topPriorityScore * 100) }}% ({{ getPriorityLabel(topPriorityScore) }})
        </span>
      </article>
      <!-- 7. Stage Confidence Card (New) -->
      <article class="summary-card">
        <span class="summary-label">Stage Confidence</span>
        <div class="score-display">
          <strong>{{ Math.round((report.confidence || 0) * 100) }}%</strong>
        </div>
        <span class="band-label">Reliability of the generated insights.</span>
      </article>
    </section>

    <!-- Executive Verdict & Star Rating Spread Redesign -->
    <div v-if="report" class="section-grid-double" id="section-verdict-priorities">
      <!-- 1. Executive Verdict -->
      <article class="premium-card verdict-card">
        <div class="card-eyebrow">SECTION 01</div>
        <h2>Executive Verdict</h2>
        <div class="metadata-badges">
          <span class="badge privacy-badge" :class="report.privacy_mode">
            🔒 Privacy: {{ formatPrivacyMode(report.privacy_mode) }}
          </span>
          <span class="badge draft-badge" v-if="report.draft_id">
            📄 Draft: {{ report.draft_id }} (v{{ report.version || '1.0' }})
          </span>
          <span class="badge confidence-badge">
            🎯 Stage Confidence: {{ Math.round((report.confidence || 0) * 100) }}%
          </span>
        </div>
        <p class="verdict-summary-text">{{ report.summary || 'No summary available.' }}</p>
      </article>

      <!-- 2. Star Rating Spread -->
      <article class="premium-card">
        <div class="card-eyebrow">SECTION 02</div>
        <h2>Star Rating Spread</h2>
        <div class="rating-overall-header">
          <div class="big-stars">{{ formatNumber(report.scorecard?.rating_distribution?.predicted_mean_rating) }} ★</div>
          <p class="muted-p">Blended estimate from persona reactions (65%) and manuscript style indicators (35%).</p>
        </div>

        <p class="chart-summary">Histogram showing predicted percentage of reader ratings across 1 to 5 stars.</p>
        <!-- Custom HTML/CSS Star Histogram -->
        <div class="star-histogram" role="img" aria-label="Star Rating Distribution Chart">
          <div class="histogram-row" v-for="star in [5, 4, 3, 2, 1]" :key="star">
            <span class="star-text-label">{{ star }} Star</span>
            <div class="bar-track" :title="star + ' Star: ' + getStarPercentage(star) + '%'">
              <div 
                class="bar-fill" 
                :style="{ width: getStarPercentage(star) + '%' }"
                :class="'bar-star-' + star"
              ></div>
            </div>
            <span class="star-percent-text">{{ getStarPercentage(star) }}%</span>
          </div>
        </div>

        <!-- Rating Components Breakdown -->
        <div class="sub-components-box">
          <h3>Rating Driver Breakdown</h3>
          <div class="drivers-row">
            <div 
              class="driver-pill" 
              v-for="(val, name) in report.scorecard?.rating_distribution?.component_scores || {}" 
              :key="name"
            >
              <span class="label">{{ formatRadarLabel(name) }}</span>
              <strong :class="getComponentScoreTone(val)">{{ Math.round(val * 100) }}%</strong>
            </div>
          </div>
        </div>
      </article>
    </div>

    <!-- Revision priorities checklist (MOVED TO TOP FOR DECISION-FIRST UX) -->
    <section v-if="report" class="dashboard-block-section">
      <div class="card-eyebrow">TOP FIXES</div>
      <h2>Revision Priorities</h2>
      <p class="section-desc">Ranked hotspots where content revisions would yield the highest predicted rating lift.</p>

      <div class="priorities-checklist-container" v-if="report.scorecard?.revision_priority?.ranked_items?.length">
        <div 
          class="priority-checklist-item" 
          v-for="item in report.scorecard.revision_priority.ranked_items" 
          :key="item.item_id"
          :class="'item-priority-' + getPriorityClass(item.priority_score)"
        >
          <div class="priority-item-side">
            <span class="priority-label-pill" :class="getPriorityClass(item.priority_score)">
              {{ getPriorityLabel(item.priority_score) }} ({{ item.priority_score }})
            </span>
            <span class="item-type-badge">{{ item.item_type }}</span>
          </div>

          <div class="priority-item-main">
            <h3>Target ID: <code>{{ item.item_id }}</code></h3>
            <ul class="reasons-bullet-list">
              <li v-for="reason in item.reasons" :key="reason">{{ reason }}</li>
            </ul>
            <div class="item-evidence" v-if="item.evidence_refs?.length">
              <strong>Evidence links:</strong>
              <span v-for="ref in item.evidence_refs" :key="ref" class="evidence-pill">#{{ ref }}</span>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="muted-note text-center">No revision priorities ranked.</p>
    </section>

    <!-- Reader Segment Map Details Table -->
    <section v-if="report" class="dashboard-block-section" id="section-rating-segments">
      <div class="card-eyebrow">SECTION 03</div>
      <h2>Reader Segment Map</h2>
      <p class="section-desc">Performance of manuscript topics, tone, and pacing split by target platform demographics.</p>
      
      <div class="table-container">
        <table class="segments-table">
          <thead>
            <tr>
              <th scope="col">Segment Identifier</th>
              <th scope="col">Predicted Mean Rating</th>
              <th scope="col">Recommendation probability</th>
              <th scope="col">Sentiment Signal</th>
              <th scope="col">Representative Personas</th>
              <th scope="col">Dominant Sentiments / Topics</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="seg in report.segment_insights || []" :key="seg.segment">
              <td class="bold-cell"><code>{{ seg.segment }}</code></td>
              <td><strong>{{ formatNumber(seg.rating_mean) }} ★</strong></td>
              <td>{{ seg.recommendation_mean !== null ? Math.round(seg.recommendation_mean * 100) + '%' : 'N/A' }}</td>
              <td>
                <span class="signal-badge" :class="seg.signal">
                  {{ seg.signal.toUpperCase() }}
                </span>
              </td>
              <td>{{ joinList(seg.sample_personas) }}</td>
              <td>
                <div class="sentiment-tags">
                  <span v-for="sent in seg.sentiments || []" :key="sent" class="sentiment-tag">{{ sent }}</span>
                </div>
              </td>
            </tr>
            <tr v-if="!report.segment_insights?.length">
              <td colspan="6" class="empty-table-cell">No segment insights available.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- DNF Analysis & Timeline Section -->
    <div v-if="report" class="section-grid-double" id="section-risk-analysis">
      <!-- 4. DNF Analysis Drivers -->
      <article class="premium-card">
        <div class="card-eyebrow">SECTION 04</div>
        <h2>DNF Abandonment Analysis</h2>
        <p class="muted-p margin-bottom-lg">Key drivers computed from pacing penalties, early chapter drag, and style mismatches.</p>

        <div class="dnf-drivers-list">
          <div 
            class="dnf-driver-row" 
            v-for="(val, name) in report.scorecard?.dnf?.component_scores || {}" 
            :key="name"
          >
            <div class="dnf-driver-header">
              <span class="label">{{ formatRadarLabel(name) }}</span>
              <strong :class="getDnfDriverTone(val)">{{ Math.round(val * 100) }}% Risk</strong>
            </div>
            <div class="dnf-driver-track">
              <div 
                class="dnf-driver-fill" 
                :style="{ width: (val * 100) + '%' }"
                :class="getDnfDriverTone(val)"
              ></div>
            </div>
          </div>
        </div>
      </article>

      <!-- Chapter abandonment pressure points timeline -->
      <article class="premium-card scrollable-card">
        <div class="card-eyebrow">TIMELINE</div>
        <h2>Chapter Pressure Points</h2>
        <p class="muted-p margin-bottom-lg">Chapters with the highest abandonment risk scores, sorted by DNF pressure.</p>

        <p class="chart-summary">Timeline highlights chapters where readers exhibit high abandonment risk.</p>
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
                <span class="dnf-value-badge" :class="getDnfRiskTone(point.dnf_points)">
                  {{ Math.round(point.dnf_points * 100) }}% DNF Risk
                </span>
              </div>
              <p class="timeline-reason">{{ point.reason }}</p>
            </div>
          </div>
        </div>
        <p v-else class="muted-note text-center">No chapter-level pressure points recorded.</p>
      </article>
    </div>

    <!-- Controversy Radar and platform viral potential comparison -->
    <div v-if="report" class="section-grid-double">
      <!-- 5. Controversy Radar -->
      <article class="premium-card">
        <div class="card-eyebrow">SECTION 05</div>
        <h2>Controversy Radar</h2>
        <p class="muted-p margin-bottom-lg">BACKLASH RISK BY AXIS</p>

        <div class="radar-card-grid">
          <div 
            class="radar-bar-item" 
            v-for="(val, name) in report.scorecard?.controversy?.radar || {}" 
            :key="name"
          >
            <div class="radar-bar-header">
              <span class="label">{{ formatRadarLabel(name) }}</span>
              <strong>{{ Math.round(val * 100) }}%</strong>
            </div>
            <div class="radar-bar-track">
              <div 
                class="radar-bar-fill" 
                :style="{ width: (val * 100) + '%' }"
                :class="getRiskLevelTone(val)"
              ></div>
            </div>
          </div>
        </div>

        <div class="hotspots-box" v-if="report.scorecard?.controversy?.hotspots?.length">
          <h3>Flagged Backlash Hotspots</h3>
          <ul class="hotspots-list">
            <li v-for="spot in report.scorecard.controversy.hotspots" :key="spot">
              ⚠️ <code>{{ spot }}</code>
            </li>
          </ul>
        </div>
      </article>

      <!-- 6. Viral Potential by Platform -->
      <article class="premium-card">
        <div class="card-eyebrow">SECTION 06</div>
        <h2>Viral Potential by Platform</h2>
        <p class="muted-p margin-bottom-lg">Platform Suitability and Spread Probability</p>

        <div class="viral-platform-chart">
          <div 
            class="platform-bar-row" 
            v-for="(val, platform) in report.scorecard?.viral?.platform_scores || {}" 
            :key="platform"
          >
            <span class="platform-name-label">{{ formatPlatformLabel(platform) }}</span>
            <div class="platform-bar-track" :title="formatPlatformLabel(platform) + ': ' + Math.round(val * 100) + '%'">
              <div 
                class="platform-bar-fill" 
                :style="{ width: (val * 100) + '%' }"
                :class="'platform-color-' + platform"
              ></div>
            </div>
            <span class="platform-percentage-value">{{ Math.round(val * 100) }}%</span>
          </div>
        </div>

        <div class="viral-drivers-box">
          <h3>Viral Driver Strengths</h3>
          <div class="drivers-row">
            <div 
              class="driver-pill" 
              v-for="(val, name) in report.scorecard?.viral?.component_scores || {}" 
              :key="name"
            >
              <span class="label">{{ formatRadarLabel(name) }}</span>
              <strong :class="getRiskLevelTone(val)">{{ Math.round(val * 100) }}%</strong>
            </div>
          </div>
        </div>
      </article>
    </div>

    <!-- Platform Reactions (Feed View Section) -->
    <section v-if="report" class="dashboard-block-section" id="section-reactions">
      <div class="card-eyebrow">SECTION 07</div>
      <h2>Simulated Reader Reactions</h2>
      <p class="section-desc">Platform-specific posts generated by reader personas. Select a platform to filter the feed.</p>

      <!-- Interactive Tab selectors -->
      <div class="tab-row-container">
        <div class="tab-row" role="tablist" aria-label="Filter Simulated Feed by Platform">
          <button 
            v-for="plat in ['all', 'goodreads', 'booktok', 'reddit', 'bookstagram', 'x']" 
            :key="plat"
            class="tab-btn"
            :class="{ active: activeTab === plat }"
            role="tab"
            :aria-selected="activeTab === plat"
            @click="activeTab = plat"
            @keydown.enter="activeTab = plat"
          >
            {{ formatPlatformTabName(plat) }}
            <span class="tab-count-badge" v-if="getPlatformPostCount(plat) > 0">
              {{ getPlatformPostCount(plat) }}
            </span>
          </button>
        </div>
      </div>

      <!-- Feed Container -->
      <div class="feed-container scrollable-feed" v-if="filteredPosts.length">
        <article 
          class="mock-post-card" 
          v-for="post in filteredPosts" 
          :key="post.post_id"
          :class="'mock-post-' + post.platform"
        >
          <!-- Platform indicator header -->
          <header class="post-header">
            <div class="user-info">
              <span class="avatar">👤</span>
              <div class="user-meta">
                <strong class="display-name">{{ getPersonaDisplayName(post.persona_id) }}</strong>
                <span class="handle">@{{ post.persona_id }}</span>
              </div>
            </div>
            <span class="post-platform-tag" :class="post.platform">
              {{ post.platform.toUpperCase() }}
            </span>
          </header>

          <!-- Post body content -->
          <div class="post-body">
            <!-- Goodreads custom rating display -->
            <div class="post-stars-row" v-if="post.rating && post.platform === 'goodreads'">
              <span class="star-rating">{{ '★'.repeat(Math.round(post.rating)) }}{{ '☆'.repeat(5 - Math.round(post.rating)) }}</span>
              <span class="rating-value">({{ post.rating }} / 5)</span>
            </div>

            <!-- Reddit Subreddit layout header -->
            <div class="subreddit-tag" v-if="post.platform === 'reddit'">
              <span>r/books</span> • Posted by u/{{ post.persona_id }}
            </div>

            <p class="post-text">{{ post.body || 'No reaction text posted.' }}</p>

            <!-- TikTok visual video mock -->
            <div class="tiktok-video-mock" v-if="post.platform === 'booktok'">
              <div class="video-overlay">
                <span>📹 Play Video Hook</span>
                <span class="hook-text" v-if="post.payload?.hook_line">"{{ post.payload.hook_line }}"</span>
              </div>
            </div>

            <!-- Hashtag inline layout -->
            <div class="post-hashtags" v-if="post.hashtags?.length">
              <span v-for="tag in post.hashtags" :key="tag" class="tag">#{{ tag }}</span>
            </div>

            <!-- Shelf inline tags -->
            <div class="post-shelf-tags" v-if="post.shelf_tags?.length">
              <span class="tag-title">Shelves:</span>
              <span v-for="shelf in post.shelf_tags" :key="shelf" class="shelf-tag">{{ shelf }}</span>
            </div>
          </div>

          <!-- Post engagement footer -->
          <footer class="post-footer">
            <div class="metric" title="Predicted simulated likes/views">
              <span>❤️ Likes</span> 
              <strong>{{ Math.round((post.engagement_prediction || 0.5) * 100) }}</strong>
            </div>
            <div class="metric" v-if="post.payload?.hot_take">
              <span class="hot-take-label">🌶️ HOT TAKE</span>
            </div>
            <div class="metric" v-if="post.payload?.viral_trigger">
              <span class="viral-trigger-label">⚡ VIRAL POTENTIAL</span>
            </div>
          </footer>
        </article>
      </div>
      <p v-else class="muted-note text-center padding-xl">No simulated posts recorded for this platform filter.</p>
    </section>

    <!-- Quoteability map -->
    <div v-if="report" class="section-grid-double">
      <!-- 8. Quoteability Map -->
      <article class="premium-card">
        <div class="card-eyebrow">SECTION 08</div>
        <h2>Quoteability Map</h2>
        <p class="muted-p margin-bottom-lg">MEMORABILITY SCORE AND ATTRIBUTES</p>

        <div class="readiness-card ready">
          <div class="score-display">
            <strong>{{ Math.round(quoteabilityScoreValue * 100) }}%</strong>
            <span class="status-indicator-text ready">Highly Quotable</span>
          </div>
          <div class="meter-bar">
            <div class="meter-fill" :style="{ width: (quoteabilityScoreValue * 100) + '%' }"></div>
          </div>
        </div>

        <div class="radar-card-grid margin-top-md">
          <div 
            class="radar-bar-item" 
            v-for="(val, name) in report.scorecard?.quoteability?.component_scores || {}" 
            :key="name"
          >
            <div class="radar-bar-header">
              <span class="label">{{ formatRadarLabel(name) }}</span>
              <strong>{{ Math.round(val * 100) }}%</strong>
            </div>
            <div class="radar-bar-track">
              <div 
                class="radar-bar-fill" 
                :style="{ width: (val * 100) + '%' }"
                :class="getRiskLevelTone(val)"
              ></div>
            </div>
          </div>
        </div>
      </article>

      <!-- Quote Candidates pull-quotes -->
      <article class="premium-card">
        <div class="card-eyebrow">HIGHLIGHTS</div>
        <h2>Excerpt Share Candidates</h2>
        <p class="muted-p margin-bottom-lg">Highlighted lines with the highest organic screenshot and share probability.</p>

        <div class="quotes-list-container" v-if="report.scorecard?.quoteability?.quote_candidates?.length">
          <blockquote 
            class="pull-quote-card" 
            v-for="candidate in report.scorecard.quoteability.quote_candidates" 
            :key="candidate.text"
          >
            <p>"{{ candidate.text }}"</p>
            <cite>Source: {{ candidate.source }}</cite>
          </blockquote>
        </div>
        <p v-else class="muted-note text-center">No quote candidates extracted.</p>
      </article>
    </div>

    <!-- Section moved up: Revision priorities checklist -->

    <!-- Marketing hooks, Author Risk Note & disclaimers -->
    <div v-if="report" class="section-grid-double">
      <!-- 10. Marketing Hooks & Strengths -->
      <article class="premium-card">
        <div class="card-eyebrow">SECTION 10</div>
        <h2>Marketing Hooks & Strengths</h2>
        <p class="muted-p margin-bottom-lg">ORGANIC POSITIONING ATTRIBUTES</p>

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
            <span 
              class="hook-pill" 
              v-for="hook in session.evidencePack.market_surface.discoverability_hooks" 
              :key="hook"
            >
              🎯 {{ hook }}
            </span>
          </div>
        </div>
      </article>

      <!-- 11. Author Risk Note & Known Limitations -->
      <article class="premium-card">
        <div class="card-eyebrow">SECTION 11</div>
        <h2>Author Risk Note & Caveats</h2>
        <p class="muted-p margin-bottom-lg">EDITORIAL FLAGS AND CRITICAL DISCLAIMERS</p>

        <div class="warning-box">
          <h3>Top Backlash Risks</h3>
          <ul class="bullets-list-warning">
            <li v-for="item in report.top_risks || []" :key="item">{{ item }}</li>
            <li v-if="!report.top_risks?.length" class="muted-note">No risks detected.</li>
          </ul>
        </div>

        <div class="uncertainty-box margin-top-md" v-if="report.uncertainty_notes?.length">
          <h3>Confidence & Scope Caveats</h3>
          <ul class="bullets-list-styled">
            <li v-for="item in report.uncertainty_notes" :key="item">{{ item }}</li>
          </ul>
        </div>
      </article>
    </div>

    <!-- Known Limitations Info Section -->
    <section v-if="report" class="limitations-info-banner">
      <div class="info-icon">ℹ️</div>
      <div class="info-content">
        <h3>Known Simulation Limitations</h3>
        <p>
          This report is synthesized from a deterministic simulation run using synthetic personas. It is designed for manuscript stress testing and structural analysis, not absolute market validation. No real social platforms or external user accounts were contacted. Local models run completely offline to preserve privacy.
        </p>
      </div>
    </section>

    <!-- Empty State Fallback -->
    <section v-if="!report && !loading" class="empty-state-card">
      <div class="empty-icon" aria-hidden="true">📊</div>
      <h2>No Swarmbook Report Available</h2>
      <p>
        You have not generated a report for this project yet. Start a reader simulation to run personas, calculate scorecard profiles, and generate revision guidelines.
      </p>

      <div class="empty-actions">
        <button 
          class="primary-btn" 
          @click="router.push({ name: 'SwarmbookSimulation', params: { projectId: session.projectId } })"
          aria-label="Navigate to Swarm Setup View to configure and run simulation"
        >
          Setup & Run Reader Swarm
        </button>
        <button 
          class="ghost-btn" 
          @click="loadDemoMock"
          aria-label="Load premium demo dataset offline for dashboard validation"
        >
          Load Premium Demo Report (Offline Mock)
        </button>
      </div>
    </section>
    <!-- Hidden PNG Summary Card (For Export) -->
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
import { generateJson, generateMarkdown, generateDocx, generatePdf, copyToClipboard } from '../../utils/exportReport'

const route = useRoute()
const router = useRouter()
const session = ref(getSwarmbookSession())
const report = ref(session.value.report)
const loading = ref(false)
const loadingMessage = ref('')
const error = ref('')
const activeTab = ref('all')

// Sync session variables when route shifts
watch(() => route.path, () => {
  session.value = getSwarmbookSession()
  report.value = session.value.report
})

// Simulated platform posts list
const platformPosts = computed(() => session.value.simulationRun?.platform_posts || [])

// Filtered posts based on active tab
const filteredPosts = computed(() => {
  if (activeTab.value === 'all') return platformPosts.value
  return platformPosts.value.filter(post => post.platform === activeTab.value)
})

// Persona display names cache
const personaNames = computed(() => {
  const result = {}
  for (const persona of session.value.simulationRun?.reader_personas || []) {
    result[persona.persona_id] = persona.display_name
  }
  return result
})

// Helper: resolve persona display names
function getPersonaDisplayName(id) {
  return personaNames.value[id] || id
}

// ----------------------------------------------------
// 1. Publishing Readiness Score Metrics
// ----------------------------------------------------
const readinessScore = computed(() => {
  if (!report.value) return 0
  const rating = Number(report.value.scorecard?.rating_distribution?.predicted_mean_rating) || 3.0
  const dnf = Number(report.value.scorecard?.dnf?.dnf_risk) || 0.5
  const controversy = Number(report.value.scorecard?.controversy?.controversy_risk) || 0.5
  
  // Rating contribution: 1-5 maps to 0-50%
  const ratingContrib = ((rating - 1.0) / 4.0) * 50
  // DNF contribution: low DNF risk increases score (up to 30%)
  const dnfContrib = (1.0 - dnf) * 30
  // Controversy contribution: lower risk increases score (up to 20%)
  const controversyContrib = (1.0 - controversy * 0.5) * 20
  
  const score = Math.max(0, Math.min(100, ratingContrib + dnfContrib + controversyContrib))
  return Math.round(score)
})

const readinessLabel = computed(() => {
  const score = readinessScore.value
  if (score >= 80) return 'Strong'
  if (score >= 60) return 'Good'
  return 'Revision Recommended'
})

const readinessTone = computed(() => {
  const score = readinessScore.value
  if (score >= 80) return 'ready'
  if (score >= 60) return 'mixed'
  return 'offline'
})

// ----------------------------------------------------
// 2. Main scorecard risk values extraction helpers
// ----------------------------------------------------
const dnfRiskValue = computed(() => {
  return Number(report.value?.scorecard?.dnf?.dnf_risk) || 0
})

const controversyRiskValue = computed(() => {
  return Number(report.value?.scorecard?.controversy?.controversy_risk) || 0
})

const quoteabilityScoreValue = computed(() => {
  return Number(report.value?.scorecard?.quoteability?.quoteability_score) || 0
})

// DNF Risk classifications
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

// Controversy Risk classifications
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

// Platform viral potential score indicators
const maxViralScore = computed(() => {
  const scores = report.value?.scorecard?.viral?.platform_scores
  if (!scores) return 0
  const values = Object.values(scores).map(v => Number(v)).filter(v => !Number.isNaN(v))
  if (!values.length) return 0
  return Math.round(Math.max(...values) * 100)
})

const maxViralPlatformName = computed(() => {
  const scores = report.value?.scorecard?.viral?.platform_scores
  if (!scores) return 'N/A'
  let best = 'None'
  let maxScore = -1
  for (const [platform, val] of Object.entries(scores)) {
    if (val > maxScore) {
      maxScore = val
      best = platform
    }
  }
  return formatPlatformLabel(best)
})

// Top revision priority extraction
const topPriorityItem = computed(() => {
  return report.value?.scorecard?.revision_priority?.ranked_items?.[0]
})

const topPriorityItemName = computed(() => {
  if (!topPriorityItem.value) return 'None'
  const item = topPriorityItem.value
  return `${item.item_type.toUpperCase()}:${item.item_id}`
})

const topPriorityScore = computed(() => {
  return topPriorityItem.value?.priority_score || 0
})

// ----------------------------------------------------
// Formatting functions
// ----------------------------------------------------
function formatNumber(value) {
  const numeric = Number(value)
  return Number.isNaN(numeric) ? 'N/A' : numeric.toFixed(2)
}

function joinList(value) {
  return value && value.length ? value.join(', ') : 'N/A'
}

function formatPlatformLabel(platform) {
  if (!platform) return 'N/A'
  const mapping = {
    goodreads: 'Goodreads',
    booktok: 'BookTok',
    reddit: 'Reddit',
    bookstagram: 'Bookstagram',
    x: 'X / Twitter',
    newsletter: 'Newsletter Feed',
    bookclub: 'Book Club Discussion'
  }
  return mapping[platform.toLowerCase()] || platform
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

function getPlatformPostCount(platform) {
  if (platform === 'all') return platformPosts.value.length
  return platformPosts.value.filter(p => p.platform === platform).length
}

function getPlatformPostCountLabel(platform) {
  const count = getPlatformPostCount(platform)
  return count > 0 ? ` (${count})` : ''
}

function getStarPercentage(star) {
  if (!report.value?.scorecard?.rating_distribution?.distribution) return 0
  const val = report.value.scorecard.rating_distribution.distribution[`${star}_star`]
  return Math.round((Number(val) || 0) * 100)
}

// Style tags tones
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

const getPriorityLabel = (score) => {
  if (score >= 0.75) return 'Critical'
  if (score >= 0.55) return 'High'
  if (score >= 0.35) return 'Medium'
  return 'Low'
}

// ----------------------------------------------------
// Exporter workflows
// ----------------------------------------------------
const copySuccess = ref(false)

function getFormatDate() {
  return new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
}

async function handleExport(type) {
  if (!report.value) return
  
  try {
    if (type === 'json') {
      generateJson(report.value, session.value)
    } else if (type === 'markdown') {
      generateMarkdown(report.value, session.value)
    } else if (type === 'docx') {
      await generateDocx(report.value, session.value)
    } else if (type === 'pdf') {
      generatePdf(report.value, session.value)
    } else if (type === 'png') {
      const element = document.getElementById('png-summary-card')
      if (element) {
        // Temporarily make it visible for html2canvas
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
    alert('Failed to copy to clipboard: ' + err.message)
  }
}

// ----------------------------------------------------
// Demo mock data loader (for verification / testing)
// ----------------------------------------------------
const MOCK_REPORT = {
  report_id: 'report_demo_123456',
  project_id: 'proj_demo_987',
  simulation_id: 'run_demo_789',
  privacy_mode: 'hybrid_safe',
  draft_id: 'draft_v1',
  version: '1.0.0',
  title: 'The Antigravity Paradox',
  summary: 'Predicted mean rating is 4.12 with DNF risk at 0.22. Best synthetic spread is on booktok, while the main blocker is chapter 3 carries DNF pressure at 0.58.',
  confidence: 0.85,
  audience_response: {
    personas_count: 30,
    posts_count: 5,
    mean_rating: 4.12,
    recommendation_mean: 0.78,
    top_platforms: ['booktok', 'goodreads', 'bookstagram']
  },
  scorecard: {
    rating_distribution: {
      predicted_mean_rating: 4.12,
      distribution: {
        '1_star': 0.05,
        '2_star': 0.08,
        '3_star': 0.12,
        '4_star': 0.45,
        '5_star': 0.30
      },
      confidence_band: { low: 3.85, mid: 4.12, high: 4.35, label: 'high' },
      component_scores: {
        comprehension: 0.88,
        emotional_payoff: 0.92,
        prose_quality: 0.85,
        pacing: 0.76,
        character_attachment: 0.90,
        packaging_fit: 0.82
      },
      evidence_refs: ['doc_dna_1', 'style_map_1']
    },
    dnf: {
      dnf_risk: 0.22,
      confidence_band: { low: 0.15, mid: 0.22, high: 0.32, label: 'moderate' },
      component_scores: {
        opening_drag: 0.28,
        confusion: 0.18,
        pacing_drag: 0.32,
        unmet_expectation: 0.15,
        voice_misalignment: 0.20,
        length_fatigue: 0.25
      },
      chapter_points: [
        { section_id: 'chapter_3', chapter_number: 3, dnf_points: 0.58, reason: 'Slow pacing; high reader friction around character decisions' },
        { section_id: 'chapter_1', chapter_number: 1, dnf_points: 0.35, reason: 'Dense worldbuilding introduction; confusion markers' },
        { section_id: 'chapter_7', chapter_number: 7, dnf_points: 0.24, reason: 'Pacing dip in intermediate act transition' }
      ]
    },
    controversy: {
      controversy_risk: 0.48,
      confidence_band: { low: 0.38, mid: 0.48, high: 0.58, label: 'moderate' },
      radar: {
        ideological_tension: 0.55,
        claim_hazard: 0.30,
        moral_disagreement: 0.62,
        tonal_disruption: 0.40,
        character_behavior_challenge: 0.50,
        packaging_mismatch: 0.32
      },
      hotspots: [
        'claim:claim_ethics_v1',
        'risk:moral_disagreement_ch3',
        'packaging:audience_expectation_gap'
      ]
    },
    polarization: {
      polarization_score: 0.52,
      confidence_band: { low: 0.42, mid: 0.52, high: 0.62, label: 'moderate' },
      component_scores: {
        taste_split: 0.58,
        ideology_split: 0.62,
        prose_split: 0.35,
        ending_split: 0.70,
        genre_expectation_split: 0.40
      },
      split_signals: ['wide_rating_spread', 'mixed_sentiment', 'reaction_backlash']
    },
    quoteability: {
      quoteability_score: 0.84,
      confidence_band: { low: 0.76, mid: 0.84, high: 0.90, label: 'high' },
      component_scores: {
        line_density: 0.88,
        image_making_language: 0.85,
        emotional_clarity: 0.82,
        repetition_resonance: 0.78,
        scene_peak_strength: 0.90,
        excerpt_friendly_structure: 0.80
      },
      quote_candidates: [
        { text: 'In the shadow of the gravity well, we learned that falling was just another form of flight.', source: 'chapter_3' },
        { text: 'Nothing is heavier than the weight of a secret left unshared among the stars.', source: 'chapter_1' },
        { text: 'They promised us we would break the orbit, but we only succeeded in breaking ourselves.', source: 'reaction_rec_3' }
      ]
    },
    viral: {
      platform_scores: {
        goodreads: 0.72,
        booktok: 0.88,
        reddit: 0.55,
        bookstagram: 0.82,
        x: 0.60,
        newsletter: 0.65,
        bookclub: 0.78
      },
      top_platforms: ['booktok', 'bookstagram', 'bookclub'],
      confidence_band: { low: 0.78, mid: 0.85, high: 0.92, label: 'high' },
      component_scores: {
        emotional_spike: 0.88,
        trope_visibility: 0.75,
        novelty: 0.82,
        controversy: 0.48,
        quoteability: 0.84,
        concise_explainability: 0.70
      }
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
  revision_priorities: [
    'chapter:chapter_3 (0.78)',
    'claim:claim_ethics_v1 (0.62)',
    'style:style_prose (0.45)'
  ],
  uncertainty_notes: [
    'Outputs are synthetic stress-test signals, not a guarantee of market behavior.',
    'Prediction confidence is lower for the hard science components due to mixed reader interest.'
  ]
}

const MOCK_PLATFORM_POSTS = [
  {
    post_id: 'post_1',
    persona_id: 'persona_aria',
    platform: 'booktok',
    round_number: 1,
    rating: 5.0,
    body: 'OMG guys, "The Antigravity Paradox" has the most beautiful prose ever! "In the shadow of the gravity well, we learned that falling was just another form of flight." 😭 Honestly obsessed with this quote. Major tearjerker alert! #booktok #mustread #antigravity',
    hashtags: ['booktok', 'mustread', 'antigravity'],
    payload: { hook_line: 'OMG guys', viral_trigger: true }
  },
  {
    post_id: 'post_2',
    persona_id: 'persona_devon',
    platform: 'goodreads',
    round_number: 1,
    rating: 4.0,
    body: 'A solid sci-fi read with highly intriguing premise. The pacing in the middle chapters (especially chapter 3) was a bit sluggish, but the ending pays off wonderfully. Highly recommended for fans of existential science fiction.',
    shelf_tags: ['scifi', 'existential', 'goodreads-challenge']
  },
  {
    post_id: 'post_3',
    persona_id: 'persona_skeptic',
    platform: 'reddit',
    round_number: 1,
    rating: 2.0,
    body: 'Anyone else read the draft of "The Antigravity Paradox" yet? The physics claims in chapter 4 make zero sense. There are some serious logic gaps in their orbital mechanics. Pacing drags forever in chapter 3. 2/5 stars.',
    payload: { hot_take: true }
  },
  {
    post_id: 'post_4',
    persona_id: 'persona_leo',
    platform: 'bookstagram',
    round_number: 1,
    rating: 5.0,
    body: 'Just finished this masterpiece. "Nothing is heavier than the weight of a secret left unshared among the stars." Look at this beautiful aesthetic. Highly recommend it to all book clubs out there! 🌌✨',
    hashtags: ['bookstagram', 'scificard', 'aesthetic']
  },
  {
    post_id: 'post_5',
    persona_id: 'persona_x',
    platform: 'x',
    round_number: 1,
    rating: 3.0,
    body: 'Controversial take: The Antigravity Paradox is just another pseudo-scientific lecture disguised as fiction. The claims are poorly supported, even if the ending hits hard. Let the debate begin. 🧵 (1/5)',
    payload: { hot_take: true }
  }
]

function loadDemoMock() {
  report.value = MOCK_REPORT
  const simulatedRunMock = {
    run_id: 'run_demo_789',
    platform_posts: MOCK_PLATFORM_POSTS,
    reader_personas: [
      { persona_id: 'persona_aria', display_name: 'Aria Reed' },
      { persona_id: 'persona_devon', display_name: 'Devon M.' },
      { persona_id: 'persona_skeptic', display_name: 'Skeptic Reader' },
      { persona_id: 'persona_leo', display_name: 'Leo Vance' },
      { persona_id: 'persona_x', display_name: 'Critical X' }
    ]
  }
  
  session.value = updateSwarmbookSession({
    projectId: 'proj_demo_987',
    report: MOCK_REPORT,
    simulationRun: simulatedRunMock
  })
}

// ----------------------------------------------------
// Main API Loader
// ----------------------------------------------------
async function ensureReport() {
  if (!session.value.projectId || session.value.projectId !== route.params.projectId) {
    // If mismatch, check if route projectId is valid, otherwise fallback
    if (route.params.projectId) {
      session.value = updateSwarmbookSession({ projectId: route.params.projectId })
    } else {
      router.replace({ name: 'SwarmbookHome' })
      return
    }
  }

  if (report.value) {
    return
  }

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
    console.warn('Report fetch failed (expected if local server is down or empty):', requestError.message)
    // We do not set the top-level error ref instantly to avoid rendering a red banner.
    // Instead we let the user click the demo loader button inside the empty state.
  } finally {
    loading.value = false
    loadingMessage.value = ''
  }
}

onMounted(() => {
  ensureReport()
})
</script>

<style scoped>
/* Redesigned Premium SaaS-Grade CSS Styling */

/* Focus overrides targeting WCAG 2.2 AA AA standards */
button:focus-visible,
a:focus-visible,
[role="tab"]:focus-visible,
[tabindex="0"]:focus-visible {
  outline: 2px solid #FF4500 !important;
  outline-offset: 3px !important;
}

/* Actions Panel */
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  background: #ffffff;
  padding: 16px 24px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 24px;
}

.nav-links-row, 
.export-actions-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* Button variants styling */
.primary-btn {
  background: #000000;
  color: #ffffff;
  border: 1px solid #000000;
  padding: 10px 18px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}

.primary-btn:hover {
  background: #222222;
}

.ghost-btn {
  background: #ffffff;
  color: #0f172a;
  border: 1px solid #cbd5e1;
  padding: 10px 18px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s, border-color 0.15s;
}

.ghost-btn:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}

.disabled-btn {
  opacity: 0.55;
  cursor: not-allowed !important;
  background: #f1f5f9 !important;
  color: #64748b !important;
  border-color: #cbd5e1 !important;
}

/* Tooltip Wrapper */
.tooltip-container {
  position: relative;
  display: inline-block;
}

.tooltip-container .tooltip-text {
  visibility: hidden;
  width: 250px;
  background-color: #0f172a;
  color: #ffffff;
  text-align: center;
  border-radius: 6px;
  padding: 10px;
  font-size: 0.78rem;
  line-height: 1.4;
  position: absolute;
  z-index: 10;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.2s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #334155;
}

.tooltip-container:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

/* 6-Card Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 120px;
  transition: box-shadow 0.15s, border-color 0.15s;
}

.summary-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.summary-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
}

.score-display strong {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0f172a;
}

.score-display .priority-title {
  font-size: 1.1rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  word-break: break-all;
}

.band-label {
  font-size: 0.78rem;
  color: #64748b;
  line-height: 1.3;
}

/* Publishing Readiness Card Variant */
.readiness-card.ready { border-left: 4px solid #10b981; }
.readiness-card.mixed { border-left: 4px solid #f59e0b; }
.readiness-card.offline { border-left: 4px solid #ef4444; }

.status-indicator-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: auto;
}

.status-indicator-text.ready { background: #d1fae5; color: #065f46; }
.status-indicator-text.mixed { background: #fef3c7; color: #92400e; }
.status-indicator-text.offline { background: #fef2f2; color: #991b1b; }

.meter-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 8px;
}

.meter-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.readiness-card.ready .meter-fill { background: #10b981; }
.readiness-card.mixed .meter-fill { background: #f59e0b; }
.readiness-card.offline .meter-fill { background: #ef4444; }

/* Highlights colors on warning/priority cards */
.warning-highlight { border-top: 3px solid #f59e0b; }
.error-highlight { border-top: 3px solid #ef4444; }

.text-ready { color: #10b981; }
.text-mixed { color: #f59e0b; }
.text-offline { color: #ef4444; }

/* Double Column Sections */
.section-grid-double {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

@media (max-width: 960px) {
  .section-grid-double {
    grid-template-columns: 1fr;
  }
}

.premium-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
}

.scrollable-card {
  max-height: 520px;
  overflow-y: auto;
}

.card-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 800;
  color: #FF4500;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.premium-card h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 16px;
  letter-spacing: -0.3px;
}

.muted-p {
  color: #64748b;
  font-size: 0.88rem;
  line-height: 1.4;
}

.margin-bottom-lg {
  margin-bottom: 20px;
}

.margin-top-md {
  margin-top: 16px;
}

/* Executive Verdict Styles */
.verdict-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafafb 100%);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.metadata-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 4px;
}

.draft-badge {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.confidence-badge {
  background: #faf5ff;
  color: #6b21a8;
  border: 1px solid #f3e8ff;
}

.privacy-badge.local_only { background: #d1fae5; color: #065f46; }
.privacy-badge.hybrid_safe { background: #fef3c7; color: #92400e; }
.privacy-badge.cloud_quality { background: #dbeafe; color: #1e40af; }

.verdict-summary-text {
  font-size: 1.05rem;
  line-height: 1.7;
  color: #1e293b;
  font-family: 'Space Grotesk', system-ui, sans-serif;
  border-left: 3px solid #000000;
  padding-left: 16px;
  margin-top: auto;
  margin-bottom: auto;
}

/* Rating overall metrics display */
.rating-overall-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 6px;
}

.big-stars {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0f172a;
}

.rating-overall-header .muted-p {
  flex: 1;
}

/* Star Histogram styles */
.star-histogram {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.histogram-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.star-text-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
  width: 50px;
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

.star-percent-text {
  font-size: 0.82rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #1e293b;
  width: 40px;
}

/* Drivers lists styles */
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
  font-size: 0.78rem;
  text-transform: uppercase;
  color: #475569;
  margin-bottom: 12px;
  font-weight: 800;
}

.drivers-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.driver-pill {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 0.78rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.driver-pill .label {
  color: #64748b;
}

/* Table Style Dashboard Blocks */
.dashboard-block-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
}

.dashboard-block-section h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 8px;
}

.section-desc {
  color: #64748b;
  font-size: 0.88rem;
  margin-bottom: 20px;
}

/* Responsive Table */
.table-container {
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.segments-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.85rem;
}

.segments-table th {
  background: #f8fafc;
  color: #475569;
  font-weight: 700;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.segments-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
  color: #334155;
  line-height: 1.4;
}

.segments-table tr:last-child td {
  border-bottom: none;
}

.bold-cell {
  font-weight: 600;
}

.signal-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 4px;
}

.signal-badge.positive { background: #d1fae5; color: #065f46; }
.signal-badge.mixed { background: #fef3c7; color: #92400e; }
.signal-badge.negative { background: #fef2f2; color: #991b1b; }

.sentiment-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.sentiment-tag {
  background: #f1f5f9;
  color: #475569;
  font-size: 0.72rem;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.empty-table-cell {
  text-align: center;
  padding: 32px !important;
  color: #94a3b8;
  font-style: italic;
}

/* DNF Drivers Analysis */
.dnf-drivers-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dnf-driver-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dnf-driver-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
}

.dnf-driver-header .label {
  font-weight: 600;
  color: #334155;
}

.dnf-driver-header strong {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
}

.dnf-driver-track {
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.dnf-driver-fill {
  height: 100%;
  border-radius: 3px;
}

.dnf-driver-fill.ready { background: #10b981; }
.dnf-driver-fill.mixed { background: #f59e0b; }
.dnf-driver-fill.offline { background: #ef4444; }

/* Timeline chapter pressure points */
.timeline {
  display: flex;
  flex-direction: column;
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 11px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: #e2e8f0;
}

.timeline-item {
  position: relative;
  padding-bottom: 24px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -24px;
  top: 2px;
  width: 24px;
  height: 24px;
  background: #ffffff;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.marker-num {
  font-size: 0.7rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #475569;
}

.timeline-item.high-pressure .timeline-marker {
  border-color: #ef4444;
  background: #fef2f2;
}

.timeline-item.high-pressure .marker-num {
  color: #ef4444;
}

.timeline-content {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px 16px;
  margin-left: 12px;
  transition: border-color 0.15s;
}

.timeline-item.high-pressure .timeline-content {
  border-left: 3px solid #ef4444;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  flex-wrap: wrap;
  gap: 8px;
}

.timeline-header h3 {
  font-size: 0.9rem;
  margin: 0;
  font-weight: 700;
}

.dnf-value-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
}

.dnf-value-badge.ready { background: #d1fae5; color: #065f46; }
.dnf-value-badge.mixed { background: #fef3c7; color: #92400e; }
.dnf-value-badge.offline { background: #fef2f2; color: #991b1b; }

.timeline-reason {
  font-size: 0.8rem;
  color: #475569;
  line-height: 1.4;
}

/* Controversy axis layout */
.radar-card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.radar-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.radar-bar-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
}

.radar-bar-header .label {
  font-weight: 600;
  color: #334155;
}

.radar-bar-header strong {
  font-family: 'JetBrains Mono', monospace;
}

.radar-bar-track {
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.radar-bar-fill {
  height: 100%;
  border-radius: 3px;
}

.radar-bar-fill.ready { background: #10b981; }
.radar-bar-fill.mixed { background: #f59e0b; }
.radar-bar-fill.offline { background: #ef4444; }

/* Hotspots container */
.hotspots-box {
  margin-top: 20px;
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}

.hotspots-list {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hotspots-list li {
  font-size: 0.78rem;
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
  padding: 4px 10px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}

/* Viral platform comparison chart */
.viral-platform-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.platform-bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.platform-name-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  width: 90px;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.platform-bar-track {
  flex: 1;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.platform-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}

/* Unique Platform Branding colors */
.platform-color-goodreads { background: #774c2a; }
.platform-color-booktok { background: #01f2ff; box-shadow: 0 0 4px #01f2ff; }
.platform-color-reddit { background: #ff4500; }
.platform-color-bookstagram { background: #c13584; }
.platform-color-x { background: #0f172a; }
.platform-color-newsletter { background: #3b82f6; }
.platform-color-bookclub { background: #10b981; }

.platform-percentage-value {
  font-size: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #1e293b;
  width: 35px;
}

.viral-drivers-box {
  margin-top: 16px;
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}

/* Platform Post Feed visual tabs */
.tab-row-container {
  overflow-x: auto;
  margin-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.tab-row {
  display: flex;
  gap: 4px;
  padding-bottom: 8px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #64748b;
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.15s;
  white-space: nowrap;
}

.tab-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.tab-btn.active {
  background: #000000;
  color: #ffffff;
}

.tab-count-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  background: rgba(255, 69, 0, 0.15);
  color: #FF4500;
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 700;
}

.tab-btn.active .tab-count-badge {
  background: #ffffff;
  color: #000000;
}

/* Mock social feed posts styling */
.feed-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.mock-post-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s;
}

.mock-post-card:hover {
  transform: translateY(-2px);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  font-size: 1.25rem;
  background: #f1f5f9;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.display-name {
  font-size: 0.82rem;
  color: #1e293b;
}

.handle {
  font-size: 0.72rem;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
}

.post-platform-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
}

.post-platform-tag.goodreads { background: #ecdcc9; color: #5c381c; }
.post-platform-tag.booktok { background: #000000; color: #ffffff; border: 1px solid #00f2fe; }
.post-platform-tag.reddit { background: #ffe9e0; color: #ff4500; }
.post-platform-tag.bookstagram { background: #fde2f3; color: #c13584; }
.post-platform-tag.x { background: #f1f5f9; color: #0f172a; }

/* Card custom bodies */
.post-body {
  flex: 1;
  margin-bottom: 14px;
}

.post-stars-row {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.star-rating {
  color: #fbbf24;
  font-size: 1rem;
}

.rating-value {
  font-size: 0.75rem;
  color: #64748b;
}

.subreddit-tag {
  font-size: 0.72rem;
  color: #475569;
  font-weight: 700;
  margin-bottom: 8px;
}

.post-text {
  font-size: 0.88rem;
  line-height: 1.5;
  color: #334155;
  word-break: break-word;
}

/* Simulated TikTok layout video player */
.tiktok-video-mock {
  height: 160px;
  background: #111113;
  border-radius: 6px;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 0.82rem;
  position: relative;
  overflow: hidden;
  border: 1px solid #334155;
}

.tiktok-video-mock::before {
  content: '▶';
  font-size: 1.8rem;
  opacity: 0.75;
  margin-bottom: 20px;
}

.video-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hook-text {
  font-style: italic;
  font-size: 0.72rem;
  color: #cbd5e1;
}

.post-hashtags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.post-hashtags .tag {
  color: #3b82f6;
  font-size: 0.78rem;
  font-weight: 600;
}

.mock-post-booktok .tag {
  color: #00f2fe;
}

.post-shelf-tags {
  margin-top: 8px;
  font-size: 0.75rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.tag-title {
  font-weight: 700;
  color: #64748b;
}

.shelf-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 1px 6px;
  border-radius: 4px;
}

/* Post engagement actions */
.post-footer {
  border-top: 1px solid #f1f5f9;
  padding-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
  color: #64748b;
}

.hot-take-label {
  background: #fff7ed;
  color: #c2410c;
  font-weight: 800;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #ffedd5;
  font-family: 'JetBrains Mono', monospace;
}

.viral-trigger-label {
  background: #fef8e6;
  color: #b45309;
  font-weight: 800;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #fef3c7;
  font-family: 'JetBrains Mono', monospace;
}

/* BookTok custom dark layout overlay overrides */
.mock-post-booktok {
  background: #121214;
  border-color: #27272a;
}

.mock-post-booktok .display-name {
  color: #f4f4f5;
}

.mock-post-booktok .handle {
  color: #a1a1aa;
}

.mock-post-booktok .post-text {
  color: #e4e4e7;
}

.mock-post-booktok .post-footer {
  border-color: #27272a;
  color: #a1a1aa;
}

.mock-post-booktok .avatar {
  background: #27272a;
}

/* Quote Candidates card layout */
.quotes-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pull-quote-card {
  background: #fafafb;
  border-left: 4px solid #FF4500;
  padding: 16px;
  border-radius: 0 6px 6px 0;
  position: relative;
}

.pull-quote-card::before {
  content: '“';
  font-size: 3rem;
  color: #e2e8f0;
  position: absolute;
  left: 10px;
  top: -10px;
  font-family: serif;
  line-height: 1;
}

.pull-quote-card p {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #1e293b;
  font-style: italic;
  position: relative;
  z-index: 2;
  margin-bottom: 8px;
}

.pull-quote-card cite {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #64748b;
  display: block;
  font-style: normal;
  text-transform: uppercase;
}

/* Revision Checklist priorities card stack */
.priorities-checklist-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.priority-checklist-item {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 18px;
  display: flex;
  gap: 16px;
  transition: border-color 0.15s;
}

.priority-checklist-item:hover {
  border-color: #cbd5e1;
}

@media (max-width: 600px) {
  .priority-checklist-item {
    flex-direction: column;
    gap: 8px;
  }
}

.priority-item-side {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 140px;
  flex-shrink: 0;
}

.priority-label-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;
  text-transform: uppercase;
}

.priority-label-pill.critical { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
.priority-label-pill.high { background: #fff7ed; color: #f97316; border: 1px solid #ffedd5; }
.priority-label-pill.medium { background: #fef8e6; color: #d97706; border: 1px solid #fef3c7; }
.priority-label-pill.low { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }

.item-type-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 700;
  text-align: center;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

.priority-item-main {
  flex: 1;
}

.priority-item-main h3 {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #0f172a;
}

.reasons-bullet-list {
  list-style: none;
  padding: 0;
  margin-bottom: 10px;
  display: grid;
  gap: 4px;
}

.reasons-bullet-list li {
  font-size: 0.82rem;
  color: #475569;
}

.reasons-bullet-list li::before {
  content: '• ';
  color: #FF4500;
  font-weight: bold;
}

.item-evidence {
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.evidence-pill {
  background: #f1f5f9;
  color: #475569;
  padding: 1px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
}

/* Hooks and strengths formatting */
.hooks-box {
  background: #fafafb;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.bullets-list-styled {
  list-style: none;
  padding: 0;
  display: grid;
  gap: 8px;
}

.bullets-list-styled li {
  font-size: 0.88rem;
  color: #334155;
  line-height: 1.4;
  padding-left: 18px;
  position: relative;
}

.bullets-list-styled li::before {
  content: '✓';
  color: #10b981;
  position: absolute;
  left: 0;
  font-weight: bold;
}

.hooks-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hook-pill {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
  font-size: 0.78rem;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: 600;
}

/* Risks and Caveats blocks formatting */
.warning-box {
  background: #fffaf0;
  border: 1px solid #feebc8;
  padding: 16px;
  border-radius: 6px;
}

.bullets-list-warning {
  list-style: none;
  padding: 0;
  display: grid;
  gap: 8px;
}

.bullets-list-warning li {
  font-size: 0.88rem;
  color: #7b341e;
  line-height: 1.4;
  padding-left: 18px;
  position: relative;
}

.bullets-list-warning li::before {
  content: '⚠️';
  position: absolute;
  left: 0;
  font-size: 0.8rem;
}

.uncertainty-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 16px;
  border-radius: 6px;
}

/* Limitations info banner banner */
.limitations-info-banner {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 18px;
  display: flex;
  gap: 14px;
  margin-top: 24px;
  margin-bottom: 24px;
}

.limitations-info-banner .info-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.limitations-info-banner h3 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e3a8a;
  margin-bottom: 6px;
}

.limitations-info-banner p {
  font-size: 0.82rem;
  line-height: 1.5;
  color: #1e40af;
  margin: 0;
}

/* Empty state styling fallbacks */
.empty-state-card {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 60px 40px;
  text-align: center;
  max-width: 600px;
  margin: 40px auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
}

.empty-state-card h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 12px;
}

.empty-state-card p {
  font-size: 0.92rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 30px;
}

.empty-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.empty-actions .primary-btn {
  padding: 12px 24px;
}

.empty-actions .ghost-btn {
  padding: 12px 24px;
}

.padding-xl {
  padding: 48px;
}

.padding-xl.text-center {
  text-align: center;
}

/* Sticky Nav & Jump Links */
.sticky-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(8px);
}

.jump-nav {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
  flex: 1 1 100%;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 8px;
}

.jump-nav a {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--sb-color-brand, #3b82f6);
  text-decoration: none;
  white-space: nowrap;
}

.jump-nav a:hover {
  text-decoration: underline;
}

.scrollable-feed {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

.chart-summary {
  font-size: 0.75rem;
  color: var(--sb-text-muted, #64748b);
  text-align: center;
  margin-top: 8px;
  font-style: italic;
}

/* Hidden PNG Capture Card */
.png-summary-capture-card {
  display: none; /* hidden until capture */
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
.png-card-verdict h2 { font-size: 1.25rem; font-weight: 700; margin-bottom: 12px; color: #047857; }
.png-card-metrics { display: flex; justify-content: space-between; margin-bottom: 24px; }
.png-metric { background: #ffffff; padding: 16px; border-radius: 8px; text-align: center; flex: 1; margin: 0 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.png-metric span { display: block; font-size: 0.85rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }
.png-metric strong { display: block; font-size: 1.5rem; font-weight: 800; }
.png-card-priorities { padding: 20px; background: #fee2e2; border-radius: 8px; border-left: 4px solid #ef4444; }
.png-card-priorities h3 { color: #b91c1c; font-size: 1.1rem; margin-bottom: 8px; }

</style>
