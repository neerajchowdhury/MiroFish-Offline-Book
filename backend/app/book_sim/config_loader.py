"""Configuration loading for Swarmbook provider routing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in environments without PyYAML
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_ROUTES_PATH = REPO_ROOT / "configs" / "book_sim" / "model_routes.yaml"
DEFAULT_PRIVACY_MODES_PATH = REPO_ROOT / "configs" / "book_sim" / "privacy_modes.yaml"


def _load_yaml_dict(path: Path) -> Dict[str, Any]:
    """Load a YAML file as dict and validate shape."""
    if yaml is None:
        raise RuntimeError("PyYAML is required to load Swarmbook YAML config files")
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping object: {path}")
    return data


@dataclass(frozen=True)
class ModelRouteEntry:
    """Single route entry from model_routes.yaml."""

    route_name: str
    provider: str
    model: str
    purpose: List[str] = field(default_factory=list)
    max_input_tokens: int = 8192
    output_mode: str = "structured_json"
    privacy_mode_allowlist: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class BookSimRoutingConfig:
    """In-memory routing config for provider selection."""

    model_routes: Dict[str, ModelRouteEntry]
    privacy_modes: Dict[str, Dict[str, Any]]
    model_routes_path: Path
    privacy_modes_path: Path

    @classmethod
    def from_yaml(
        cls,
        model_routes_path: Optional[Path] = None,
        privacy_modes_path: Optional[Path] = None,
    ) -> "BookSimRoutingConfig":
        """Load model routes and privacy modes from YAML files."""
        routes_path = model_routes_path or DEFAULT_MODEL_ROUTES_PATH
        privacy_path = privacy_modes_path or DEFAULT_PRIVACY_MODES_PATH

        routes_raw = _load_yaml_dict(routes_path)
        privacy_raw = _load_yaml_dict(privacy_path)

        raw_routes = routes_raw.get("model_routes", {})
        if not isinstance(raw_routes, dict):
            raise ValueError("model_routes.yaml must contain top-level 'model_routes' mapping")

        route_entries: Dict[str, ModelRouteEntry] = {}
        for route_name, payload in raw_routes.items():
            if not isinstance(payload, dict):
                raise ValueError(f"Route payload must be a mapping: {route_name}")
            route_entries[route_name] = ModelRouteEntry(
                route_name=route_name,
                provider=str(payload.get("provider", "")).strip(),
                model=str(payload.get("model", "")).strip(),
                purpose=list(payload.get("purpose", []) or []),
                max_input_tokens=int(payload.get("max_input_tokens", 8192)),
                output_mode=str(payload.get("output_mode", "structured_json")),
                privacy_mode_allowlist=list(payload.get("privacy_mode_allowlist", []) or []),
            )

        if "local_ollama" not in route_entries:
            raise ValueError("model_routes.yaml must include local_ollama route")

        raw_privacy_modes = privacy_raw.get("privacy_modes", {})
        if not isinstance(raw_privacy_modes, dict):
            raise ValueError("privacy_modes.yaml must contain top-level 'privacy_modes' mapping")

        return cls(
            model_routes=route_entries,
            privacy_modes=raw_privacy_modes,
            model_routes_path=routes_path,
            privacy_modes_path=privacy_path,
        )
