"""Serialization tests for Swarmbook dataclass models."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.models import (
    BookDNA,
    BookPredictionReport,
    BookProject,
    ChapterMap,
    ChapterSummary,
    CharacterMap,
    CharacterProfile,
    ClaimMap,
    ClaimProfile,
    CrossReaction,
    DraftComparisonReport,
    EvidencePack,
    ManuscriptInput,
    MarketSurface,
    PlatformPost,
    PrivateReaderReaction,
    ReaderArchetype,
    ReaderPersona,
    RiskMap,
    RiskProfile,
    SimulationRun,
    StyleMap,
)


class TestBookSimModels(unittest.TestCase):
    def setUp(self) -> None:
        manuscript = ManuscriptInput(
            input_id="input_001",
            project_id="proj_001",
            title="The Lighthouse Draft",
            author_name="A. Writer",
            filename="draft.pdf",
            mime_type="application/pdf",
            text="Chapter one begins here.",
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
            evidence_refs=["chunk_1"],
            confidence=0.91,
        )

        chapter = ChapterSummary(
            chapter_id="ch_01",
            chapter_number=1,
            title="Opening",
            summary="The book introduces the central conflict.",
            purpose="establish stakes",
            pacing="fast",
            key_beats=["hook", "inciting incident"],
            turning_points=["decision"],
            open_questions=["who is the antagonist?"],
            spoiler_notes=["major reveal withheld"],
            evidence_refs=["chunk_1", "chunk_2"],
            confidence=0.82,
        )

        character = CharacterProfile(
            character_id="char_01",
            name="Mara",
            role="protagonist",
            goals=["discover the truth"],
            conflicts=["fear of loss"],
            relationships={"Iris": "ally"},
            arc_summary="Moves from avoidance to action.",
            attachment_potential=0.74,
            reader_friction=["withholding feelings"],
            evidence_refs=["chunk_1"],
            confidence=0.79,
        )

        claim = ClaimProfile(
            claim_id="claim_01",
            claim_text="The policy change will reduce churn.",
            support_type="analysis",
            support_quality="moderate",
            evidence_strength=0.67,
            counterarguments=["sample size is limited"],
            reader_trust_sensitivity=0.58,
            evidence_refs=["source_1", "source_2"],
            confidence=0.76,
        )

        risk = RiskProfile(
            risk_id="risk_01",
            risk_type="pacing_drag",
            severity="medium",
            description="The middle section may slow down.",
            affected_segments=["chapter_3", "chapter_4"],
            trigger_text="long exposition block",
            mitigation_hint="tighten transitions",
            evidence_refs=["chunk_3"],
            confidence=0.69,
        )

        self.manuscript = manuscript
        self.book_project = BookProject(
            project_id="proj_001",
            name="Lighthouse Project",
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
            title="The Lighthouse Draft",
            author_name="A. Writer",
            manuscript_input=manuscript,
            source_files=["draft.pdf"],
            metadata={"genre": "literary fiction"},
            evidence_refs=["manuscript_manifest"],
            confidence=0.88,
        )
        self.book_dna = BookDNA(
            title="The Lighthouse Draft",
            premise="A keeper confronts a hidden history.",
            genre="literary fiction",
            subgenre="psychological drama",
            tone="melancholic",
            emotional_promise="a slow reveal with emotional payoff",
            narrative_engine="mystery-driven character study",
            reading_difficulty="medium",
            target_reader="literary readers",
            comparable_titles=["The Night Circus"],
            themes=["memory", "grief"],
            spoilers_safe_summary="A keeper discovers the island is not what it seems.",
            evidence_refs=["book_dna_1"],
            confidence=0.84,
        )
        self.chapter_map = ChapterMap(
            book_id="book_001",
            chapters=[chapter],
            total_chapters=12,
            pacing_profile="front-loaded",
            structural_notes=["chapter one is hook-heavy"],
            evidence_refs=["chapter_manifest"],
            confidence=0.81,
        )
        self.character_map = CharacterMap(
            book_id="book_001",
            characters=[character],
            cast_size=8,
            relationship_graph_summary="Mara and Iris form the emotional center.",
            evidence_refs=["character_manifest"],
            confidence=0.78,
        )
        self.claim_map = ClaimMap(
            book_id="book_001",
            claims=[claim],
            thesis_summary="The policy shifts are more complex than they appear.",
            argument_strength_summary="Moderate but depends on source quality.",
            evidence_refs=["claim_manifest"],
            confidence=0.75,
        )
        self.risk_map = RiskMap(
            book_id="book_001",
            risks=[risk],
            risk_summary="Moderate pacing and trust risks.",
            evidence_refs=["risk_manifest"],
            confidence=0.68,
        )
        self.style_map = StyleMap(
            book_id="book_001",
            prose_density="medium",
            clarity="high",
            rhythm="measured",
            voice_consistency="steady",
            quoteability="medium",
            accessibility="medium",
            style_notes=["strong imagery", "occasional density"],
            evidence_refs=["style_manifest"],
            confidence=0.73,
        )
        self.market_surface = MarketSurface(
            book_id="book_001",
            target_segments=["literary readers", "book club readers"],
            comp_titles=["The Night Circus", "Piranesi"],
            positioning_summary="A reflective mystery with literary appeal.",
            discoverability_hooks=["island mystery", "emotional reveal"],
            packaging_expectations=["atmospheric", "character-driven"],
            promise_gap="covers more mystery than the blurb suggests",
            audience_fit="medium_high",
            evidence_refs=["market_manifest"],
            confidence=0.7,
        )
        self.evidence_pack = EvidencePack(
            pack_id="pack_001",
            project_id="proj_001",
            draft_id="draft_a",
            version="v1",
            privacy_mode="hybrid_safe",
            manuscript_input=manuscript,
            book_dna=self.book_dna,
            chapter_map=self.chapter_map,
            character_map=self.character_map,
            claim_map=self.claim_map,
            risk_map=self.risk_map,
            style_map=self.style_map,
            market_surface=self.market_surface,
            evidence_refs=["pack_manifest"],
            confidence=0.8,
        )
        self.reader_archetype = ReaderArchetype(
            archetype_id="goodreads_harsh_reviewer",
            display_name="Goodreads harsh reviewer",
            platform_home="goodreads",
            review_style="critical_balanced",
            cohort="community_reviewers",
            favorite_genres=["literary fiction", "mystery"],
            disliked_patterns=["slow_start"],
            dnf_threshold=0.46,
            controversy_sensitivity=0.42,
            rating_bias=-0.18,
            influence_weight=0.34,
            susceptibility_to_peer_reaction=0.39,
            quote_sharing_probability=0.44,
            evidence_focus=0.58,
            privacy_constraints=["synthetic_persona_only", "simulated_platform_only"],
            book_type_suitability=["fiction"],
            selection_weight=0.7,
            genre_bias="high_standards",
            patience_level="medium_low",
            dnf_triggers=["slow_start"],
            delight_triggers=["clean_prose"],
            influence_profile="medium",
            spoiler_tolerance="low",
            reaction_tempo="slow",
            evidence_refs=["archetype_manifest"],
            confidence=1.0,
        )
        self.reader_persona = ReaderPersona(
            persona_id="persona_001",
            archetype_id="goodreads_harsh_reviewer",
            display_name="Casey",
            platform_home="goodreads",
            review_style="critical_balanced",
            id="persona_001",
            name="Casey",
            cohort="community_reviewers",
            platform="goodreads",
            favorite_genres=["character depth", "mystery"],
            disliked_patterns=["padding"],
            dnf_threshold=0.49,
            controversy_sensitivity=0.45,
            rating_bias=-0.12,
            influence_weight=0.42,
            susceptibility_to_peer_reaction=0.37,
            quote_sharing_probability=0.51,
            evidence_focus=0.6,
            privacy_constraints=["synthetic_persona_only"],
            book_type_suitability=["fiction"],
            reading_preferences=["character depth", "tight pacing"],
            dnf_triggers=["padding"],
            delight_triggers=["clean prose"],
            private_bias="skeptical",
            influence_score=0.42,
            spoiler_tolerance="low",
            evidence_refs=["persona_manifest"],
            confidence=0.77,
        )
        self.private_reaction = PrivateReaderReaction(
            reaction_id="reaction_001",
            simulation_id="sim_001",
            persona_id="persona_001",
            chapter_id="ch_01",
            rating=4.0,
            dnf_probability=0.18,
            sentiment="positive-mixed",
            attachment_score=0.61,
            confusion_score=0.23,
            recommendation_probability=0.71,
            praise=["strong opening"],
            friction=["a bit dense"],
            notable_quotes=["The island felt alive."],
            evidence_refs=["reaction_manifest"],
            confidence=0.74,
        )
        self.platform_post = PlatformPost(
            post_id="post_001",
            simulation_id="sim_001",
            persona_id="persona_001",
            platform="goodreads",
            round_number=1,
            title="Atmospheric but demanding",
            body="I liked the atmosphere, but the middle drags.",
            rating=4.0,
            hashtags=["#literaryfiction"],
            shelf_tags=["slow-burn", "atmospheric"],
            payload={"review_title": "Atmospheric but demanding", "quote_highlights": ["The island felt alive."]},
            engagement_prediction=0.33,
            sentiment="mixed-positive",
            evidence_refs=["post_manifest"],
            confidence=0.68,
        )
        self.cross_reaction = CrossReaction(
            reaction_id="cross_001",
            simulation_id="sim_001",
            source_post_id="post_001",
            target_post_id="post_002",
            persona_id="persona_001",
            platform="reddit",
            reacted_post_ids=["post_001", "post_002"],
            stance_shift="slightly_more_positive",
            agree_probability=0.54,
            disagree_probability=0.31,
            reply_likelihood=0.47,
            rating_shift=0.12,
            recommendation_shift=0.09,
            sentiment="mixed",
            evidence_refs=["cross_manifest"],
            confidence=0.63,
        )
        self.simulation_run = SimulationRun(
            run_id="run_001",
            project_id="proj_001",
            graph_id="graph_001",
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
            provider_route="local_ollama",
            status="completed",
            started_at="2026-05-16T10:00:00",
            ended_at="2026-05-16T10:30:00",
            total_rounds=3,
            current_round=3,
            personas_count=12,
            reactions_count=48,
            posts_count=24,
            report_id="report_001",
            reader_personas=[self.reader_persona],
            private_reactions=[self.private_reaction],
            platform_posts=[self.platform_post],
            cross_reactions=[self.cross_reaction],
            evidence_refs=["run_manifest"],
            confidence=0.9,
            metadata={"seed": 42},
        )
        self.prediction_report = BookPredictionReport(
            report_id="report_001",
            project_id="proj_001",
            simulation_id="sim_001",
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
            title="Swarmbook prediction",
            summary="Readers are likely to like the atmosphere but split on pacing.",
            audience_response={"goodreads": "mixed-positive"},
            scorecard={"rating": 4.1, "dnf_risk": 0.22},
            segment_insights=[{"segment": "literary readers", "signal": "positive"}],
            top_risks=["pacing drag"],
            top_strengths=["atmosphere"],
            revision_priorities=["tighten middle"],
            uncertainty_notes=["small sample size"],
            evidence_refs=["report_manifest"],
            confidence=0.66,
        )
        self.comparison_report = DraftComparisonReport(
            comparison_id="cmp_001",
            project_id="proj_001",
            privacy_mode="cloud_quality",
            base_draft_id="draft_a",
            base_version="v1",
            compare_draft_id="draft_b",
            compare_version="v2",
            summary="Draft B improves pacing but slightly reduces tone consistency.",
            delta_scores={"rating": 0.2, "dnf_risk": -0.08},
            chapter_deltas=[{"chapter_id": "ch_03", "delta": "faster"}],
            character_deltas=[{"character_id": "char_01", "delta": "more attachment"}],
            claim_deltas=[{"claim_id": "claim_01", "delta": "better sourced"}],
            revision_priorities=["keep pacing gains", "tighten tone"],
            evidence_refs=["comparison_manifest"],
            confidence=0.72,
        )

    def round_trip(self, obj):
        restored = obj.__class__.from_dict(obj.to_dict())
        self.assertEqual(obj, restored)
        restored_json = obj.__class__.from_json(obj.to_json())
        self.assertEqual(obj, restored_json)

    def test_model_round_trips(self) -> None:
        objects = [
            self.manuscript,
            self.book_project,
            self.book_dna,
            self.chapter_map,
            self.chapter_map.chapters[0],
            self.character_map,
            self.character_map.characters[0],
            self.claim_map,
            self.claim_map.claims[0],
            self.risk_map,
            self.risk_map.risks[0],
            self.style_map,
            self.market_surface,
            self.evidence_pack,
            self.reader_archetype,
            self.reader_persona,
            self.private_reaction,
            self.platform_post,
            self.cross_reaction,
            self.simulation_run,
            self.prediction_report,
            self.comparison_report,
        ]

        for obj in objects:
            with self.subTest(model=obj.__class__.__name__):
                self.round_trip(obj)

    def test_nested_models_preserve_types(self) -> None:
        pack = self.evidence_pack
        restored = EvidencePack.from_json(pack.to_json())
        self.assertIsInstance(restored.manuscript_input, ManuscriptInput)
        self.assertIsInstance(restored.book_dna, BookDNA)
        self.assertIsInstance(restored.chapter_map, ChapterMap)
        self.assertIsInstance(restored.chapter_map.chapters[0], ChapterSummary)


if __name__ == "__main__":
    unittest.main()
