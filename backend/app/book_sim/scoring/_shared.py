"""Shared utilities for deterministic Swarmbook scoring."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is available in the repo, but keep a hard failure path.
    yaml = None

from ..config_loader import REPO_ROOT
from ..models import EvidencePack, PrivateReaderReaction, SimulationRun


DEFAULT_SCORING_WEIGHTS_PATH = REPO_ROOT / "configs" / "book_sim" / "scoring_weights.yaml"


def _parse_scalar(raw_value: str) -> Any:
    value = raw_value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip() for item in inner.split(",") if item.strip()]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _load_scoring_weights_raw(path: Path) -> Dict[str, Any]:
    if yaml is not None:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    sections: Dict[str, Dict[str, Any]] = {}
    current_section: Optional[str] = None
    current_map: Optional[str] = None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if line.strip() == "scoring_weights:":
                continue
            if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(":"):
                current_section = line.strip()[:-1]
                sections[current_section] = {}
                current_map = None
                continue
            if current_section and line.startswith("    ") and line.strip().endswith(":"):
                current_map = line.strip()[:-1]
                sections[current_section][current_map] = {}
                continue
            if current_section and current_map and line.startswith("      ") and ":" in line:
                key, raw_value = line.strip().split(":", 1)
                sections[current_section][current_map][key] = _parse_scalar(raw_value)
            elif current_section and line.startswith("    ") and ":" in line:
                key, raw_value = line.strip().split(":", 1)
                sections[current_section][key] = _parse_scalar(raw_value)
    return {"scoring_weights": sections}


@dataclass(frozen=True)
class ConfidenceBand:
    """Human-readable band around a deterministic estimate."""

    low: float
    mid: float
    high: float
    label: str

    def to_dict(self) -> Dict[str, float | str]:
        return {"low": self.low, "mid": self.mid, "high": self.high, "label": self.label}


@dataclass(frozen=True)
class ScoringContext:
    """Bundle the simulation artifacts needed for scoring."""

    evidence_pack: EvidencePack
    simulation_run: SimulationRun

    @property
    def private_reactions(self) -> Sequence[PrivateReaderReaction]:
        return self.simulation_run.private_reactions

    @property
    def platform_posts(self) -> Sequence[Any]:
        return self.simulation_run.platform_posts

    @property
    def cross_reactions(self) -> Sequence[Any]:
        return self.simulation_run.cross_reactions


def load_scoring_weights(path: Optional[Path] = None) -> Dict[str, Dict[str, float]]:
    """Load the scoring configuration once and normalize it into numeric weights."""
    weights_path = path or DEFAULT_SCORING_WEIGHTS_PATH
    if not weights_path.exists():
        raise FileNotFoundError(f"Missing scoring weights config: {weights_path}")
    payload = _load_scoring_weights_raw(weights_path)
    scoring = payload.get("scoring_weights", {})
    if not isinstance(scoring, dict):
        raise ValueError("scoring_weights.yaml must contain top-level 'scoring_weights' mapping")
    normalized: Dict[str, Dict[str, float]] = {}
    for section, section_payload in scoring.items():
        if not isinstance(section_payload, dict):
            continue
        components = section_payload.get("components", {})
        if isinstance(components, dict):
            normalized[section] = {str(key): float(value) for key, value in components.items()}
    return normalized


@lru_cache(maxsize=1)
def scoring_weights() -> Dict[str, Dict[str, float]]:
    return load_scoring_weights()


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def weighted_average(values: Dict[str, float], weights: Dict[str, float]) -> float:
    numerator = 0.0
    denominator = 0.0
    for key, weight in weights.items():
        numerator += values.get(key, 0.0) * weight
        denominator += weight
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def weighted_sum(values: Dict[str, float], weights: Dict[str, float]) -> float:
    return sum(values.get(key, 0.0) * weight for key, weight in weights.items())


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    if not values or not weights:
        return 0.0
    pairs = list(zip(values, weights))
    denominator = sum(weight for _, weight in pairs)
    if denominator == 0.0:
        return 0.0
    return sum(value * weight for value, weight in pairs) / denominator


def weighted_stddev(values: Sequence[float], weights: Sequence[float]) -> float:
    if not values or not weights:
        return 0.0
    avg = weighted_mean(values, weights)
    pairs = list(zip(values, weights))
    denominator = sum(weight for _, weight in pairs)
    if denominator == 0.0:
        return 0.0
    variance = sum(weight * ((value - avg) ** 2) for value, weight in pairs) / denominator
    return variance ** 0.5


def confidence_band(mid: float, spread: float, label: str) -> ConfidenceBand:
    spread = abs(spread)
    return ConfidenceBand(
        low=round(clamp(mid - spread), 3),
        mid=round(clamp(mid), 3),
        high=round(clamp(mid + spread), 3),
        label=label,
    )


def confidence_band_from_sample(mid: float, sample_size: int, variability: float, label: str) -> ConfidenceBand:
    sample_factor = 1.0 / max(1.5, sample_size ** 0.5)
    spread = clamp((0.18 * sample_factor) + (variability * 0.12), 0.03, 0.22)
    return confidence_band(mid, spread, label)


def sorted_unique(values: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def evidence_refs(*groups: Iterable[str]) -> List[str]:
    refs: List[str] = []
    for group in groups:
        if isinstance(group, str):
            refs.append(group)
            continue
        for item in group:
            if isinstance(item, str):
                refs.append(item)
            elif isinstance(item, Iterable):
                refs.extend(str(sub_item) for sub_item in item if sub_item)
            elif item:
                refs.append(str(item))
    return sorted_unique(refs)


def stable_digest(*parts: object) -> str:
    raw = "::".join(str(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
