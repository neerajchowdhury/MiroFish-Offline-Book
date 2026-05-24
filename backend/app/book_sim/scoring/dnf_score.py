"""DNF (Did Not Finish) risk scoring.

What this score measures
------------------------
The probability that a reader will abandon the book before completing it.
DNF risk is one of the strongest predictors of poor word-of-mouth and low
sales velocity, since readers who don't finish rarely recommend the book.

How it's calculated
-------------------
Six component scores are computed and combined via YAML-configured weights:

opening_drag       -- How likely readers are to drop out in the first two
                      chapters.  Based on early-chapter pacing, friction
                      markers, and reader confusion scores.
confusion          -- Average confusion score across all reader reactions.
                      High confusion correlates strongly with abandonment.
pacing_drag        -- Mean pacing penalty across all chapters.  Slow-paced
                      chapters with friction markers increase drag.
unmet_expectation  -- Gap between what the market surface promises and what
                      the manuscript delivers.  Promise gaps and packaging
                      mismatches drive this component up.
voice_misalignment -- Mismatch between the prose style and reader expectations.
                      Low accessibility and low clarity increase risk.
length_fatigue     -- Simple function of chapter count.  Books with more than
                      12 chapters get a higher baseline fatigue score.

Additionally, detected risks from the risk_map add small penalties to
opening_drag and pacing_drag, acknowledging that identified hazards compound
abandonment pressure.

Chapter-level pressure points are also computed: each chapter receives a
DNF score based on its position (early chapters weighted higher), pacing,
friction markers, and open questions.  These are returned sorted by severity.

Score range meaning
-------------------
dnf_risk: 0.0 - 1.0
  0.0-0.2  -- Very low abandonment risk; strong hook and pacing.
  0.2-0.4  -- Low risk; minor friction points unlikely to cause drop-off.
  0.4-0.6  -- Moderate risk; some readers may abandon mid-book.
  0.6-0.8  -- High risk; significant pacing or clarity issues.
  0.8-1.0  -- Very high risk; likely mass abandonment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..models import JsonDataclassMixin
from ._shared import ScoringContext, clamp, confidence_band_from_sample, evidence_refs, mean, scoring_weights, weighted_sum


@dataclass
class DNFScoreResult(JsonDataclassMixin):
    """Deterministic DNF risk output."""

    dnf_risk: float
    confidence_band: Dict[str, float | str] = field(default_factory=dict)
    component_scores: Dict[str, float] = field(default_factory=dict)
    chapter_points: List[Dict[str, float | str]] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def score_dnf(context: ScoringContext) -> DNFScoreResult:
    """Score abandonment risk and chapter-level pressure points."""
    weights = scoring_weights()["dnf_risk"]
    components = _component_scores(context)
    dnf_risk = round(clamp(weighted_sum(components, weights)), 3)
    chapter_points = _chapter_points(context, dnf_risk)
    variability = max(components.values()) - min(components.values()) if components else 0.0
    band = confidence_band_from_sample(dnf_risk, max(1, len(context.private_reactions)), variability, "moderate")

    return DNFScoreResult(
        dnf_risk=dnf_risk,
        confidence_band=band.to_dict(),
        component_scores=components,
        chapter_points=chapter_points,
        evidence_refs=evidence_refs(
            context.evidence_pack.evidence_refs,
            context.evidence_pack.risk_map.evidence_refs if context.evidence_pack.risk_map else [],
            (risk.evidence_refs for risk in context.evidence_pack.risk_map.risks) if context.evidence_pack.risk_map else [],
        ),
        notes=[
            "Chapter points are descriptive hotspots, not predictive certainty.",
            "Scores are deterministic and derived from the evidence pack plus private reactions.",
        ],
    )


def _component_scores(context: ScoringContext) -> Dict[str, float]:
    chapter_map = context.evidence_pack.chapter_map
    private_reactions = list(context.private_reactions)
    risk_map = context.evidence_pack.risk_map
    style_map = context.evidence_pack.style_map
    market_surface = context.evidence_pack.market_surface

    opening_drag = _opening_drag(chapter_map, private_reactions)
    confusion = clamp(mean([reaction.confusion_score or 0.0 for reaction in private_reactions]))
    pacing_drag = _pacing_drag(chapter_map)
    unmet_expectation = _unmet_expectation(market_surface, private_reactions)
    voice_misalignment = _voice_misalignment(style_map, private_reactions)
    length_fatigue = _length_fatigue(chapter_map)
    if risk_map and risk_map.risks:
        opening_drag = clamp(opening_drag + min(0.12, len(risk_map.risks) * 0.03))
        pacing_drag = clamp(pacing_drag + min(0.1, len(risk_map.risks) * 0.02))

    return {
        "opening_drag": round(opening_drag, 3),
        "confusion": round(confusion, 3),
        "pacing_drag": round(pacing_drag, 3),
        "unmet_expectation": round(unmet_expectation, 3),
        "voice_misalignment": round(voice_misalignment, 3),
        "length_fatigue": round(length_fatigue, 3),
    }


def _chapter_points(context: ScoringContext, dnf_risk: float) -> List[Dict[str, float | str]]:
    chapter_map = context.evidence_pack.chapter_map
    if not chapter_map:
        return [{"section_id": "book", "dnf_points": round(dnf_risk, 3), "reason": "No chapter map available."}]
    points: List[Dict[str, float | str]] = []
    for chapter in chapter_map.chapters:
        base = 0.25 + (0.1 if chapter.chapter_number <= 2 else 0.0)
        base += min(0.2, len(chapter.likely_reader_friction) * 0.04)
        if chapter.pacing == "slow":
            base += 0.12
        if chapter.pacing == "fast":
            base -= 0.04
        if chapter.open_questions:
            base += min(0.08, len(chapter.open_questions) * 0.02)
        points.append(
            {
                "section_id": chapter.chapter_id,
                "chapter_number": chapter.chapter_number,
                "dnf_points": round(clamp(base), 3),
                "reason": _chapter_reason(chapter.chapter_number, chapter.pacing, chapter.likely_reader_friction),
            }
        )
    points.sort(key=lambda item: (item["dnf_points"], -int(item["chapter_number"])), reverse=True)
    return points


def _chapter_reason(chapter_number: int, pacing: str | None, friction: List[str]) -> str:
    reasons = [f"chapter {chapter_number}"]
    if pacing:
        reasons.append(f"pacing={pacing}")
    if friction:
        reasons.append(f"friction={','.join(friction[:2])}")
    return "; ".join(reasons)


def _opening_drag(chapter_map, private_reactions) -> float:
    if not chapter_map or not chapter_map.chapters:
        return 0.35
    first_chapters = chapter_map.chapters[:2]
    score = 0.25
    for chapter in first_chapters:
        score += 0.1 if chapter.pacing == "slow" else 0.02
        score += min(0.08, len(chapter.likely_reader_friction) * 0.03)
    score += mean([reaction.confusion_score or 0.0 for reaction in private_reactions]) * 0.2
    return clamp(score)


def _pacing_drag(chapter_map) -> float:
    if not chapter_map or not chapter_map.chapters:
        return 0.3
    scores = []
    for chapter in chapter_map.chapters:
        value = 0.2
        if chapter.pacing == "slow":
            value += 0.2
        elif chapter.pacing == "balanced":
            value += 0.05
        elif chapter.pacing == "fast":
            value -= 0.05
        value += min(0.08, len(chapter.likely_reader_friction) * 0.02)
        scores.append(clamp(value))
    return clamp(mean(scores))


def _unmet_expectation(market_surface, private_reactions) -> float:
    if not market_surface:
        return 0.35
    score = 0.25
    if market_surface.promise_gap:
        score += 0.18
    if market_surface.packaging_expectations:
        score += min(0.1, len(market_surface.packaging_expectations) * 0.02)
    score += min(0.12, sum(len(reaction.friction) for reaction in private_reactions) / max(1, len(private_reactions) * 10))
    return clamp(score)


def _voice_misalignment(style_map, private_reactions) -> float:
    if not style_map:
        return 0.25
    score = 0.2
    if style_map.accessibility == "low":
        score += 0.18
    if style_map.clarity == "low":
        score += 0.12
    score += min(0.08, sum(reaction.confusion_score or 0.0 for reaction in private_reactions) / max(1, len(private_reactions) * 6))
    return clamp(score)


def _length_fatigue(chapter_map) -> float:
    if not chapter_map:
        return 0.2
    count = len(chapter_map.chapters)
    if count <= 4:
        return 0.12
    if count <= 12:
        return 0.25
    return 0.38
