# MiroFish-Offline-Book: Comprehensive Remediation Plan

> Generated: 2026-05-20
> Scope: All 6 phases, executed sequentially
> Total items: 22 fixes across security, bugs, architecture, quality, docs, and infra

---

## Phase 1: Critical Security Fixes (P0)

### 1.1 Fix Hardcoded SECRET_KEY

**File:** `backend/app/config.py`

**Change:** Replace hardcoded default with cryptographically random key.

```python
# BEFORE (line 24):
SECRET_KEY = os.environ.get('SECRET_KEY', 'mirofish-secret-key')

# AFTER:
def _generate_secret_key() -> str:
    """Generate a random secret key if none is configured."""
    import secrets
    return secrets.token_hex(32)

SECRET_KEY = os.environ.get('SECRET_KEY') or _generate_secret_key()
```

Also create `backend/.env.example`:
```
# Flask
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
FLASK_DEBUG=True

# LLM (Ollama)
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=qwen2.5:32b

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# Embedding
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://localhost:11434

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Cloud providers (optional)
GEMINI_API_KEY=
GEMINI_BASE_URL=https://generativelanguage.googleapis.com
NVIDIA_API_KEY=
```

---

### 1.2 Remove Traceback Exposure from Legacy API

**Files:** `backend/app/api/simulation.py`, `backend/app/api/graph.py`, `backend/app/api/report.py`

**Strategy:** Create a shared `_legacy_api_route` decorator, then apply it to all endpoints.

**New file:** `backend/app/api/_legacy_error_handler.py`
```python
"""Shared error handling for legacy MiroFish API endpoints."""

from functools import wraps
from flask import jsonify
from ..utils.logger import get_logger

logger = get_logger('mirofish.api.error_handler')


def legacy_api_route(handler):
    """Wrap a legacy route with structured JSON error handling.
    
    Logs full tracebacks server-side but returns only safe messages to clients.
    """
    @wraps(handler)
    def wrapped(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except ValueError as exc:
            return jsonify({
                "success": False,
                "error": str(exc),
            }), 400
        except Exception as exc:
            logger.exception("Legacy API endpoint failed: %s", handler.__name__)
            return jsonify({
                "success": False,
                "error": "Internal server error",
            }), 500
    return wrapped
```

**Apply to simulation.py:** Replace every `try/except` block that returns `"traceback": traceback.format_exc()` with the decorator pattern. For example:

```python
# BEFORE:
@simulation_bp.route('/entities/<graph_id>', methods=['GET'])
def get_graph_entities(graph_id: str):
    try:
        ...
    except Exception as e:
        logger.error(f"Failed to get knowledge graph entities: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

# AFTER:
@simulation_bp.route('/entities/<graph_id>', methods=['GET'])
@legacy_api_route
def get_graph_entities(graph_id: str):
    ...  # No try/except needed; decorator handles errors
```

**Same pattern applied to:**
- `graph.py`: `generate_ontology`, `build_graph`, `get_graph_data`, `delete_graph`
- `report.py`: `generate_report`, `get_report`, `get_report_by_simulation`, `list_reports`, `download_report`, `delete_report`, `chat_with_report_agent`, `get_report_progress`, `get_report_sections`, `get_single_section`, `check_report_status`, `get_agent_log`, `stream_agent_log`, `get_console_log`, `stream_console_log`, `search_graph_tool`, `get_graph_statistics_tool`
- `simulation.py`: All 15+ endpoints (get_graph_entities, get_entity_detail, get_entities_by_type, create_simulation, prepare_simulation, get_prepare_status, get_simulation, list_simulations, get_simulation_history, get_simulation_profiles, get_simulation_profiles_realtime, get_simulation_config_realtime, get_simulation_config, download_simulation_config, download_simulation_script, generate_profiles, start_simulation, stop_simulation, get_run_status, get_run_status_detail, get_simulation_actions, get_simulation_timeline, get_agent_stats, get_simulation_posts, get_simulation_comments, interview_agent, interview_agents_batch, interview_all_agents, get_interview_history, get_env_status, close_simulation_env)

---

### 1.3 Restrict CORS Wildcard

