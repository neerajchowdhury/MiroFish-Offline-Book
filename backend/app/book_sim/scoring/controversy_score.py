"""Controversy radar scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..models import JsonDataclassMixin
from ._shared import ScoringContext, clamp, confidence_band_from_sample, evidence_refs, mean, scoring_weights, weighted_sum


@dataclass
class ControversyScoreResult(JsonDataclassMixin):
    """Controversy radar with component breakdown."""

    controversy_risk: float
    radar: Dict[str, float] = field(default_factory=dict)
    confidence_band: Dict[str, float | str] = field(default_factory=dict)
    hotspots: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def score_controversy(context: ScoringContext) -> ControversyScoreResult:
    """Score ideological and moral backlash risk."""
    weights = scoring_weights()["controversy_risk"]
    radar = _radar(context)
    controversy_risk = round(clamp(weighted_sum(radar, weights)), 3)
    variability = max(radar.values()) - min(radar.values()) if radar else 0.0
    band = confidence_band_from_sample(controversy_risk, max(1, len(context.cross_reactions) or len(context.private_reactions)), variability, "moderate")
    hotspots = _hotspots(context, radar)

    return ControversyScoreResult(
        controversy_risk=controversy_risk,
        radar=radar,
        confidence_band=band.to_dict(),
        hotspots=hotspots,
        evidence_refs=evidence_refs(
            context.evidence_pack.evidence_refs,
            context.evidence_pack.claim_map.evidence_refs if context.evidence_pack.claim_map else [],
            context.evidence_pack.risk_map.evidence_refs if context.evidence_pack.risk_map else [],
            (claim.evidence_refs for claim in context.evidence_pack.claim_map.claims) if context.evidence_pack.claim_map else [],
            (risk.evidence_refs for risk in context.evidence_pack.risk_map.risks) if context.evidence_pack.risk_map else [],
        ),
        notes=["Controversy is a descriptive radar, not a scientific certainty."],
    )


def _radar(context: ScoringContext) -> Dict[str, float]:
    evidence_pack = context.evidence_pack
    claim_map = evidence_pack.claim_map
    risk_map = evidence_pack.risk_map
    market_surface = evidence_pack.market_surface
    private_reactions = list(context.private_reactions)
    cross_reactions = list(context.cross_reactions)

    ideological_tension = _ideological_tension(claim_map, private_reactions, cross_reactions)
    claim_hazard = _claim_hazard(claim_map, risk_map)
    moral_disagreement = _moral_disagreement(risk_map, cross_reactions)
    tonal_disruption = _tonal_disruption(evidence_pack.style_map, private_reactions)
    character_behavior_challenge = _character_behavior_challenge(evidence_pack.character_map, private_reactions)
    packaging_mismatch = _packaging_mismatch(market_surface, evidence_pack.book_dna)

    return {
        "ideological_tension": round(ideological_tension, 3),
        "claim_hazard": round(claim_hazard, 3),
        "moral_disagreement": round(moral_disagreement, 3),
        "tonal_disruption": round(tonal_disruption, 3),
        "character_behavior_challenge": round(character_behavior_challenge, 3),
        "packaging_mismatch": round(packaging_mismatch, 3),
    }


def _hotspots(context: ScoringContext, radar: Dict[str, float]) -> List[str]:
    evidence_pack = context.evidence_pack
    hotspots: List[str] = []
    if evidence_pack.claim_map:
        for claim in evidence_pack.claim_map.claims:
            if claim.factual_risk_flags or claim.counterarguments:
                hotspots.append(f"claim:{claim.claim_id}")
    if evidence_pack.risk_map:
        for risk in evidence_pack.risk_map.risks:
            if risk.risk_type in {"moral_disagreement", "ideological_tension", "packaging_mismatch"}:
                hotspots.append(f"risk:{risk.risk_id}")
    if radar["packaging_mismatch"] >= 0.55:
        hotspots.append("packaging:audience_expectation_gap")
    return hotspots[:8]


def _ideological_tension(claim_map, private_reactions, cross_reactions) -> float:
    score = 0.22
    if claim_map and claim_map.claims:
        score += min(0.28, len(claim_map.claims) * 0.03)
        score += min(0.12, sum(len(claim.counterarguments) for claim in claim_map.claims) * 0.02)
    score += mean([abs(reaction.rating_shift or 0.0) for reaction in cross_reactions]) * 0.4 if cross_reactions else 0.0
    score += mean([reaction.confusion_score or 0.0 for reaction in private_reactions]) * 0.15
    return clamp(score)


def _claim_hazard(claim_map, risk_map) -> float:
    score = 0.18
    if claim_map and claim_map.claims:
        score += min(0.3, sum(claim.evidence_strength or 0.0 for claim in claim_map.claims) / max(1, len(claim_map.claims)) * 0.08)
        score += min(0.18, sum(len(claim.factual_risk_flags) for claim in claim_map.claims) * 0.03)
    if risk_map and risk_map.risks:
        score += min(0.16, len(risk_map.risks) * 0.02)
    return clamp(score)


def _moral_disagreement(risk_map, cross_reactions) -> float:
    score = 0.2
    if risk_map and risk_map.risks:
        score += min(0.25, sum(1 for risk in risk_map.risks if "moral" in risk.risk_type.lower()) * 0.08)
    score += min(0.15, sum(1 for reaction in cross_reactions if reaction.stance_shift == "more_negative") * 0.02)
    return clamp(score)


def _tonal_disruption(style_map, private_reactions) -> float:
    score = 0.18
    if style_map and style_map.accessibility == "low":
        score += 0.15
    if style_map and style_map.clarity == "low":
        score += 0.08
    score += min(0.1, mean([reaction.confusion_score or 0.0 for reaction in private_reactions]) * 0.2)
    return clamp(score)


def _character_behavior_challenge(character_map, private_reactions) -> float:
    score = 0.18
    if character_map and character_map.characters:
        score += min(0.18, sum(len(character.conflicts) + len(character.contradictions) for character in character_map.characters) * 0.02)
    score += min(0.12, sum(len(reaction.friction) for reaction in private_reactions) / max(1, len(private_reactions) * 12))
    return clamp(score)


def _packaging_mismatch(market_surface, book_dna) -> float:
    score = 0.18
    if market_surface and market_surface.promise_gap:
        score += 0.22
    if market_surface and market_surface.packaging_expectations:
        score += min(0.12, len(market_surface.packaging_expectations) * 0.02)
    if book_dna and book_dna.genre and market_surface and market_surface.target_segments:
        score += 0.05 if not any(book_dna.genre.lower() in segment.lower() for segment in market_surface.target_segments) else 0.0
    return clamp(score)
