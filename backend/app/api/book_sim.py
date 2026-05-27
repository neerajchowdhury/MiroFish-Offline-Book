"""Additive Swarmbook API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

from flask import current_app, jsonify, request

from . import book_sim_bp
from ..book_sim.comparison import DraftComparator
from ..book_sim.evidence_pack_builder import EvidencePackBuilder
from ..book_sim.graph_persistence import BookGraphPersistence
from ..book_sim.interrogation import PersonaInterrogator
from ..book_sim.local_cache import LocalArtifactCache
from ..book_sim.local_profiles import LocalProfile, LocalProfileLoader
from ..book_sim.models import (
    BookProject,
    EvidencePack,
    ManuscriptInput,
    SimulationRun,
)
from ..book_sim.provider_router import BookSimProviderRouter, RouteSelection
from ..book_sim.reader_persona_generator import PersonaGenerationOverrides
from ..book_sim.report_builder import build_prediction_report
from ..book_sim.report_markdown import render_prediction_report_markdown
from ..book_sim.runtime_store import BookSimRuntimeStore
from ..book_sim.scoring._shared import stable_digest
from ..book_sim.simulation import SimulationOrchestrator
from ..utils.logger import get_logger


logger = get_logger("mirofish.api.book_sim")
ALLOWED_PRIVACY_MODES = {"local_only", "hybrid_safe", "cloud_quality"}
MAX_MANUSCRIPT_CHARS_DEFAULT = 500_000
F = TypeVar("F", bound=Callable[..., Any])


class ApiError(Exception):
    """Structured API error with status code and optional details."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "validation_error",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


def _api_route(handler: F) -> F:
    """Wrap a route with structured JSON error handling."""

    @wraps(handler)
    def wrapped(*args: Any, **kwargs: Any):
        try:
            return handler(*args, **kwargs)
        except ApiError as exc:
            return _error_response(
                exc.message,
                status_code=exc.status_code,
                error_code=exc.error_code,
                details=exc.details,
            )
        except ValueError as exc:
            return _error_response(str(exc), status_code=400, error_code="validation_error")
        except RuntimeError as exc:
            # Providers raise RuntimeError for missing keys, missing deps, or unavailable runtimes.
            return _error_response(str(exc), status_code=503, error_code="runtime_unavailable")
        except Exception as exc:  # pragma: no cover - defensive API guard
            logger.error("Book-sim endpoint failed: %s", exc, exc_info=True)
            return _error_response(str(exc), status_code=500, error_code="internal_error")

    return wrapped  # type: ignore[return-value]


def _success_response(data: Dict[str, Any], status_code: int = 200):
    return jsonify({"success": True, "data": data}), status_code


def _error_response(
    message: str,
    status_code: int = 400,
    error_code: str = "validation_error",
    details: Optional[Dict[str, Any]] = None,
):
    payload: Dict[str, Any] = {
        "success": False,
        "error": message,
        "error_code": error_code,
    }
    if details:
        payload["details"] = details
    return jsonify(payload), status_code


def _request_payload() -> Dict[str, Any]:
    payload = request.get_json(silent=True)
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ApiError("JSON body must be an object", details={"body_type": type(payload).__name__})
    return payload


def _cache() -> LocalArtifactCache:
    return LocalArtifactCache(base_dir=current_app.config.get("BOOK_SIM_CACHE_DIR"))


def _store() -> BookSimRuntimeStore:
    return BookSimRuntimeStore(cache=_cache())


def _graph_persistence() -> BookGraphPersistence:
    storage = None
    if hasattr(current_app, "extensions"):
        storage = current_app.extensions.get("neo4j_storage")
    return BookGraphPersistence(storage=storage)


def _maybe_router() -> Tuple[Optional[BookSimProviderRouter], Optional[str]]:
    try:
        return BookSimProviderRouter(), None
    except Exception as exc:
        return None, str(exc)


def _profile_loader() -> LocalProfileLoader:
    return LocalProfileLoader()


def _profile_name_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    return _optional_text(payload, "profile_name") or _optional_text(payload, "local_profile")


