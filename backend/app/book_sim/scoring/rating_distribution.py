"""Predicted star rating distribution.

What this score measures
------------------------
The likely distribution of star ratings (1-5) that real readers would assign
to the book, summarized as a predicted mean rating.  This is the single most
important aggregate signal in the report -- it answers "will readers like this
book?" in one number.

How it's calculated
-------------------
1. Collect all ratings from simulated reader reactions, each weighted by the
   reaction's confidence score.
2. Compute a weighted mean from the sample ratings (65% weight).
3. Compute six component scores -- comprehension, emotional payoff, prose
   quality, pacing, character attachment, and packaging fit -- each derived
   from evidence-pack attributes and reaction signals.
4. Blend the components via YAML-configured weights into a single "blended"
   score, then convert to a 1-5 scale: ``1.0 + 4.0 * blended``.
5. Combine the sample-based mean (65%) and the component-based estimate (35%)
   for the final predicted mean rating.
6. Build a histogram distribution from the sample ratings, or generate a
   synthetic distribution centered on the predicted mean if no sample exists.

Score range meaning
-------------------
predicted_mean_rating: 1.0 - 5.0 (star scale)
  1.0-2.0  -- Strong negative reception; major revision needed.
  2.0-3.0  -- Below average; significant friction or mismatch.
  3.0-3.5  -- Mixed reception; polarizing or uneven.
  3.5-4.2  -- Positive reception; solid reader satisfaction.
  4.2-5.0  -- Strong positive reception; likely word-of-mouth driver.

The confidence band indicates uncertainty: a wider band means fewer reactions
or higher variance among them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..models import JsonDataclassMixin
from ._shared import (
    ScoringContext,
    confidence_band_from_sample,
    evidence_refs,
    mean,
    scoring_weights,
    weighted_average,
    clamp,
)


@dataclass
class RatingDistributionResult(JsonDataclassMixin):
    """Deterministic star-rating forecast with uncertainty band."""

    predicted_mean_rating: float
    distribution: Dict[str, float] = field(default_factory=dict)
    confidence_band: Dict[str, float | str] = field(default_factory=dict)
    component_scores: Dict[str, float] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def score_rating_distribution(context: ScoringContext) -> RatingDistributionResult:
    """Score the likely rating distribution from simulation outputs."""
    weights = scoring_weights()["rating"]
    private_reactions = list(context.private_reactions)
    ratings = [reaction.rating for reaction in private_reactions if reaction.rating is not None]
    sample_size = len(ratings)
    rating_weights = [max(0.2, reaction.confidence or 0.5) for reaction in private_reactions if reaction.rating is not None]
    base_mean = mean(ratings) if ratings else 3.0
    weighted_mean_rating = base_mean if not ratings else round(sum(
        rating * weight for rating, weight in zip(ratings, rating_weights)
    ) / max(0.0001, sum(rating_weights)), 3)

    components = _component_scores(context)
    blended = weighted_average(components, weights)
    predicted_mean = round(clamp((weighted_mean_rating * 0.65 + (1.0 + 4.0 * blended) * 0.35), 1.0, 5.0), 3)

    distribution = _distribution_from_sample(ratings, predicted_mean)
    variability = 0.0 if not ratings else max(ratings) - min(ratings)
    band = confidence_band_from_sample(predicted_mean, max(1, sample_size), variability / 4.0, "moderate")
    notes = [
        "Deterministic rating estimate derived from private reactions and config weights.",
        "This is descriptive forecasting, not scientific certainty.",
    ]

    return RatingDistributionResult(
        predicted_mean_rating=predicted_mean,
        distribution=distribution,
        confidence_band=band.to_dict(),
        component_scores=components,
        evidence_refs=evidence_refs(
            context.evidence_pack.evidence_refs,
            context.evidence_pack.book_dna.evidence_refs if context.evidence_pack.book_dna else [],
            (reaction.evidence_refs for reaction in private_reactions),
        ),
        notes=notes,
    )


def _component_scores(context: ScoringContext) -> Dict[str, float]:
    private_reactions = list(context.private_reactions)
    evidence_pack = context.evidence_pack
    book_dna = evidence_pack.book_dna
    chapter_map = evidence_pack.chapter_map
    character_map = evidence_pack.character_map
    market_surface = evidence_pack.market_surface
    style_map = evidence_pack.style_map

    ratings = [reaction.rating or 3.0 for reaction in private_reactions]
    attachments = [reaction.attachment_score or 0.0 for reaction in private_reactions]
    confusions = [reaction.confusion_score or 0.0 for reaction in private_reactions]
    praises = sum(len(reaction.praise) for reaction in private_reactions)
    frictions = sum(len(reaction.friction) for reaction in private_reactions)

    comprehension = clamp(1.0 - (mean(confusions) * 0.75 + frictions / max(1, len(private_reactions) * 4)))
    emotional_payoff = clamp((mean(attachments) * 0.7) + (praises / max(1, len(private_reactions) * 3)))
    prose_quality = _style_quality(style_map)
    pacing = _pacing_quality(chapter_map, private_reactions)
    character_attachment = _character_attachment(character_map, private_reactions)
    packaging_fit = _packaging_fit(book_dna, market_surface)

    return {
        "comprehension": round(comprehension, 3),
        "emotional_payoff": round(emotional_payoff, 3),
        "prose_quality": round(prose_quality, 3),
        "pacing": round(pacing, 3),
        "character_attachment": round(character_attachment, 3),
        "packaging_fit": round(packaging_fit, 3),
    }


def _style_quality(style_map) -> float:
    if not style_map:
        return 0.5
    quality = 0.5
    quality += 0.15 if (style_map.clarity or "").lower() == "high" else 0.0
    quality += 0.15 if (style_map.rhythm or "").lower() == "high" else 0.0
    quality += 0.1 if (style_map.quoteability or "").lower() == "high" else 0.0
    quality -= 0.1 if (style_map.accessibility or "").lower() == "low" else 0.0
    return clamp(quality)


def _pacing_quality(chapter_map, private_reactions) -> float:
    if not chapter_map:
        return 0.5
    pacing_scores = []
    for chapter in chapter_map.chapters:
        chapter_score = 0.55
        if chapter.pacing:
            chapter_score += 0.12 if chapter.pacing in {"fast", "balanced"} else -0.12 if chapter.pacing == "slow" else 0.0
        chapter_score -= min(0.18, len(chapter.likely_reader_friction) * 0.04)
        if chapter.chapter_number <= 2:
            chapter_score -= 0.04
        pacing_scores.append(clamp(chapter_score))
    reaction_adjustment = 0.5 - mean([reaction.confusion_score or 0.0 for reaction in private_reactions]) * 0.25
    return clamp(mean(pacing_scores) * 0.75 + reaction_adjustment * 0.25)


def _character_attachment(character_map, private_reactions) -> float:
    if not character_map:
        return 0.45
    attachment = 0.45
    attachment += min(0.25, sum(character.attachment_potential or 0.0 for character in character_map.characters) / max(1, len(character_map.characters)) * 0.3)
    attachment += min(0.12, sum(len(reaction.praise) for reaction in private_reactions) / max(1, len(private_reactions) * 10))
    return clamp(attachment)


def _packaging_fit(book_dna, market_surface) -> float:
    if not book_dna or not market_surface:
        return 0.5
    fit = 0.5
    if book_dna.genre and any(book_dna.genre.lower() in segment.lower() for segment in market_surface.target_segments):
        fit += 0.15
    if market_surface.promise_gap:
        fit -= 0.1
    fit += min(0.15, len(market_surface.discoverability_hooks) * 0.03)
    return clamp(fit)


def _distribution_from_sample(ratings: List[float], predicted_mean: float) -> Dict[str, float]:
    if ratings:
        bins = {star: 0.25 for star in range(1, 6)}
        for rating in ratings:
            star = min(5, max(1, int(round(rating))))
            bins[star] += 1.0
        total = sum(bins.values())
        return {f"{star}_star": round(count / total, 3) for star, count in bins.items()}

    center = int(round(predicted_mean))
    bins = {star: max(0.01, 1.0 - abs(star - center) * 0.3) for star in range(1, 6)}
    total = sum(bins.values())
    return {f"{star}_star": round(count / total, 3) for star, count in bins.items()}