**File:** `backend/app/config.py` — add new config:
```python
# CORS configuration
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000')
ALLOWED_ORIGINS = [o.strip() for o in CORS_ORIGINS.split(',') if o.strip()]
```

**File:** `backend/app/__init__.py` — line 43:
```python
# BEFORE:
CORS(app, resources={r"/api/*": {"origins": "*"}})

# AFTER:
CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})
```

---

### 1.4 Move Gemini API Key from URL Params to Authorization Header

**File:** `backend/app/book_sim/providers/gemini_provider.py`

Three call sites need updating:

```python
# Line 43-44 (generate_text) — BEFORE:
url = f"{self.base_url}/v1beta/models/{self.route.model}:generateContent"
params = {"key": self.api_key}

# AFTER:
url = f"{self.base_url}/v1beta/models/{self.route.model}:generateContent"
headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

# Line 57 — BEFORE:
response = requests.post(url, params=params, json=payload, timeout=self.timeout_s)

# AFTER:
response = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
```

```python
# Line 89-90 (embed_text) — BEFORE:
url = f"{self.base_url}/v1beta/models/text-embedding-004:embedContent"
params = {"key": self.api_key}

# AFTER:
url = f"{self.base_url}/v1beta/models/text-embedding-004:embedContent"
headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

# Line 96 — BEFORE:
response = requests.post(url, params=params, json=payload, timeout=self.timeout_s)

# AFTER:
response = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
```

```python
# Line 122-124 (health_check) — BEFORE:
response = requests.get(
    f"{self.base_url}/v1beta/models/{self.route.model}",
    params={"key": self.api_key},
    timeout=self.timeout_s,
)

# AFTER:
response = requests.get(
    f"{self.base_url}/v1beta/models/{self.route.model}",
    headers={"Authorization": f"Bearer {self.api_key}"},
    timeout=self.timeout_s,
)
```

---

### 1.5 Add Cypher Label Sanitization

**File:** `backend/app/storage/neo4j_storage.py`

Add import at top:
```python
import re
```

**Line 440-451 — BEFORE:**
```python
def get_nodes_by_label(self, graph_id: str, label: str) -> List[Dict[str, Any]]:
    def _read(tx):
        # Dynamic label in query (safe — label comes from ontology, not user input)
        query = f"""
            MATCH (n:Entity:`{label}` {{graph_id: $gid}})
            RETURN n, labels(n) AS labels
        """
        result = tx.run(query, gid=graph_id)
        return [self._node_to_dict(record["n"], record["labels"]) for record in result]

    with self._driver.session() as session:
        return self._call_with_retry(session.execute_read, _read)
```

**AFTER:**
```python
def get_nodes_by_label(self, graph_id: str, label: str) -> List[Dict[str, Any]]:
    # Sanitize label to prevent Cypher injection
    safe_label = re.sub(r'[^a-zA-Z0-9_]', '', label)
    if not safe_label:
        logger.warning("Invalid label '%s' sanitized to empty; returning empty result", label)
        return []
    if safe_label != label:
        logger.warning("Label '%s' sanitized to '%s' for Cypher safety", label, safe_label)

    def _read(tx):
        query = f"""
            MATCH (n:Entity:`{safe_label}` {{graph_id: $gid}})
            RETURN n, labels(n) AS labels
        """
        result = tx.run(query, gid=graph_id)
        return [self._node_to_dict(record["n"], record["labels"]) for record in result]

    with self._driver.session() as session:
        return self._call_with_retry(session.execute_read, _read)
```

Also sanitize label at line 284-292 in `add_text`:
```python
# BEFORE (line 285-289):
def _add_label(tx, _name_lower=ename.lower()):
    tx.run(
        f"MATCH (n:Entity {{graph_id: $gid, name_lower: $nl}}) SET n:`{etype}`",
        gid=graph_id,
        nl=_name_lower,
    )

# AFTER:
safe_etype = re.sub(r'[^a-zA-Z0-9_]', '', etype)
if not safe_etype:
    logger.warning("Skipping invalid entity type label: '%s'", etype)
    return
def _add_label(tx, _name_lower=ename.lower()):
    tx.run(
        f"MATCH (n:Entity {{graph_id: $gid, name_lower: $nl}}) SET n:`{safe_etype}`",
        gid=graph_id,
        nl=_name_lower,
    )
```

