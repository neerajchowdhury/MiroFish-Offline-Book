"""Review polarization scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..models import JsonDataclassMixin
from ._shared import ScoringContext, clamp, confidence_band_from_sample, evidence_refs, mean, scoring_weights


@dataclass
class PolarizationScoreResult(JsonDataclassMixin):
    """How strongly reader reactions split in either direction."""

    polarization_score: float
    component_scores: Dict[str, float] = field(default_factory=dict)
    confidence_band: Dict[str, float | str] = field(default_factory=dict)
    split_signals: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def score_polarization(context: ScoringContext) -> PolarizationScoreResult:
    """Score the likelihood of sharply divided reader reviews."""
    weights = scoring_weights()["polarization"]
    components = _components(context)
    polarization_score = round(clamp(sum(components[key] * weight for key, weight in weights.items())), 3)
    band = confidence_band_from_sample(polarization_score, max(1, len(context.private_reactions)), max(components.values()) - min(components.values()), "moderate")

    return PolarizationScoreResult(
        polarization_score=polarization_score,
        component_scores=components,
        confidence_band=band.to_dict(),
        split_signals=_split_signals(context),
        evidence_refs=evidence_refs(
            context.evidence_pack.evidence_refs,
            context.evidence_pack.book_dna.evidence_refs if context.evidence_pack.book_dna else [],
            context.evidence_pack.character_map.evidence_refs if context.evidence_pack.character_map else [],
            (reaction.evidence_refs for reaction in context.private_reactions),
            (cross.evidence_refs for cross in context.cross_reactions),
        ),
        notes=["Polarization is a descriptive split signal, not a certainty statement."],
    )


def _components(context: ScoringContext) -> Dict[str, float]:
    private_reactions = list(context.private_reactions)
    evidence_pack = context.evidence_pack
    book_dna = evidence_pack.book_dna

    taste_split = _taste_split(private_reactions)
    ideology_split = _ideology_split(context)
    prose_split = _prose_split(evidence_pack)
    ending_split = _ending_split(evidence_pack)
    genre_expectation_split = _genre_expectation_split(book_dna, evidence_pack)

    return {
        "taste_split": round(taste_split, 3),
        "ideology_split": round(ideology_split, 3),
        "prose_split": round(prose_split, 3),
        "ending_split": round(ending_split, 3),
        "genre_expectation_split": round(genre_expectation_split, 3),
    }


def _split_signals(context: ScoringContext) -> List[str]:
    signals: List[str] = []
    ratings = [reaction.rating or 3.0 for reaction in context.private_reactions]
    if ratings and max(ratings) - min(ratings) >= 1.5:
        signals.append("wide_rating_spread")
    if any(reaction.sentiment == "positive" for reaction in context.private_reactions) and any(
        reaction.sentiment == "negative" for reaction in context.private_reactions
    ):
        signals.append("mixed_sentiment")
    if context.cross_reactions and any(reaction.stance_shift == "more_negative" for reaction in context.cross_reactions):
        signals.append("reaction_backlash")
    return signals


def _taste_split(private_reactions) -> float:
    if not private_reactions:
        return 0.3
    ratings = [reaction.rating or 3.0 for reaction in private_reactions]
    return clamp(0.2 + min(0.5, (max(ratings) - min(ratings)) / 4.0))


def _ideology_split(context: ScoringContext) -> float:
    claim_map = context.evidence_pack.claim_map
    risk_map = context.evidence_pack.risk_map
    score = 0.22
    if claim_map and claim_map.claims:
        score += min(0.2, sum(len(claim.counterarguments) for claim in claim_map.claims) * 0.03)
    if risk_map and risk_map.risks:
        score += min(0.12, sum(1 for risk in risk_map.risks if "ideological" in risk.risk_type.lower()) * 0.06)
    return clamp(score)


def _prose_split(evidence_pack) -> float:
    style_map = evidence_pack.style_map
    score = 0.18
    if style_map and style_map.accessibility == "low":
        score += 0.18
    if style_map and style_map.clarity == "low":
        score += 0.12
    return clamp(score)


def _ending_split(evidence_pack) -> float:
    chapter_map = evidence_pack.chapter_map
    score = 0.16
    if chapter_map and chapter_map.chapters:
        tail = chapter_map.chapters[-3:]
        score += min(0.2, sum(len(chapter.open_questions) for chapter in tail) * 0.04)
        if any(chapter.chapter_function == "ending" for chapter in tail):
            score += 0.08
    return clamp(score)


def _genre_expectation_split(book_dna, evidence_pack) -> float:
    score = 0.22
    if book_dna and book_dna.book_type == "mixed_unknown":
        score += 0.14
    if evidence_pack.market_surface and evidence_pack.market_surface.promise_gap:
        score += 0.16
    return clamp(score)
