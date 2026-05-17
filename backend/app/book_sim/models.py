"""Typed Swarmbook schemas and models.

The backend mostly uses dataclasses with explicit JSON helpers, so the Swarmbook
models follow that style to stay consistent with Project, Task, and simulation
state objects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, fields, is_dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Type, TypeVar, Union, get_args, get_origin, get_type_hints


T = TypeVar("T", bound="JsonDataclassMixin")


def _now_iso() -> str:
    return datetime.now().isoformat()


def _serialize_value(value: Any) -> Any:
    """Recursively convert dataclass trees into JSON-safe values."""
    if is_dataclass(value):
        return {f.name: _serialize_value(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, dict):
        return {str(key): _serialize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value") and not isinstance(value, (str, bytes, int, float, bool)):
        return value.value
    return value


def _coerce_value(annotation: Any, value: Any) -> Any:
    """Best-effort conversion from plain JSON values back into typed fields."""
    if value is None:
        return None

    if annotation in (Any, object) or annotation is None:
        return value

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (list, List):
        item_type = args[0] if args else Any
        return [_coerce_value(item_type, item) for item in value]

    if origin in (dict, Dict, Mapping):
        value_type = args[1] if len(args) > 1 else Any
        return {key: _coerce_value(value_type, item) for key, item in value.items()}

    if origin is Union:
        non_none_args = [arg for arg in args if arg is not type(None)]
        if not non_none_args:
            return value
        for candidate in non_none_args:
            try:
                return _coerce_value(candidate, value)
            except Exception:
                continue
        return value

    if isinstance(annotation, type):
        if is_dataclass(annotation) and hasattr(annotation, "from_dict"):
            return annotation.from_dict(value)
        if annotation is Path:
            return Path(value)
        if annotation in (str, int, float, bool):
            return annotation(value)

    return value


class JsonDataclassMixin:
    """Shared JSON helpers for Swarmbook dataclasses."""

    def to_dict(self) -> Dict[str, Any]:
        return _serialize_value(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        kwargs: Dict[str, Any] = {}
        field_map = {item.name: item for item in fields(cls)}
        type_hints = get_type_hints(cls)
        for name, item in field_map.items():
            if name not in data:
                continue
            annotation = type_hints.get(name, item.type)
            kwargs[name] = _coerce_value(annotation, data[name])
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls: Type[T], raw_json: str) -> T:
        return cls.from_dict(json.loads(raw_json))


@dataclass
class ManuscriptInput(JsonDataclassMixin):
    """Incoming manuscript payload and ingest metadata."""

    input_id: str
    project_id: str
    title: str
    author_name: Optional[str] = None
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    text: str = ""
    language: Optional[str] = None
    privacy_mode: str = "hybrid_safe"
    draft_id: Optional[str] = None
    version: Optional[str] = None
    chunk_size: int = 500
    chunk_overlap: int = 50
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    created_at: str = field(default_factory=_now_iso)


@dataclass
class BookProject(JsonDataclassMixin):
    """Top-level Swarmbook project state."""

    project_id: str
    name: str
    privacy_mode: str = "hybrid_safe"
    draft_id: Optional[str] = None
    version: Optional[str] = None
    title: Optional[str] = None
    author_name: Optional[str] = None
    manuscript_input: Optional[ManuscriptInput] = None
    source_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)


@dataclass
class BookDNA(JsonDataclassMixin):
    """High-level book identity derived from the manuscript."""

    title: str
    premise: str
    genre: str
    book_type: str = "mixed_unknown"
    subgenre: Optional[str] = None
    tone: Optional[str] = None
    emotional_promise: Optional[str] = None
    narrative_engine: Optional[str] = None
    reading_difficulty: Optional[str] = None
    target_reader: Optional[str] = None
    comparable_titles: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    spoilers_safe_summary: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class ChapterSummary(JsonDataclassMixin):
    """Single chapter summary within a chapter map."""

    chapter_id: str
    chapter_number: int
    title: Optional[str] = None
    summary: str = ""
    purpose: Optional[str] = None
    chapter_function: Optional[str] = None
    pacing: Optional[str] = None
    pacing_note: Optional[str] = None
    key_beats: List[str] = field(default_factory=list)
    emotional_beats: List[str] = field(default_factory=list)
    turning_points: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    likely_reader_friction: List[str] = field(default_factory=list)
    spoiler_notes: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class ChapterMap(JsonDataclassMixin):
    """Chapters and book-level structural pacing summary."""

    book_id: str
    chapters: List[ChapterSummary] = field(default_factory=list)
    total_chapters: int = 0
    pacing_profile: Optional[str] = None
    structural_notes: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class CharacterProfile(JsonDataclassMixin):
    """Single fiction character profile used for reader reaction simulation."""

    character_id: str
    name: str
    role: Optional[str] = None
    motivations: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    arc_summary: Optional[str] = None
    attachment_potential: Optional[float] = None
    reader_friction: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class CharacterMap(JsonDataclassMixin):
    """All characters and relationship summary for the book."""

    book_id: str
    characters: List[CharacterProfile] = field(default_factory=list)
    cast_size: int = 0
    relationship_graph_summary: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class ClaimProfile(JsonDataclassMixin):
    """Single claim or argument unit in nonfiction manuscripts."""

    claim_id: str
    claim_text: str
    support_type: Optional[str] = None
    support_quality: Optional[str] = None
    evidence_strength: Optional[float] = None
    evidence_items: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    promises: List[str] = field(default_factory=list)
    factual_risk_flags: List[str] = field(default_factory=list)
    counterarguments: List[str] = field(default_factory=list)
    reader_trust_sensitivity: Optional[float] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class ClaimMap(JsonDataclassMixin):
    """All claims and argument summary for a nonfiction book."""

    book_id: str
    claims: List[ClaimProfile] = field(default_factory=list)
    thesis_summary: Optional[str] = None
    argument_strength_summary: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class RiskProfile(JsonDataclassMixin):
    """Single risk item inside a risk map."""

    risk_id: str
    risk_type: str
    severity: Optional[str] = None
    description: Optional[str] = None
    affected_segments: List[str] = field(default_factory=list)
    trigger_text: Optional[str] = None
    mitigation_hint: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class RiskMap(JsonDataclassMixin):
    """Reader, market, pacing, and factual risk summary."""

    book_id: str
    risks: List[RiskProfile] = field(default_factory=list)
    risk_summary: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class StyleMap(JsonDataclassMixin):
    """Writing-style summary used for quoteability and positioning."""

    book_id: str
    prose_density: Optional[str] = None
    clarity: Optional[str] = None
    rhythm: Optional[str] = None
    voice_consistency: Optional[str] = None
    quoteability: Optional[str] = None
    accessibility: Optional[str] = None
    style_notes: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class MarketSurface(JsonDataclassMixin):
    """Market-facing packaging and positioning summary."""

    book_id: str
    target_segments: List[str] = field(default_factory=list)
    comp_titles: List[str] = field(default_factory=list)
    positioning_summary: Optional[str] = None
    discoverability_hooks: List[str] = field(default_factory=list)
    packaging_expectations: List[str] = field(default_factory=list)
    promise_gap: Optional[str] = None
    audience_fit: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class EvidencePack(JsonDataclassMixin):
    """Compressed manuscript intelligence bundle used by downstream stages."""

    pack_id: str
    project_id: str
    draft_id: Optional[str] = None
    version: Optional[str] = None
    privacy_mode: str = "hybrid_safe"
    manuscript_input: Optional[ManuscriptInput] = None
    book_dna: Optional[BookDNA] = None
    chapter_map: Optional[ChapterMap] = None
    character_map: Optional[CharacterMap] = None
    claim_map: Optional[ClaimMap] = None
    risk_map: Optional[RiskMap] = None
    style_map: Optional[StyleMap] = None
    market_surface: Optional[MarketSurface] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    generated_at: str = field(default_factory=_now_iso)


@dataclass
class ReaderArchetype(JsonDataclassMixin):
    """Reusable synthetic reader starting point."""

    archetype_id: str
    display_name: str
    platform_home: str
    review_style: str
    cohort: Optional[str] = None
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
    selection_weight: float = 1.0
    genre_bias: Optional[str] = None
    patience_level: Optional[str] = None
    dnf_triggers: List[str] = field(default_factory=list)
    delight_triggers: List[str] = field(default_factory=list)
    influence_profile: Optional[str] = None
    spoiler_tolerance: Optional[str] = None
    reaction_tempo: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None

    def __post_init__(self) -> None:
        if self.cohort is None:
            self.cohort = self.platform_home
        if not self.disliked_patterns and self.dnf_triggers:
            self.disliked_patterns = list(self.dnf_triggers)


@dataclass
class ReaderPersona(JsonDataclassMixin):
    """Expanded reader persona used during simulation."""

    persona_id: str
    archetype_id: str
    display_name: str
    platform_home: str
    review_style: str
    id: Optional[str] = None
    name: Optional[str] = None
    cohort: Optional[str] = None
    platform: Optional[str] = None
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
        if self.id is None:
            self.id = self.persona_id
        if self.name is None:
            self.name = self.display_name
        if self.cohort is None:
            self.cohort = self.platform_home
        if self.platform is None:
            self.platform = self.platform_home
        if not self.favorite_genres and self.reading_preferences:
            self.favorite_genres = list(self.reading_preferences)
        if not self.reading_preferences and self.favorite_genres:
            self.reading_preferences = list(self.favorite_genres)
        if not self.disliked_patterns and self.dnf_triggers:
            self.disliked_patterns = list(self.dnf_triggers)
        if self.influence_score == 0.0 and self.influence_weight:
            self.influence_score = self.influence_weight


@dataclass
class PrivateReaderReaction(JsonDataclassMixin):
    """Private reaction before a reader posts anywhere."""

    reaction_id: str
    simulation_id: str
    persona_id: str
    chapter_id: Optional[str] = None
    rating: Optional[float] = None
    dnf_probability: Optional[float] = None
    sentiment: Optional[str] = None
    attachment_score: Optional[float] = None
    confusion_score: Optional[float] = None
    recommendation_probability: Optional[float] = None
    praise: List[str] = field(default_factory=list)
    friction: List[str] = field(default_factory=list)
    notable_quotes: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class PlatformPost(JsonDataclassMixin):
    """Platform-shaped public reaction emitted by a simulated reader."""

    post_id: str
    simulation_id: str
    persona_id: str
    platform: str
    round_number: int
    title: Optional[str] = None
    body: str = ""
    rating: Optional[float] = None
    hashtags: List[str] = field(default_factory=list)
    shelf_tags: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    engagement_prediction: Optional[float] = None
    sentiment: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class CrossReaction(JsonDataclassMixin):
    """Reaction generated after a reader sees another reader's post."""

    reaction_id: str
    simulation_id: str
    source_post_id: str
    target_post_id: str
    persona_id: str
    platform: str
    reacted_post_ids: List[str] = field(default_factory=list)
    stance_shift: Optional[str] = None
    agree_probability: Optional[float] = None
    disagree_probability: Optional[float] = None
    reply_likelihood: Optional[float] = None
    rating_shift: Optional[float] = None
    recommendation_shift: Optional[float] = None
    sentiment: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class SimulationRun(JsonDataclassMixin):
    """One Swarmbook simulation run."""

    run_id: str
    project_id: str
    graph_id: Optional[str] = None
    privacy_mode: str = "hybrid_safe"
    draft_id: Optional[str] = None
    version: Optional[str] = None
    provider_route: Optional[str] = None
    status: str = "created"
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    total_rounds: int = 0
    current_round: int = 0
    personas_count: int = 0
    reactions_count: int = 0
    posts_count: int = 0
    report_id: Optional[str] = None
    reader_personas: List[ReaderPersona] = field(default_factory=list)
    private_reactions: List[PrivateReaderReaction] = field(default_factory=list)
    platform_posts: List[PlatformPost] = field(default_factory=list)
    cross_reactions: List[CrossReaction] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BookPredictionReport(JsonDataclassMixin):
    """Prediction report for one simulation run or draft."""

    report_id: str
    project_id: str
    simulation_id: Optional[str] = None
    privacy_mode: str = "hybrid_safe"
    draft_id: Optional[str] = None
    version: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    audience_response: Dict[str, Any] = field(default_factory=dict)
    scorecard: Dict[str, Any] = field(default_factory=dict)
    segment_insights: List[Dict[str, Any]] = field(default_factory=list)
    top_risks: List[str] = field(default_factory=list)
    top_strengths: List[str] = field(default_factory=list)
    revision_priorities: List[str] = field(default_factory=list)
    uncertainty_notes: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None


@dataclass
class DraftComparisonReport(JsonDataclassMixin):
    """Comparison between two manuscript versions or drafts."""

    comparison_id: str
    project_id: str
    privacy_mode: str = "hybrid_safe"
    base_draft_id: Optional[str] = None
    base_version: Optional[str] = None
    compare_draft_id: Optional[str] = None
    compare_version: Optional[str] = None
    summary: Optional[str] = None
    delta_scores: Dict[str, Any] = field(default_factory=dict)
    chapter_deltas: List[Dict[str, Any]] = field(default_factory=list)
    character_deltas: List[Dict[str, Any]] = field(default_factory=list)
    claim_deltas: List[Dict[str, Any]] = field(default_factory=list)
    revision_priorities: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
