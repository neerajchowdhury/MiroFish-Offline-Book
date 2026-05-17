# Swarmbook Architecture

## Goal

Swarmbook transforms MiroFish-Offline from a general social-reaction simulator into a local-first personal tool for simulating how readers may react to any book-length work. The target input is a fiction or non-fiction manuscript plus optional packaging context such as title, subtitle, blurb, genre, comps, and audience assumptions.

The product goal is not public posting or platform automation. The goal is private pre-publication stress testing:

- ingest a manuscript safely on local hardware
- generate structured evidence about the book
- simulate diverse reader cohorts and platform-native reactions
- detect friction, delight, confusion, controversy, and drop-off risk
- produce prediction reports and interviewable synthetic readers
- compare drafts without exposing manuscript text unnecessarily

Swarmbook must preserve existing MiroFish-Offline behavior until the new path proves stable. The transformation is additive, not a rewrite.

## First Build Scope

The first release merges MVP1, MVP2, and MVP3 into one bounded local product slice:

- MVP1: manuscript ingest, evidence-pack generation, book graph creation
- MVP2: reader cohort generation, private reading simulation, platform-style reactions
- MVP3: scoring, prediction report, agent interrogation, and draft comparison

This merged scope is still intentionally narrow:

- local-first by default
- simulated platform adapters only
- structured JSON artifacts at each stage
- no live Goodreads, TikTok, Instagram, Reddit, or X scraping
- no claims of market certainty

## Design Principles

- Preserve the current MiroFish-Offline graph, simulation, and report stack unless a change is strictly necessary.
- Add `book_sim` modules beside the existing simulation modules rather than repurposing social-platform code in place.
- Keep local Ollama and Neo4j as first-class runtime dependencies.
- Route all external model use through provider adapters and privacy-mode policy.
- Store intermediate artifacts as compact JSON so later phases can be replayed, diffed, and audited.
- Treat unpublished manuscripts as sensitive local IP.

## End-to-End Pipeline

Swarmbook extends the current upload -> graph -> simulation -> report shape into a book-specific pipeline:

### 1. Manuscript Ingest

Input:

- manuscript files: `pdf`, `md`, `txt`, `markdown`
- optional metadata: title, subtitle, blurb, genre, target audience, comp titles, author notes

Responsibilities:

- safe file validation and parsing
- chunking into scenes, sections, chapters, and book-level summaries
- package metadata normalization
- privacy-mode policy check before any cloud-bound step

Primary outputs:

- `manuscript_manifest.json`
- `chunk_index.json`
- `chapter_boundaries.json`
- `package_context.json`

### 2. Evidence-Pack Generation

Generate a structured manuscript intelligence layer before any persona or simulation work. This reduces repeated prompt cost and keeps downstream stages compact.

Primary outputs:

- `book_dna.json`
- `chapter_map.json`
- `character_map.json`
- `claim_map.json` for non-fiction
- `risk_map.json`
- `style_map.json`
- `market_surface.json`

### 3. Book Graph Creation

Build a graph specialized for books while reusing the existing Neo4j abstraction:

- nodes for characters, factions, settings, objects, themes, claims, arguments, scenes, chapters, risks, and market comps
- edges for relationships such as `APPEARS_IN`, `CONFLICTS_WITH`, `SUPPORTS`, `FORESHADOWS`, `CONTRADICTS`, `TRANSFORMS`, and `TARGETS_READER_SEGMENT`

This graph should remain separate from the existing social-event graph shape when needed, but use the same storage interface and retrieval tooling where possible.

Primary outputs:

- `book_graph_manifest.json`
- Neo4j graph namespace or project-scoped labels

### 4. Reader Cohort and Persona Generation

Generate compact synthetic readers as structured taste vectors rather than long biographies. Cohorts should include:

- genre loyalists
- casual browsers
- literary readers
- trope-seeking readers
- plot-logic readers
- emotional readers
- skeptics and adversarial readers
- non-fiction domain readers for claim-driven books

Each agent should capture:

- reading taste
- patience level
- delight triggers
- DNF triggers
- review style
- platform home
- influence score
- spoiler tolerance
- sensitivity to pacing, ideology, ambiguity, prose density, and factual rigor

Primary outputs:

- `reader_cohorts.json`
- `reader_personas.json`

### 5. Platform-Style Reactions

Simulate how each reader responds in formats inspired by platform norms, but without hitting real platforms:

- Goodreads-style star review and shelf behavior
- BookTok-style emotional short-form reaction
- Reddit-style discussion post or comment thread
- Bookstagram-style aesthetic reaction summary
- X or Threads-style hot take
- newsletter or blog-style reflective review

The system should separate:

- private reading reaction
- public-facing platform expression

That separation matters because a reader may finish a book privately with mixed feelings and still post a more polarized public reaction.

Primary outputs:

- `private_reactions.json`
- `platform_reactions.json`

### 6. Cross-Reader Reactions