---

## Phase 2: Bug Fixes (P1)

### 2.1 Register Neo4j Driver Teardown Handler

**File:** `backend/app/__init__.py`

Add after line 59 (after `SimulationRunner.register_cleanup()`):
```python
# Register Neo4j driver cleanup on app shutdown
@app.teardown_appcontext
def close_neo4j_driver(exception=None):
    """Close Neo4j driver connection when app context tears down."""
    neo4j_storage = app.extensions.get('neo4j_storage')
    if neo4j_storage is not None:
        try:
            neo4j_storage.close()
        except Exception:
            pass  # Driver may already be closed
```

---

### 2.2 Fix Naive Timestamps to Use UTC

**File:** `backend/app/book_sim/models.py`

```python
# Line 1-13 — add timezone import:
from datetime import datetime, timezone

# Line 20-21 — BEFORE:
def _now_iso() -> str:
    return datetime.now().isoformat()

# AFTER:
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
```

**File:** `backend/app/api/book_sim.py`

```python
# Line 5 — update import:
from datetime import datetime, timezone

# Line 429 — BEFORE:
digest = stable_digest(name, title or "", draft_id or "", version or "", datetime.now().isoformat())

# AFTER:
digest = stable_digest(name, title or "", draft_id or "", version or "", datetime.now(timezone.utc).isoformat())

# Line 552 — BEFORE:
"updated_at": datetime.now().isoformat(),

# AFTER:
"updated_at": datetime.now(timezone.utc).isoformat(),
```

**File:** `backend/app/book_sim/simulation/simulation_orchestrator.py`

```python
# Line 7 — update import:
from datetime import datetime, timezone

# Line 59 — BEFORE:
started_at = datetime.now().isoformat()

# AFTER:
started_at = datetime.now(timezone.utc).isoformat()

# Line 106 — BEFORE:
ended_at=datetime.now().isoformat(),

# AFTER:
ended_at=datetime.now(timezone.utc).isoformat(),
```

---

### 2.3 Fix Simulation Cache Key Bloat

**File:** `backend/app/book_sim/simulation/simulation_orchestrator.py`

```python
# Lines 152-168 — BEFORE:
def _cache_key(
    self,
    project: BookProject,
    evidence_pack: EvidencePack,
    simulation_seed: Optional[int],
    persona_overrides: Optional[PersonaGenerationOverrides],
) -> str:
    payload = {
        "project": project.to_dict(),
        "evidence_pack": evidence_pack.to_dict(),
        "simulation_seed": simulation_seed,
        "persona_overrides": persona_overrides.__dict__ if persona_overrides else {},
        "cross_reaction_posts": self.cross_reaction_posts,
        "max_reaction_rounds": self.max_reaction_rounds,
        "max_parallel_jobs": self.max_parallel_jobs,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

# AFTER:
def _cache_key(
    self,
    project: BookProject,
    evidence_pack: EvidencePack,
    simulation_seed: Optional[int],
    persona_overrides: Optional[PersonaGenerationOverrides],
) -> str:
    # Use stable identifiers instead of full dict serialization
    # to avoid cache invalidation from irrelevant metadata changes
    payload = {
        "project_id": project.project_id,
        "pack_id": evidence_pack.pack_id,
        "pack_version": evidence_pack.version,
        "simulation_seed": simulation_seed,
        "persona_overrides": persona_overrides.__dict__ if persona_overrides else {},
        "cross_reaction_posts": self.cross_reaction_posts,
        "max_reaction_rounds": self.max_reaction_rounds,
        "max_parallel_jobs": self.max_parallel_jobs,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
```

---

### 2.4 Fix Python Version Constraint

**File:** `backend/pyproject.toml`

```toml
# Line 5 — BEFORE:
requires-python = ">=3.11"

# AFTER:
requires-python = ">=3.11,<3.12"
```

---

## Phase 3: Architecture Improvements (P2)

### 3.1 System-Wide PrivacyGuard Middleware

