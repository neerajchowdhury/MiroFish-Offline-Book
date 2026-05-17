"""Tests for Swarmbook draft comparison."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.comparison import DraftComparator
from book_sim.models import (
    BookDNA,
    ChapterMap,
    ChapterSummary,
    CharacterMap,
    CharacterProfile,
    ClaimMap,
    ClaimProfile,
    EvidencePack,
    ManuscriptInput,
    MarketSurface,
    PrivateReaderReaction,
    ReaderPersona,
    RiskMap,
    RiskProfile,
    SimulationRun,
    StyleMap,
)


class DraftComparatorTests(unittest.TestCase):
    def setUp(self) -> None:
        base_text = (FIXTURE_ROOT / "book_sim_compare_draft_a.txt").read_text(encoding="utf-8")
        compare_text = (FIXTURE_ROOT / "book_sim_compare_draft_b.txt").read_text(encoding="utf-8")
        self.base_pack = self._pack(
            draft_id="draft_a",
            version="v1",
            text=base_text,
            premise="A tense choice is delayed by hesitation.",
            tone="moody",
            chapter_two_pacing="slow",
            risk_type="pacing_drag",
            risk_description="The middle lingers before the choice lands.",
            attachment=0.52,
            evidence_strength=0.48,
            target_segments=["book clubs", "slow-burn readers"],
            style_quoteability="medium",
            style_note="atmospheric prose",
        )
        self.compare_pack = self._pack(
            draft_id="draft_b",
            version="v2",
            text=compare_text,
            premise="A tense choice is forced early and carries immediate cost.",
            tone="urgent",
            chapter_two_pacing="balanced",
            risk_type="controversial_choice",
            risk_description="The choice may divide readers morally.",
            attachment=0.67,
            evidence_strength=0.74,
            target_segments=["book clubs", "speculative fiction readers"],
            style_quoteability="high",
            style_note="clean prose",
        )
        self.base_run = self._simulation_run(
            draft_id="draft_a",
            rating=3.3,
            dnf_probability=0.46,
            recommendation_probability=0.43,
            attachment_score=0.49,
            confusion_score=0.42,
            praise=["atmosphere"],
            friction=["padding", "slow_start"],
            persona_segment="community_reviewers",
            sentiment="mixed",
        )
        self.compare_run = self._simulation_run(
            draft_id="draft_b",
            rating=4.1,
            dnf_probability=0.28,
            recommendation_probability=0.72,
            attachment_score=0.68,
            confusion_score=0.23,
            praise=["moral tension", "clean prose"],
            friction=["controversial_choice"],
            persona_segment="community_reviewers",
            sentiment="positive",
        )

    def test_compare_with_simulations_is_deterministic_and_complete(self) -> None:
        comparator = DraftComparator()
        first = comparator.compare(
            project_id="proj_compare",
            base_evidence_pack=self.base_pack,
            compare_evidence_pack=self.compare_pack,
            base_simulation_run=self.base_run,
            compare_simulation_run=self.compare_run,
            simulation_seed=11,
        )
        second = comparator.compare(
            project_id="proj_compare",
            base_evidence_pack=self.base_pack,
            compare_evidence_pack=self.compare_pack,
            base_simulation_run=self.base_run,
            compare_simulation_run=self.compare_run,
            simulation_seed=11,
        )

        self.assertEqual(first.to_dict(), second.to_dict())
        report = first.report
        self.assertIn("rating_mean", report.delta_scores)
        self.assertIn("dnf_risk", report.delta_scores)
        self.assertIn("controversy_risk", report.delta_scores)
        self.assertIn("viral_mean", report.delta_scores)
        self.assertTrue(report.book_dna_changes)
        self.assertTrue(report.chapter_deltas)
        self.assertTrue(report.character_deltas)
        self.assertTrue(report.claim_deltas)
        self.assertTrue(report.reader_segment_movement)
        self.assertTrue(report.revision_impact_summary)
        self.assertTrue(report.what_improved)
        self.assertTrue(report.still_blocking)
        self.assertIn("## What Improved", first.markdown)
        self.assertIn("## What Still Blocks Publishing", first.markdown)
        self.assertEqual(report.metadata["simulation_seed"], 11)

    def test_compare_without_simulations_uses_available_scores(self) -> None:
        comparator = DraftComparator()
        export = comparator.compare(
            project_id="proj_compare",
            base_evidence_pack=self.base_pack,
            compare_evidence_pack=self.compare_pack,
            base_scores={
                "rating_mean": 3.2,
                "dnf_risk": 0.5,
                "quoteability_score": 0.42,
                "controversy_risk": 0.31,
                "viral_mean": 0.33,
            },
            compare_scores={
                "rating_mean": 3.9,
                "dnf_risk": 0.34,
                "quoteability_score": 0.58,
                "controversy_risk": 0.45,
                "viral_mean": 0.47,
            },
        )

        report = export.report
        self.assertEqual(report.base_scores["rating_mean"], 3.2)
        self.assertEqual(report.compare_scores["rating_mean"], 3.9)
        self.assertAlmostEqual(report.delta_scores["rating_mean"]["delta"], 0.7, places=3)
        self.assertTrue(report.book_dna_changes)
        self.assertTrue(report.chapter_deltas)
        self.assertTrue(report.reader_segment_movement)
        self.assertIn("## Score Movement", export.markdown)

    def _pack(
        self,
        draft_id: str,
        version: str,
        text: str,
        premise: str,
        tone: str,
        chapter_two_pacing: str,
        risk_type: str,
        risk_description: str,
        attachment: float,
        evidence_strength: float,
        target_segments: list[str],
        style_quoteability: str,
        style_note: str,
    ) -> EvidencePack:
        manuscript = ManuscriptInput(
            input_id=f"input_{draft_id}",
            project_id="proj_compare",
            title="Pressure Test",
            text=text,
            privacy_mode="local_only",
            draft_id=draft_id,
            version=version,
        )
        return EvidencePack(
            pack_id=f"pack_{draft_id}",
            project_id="proj_compare",
            draft_id=draft_id,
            version=version,
            privacy_mode="local_only",
            manuscript_input=manuscript,
            book_dna=BookDNA(
                title="Pressure Test",
                premise=premise,
                genre="speculative fiction",
                book_type="fiction",
                tone=tone,
                themes=["trust", "responsibility"],
                spoilers_safe_summary="A public decision changes the town.",
                evidence_refs=[f"dna_ref_{draft_id}"],
            ),
            chapter_map=ChapterMap(
                book_id=f"book_{draft_id}",
                chapters=[
                    ChapterSummary(
                        chapter_id=f"{draft_id}_ch_1",
                        chapter_number=1,
                        title="Arrival",
                        summary="The town pressure starts immediately.",
                        pacing="fast",
                        key_beats=["arrival", "choice"],
                        evidence_refs=[f"chapter1_ref_{draft_id}"],
                    ),
                    ChapterSummary(
                        chapter_id=f"{draft_id}_ch_2",
                        chapter_number=2,
                        title="Consequences",
                        summary="The consequences either linger or escalate.",
                        pacing=chapter_two_pacing,
                        likely_reader_friction=["middle_drag"] if chapter_two_pacing == "slow" else ["moral_divide"],
                        evidence_refs=[f"chapter2_ref_{draft_id}"],
                    ),
                ],
                evidence_refs=[f"chapter_map_ref_{draft_id}"],
            ),
            character_map=CharacterMap(
                book_id=f"book_{draft_id}",
                characters=[
                    CharacterProfile(
                        character_id="char_mara",
                        name="Mara",
                        role="lead",
                        attachment_potential=attachment,
                        reader_friction=["hesitation"] if draft_id == "draft_a" else ["moral_cost"],
                        evidence_refs=[f"char_ref_{draft_id}"],
                    )
                ],
                evidence_refs=[f"character_map_ref_{draft_id}"],
            ),
            claim_map=ClaimMap(
                book_id=f"book_{draft_id}",
                claims=[
                    ClaimProfile(
                        claim_id="claim_choice",
                        claim_text="Public compromise has a real cost.",
                        evidence_strength=evidence_strength,
                        factual_risk_flags=["unclear_scope"] if draft_id == "draft_a" else [],
                        counterarguments=["too soft"] if draft_id == "draft_a" else ["too harsh"],
                        evidence_refs=[f"claim_ref_{draft_id}"],
                    )
                ],
                evidence_refs=[f"claim_map_ref_{draft_id}"],
            ),
            risk_map=RiskMap(
                book_id=f"book_{draft_id}",
                risks=[
                    RiskProfile(
                        risk_id=f"risk_{draft_id}",
                        risk_type=risk_type,
                        description=risk_description,
                        mitigation_hint="tighten pacing where momentum sags" if draft_id == "draft_a" else "clarify the moral framing",
                        evidence_refs=[f"risk_ref_{draft_id}"],
                    )
                ],
                evidence_refs=[f"risk_map_ref_{draft_id}"],
            ),
            style_map=StyleMap(
                book_id=f"book_{draft_id}",
                clarity="high",
                rhythm="high" if draft_id == "draft_b" else "medium",
                quoteability=style_quoteability,
                style_notes=[style_note],
                evidence_refs=[f"style_ref_{draft_id}"],
            ),
            market_surface=MarketSurface(
                book_id=f"book_{draft_id}",
                target_segments=target_segments,
                discoverability_hooks=["moral dilemma"] if draft_id == "draft_b" else ["slow-burn tension"],
                packaging_expectations=["clear genre signal"],
                promise_gap="blurb undersells urgency" if draft_id == "draft_a" else None,
                evidence_refs=[f"market_ref_{draft_id}"],
            ),
            evidence_refs=[f"pack_ref_{draft_id}"],
            confidence=0.8,
        )

    def _simulation_run(
        self,
        draft_id: str,
        rating: float,
        dnf_probability: float,
        recommendation_probability: float,
        attachment_score: float,
        confusion_score: float,
        praise: list[str],
        friction: list[str],
        persona_segment: str,
        sentiment: str,
    ) -> SimulationRun:
        persona = ReaderPersona(
            persona_id=f"persona_{draft_id}",
            archetype_id="arch_reader",
            display_name="Casey",
            platform_home="goodreads",
            review_style="critical_balanced",
            platform="goodreads",
            cohort=persona_segment,
            favorite_genres=["speculative fiction"],
            disliked_patterns=["padding"],
            dnf_threshold=0.5,
            delight_triggers=["moral tension"],
            evidence_refs=[f"persona_ref_{draft_id}"],
            confidence=0.78,
        )
        reaction = PrivateReaderReaction(
            reaction_id=f"reaction_{draft_id}",
            simulation_id=f"sim_{draft_id}",
            persona_id=persona.persona_id,
            rating=rating,
            dnf_probability=dnf_probability,
            sentiment=sentiment,
            attachment_score=attachment_score,
            confusion_score=confusion_score,
            recommendation_probability=recommendation_probability,
            praise=praise,
            friction=friction,
            notable_quotes=["A public decision changes the town."],
            evidence_refs=[f"reaction_ref_{draft_id}"],
            confidence=0.77,
        )
        return SimulationRun(
            run_id=f"sim_{draft_id}",
            project_id="proj_compare",
            privacy_mode="local_only",
            draft_id=draft_id,
            version="v1" if draft_id == "draft_a" else "v2",
            provider_route="local_ollama",
            status="completed",
            personas_count=1,
            reactions_count=1,
            posts_count=0,
            reader_personas=[persona],
            private_reactions=[reaction],
            platform_posts=[],
            cross_reactions=[],
            evidence_refs=[f"run_ref_{draft_id}"],
            confidence=0.79,
            metadata={"seed": 11},
        )


if __name__ == "__main__":
    unittest.main()