After initial reactions, readers should see selected reactions from other agents and update their stance probabilistically. This stage models:

- dogpiles
- backlash
- cult-niche clustering
- quote amplification
- confusion contagion
- recommendation cascades

Primary outputs:

- `exposure_events.json`
- `opinion_updates.json`
- `cascade_signals.json`

### 7. Scoring

Compute structured scorecards from distributions rather than single deterministic verdicts.

Core score families:

- rating distribution
- completion and DNF risk
- confusion risk
- attachment strength
- controversy and backlash risk
- quoteability and shareability
- pacing drag
- claim credibility for non-fiction
- market positioning fit
- revision priority ranking

Primary outputs:

- `scorecard.json`
- `segment_scores.json`
- `revision_priorities.json`

### 8. Prediction Report

Generate a structured report that summarizes what the swarm predicts, where the confidence is weak, and what revision levers matter most.

Report sections should cover:

- likely audience response by segment
- strongest praise drivers
- strongest friction drivers
- DNF hotspots
- controversy triggers
- packaging mismatch
- positioning recommendations
- confidence and uncertainty notes

Primary outputs:

- `prediction_report.json`
- `prediction_report.md`

### 9. Agent Interrogation

Allow the user to interview selected synthetic readers after the simulation:

- why they liked or disliked a passage
- where they almost stopped reading
- what claim felt weak or unsupported
- what would make them recommend the book

This should reuse the current interaction pattern conceptually, but operate on book-simulation state and evidence packs.

Primary outputs:

- `agent_interviews.json`

### 10. Draft Comparison

Support side-by-side comparison between manuscript versions by replaying evidence-pack generation and scoring on both versions.

Comparison targets:

- pacing changes
- chapter-level confusion shifts
- character attachment shifts
- claim-strength shifts
- rating distribution changes
- DNF risk movement
- revised market position

Primary outputs:

- `draft_comparison.json`
- `draft_delta_report.md`

## Evidence Packs

Evidence packs are the core compression layer. They convert manuscript-scale text into reusable structured artifacts that later modules can consume cheaply.

### Book DNA

Captures the book's high-level identity:

- premise
- genre and subgenre
- tonal profile
- emotional promise
- reading difficulty
- narrative engine or thesis engine
- comparable titles
- likely promise-to-reader

### Chapter Map

Tracks chapter-by-chapter structure:

- chapter purpose
- beat summary
- pacing estimate
- confusion hotspots
- revelation points
- transition quality
- stop-reading risk markers

### Character Map

Primarily for fiction:

- cast list
- goals
- conflicts
- transformations
- attachment potential
- relationship edges
- scene centrality

### Claim Map

Primarily for non-fiction:

- core claims
- supporting arguments
- anecdotal versus evidence-backed support
- contradiction or overreach risk
- reader trust sensitivity

### Risk Map

Surfaces synthetic-review risks without making moral claims of certainty:

- pacing drag
- thin motivation
- ideological backlash
- factual challenge risk
- tonal mismatch
- trope fatigue
- ending dissatisfaction
- packaging mismatch

### Style Map

Models how prose style may land:

- density
- clarity
- rhythm
- quoteability
- sentiment texture
- repetition
- accessibility
- voice consistency

### Market Surface

Maps how the book may present in the market:

- target segments
- comp-title neighborhood
- packaging expectations
- likely discoverability hooks
- likely mismatch between actual book and implied promise

## Hybrid Model Strategy

Swarmbook should use a cost-aware, privacy-aware hybrid model stack instead of one model for all stages.

### Local Ollama

Default use cases:

- chunking helpers and local summarization
- embeddings
- chapter and scene compression
- cheap persona expansion
- cheap private reactions
- low-cost opinion updates
- local-first fallback for every stage

Reason:

- keeps sensitive manuscript processing on the local machine
- preserves offline or mostly-offline usability
- aligns with the current MiroFish-Offline deployment model

### Gemini

Preferred use cases when privacy mode allows:

- long-context manuscript synthesis
- evidence-pack consolidation across many chapters
- structured prediction report generation
- draft comparison synthesis
- higher-quality segment summaries

Reason:

- better fit for long-context reasoning and structured synthesis than using local models alone in the early product phase

### NVIDIA API or NIM

Optional use cases:

- fallback inference when Gemini is unavailable
- adversarial review pass
- alternate perspective generation for stress testing
- secondary scoring or disagreement checks

Reason:

- provides model diversity without hardwiring a single external provider

### Provider Boundary

All model calls should go through a provider abstraction that supports:

- provider selection by privacy mode
- structured JSON output validation
- retries and timeout policies
- redaction policy for cloud-bound payloads
- model capability tags such as `cheap_local`, `long_context`, `adversarial_review`

No direct Gemini or NVIDIA calls should be scattered through simulation code.

## Privacy Modes

Swarmbook must make privacy tradeoffs explicit and user-controlled.

### `local_only`

- manuscript text stays local
- Ollama handles all stages
- no external provider calls
- quality may be lower on long-context synthesis and reporting

