"""Tests for deterministic Swarmbook report synthesis."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.models import (
    BookDNA,
    BookProject,
    ChapterMap,
    ChapterSummary,
    CharacterMap,
    CharacterProfile,
    ClaimMap,
    ClaimProfile,
    CrossReaction,
    EvidencePack,
    ManuscriptInput,
    MarketSurface,
    PlatformPost,
    PrivateReaderReaction,
    ReaderPersona,
    RiskMap,
    RiskProfile,
    SimulationRun,
    StyleMap,
)
from book_sim.report_builder import build_prediction_report


class ReportBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        manuscript = ManuscriptInput(
            input_id="input_report",
            project_id="proj_report",
            title="Signal and Pressure",
            text="A small manuscript sample.",
            privacy_mode="local_only",
            draft_id="draft_report",
            version="v1",
        )
        self.project = BookProject(
            project_id="proj_report",
            name="Report Project",
            privacy_mode="local_only",
            draft_id="draft_report",
            version="v1",
            title="Signal and Pressure",
            manuscript_input=manuscript,
            confidence=0.75,
        )
        self.pack = EvidencePack(
            pack_id="pack_report",
            project_id="proj_report",
            draft_id="draft_report",
            version="v1",
            privacy_mode="local_only",
            manuscript_input=manuscript,
            book_dna=BookDNA(
                title="Signal and Pressure",
                premise="A tense choice in a fragile town.",
                genre="speculative fiction",
                book_type="fiction",
                tone="tense",
                themes=["trust", "responsibility"],
                spoilers_safe_summary="A hard decision changes the community.",
                evidence_refs=["dna_ref"],
            ),
            chapter_map=ChapterMap(
                book_id="book_report",
                chapters=[
                    ChapterSummary(
                        chapter_id="ch_1",
                        chapter_number=1,
                        title="Start",
                        summary="Pressure arrives quickly.",
                        pacing="slow",
                        likely_reader_friction=["setup"],
                    ),
                    ChapterSummary(
                        chapter_id="ch_2",
                        chapter_number=2,
                        title="Choice",
                        summary="The cost becomes clear.",
                        pacing="balanced",
                        key_beats=["choice"],
                    ),
                ],
            ),
            character_map=CharacterMap(
                book_id="book_report",
                characters=[
                    CharacterProfile(
                        character_id="char_1",
                        name="Mara",
                        role="lead",
                        attachment_potential=0.7,
                        evidence_refs=["char_ref"],
                    )
                ],
            ),
            claim_map=ClaimMap(
                book_id="book_report",
                claims=[
                    ClaimProfile(
                        claim_id="claim_1",
                        claim_text="Compromise carries a cost.",
                        evidence_strength=0.8,
                        counterarguments=["too bleak"],
                        factual_risk_flags=["unclear_scope"],
                        evidence_refs=["claim_ref"],
                    )
                ],
            ),
            risk_map=RiskMap(
                book_id="book_report",
                risks=[
                    RiskProfile(
                        risk_id="risk_1",
                        risk_type="pacing_drag",
                        description="The opening may feel slow.",
                        evidence_refs=["risk_ref"],
                    )
                ],
            ),
            style_map=StyleMap(
                book_id="book_report",
                quoteability="high",
                clarity="high",
                rhythm="high",
                accessibility="medium",
                style_notes=["clean"],
            ),
            market_surface=MarketSurface(
                book_id="book_report",
                discoverability_hooks=["moral dilemma"],
                target_segments=["book clubs", "Goodreads genre loyalist"],
                audience_fit="medium_high",
                evidence_refs=["market_ref"],
            ),
            evidence_refs=["pack_ref"],
            confidence=0.8,
        )
        personas = [
            ReaderPersona(
                persona_id="persona_1",
                archetype_id="arch_1",
                display_name="Avery",
                platform_home="goodreads",
                review_style="critical_balanced",
                platform="goodreads",
                cohort="community_reviewers",
                favorite_genres=["speculative fiction"],
                disliked_patterns=["pacing_drag"],
                delight_triggers=["moral tension"],
                influence_weight=0.6,
                quote_sharing_probability=0.55,
                evidence_focus=0.7,
                confidence=0.8,
            ),
            ReaderPersona(
                persona_id="persona_2",
                archetype_id="arch_2",
                display_name="Morgan",
                platform_home="booktok",
                review_style="emotional",
                platform="booktok",
                cohort="viral_emotion_seekers",
                favorite_genres=["speculative fiction"],
                disliked_patterns=["slow_start"],
                delight_triggers=["moral tension"],
                influence_weight=0.7,
                quote_sharing_probability=0.8,
                evidence_focus=0.6,
                confidence=0.8,
            ),
        ]
        private_reactions = [
            PrivateReaderReaction(
                reaction_id="private_1",
                simulation_id="sim_report",
                persona_id="persona_1",
                rating=4.3,
                dnf_probability=0.2,
                sentiment="positive",
                attachment_score=0.7,
                confusion_score=0.2,
                recommendation_probability=0.75,
                praise=["moral tension"],
                friction=["slow_start"],
                notable_quotes=["A hard decision changes the community."],
                evidence_refs=["private_ref_1"],
                confidence=0.82,
            ),
            PrivateReaderReaction(
                reaction_id="private_2",
                simulation_id="sim_report",
                persona_id="persona_2",
                rating=2.7,
                dnf_probability=0.35,
                sentiment="mixed",
                attachment_score=0.4,
                confusion_score=0.5,
                recommendation_probability=0.4,
                praise=["choice"],
                friction=["slow_start"],
                notable_quotes=["Pressure arrives quickly."],
                evidence_refs=["private_ref_2"],
                confidence=0.78,
            ),
        ]
        platform_posts = [
            PlatformPost(
                post_id="post_1",
                simulation_id="sim_report",
                persona_id="persona_1",
                platform="goodreads",
                round_number=1,
                title="A hard recommendation",
                body="...",
                rating=4.3,
                shelf_tags=["book-club"],
                payload={"review_title": "A hard recommendation", "review_body": "...", "evidence_refs": ["private_ref_1"]},
                engagement_prediction=0.7,
                sentiment="positive",
                evidence_refs=["private_ref_1"],
                confidence=0.82,
            ),
            PlatformPost(
                post_id="post_2",
                simulation_id="sim_report",
                persona_id="persona_2",
                platform="booktok",
                round_number=1,
                title="Hook",
                body="...",
                rating=2.7,
                hashtags=["booktok"],
                payload={"viral_trigger": "high", "hook_line": "You will feel this choice.", "evidence_refs": ["private_ref_2"]},
                engagement_prediction=0.85,
                sentiment="mixed",
                evidence_refs=["private_ref_2"],
                confidence=0.78,
            ),
        ]
        cross_reactions = [
            CrossReaction(
                reaction_id="cross_1",
                simulation_id="sim_report",
                source_post_id="post_1",
                target_post_id="post_2",
                persona_id="persona_1",
                platform="goodreads",
                reacted_post_ids=["post_1", "post_2"],
                stance_shift="more_negative",
                agree_probability=0.3,
                disagree_probability=0.7,
                reply_likelihood=0.5,
                rating_shift=-0.2,
                recommendation_shift=-0.1,
                sentiment="mixed",
                evidence_refs=["private_ref_1", "private_ref_2"],
                confidence=0.8,
            )
        ]
        self.run = SimulationRun(
            run_id="sim_report",
            project_id="proj_report",
            privacy_mode="local_only",
            draft_id="draft_report",
            version="v1",
            provider_route="local_ollama",
            status="completed",
            personas_count=2,
            reactions_count=2,
            posts_count=2,
            reader_personas=personas,
            private_reactions=private_reactions,
            platform_posts=platform_posts,
            cross_reactions=cross_reactions,
            evidence_refs=["pack_ref"],
            confidence=0.85,
        )

    def test_build_prediction_report_is_deterministic_and_json_safe(self) -> None:
        first = build_prediction_report(self.project, self.pack, self.run)
        second = build_prediction_report(self.project, self.pack, self.run)

        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.privacy_mode, "local_only")
        self.assertIn("rating_distribution", first.scorecard)
        self.assertIn("dnf", first.scorecard)
        self.assertTrue(first.segment_insights)
        self.assertTrue(first.top_risks)
        self.assertTrue(first.top_strengths)
        self.assertTrue(first.revision_priorities)
        self.assertTrue(first.evidence_refs)

        encoded = first.to_json()
        decoded = json.loads(encoded)
        self.assertEqual(decoded["report_id"], first.report_id)
        self.assertEqual(decoded["privacy_mode"], "local_only")


if __name__ == "__main__":
    unittest.main()
