"""Additional comprehensive edge cases and error boundary tests for Swarmbook Studio."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure backend app paths are resolved
BACKEND_ROOT = Path(__file__).resolve().parents[1]
BACKEND_APP_ROOT = BACKEND_ROOT / "app"
for root in (BACKEND_ROOT, BACKEND_APP_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from book_sim.comparison import DraftComparator
from book_sim.models import (
    BookProject,
    EvidencePack,
    SimulationRun,
    PrivateReaderReaction,
    BookDNA,
    ChapterMap,
    RiskMap,
    StyleMap,
    MarketSurface,
    ReaderPersona,
    ManuscriptInput,
)
from book_sim.provider_router import BookSimProviderRouter
from book_sim.scoring import (
    ScoringContext,
    score_rating_distribution,
    score_dnf,
    score_controversy,
)


class TestExtraScoringAndComparisonEdgeCases(unittest.TestCase):
    """Verifies behavior under edge inputs for DraftComparator and scoring routines."""

    def setUp(self) -> None:
        # Create minimal mock structures
        self.project = BookProject(
            project_id="proj_extra",
            name="Extra Edge Project",
            privacy_mode="local_only",
            draft_id="draft_x",
            version="v1",
            title="Boundary Test",
        )

        self.manuscript = ManuscriptInput(
            input_id="input_x",
            project_id="proj_extra",
            title="Boundary Test",
            text="Boundary content",
            privacy_mode="local_only",
            draft_id="draft_x",
            version="v1",
        )

        self.evidence = EvidencePack(
            pack_id="pack_x",
            project_id="proj_extra",
            draft_id="draft_x",
            version="v1",
            privacy_mode="local_only",
            manuscript_input=self.manuscript,
            book_dna=BookDNA(
                title="Boundary Test",
                premise="Premise",
                genre="fiction",
                book_type="fiction",
                tone="neutral",
                themes=[],
                spoilers_safe_summary="",
                evidence_refs=[],
            ),
            chapter_map=ChapterMap(book_id="book_x", chapters=[]),
            risk_map=RiskMap(book_id="book_x", risks=[]),
            style_map=StyleMap(book_id="book_x", style_notes=[], evidence_refs=[]),
            market_surface=MarketSurface(
                book_id="book_x",
                target_segments=[],
                discoverability_hooks=[],
                evidence_refs=[],
            ),
            evidence_refs=[],
            confidence=0.9,
        )

        self.persona = ReaderPersona(
            persona_id="persona_x",
            archetype_id="arch_x",
            display_name="Case Study",
            platform_home="reddit",
            review_style="analytical",
            platform="reddit",
            cohort="test",
            favorite_genres=[],
            disliked_patterns=[],
            dnf_threshold=0.5,
            delight_triggers=[],
            dnf_triggers=[],
            evidence_refs=[],
            confidence=0.9,
        )

        self.reaction = PrivateReaderReaction(
            reaction_id="reaction_x",
            simulation_id="sim_x",
            persona_id="persona_x",
            rating=5.0,  # Extreme rating boundary
            dnf_probability=0.0,
            sentiment="positive",
            attachment_score=1.0,
            confusion_score=0.0,
            recommendation_probability=1.0,
            praise=["Flawless layout"],
            friction=[],
            evidence_refs=[],
            confidence=0.9,
        )

        self.run = SimulationRun(
            run_id="sim_x",
            project_id="proj_extra",
            privacy_mode="local_only",
            draft_id="draft_x",
            version="v1",
            provider_route="local_ollama",
            status="completed",
            personas_count=1,
            reactions_count=1,
            posts_count=0,
            reader_personas=[self.persona],
            private_reactions=[self.reaction],
            platform_posts=[],
            cross_reactions=[],
            evidence_refs=[],
            confidence=0.9,
        )

    def test_compare_self_zero_deltas(self) -> None:
        """Comparing a draft version against itself should yield zero rating/risk deltas and empty qualitative sets."""
        comparator = DraftComparator()
        comparison = comparator.compare(
            project_id="proj_extra",
            base_evidence_pack=self.evidence,
            compare_evidence_pack=self.evidence,
            base_simulation_run=self.run,
            compare_simulation_run=self.run,
            simulation_seed=12345,
        )

        # Delta checks
        deltas = comparison.report.delta_scores
        self.assertEqual(deltas["rating_mean"]["delta"], 0.0)
        self.assertEqual(deltas["dnf_risk"]["delta"], 0.0)
        self.assertEqual(deltas["controversy_risk"]["delta"], 0.0)
        self.assertEqual(deltas["viral_mean"]["delta"], 0.0)
        self.assertEqual(deltas["quoteability_score"]["delta"], 0.0)

        # Empty sets or qualitative lists check
        self.assertEqual(len(comparison.report.what_improved), 0)
        self.assertEqual(len(comparison.report.what_got_worse), 0)
        self.assertEqual(len(comparison.report.still_blocking), 0)

    def test_extreme_scoring_boundaries(self) -> None:
        """Verifies scoring outputs when ratings are uniformly at maximum boundary."""
        context = ScoringContext(evidence_pack=self.evidence, simulation_run=self.run)
        rating_scores = score_rating_distribution(context)
        # 5.0 weighted mean (65%) blended with ~3.54 component estimation (35%) yields 4.491
        self.assertAlmostEqual(rating_scores.predicted_mean_rating, 4.491, places=3)

        # Verify DNF risk scoring works and returns ~0.217 baseline with empty maps and perfect reactions
        dnf_scores = score_dnf(context)
        self.assertAlmostEqual(dnf_scores.dnf_risk, 0.217, places=3)

        # Verify controversy risk scoring handles uniform ratings
        controversy_scores = score_controversy(context)
        self.assertAlmostEqual(controversy_scores.controversy_risk, 0.194, places=3)

    def test_privacy_guard_router_route_filtering(self) -> None:
        """Verifies router excludes cloud models when in local_only privacy mode, regardless of environment keys."""
        # Setup environment with external keys populated
        env = {
            "GEMINI_API_KEY": "dummy_gemini_key",
            "NVIDIA_API_KEY": "dummy_nvidia_key",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "BOOK_SIM_PROVIDER_TIMEOUT": "0.1",
        }
        router = BookSimProviderRouter(env=env)

        # Requesting a Gemini route with local_only constraint should route to local_ollama
        selection = router.select_route("gemini_fast", privacy_mode="local_only")
        self.assertEqual(selection.selected_route, "local_ollama")
        self.assertEqual(selection.provider_name, "ollama")


if __name__ == "__main__":
    unittest.main()
