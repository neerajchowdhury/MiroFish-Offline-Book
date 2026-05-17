"""End-to-end tests for manuscript ingestion and evidence-pack generation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.evidence_pack_builder import EvidencePackBuilder
from book_sim.local_cache import LocalArtifactCache
from book_sim.models import BookProject, ManuscriptInput


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class FakeRouter:
    """Capture route usage and return deterministic JSON outputs."""

    def __init__(self) -> None:
        self.calls = []

    def generate_json(
        self,
        prompt: str,
        route_name: str = "local_ollama",
        privacy_mode: str = "hybrid_safe",
        system_prompt: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ):
        self.calls.append(
            {
                "route_name": route_name,
                "privacy_mode": privacy_mode,
                "prompt": prompt,
            }
        )
        if "Create Book DNA JSON" in prompt:
            book_type = "nonfiction" if "Book type: nonfiction" in prompt else "fiction" if "Book type: fiction" in prompt else "mixed_unknown"
            return {
                "title": "Synthetic Book DNA",
                "premise": "A concise synthesis of the manuscript.",
                "genre": "nonfiction" if book_type == "nonfiction" else "literary fiction",
                "subgenre": "strategy" if book_type == "nonfiction" else "psychological drama",
                "tone": "measured",
                "emotional_promise": "clarity and tension",
                "narrative_engine": "argument" if book_type == "nonfiction" else "mystery",
                "reading_difficulty": "medium",
                "target_reader": "practical readers" if book_type == "nonfiction" else "fiction readers",
                "comparable_titles": ["Comp A", "Comp B"],
                "themes": ["trust", "change"],
                "spoilers_safe_summary": "A high-level summary.",
                "confidence": 0.81,
            }
        return {
            "summary": "Condensed chapter summary.",
            "emotional_beats": ["tension", "hope"],
            "chapter_function": "escalation",
            "pacing": "measured",
            "pacing_note": "Balanced movement and reflection.",
            "likely_reader_friction": ["light_density"],
            "key_beats": ["beat one", "beat two"],
            "confidence": 0.75,
        }


class TestEvidencePackBuilder(unittest.TestCase):
    def _load_fixture(self, name: str) -> str:
        return (FIXTURES_DIR / name).read_text(encoding="utf-8")

    def _build_project(self, text: str, title: str) -> tuple[BookProject, ManuscriptInput]:
        manuscript = ManuscriptInput(
            input_id=f"input_{title}",
            project_id=f"proj_{title}",
            title=title,
            text=text,
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
        )
        project = BookProject(
            project_id=f"proj_{title}",
            name=title,
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
            title=title,
            manuscript_input=manuscript,
        )
        return project, manuscript

    def test_fiction_evidence_pack_generation(self) -> None:
        text = self._load_fixture("book_sim_fiction_sample.txt")
        router = FakeRouter()
        with tempfile.TemporaryDirectory() as temp_dir:
            builder = EvidencePackBuilder(model_router=router, cache=LocalArtifactCache(base_dir=temp_dir))
            project, manuscript = self._build_project(text, "Fiction Sample")
            pack = builder.build_from_manuscript(project, manuscript)
            calls_after_first_build = len(router.calls)
            cached_pack = builder.build_from_manuscript(project, manuscript)

        self.assertEqual(pack.pack_id, cached_pack.pack_id)
        self.assertEqual(calls_after_first_build, len(router.calls))
        self.assertEqual(pack.book_dna.book_type, "fiction")
        self.assertGreaterEqual(pack.chapter_map.total_chapters, 2)
        self.assertGreater(len(pack.character_map.characters), 0)
        self.assertEqual(len(pack.claim_map.claims), 0)
        self.assertIsNotNone(pack.style_map)
        self.assertIsNotNone(pack.risk_map)
        self.assertIsNotNone(pack.market_surface)
        self.assertIn("local_ollama", [call["route_name"] for call in router.calls])
        self.assertIn("gemini_fast", [call["route_name"] for call in router.calls])

    def test_nonfiction_evidence_pack_generation(self) -> None:
        text = self._load_fixture("book_sim_nonfiction_sample.txt")
        router = FakeRouter()
        with tempfile.TemporaryDirectory() as temp_dir:
            builder = EvidencePackBuilder(model_router=router, cache=LocalArtifactCache(base_dir=temp_dir))
            project, manuscript = self._build_project(text, "Nonfiction Sample")
            pack = builder.build_from_manuscript(project, manuscript)

        self.assertEqual(pack.book_dna.book_type, "nonfiction")
        self.assertGreaterEqual(pack.chapter_map.total_chapters, 2)
        self.assertGreater(len(pack.claim_map.claims), 0)
        self.assertEqual(len(pack.character_map.characters), 0)
        self.assertTrue(any(claim.factual_risk_flags or claim.evidence_items for claim in pack.claim_map.claims))
        self.assertIsNotNone(pack.style_map)
        self.assertIsNotNone(pack.risk_map)
        self.assertIsNotNone(pack.market_surface)


if __name__ == "__main__":
    unittest.main()
