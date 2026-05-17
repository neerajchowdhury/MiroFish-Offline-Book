"""Load and normalize reader archetypes for persona generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .config_loader import REPO_ROOT, _load_yaml_dict
from .models import ReaderArchetype


DEFAULT_READER_ARCHETYPES_PATH = REPO_ROOT / "configs" / "book_sim" / "reader_archetypes.yaml"

_FAVORITE_GENRES_BY_BIAS: Dict[str, List[str]] = {
    "high_standards": ["literary fiction", "upmarket fiction", "mystery"],
    "loyal": ["romance", "fantasy", "thriller"],
    "emotion_first": ["romance", "women's fiction", "young adult"],
    "trope_aware": ["romance", "fantasy romance", "new adult"],
    "evidence_first": ["nonfiction", "history", "science"],
    "strict": ["science fiction", "fantasy", "crime"],
    "visual_mood": ["romantasy", "literary fiction", "art books"],
    "reactive": ["cultural criticism", "literary fiction", "memoir"],
    "broad": ["thriller", "romance", "self-help"],
    "craft_first": ["literary fiction", "short stories", "essays"],
    "practical": ["business", "self-help", "psychology"],
    "rigor_first": ["history", "science", "business"],
}

_COHORT_BY_PLATFORM = {
    "goodreads": "community_reviewers",
    "booktok": "viral_emotion_seekers",
    "reddit": "skeptical_forum_readers",
    "bookstagram": "aesthetic_curators",
    "x": "hot_take_amplifiers",
    "kindle": "casual_volume_readers",
    "newsletter": "craft_conscious_readers",
    "bookclub": "discussion_driven_readers",
}

_DNF_THRESHOLD_BY_TENDENCY = {
    "low": 0.8,
    "low_medium": 0.72,
    "medium": 0.6,
    "medium_high": 0.45,
    "high": 0.3,
}

_INFLUENCE_WEIGHT_BY_PROFILE = {
    "low": 0.2,
    "low_to_medium": 0.35,
    "medium": 0.55,
    "medium_high": 0.72,
    "high": 0.9,
}

_RATING_BIAS_BY_STYLE = {
    "critical_balanced": -0.2,
    "genre_defense": 0.15,
    "emotional_confessional": 0.1,
    "trope_driven": 0.2,
    "analytical_skeptical": -0.15,
    "taxonomy_focused": -0.1,
    "aesthetic_curated": 0.05,
    "punchy_polarized": -0.05,
    "pragmatic_plainspoken": -0.1,
    "reflective_critical": -0.05,
    "utility_focused": 0.05,
    "source_auditor": -0.2,
}

_CONTROVERSY_BY_PLATFORM = {
    "goodreads": 0.45,
    "booktok": 0.7,
    "reddit": 0.6,
    "bookstagram": 0.35,
    "x": 0.9,
    "kindle": 0.3,
    "newsletter": 0.4,
    "bookclub": 0.5,
}

_EVIDENCE_FOCUS_BY_STYLE = {
    "critical_balanced": 0.55,
    "genre_defense": 0.35,
    "emotional_confessional": 0.2,
    "trope_driven": 0.25,
    "analytical_skeptical": 0.9,
    "taxonomy_focused": 0.75,
    "aesthetic_curated": 0.15,
    "punchy_polarized": 0.2,
    "pragmatic_plainspoken": 0.5,
    "reflective_critical": 0.7,
    "utility_focused": 0.8,
    "source_auditor": 0.95,
}


def _normalize_book_type(book_type: Optional[str]) -> str:
    value = (book_type or "").strip().lower()
    if "nonfiction" in value:
        return "nonfiction"
    if "fiction" in value:
        return "fiction"
    return "mixed_unknown"


def _infer_book_type_suitability(archetype_id: str, genre_bias: Optional[str], platform_home: str) -> List[str]:
    normalized_bias = (genre_bias or "").strip().lower()
    if archetype_id.startswith("nonfiction_"):
        return ["nonfiction"]
    if normalized_bias in {"practical", "rigor_first"}:
        return ["nonfiction"]
    if archetype_id in {"casual_kindle_reader", "reddit_skeptic"}:
        return ["fiction", "nonfiction"]
    if platform_home in {"booktok", "bookstagram"}:
        return ["fiction"]
    if archetype_id == "literary_reader":
        return ["fiction"]
    return ["fiction"]


def _parse_scalar(raw_value: str):
    value = raw_value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip() for item in inner.split(",") if item.strip()]
    return value


def _load_reader_archetypes_raw(path: Path) -> Dict[str, object]:
    try:
        return _load_yaml_dict(path)
    except RuntimeError:
        entries: List[Dict[str, object]] = []
        current: Optional[Dict[str, object]] = None
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped == "reader_archetypes:":
                    continue
                if stripped.startswith("- "):
                    if current:
                        entries.append(current)
                    current = {}
                    stripped = stripped[2:]
                if ":" not in stripped:
                    continue
                key, raw_value = stripped.split(":", 1)
                if current is None:
                    current = {}
                current[key.strip()] = _parse_scalar(raw_value)
        if current:
            entries.append(current)
        return {"reader_archetypes": entries}


@dataclass(frozen=True)
class ReaderArchetypeCatalog:
    """Normalized archetype catalog loaded from YAML."""

    archetypes: List[ReaderArchetype]
    source_path: Path

    def for_book_type(self, book_type: str) -> List[ReaderArchetype]:
        normalized = _normalize_book_type(book_type)
        if normalized == "mixed_unknown":
            return list(self.archetypes)
        return [
            archetype
            for archetype in self.archetypes
            if normalized in archetype.book_type_suitability
        ]


class ReaderArchetypeLoader:
    """Load reader archetypes from config and normalize missing fields."""

    @classmethod
    def from_yaml(cls, path: Optional[Path] = None) -> ReaderArchetypeCatalog:
        source_path = path or DEFAULT_READER_ARCHETYPES_PATH
        raw = _load_reader_archetypes_raw(source_path)
        items = raw.get("reader_archetypes", [])
        if not isinstance(items, list):
            raise ValueError("reader_archetypes.yaml must contain a top-level 'reader_archetypes' list")

        archetypes: List[ReaderArchetype] = []
        for payload in items:
            if not isinstance(payload, dict):
                raise ValueError("Each reader archetype entry must be a mapping")

            archetype_id = str(payload.get("archetype_id", "")).strip()
            display_name = str(payload.get("display_name", "")).strip()
            platform_home = str(payload.get("platform_home", "")).strip().lower()
            review_style = str(payload.get("review_style", "")).strip()
            genre_bias = str(payload.get("genre_bias", "")).strip().lower() or None
            dnf_tendency = str(payload.get("dnf_tendency", "medium")).strip().lower()
            influence_profile = str(payload.get("influence_profile", "medium")).strip().lower()
            friction_triggers = list(payload.get("friction_triggers", []) or [])
            delight_triggers = list(payload.get("delight_triggers", []) or [])

            if not archetype_id or not display_name or not platform_home or not review_style:
                raise ValueError(f"Archetype is missing required fields: {payload}")

            archetypes.append(
                ReaderArchetype(
                    archetype_id=archetype_id,
                    display_name=display_name,
                    platform_home=platform_home,
                    review_style=review_style,
                    cohort=str(payload.get("cohort") or _COHORT_BY_PLATFORM.get(platform_home, platform_home)),
                    favorite_genres=list(payload.get("favorite_genres", []) or _FAVORITE_GENRES_BY_BIAS.get(genre_bias or "", [])),
                    disliked_patterns=list(payload.get("disliked_patterns", []) or friction_triggers),
                    dnf_threshold=float(payload.get("dnf_threshold", _DNF_THRESHOLD_BY_TENDENCY.get(dnf_tendency, 0.6))),
                    controversy_sensitivity=float(payload.get("controversy_sensitivity", _CONTROVERSY_BY_PLATFORM.get(platform_home, 0.5))),
                    rating_bias=float(payload.get("rating_bias", _RATING_BIAS_BY_STYLE.get(review_style, 0.0))),
                    influence_weight=float(payload.get("influence_weight", _INFLUENCE_WEIGHT_BY_PROFILE.get(influence_profile, 0.5))),
                    susceptibility_to_peer_reaction=float(
                        payload.get(
                            "susceptibility_to_peer_reaction",
                            min(0.95, _INFLUENCE_WEIGHT_BY_PROFILE.get(influence_profile, 0.5) + 0.1),
                        )
                    ),
                    quote_sharing_probability=float(
                        payload.get(
                            "quote_sharing_probability",
                            0.75 if "quotable" in " ".join(delight_triggers) else 0.45,
                        )
                    ),
                    evidence_focus=float(payload.get("evidence_focus", _EVIDENCE_FOCUS_BY_STYLE.get(review_style, 0.5))),
                    privacy_constraints=list(
                        payload.get(
                            "privacy_constraints",
                            ["synthetic_persona_only", "simulated_platform_only"],
                        )
                    ),
                    book_type_suitability=list(
                        payload.get(
                            "book_type_suitability",
                            _infer_book_type_suitability(archetype_id, genre_bias, platform_home),
                        )
                    ),
                    selection_weight=float(
                        payload.get(
                            "selection_weight",
                            payload.get(
                                "weight",
                                max(0.5, _INFLUENCE_WEIGHT_BY_PROFILE.get(influence_profile, 0.5)),
                            ),
                        )
                    ),
                    genre_bias=genre_bias,
                    patience_level=str(payload.get("patience_level", "")).strip() or None,
                    dnf_triggers=list(payload.get("dnf_triggers", []) or friction_triggers),
                    delight_triggers=delight_triggers,
                    influence_profile=influence_profile,
                    spoiler_tolerance=str(payload.get("spoiler_tolerance", "")).strip() or None,
                    reaction_tempo=str(payload.get("reaction_tempo", "")).strip() or None,
                    evidence_refs=[f"config:{source_path.name}:{archetype_id}"],
                    confidence=float(payload.get("confidence", 0.8)),
                )
            )

        return ReaderArchetypeCatalog(archetypes=archetypes, source_path=source_path)
