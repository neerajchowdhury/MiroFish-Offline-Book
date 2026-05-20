"""API tests for additive Swarmbook backend routes."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from flask import Flask
except ImportError:  # pragma: no cover - route tests are optional in minimal environments
    Flask = None


BACKEND_ROOT = Path(__file__).resolve().parents[1]
BACKEND_APP_ROOT = BACKEND_ROOT / "app"
for root in (BACKEND_ROOT, BACKEND_APP_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

if Flask is not None:
    from app.api import book_sim_bp
else:  # pragma: no cover - exercised only in environments without Flask
    book_sim_bp = None


@unittest.skipIf(Flask is None, "Flask is not available in this Python environment")
class BookSimApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._previous_timeout = os.environ.get("BOOK_SIM_PROVIDER_TIMEOUT")
        os.environ["BOOK_SIM_PROVIDER_TIMEOUT"] = "0.1"

        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["BOOK_SIM_CACHE_DIR"] = self._tmpdir.name
        app.extensions["neo4j_storage"] = None
        app.register_blueprint(book_sim_bp, url_prefix="/api/book-sim")
        self.client = app.test_client()

    def tearDown(self) -> None:
        if self._previous_timeout is None:
            os.environ.pop("BOOK_SIM_PROVIDER_TIMEOUT", None)
        else:
            os.environ["BOOK_SIM_PROVIDER_TIMEOUT"] = self._previous_timeout
        self._tmpdir.cleanup()

    def test_project_ingest_simulate_report_and_persona_chat(self) -> None:
        project_id = self._create_project(
            name="Pressure Project A",
            privacy_mode="local_only",
            draft_id="draft_a",
            version="v1",
        )
        ingest = self.client.post(
            "/api/book-sim/evidence-packs",
            json={
                "project_id": project_id,
                "title": "Pressure Book",
                "author_name": "A. Writer",
                "text": _draft_text("The decision is delayed, and the town grows impatient."),
            },
        )
        self.assertEqual(ingest.status_code, 201)
        ingest_payload = ingest.get_json()
        self.assertTrue(ingest_payload["success"])
        self.assertTrue(ingest_payload["data"]["evidence_pack"]["pack_id"])

        simulate = self.client.post(
            "/api/book-sim/simulate",
            json={
                "project_id": project_id,
                "simulation_seed": 17,
                "route_name": "gemini_fast",
            },
        )
        self.assertEqual(simulate.status_code, 201)
        simulate_payload = simulate.get_json()
        self.assertTrue(simulate_payload["success"])
        self.assertEqual(simulate_payload["data"]["route_selection"]["selected_route"], "local_ollama")
        self.assertEqual(simulate_payload["data"]["simulation_run"]["metadata"]["seed"], 17)
        self.assertIn("report_markdown", simulate_payload["data"])
        self.assertIn("# Swarmbook Report", simulate_payload["data"]["report_markdown"])
        report_id = simulate_payload["data"]["report"]["report_id"]
        persona_id = simulate_payload["data"]["simulation_run"]["reader_personas"][0]["persona_id"]

        report = self.client.get(f"/api/book-sim/projects/{project_id}/report")
        self.assertEqual(report.status_code, 200)
        report_payload = report.get_json()
        self.assertTrue(report_payload["success"])
        self.assertEqual(report_payload["data"]["report_id"], report_id)
        self.assertTrue(report_payload["data"]["scorecard"])

        chat = self.client.post(
            f"/api/book-sim/personas/{persona_id}/chat",
            json={
                "project_id": project_id,
                "question": "Why did you rate this book this way?",
            },
        )
        self.assertEqual(chat.status_code, 200)
        chat_payload = chat.get_json()
        self.assertTrue(chat_payload["success"])
        self.assertEqual(chat_payload["data"]["persona_id"], persona_id)
        self.assertTrue(chat_payload["data"]["based_on"])

    def test_compare_and_health_routes(self) -> None:
        base_project_id = self._create_project(
            name="Pressure Project Base",
            privacy_mode="local_only",
            draft_id="draft_base",
            version="v1",
        )
        compare_project_id = self._create_project(
            name="Pressure Project Compare",
            privacy_mode="local_only",
            draft_id="draft_compare",
            version="v2",
        )
        self._ingest_and_simulate(
            project_id=base_project_id,
            title="Pressure Book A",
            text=_draft_text("The middle lingers before the choice arrives."),
            simulation_seed=23,
        )
        self._ingest_and_simulate(
            project_id=compare_project_id,
            title="Pressure Book B",
            text=_draft_text("The choice lands early and the consequences escalate."),
            simulation_seed=23,
        )

        compare = self.client.post(
            "/api/book-sim/compare",
            json={
                "project_id": "proj_compare_runtime",
                "base_project_id": base_project_id,
                "compare_project_id": compare_project_id,
                "simulation_seed": 23,
            },
        )
        self.assertEqual(compare.status_code, 200)
        compare_payload = compare.get_json()
        self.assertTrue(compare_payload["success"])
        self.assertIn("markdown", compare_payload["data"])
        self.assertIn("## What Improved", compare_payload["data"]["markdown"])
        self.assertEqual(compare_payload["data"]["report"]["metadata"]["simulation_seed"], 23)

        health = self.client.get("/api/book-sim/health")
        self.assertEqual(health.status_code, 200)
        health_payload = health.get_json()
        self.assertTrue(health_payload["success"])
        self.assertIn("router", health_payload["data"])
        self.assertIn("providers", health_payload["data"])
        self.assertIn("neo4j", health_payload["data"])
        self.assertIn("ollama", health_payload["data"])
        self.assertIn("profiles", health_payload["data"])
        self.assertEqual(health_payload["data"]["profiles"]["default_profile"], "hybrid_safe_default")
        self.assertTrue(health_payload["data"]["profiles"]["items"])
        cloud_profile = next(
            item for item in health_payload["data"]["profiles"]["items"] if item["profile_name"] == "cloud_quality"
        )
        cloud_warning_text = " ".join(warning["message"].lower() for warning in cloud_profile["computed_warnings"])
        self.assertIn("cloud", cloud_warning_text)
        self.assertIn("slower", cloud_warning_text)

    def test_project_defaults_to_hybrid_safe_profile(self) -> None:
        response = self.client.post(
            "/api/book-sim/projects",
            json={"name": "Profile Default Project"},
        )
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["privacy_mode"], "hybrid_safe")
        self.assertEqual(payload["data"]["metadata"]["local_profile"], "hybrid_safe_default")
        self.assertTrue(payload["data"]["metadata"]["local_profile_warnings"])

    def _create_project(self, name: str, privacy_mode: str, draft_id: str, version: str) -> str:
        response = self.client.post(
            "/api/book-sim/projects",
            json={
                "name": name,
                "privacy_mode": privacy_mode,
                "draft_id": draft_id,
                "version": version,
            },
        )
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        return payload["data"]["project_id"]

    def _ingest_and_simulate(self, project_id: str, title: str, text: str, simulation_seed: int) -> None:
        ingest = self.client.post(
            "/api/book-sim/evidence-packs",
            json={"project_id": project_id, "title": title, "text": text},
        )
        self.assertEqual(ingest.status_code, 201)

        simulate = self.client.post(
            "/api/book-sim/simulate",
            json={"project_id": project_id, "simulation_seed": simulation_seed},
        )
        self.assertEqual(simulate.status_code, 201)


def _draft_text(pivot_line: str) -> str:
    return (
        "Chapter 1\n"
        "Mara arrives at the town hall carrying a secret.\n\n"
        "Chapter 2\n"
        f"{pivot_line}\n\n"
        "Chapter 3\n"
        "The public cost becomes impossible to ignore."
    )


if __name__ == "__main__":
    unittest.main()