**New file:** `backend/app/book_sim/privacy_guard.py`
```python
"""System-wide privacy enforcement for Swarmbook.

Ensures that local_only mode never calls external providers,
regardless of which code path is used.
"""

from __future__ import annotations

from typing import Optional


class PrivacyViolationError(Exception):
    """Raised when a cloud provider is requested in local_only mode."""


class PrivacyGuard:
    """Global privacy mode enforcer.
    
    All provider calls should pass through this guard to ensure
    local_only mode is never bypassed.
    """
    
    _instance: Optional["PrivacyGuard"] = None
    _privacy_mode: str = "hybrid_safe"
    
    LOCAL_PROVIDERS = {"ollama"}
    CLOUD_PROVIDERS = {"gemini", "nvidia"}
    
    @classmethod
    def get_instance(cls) -> "PrivacyGuard":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_mode(self, mode: str) -> None:
        """Set the global privacy mode."""
        if mode not in ("local_only", "hybrid_safe", "cloud_quality"):
            raise ValueError(f"Invalid privacy mode: {mode}")
        self._privacy_mode = mode
    
    @property
    def mode(self) -> str:
        return self._privacy_mode
    
    def is_local_only(self) -> bool:
        return self._privacy_mode == "local_only"
    
    def assert_local_provider(self, provider_name: str) -> None:
        """Raise PrivacyViolationError if a cloud provider is used in local_only mode."""
        if self._privacy_mode == "local_only" and provider_name.lower() not in self.LOCAL_PROVIDERS:
            raise PrivacyViolationError(
                f"Provider '{provider_name}' is not allowed in local_only mode. "
                f"Only {sorted(self.LOCAL_PROVIDERS)} providers are permitted."
            )
    
    def can_use_provider(self, provider_name: str) -> bool:
        """Check if a provider is allowed under current privacy mode."""
        if self._privacy_mode == "local_only":
            return provider_name.lower() in self.LOCAL_PROVIDERS
        return True
```

**Integrate into provider_router.py** — update `select_route`:
```python
# Add import at top:
from .privacy_guard import PrivacyGuard, PrivacyViolationError

# In select_route method, after line 71, add:
# Enforce privacy guard system-wide
guard = PrivacyGuard.get_instance()
if privacy_mode == "local_only":
    guard.set_mode("local_only")
```

**Integrate into each provider's `__init__`**:
```python
# In OllamaProvider, GeminiProvider, NvidiaProvider __init__:
from ..privacy_guard import PrivacyGuard

# At end of __init__:
guard = PrivacyGuard.get_instance()
guard.assert_local_provider(self.route.provider)
```

---

### 3.2 Transactional Runtime Store

**File:** `backend/app/book_sim/local_cache.py` — add atomic write:

```python
import os
import tempfile
import json
from pathlib import Path
from typing import Any, Dict, Optional
from contextlib import contextmanager
import threading

class LocalArtifactCache:
    """Store cached Swarmbook artifacts by namespace and content hash."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        default_root = Path(__file__).resolve().parents[1] / "uploads" / "book_sim_cache"
        cache_root = Path(base_dir) if base_dir else default_root
        self.base_dir = Path(cache_root)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def _get_lock(self, namespace: str, cache_key: str) -> threading.Lock:
        lock_key = f"{namespace}:{cache_key}"
        with self._global_lock:
            if lock_key not in self._locks:
                self._locks[lock_key] = threading.Lock()
            return self._locks[lock_key]

    def _path_for(self, namespace: str, cache_key: str) -> Path:
        namespace_dir = self.base_dir / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        return namespace_dir / f"{cache_key}.json"

    def get_json(self, namespace: str, cache_key: str) -> Optional[Dict[str, Any]]:
        path = self._path_for(namespace, cache_key)
        lock = self._get_lock(namespace, cache_key)
        with lock:
            if not path.exists():
                return None
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)

    def set_json(self, namespace: str, cache_key: str, payload: Dict[str, Any]) -> None:
        path = self._path_for(namespace, cache_key)
        lock = self._get_lock(namespace, cache_key)
        with lock:
            # Atomic write: write to temp file, then rename
            dir_path = path.parent
            fd, tmp_path = tempfile.mkstemp(dir=str(dir_path), suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, ensure_ascii=False, indent=2)
                os.replace(tmp_path, str(path))
            except Exception:
                # Clean up temp file on failure
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
```

