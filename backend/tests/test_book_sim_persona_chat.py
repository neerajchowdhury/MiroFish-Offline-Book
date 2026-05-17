"""Tests for Swarmbook reader persona interrogation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

try:
    from flask import Flask
except ImportError:  # pragma: no cover - route test is optional in minimal environments
    Flask = None


BACKEND_ROOT = Path(__file__).resolve().parents[1]
BACKEND_APP_ROOT = BACKEND_ROOT / "app"
for root in (BACKEND_ROOT, BACKEND_APP_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from book_sim.interrogation import PersonaInterrogator
from book_sim.models import (
    BookDNA,
    ChapterMap,
    ChapterSummary,
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

if Flask is not None:
    from app.api import book_sim_bp
else:  # pragma: no cover - exercised only in environments without Flask
    book_sim_bp = None


class PersonaChatTests(unittest.TestCase):
    def setUp(self) -> None:
        manuscript = ManuscriptInput(
            input_id="input_chat",
            project_id="proj_chat",
            title="Pressure Book",
            text="A compact test manuscript.",
            privacy_mode="local_only",
            draft_id="draft_chat",
            version="v1",
        )
        self.evidence_pack = EvidencePack(
            pack_id="pack_chat",
            project_id="proj_chat",
            draft_id="draft_chat",
            version="v1",
            privacy_mode="local_only",
            manuscript_input=manuscript,
            book_dna=BookDNA(
                title="Pressure Book",
                premise="A hard choice splits a community.",
                genre="speculative fiction",
                book_type="fiction",
                tone="tense",
                themes=["trust", "responsibility"],
                spoilers_safe_summary="A hard choice changes the town.",
                evidence_refs=["dna_ref"],
            ),
            chapter_map=ChapterMap(
                book_id="book_chat",
                chapters=[
                    ChapterSummary(
                        chapter_id="ch_1",
                        chapter_number=1,
                        title="Start",
                        summary="The pressure arrives early.",
                        likely_reader_friction=["dense setup"],
                        evidence_refs=["chapter_ref"],
                    )
                ],
            ),
            risk_map=RiskMap(
                book_id="book_chat",
                risks=[
                    RiskProfile(
                        risk_id="risk_1",
                        risk_type="pacing_drag",
                        mitigation_hint="tightening pacing where momentum sags",
                        evidence_refs=["risk_ref"],
                    )
                ],
            ),
            style_map=StyleMap(
                book_id="book_chat",
                style_notes=["clean prose"],
                evidence_refs=["style_ref"],
            ),
            market_surface=MarketSurface(
                book_id="book_chat",
                target_segments=["book club readers", "speculative fiction loyalists"],
                discoverability_hooks=["moral dilemma"],
                evidence_refs=["market_ref"],
            ),
            evidence_refs=["pack_ref"],
            confidence=0.82,
        )
        self.persona = ReaderPersona(
            persona_id="persona_casey",
            archetype_id="arch_casey",
            display_name="Casey",
            platform_home="goodreads",
            review_style="critical_balanced",
            platform="goodreads",
            cohort="community_reviewers",
            favorite_genres=["speculative fiction", "character depth"],
            disliked_patterns=["padding"],
            dnf_threshold=0.6,
            delight_triggers=["clean prose"],
            dnf_triggers=["slow_start"],
            evidence_refs=["persona_ref"],
            confidence=0.76,
        )
        other_persona = ReaderPersona(
            persona_id="persona_morgan",
            archetype_id="arch_morgan",
            display_name="Morgan",
            platform_home="booktok",
            review_style="emotional_confessional",
            platform="booktok",
            cohort="emotion_seekers",
            favorite_genres=["trust", "responsibility"],
            disliked_patterns=["pacing_drag"],
            dnf_threshold=0.4,
            delight_triggers=["moral dilemma"],
            dnf_triggers=["pacing_drag"],
            evidence_refs=["persona_morgan_ref"],
            confidence=0.79,
        )
        reaction = PrivateReaderReaction(
            reaction_id="reaction_casey",
            simulation_id="sim_chat",
            persona_id="persona_casey",
            rating=4.1,
            dnf_probability=0.38,
            sentiment="mixed",
            attachment_score=0.66,
            confusion_score=0.43,
            recommendation_probability=0.64,
            praise=["clean prose", "moral tension"],
            friction=["padding"],
            notable_quotes=["A hard choice changes the town."],
            evidence_refs=["reaction_ref"],
            confidence=0.74,
        )
        other_reaction = PrivateReaderReaction(
            reaction_id="reaction_morgan",
            simulation_id="sim_chat",
            persona_id="persona_morgan",
            rating=2.9,
            dnf_probability=0.69,
            sentiment="negative",
            attachment_score=0.41,
            confusion_score=0.61,
            recommendation_probability=0.31,
            praise=["moral dilemma"],
            friction=["pacing_drag"],
            evidence_refs=["reaction_morgan_ref"],
            confidence=0.71,
        )
        post = PlatformPost(
            post_id="post_casey",
            simulation_id="sim_chat",
            persona_id="persona_casey",
            platform="goodreads",
            round_number=1,
            title="Strong premise, soft middle",
            body="The atmosphere worked for me more than the middle did.",
            rating=4.1,
            payload={"review_title": "Strong premise, soft middle", "evidence_refs": ["reaction_ref"]},
            engagement_prediction=0.51,
            sentiment="mixed",
            evidence_refs=["post_ref"],
            confidence=0.7,
        )
        other_post = PlatformPost(
            post_id="post_morgan",
            simulation_id="sim_chat",
            persona_id="persona_morgan",
            platform="booktok",
            round_number=1,
            title="Needed more momentum",
            body="I wanted it to hit faster.",
            rating=2.9,
            payload={"hook_line": "Needed more momentum", "evidence_refs": ["reaction_morgan_ref"]},
            engagement_prediction=0.74,
            sentiment="negative",
            evidence_refs=["post_morgan_ref"],
            confidence=0.69,
        )
        cross = CrossReaction(
            reaction_id="cross_casey",
            simulation_id="sim_chat",
            source_post_id="post_casey",
            target_post_id="post_morgan",
            persona_id="persona_casey",
            platform="goodreads",
            reacted_post_ids=["post_casey", "post_morgan"],
            stance_shift="more_negative",
            agree_probability=0.33,
            disagree_probability=0.67,
            reply_likelihood=0.42,
            rating_shift=-0.1,
            recommendation_shift=-0.08,
            sentiment="mixed",
            evidence_refs=["cross_ref"],
            confidence=0.68,
        )
        self.simulation_run = SimulationRun(
            run_id="sim_chat",
            project_id="proj_chat",
            privacy_mode="local_only",
            draft_id="draft_chat",
            version="v1",
            provider_route="local_ollama",
            status="completed",
            personas_count=2,
            reactions_count=2,
            posts_count=2,
            reader_personas=[self.persona, other_persona],
            private_reactions=[reaction, other_reaction],
            platform_posts=[post, other_post],
            cross_reactions=[cross],
            evidence_refs=["run_ref"],
            confidence=0.81,
        )

    def test_rating_answer_is_grounded(self) -> None:
        result = PersonaInterrogator().interrogate(
            simulation_run=self.simulation_run,
            evidence_pack=self.evidence_pack,
            persona_id="persona_casey",
            question="Why did you rate this book this way?",
        )

        self.assertEqual(result.intent, "rating_why")
        self.assertIn("4.10", result.answer)
        self.assertIn("reaction_ref", result.based_on)
        self.assertIn("risk_ref", result.based_on)
        self.assertIn("rating", result.signals)

    def test_dnf_answer_does_not_claim_unseen_detail(self) -> None:
        result = PersonaInterrogator().interrogate(
            simulation_run=self.simulation_run,
            evidence_pack=self.evidence_pack,
            persona_id="persona_casey",
            question="Why did you DNF?",
        )

        self.assertEqual(result.intent, "dnf_why")
        self.assertIn("DNF pressure", result.answer)
        self.assertIn("risk_ref", result.based_on)
        self.assertIn("stored signals", result.answer)

    def test_audience_fit_uses_other_personas(self) -> None:
        result = PersonaInterrogator().interrogate(
            simulation_run=self.simulation_run,
            evidence_pack=self.evidence_pack,
            persona_id="persona_casey",
            question="Which reader would love or hate it?",
        )

        self.assertEqual(result.intent, "audience_fit")
        self.assertIn("Morgan", result.answer)
        self.assertIn("persona_morgan_ref", result.based_on)

    @unittest.skipIf(Flask is None, "Flask is not available in this Python environment")
    def test_route_returns_structured_json(self) -> None:
        app = Flask(__name__)
        app.register_blueprint(book_sim_bp, url_prefix="/api/book-sim")
        client = app.test_client()

        response = client.post(
            "/api/book-sim/interrogate",
            json={
                "persona_id": "persona_casey",
                "question": "Would you recommend this book?",
                "simulation_run": self.simulation_run.to_dict(),
                "evidence_pack": self.evidence_pack.to_dict(),
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["intent"], "recommend")
        self.assertTrue(payload["data"]["based_on"])


if __name__ == "__main__":
    unittest.main()
