"""Deterministic draft comparison for Swarmbook evidence, simulations, and scores."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..models import (
    ChapterSummary,
    ClaimProfile,
    DraftComparisonReport,
    EvidencePack,
    ReaderPersona,
    SimulationRun,
)
from ..scoring import (
    ScoringContext,
    score_controversy,
    score_dnf,
    score_quoteability,
    score_rating_distribution,
    score_revision_priority,
    score_viral_potential,
)
from ..scoring._shared import stable_digest
from .comparison_report import DraftComparisonExport, render_comparison_markdown


class DraftComparator:
    """Compare two drafts using available evidence packs, simulations, and scores."""

    def compare(
        self,
        project_id: str,
        base_evidence_pack: EvidencePack,
        compare_evidence_pack: EvidencePack,
        base_simulation_run: Optional[SimulationRun] = None,
        compare_simulation_run: Optional[SimulationRun] = None,
        base_scores: Optional[Dict[str, Any]] = None,
        compare_scores: Optional[Dict[str, Any]] = None,
        simulation_seed: Optional[int] = None,
    ) -> DraftComparisonExport:
        resolved_seed = self._resolved_seed(base_simulation_run, compare_simulation_run, simulation_seed)
        base_scorecard = self._scorecard(base_evidence_pack, base_simulation_run, base_scores)
        compare_scorecard = self._scorecard(compare_evidence_pack, compare_simulation_run, compare_scores)

        report = DraftComparisonReport(
            comparison_id=self._comparison_id(
                project_id,
                base_evidence_pack,
                compare_evidence_pack,
                resolved_seed,
            ),
            project_id=project_id,
            privacy_mode=compare_evidence_pack.privacy_mode or base_evidence_pack.privacy_mode,
            base_draft_id=base_evidence_pack.draft_id,
            base_version=base_evidence_pack.version,
            compare_draft_id=compare_evidence_pack.draft_id,
            compare_version=compare_evidence_pack.version,
            summary="",
            base_scores=base_scorecard,
            compare_scores=compare_scorecard,
            delta_scores=self._delta_scores(base_scorecard, compare_scorecard),
            book_dna_changes=self._book_dna_changes(base_evidence_pack, compare_evidence_pack),
            chapter_deltas=self._chapter_deltas(base_evidence_pack, compare_evidence_pack),
            character_deltas=self._character_deltas(base_evidence_pack, compare_evidence_pack),
            claim_deltas=self._claim_deltas(base_evidence_pack, compare_evidence_pack),
            reader_segment_movement=self._reader_segment_movement(
                base_evidence_pack,
                compare_evidence_pack,
                base_simulation_run,
                compare_simulation_run,
            ),
            revision_impact_summary=[],
            revision_priorities=[],
            what_improved=[],
            what_got_worse=[],
            still_blocking=[],
            evidence_refs=self._evidence_refs(base_evidence_pack, compare_evidence_pack, base_scorecard, compare_scorecard),
            confidence=self._confidence(base_evidence_pack, compare_evidence_pack, base_simulation_run, compare_simulation_run),
            metadata={
                "simulation_seed": resolved_seed,
                "used_base_simulation": base_simulation_run is not None,
                "used_compare_simulation": compare_simulation_run is not None,
            },
        )
        report.what_improved = self._what_improved(report)
        report.what_got_worse = self._what_got_worse(report)
        report.still_blocking = self._still_blocking(compare_evidence_pack, compare_scorecard)
        report.revision_impact_summary = self._revision_impact_summary(report)
        report.revision_priorities = self._revision_priorities(report)
        report.summary = self._summary(report)
        markdown = render_comparison_markdown(report)
        return DraftComparisonExport(report=report, markdown=markdown)

    def _resolved_seed(
        self,
        base_simulation_run: Optional[SimulationRun],
        compare_simulation_run: Optional[SimulationRun],
        explicit_seed: Optional[int],
    ) -> Optional[int]:
        if explicit_seed is not None:
            return int(explicit_seed)
        seeds: List[int] = []
        for run in (base_simulation_run, compare_simulation_run):
            if not run:
                continue
            value = run.metadata.get("seed") if isinstance(run.metadata, dict) else None
            if isinstance(value, int):
                seeds.append(value)
        if not seeds:
            return None
        return seeds[0] if len(set(seeds)) == 1 else min(seeds)

    def _comparison_id(
        self,
        project_id: str,
        base_evidence_pack: EvidencePack,
        compare_evidence_pack: EvidencePack,
        simulation_seed: Optional[int],
    ) -> str:
        digest = stable_digest(
            project_id,
            base_evidence_pack.pack_id,
            compare_evidence_pack.pack_id,
            base_evidence_pack.draft_id,
            compare_evidence_pack.draft_id,
            base_evidence_pack.version,
            compare_evidence_pack.version,
            simulation_seed,
        )
        return f"cmp_{digest[:12]}"

    def _scorecard(
        self,
        evidence_pack: EvidencePack,
        simulation_run: Optional[SimulationRun],
        provided_scores: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        scorecard = dict(provided_scores or {})
        if simulation_run is None:
            return scorecard

        context = ScoringContext(evidence_pack=evidence_pack, simulation_run=simulation_run)
        rating = score_rating_distribution(context)
        dnf = score_dnf(context)
        controversy = score_controversy(context)
        quoteability = score_quoteability(context)
        viral = score_viral_potential(context)
        revision = score_revision_priority(context)

        computed = {
            "rating_mean": rating.predicted_mean_rating,
            "rating_distribution": dict(rating.distribution),
            "dnf_risk": dnf.dnf_risk,
            "dnf_chapter_points": list(dnf.chapter_points),
            "controversy_risk": controversy.controversy_risk,
            "controversy_hotspots": list(controversy.hotspots),
            "quoteability_score": quoteability.quoteability_score,
            "quote_candidates": list(quoteability.quote_candidates),
            "viral_mean": self._mean(list(viral.platform_scores.values())),
            "viral_platform_scores": dict(viral.platform_scores),
            "top_platforms": list(viral.top_platforms),
            "revision_priority_items": [item.to_dict() for item in revision.ranked_items[:5]],
            "reader_segments": self._reader_segments(simulation_run),
        }
        computed.update(scorecard)
        return computed

    def _delta_scores(self, base_scores: Dict[str, Any], compare_scores: Dict[str, Any]) -> Dict[str, Any]:
        deltas: Dict[str, Any] = {}
        deltas["rating_mean"] = self._movement(base_scores.get("rating_mean"), compare_scores.get("rating_mean"))
        deltas["rating_distribution"] = self._distribution_delta(
            base_scores.get("rating_distribution"),
            compare_scores.get("rating_distribution"),
        )
        deltas["dnf_risk"] = self._movement(base_scores.get("dnf_risk"), compare_scores.get("dnf_risk"))
        deltas["controversy_risk"] = self._movement(base_scores.get("controversy_risk"), compare_scores.get("controversy_risk"))
        deltas["quoteability_score"] = self._movement(base_scores.get("quoteability_score"), compare_scores.get("quoteability_score"))
        deltas["viral_mean"] = self._movement(base_scores.get("viral_mean"), compare_scores.get("viral_mean"))
        deltas["viral_platform_scores"] = self._distribution_delta(
            base_scores.get("viral_platform_scores"),
            compare_scores.get("viral_platform_scores"),
        )
        return {key: value for key, value in deltas.items() if value not in ({}, {"from": None, "to": None, "delta": None})}

    def _movement(self, base_value: Any, compare_value: Any) -> Dict[str, Optional[float]]:
        base_number = self._as_float(base_value)
        compare_number = self._as_float(compare_value)
        if base_number is None and compare_number is None:
            return {"from": None, "to": None, "delta": None}
        if base_number is None or compare_number is None:
            return {
                "from": base_number,
                "to": compare_number,
                "delta": None,
            }
        return {
            "from": round(base_number, 3),
            "to": round(compare_number, 3),
            "delta": round(compare_number - base_number, 3),
        }

    def _distribution_delta(self, base_map: Any, compare_map: Any) -> Dict[str, float]:
        if not isinstance(base_map, dict) and not isinstance(compare_map, dict):
            return {}
        keys = sorted(set((base_map or {}).keys()) | set((compare_map or {}).keys()))
        return {
            key: round(self._as_float((compare_map or {}).get(key), 0.0) - self._as_float((base_map or {}).get(key), 0.0), 3)
            for key in keys
        }

    def _book_dna_changes(self, base_pack: EvidencePack, compare_pack: EvidencePack) -> List[Dict[str, Any]]:
        base = base_pack.book_dna
        compare = compare_pack.book_dna
        if not base and not compare:
            return []
        changes: List[Dict[str, Any]] = []
        scalar_fields = [
            "premise",
            "genre",
            "subgenre",
            "tone",
            "emotional_promise",
            "narrative_engine",
            "reading_difficulty",
            "target_reader",
        ]
        for field_name in scalar_fields:
            base_value = getattr(base, field_name, None) if base else None
            compare_value = getattr(compare, field_name, None) if compare else None
            if base_value == compare_value:
                continue
            changes.append({
                "field": field_name,
                "from": base_value,
                "to": compare_value,
            })
        changes.extend(self._list_change("themes", getattr(base, "themes", []), getattr(compare, "themes", [])))
        changes.extend(self._list_change("comparable_titles", getattr(base, "comparable_titles", []), getattr(compare, "comparable_titles", [])))
        return changes

    def _chapter_deltas(self, base_pack: EvidencePack, compare_pack: EvidencePack) -> List[Dict[str, Any]]:
        base_map = self._chapter_index(base_pack)
        compare_map = self._chapter_index(compare_pack)
        chapter_keys = sorted(set(base_map) | set(compare_map), key=lambda item: (item[0], item[1]))
        deltas: List[Dict[str, Any]] = []
        for key in chapter_keys:
            base_chapter = base_map.get(key)
            compare_chapter = compare_map.get(key)
            if base_chapter is None:
                deltas.append({
                    "chapter_id": compare_chapter.chapter_id,
                    "chapter_number": compare_chapter.chapter_number,
                    "change_type": "added",
                    "title": compare_chapter.title,
                })
                continue
            if compare_chapter is None:
                deltas.append({
                    "chapter_id": base_chapter.chapter_id,
                    "chapter_number": base_chapter.chapter_number,
                    "change_type": "removed",
                    "title": base_chapter.title,
                })
                continue
            if self._chapter_signature(base_chapter) == self._chapter_signature(compare_chapter):
                continue
            deltas.append({
                "chapter_id": compare_chapter.chapter_id,
                "chapter_number": compare_chapter.chapter_number,
                "change_type": "modified",
                "pacing_from": base_chapter.pacing,
                "pacing_to": compare_chapter.pacing,
                "friction_from": list(base_chapter.likely_reader_friction[:2]),
                "friction_to": list(compare_chapter.likely_reader_friction[:2]),
                "summary_shift": self._text_shift(base_chapter.summary, compare_chapter.summary),
            })
        return deltas

    def _character_deltas(self, base_pack: EvidencePack, compare_pack: EvidencePack) -> List[Dict[str, Any]]:
        base_map = self._named_profile_map(getattr(base_pack.character_map, "characters", []), "character_id", "name")
        compare_map = self._named_profile_map(getattr(compare_pack.character_map, "characters", []), "character_id", "name")
        deltas: List[Dict[str, Any]] = []
        for key in sorted(set(base_map) | set(compare_map)):
            base_item = base_map.get(key)
            compare_item = compare_map.get(key)
            if base_item is None:
                deltas.append({"character_id": compare_item.character_id, "change_type": "added", "name": compare_item.name})
                continue
            if compare_item is None:
                deltas.append({"character_id": base_item.character_id, "change_type": "removed", "name": base_item.name})
                continue
            attachment_delta = self._delta_value(base_item.attachment_potential, compare_item.attachment_potential)
            if attachment_delta is None and base_item.role == compare_item.role and base_item.reader_friction == compare_item.reader_friction:
                continue
            deltas.append({
                "character_id": compare_item.character_id,
                "change_type": "modified",
                "name": compare_item.name,
                "role_from": base_item.role,
                "role_to": compare_item.role,
                "attachment_delta": attachment_delta,
                "friction_from": list(base_item.reader_friction[:2]),
                "friction_to": list(compare_item.reader_friction[:2]),
            })
        return deltas

    def _claim_deltas(self, base_pack: EvidencePack, compare_pack: EvidencePack) -> List[Dict[str, Any]]:
        base_map = self._named_profile_map(getattr(base_pack.claim_map, "claims", []), "claim_id", "claim_text")
        compare_map = self._named_profile_map(getattr(compare_pack.claim_map, "claims", []), "claim_id", "claim_text")
        deltas: List[Dict[str, Any]] = []
        for key in sorted(set(base_map) | set(compare_map)):
            base_item = base_map.get(key)
            compare_item = compare_map.get(key)
            if base_item is None:
                deltas.append({"claim_id": compare_item.claim_id, "change_type": "added", "claim_text": compare_item.claim_text[:80]})
                continue
            if compare_item is None:
                deltas.append({"claim_id": base_item.claim_id, "change_type": "removed", "claim_text": base_item.claim_text[:80]})
                continue
            evidence_delta = self._delta_value(base_item.evidence_strength, compare_item.evidence_strength)
            if evidence_delta is None and base_item.factual_risk_flags == compare_item.factual_risk_flags and base_item.counterarguments == compare_item.counterarguments:
                continue
            deltas.append({
                "claim_id": compare_item.claim_id,
                "change_type": "modified",
                "claim_text": compare_item.claim_text[:80],
                "evidence_strength_delta": evidence_delta,
                "risk_flags_from": list(base_item.factual_risk_flags[:2]),
                "risk_flags_to": list(compare_item.factual_risk_flags[:2]),
                "counterarguments_from": list(base_item.counterarguments[:2]),
                "counterarguments_to": list(compare_item.counterarguments[:2]),
            })
        return deltas

    def _reader_segment_movement(
        self,
        base_pack: EvidencePack,
        compare_pack: EvidencePack,
        base_run: Optional[SimulationRun],
        compare_run: Optional[SimulationRun],
    ) -> List[Dict[str, Any]]:
        if base_run and compare_run:
            base_segments = {item["segment"]: item for item in self._reader_segments(base_run)}
            compare_segments = {item["segment"]: item for item in self._reader_segments(compare_run)}
            movements: List[Dict[str, Any]] = []
            for segment in sorted(set(base_segments) | set(compare_segments)):
                base_item = base_segments.get(segment, {})
                compare_item = compare_segments.get(segment, {})
                movements.append({
                    "segment": segment,
                    "rating_delta": self._delta_value(base_item.get("rating_mean"), compare_item.get("rating_mean")),
                    "recommendation_delta": self._delta_value(
                        base_item.get("recommendation_mean"),
                        compare_item.get("recommendation_mean"),
                    ),
                    "from_signal": base_item.get("signal"),
                    "to_signal": compare_item.get("signal"),
                })
            return movements
        return self._market_segment_movement(base_pack, compare_pack)

    def _market_segment_movement(self, base_pack: EvidencePack, compare_pack: EvidencePack) -> List[Dict[str, Any]]:
        base_segments = set(getattr(base_pack.market_surface, "target_segments", []) or [])
        compare_segments = set(getattr(compare_pack.market_surface, "target_segments", []) or [])
        movement: List[Dict[str, Any]] = []
        for segment in sorted(compare_segments - base_segments):
            movement.append({"segment": segment, "change_type": "added"})
        for segment in sorted(base_segments - compare_segments):
            movement.append({"segment": segment, "change_type": "removed"})
        for segment in sorted(base_segments & compare_segments):
            movement.append({"segment": segment, "change_type": "retained"})
        return movement

    def _reader_segments(self, simulation_run: SimulationRun) -> List[Dict[str, Any]]:
        persona_map = {persona.persona_id: persona for persona in simulation_run.reader_personas}
        buckets: Dict[str, Dict[str, List[float] | str]] = {}
        for reaction in simulation_run.private_reactions:
            persona = persona_map.get(reaction.persona_id)
            if persona is None:
                continue
            segment = f"{persona.cohort or persona.platform_home}:{persona.platform or persona.platform_home}"
            bucket = buckets.setdefault(
                segment,
                {"segment": segment, "ratings": [], "recommendations": []},
            )
            if reaction.rating is not None:
                bucket["ratings"].append(float(reaction.rating))
            if reaction.recommendation_probability is not None:
                bucket["recommendations"].append(float(reaction.recommendation_probability))
        segments: List[Dict[str, Any]] = []
        for segment in sorted(buckets):
            bucket = buckets[segment]
            rating_mean = self._mean(bucket["ratings"])
            recommendation_mean = self._mean(bucket["recommendations"])
            signal = "positive" if rating_mean >= 3.8 else "negative" if rating_mean <= 2.8 else "mixed"
            segments.append({
                "segment": segment,
                "rating_mean": round(rating_mean, 3) if bucket["ratings"] else None,
                "recommendation_mean": round(recommendation_mean, 3) if bucket["recommendations"] else None,
                "signal": signal,
            })
        return segments

    def _what_improved(self, report: DraftComparisonReport) -> List[str]:
        improvements: List[str] = []
        rating_delta = self._delta_from_movement(report.delta_scores.get("rating_mean"))
        if rating_delta is not None and rating_delta > 0.05:
            improvements.append(f"Predicted rating improved by {rating_delta:.2f}.")
        dnf_delta = self._delta_from_movement(report.delta_scores.get("dnf_risk"))
        if dnf_delta is not None and dnf_delta < -0.03:
            improvements.append(f"DNF risk dropped by {abs(dnf_delta):.2f}.")
        controversy_delta = self._delta_from_movement(report.delta_scores.get("controversy_risk"))
        if controversy_delta is not None and controversy_delta < -0.03:
            improvements.append(f"Controversy risk eased by {abs(controversy_delta):.2f}.")
        quote_delta = self._delta_from_movement(report.delta_scores.get("quoteability_score"))
        if quote_delta is not None and quote_delta > 0.03:
            improvements.append(f"Quoteability improved by {quote_delta:.2f}.")
        improvements.extend(self._improved_evidence_changes(report))
        return self._unique(improvements)

    def _what_got_worse(self, report: DraftComparisonReport) -> List[str]:
        regressions: List[str] = []
        rating_delta = self._delta_from_movement(report.delta_scores.get("rating_mean"))
        if rating_delta is not None and rating_delta < -0.05:
            regressions.append(f"Predicted rating fell by {abs(rating_delta):.2f}.")
        dnf_delta = self._delta_from_movement(report.delta_scores.get("dnf_risk"))
        if dnf_delta is not None and dnf_delta > 0.03:
            regressions.append(f"DNF risk increased by {dnf_delta:.2f}.")
        controversy_delta = self._delta_from_movement(report.delta_scores.get("controversy_risk"))
        if controversy_delta is not None and controversy_delta > 0.03:
            regressions.append(f"Controversy risk increased by {controversy_delta:.2f}.")
        quote_delta = self._delta_from_movement(report.delta_scores.get("quoteability_score"))
        if quote_delta is not None and quote_delta < -0.03:
            regressions.append(f"Quoteability dropped by {abs(quote_delta):.2f}.")
        regressions.extend(self._worse_evidence_changes(report))
        return self._unique(regressions)

    def _still_blocking(self, compare_pack: EvidencePack, compare_scores: Dict[str, Any]) -> List[str]:
        blockers: List[str] = []
        dnf_risk = self._as_float(compare_scores.get("dnf_risk"))
        if dnf_risk is not None and dnf_risk >= 0.45:
            blockers.append(f"DNF risk remains elevated at {dnf_risk:.2f}.")
        controversy = self._as_float(compare_scores.get("controversy_risk"))
        if controversy is not None and controversy >= 0.55:
            blockers.append(f"Controversy risk remains elevated at {controversy:.2f}.")
        rating = self._as_float(compare_scores.get("rating_mean"))
        if rating is not None and rating < 3.4:
            blockers.append(f"Predicted rating remains soft at {rating:.2f}.")
        if compare_pack.risk_map:
            for risk in compare_pack.risk_map.risks[:3]:
                blockers.append(f"Open risk: {risk.description or risk.risk_type}.")
        return self._unique(blockers)

    def _revision_impact_summary(self, report: DraftComparisonReport) -> List[str]:
        summary: List[str] = []
        if report.what_improved:
            summary.append(f"Improvements landed in {len(report.what_improved)} major areas.")
        if report.what_got_worse:
            summary.append(f"Regressions appeared in {len(report.what_got_worse)} areas.")
        if report.chapter_deltas:
            summary.append(f"{len(report.chapter_deltas)} chapter-level shifts were detected.")
        if report.character_deltas or report.claim_deltas:
            summary.append("Core structural changes touched characters or claims, so the revision impact is not cosmetic.")
        if report.still_blocking:
            summary.append("Some publishing blockers still remain in the latest draft.")
        return summary

    def _revision_priorities(self, report: DraftComparisonReport) -> List[str]:
        priorities: List[str] = []
        for blocker in report.still_blocking[:3]:
            priorities.append(blocker)
        for item in report.what_got_worse[:2]:
            priorities.append(item)
        if not priorities:
            priorities.extend(report.what_improved[:2])
        return self._unique(priorities)

    def _summary(self, report: DraftComparisonReport) -> str:
        improved = len(report.what_improved)
        worsened = len(report.what_got_worse)
        blocking = len(report.still_blocking)
        rating_delta = self._delta_from_movement(report.delta_scores.get("rating_mean"))
        rating_clause = ""
        if rating_delta is not None:
            rating_clause = f" Predicted rating moved by {rating_delta:.2f}."
        return (
            f"Compared with {report.base_draft_id or 'the base draft'}, "
            f"{report.compare_draft_id or 'the comparison draft'} shows {improved} improvement signals and "
            f"{worsened} regression signals, with {blocking} remaining publishing blockers."
            f"{rating_clause}"
        )

    def _improved_evidence_changes(self, report: DraftComparisonReport) -> List[str]:
        improvements: List[str] = []
        for item in report.chapter_deltas:
            if item.get("pacing_from") == "slow" and item.get("pacing_to") in {"balanced", "fast"}:
                improvements.append(f"Chapter {item.get('chapter_number')} pacing improved from slow to {item.get('pacing_to')}.")
        for item in report.character_deltas:
            attachment_delta = self._as_float(item.get("attachment_delta"))
            if attachment_delta is not None and attachment_delta > 0.05:
                improvements.append(f"Character {item.get('name')} gained reader attachment.")
        for item in report.claim_deltas:
            evidence_delta = self._as_float(item.get("evidence_strength_delta"))
            if evidence_delta is not None and evidence_delta > 0.05:
                improvements.append(f"Claim {item.get('claim_id')} gained support strength.")
        return improvements

    def _worse_evidence_changes(self, report: DraftComparisonReport) -> List[str]:
        regressions: List[str] = []
        for item in report.chapter_deltas:
            if item.get("pacing_from") in {"balanced", "fast"} and item.get("pacing_to") == "slow":
                regressions.append(f"Chapter {item.get('chapter_number')} pacing slowed down.")
        for item in report.character_deltas:
            attachment_delta = self._as_float(item.get("attachment_delta"))
            if attachment_delta is not None and attachment_delta < -0.05:
                regressions.append(f"Character {item.get('name')} lost reader attachment.")
        for item in report.claim_deltas:
            evidence_delta = self._as_float(item.get("evidence_strength_delta"))
            if evidence_delta is not None and evidence_delta < -0.05:
                regressions.append(f"Claim {item.get('claim_id')} lost support strength.")
        return regressions

    def _evidence_refs(
        self,
        base_pack: EvidencePack,
        compare_pack: EvidencePack,
        base_scores: Dict[str, Any],
        compare_scores: Dict[str, Any],
    ) -> List[str]:
        refs: List[str] = list(base_pack.evidence_refs) + list(compare_pack.evidence_refs)
        for pack in (base_pack, compare_pack):
            for child in (
                pack.book_dna,
                pack.chapter_map,
                pack.character_map,
                pack.claim_map,
                pack.risk_map,
                pack.style_map,
                pack.market_surface,
            ):
                refs.extend(getattr(child, "evidence_refs", []) if child else [])
        refs.extend(self._extract_score_refs(base_scores))
        refs.extend(self._extract_score_refs(compare_scores))
        return self._unique(refs)

    def _extract_score_refs(self, scorecard: Dict[str, Any]) -> List[str]:
        refs: List[str] = []
        for value in scorecard.values():
            if isinstance(value, dict):
                refs.extend(self._extract_score_refs(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        refs.extend(self._extract_score_refs(item))
            elif isinstance(value, str) and value.endswith("_ref"):
                refs.append(value)
        return refs

    def _confidence(
        self,
        base_pack: EvidencePack,
        compare_pack: EvidencePack,
        base_run: Optional[SimulationRun],
        compare_run: Optional[SimulationRun],
    ) -> Optional[float]:
        values = [base_pack.confidence, compare_pack.confidence]
        if base_run:
            values.append(base_run.confidence)
        if compare_run:
            values.append(compare_run.confidence)
        scores = [float(value) for value in values if value is not None]
        if not scores:
            return None
        return round(sum(scores) / len(scores), 3)

    def _chapter_index(self, pack: EvidencePack) -> Dict[Tuple[int, str], ChapterSummary]:
        chapters = getattr(pack.chapter_map, "chapters", []) or []
        return {(chapter.chapter_number, chapter.chapter_id): chapter for chapter in chapters}

    def _chapter_signature(self, chapter: ChapterSummary) -> Tuple[Any, ...]:
        return (
            chapter.title,
            chapter.summary,
            chapter.pacing,
            tuple(chapter.likely_reader_friction),
            tuple(chapter.key_beats),
            tuple(chapter.turning_points),
        )

    def _named_profile_map(
        self,
        items: Sequence[Any],
        primary_field: str,
        fallback_field: str,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for item in items:
            primary = getattr(item, primary_field, None)
            fallback = getattr(item, fallback_field, None)
            key = str(primary or fallback or stable_digest(fallback_field, fallback))  # deterministic fallback
            result[key] = item
        return result

    def _text_shift(self, base_text: str, compare_text: str) -> str:
        if not base_text and not compare_text:
            return "unchanged"
        if base_text == compare_text:
            return "unchanged"
        if len(compare_text or "") > len(base_text or ""):
            return "expanded"
        if len(compare_text or "") < len(base_text or ""):
            return "compressed"
        return "rewritten"

    def _list_change(self, field_name: str, base_values: Iterable[str], compare_values: Iterable[str]) -> List[Dict[str, Any]]:
        base_set = {item for item in base_values if item}
        compare_set = {item for item in compare_values if item}
        changes: List[Dict[str, Any]] = []
        for item in sorted(compare_set - base_set):
            changes.append({"field": field_name, "change_type": "added", "value": item})
        for item in sorted(base_set - compare_set):
            changes.append({"field": field_name, "change_type": "removed", "value": item})
        return changes

    def _delta_value(self, base_value: Any, compare_value: Any) -> Optional[float]:
        base_number = self._as_float(base_value)
        compare_number = self._as_float(compare_value)
        if base_number is None or compare_number is None:
            return None
        return round(compare_number - base_number, 3)

    def _delta_from_movement(self, movement: Any) -> Optional[float]:
        if not isinstance(movement, dict):
            return None
        return self._as_float(movement.get("delta"))

    def _as_float(self, value: Any, default: Optional[float] = None) -> Optional[float]:
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _mean(self, values: Sequence[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _unique(self, values: Sequence[str]) -> List[str]:
        seen = set()
        result: List[str] = []
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result