**Add TransactionContext to runtime_store.py:**
```python
from contextlib import contextmanager

class BookSimRuntimeStore:
    # ... existing code ...
    
    @contextmanager
    def transaction(self, project_id: str):
        """Context manager for atomic multi-step operations.
        
        Usage:
            with store.transaction(project_id) as txn:
                txn.save_project(project)
                txn.save_evidence_pack(pack)
        """
        state = self._load_state(project_id)
        snapshot = state.to_dict()  # Save rollback point
        try:
            yield self
        except Exception:
            # Rollback to snapshot
            self._save_state(ProjectArtifactState.from_dict(snapshot))
            raise
```

---

### 3.3 Split Monolithic simulation.py

**New directory structure:**
```
backend/app/api/simulation/
    __init__.py
    _shared.py
    entities.py
    preparation.py
    execution.py
    monitoring.py
    interview.py
    downloads.py
```

**`backend/app/api/simulation/__init__.py`:**
```python
"""Refactored simulation API blueprint."""
from flask import Blueprint

simulation_bp = Blueprint('simulation', __name__)

from . import entities, preparation, execution, monitoring, interview, downloads
```

**`backend/app/api/simulation/_shared.py`:**
```python
"""Shared helpers for simulation API endpoints."""
import os
import json
from datetime import datetime, timezone
from flask import current_app
from ..config import Config
from ..utils.logger import get_logger
from ..services.simulation_manager import SimulationManager, SimulationStatus
from ..services.simulation_runner import SimulationRunner

logger = get_logger('mirofish.api.simulation.shared')

INTERVIEW_PROMPT_PREFIX = "Based on your persona, all your past memories and actions, reply directly with text without calling any tools:"


def optimize_interview_prompt(prompt: str) -> str:
    """Add prefix to prevent agents from calling tools during interviews."""
    if not prompt:
        return prompt
    if prompt.startswith(INTERVIEW_PROMPT_PREFIX):
        return prompt
    return f"{INTERVIEW_PROMPT_PREFIX}{prompt}"


def check_simulation_prepared(simulation_id: str) -> tuple:
    """Check if simulation preparation is complete."""
    simulation_dir = os.path.join(Config.OASIS_SIMULATION_DATA_DIR, simulation_id)
    
    if not os.path.exists(simulation_dir):
        return False, {"reason": "Simulation directory does not exist"}
    
    required_files = [
        "state.json", "simulation_config.json",
        "reddit_profiles.json", "twitter_profiles.csv"
    ]
    
    existing_files = []
    missing_files = []
    for f in required_files:
        if os.path.exists(os.path.join(simulation_dir, f)):
            existing_files.append(f)
        else:
            missing_files.append(f)
    
    if missing_files:
        return False, {
            "reason": "Missing required files",
            "missing_files": missing_files,
            "existing_files": existing_files
        }
    
    state_file = os.path.join(simulation_dir, "state.json")
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        status = state_data.get("status", "")
        config_generated = state_data.get("config_generated", False)
        
        prepared_statuses = ["ready", "preparing", "running", "completed", "stopped", "failed"]
        if status in prepared_statuses and config_generated:
            if status == "preparing":
                try:
                    state_data["status"] = "ready"
                    state_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                    with open(state_file, 'w', encoding='utf-8') as f:
                        json.dump(state_data, f, ensure_ascii=False, indent=2)
                    logger.info("Auto-updated simulation %s: preparing -> ready", simulation_id)
                    status = "ready"
                except Exception as e:
                    logger.warning("Failed to auto-update status: %s", e)
            
            profiles_file = os.path.join(simulation_dir, "reddit_profiles.json")
            profiles_count = 0
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    profiles_data = json.load(f)
                    profiles_count = len(profiles_data) if isinstance(profiles_data, list) else 0
            
            return True, {
                "status": status,
                "entities_count": state_data.get("entities_count", 0),
                "profiles_count": profiles_count,
                "entity_types": state_data.get("entity_types", []),
                "config_generated": config_generated,
                "created_at": state_data.get("created_at"),
                "updated_at": state_data.get("updated_at"),
                "existing_files": existing_files
            }
        else:
            return False, {
                "reason": f"Status not prepared: status={status}, config_generated={config_generated}",
                "status": status,
                "config_generated": config_generated
            }
    except Exception as e:
        return False, {"reason": f"Failed to read state file: {str(e)}"}


def get_storage():
    """Get Neo4jStorage from Flask app extensions."""
    storage = current_app.extensions.get('neo4j_storage')
    if not storage:
        raise ValueError("GraphStorage not initialized — check Neo4j connection")
    return storage


def get_report_id_for_simulation(simulation_id: str) -> str:
    """Find the latest report_id for a given simulation_id."""
    reports_dir = os.path.join(os.path.dirname(__file__), '../../../uploads/reports')
    if not os.path.exists(reports_dir):
        return None
    
    matching_reports = []
    try:
        for report_folder in os.listdir(reports_dir):
            report_path = os.path.join(reports_dir, report_folder)
            if not os.path.isdir(report_path):
                continue
            meta_file = os.path.join(report_path, "meta.json")
            if not os.path.exists(meta_file):
                continue
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                if meta.get("simulation_id") == simulation_id:
                    matching_reports.append({
                        "report_id": meta.get("report_id"),
                        "created_at": meta.get("created_at", ""),
                        "status": meta.get("status", ""),
                    })
            except Exception:
                continue
        
        if not matching_reports:
            return None
        matching_reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return matching_reports[0].get("report_id")
    except Exception as e:
        logger.warning("Failed to find report for simulation %s: %s", simulation_id, e)
        return None
```

