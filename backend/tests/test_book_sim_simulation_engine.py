"""Tests for the Swarmbook simulation engine."""

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
    EvidencePack,
    ManuscriptInput,
    MarketSurface,
    RiskMap,
    RiskProfile,
    StyleMap,
)
from book_sim.reader_persona_generator import PersonaGenerationOverrides, ReaderPersonaGenerator
from book_sim.simulation import SimulationOrchestrator


class SimulationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        manuscript = ManuscriptInput(
            input_id="input_engine",
            project_id="proj_engine",
            title="Tiny Signal Book",
            text="A compact manuscript sample.",
            privacy_mode="local_only",
            draft_id="draft_engine",
            version="v1",
        )
        self.project = BookProject(
            project_id="proj_engine",
            name="Tiny Signal Project",
            privacy_mode="local_only",
            draft_id="draft_engine",
            version="v1",
            title="Tiny Signal Book",
            manuscript_input=manuscript,
        )
        self.pack = EvidencePack(
            pack_id="pack_engine",
            project_id="proj_engine",
            draft_id="draft_engine",
            version="v1",
            privacy_mode="local_only",
            manuscript_input=manuscript,
            book_dna=BookDNA(
                title="Tiny Signal Book",
                premise="A decision under pressure changes a small community.",
                genre="speculative fiction",
                book_type="fiction",
                tone="tense",
                themes=["trust", "responsibility"],
                spoilers_safe_summary="A difficult choice changes the group.",
                evidence_refs=["dna_ref"],
            ),
            chapter_map=ChapterMap(
                book_id="book_engine",
                chapters=[ChapterSummary(chapter_id="ch_1", chapter_number=1, title="Start", summary="Pressure arrives quickly.")],
            ),
            character_map=CharacterMap(
                book_id="book_engine",
                characters=[CharacterProfile(character_id="char_1", name="Mara", role="lead", evidence_refs=["char_ref"])],
            ),
            risk_map=RiskMap(
                book_id="book_engine",
                risks=[RiskProfile(risk_id="risk_1", risk_type="pacing_drag", evidence_refs=["risk_ref"])],
            ),
            style_map=StyleMap(book_id="book_engine", style_notes=["clean prose"]),
            market_surface=MarketSurface(book_id="book_engine", discoverability_hooks=["moral dilemma"], target_segments=["book clubs"]),
            evidence_refs=["pack_ref"],
            confidence=0.8,
        )

    def test_tiny_simulation_run_is_deterministic_and_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = LocalArtifactCache(base_dir=temp_dir)
            generator = ReaderPersonaGenerator()
            orchestrator = SimulationOrchestrator(
                persona_generator=generator,
                cache=cache,
                max_reaction_rounds=2,
                cross_reaction_posts=8,
            )
            overrides = PersonaGenerationOverrides(persona_count=5, allowed_platforms=["goodreads", "reddit", "bookclub", "booktok"])
            first = orchestrator.run(self.project, self.pack, simulation_seed=21, persona_overrides=overrides)
            second = orchestrator.run(self.project, self.pack, simulation_seed=21, persona_overrides=overrides)

        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.personas_count, 5)
        self.assertEqual(len(first.reader_personas), 5)
        self.assertEqual(len(first.private_reactions), 5)
        self.assertEqual(len(first.platform_posts), 5)
        self.assertLessEqual(len(first.cross_reactions), 10)
        self.assertTrue(all(len(reaction.reacted_post_ids) <= 7 for reaction in first.cross_reactions))
        self.assertEqual(first.metadata["max_parallel_jobs"], 1)


if __name__ == "__main__":
    unittest.main()
