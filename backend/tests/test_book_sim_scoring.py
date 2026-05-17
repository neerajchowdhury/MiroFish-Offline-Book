"""Tests for Swarmbook scoring functions."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.local_cache import LocalArtifactCache
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
from book_sim.scoring import (
    ScoringContext,
    score_controversy,
    score_dnf,
    score_polarization,
    score_quoteability,
    score_rating_distribution,
    score_revision_priority,
    score_viral_potential,
)


class SwarmbookScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        manuscript = ManuscriptInput(
            input_id="input_score",
            project_id="proj_score",
            title="Signal and Pressure",
            text="A small manuscript sample.",
            privacy_mode="local_only",
            draft_id="draft_score",
            version="v1",
        )
        self.project = BookProject(
            project_id="proj_score",
            name="Scoring Project",
            privacy_mode="local_only",
            draft_id="draft_score",
            version="v1",
            title="Signal and Pressure",
            manuscript_input=manuscript,
        )
        self.pack = EvidencePack(
            pack_id="pack_score",
            project_id="proj_score",
            draft_id="draft_score",
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
                book_id="book_score",
                chapters=[
                    ChapterSummary(
                        chapter_id="ch_1",
                        chapter_number=1,
                        title="Start",
                        summary="Pressure arrives quickly.",
                        pacing="slow",
                        likely_reader_friction=["setup"],
                        open_questions=["why now"],
                    ),
                    ChapterSummary(
                        chapter_id="ch_2",
                        chapter_number=2,
                        title="Choice",
                        summary="The cost becomes clear.",
                        pacing="balanced",
                        key_beats=["choice"],
                        emotional_beats=["fear"],
                        turning_points=["decision"],
                    ),
                ],
            ),
            character_map=CharacterMap(
                book_id="book_score",
                characters=[
                    CharacterProfile(character_id="char_1", name="Mara", role="lead", attachment_potential=0.7, evidence_refs=["char_ref"])
                ],
            ),
            claim_map=ClaimMap(
                book_id="book_score",
                claims=[
                    ClaimProfile(
                        claim_id="claim_1",
                        claim_text="The premise argues that compromise carries a cost.",
                        evidence_strength=0.8,
                        counterarguments=["too bleak"],
                        factual_risk_flags=["unclear_scope"],
                        evidence_refs=["claim_ref"],
                    )
                ],
            ),
            risk_map=RiskMap(
                book_id="book_score",
                risks=[RiskProfile(risk_id="risk_1", risk_type="pacing_drag", evidence_refs=["risk_ref"])],
            ),
            style_map=StyleMap(book_id="book_score", quoteability="high", clarity="high", rhythm="high", accessibility="medium", style_notes=["clean"]),
            market_surface=MarketSurface(
                book_id="book_score",
                discoverability_hooks=["moral dilemma"],
                target_segments=["book clubs", "Goodreads genre loyalist"],
                packaging_expectations=["clear genre signal"],
                audience_fit="medium_high",
                evidence_refs=["market_ref"],
            ),
            evidence_refs=["pack_ref"],
            confidence=0.8,
        )
        self.personas = [
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
        self.private_reactions = [
            PrivateReaderReaction(
                reaction_id="private_1",
                simulation_id="sim_1",
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
                simulation_id="sim_1",
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
        self.platform_posts = [
            PlatformPost(
                post_id="post_1",
                simulation_id="sim_1",
                persona_id="persona_1",
                platform="goodreads",
                round_number=1,
                title="A hard recommendation",
                body="...",
                rating=4.3,
                shelf_tags=["book-club", "speculative-fiction"],
                payload={"review_title": "A hard recommendation", "review_body": "..." , "shelf_tags": ["book-club"], "evidence_refs": ["private_ref_1"]},
                engagement_prediction=0.7,
                sentiment="positive",
                evidence_refs=["private_ref_1"],
                confidence=0.82,
            ),
            PlatformPost(
                post_id="post_2",
                simulation_id="sim_1",
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
        self.cross_reactions = [
            CrossReaction(
                reaction_id="cross_1",
                simulation_id="sim_1",
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
            run_id="sim_1",
            project_id="proj_score",
            privacy_mode="local_only",
            draft_id="draft_score",
            version="v1",
            provider_route="local_ollama",
            status="completed",
            personas_count=2,
            reactions_count=2,
            posts_count=2,
            reader_personas=list(self.personas),
            private_reactions=list(self.private_reactions),
            platform_posts=list(self.platform_posts),
            cross_reactions=list(self.cross_reactions),
            evidence_refs=["pack_ref"],
            confidence=0.8,
        )

    def test_rating_distribution(self) -> None:
        result = score_rating_distribution(self._context())
        self.assertGreaterEqual(result.predicted_mean_rating, 1.0)
        self.assertLessEqual(result.predicted_mean_rating, 5.0)
        self.assertIn("1_star", result.distribution)
        self.assertIn("confidence_band", result.to_dict())
        self.assertTrue(result.evidence_refs)

    def test_dnf_score(self) -> None:
        result = score_dnf(self._context())
        self.assertGreaterEqual(result.dnf_risk, 0.0)
        self.assertLessEqual(result.dnf_risk, 1.0)
        self.assertTrue(result.chapter_points)
        self.assertTrue(result.evidence_refs)

    def test_viral_potential(self) -> None:
        result = score_viral_potential(self._context())
        self.assertIn("goodreads", result.platform_scores)
        self.assertIn("booktok", result.platform_scores)
        self.assertGreater(len(result.top_platforms), 0)
        self.assertTrue(result.evidence_refs)

    def test_controversy_radar(self) -> None:
        result = score_controversy(self._context())
        self.assertGreaterEqual(result.controversy_risk, 0.0)
        self.assertLessEqual(result.controversy_risk, 1.0)
        self.assertIn("claim_hazard", result.radar)
        self.assertTrue(result.hotspots)

    def test_quoteability_score(self) -> None:
        result = score_quoteability(self._context())
        self.assertGreaterEqual(result.quoteability_score, 0.0)
        self.assertLessEqual(result.quoteability_score, 1.0)
        self.assertTrue(result.quote_candidates)
        self.assertTrue(result.evidence_refs)

    def test_polarization_score(self) -> None:
        result = score_polarization(self._context())
        self.assertGreaterEqual(result.polarization_score, 0.0)
        self.assertLessEqual(result.polarization_score, 1.0)
        self.assertIn("taste_split", result.component_scores)
        self.assertTrue(result.split_signals)

    def test_revision_priority(self) -> None:
        result = score_revision_priority(self._context())
        self.assertGreater(len(result.ranked_items), 0)
        self.assertIn(result.ranked_items[0].item_type, {"chapter", "claim", "style", "market"})
        self.assertTrue(result.evidence_refs)

    def test_deterministic_outputs(self) -> None:
        first = score_revision_priority(self._context()).to_dict()
        second = score_revision_priority(self._context()).to_dict()
        self.assertEqual(first, second)

    def _context(self) -> ScoringContext:
        return ScoringContext(evidence_pack=self.pack, simulation_run=self.run)


if __name__ == "__main__":
    unittest.main()