def _resolve_profile(
    payload: Dict[str, Any],
    project: Optional[BookProject] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[LocalProfileLoader, LocalProfile]:
    loader = _profile_loader()
    profile_name = _profile_name_from_payload(payload)
    if not profile_name and metadata:
        profile_name = str(metadata.get("local_profile", "")).strip() or None
    if not profile_name and project and isinstance(project.metadata, dict):
        profile_name = str(project.metadata.get("local_profile", "")).strip() or None
    if not profile_name:
        profile_name = loader.get_default_profile().profile_name
    profile = loader.get_profile(profile_name)
    if profile is None:
        raise ApiError(
            f"Unknown local profile: {profile_name}",
            details={
                "profile_name": profile_name,
                "available_profiles": sorted(loader.load().profiles.keys()),
            },
        )
    return loader, profile


def _profile_response_payload(
    loader: LocalProfileLoader,
    profile: LocalProfile,
) -> Dict[str, Any]:
    catalog = loader.load()
    return {
        "selected_profile": profile.profile_name,
        "default_profile": catalog.default_profile,
        "hardware_target": catalog.hardware_target.to_dict(),
        "warnings": loader.get_profile_warnings(profile.profile_name),
        "load_error": catalog.load_error,
    }


def _validate_privacy_mode(raw_value: Optional[str], default: str = "hybrid_safe") -> str:
    privacy_mode = (raw_value or default).strip() or default
    if privacy_mode not in ALLOWED_PRIVACY_MODES:
        raise ApiError(
            f"Unsupported privacy_mode: {privacy_mode}",
            details={"allowed": sorted(ALLOWED_PRIVACY_MODES)},
        )
    return privacy_mode


def _require_text(payload: Dict[str, Any], field_name: str) -> str:
    value = str(payload.get(field_name, "")).strip()
    if not value:
        raise ApiError(
            f"Please provide {field_name}",
            details={"field": field_name},
        )
    return value


def _optional_text(payload: Dict[str, Any], field_name: str) -> Optional[str]:
    raw = payload.get(field_name)
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def _optional_dict(payload: Dict[str, Any], field_name: str) -> Optional[Dict[str, Any]]:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ApiError(
            f"{field_name} must be a JSON object",
            details={"field": field_name},
        )
    return value


def _optional_list(payload: Dict[str, Any], field_name: str) -> list[Any]:
    value = payload.get(field_name)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ApiError(f"{field_name} must be a list", details={"field": field_name})
    return value


def _optional_int(payload: Dict[str, Any], field_name: str) -> Optional[int]:
    value = payload.get(field_name)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(f"{field_name} must be an integer", details={"field": field_name}) from exc


def _optional_positive_int(
    payload: Dict[str, Any],
    field_name: str,
    minimum: int = 1,
) -> Optional[int]:
    value = _optional_int(payload, field_name)
    if value is None:
        return None
    if value < minimum:
        raise ApiError(
            f"{field_name} must be >= {minimum}",
            details={"field": field_name, "minimum": minimum},
        )
    return value


def _optional_float(payload: Dict[str, Any], field_name: str) -> Optional[float]:
    value = payload.get(field_name)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(f"{field_name} must be a number", details={"field": field_name}) from exc


def _optional_bool(payload: Dict[str, Any], field_name: str, default: bool = False) -> bool:
    value = payload.get(field_name)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    raise ApiError(f"{field_name} must be a boolean", details={"field": field_name})


def _load_project(store: BookSimRuntimeStore, project_id: str) -> BookProject:
    project = store.get_project(project_id)
    if project is None:
        raise ApiError(f"Project does not exist: {project_id}", status_code=404, error_code="not_found")
    return project


def _resolve_evidence_pack(payload: Dict[str, Any], store: BookSimRuntimeStore) -> EvidencePack:
    evidence_payload = _optional_dict(payload, "evidence_pack")
    if evidence_payload is not None:
        return EvidencePack.from_dict(evidence_payload)

    evidence_pack_id = _optional_text(payload, "evidence_pack_id")
    if evidence_pack_id:
        evidence_pack = store.get_evidence_pack(evidence_pack_id)
        if evidence_pack is None:
            raise ApiError(f"Evidence pack does not exist: {evidence_pack_id}", status_code=404, error_code="not_found")
        return evidence_pack

    project_id = _optional_text(payload, "project_id")
    if project_id:
        evidence_pack = store.get_latest_evidence_pack(project_id)
        if evidence_pack is None:
            raise ApiError(
                f"No evidence pack is available for project: {project_id}",
                status_code=404,
                error_code="not_found",
            )
        return evidence_pack

    raise ApiError(
        "Please provide evidence_pack, evidence_pack_id, or project_id",
        details={"required_any_of": ["evidence_pack", "evidence_pack_id", "project_id"]},
    )


def _resolve_simulation_run(payload: Dict[str, Any], store: BookSimRuntimeStore) -> SimulationRun:
    simulation_payload = _optional_dict(payload, "simulation_run")
    if simulation_payload is not None:
        return SimulationRun.from_dict(simulation_payload)

    simulation_id = _optional_text(payload, "simulation_id")
    if simulation_id:
        simulation_run = store.get_simulation_run(simulation_id)
        if simulation_run is None:
            raise ApiError(f"Simulation does not exist: {simulation_id}", status_code=404, error_code="not_found")
        return simulation_run

    project_id = _optional_text(payload, "project_id")
    if project_id:
        simulation_run = store.get_latest_simulation_run(project_id)
        if simulation_run is None:
            raise ApiError(
                f"No simulation is available for project: {project_id}",
                status_code=404,
                error_code="not_found",
            )
        return simulation_run

    raise ApiError(
        "Please provide simulation_run, simulation_id, or project_id",
        details={"required_any_of": ["simulation_run", "simulation_id", "project_id"]},
    )


def _route_selection(router: Optional[BookSimProviderRouter], route_name: Optional[str], privacy_mode: str) -> RouteSelection:
    if router is None:
        return RouteSelection(
            requested_route=route_name or "local_ollama",
            selected_route="local_ollama",
            provider_name="ollama",
            privacy_mode=privacy_mode,
            reason="router unavailable; defaulting to local_ollama",
        )
    return router.select_route(route_name=route_name or "local_ollama", privacy_mode=privacy_mode)


def _persona_overrides(payload: Dict[str, Any], profile: LocalProfile) -> PersonaGenerationOverrides:
    overrides = _optional_dict(payload, "persona_overrides") or {}
    persona_count = (
        _optional_positive_int(payload, "persona_count")
        or _optional_positive_int(overrides, "persona_count")
        or _optional_positive_int(overrides, "cohort_size")
        or profile.max_personas
    )
    allowed_platforms = [str(item).strip().lower() for item in _optional_list(overrides, "force_platforms") if str(item).strip()]
    if not allowed_platforms:
        allowed_platforms = [str(item).strip().lower() for item in _optional_list(payload, "platforms") if str(item).strip()]
    if not allowed_platforms:
        allowed_platforms = [platform.lower() for platform in profile.platforms]

    include_archetypes = [str(item).strip() for item in _optional_list(overrides, "include_archetypes") if str(item).strip()]
    if not include_archetypes:
        include_archetypes = [str(item).strip() for item in _optional_list(payload, "include_archetypes") if str(item).strip()]

    exclude_archetypes = [str(item).strip() for item in _optional_list(overrides, "exclude_archetypes") if str(item).strip()]
    if not exclude_archetypes:
        exclude_archetypes = [str(item).strip() for item in _optional_list(payload, "exclude_archetypes") if str(item).strip()]

    return PersonaGenerationOverrides(
        persona_count=persona_count,
        allowed_platforms=allowed_platforms,
        include_archetypes=include_archetypes,
        exclude_archetypes=exclude_archetypes,
    )


def _comparison_project_id(
    payload: Dict[str, Any],
    base_pack: EvidencePack,
    compare_pack: EvidencePack,
) -> str:
    explicit_project_id = _optional_text(payload, "project_id")
    if explicit_project_id:
        return explicit_project_id
    if base_pack.project_id == compare_pack.project_id:
        return base_pack.project_id
    raise ApiError(
        "Please provide project_id when comparing drafts from different projects",
        details={"base_project_id": base_pack.project_id, "compare_project_id": compare_pack.project_id},
    )


def _resolve_report_payload(project: BookProject, evidence_pack: EvidencePack, simulation_run: SimulationRun) -> Dict[str, Any]:
    report = build_prediction_report(project=project, evidence_pack=evidence_pack, simulation_run=simulation_run)
    simulation_run_payload = simulation_run.to_dict()
    simulation_run_payload["report_id"] = report.report_id
    simulation_run_payload["provider_route"] = simulation_run.provider_route
    simulation_run = SimulationRun.from_dict(simulation_run_payload)
    return {"report": report, "simulation_run": simulation_run}


def _neo4j_health() -> Dict[str, Any]:
    storage = None
    if hasattr(current_app, "extensions"):
        storage = current_app.extensions.get("neo4j_storage")
    if storage is None:
        return {"ok": False, "error": "Neo4jStorage not initialized"}

    driver = getattr(storage, "_driver", None)
    if driver is None:
        return {"ok": False, "error": "Neo4j driver is not available"}

    try:
        driver.verify_connectivity()
        return {
            "ok": True,
            "uri": getattr(storage, "_uri", None),
        }
    except Exception as exc:  # pragma: no cover - depends on local Neo4j runtime
        return {
            "ok": False,
            "uri": getattr(storage, "_uri", None),
            "error": str(exc),
        }


def _project_id(name: str, title: Optional[str], draft_id: Optional[str], version: Optional[str]) -> str:
    digest = stable_digest(name, title or "", draft_id or "", version or "", datetime.now(timezone.utc).isoformat())
    return f"proj_{digest[:12]}"


def _manuscript_input(project: BookProject, payload: Dict[str, Any]) -> ManuscriptInput:
    title = _optional_text(payload, "title") or project.title or project.name
    text = _require_text(payload, "text")
    max_chars = _optional_positive_int(payload, "max_manuscript_chars", minimum=10_000) or MAX_MANUSCRIPT_CHARS_DEFAULT
    if len(text) > max_chars:
        raise ApiError(
            "Manuscript is too large for a local-first run. Provide a smaller excerpt or raise max_manuscript_chars.",
            details={
                "text_chars": len(text),
                "max_manuscript_chars": max_chars,
                "suggestion": "Try 1-3 chapters or 30-80k characters for local_tiny / hybrid_safe_default.",
            },
        )
    input_id = f"input_{stable_digest(project.project_id, title, text, project.draft_id or '', project.version or '')[:12]}"
    return ManuscriptInput(
        input_id=input_id,
        project_id=project.project_id,
        title=title,
        author_name=_optional_text(payload, "author_name") or project.author_name,
        filename=_optional_text(payload, "filename"),
        mime_type=_optional_text(payload, "mime_type") or "text/plain",
        text=text,
        language=_optional_text(payload, "language"),
        privacy_mode=project.privacy_mode,
        draft_id=project.draft_id,
        version=project.version,
        chunk_size=_optional_int(payload, "chunk_size") or 500,
        chunk_overlap=_optional_int(payload, "chunk_overlap") or 50,
        metadata=_optional_dict(payload, "metadata") or {},
    )


def _interrogate_result(persona_id: str, payload: Dict[str, Any], store: BookSimRuntimeStore) -> Dict[str, Any]:
    question = _require_text(payload, "question")
    simulation_run = _resolve_simulation_run(payload, store)
    evidence_pack = _resolve_evidence_pack(
        {**payload, "project_id": payload.get("project_id") or simulation_run.project_id},
        store,
    )
    if evidence_pack.project_id != simulation_run.project_id:
        raise ApiError(
            "evidence_pack project_id does not match simulation_run project_id",
            details={
                "evidence_pack_project_id": evidence_pack.project_id,
                "simulation_project_id": simulation_run.project_id,
            },
        )
    result = PersonaInterrogator().interrogate(
        simulation_run=simulation_run,
        evidence_pack=evidence_pack,
        persona_id=persona_id,
        question=question,
    )
    return result.to_dict()


@book_sim_bp.before_request
def enforce_privacy_policy():
    """Blueprint-level middleware to enforce the privacy policy across all routes.

    Inspects request args, URL parameters, and JSON payloads for privacy_mode,
    project_id, evidence_pack_id, or simulation_id to resolve the active privacy
    mode and update the global PrivacyGuard.
    """
    payload = {}
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            payload = {}

    privacy_mode = payload.get("privacy_mode") or request.args.get("privacy_mode")
    if privacy_mode:
        try:
            from ..book_sim.privacy_guard import PrivacyGuard
            PrivacyGuard.get_instance().set_mode(privacy_mode)
        except Exception:
            pass
        return

    # Try resolving project_id from payload, view args, or query string
    project_id = (
        payload.get("project_id") or
        payload.get("base_project_id") or
        payload.get("compare_project_id") or
        (request.view_args.get("project_id") if request.view_args else None) or
        request.args.get("project_id")
    )

    store = None
    try:
        from ..book_sim.runtime_store import BookSimRuntimeStore
        from ..book_sim.local_cache import LocalArtifactCache
        cache = LocalArtifactCache(base_dir=current_app.config.get("BOOK_SIM_CACHE_DIR"))
        store = BookSimRuntimeStore(cache=cache)
    except Exception:
        pass

    if store and project_id:
        try:
            project = store.get_project(project_id)
            if project and project.privacy_mode:
                from ..book_sim.privacy_guard import PrivacyGuard
                PrivacyGuard.get_instance().set_mode(project.privacy_mode)
                return
        except Exception:
            pass

    evidence_pack_id = (
        payload.get("evidence_pack_id") or
        payload.get("base_evidence_pack_id") or
        payload.get("compare_evidence_pack_id") or
        request.args.get("evidence_pack_id")
    )
    if store and evidence_pack_id:
        try:
            ep = store.get_evidence_pack(evidence_pack_id)
            if ep and ep.privacy_mode:
                from ..book_sim.privacy_guard import PrivacyGuard
                PrivacyGuard.get_instance().set_mode(ep.privacy_mode)
                return
        except Exception:
            pass

    simulation_id = (
        payload.get("simulation_id") or
        payload.get("base_simulation_id") or
        payload.get("compare_simulation_id") or
        request.args.get("simulation_id")
    )
    if store and simulation_id:
        try:
            sr = store.get_simulation_run(simulation_id)
            if sr and sr.metadata and isinstance(sr.metadata, dict):
                mode = sr.metadata.get("effective_privacy_mode") or sr.metadata.get("profile_privacy_mode")
                if mode:
                    from ..book_sim.privacy_guard import PrivacyGuard
                    PrivacyGuard.get_instance().set_mode(mode)
                    return
        except Exception:
            pass


# Create or update Swarmbook project metadata before ingestion starts.
@book_sim_bp.route("/projects", methods=["POST"])
@_api_route
def create_project():
    """Create Swarmbook project metadata in the additive runtime store."""
    payload = _request_payload()
    name = _require_text(payload, "name")
    draft_id = _optional_text(payload, "draft_id")
    version = _optional_text(payload, "version")
    project_id = _optional_text(payload, "project_id") or _project_id(
        name=name,
        title=_optional_text(payload, "title"),
        draft_id=draft_id,
        version=version,
    )
    store = _store()
    existing_project = store.get_project(project_id)
    incoming_metadata = _optional_dict(payload, "metadata") or {}
    existing_metadata = existing_project.metadata if existing_project and isinstance(existing_project.metadata, dict) else {}
    merged_metadata = {**existing_metadata, **incoming_metadata}
    profile_loader, selected_profile = _resolve_profile(
        payload=payload,
        project=existing_project,
        metadata=merged_metadata,
    )
    merged_metadata["local_profile"] = selected_profile.profile_name
    merged_metadata["local_profile_warnings"] = profile_loader.get_profile_warnings(selected_profile.profile_name)
    project = BookProject(
        project_id=project_id,
        name=name,
        privacy_mode=_validate_privacy_mode(
            _optional_text(payload, "privacy_mode"),
            default=selected_profile.privacy_mode,
        ),
        draft_id=draft_id,
        version=version,
        title=_optional_text(payload, "title"),
        author_name=_optional_text(payload, "author_name"),
        source_files=[str(item) for item in _optional_list(payload, "source_files")],
        metadata=merged_metadata,
    )
    store.save_project(project)
    return _success_response(project.to_dict(), status_code=201)


@book_sim_bp.route("/parse-file", methods=["POST"])
@_api_route
def parse_file():
    """Extract text and metadata from an uploaded file (PDF, DOCX, TXT, MD)."""
    if 'file' not in request.files:
        raise ApiError("No file part in the request", status_code=400, error_code="validation_error")
    
    file = request.files['file']
    if not file or not file.filename:
        raise ApiError("No file selected", status_code=400, error_code="validation_error")

    filename = file.filename
    from ..utils.file_parser import FileParser
    import os
    import tempfile
    import uuid

    # Get file suffix
    ext = os.path.splitext(filename)[1].lower()
    if ext not in FileParser.SUPPORTED_EXTENSIONS:
        raise ApiError(
            f"Unsupported file format: {ext}",
            status_code=400,
            error_code="unsupported_file",
            details={
                "filename": filename,
                "supported": sorted(list(FileParser.SUPPORTED_EXTENSIONS))
            }
        )

    # Absolute raw file size limit is 10 MB to prevent server crash
    max_file_size = 10 * 1024 * 1024  # 10 MB
    raw_data = file.read()
    file_size = len(raw_data)
    
    if file_size > max_file_size:
        oversized_bytes = file_size - max_file_size
        oversized_percent = (oversized_bytes / max_file_size) * 100
        raise ApiError(
            f"File too large: {filename} exceeds the limit of {max_file_size} bytes.",
            status_code=400,
            error_code="file_too_large",
            details={
                "filename": filename,
                "max_size": max_file_size,
                "actual_size": file_size,
                "oversized_absolute": oversized_bytes,
                "oversized_percentage": round(oversized_percent, 2)
            }
        )

    # Save to workspace temporary directory
    workspace_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    temp_dir = os.path.join(workspace_dir, "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")

    try:
        with open(temp_file_path, "wb") as temp_f:
            temp_f.write(raw_data)
        
        try:
            text = FileParser.extract_text(temp_file_path)
        except Exception as exc:
            raise ApiError(
                f"Failed to parse file: {str(exc)}",
                status_code=400,
                error_code="parsing_failed",
                details={
                    "filename": filename,
                    "error": str(exc)
                }
            )
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

    # Check parsed character limit (500,000 characters limit)
    max_chars = MAX_MANUSCRIPT_CHARS_DEFAULT
    if len(text) > max_chars:
        oversized_chars = len(text) - max_chars
        oversized_percent = (oversized_chars / max_chars) * 100
        raise ApiError(
            f"Manuscript text is too large: {len(text)} characters exceeds the limit of {max_chars}.",
            status_code=400,
            error_code="file_too_large",
            details={
                "filename": filename,
                "max_size": max_chars,
                "actual_size": len(text),
                "oversized_absolute": oversized_chars,
                "oversized_percentage": round(oversized_percent, 2),
                "unit": "characters"
            }
        )

    word_count = len(text.split())

    return _success_response({
        "filename": filename,
        "size_bytes": file_size,
        "character_count": len(text),
        "word_count": word_count,
        "text": text,
        "mime_type": file.mimetype or "text/plain"
    })


# Ingest manuscript text and build a Swarmbook evidence pack.
@book_sim_bp.route("/evidence-packs", methods=["POST"])
@_api_route
def create_evidence_pack():
    """Generate an evidence pack for a stored project."""
    payload = _request_payload()
    project_id = _require_text(payload, "project_id")
    store = _store()
    project = _load_project(store, project_id)
    router, _ = _maybe_router()
    builder = EvidencePackBuilder(model_router=router, cache=_cache())
    manuscript = _manuscript_input(project, payload)
    updated_project = BookProject.from_dict(
        {
            **project.to_dict(),
            "title": manuscript.title,
            "author_name": manuscript.author_name,
            "manuscript_input": manuscript.to_dict(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    evidence_pack = builder.build_from_manuscript(updated_project, manuscript)
    store.save_project(updated_project)
    store.save_evidence_pack(evidence_pack)
    persistence = _graph_persistence().persist_evidence_pack(project=updated_project, evidence_pack=evidence_pack)
    return _success_response(
        {
            "project": updated_project.to_dict(),
            "evidence_pack": evidence_pack.to_dict(),
            "persistence": persistence.__dict__,
        },
        status_code=201,
    )


# Run the Swarmbook simulation pipeline, then synthesize scores and a report.
@book_sim_bp.route("/simulate", methods=["POST"])
@_api_route
def simulate_book():
    """Run persona generation, reactions, scoring, and report synthesis."""
    payload = _request_payload()
    project_id = _require_text(payload, "project_id")
    store = _store()
    project = _load_project(store, project_id)
    profile_loader, selected_profile = _resolve_profile(payload=payload, project=project)
    evidence_pack = _resolve_evidence_pack(payload, store)
    if evidence_pack.project_id != project.project_id:
        raise ApiError(
            "evidence_pack project_id does not match project_id",
            details={"project_id": project.project_id, "evidence_pack_project_id": evidence_pack.project_id},
        )

    router, _ = _maybe_router()
    effective_privacy_mode = _validate_privacy_mode(
        _optional_text(payload, "privacy_mode"),
        default=project.privacy_mode or selected_profile.privacy_mode,
    )
    selection = _route_selection(router, _optional_text(payload, "route_name"), effective_privacy_mode)
    reaction_rounds = _optional_positive_int(payload, "reaction_rounds") or selected_profile.reaction_rounds
    cross_reaction_posts = _optional_positive_int(payload, "cross_reaction_posts") or selected_profile.cross_reaction_posts
    local_parallel_jobs = _optional_positive_int(payload, "local_parallel_jobs") or selected_profile.local_parallel_jobs
    orchestrator = SimulationOrchestrator(
        cache=_cache(),
        graph_persistence=None,
        model_router=router,
        cross_reaction_posts=cross_reaction_posts,
        max_reaction_rounds=reaction_rounds,
        max_parallel_jobs=local_parallel_jobs,
    )
    simulation_seed = _optional_int(payload, "simulation_seed")
    persona_overrides = _persona_overrides(payload, selected_profile)
    simulation_run = orchestrator.run(
        project=project,
        evidence_pack=evidence_pack,
        simulation_seed=simulation_seed,
        persona_overrides=persona_overrides,
    )
    simulation_payload = simulation_run.to_dict()
    simulation_payload["provider_route"] = selection.selected_route
    simulation_payload["metadata"] = {
        **simulation_run.metadata,
        "seed": simulation_seed,
        "local_profile": selected_profile.profile_name,
        "profile_privacy_mode": selected_profile.privacy_mode,
        "effective_privacy_mode": effective_privacy_mode,
        "profile_defaults": {
            "max_personas": selected_profile.max_personas,
            "platforms": selected_profile.platforms,
            "reaction_rounds": selected_profile.reaction_rounds,
            "cross_reaction_posts": selected_profile.cross_reaction_posts,
            "local_parallel_jobs": selected_profile.local_parallel_jobs,
        },
        "applied_settings": {
            "persona_count": persona_overrides.persona_count,
            "platforms": persona_overrides.allowed_platforms,
            "reaction_rounds": reaction_rounds,
            "cross_reaction_posts": cross_reaction_posts,
            "local_parallel_jobs": local_parallel_jobs,
        },
        "requested_route": selection.requested_route,
        "selected_route": selection.selected_route,
        "route_reason": selection.reason,
    }
    simulation_run = SimulationRun.from_dict(simulation_payload)

    # Persist the simulation payload even if report synthesis fails, so callers can recover.
    store.save_simulation_run(simulation_run)

    try:
        report_payload = _resolve_report_payload(project=project, evidence_pack=evidence_pack, simulation_run=simulation_run)
        report = report_payload["report"]
        simulation_run = report_payload["simulation_run"]
        store.save_simulation_run(simulation_run)
        store.save_report(report)
    except Exception as exc:
        raise ApiError(
            "Simulation ran but report synthesis failed. You can retry report generation using the stored simulation_id.",
            status_code=502,
            error_code="partial_failure",
            details={
                "project_id": project.project_id,
                "simulation_id": simulation_run.run_id,
                "error": str(exc),
            },
        ) from exc
    persistence = _graph_persistence().persist_simulation_artifacts(
        project=project,
        simulation_run=simulation_run,
        reader_personas=simulation_run.reader_personas,
        private_reactions=simulation_run.private_reactions,
        platform_posts=simulation_run.platform_posts,
        cross_reactions=simulation_run.cross_reactions,
        report=report,
    )
    return _success_response(
        {
            "simulation_run": simulation_run.to_dict(),
            "report": report.to_dict(),
            "report_markdown": render_prediction_report_markdown(report),
            "route_selection": selection.__dict__,
            "profile": _profile_response_payload(profile_loader, selected_profile),
            "persistence": persistence.__dict__,
        },
        status_code=201,
    )


# Return the latest synthesized Swarmbook report for a project.
@book_sim_bp.route("/projects/<project_id>/report", methods=["GET"])
@_api_route
def get_latest_report(project_id: str):
    """Fetch the latest report stored for one Swarmbook project."""
    report = _store().get_latest_report(project_id)
    if report is None:
        raise ApiError(
            f"No report is available for project: {project_id}",
            status_code=404,
            error_code="not_found",
        )
    return _success_response(report.to_dict())


# Interrogate a stored simulated persona using the latest or explicit artifacts.
@book_sim_bp.route("/personas/<persona_id>/chat", methods=["POST"])
@_api_route
def chat_with_persona(persona_id: str):
    """Answer a grounded persona question from stored Swarmbook artifacts."""
    payload = _request_payload()
    result = _interrogate_result(persona_id=persona_id, payload=payload, store=_store())
    return _success_response(result)


# Compare two drafts using stored or explicit evidence packs, simulations, and scores.
@book_sim_bp.route("/compare", methods=["POST"])
@_api_route
def compare_drafts():
    """Compare two drafts and export both JSON and Markdown representations."""
    payload = _request_payload()
    store = _store()
    base_pack = _resolve_evidence_pack(
        {
            "evidence_pack": payload.get("base_evidence_pack"),
            "evidence_pack_id": payload.get("base_evidence_pack_id"),
            "project_id": payload.get("base_project_id"),
        },
        store,
    )
    compare_pack = _resolve_evidence_pack(
        {
            "evidence_pack": payload.get("compare_evidence_pack"),
            "evidence_pack_id": payload.get("compare_evidence_pack_id"),
            "project_id": payload.get("compare_project_id"),
        },
        store,
    )
    base_run = None
    base_run_explicit = payload.get("base_simulation_run") is not None or payload.get("base_simulation_id") is not None
    if payload.get("base_simulation_run") is not None or payload.get("base_simulation_id") or payload.get("base_project_id"):
        try:
            base_run = _resolve_simulation_run(
                {
                    "simulation_run": payload.get("base_simulation_run"),
                    "simulation_id": payload.get("base_simulation_id"),
                    "project_id": payload.get("base_project_id"),
                },
                store,
            )
        except ApiError:
            if base_run_explicit:
                raise
            base_run = None
    compare_run = None
    compare_run_explicit = payload.get("compare_simulation_run") is not None or payload.get("compare_simulation_id") is not None
    if payload.get("compare_simulation_run") is not None or payload.get("compare_simulation_id") or payload.get("compare_project_id"):
        try:
            compare_run = _resolve_simulation_run(
                {
                    "simulation_run": payload.get("compare_simulation_run"),
                    "simulation_id": payload.get("compare_simulation_id"),
                    "project_id": payload.get("compare_project_id"),
                },
                store,
            )
        except ApiError:
            if compare_run_explicit:
                raise
            compare_run = None

    export = DraftComparator().compare(
        project_id=_comparison_project_id(payload, base_pack, compare_pack),
        base_evidence_pack=base_pack,
        compare_evidence_pack=compare_pack,
        base_simulation_run=base_run,
        compare_simulation_run=compare_run,
        base_scores=_optional_dict(payload, "base_scores"),
        compare_scores=_optional_dict(payload, "compare_scores"),
        simulation_seed=_optional_int(payload, "simulation_seed"),
    )
    _store().save_comparison(export.report)
    return _success_response(export.to_dict())


# Report router, provider, Neo4j, and local-Ollama health without mutating state.
@book_sim_bp.route("/health", methods=["GET"])
@_api_route
def health():
    """Expose additive Swarmbook runtime health details."""
    router, router_error = _maybe_router()
    provider_health = router.health_check() if router else {}
    profile_loader = _profile_loader()
    profile_catalog = profile_loader.load()
    router_data: Dict[str, Any] = {
        "ok": router is not None,
        "configured_routes": sorted(router.routing_config.model_routes) if router else [],
        "privacy_modes": sorted(router.routing_config.privacy_modes) if router else [],
    }
    if router_error:
        router_data["error"] = router_error
    return _success_response(
        {
            "router": router_data,
            "providers": provider_health,
            "neo4j": _neo4j_health(),
            "ollama": provider_health.get("local_ollama", {}),
            "profiles": {
                "default_profile": profile_catalog.default_profile,
                "hardware_target": profile_catalog.hardware_target.to_dict(),
                "load_error": profile_catalog.load_error,
                "items": profile_loader.list_profiles(),
            },
        }
    )


# Preserve the original narrow interrogation route for existing callers.
@book_sim_bp.route("/interrogate", methods=["POST"])
@_api_route
def interrogate_persona():
    """Backwards-compatible persona interrogation route."""
    payload = _request_payload()
    persona_id = _require_text(payload, "persona_id")
    result = _interrogate_result(persona_id=persona_id, payload=payload, store=_store())
    return _success_response(result)
