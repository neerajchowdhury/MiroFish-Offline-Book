"""Tests for Swarmbook graph persistence."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.graph_persistence import BookGraphPersistence
from book_sim.models import (
    BookDNA,
    BookProject,
    ChapterMap,
    ChapterSummary,
    CharacterMap,
    CharacterProfile,
    ClaimMap,
    ClaimProfile,
    EvidencePack,
    MarketSurface,
    ManuscriptInput,
    RiskMap,
    RiskProfile,
    SimulationRun,
    StyleMap,
)


class FakeTx:
    def __init__(self, statements):
        self.statements = statements

    def run(self, query, **params):
        self.statements.append((query, params))
        return None


class FakeSession:
    def __init__(self):
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def run(self, query):
        self.statements.append((query, {}))
        return None

    def execute_write(self, callback):
        return callback(FakeTx(self.statements))


class FakeDriver:
    def __init__(self):
        self.session_obj = FakeSession()

    def session(self):
        return self.session_obj


class BookGraphPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        manuscript = ManuscriptInput(
            input_id="input_a",
            project_id="proj_a",
            title="The Test Draft",
            text="Chapter one.",
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
        )
        project = BookProject(
            project_id="proj_a",
            name="Project A",
            privacy_mode="hybrid_safe",
            draft_id="draft_a",
            version="v1",
            title="The Test Draft",
            manuscript_input=manuscript,
        )
        chapter = ChapterSummary(chapter_id="ch_1", chapter_number=1, title="Opening", summary="Intro")
        character = CharacterProfile(character_id="char_1", name="Mara", role="lead")
        claim = ClaimProfile(claim_id="claim_1", claim_text="The premise holds.", evidence_refs=["e1"])
        risk = RiskProfile(risk_id="risk_1", risk_type="pacing")
        self.pack = EvidencePack(
            pack_id="pack_1",
            project_id="proj_a",
            draft_id="draft_a",
            version="v1",
            privacy_mode="hybrid_safe",
            manuscript_input=manuscript,
            book_dna=BookDNA(title="The Test Draft", premise="A test premise", genre="fiction"),
            chapter_map=ChapterMap(book_id="book_a", chapters=[chapter]),
            character_map=CharacterMap(book_id="book_a", characters=[character]),
            claim_map=ClaimMap(book_id="book_a", claims=[claim]),
            risk_map=RiskMap(book_id="book_a", risks=[risk]),
            style_map=StyleMap(book_id="book_a", prose_density="medium"),
            market_surface=MarketSurface(book_id="book_a", target_segments=["fiction readers"]),
        )
        self.project = project

    def test_dry_run_namespaces_book_artifacts(self) -> None:
        persister = BookGraphPersistence(dry_run=True)
        result = persister.persist_evidence_pack(self.project, self.pack, book_id="book_a")

        self.assertTrue(result.dry_run)
        self.assertEqual(result.namespace, "book_sim:proj_a:book_a:draft_a")
        self.assertGreater(result.nodes_upserted, 0)
        self.assertIn("Book", result.artifacts)
        self.assertIn("MarketSurface", result.artifacts)

    def test_real_driver_uses_merge_based_writes(self) -> None:
        driver = FakeDriver()
        persister = BookGraphPersistence(driver=driver)
        result = persister.persist_evidence_pack(self.project, self.pack, book_id="book_a")

        self.assertFalse(result.dry_run)
        self.assertGreater(len(driver.session_obj.statements), 0)
        queries = [stmt[0] for stmt in driver.session_obj.statements]
        self.assertTrue(any("MERGE (n:`Book`" in query for query in queries))
        self.assertTrue(any("MERGE (src)-[r:`HAS_CHAPTER`" in query for query in queries))
        self.assertTrue(any("MERGE (src)-[r:`SUPPORTS`" in query for query in queries))

    def test_simulation_artifacts_are_prepared_but_not_overbuilt(self) -> None:
        driver = FakeDriver()
        persister = BookGraphPersistence(driver=driver)
        sim = SimulationRun(run_id="run_1", project_id="proj_a", draft_id="draft_a", version="v1")
        result = persister.persist_simulation_artifacts(self.project, sim)

        self.assertFalse(result.dry_run)
        queries = [stmt[0] for stmt in driver.session_obj.statements]
        self.assertTrue(any("MERGE (n:`Draft`" in query for query in queries))
        self.assertFalse(any("PlatformPost" in query and "platform adapter" in query for query in queries))


if __name__ == "__main__":
    unittest.main()
