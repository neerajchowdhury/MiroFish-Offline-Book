"""Local Swarmbook execution profiles for low-resource hardware defaults."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    import yaml
except ImportError:  # pragma: no cover - exercised where PyYAML is unavailable
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LOCAL_PROFILES_PATH = REPO_ROOT / "configs" / "book_sim" / "local_profiles.yaml"


def _clean_scalar(value: str) -> Any:
    # Strip any leading/trailing quotes
    val = value.strip()
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    try:
        return int(val)
    except ValueError:
        return val


def _load_local_profiles_without_pyyaml(path: Path) -> Dict[str, Any]:
    """Parse local_profiles.yaml when PyYAML is unavailable."""
    data: Dict[str, Any] = {
        "profiles": {}
    }
    current_section = None
    current_profile = None
    current_list_key = None

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            # Strip comments and trailing space
            line = raw_line.split("#", 1)[0].rstrip()
            if not line.strip():
                continue

            # Level 0 (no leading spaces)
            if not raw_line.startswith(" "):
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if key == "default_profile":
                        data["default_profile"] = val
                    elif key in ("hardware_target", "profiles"):
                        current_section = key
                continue

            # Level 1 (2 leading spaces, e.g. hardware_target attributes or profile keys)
            if raw_line.startswith("  ") and not raw_line.startswith("    "):
                stripped = line.strip()
                if ":" in stripped:
                    key, val = stripped.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if current_section == "hardware_target":
                        data.setdefault("hardware_target", {})[key] = _clean_scalar(val)
                    elif current_section == "profiles":
                        current_profile = key
                        data["profiles"][current_profile] = {}
                        current_list_key = None
                continue

            # Level 2 (4 leading spaces, e.g. profile attributes)
            if raw_line.startswith("    ") and not raw_line.startswith("      "):
                if not current_profile:
                    continue
                stripped = line.strip()
                if ":" in stripped:
                    key, val = stripped.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if not val:
                        # Start of a list
                        data["profiles"][current_profile][key] = []
                        current_list_key = key
                    else:
                        data["profiles"][current_profile][key] = _clean_scalar(val)
                        current_list_key = None
                continue

            # Level 3 (6 leading spaces, e.g. list items)
            if raw_line.startswith("      "):
                if not current_profile or not current_list_key:
                    continue
                stripped = line.strip()
                if stripped.startswith("- "):
                    item = stripped[2:].strip()
                    # Strip any surrounding quotes
                    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                        item = item[1:-1]
                    data["profiles"][current_profile][current_list_key].append(_clean_scalar(item))
                continue

    return data


_REQUIRED_PROFILE_FIELDS = {
    "label",
    "description",
    "privacy_mode",
    "recommended_for",
    "max_personas",
    "platforms",
    "reaction_rounds",
    "cross_reaction_posts",
    "local_parallel_jobs",
    "use_local_embeddings",
    "use_local_chunk_summaries",
    "allow_external_models",
    "allow_full_manuscript_to_cloud",
    "allow_evidence_packs_to_cloud",
    "preferred_tasks",
    "warnings",
    "estimated_resource_level",
}


@dataclass(frozen=True)
class HardwareTarget:
    """Hardware target metadata used for profile-level warnings."""

    os: str
    ram_gb: int
    gpu: str
    vram_gb: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "os": self.os,
            "ram_gb": self.ram_gb,
            "gpu": self.gpu,
            "vram_gb": self.vram_gb,
        }


@dataclass(frozen=True)
class LocalProfile:
    """One named local profile with simulation/runtime defaults."""

    profile_name: str
    label: str
    description: str
    privacy_mode: str
    recommended_for: List[str]
    max_personas: int
    platforms: List[str]
    reaction_rounds: int
    cross_reaction_posts: int
    local_parallel_jobs: int
    use_local_embeddings: bool
    use_local_chunk_summaries: bool
    allow_external_models: bool
    allow_full_manuscript_to_cloud: bool
    allow_evidence_packs_to_cloud: bool
    preferred_tasks: List[str]
    warnings: List[str]
    estimated_resource_level: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_name": self.profile_name,
            "label": self.label,
            "description": self.description,
            "privacy_mode": self.privacy_mode,
            "recommended_for": list(self.recommended_for),
            "max_personas": self.max_personas,
            "platforms": list(self.platforms),
            "reaction_rounds": self.reaction_rounds,
            "cross_reaction_posts": self.cross_reaction_posts,
            "local_parallel_jobs": self.local_parallel_jobs,
            "use_local_embeddings": self.use_local_embeddings,
            "use_local_chunk_summaries": self.use_local_chunk_summaries,
            "allow_external_models": self.allow_external_models,
            "allow_full_manuscript_to_cloud": self.allow_full_manuscript_to_cloud,
            "allow_evidence_packs_to_cloud": self.allow_evidence_packs_to_cloud,
            "preferred_tasks": list(self.preferred_tasks),
            "warnings": list(self.warnings),
            "estimated_resource_level": self.estimated_resource_level,
        }


@dataclass(frozen=True)
class LocalProfileCatalog:
    """Parsed local profile catalog, including load status."""

    default_profile: str
    hardware_target: HardwareTarget
    profiles: Dict[str, LocalProfile]
    config_path: Path
    load_error: Optional[str] = None

    def get_profile(self, profile_name: str) -> Optional[LocalProfile]:
        return self.profiles.get(profile_name)

    def get_default_profile(self) -> LocalProfile:
        default = self.get_profile(self.default_profile)
        if default is not None:
            return default
        # Fallback safety in case of malformed config.
        return next(iter(self.profiles.values()))


@dataclass
class LocalProfileLoader:
    """Load, validate, and expose local profile defaults and warnings."""

    config_path: Path = DEFAULT_LOCAL_PROFILES_PATH
    _catalog: Optional[LocalProfileCatalog] = field(default=None, init=False, repr=False)

    def load(self) -> LocalProfileCatalog:
        if self._catalog is not None:
            return self._catalog
        try:
            self._catalog = self._load_from_disk()
        except Exception as exc:  # pragma: no cover - defensive fallback path
            self._catalog = self._fallback_catalog(str(exc))
        return self._catalog

    def list_profiles(self) -> List[Dict[str, Any]]:
        catalog = self.load()
        profiles: List[Dict[str, Any]] = []
        for profile_name in sorted(catalog.profiles.keys()):
            profile = catalog.profiles[profile_name]
            profiles.append(
                {
                    **profile.to_dict(),
                    "is_default": profile_name == catalog.default_profile,
                    "computed_warnings": self.get_profile_warnings(profile_name),
                }
            )
        return profiles

    def get_profile(self, profile_name: str) -> Optional[LocalProfile]:
        if not profile_name:
            return None
        return self.load().get_profile(profile_name)

    def get_default_profile(self) -> LocalProfile:
        return self.load().get_default_profile()

    def get_profile_warnings(
        self,
        profile_name: str,
        detected_or_configured_hardware: Optional[Mapping[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        profile = self.get_profile(profile_name)
        if profile is None:
            return [
                {
                    "code": "unknown_profile",
                    "level": "error",
                    "message": f"Unknown profile: {profile_name}",
                }
            ]

        catalog = self.load()
        hardware = self._effective_hardware(catalog.hardware_target, detected_or_configured_hardware)
        warnings: List[Dict[str, str]] = []

        for message in profile.warnings:
            warnings.append({"code": "profile_warning", "level": "info", "message": message})

        if profile.profile_name == "local_tiny":
            warnings.append(
                {
                    "code": "local_tiny_quality_tradeoff",
                    "level": "info",
                    "message": "local_tiny prioritizes privacy and speed over quality depth.",
                }
            )
        if profile.profile_name == catalog.default_profile:
            warnings.append(
                {
                    "code": "recommended_default",
                    "level": "info",
                    "message": f"{profile.profile_name} is the recommended default for the configured hardware target.",
                }
            )
        if profile.profile_name == "cloud_quality":
            warnings.append(
                {
                    "code": "cloud_quality_heavy",
                    "level": "warning",
                    "message": "cloud_quality can be slower and more costly on 16 GB RAM / 6 GB VRAM systems.",
                }
            )
        if profile.max_personas > 30 and hardware["ram_gb"] <= 16 and hardware["vram_gb"] <= 6:
            warnings.append(
                {
                    "code": "high_persona_load",
                    "level": "warning",
                    "message": "Persona count above 30 may increase latency on the configured hardware target.",
                }
            )
        if profile.allow_full_manuscript_to_cloud:
            warnings.append(
                {
                    "code": "cloud_manuscript_privacy",
                    "level": "warning",
                    "message": "This profile allows full manuscript cloud upload. Review privacy policy before use.",
                }
            )

        deduped: List[Dict[str, str]] = []
        seen = set()
        for warning in warnings:
            key = (warning["code"], warning["message"])
            if key in seen:
                continue
            seen.add(key)
            deduped.append(warning)
        return deduped

    def _load_from_disk(self) -> LocalProfileCatalog:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Missing local profile config: {self.config_path}")
        if yaml is None:
            payload = _load_local_profiles_without_pyyaml(self.config_path)
        else:
            with self.config_path.open("r", encoding="utf-8") as handle:
                payload = yaml.safe_load(handle) or {}
        if not isinstance(payload, dict):
            raise ValueError("local_profiles.yaml must contain a mapping at the top level")

        default_profile = str(payload.get("default_profile", "")).strip()
        if not default_profile:
            raise ValueError("local_profiles.yaml must define default_profile")

        hardware_payload = payload.get("hardware_target", {})
        if not isinstance(hardware_payload, dict):
            raise ValueError("hardware_target must be a mapping object")
        hardware_target = HardwareTarget(
            os=str(hardware_payload.get("os", "Windows 11")).strip() or "Windows 11",
            ram_gb=int(hardware_payload.get("ram_gb", 16)),
            gpu=str(hardware_payload.get("gpu", "NVIDIA")).strip() or "NVIDIA",
            vram_gb=int(hardware_payload.get("vram_gb", 6)),
        )

        raw_profiles = payload.get("profiles", {})
        if not isinstance(raw_profiles, dict) or not raw_profiles:
            raise ValueError("local_profiles.yaml must define a non-empty profiles mapping")

        profiles: Dict[str, LocalProfile] = {}
        for profile_name, profile_payload in raw_profiles.items():
            if not isinstance(profile_payload, dict):
                raise ValueError(f"Profile payload must be an object: {profile_name}")
            missing = sorted(_REQUIRED_PROFILE_FIELDS - set(profile_payload.keys()))
            if missing:
                raise ValueError(f"Profile '{profile_name}' is missing required fields: {', '.join(missing)}")
            profiles[profile_name] = LocalProfile(
                profile_name=profile_name,
                label=str(profile_payload["label"]),
                description=str(profile_payload["description"]),
                privacy_mode=str(profile_payload["privacy_mode"]),
                recommended_for=[str(item) for item in profile_payload.get("recommended_for", [])],
                max_personas=int(profile_payload["max_personas"]),
                platforms=[str(item) for item in profile_payload.get("platforms", [])],
                reaction_rounds=int(profile_payload["reaction_rounds"]),
                cross_reaction_posts=int(profile_payload["cross_reaction_posts"]),
                local_parallel_jobs=max(1, int(profile_payload["local_parallel_jobs"])),
                use_local_embeddings=bool(profile_payload["use_local_embeddings"]),
                use_local_chunk_summaries=bool(profile_payload["use_local_chunk_summaries"]),
                allow_external_models=bool(profile_payload["allow_external_models"]),
                allow_full_manuscript_to_cloud=bool(profile_payload["allow_full_manuscript_to_cloud"]),
                allow_evidence_packs_to_cloud=bool(profile_payload["allow_evidence_packs_to_cloud"]),
                preferred_tasks=[str(item) for item in profile_payload.get("preferred_tasks", [])],
                warnings=[str(item) for item in profile_payload.get("warnings", [])],
                estimated_resource_level=str(profile_payload["estimated_resource_level"]),
            )

        if default_profile not in profiles:
            raise ValueError("default_profile must match one of the configured profiles")

        return LocalProfileCatalog(
            default_profile=default_profile,
            hardware_target=hardware_target,
            profiles=profiles,
            config_path=self.config_path,
            load_error=None,
        )

    def _fallback_catalog(self, load_error: str) -> LocalProfileCatalog:
        fallback_payload: Dict[str, Any] = {
            "default_profile": "hybrid_safe_default",
            "hardware_target": {
                "os": "Windows 11",
                "ram_gb": 16,
                "gpu": "NVIDIA",
                "vram_gb": 6,
            },
            "profiles": {
                "local_tiny": {
                    "label": "Local Tiny",
                    "description": "Safest fully local profile.",
                    "privacy_mode": "local_only",
                    "recommended_for": ["quick local checks"],
                    "max_personas": 12,
                    "platforms": ["Goodreads", "Reddit", "X"],
                    "reaction_rounds": 1,
                    "cross_reaction_posts": 4,
                    "local_parallel_jobs": 1,
                    "use_local_embeddings": True,
                    "use_local_chunk_summaries": True,
                    "allow_external_models": False,
                    "allow_full_manuscript_to_cloud": False,
                    "allow_evidence_packs_to_cloud": False,
                    "preferred_tasks": ["privacy-first simulation"],
                    "warnings": ["Fallback profile loaded because local_profiles.yaml was unavailable."],
                    "estimated_resource_level": "low",
                },
                "hybrid_safe_default": {
                    "label": "Hybrid Safe Default",
                    "description": "Balanced default profile.",
                    "privacy_mode": "hybrid_safe",
                    "recommended_for": ["balanced simulation"],
                    "max_personas": 30,
                    "platforms": ["Goodreads", "Reddit", "BookTok", "Bookstagram", "X"],
                    "reaction_rounds": 2,
                    "cross_reaction_posts": 8,
                    "local_parallel_jobs": 1,
                    "use_local_embeddings": True,
                    "use_local_chunk_summaries": True,
                    "allow_external_models": True,
                    "allow_full_manuscript_to_cloud": False,
                    "allow_evidence_packs_to_cloud": True,
                    "preferred_tasks": ["default simulation"],
                    "warnings": ["Fallback profile loaded because local_profiles.yaml was unavailable."],
                    "estimated_resource_level": "medium",
                },
                "cloud_quality": {
                    "label": "Cloud Quality",
                    "description": "Highest quality cloud-assisted profile.",
                    "privacy_mode": "cloud_quality",
                    "recommended_for": ["high-fidelity simulation"],
                    "max_personas": 60,
                    "platforms": ["Goodreads", "Reddit", "BookTok", "Bookstagram", "X", "newsletter", "bookclub"],
                    "reaction_rounds": 2,
                    "cross_reaction_posts": 12,
                    "local_parallel_jobs": 1,
                    "use_local_embeddings": True,
                    "use_local_chunk_summaries": False,
                    "allow_external_models": True,
                    "allow_full_manuscript_to_cloud": True,
                    "allow_evidence_packs_to_cloud": True,
                    "preferred_tasks": ["quality-max simulation"],
                    "warnings": ["Fallback profile loaded because local_profiles.yaml was unavailable."],
                    "estimated_resource_level": "high",
                },
            },
        }

        raw_default = str(fallback_payload["default_profile"])
        hardware_target = HardwareTarget(
            os=str(fallback_payload["hardware_target"]["os"]),
            ram_gb=int(fallback_payload["hardware_target"]["ram_gb"]),
            gpu=str(fallback_payload["hardware_target"]["gpu"]),
            vram_gb=int(fallback_payload["hardware_target"]["vram_gb"]),
        )
        profiles: Dict[str, LocalProfile] = {}
        for profile_name, profile_payload in fallback_payload["profiles"].items():
            profiles[profile_name] = LocalProfile(
                profile_name=profile_name,
                label=str(profile_payload["label"]),
                description=str(profile_payload["description"]),
                privacy_mode=str(profile_payload["privacy_mode"]),
                recommended_for=[str(item) for item in profile_payload["recommended_for"]],
                max_personas=int(profile_payload["max_personas"]),
                platforms=[str(item) for item in profile_payload["platforms"]],
                reaction_rounds=int(profile_payload["reaction_rounds"]),
                cross_reaction_posts=int(profile_payload["cross_reaction_posts"]),
                local_parallel_jobs=int(profile_payload["local_parallel_jobs"]),
                use_local_embeddings=bool(profile_payload["use_local_embeddings"]),
                use_local_chunk_summaries=bool(profile_payload["use_local_chunk_summaries"]),
                allow_external_models=bool(profile_payload["allow_external_models"]),
                allow_full_manuscript_to_cloud=bool(profile_payload["allow_full_manuscript_to_cloud"]),
                allow_evidence_packs_to_cloud=bool(profile_payload["allow_evidence_packs_to_cloud"]),
                preferred_tasks=[str(item) for item in profile_payload["preferred_tasks"]],
                warnings=[str(item) for item in profile_payload["warnings"]],
                estimated_resource_level=str(profile_payload["estimated_resource_level"]),
            )
        return LocalProfileCatalog(
            default_profile=raw_default,
            hardware_target=hardware_target,
            profiles=profiles,
            config_path=self.config_path,
            load_error=load_error,
        )

    def _effective_hardware(
        self,
        configured_hardware: HardwareTarget,
        override: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        if not override:
            return configured_hardware.to_dict()
        base = configured_hardware.to_dict()
        return {
            "os": str(override.get("os", base["os"])),
            "ram_gb": int(override.get("ram_gb", base["ram_gb"])),
            "gpu": str(override.get("gpu", base["gpu"])),
            "vram_gb": int(override.get("vram_gb", base["vram_gb"])),
        }


_DEFAULT_LOADER = LocalProfileLoader()


def list_profiles() -> List[Dict[str, Any]]:
    """List all configured profiles with computed warnings."""
    return _DEFAULT_LOADER.list_profiles()


def get_profile(profile_name: str) -> Optional[LocalProfile]:
    """Return one profile by name, or None when unknown."""
    return _DEFAULT_LOADER.get_profile(profile_name)


def get_default_profile() -> LocalProfile:
    """Return the configured default profile."""
    return _DEFAULT_LOADER.get_default_profile()


def get_profile_warnings(
    profile_name: str,
    detected_or_configured_hardware: Optional[Mapping[str, Any]] = None,
) -> List[Dict[str, str]]:
    """Return structured warnings for one profile and hardware context."""
    return _DEFAULT_LOADER.get_profile_warnings(profile_name, detected_or_configured_hardware)
