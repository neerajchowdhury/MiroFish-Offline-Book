"""Deterministic report synthesis for Swarmbook runtime endpoints."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence

from .models import BookPredictionReport, BookProject, EvidencePack, ReaderPersona, SimulationRun
from .scoring import (
    ScoringContext,
    score_controversy,
    score_dnf,
    score_polarization,
    score_quoteability,
    score_rating_distribution,
    score_revision_priority,
    score_viral_potential,
)
from .scoring._shared import stable_digest


def build_prediction_report(
    project: BookProject,
    evidence_pack: EvidencePack,
    simulation_run: SimulationRun,
) -> BookPredictionReport:
    """Build a stable report from existing simulation and scoring outputs."""
    context = ScoringContext(evidence_pack=evidence_pack, simulation_run=simulation_run)
    rating = score_rating_distribution(context)
    dnf = score_dnf(context)
    controversy = score_controversy(context)
    quoteability = score_quoteability(context)
    polarization = score_polarization(context)
    viral = score_viral_potential(context)
    revision = score_revision_priority(context)

    scorecard = {
        "rating_distribution": rating.to_dict(),
        "dnf": dnf.to_dict(),
        "controversy": controversy.to_dict(),
        "quoteability": quoteability.to_dict(),
        "polarization": polarization.to_dict(),
        "viral": viral.to_dict(),
        "revision_priority": revision.to_dict(),
    }
    segment_insights = _segment_insights(simulation_run)
    top_risks = _top_risks(evidence_pack, dnf.chapter_points, controversy.hotspots)
    top_strengths = _top_strengths(evidence_pack, simulation_run, viral.top_platforms, quoteability.quote_candidates)
    revision_priorities = [
        f"{item.item_type}:{item.item_id} ({item.priority_score:.2f})"
        for item in revision.ranked_items[:5]
    ]
    uncertainty_notes = _unique(
        [
            *rating.notes,
            *dnf.notes,
            *controversy.notes,
            *quoteability.notes,
            *polarization.notes,
            *viral.notes,
            "Outputs are synthetic stress-test signals, not a guarantee of market behavior.",
        ]
    )

    report_id = f"report_{stable_digest(project.project_id, simulation_run.run_id, evidence_pack.pack_id)[:12]}"
    return BookPredictionReport(
        report_id=report_id,
        project_id=project.project_id,
        simulation_id=simulation_run.run_id,
        privacy_mode=evidence_pack.privacy_mode,
        draft_id=evidence_pack.draft_id,
        version=evidence_pack.version,
        title=evidence_pack.book_dna.title if evidence_pack.book_dna else project.title or project.name,
        summary=_summary(rating.predicted_mean_rating, dnf.dnf_risk, viral.top_platforms, top_risks),
        audience_response={
            "personas_count": simulation_run.personas_count,
            "posts_count": simulation_run.posts_count,
            "mean_rating": rating.predicted_mean_rating,
            "recommendation_mean": _recommendation_mean(simulation_run),
            "top_platforms": viral.top_platforms,
        },
        scorecard=scorecard,
        segment_insights=segment_insights,
        top_risks=top_risks,
        top_strengths=top_strengths,
        revision_priorities=revision_priorities,
        uncertainty_notes=uncertainty_notes,
        evidence_refs=_unique(
            [
                *evidence_pack.evidence_refs,
                *simulation_run.evidence_refs,
                *rating.evidence_refs,
                *dnf.evidence_refs,
                *controversy.evidence_refs,
                *quoteability.evidence_refs,
                *polarization.evidence_refs,
                *viral.evidence_refs,
                *revision.evidence_refs,
            ]
        ),
        confidence=_confidence(project, evidence_pack, simulation_run),
    )


def _segment_insights(simulation_run: SimulationRun) -> List[Dict[str, Any]]:
    persona_map = {persona.persona_id: persona for persona in simulation_run.reader_personas}
    buckets: Dict[str, Dict[str, Any]] = {}
    for reaction in simulation_run.private_reactions:
        persona = persona_map.get(reaction.persona_id)
        if persona is None:
            continue
        segment = f"{persona.cohort or persona.platform_home}:{persona.platform or persona.platform_home}"
        bucket = buckets.setdefault(
            segment,
            {
                "segment": segment,
                "ratings": [],
                "recommendations": [],
                "sentiments": [],
                "personas": [],
            },
        )
        if reaction.rating is not None:
            bucket["ratings"].append(float(reaction.rating))
        if reaction.recommendation_probability is not None:
            bucket["recommendations"].append(float(reaction.recommendation_probability))
        if reaction.sentiment:
            bucket["sentiments"].append(reaction.sentiment)
        bucket["personas"].append(persona.display_name)

    insights: List[Dict[str, Any]] = []
    for segment, bucket in sorted(buckets.items()):
        ratings = bucket["ratings"]
        recommendations = bucket["recommendations"]
        insights.append(
            {
                "segment": segment,
                "rating_mean": round(sum(ratings) / len(ratings), 3) if ratings else None,
                "recommendation_mean": round(sum(recommendations) / len(recommendations), 3) if recommendations else None,
                "signal": _segment_signal(ratings),
                "sample_personas": _unique(bucket["personas"])[:3],
                "sentiments": _unique(bucket["sentiments"])[:3],
            }
        )
    return insights


def _top_risks(
    evidence_pack: EvidencePack,
    chapter_points: Sequence[Dict[str, Any]],
    hotspots: Sequence[str],
) -> List[str]:
    risks: List[str] = []
    for risk in getattr(evidence_pack.risk_map, "risks", [])[:3]:
        risks.append(risk.description or risk.risk_type)
    for point in chapter_points[:2]:
        section_id = point.get("section_id")
        dnf_points = point.get("dnf_points")
        if section_id and dnf_points is not None:
            risks.append(f"{section_id} carries DNF pressure at {float(dnf_points):.2f}.")
    for hotspot in hotspots[:3]:
        risks.append(f"Controversy hotspot: {hotspot}.")
    return _unique(risks)


def _top_strengths(
    evidence_pack: EvidencePack,
    simulation_run: SimulationRun,
    top_platforms: Sequence[str],
    quote_candidates: Sequence[Dict[str, str]],
) -> List[str]:
    strengths: List[str] = []
    if evidence_pack.book_dna:
        strengths.extend(f"Theme signal: {theme}." for theme in evidence_pack.book_dna.themes[:2])
    for reaction in simulation_run.private_reactions[:3]:
        strengths.extend(f"Reader praise: {item}." for item in reaction.praise[:2])
    strengths.extend(f"Best synthetic platform fit: {platform}." for platform in top_platforms[:2])
    strengths.extend(f"Quote candidate: {item['text'][:90]}." for item in quote_candidates[:2] if item.get("text"))
    return _unique(strengths)


def _summary(
    mean_rating: float,
    dnf_risk: float,
    top_platforms: Sequence[str],
    top_risks: Sequence[str],
) -> str:
    platform_text = ", ".join(top_platforms[:2]) if top_platforms else "no standout platform"
    blocker_text = top_risks[0] if top_risks else "no dominant blocker was detected"
    return (
        f"Predicted mean rating is {mean_rating:.2f} with DNF risk at {dnf_risk:.2f}. "
        f"Best synthetic spread is on {platform_text}, while the main blocker is {blocker_text}"
    )


def _recommendation_mean(simulation_run: SimulationRun) -> float | None:
    values = [
        float(reaction.recommendation_probability)
        for reaction in simulation_run.private_reactions
        if reaction.recommendation_probability is not None
    ]
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def _segment_signal(ratings: Sequence[float]) -> str:
    if not ratings:
        return "unknown"
    mean_rating = sum(ratings) / len(ratings)
    if mean_rating >= 3.8:
        return "positive"
    if mean_rating <= 2.8:
        return "negative"
    return "mixed"


def _confidence(project: BookProject, evidence_pack: EvidencePack, simulation_run: SimulationRun) -> float | None:
    values = [project.confidence, evidence_pack.confidence, simulation_run.confidence]
    scores = [float(value) for value in values if value is not None]
    if not scores:
        return None
    return round(sum(scores) / len(scores), 3)


def _unique(values: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
