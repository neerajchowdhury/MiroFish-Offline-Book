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
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    if yaml is None:
        return _load_known_config_without_pyyaml(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping object: {path}")
    return data


def _clean_scalar(value: str) -> Any:
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _load_known_config_without_pyyaml(path: Path) -> Dict[str, Any]:
    """Parse the constrained Swarmbook route/privacy YAML when PyYAML is absent."""
    if path.name == "model_routes.yaml":
        return _load_model_routes_without_pyyaml(path)
    if path.name == "privacy_modes.yaml":
        return _load_privacy_modes_without_pyyaml(path)
    raise RuntimeError("PyYAML is required to load Swarmbook YAML config files")


def _load_model_routes_without_pyyaml(path: Path) -> Dict[str, Any]:
    routes: Dict[str, Dict[str, Any]] = {}
    current_route: Optional[str] = None
    current_list_key: Optional[str] = None
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.split("#", 1)[0].rstrip()
            if not line.strip() or line.strip() == "model_routes:":
                continue
            if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(":"):
                current_route = line.strip()[:-1]
                routes[current_route] = {}
                current_list_key = None
                continue
            if not current_route or not line.startswith("    "):
                continue
            stripped = line.strip()
            if stripped.startswith("- ") and current_list_key:
                routes[current_route].setdefault(current_list_key, []).append(_clean_scalar(stripped[2:]))
                continue
            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not value:
                routes[current_route][key] = []
                current_list_key = key
            else:
                routes[current_route][key] = _clean_scalar(value)
                current_list_key = None
    return {"model_routes": routes}


def _load_privacy_modes_without_pyyaml(path: Path) -> Dict[str, Any]:
    modes: Dict[str, Dict[str, Any]] = {}
    current_mode: Optional[str] = None
    current_list_key: Optional[str] = None
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.split("#", 1)[0].rstrip()
            if not line.strip() or line.strip() == "privacy_modes:":
                continue
            if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(":"):
                current_mode = line.strip()[:-1]
                modes[current_mode] = {}
                current_list_key = None
                continue
            if not current_mode or not line.startswith("    "):
                continue
            stripped = line.strip()
            if stripped.startswith("- ") and current_list_key:
                item = stripped[2:].strip()
                if ":" in item:
                    key, value = item.split(":", 1)
                    modes[current_mode].setdefault(current_list_key, []).append({key.strip(): _clean_scalar(value)})
                else:
                    modes[current_mode].setdefault(current_list_key, []).append(_clean_scalar(item))
                continue
            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not value:
                modes[current_mode][key] = []
                current_list_key = key
            else:
                modes[current_mode][key] = _clean_scalar(value)
                current_list_key = None
    return {"privacy_modes": modes}


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
