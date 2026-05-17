"""Shared tests for synthetic platform adapters."""

from __future__ import annotations

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
    EvidencePack,
    ManuscriptInput,
    MarketSurface,
    PrivateReaderReaction,
    ReaderPersona,
    RiskMap,
    RiskProfile,
    StyleMap,
)
from book_sim.platform_adapters import AdapterContext, PLATFORM_ADAPTERS


REQUIRED_KEYS = {
    "goodreads": {"star_rating", "review_title", "review_body", "shelf_tags", "dnf_note", "quote_highlights", "evidence_refs"},
    "booktok": {"video_script", "trope_tags", "hook_line", "visual_motif", "viral_trigger", "cringe_mockery_risk", "evidence_refs"},
    "reddit": {"thread_title", "top_comment", "skeptical_comment", "debate_branch", "logic_framing_objection", "evidence_refs"},
    "bookstagram": {"caption", "carousel_idea", "aesthetic_tags", "quote_card_candidates", "save_share_reason", "evidence_refs"},
    "x": {"hot_take", "quote_tweet", "controversy_compression", "author_brand_reaction", "evidence_refs"},
    "newsletter": {"recommendation_blurb", "target_subscriber_type", "referral_likelihood", "evidence_refs"},
    "bookclub": {"discussion_questions", "moral_disagreement_points", "ending_debate_hooks", "evidence_refs"},
}


class PlatformAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        manuscript = ManuscriptInput(
            input_id="input_1",
            project_id="proj_1",
            title="Signal Book",
            text="One chapter of text.",
            privacy_mode="local_only",
        )
        self.project = BookProject(project_id="proj_1", name="Signal Project", manuscript_input=manuscript)
        self.pack = EvidencePack(
            pack_id="pack_1",
            project_id="proj_1",
            privacy_mode="local_only",
            manuscript_input=manuscript,
            book_dna=BookDNA(
                title="Signal Book",
                premise="A sharp premise with moral tension.",
                genre="speculative fiction",
                book_type="fiction",
                tone="tense",
                themes=["trust", "identity"],
                spoilers_safe_summary="A high-pressure choice changes everything.",
                evidence_refs=["dna_ref"],
            ),
            chapter_map=ChapterMap(
                book_id="book_1",
                chapters=[ChapterSummary(chapter_id="ch_1", chapter_number=1, title="Opening", summary="A difficult choice appears.")],
            ),
            character_map=CharacterMap(
                book_id="book_1",
                characters=[CharacterProfile(character_id="char_1", name="Mara", role="lead", evidence_refs=["char_ref"])],
            ),
            risk_map=RiskMap(
                book_id="book_1",
                risks=[RiskProfile(risk_id="risk_1", risk_type="pacing_drag", evidence_refs=["risk_ref"])],
            ),
            style_map=StyleMap(book_id="book_1", style_notes=["clean prose"]),
            market_surface=MarketSurface(book_id="book_1", discoverability_hooks=["moral dilemma"], target_segments=["book clubs"]),
            evidence_refs=["pack_ref"],
            confidence=0.8,
        )
        self.reaction = PrivateReaderReaction(
            reaction_id="private_1",
            simulation_id="sim_1",
            persona_id="persona_1",
            rating=4.2,
            dnf_probability=0.2,
            sentiment="positive",
            attachment_score=0.7,
            confusion_score=0.2,
            recommendation_probability=0.75,
            praise=["moral tension", "clean prose"],
            friction=["pacing_drag"],
            notable_quotes=["A high-pressure choice changes everything."],
            evidence_refs=["private_ref"],
            confidence=0.82,
        )

    def _persona(self, platform: str) -> ReaderPersona:
        return ReaderPersona(
            persona_id=f"persona_{platform}",
            archetype_id=f"arch_{platform}",
            display_name=f"{platform.title()} Reader",
            platform_home=platform,
            review_style="critical_balanced",
            platform=platform,
            cohort=f"{platform}_cohort",
            favorite_genres=["speculative fiction"],
            disliked_patterns=["pacing_drag"],
            delight_triggers=["moral tension"],
            influence_weight=0.6,
            quote_sharing_probability=0.55,
            evidence_focus=0.7,
            confidence=0.8,
        )

    def test_each_required_adapter_returns_structured_payload(self) -> None:
        for platform, required_keys in REQUIRED_KEYS.items():
            with self.subTest(platform=platform):
                adapter = PLATFORM_ADAPTERS[platform]()
                post = adapter.create_post(
                    persona=self._persona(platform),
                    evidence_pack=self.pack,
                    private_reaction=self.reaction,
                    context=AdapterContext(simulation_id="sim_1", round_number=1, privacy_mode="local_only", simulation_seed=7),
                )
                self.assertEqual(post.platform, platform)
                self.assertTrue(required_keys.issubset(post.payload.keys()))
                self.assertGreater(len(post.evidence_refs), 0)
                self.assertGreater(len(post.payload.get("evidence_refs", [])), 0)


if __name__ == "__main__":
    unittest.main()