### `hybrid_safe`

- local processing for ingest, embeddings, chunking, and most simulation stages
- cloud use limited to compact evidence packs, derived summaries, or redacted slices
- default hybrid mode for users who want better synthesis without sending full manuscripts by default

### `cloud_quality`

- allows larger cloud-bound synthesis tasks when explicitly enabled
- full or near-full evidence-pack payloads may be sent to configured providers
- highest expected report quality, weakest privacy posture

Every run should record the chosen privacy mode in its manifest and artifact metadata.

## Additive Backend Module Structure

The cleanest additive path is a new package under `backend/app/book_sim`, while reusing existing storage and reporting abstractions.

Proposed structure:

```text
backend/app/book_sim/
  __init__.py
  api/
    __init__.py
    book_sim.py
  models/
    artifacts.py
    requests.py
    scoring.py
  services/
    ingest_service.py
    evidence_pack_service.py
    book_graph_service.py
    persona_factory.py
    platform_reaction_service.py
    cross_reader_service.py
    scoring_service.py
    report_service.py
    interrogation_service.py
    draft_compare_service.py
  providers/
    base.py
    ollama_provider.py
    gemini_provider.py
    nvidia_provider.py
    router.py
  storage/
    artifact_store.py
  prompts/
    evidence_pack_prompts.py
    reaction_prompts.py
    report_prompts.py
  schemas/
    book_dna.py
    chapter_map.py
    character_map.py
    claim_map.py
    risk_map.py
    style_map.py
    market_surface.py
```

Recommended reuse points from the current app:

- `backend/app/storage/graph_storage.py`
- `backend/app/storage/neo4j_storage.py`
- `backend/app/storage/search_service.py`
- `backend/app/services/graph_tools.py`
- `backend/app/services/report_agent.py` as a conceptual reference, not as a dumping ground
- `backend/app/utils/llm_client.py` only if wrapped behind a cleaner provider interface

Recommended boundary:

- existing `api/simulation.py` remains the current social-simulation path
- new `book_sim/api/book_sim.py` exposes a parallel book-specific route family
- current services are reused only where contracts align cleanly

## Frontend Additions

The frontend should add book-specific views instead of stretching the current simulation screens past their intended shape.

Proposed additions:

- `BookProjectSetupView`
- `BookEvidenceView`
- `ReaderCohortView`
- `BookSimulationView`
- `PredictionReportView`
- `AgentInterrogationView`
- `DraftComparisonView`

Likely component families:

- manuscript upload and metadata form
- evidence-pack explorer
- chapter and character heatmaps
- cohort distribution tables
- reaction timeline and cascade panels
- scorecard cards and uncertainty panels
- draft delta comparison tables

Frontend state should track:

- privacy mode
- provider availability
- active manuscript version
- simulation status
- artifact download and replay handles

## Implementation Phases

### Phase 1: Documentation and Contracts

- architecture document
- artifact schema definitions
- privacy-mode contract
- provider abstraction design

### Phase 2: Ingest and Evidence Packs

- manuscript manifest
- chunking and chapter boundaries
- Book DNA, chapter map, character or claim maps
- local artifact persistence

### Phase 3: Book Graph

- book graph schema
- project-scoped graph build path
- retrieval helpers for downstream book simulation

### Phase 4: Persona Factory and Platform Reactions

- reader cohorts
- compact personas
- private reaction generation
- platform-style expression layer

### Phase 5: Cross-Reader Dynamics and Scoring

- exposure and opinion updates
- cascade detection
- scorecard generation

### Phase 6: Reporting, Interrogation, and Draft Comparison

- structured prediction report
- agent Q&A
- draft delta workflow

### Phase 7: Hardening

- privacy-mode enforcement
- provider failover behavior
- artifact replay tests
- smoke tests and regression coverage

## Known Limitations

Swarmbook is a synthetic stress-test tool, not a guaranteed market predictor.

Known limits:

- synthetic readers are useful approximations, not real human readers
- outputs depend on evidence-pack quality and model quality
- virality, controversy, and recommendation behavior are inherently unstable
- niche audiences may be under-modeled unless cohorts are tuned explicitly
- non-fiction factual trust modeling is heuristic, not formal truth verification
- draft comparison can reveal directional improvements, not certainty of commercial outcome

The product should present outputs as decision support, not forecast certainty.

## Suggested Initial JSON Artifact Set

The first implementation slice should standardize these project-scoped artifacts:

```text
manuscript_manifest.json
chunk_index.json
chapter_boundaries.json
book_dna.json
chapter_map.json
character_map.json
claim_map.json
risk_map.json
style_map.json
market_surface.json
reader_cohorts.json
reader_personas.json
private_reactions.json
platform_reactions.json
opinion_updates.json
scorecard.json
prediction_report.json
agent_interviews.json
draft_comparison.json
```

This artifact-first design keeps the transformation auditable, replayable, and compatible with the local-first character of MiroFish-Offline.