**Each module file** (entities.py, preparation.py, etc.) contains the extracted route handlers from the original simulation.py, using `from ._shared import ...` for shared helpers.

**Update `backend/app/__init__.py`** line 80:
```python
# BEFORE:
from .api import book_sim_bp, graph_bp, simulation_bp, report_bp
app.register_blueprint(simulation_bp, url_prefix='/api/simulation')

# AFTER:
from .api import book_sim_bp, graph_bp, report_bp
from .api.simulation import simulation_bp
app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
```

---

### 3.4 Shared Legacy Error Handler

Already created as part of 1.2 — `backend/app/api/_legacy_error_handler.py`.

---

## Phase 4: Code Quality Enhancements (P3)

### 4.1 Deduplicate ReaderPersona Redundant Fields

**File:** `backend/app/book_sim/models.py`

```python
@dataclass
class ReaderPersona(JsonDataclassMixin):
    """Expanded reader persona used during simulation."""

    persona_id: str
    archetype_id: str
    display_name: str
    platform_home: str
    review_style: str
    favorite_genres: List[str] = field(default_factory=list)
    disliked_patterns: List[str] = field(default_factory=list)
    dnf_threshold: float = 0.6
    controversy_sensitivity: float = 0.5
    rating_bias: float = 0.0
    influence_weight: float = 0.5
    susceptibility_to_peer_reaction: float = 0.5
    quote_sharing_probability: float = 0.5
    evidence_focus: float = 0.5
    privacy_constraints: List[str] = field(default_factory=list)
    book_type_suitability: List[str] = field(default_factory=lambda: ["fiction", "nonfiction"])
    reading_preferences: List[str] = field(default_factory=list)
    dnf_triggers: List[str] = field(default_factory=list)
    delight_triggers: List[str] = field(default_factory=list)
    private_bias: Optional[str] = None
    influence_score: float = 0.0
    spoiler_tolerance: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.favorite_genres and self.reading_preferences:
            self.favorite_genres = list(self.reading_preferences)
        if not self.reading_preferences and self.favorite_genres:
            self.reading_preferences = list(self.favorite_genres)
        if not self.disliked_patterns and self.dnf_triggers:
            self.disliked_patterns = list(self.dnf_triggers)
        if self.influence_score == 0.0 and self.influence_weight:
            self.influence_score = self.influence_weight

    # Backward-compatibility property accessors
    @property
    def id(self) -> str:
        return self.persona_id

    @property
    def name(self) -> str:
        return self.display_name

    @property
    def cohort(self) -> str:
        return self.platform_home

    @property
    def platform(self) -> str:
        return self.platform_home
```

