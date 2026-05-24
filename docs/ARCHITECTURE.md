# MiroFish-Offline Architecture

## Overview

MiroFish-Offline is a fully local multi-agent swarm intelligence engine that simulates public opinion, market sentiment, and social dynamics. It runs entirely on local hardware using Neo4j Community Edition for graph storage and Ollama for LLM inference — zero cloud APIs required.

The **Swarmbook** module is an additive extension that transforms MiroFish into a "simulate any book" tool for authors to stress-test manuscripts before publication.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (Vue 3 + Vite)                    │
│  Legacy MiroFish UI (/) + Swarmbook UI (/swarmbook/*)        │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼───────────────────────────────────────┐
│                    Flask Backend (Python 3.11)                │
│                                                              │
│  Legacy Routes:          Swarmbook Routes (additive):        │
│  /api/graph/*            /api/book-sim/projects              │
│  /api/simulation/*       /api/book-sim/evidence-packs        │
│  /api/report/*           /api/book-sim/simulate              │
│                          /api/book-sim/personas/<id>/chat    │
│                          /api/book-sim/compare               │
│                          /api/book-sim/health                │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                    Service / Storage Layer                    │
│                                                              │
│  Legacy:                 Swarmbook (book_sim):               │
│  GraphStorage (abstract)  ProviderRouter (+ PrivacyGuard)    │
│  Neo4jStorage             EvidencePackBuilder                │
│  SearchService            SimulationOrchestrator             │
│  EmbeddingService         ScoringEngine (7 modules)          │
│  NERExtractor             ReportBuilder                      │
│  EntityReader             PersonaInterrogator                │
│  ReportAgent              DraftComparator                    │
│  SimulationManager        BookGraphPersistence              │
│  OasisProfileGenerator    RuntimeStore (atomic file-backed)  │
│                          LocalArtifactCache (thread-safe)    │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                    External Services                          │
│                                                              │
│  Neo4j CE 5.18 (graph DB)  Ollama (local LLM)               │
│  [Optional] Gemini API     [Optional] NVIDIA NIM API         │
└───────────────────────────────────────────────────────────────┘
```

---

## Two Parallel Pipelines

### Legacy MiroFish Pipeline (Social Simulation)

1. **Upload** — User uploads a document (PDF, MD, TXT)
2. **Ontology Generation** — LLM analyzes document to define entity types and relations
3. **Graph Build** — NER/RE extraction creates entities and relationships in Neo4j
4. **Entity Reading** — Entities are filtered and read from the graph
5. **Simulation Preparation** — OASIS agent profiles generated per entity
6. **Simulation Execution** — Multi-round social simulation on Twitter/Reddit
7. **Report** — ReportAgent analyzes results and generates structured analysis
8. **Interview** — Chat with any agent from the simulation

### Swarmbook Pipeline (Book Simulation)

1. **Project Creation** — Create a book project with metadata and privacy mode
2. **Manuscript Ingest** — Parse and chunk manuscript text
3. **Evidence Pack Generation** — Build structured intelligence:
   - **BookDNA** — Genre, tone, premise, themes, target reader
   - **ChapterMap** — Pacing, friction, key beats per chapter
   - **CharacterMap** (fiction) — Character profiles, relationships, arcs
   - **ClaimMap** (nonfiction) — Claims, evidence strength, counterarguments
   - **RiskMap** — Pacing drag, backlash, trope fatigue, factual risks
   - **StyleMap** — Prose density, clarity, quoteability, accessibility
   - **MarketSurface** — Target segments, comp titles, discoverability hooks
4. **Persona Generation** — Generate synthetic readers from YAML archetypes with deterministic seeding
5. **Simulation** — Three-pass pipeline:
   - **Private Reading** — Individual reader reactions (rating, DNF probability, sentiment)
   - **Platform Posts** — Platform-shaped public reactions (Goodreads, BookTok, Reddit, etc.)
   - **Cross-Reactions** — Opinion shifts from peer exposure over multiple rounds
6. **Scoring** — Seven deterministic scoring modules:
   - Rating distribution, DNF risk, viral potential, controversy, quoteability, polarization, revision priorities
7. **Report** — Structured prediction report with segment insights
8. **Interrogation** — Template-based Q&A with simulated readers
9. **Draft Comparison** — Side-by-side comparison of manuscript versions

---

## Provider Routing & Privacy

### Privacy Modes

| Mode | Behavior |
|------|----------|
| `local_only` | No external API calls. Only Ollama permitted. Enforced by PrivacyGuard. |
| `hybrid_safe` | Only derived/compact artifacts may be sent to cloud providers. |
| `cloud_quality` | Full evidence packs may be sent to cloud providers for higher quality. |

### Provider Selection Cascade

```
Requested Route
       │
       ▼
┌──────────────────┐
│ Route exists?    │──No──► Default to local_ollama
└────────┬─────────┘
         │ Yes
         ▼
┌──────────────────┐
│ Privacy mode     │──local_only + cloud provider──► Fallback to local_ollama
│ allowlisted?     │
└────────┬─────────┘
         │ Yes
         ▼
┌──────────────────┐
│ Provider         │──Unavailable──► Fallback to local_ollama
│ available?       │
└────────┬─────────┘
         │ Yes
         ▼
   Use selected provider
         │
         ▼
┌──────────────────┐
│ PrivacyGuard     │──local_only + cloud──► Raise PrivacyViolationError
│ assertion        │
└──────────────────┘
```

### PrivacyGuard

The `PrivacyGuard` singleton provides system-wide enforcement of `local_only` mode. It is checked:
1. In `BookSimProviderRouter.select_route()` — before every provider selection
2. Can be called directly by any code that instantiates providers outside the router

This closes the gap where privacy enforcement was previously only router-scoped.

---

## Data Flow: Evidence Pack

```
Manuscript Text
       │
       ▼
┌─────────────────────┐
│ Chunk (500 chars,   │
│ 50 char overlap)    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│ LLM Analysis (per chunk, via ProviderRouter)        │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ BookDNA  │  │ Chapters │  │ Characters│          │
│  └──────────┘  └──────────┘  └──────────┘          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Claims   │  │ Risks    │  │ Style    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│  ┌──────────┐                                       │
│  │ Market   │                                       │
│  └──────────┘                                       │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  EvidencePack       │
              │  (all components    │
              │   bundled + cached) │
              └─────────────────────┘
```

---

## File Structure

```
backend/
├── app/
│   ├── __init__.py              # Flask app factory, CORS, Neo4j init, teardown
│   ├── config.py                # Config from .env, SECRET_KEY generation
│   ├── api/
│   │   ├── _legacy_error_handler.py  # Shared error decorator for legacy APIs
│   │   ├── book_sim.py          # Swarmbook REST endpoints (816 lines)
│   │   ├── simulation.py        # Legacy OASIS simulation endpoints (2711 lines)
│   │   ├── graph.py             # Graph CRUD endpoints
│   │   └── report.py            # Report generation/chat endpoints
│   ├── book_sim/                # Swarmbook module (additive)
│   │   ├── models.py            # Typed dataclasses (583 lines)
│   │   ├── privacy_guard.py     # System-wide privacy enforcement
│   │   ├── validators.py        # Input validation functions
│   │   ├── provider_router.py   # Model routing with privacy cascade
│   │   ├── config_loader.py     # YAML config loading
│   │   ├── evidence_pack_builder.py  # Manuscript -> evidence pack
│   │   ├── runtime_store.py     # File-backed artifact store (atomic writes)
│   │   ├── local_cache.py       # Thread-safe JSON cache (atomic writes)
│   │   ├── report_builder.py    # Deterministic report synthesis
│   │   ├── graph_persistence.py # Neo4j namespace-scoped writes
│   │   ├── local_profiles.py    # Hardware profile loader
│   │   ├── providers/           # Ollama, Gemini, NVIDIA adapters
│   │   │   ├── base.py          # Abstract provider with retry logic
│   │   │   ├── ollama_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   └── nvidia_provider.py
│   │   ├── simulation/          # Three-pass simulation pipeline
│   │   │   ├── simulation_orchestrator.py
│   │   │   ├── private_reading_pass.py
│   │   │   ├── platform_reaction_pass.py
│   │   │   └── cross_reaction_pass.py
│   │   ├── platform_adapters/   # Goodreads, BookTok, Reddit, etc.
│   │   ├── scoring/             # 7 scoring modules
│   │   ├── interrogation/       # Persona Q&A
│   │   └── comparison/          # Draft comparison
│   ├── storage/                 # Graph storage abstraction
│   │   ├── graph_storage.py     # Abstract interface
│   │   ├── neo4j_storage.py     # Neo4j CE implementation
│   │   ├── embedding_service.py
│   │   ├── ner_extractor.py
│   │   └── search_service.py
│   ├── services/                # Legacy simulation services
│   └── models/                  # Legacy data models
├── tests/                       # Unit tests (46-48 passing)
├── run.py                       # Entry point
├── requirements.txt
├── pyproject.toml               # Python 3.11 only (CAMEL-AI constraint)
└── .env.example                 # Template for environment variables

configs/book_sim/                # YAML configs for Swarmbook
docs/                            # Extensive Swarmbook documentation
frontend/                        # Vue 3 + Vite frontend
```

---

## Key Design Decisions

### Additive Architecture
Swarmbook modules live under `book_sim/` without modifying legacy code. This preserves the original MiroFish behavior while adding new capabilities.

### Evidence-First Design
Evidence packs compress manuscript text into reusable structured artifacts, reducing repeated LLM calls. Downstream stages (simulation, scoring, reporting) all consume the same evidence pack.

### Deterministic Simulation
The `simulation_seed` parameter enables reproducible runs. The same seed + evidence pack + persona count produces identical results.

### File-Backed Persistence
The runtime store uses the local filesystem for persistence (not a database). This is acceptable for a local-first tool but limits scalability. Atomic writes (temp file + rename) prevent corruption from crashes.

### Two Parallel Simulation Systems
Legacy (OASIS/CAMEL-AI) and Swarmbook (custom pipeline) share no code. This is a deliberate trade-off: Swarmbook's pipeline is purpose-built for book simulation and would be constrained by OASIS's social media simulation model.

---

## Security Model

1. **Secret Key** — Generated randomly at startup if not configured via `SECRET_KEY` env var
2. **CORS** — Restricted to configurable origins (default: localhost dev servers)
3. **Traceback Protection** — Legacy API errors log tracebacks server-side only; clients receive generic messages
4. **API Key Handling** — Cloud provider keys sent via `Authorization` headers, not URL params
5. **Cypher Injection** — Dynamic labels sanitized before interpolation
6. **Privacy Enforcement** — PrivacyGuard singleton prevents cloud provider calls in `local_only` mode
