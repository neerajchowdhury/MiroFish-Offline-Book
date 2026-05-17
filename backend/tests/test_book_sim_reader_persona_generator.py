"""Tests for reader archetype loading and persona generation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.reader_archetype_loader import ReaderArchetypeLoader
from book_sim.reader_persona_generator import (
    PersonaGenerationOverrides,
    ReaderPersonaGenerator,
)


class FakeRouter:
    def __init__(self) -> None:
        self.calls = []

    def generate_json(self, **kwargs):
        self.calls.append(kwargs)
        return {"private_bias": "slightly_more_open"}


class ReaderPersonaGeneratorTests(unittest.TestCase):
    def test_loader_normalizes_archetypes(self) -> None:
        catalog = ReaderArchetypeLoader.from_yaml()

        self.assertGreaterEqual(len(catalog.archetypes), 10)
        nonfiction_only = [item for item in catalog.archetypes if item.archetype_id.startswith("nonfiction_")]
        self.assertTrue(all(item.book_type_suitability == ["nonfiction"] for item in nonfiction_only))
        self.assertTrue(all(item.cohort for item in catalog.archetypes))

    def test_same_seed_produces_identical_personas(self) -> None:
        generator = ReaderPersonaGenerator()

        first = generator.generate(book_type="fiction", privacy_mode="hybrid_safe", simulation_seed=17)
        second = generator.generate(book_type="fiction", privacy_mode="hybrid_safe", simulation_seed=17)

        self.assertEqual([persona.to_dict() for persona in first], [persona.to_dict() for persona in second])
        self.assertEqual(len(first), 30)

    def test_local_only_default_count_and_constraints(self) -> None:
        generator = ReaderPersonaGenerator()
        personas = generator.generate(book_type="nonfiction", privacy_mode="local_only", simulation_seed=9)

        self.assertGreaterEqual(len(personas), 12)
        self.assertLessEqual(len(personas), 20)
        self.assertEqual(len(personas), 16)
        self.assertTrue(all("local_processing_only" in persona.privacy_constraints for persona in personas))

    def test_overrides_adjust_count_and_filtering(self) -> None:
        generator = ReaderPersonaGenerator()
        personas = generator.generate(
            book_type="nonfiction",
            privacy_mode="hybrid_safe",
            simulation_seed=5,
            overrides=PersonaGenerationOverrides(
                persona_count=14,
                allowed_platforms=["reddit", "bookclub"],
            ),
        )

        self.assertEqual(len(personas), 14)
        self.assertTrue(all(persona.platform in {"reddit", "bookclub"} for persona in personas))

    def test_llm_enrichment_is_optional(self) -> None:
        router = FakeRouter()
        generator = ReaderPersonaGenerator(model_router=router)

        generator.generate(book_type="fiction", privacy_mode="hybrid_safe", simulation_seed=99)

        self.assertEqual(router.calls, [])


if __name__ == "__main__":
    unittest.main()