---

### 4.2 Standardize Mutable Default Factories

**File:** `backend/app/book_sim/models.py`

```python
# Define module-level constant
_DEFAULT_BOOK_TYPES = ["fiction", "nonfiction"]

# In ReaderArchetype (line 369):
book_type_suitability: List[str] = field(default_factory=lambda: list(_DEFAULT_BOOK_TYPES))

# In ReaderPersona (line 411):
book_type_suitability: List[str] = field(default_factory=lambda: list(_DEFAULT_BOOK_TYPES))
```

---

### 4.3 Add Input Validation Layer

**New file:** `backend/app/book_sim/validators.py`
```python
"""Input validation for Swarmbook API endpoints."""

from __future__ import annotations

import re
from typing import Optional

ALLOWED_PRIVACY_MODES = {"local_only", "hybrid_safe", "cloud_quality"}


def validate_privacy_mode(value: Optional[str], default: str = "hybrid_safe") -> str:
    mode = (value or default).strip() or default
    if mode not in ALLOWED_PRIVACY_MODES:
        raise ValueError(
            f"Unsupported privacy_mode: {mode}. "
            f"Allowed: {sorted(ALLOWED_PRIVACY_MODES)}"
        )
    return mode


def validate_positive_int(value, field_name: str, minimum: int = 1) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer")
    if n < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}")
    return n


def validate_non_empty_string(value, field_name: str) -> str:
    if value is None:
        raise ValueError(f"{field_name} is required")
    s = str(value).strip()
    if not s:
        raise ValueError(f"{field_name} must not be empty")
    return s


def validate_max_length(value: str, field_name: str, max_length: int) -> str:
    if len(value) > max_length:
        raise ValueError(
            f"{field_name} exceeds maximum length of {max_length} "
            f"(got {len(value)})"
        )
    return value
```

---

### 4.4 Improve Provider Base with Retry and Logging

**File:** `backend/app/book_sim/providers/base.py`

```python
"""Base provider contract for Swarmbook model routing."""

from __future__ import annotations

import json
import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional

from ..config_loader import ModelRouteEntry

logger = logging.getLogger('mirofish.book_sim.provider')


class ProviderError(Exception):
    """Base exception for provider failures."""


class ProviderRetryError(ProviderError):
    """Raised when all retry attempts are exhausted."""


class BaseProvider(ABC):
    """Typed interface for provider implementations."""

    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 1.0  # seconds

    def __init__(self, route: ModelRouteEntry, env: Mapping[str, str]) -> None:
        self.route = route
        self.env = env

    @staticmethod
    def _parse_json_text(raw_text: str) -> Dict[str, Any]:
        """Extract and parse JSON from raw model text."""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()
        if not cleaned:
            raise ValueError("Provider returned empty JSON payload")
        return json.loads(cleaned)

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute a function with exponential backoff retry."""
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (ConnectionError, TimeoutError, OSError) as e:
                last_error = e
                wait = self.RETRY_DELAY_BASE * (2 ** attempt)
                logger.warning(
                    "Provider %s transient error (attempt %d/%d), retrying in %.1fs: %s",
                    self.route.provider, attempt + 1, self.MAX_RETRIES, wait, e,
                )
                time.sleep(wait)
            except Exception:
                raise
        raise ProviderRetryError(
            f"Provider {self.route.provider} failed after {self.MAX_RETRIES} attempts"
        ) from last_error

    @abstractmethod
    def is_available(self) -> bool:
        """Return True when provider is configured enough to receive calls."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Generate natural language text."""

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate structured JSON response."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector."""

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return provider health status without raising on missing keys."""
```

---

## Phase 5: Documentation & Comments (P4)

### 5.1 Add Educational Comments

Target files in priority order (add section-header comments explaining purpose, architecture role, and key design decisions):

