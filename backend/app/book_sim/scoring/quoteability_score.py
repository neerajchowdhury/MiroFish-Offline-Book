"""Quoteability scoring.

What this score measures
------------------------
How easily the book yields memorable, reusable lines, scenes, or passages
that readers will quote, screenshot, share on social media, or highlight
in their e-readers.  High quoteability correlates with organic word-of-mouth
and social media virality.

How it's calculated
-------------------
Six component scores are combined via YAML-configured weights:

line_density             -- How "quotable" the prose is based on the style
                            map's quoteability rating and the count of
                            notable quotes extracted by reader reactions.
image_making_language    -- Presence of vivid imagery signaled by tone
                            metadata and high rhythm in the style map.
emotional_clarity        -- Average reader attachment score plus the count
                            of emotional beats mapped across chapters.
repetition_resonance     -- Thematic repetition (number of distinct themes)
                            and turning-point density across chapters.
scene_peak_strength      -- Sum of key beats and turning points across
                            chapters, plus reader praise count.
excerpt_friendly_structure
                         -- Shorter chapter counts (<=20) and presence of
                            a spoilers-safe summary make excerpts easier
                            to extract and share.

Quote candidates are extracted from the book DNA summary, chapter summaries,
and notable quotes in reader reactions, capped at six candidates.

Score range meaning
-------------------
quoteability_score: 0.0 - 1.0
  0.0-0.2  -- Very low; prose is functional but not memorable.
  0.2-0.4  -- Low; occasional quotable lines but not a strength.
  0.4-0.6  -- Moderate; some passages will resonate with readers.
  0.6-0.8  -- High; many shareable lines and scenes.
  0.8-1.0  -- Very high; the book is highly quotable and excerpt-friendly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..models import JsonDataclassMixin
from ._shared import ScoringContext, clamp, confidence_band_from_sample, evidence_refs, mean, scoring_weights


@dataclass
class QuoteabilityScoreResult(JsonDataclassMixin):
    """Reusable quote potential with candidate highlights."""

    quoteability_score: float
    component_scores: Dict[str, float] = field(default_factory=dict)
    confidence_band: Dict[str, float | str] = field(default_factory=dict)
    quote_candidates: List[Dict[str, str]] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def score_quoteability(context: ScoringContext) -> QuoteabilityScoreResult:
    """Score how easily the book yields reusable lines or scenes."""
    weights = scoring_weights()["quoteability"]
    components = _components(context)
    quoteability_score = round(clamp(sum(components[key] * weight for key, weight in weights.items())), 3)
    band = confidence_band_from_sample(quoteability_score, max(1, len(context.platform_posts) + len(context.private_reactions)), max(components.values()) - min(components.values()), "moderate")

    return QuoteabilityScoreResult(
        quoteability_score=quoteability_score,
        component_scores=components,
        confidence_band=band.to_dict(),
        quote_candidates=_quote_candidates(context),
        evidence_refs=evidence_refs(
            context.evidence_pack.evidence_refs,
            context.evidence_pack.book_dna.evidence_refs if context.evidence_pack.book_dna else [],
            context.evidence_pack.style_map.evidence_refs if context.evidence_pack.style_map else [],
            (reaction.evidence_refs for reaction in context.private_reactions),
        ),
        notes=["Quoteability is a descriptive score and should not be treated as certainty."],
    )


def _components(context: ScoringContext) -> Dict[str, float]:
    evidence_pack = context.evidence_pack
    style_map = evidence_pack.style_map
    chapter_map = evidence_pack.chapter_map
    private_reactions = list(context.private_reactions)

    line_density = _line_density(style_map, private_reactions)
    image_making_language = _image_making_language(evidence_pack)
    emotional_clarity = _emotional_clarity(private_reactions, chapter_map)
    repetition_resonance = _repetition_resonance(chapter_map, evidence_pack)
    scene_peak_strength = _scene_peak_strength(chapter_map, private_reactions)
    excerpt_friendly_structure = _excerpt_friendly_structure(evidence_pack)

    return {
        "line_density": round(line_density, 3),
        "image_making_language": round(image_making_language, 3),
        "emotional_clarity": round(emotional_clarity, 3),
        "repetition_resonance": round(repetition_resonance, 3),
        "scene_peak_strength": round(scene_peak_strength, 3),
        "excerpt_friendly_structure": round(excerpt_friendly_structure, 3),
    }


def _quote_candidates(context: ScoringContext) -> List[Dict[str, str]]:
    candidates: List[Dict[str, str]] = []
    book_dna = context.evidence_pack.book_dna
    if book_dna and book_dna.spoilers_safe_summary:
        candidates.append({"text": book_dna.spoilers_safe_summary[:180], "source": "book_dna"})
    if context.evidence_pack.chapter_map:
        for chapter in context.evidence_pack.chapter_map.chapters[:3]:
            if chapter.summary:
                candidates.append({"text": chapter.summary[:180], "source": chapter.chapter_id})
    for reaction in context.private_reactions[:3]:
        for quote in reaction.notable_quotes[:1]:
            candidates.append({"text": quote[:180], "source": reaction.reaction_id})
    return candidates[:6]


def _line_density(style_map, private_reactions) -> float:
    score = 0.32
    if style_map and style_map.quoteability == "high":
        score += 0.28
    score += min(0.15, sum(len(reaction.notable_quotes) for reaction in private_reactions) * 0.03)
    return clamp(score)


def _image_making_language(evidence_pack) -> float:
    score = 0.3
    if evidence_pack.book_dna and evidence_pack.book_dna.tone:
        score += 0.12
    if evidence_pack.style_map and evidence_pack.style_map.rhythm == "high":
        score += 0.12
    return clamp(score)


def _emotional_clarity(private_reactions, chapter_map) -> float:
    score = 0.35
    score += mean([reaction.attachment_score or 0.0 for reaction in private_reactions]) * 0.25
    if chapter_map and chapter_map.chapters:
        score += min(0.12, sum(len(chapter.emotional_beats) for chapter in chapter_map.chapters) * 0.015)
    return clamp(score)


def _repetition_resonance(chapter_map, evidence_pack) -> float:
    score = 0.28
    if evidence_pack.book_dna and evidence_pack.book_dna.themes:
        repeated = len(set(evidence_pack.book_dna.themes))
        score += min(0.12, repeated * 0.03)
    if chapter_map and chapter_map.chapters:
        score += min(0.12, sum(len(chapter.turning_points) for chapter in chapter_map.chapters) * 0.01)
    return clamp(score)


def _scene_peak_strength(chapter_map, private_reactions) -> float:
    score = 0.32
    if chapter_map and chapter_map.chapters:
        score += min(0.18, sum(len(chapter.key_beats) + len(chapter.turning_points) for chapter in chapter_map.chapters) * 0.01)
    score += min(0.12, sum(len(reaction.praise) for reaction in private_reactions) * 0.02)
    return clamp(score)


def _excerpt_friendly_structure(evidence_pack) -> float:
    score = 0.34
    if evidence_pack.chapter_map and evidence_pack.chapter_map.chapters:
        score += 0.12 if len(evidence_pack.chapter_map.chapters) <= 20 else 0.05
    if evidence_pack.book_dna and evidence_pack.book_dna.spoilers_safe_summary:
        score += 0.08
    return clamp(score)
