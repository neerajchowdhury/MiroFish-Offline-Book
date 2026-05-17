"""Revision priority ranking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..models import JsonDataclassMixin
from ._shared import ScoringContext, clamp, confidence_band_from_sample, evidence_refs, stable_digest


@dataclass
class RevisionPriorityItem(JsonDataclassMixin):
    """Single prioritized revision target."""

    item_id: str
    item_type: str
    priority_score: float
    reasons: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class RevisionPriorityResult(JsonDataclassMixin):
    """Ordered revision targets with a confidence band."""

    ranked_items: List[RevisionPriorityItem] = field(default_factory=list)
    confidence_band: Dict[str, float | str] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def score_revision_priority(context: ScoringContext) -> RevisionPriorityResult:
    """Rank the highest-value revision targets."""
    from .controversy_score import score_controversy
    from .dnf_score import score_dnf
    from .polarization_score import score_polarization
    from .quoteability_score import score_quoteability
    from .rating_distribution import score_rating_distribution
    from .viral_score import score_viral_potential

    rating = score_rating_distribution(context)
    dnf = score_dnf(context)
    viral = score_viral_potential(context)
    controversy = score_controversy(context)
    quoteability = score_quoteability(context)
    polarization = score_polarization(context)

    items: List[RevisionPriorityItem] = []
    items.extend(_chapter_items(context, dnf, rating, controversy, quoteability))
    items.extend(_claim_items(context, controversy, viral, polarization))
    items.extend(_style_items(context, quoteability, rating))
    items.extend(_market_items(context, viral, controversy))
    items.sort(key=lambda item: (item.priority_score, item.item_type, item.item_id), reverse=True)

    if items:
        mid = items[0].priority_score
        spread = min(0.25, max(item.priority_score for item in items) - min(item.priority_score for item in items))
    else:
        mid = 0.0
        spread = 0.08

    return RevisionPriorityResult(
        ranked_items=items,
        confidence_band=confidence_band_from_sample(mid, max(1, len(items)), spread, "moderate").to_dict(),
        evidence_refs=evidence_refs(
            context.evidence_pack.evidence_refs,
            context.evidence_pack.book_dna.evidence_refs if context.evidence_pack.book_dna else [],
            context.evidence_pack.chapter_map.evidence_refs if context.evidence_pack.chapter_map else [],
            context.evidence_pack.claim_map.evidence_refs if context.evidence_pack.claim_map else [],
            context.evidence_pack.risk_map.evidence_refs if context.evidence_pack.risk_map else [],
        ),
        notes=[
            "Revision priority is a deterministic ranking, not a prescriptive editorial verdict.",
        ],
    )


def _chapter_items(context: ScoringContext, dnf, rating, controversy, quoteability) -> List[RevisionPriorityItem]:
    chapter_map = context.evidence_pack.chapter_map
    if not chapter_map:
        return []
    chapter_dnf_points = {item["section_id"]: float(item["dnf_points"]) for item in dnf.chapter_points if isinstance(item.get("section_id"), str)}
    items: List[RevisionPriorityItem] = []
    for chapter in chapter_map.chapters:
        risk = chapter_dnf_points.get(chapter.chapter_id, 0.25)
        low_quote = 1.0 - quoteability.quoteability_score
        priority = clamp(risk * 0.45 + controversy.controversy_risk * 0.2 + low_quote * 0.2 + (1.0 - rating.predicted_mean_rating / 5.0) * 0.15)
        reasons = [
            f"dnf_points={round(risk, 3)}",
            f"quoteability={quoteability.quoteability_score}",
            f"rating={rating.predicted_mean_rating}",
        ]
        if chapter.likely_reader_friction:
            reasons.append(f"friction={','.join(chapter.likely_reader_friction[:2])}")
        items.append(
            RevisionPriorityItem(
                item_id=chapter.chapter_id,
                item_type="chapter",
                priority_score=round(priority, 3),
                reasons=reasons,
                evidence_refs=evidence_refs(chapter.evidence_refs),
            )
        )
    return items


def _claim_items(context: ScoringContext, controversy, viral, polarization) -> List[RevisionPriorityItem]:
    claim_map = context.evidence_pack.claim_map
    if not claim_map:
        return []
    items: List[RevisionPriorityItem] = []
    for claim in claim_map.claims:
        priority = clamp(
            controversy.controversy_risk * 0.35
            + viral.platform_scores.get("reddit", 0.0) * 0.15
            + polarization.polarization_score * 0.3
            + min(0.2, len(claim.factual_risk_flags) * 0.05)
        )
        reasons = [
            f"controversy={controversy.controversy_risk}",
            f"polarization={polarization.polarization_score}",
            f"reddit_viral={viral.platform_scores.get('reddit', 0.0)}",
        ]
        if claim.counterarguments:
            reasons.append(f"counterarguments={','.join(claim.counterarguments[:2])}")
        items.append(
            RevisionPriorityItem(
                item_id=claim.claim_id,
                item_type="claim",
                priority_score=round(priority, 3),
                reasons=reasons,
                evidence_refs=evidence_refs(claim.evidence_refs),
            )
        )
    return items


def _style_items(context: ScoringContext, quoteability, rating) -> List[RevisionPriorityItem]:
    style_map = context.evidence_pack.style_map
    if not style_map:
        return []
    priority = clamp((1.0 - quoteability.quoteability_score) * 0.45 + (1.0 - rating.predicted_mean_rating / 5.0) * 0.25)
    return [
        RevisionPriorityItem(
            item_id=stable_digest(context.evidence_pack.pack_id, "style"),
            item_type="style",
            priority_score=round(priority, 3),
            reasons=[
                f"quoteability={quoteability.quoteability_score}",
                f"rating={rating.predicted_mean_rating}",
                f"clarity={style_map.clarity}",
            ],
            evidence_refs=evidence_refs(style_map.evidence_refs),
        )
    ]


def _market_items(context: ScoringContext, viral, controversy) -> List[RevisionPriorityItem]:
    market_surface = context.evidence_pack.market_surface
    if not market_surface:
        return []
    priority = clamp((1.0 - viral.platform_scores.get("goodreads", 0.0)) * 0.4 + controversy.controversy_risk * 0.3)
    reasons = [
        f"goodreads_viral={viral.platform_scores.get('goodreads', 0.0)}",
        f"controversy={controversy.controversy_risk}",
    ]
    if market_surface.promise_gap:
        reasons.append("promise_gap")
    return [
        RevisionPriorityItem(
            item_id=stable_digest(context.evidence_pack.pack_id, "market"),
            item_type="market",
            priority_score=round(priority, 3),
            reasons=reasons,
            evidence_refs=evidence_refs(market_surface.evidence_refs),
        )
    ]