1. `backend/app/book_sim/provider_router.py` — Explain routing logic, privacy mode enforcement, and provider selection cascade
2. `backend/app/book_sim/simulation/simulation_orchestrator.py` — Document the 3-pass pipeline (private reading, platform posts, cross-reactions)
3. `backend/app/book_sim/scoring/` — Explain each scoring algorithm's purpose and weight rationale
4. `backend/app/storage/neo4j_storage.py` — Document Cypher patterns, retry logic, and batch embedding strategy
5. `backend/app/book_sim/evidence_pack_builder.py` — Document evidence pack structure and why each component exists
6. `backend/app/book_sim/report_builder.py` — Explain report synthesis logic and score aggregation

### 5.2 Standardize Comments to English

Convert all Chinese comments in:
- `backend/app/api/simulation.py` (or its split modules)
- `backend/app/api/graph.py`
- `backend/app/config.py` (section headers)
- `backend/pyproject.toml` (dependency section headers)

Keep bilingual only for encoding-specific comments (e.g., explaining why `JSON_AS_ASCII = False`).

### 5.3 Create Architecture Documentation

**New file:** `docs/ARCHITECTURE.md`

Contents:
- Component diagram (legacy vs Swarmbook)
- Data flow: manuscript -> evidence pack -> personas -> reactions -> scores -> report
- Provider routing decision tree
- Privacy mode matrix
- File structure overview
- Key design decisions and trade-offs

---

## Phase 6: Testing & Infrastructure (P5)

### 6.1 Add Legacy Health Endpoint

**New endpoint in `backend/app/__init__.py`:**
```python
@app.route('/api/health')
def legacy_health():
    """Health check for the legacy MiroFish system."""
    import platform
    import shutil
    
    neo4j_ok = False
    neo4j_error = None
    neo4j_storage = app.extensions.get('neo4j_storage')
    if neo4j_storage:
        try:
            driver = getattr(neo4j_storage, '_driver', None)
            if driver:
                driver.verify_connectivity()
                neo4j_ok = True
        except Exception as e:
            neo4j_error = str(e)
    
    # Check disk space
    backend_dir = os.path.dirname(__file__)
    try:
        disk = shutil.disk_usage(backend_dir)
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 1),
            "free_gb": round(disk.free / (1024**3), 1),
            "used_percent": round(disk.used / disk.total * 100, 1),
        }
    except Exception:
        disk_info = {"error": "Unable to determine disk usage"}
    
    return jsonify({
        "status": "ok" if neo4j_ok else "degraded",
        "service": "MiroFish-Offline Backend",
        "python_version": platform.python_version(),
        "neo4j": {"ok": neo4j_ok, "error": neo4j_error},
        "disk": disk_info,
    })
```

### 6.2 Docker GPU Fallback Profile

**File:** `docker-compose.yml`

```yaml
# Add profiles for GPU vs CPU-only operation
services:
  ollama:
    # ... existing config ...
    profiles: ["gpu"]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  ollama-cpu:
    image: ollama/ollama:latest
    container_name: mirofish-ollama-cpu
    profiles: ["cpu"]
    ports:
      - "11434:11434"
    volumes:
      - ollama_data_cpu:/root/.ollama
    # Note: CPU mode is significantly slower

volumes:
  ollama_data:
  ollama_data_cpu:
```

Usage:
- GPU: `docker compose --profile gpu up -d`
- CPU: `docker compose --profile cpu up -d`

---

## Execution Checklist

- [ ] 1.1 Fix SECRET_KEY
- [ ] 1.2 Remove traceback exposure (all 3 API files)
- [ ] 1.3 Restrict CORS
- [ ] 1.4 Gemini API key to header
- [ ] 1.5 Cypher label sanitization
- [ ] 2.1 Neo4j teardown handler
- [ ] 2.2 UTC timestamps
- [ ] 2.3 Cache key fix
- [ ] 2.4 Python version constraint
- [ ] 3.1 PrivacyGuard middleware
- [ ] 3.2 Transactional store
- [ ] 3.3 Split simulation.py
- [ ] 3.4 Legacy error handler (done with 1.2)
- [ ] 4.1 Deduplicate persona fields
- [ ] 4.2 Mutable defaults
- [ ] 4.3 Input validators
- [ ] 4.4 Provider base improvements
- [ ] 5.1 Educational comments
- [ ] 5.2 English standardization
- [ ] 5.3 Architecture doc
- [ ] 6.1 Legacy health endpoint
- [ ] 6.2 Docker GPU fallback
