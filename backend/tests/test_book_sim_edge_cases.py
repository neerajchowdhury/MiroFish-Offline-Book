"""Edge cases and error boundary tests for the Swarmbook Studio backend."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

try:
    from flask import Flask
except ImportError:
    Flask = None

# Ensure backend app paths are resolved
BACKEND_ROOT = Path(__file__).resolve().parents[1]
BACKEND_APP_ROOT = BACKEND_ROOT / "app"
for root in (BACKEND_ROOT, BACKEND_APP_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from app.api.book_sim import ApiError, _api_route
from book_sim.models import (
    BookProject,
    EvidencePack,
    SimulationRun,
    PrivateReaderReaction,
    PlatformPost,
    BookDNA,
    ChapterMap,
    RiskMap,
    StyleMap,
    MarketSurface,
    ReaderPersona,
    ManuscriptInput,
)
from book_sim.privacy_guard import PrivacyGuard, PrivacyViolationError
from book_sim.validators import (
    validate_privacy_mode,
    validate_positive_int,
    validate_non_empty_string,
    validate_max_length,
)
from book_sim.interrogation.persona_chat import PersonaInterrogator


class TestValidatorsEdgeCases(unittest.TestCase):
    """Verifies input validators with malformed inputs and boundary sizes."""

    def test_validate_privacy_mode_edge_cases(self) -> None:
        # Invalid privacy modes
        with self.assertRaises(ValueError) as ctx:
            validate_privacy_mode("ultra_secret_mode")
        self.assertIn("Unsupported privacy_mode", str(ctx.exception))

        # None/empty fallbacks
        self.assertEqual(validate_privacy_mode(None), "hybrid_safe")
        self.assertEqual(validate_privacy_mode(""), "hybrid_safe")
        self.assertEqual(validate_privacy_mode("   "), "hybrid_safe")

    def test_validate_positive_int_edge_cases(self) -> None:
        # Invalid string inputs
        with self.assertRaises(ValueError):
            validate_positive_int("not_a_number", "reader_count")
        with self.assertRaises(ValueError):
            validate_positive_int(None, "reader_count")

        # Zero and negative boundary checks
        with self.assertRaises(ValueError) as ctx:
            validate_positive_int(0, "reader_count", minimum=1)
        self.assertIn("must be >= 1", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            validate_positive_int(-5, "reader_count", minimum=1)
        self.assertIn("must be >= 1", str(ctx.exception))

    def test_validate_non_empty_string_edge_cases(self) -> None:
        # Spaces-only string check
        with self.assertRaises(ValueError) as ctx:
            validate_non_empty_string("     ", "projectName")
        self.assertIn("must not be empty", str(ctx.exception))

        # Int coercion fallback
        self.assertEqual(validate_non_empty_string(42, "projectName"), "42")


@unittest.skipIf(Flask is None, "Flask is not available in this Python environment")
class TestFlaskApiEdgeCases(unittest.TestCase):
    """Blueprint-level API testing for missing entities, socket failures, and route errors."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["BOOK_SIM_CACHE_DIR"] = self._tmpdir.name
        self.app.extensions["neo4j_storage"] = None

        from app.api import book_sim_bp
        self.app.register_blueprint(book_sim_bp, url_prefix="/api/book-sim")
        self.client = self.app.test_client()

        # Create a default project in setUp so it's always ready for ingestion/simulation tests!
        response = self.client.post(
            "/api/book-sim/projects",
            json={
                "name": "default_test_project",
                "privacy_mode": "local_only",
                "draft_id": "draft_default",
                "version": "v1",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.project_id = response.get_json()["data"]["project_id"]

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_create_project_empty_name(self) -> None:
        response = self.client.post("/api/book-sim/projects", json={"name": ""})
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertIn("error", payload)

    def test_create_project_invalid_profile(self) -> None:
        response = self.client.post(
            "/api/book-sim/projects",
            json={
                "name": "edge_project",
                "profile_name": "invalid_super_heavy_workstation",
            },
        )
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])

    def test_ingest_empty_text(self) -> None:
        response = self.client.post(
            "/api/book-sim/evidence-packs",
            json={
                "project_id": self.project_id,
                "title": "Book Title",
                "text": "   ",
            },
        )
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])

    def test_ingest_oversized_text(self) -> None:
        # Exceed characters limit (500,000 by default)
        oversized_text = "A" * 600_000
        response = self.client.post(
            "/api/book-sim/evidence-packs",
            json={
                "project_id": self.project_id,
                "title": "Oversized Title",
                "text": oversized_text,
            },
        )
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error_code"], "validation_error")

    def test_interrogate_missing_context(self) -> None:
        # Access persona chat directly without a prior simulation run
        response = self.client.post(
            "/api/book-sim/interrogate",
            json={
                "persona_id": "harsh_reviewer",
                "question": "What is your rating?",
            },
        )
        # Should raise validation_error for missing context payloads
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload["error_code"], "validation_error")

    def test_compare_mismatched_project_ids(self) -> None:
        response = self.client.post(
            "/api/book-sim/compare",
            json={
                "base_project_id": "proj_a",
                "compare_project_id": "proj_b",
            },
        )
        # Runtime database missing these project IDs will trigger a 404 validation error
        self.assertEqual(response.status_code, 404)
        payload = response.get_json()
        self.assertIn("no evidence pack", payload["error"].lower())

    @patch("app.api.book_sim._maybe_router")
    def test_health_check_socket_connection_failures(self, mock_maybe_router) -> None:
        # Simulate local Ollama and Neo4j servers offline by returning a router error string
        mock_maybe_router.return_value = (None, "Connection refused")

        response = self.app.test_client().get("/api/book-sim/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        # Sockets checked and verified as offline but endpoint itself survives and reports state
        self.assertFalse(payload["data"]["router"]["ok"])
        self.assertEqual(payload["data"]["router"]["error"], "Connection refused")


class TestPersonaInterrogatorFallbacks(unittest.TestCase):
    """Verifies that the interrogation responder recovers gracefully when stored reaction logs are missing."""

    def test_interrogation_fallback_praise_and_friction(self) -> None:
        # Create actual data models with empty/minimal attributes
        evidence = EvidencePack(
            pack_id="pack_edge",
            project_id="proj_edge",
            draft_id="draft_edge",
            version="v1",
            privacy_mode="local_only",
            manuscript_input=ManuscriptInput(
                input_id="input_edge",
                project_id="proj_edge",
                title="Title",
                text="Draft content",
                privacy_mode="local_only",
                draft_id="draft_edge",
                version="v1",
            ),
            book_dna=BookDNA(
                title="Title",
                premise="Premise",
                genre="genre",
                book_type="fiction",
                tone="tone",
                themes=[],
                spoilers_safe_summary="",
                evidence_refs=[],
            ),
            chapter_map=ChapterMap(book_id="book_edge", chapters=[]),
            risk_map=RiskMap(book_id="book_edge", risks=[]),
            style_map=StyleMap(book_id="book_edge", style_notes=[], evidence_refs=[]),
            market_surface=MarketSurface(
                book_id="book_edge",
                target_segments=[],
                discoverability_hooks=[],
                evidence_refs=[],
            ),
            evidence_refs=[],
            confidence=0.8,
        )

        persona = ReaderPersona(
            persona_id="persona_edge",
            archetype_id="arch_edge",
            display_name="Edge Casey",
            platform_home="goodreads",
            review_style="critical",
            platform="goodreads",
            cohort="cohort",
            favorite_genres=[],
            disliked_patterns=[],
            dnf_threshold=0.5,
            delight_triggers=[],
            dnf_triggers=[],
            evidence_refs=[],
            confidence=0.8,
        )

        reaction = PrivateReaderReaction(
            reaction_id="reaction_edge",
            simulation_id="sim_edge",
            persona_id="persona_edge",
            rating=3.0,
            dnf_probability=0.2,
            sentiment="neutral",
            attachment_score=0.5,
            confusion_score=0.1,
            recommendation_probability=0.5,
            praise=[],
            friction=[],
            evidence_refs=[],
            confidence=0.8,
        )

        run = SimulationRun(
            run_id="sim_edge",
            project_id="proj_edge",
            privacy_mode="local_only",
            draft_id="draft_edge",
            version="v1",
            provider_route="local_ollama",
            status="completed",
            personas_count=1,
            reactions_count=1,
            posts_count=0,
            reader_personas=[persona],
            private_reactions=[reaction],
            platform_posts=[],
            cross_reactions=[],
            evidence_refs=[],
            confidence=0.8,
        )

        interrogator = PersonaInterrogator()
        result = interrogator.interrogate(
            simulation_run=run,
            evidence_pack=evidence,
            persona_id="persona_edge",
            question="Why did you rate this book this way?",
        )

        self.assertEqual(result.persona_id, "persona_edge")
        self.assertTrue(result.answer)
        self.assertEqual(len(result.based_on), 0)


if __name__ == "__main__":
    unittest.main()
