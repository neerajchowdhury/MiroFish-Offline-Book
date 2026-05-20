"""Tiny local-only end-to-end smoke test for Swarmbook."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.comparison import DraftComparator
from book_sim.evidence_pack_builder import EvidencePackBuilder
from book_sim.graph_persistence import BookGraphPersistence
from book_sim.interrogation import PersonaInterrogator
from book_sim.local_cache import LocalArtifactCache
from book_sim.local_profiles import LocalProfileLoader
from book_sim.models import BookProject, ManuscriptInput
from book_sim.provider_router import BookSimProviderRouter
from book_sim.reader_persona_generator import PersonaGenerationOverrides
from book_sim.report_builder import build_prediction_report
from book_sim.report_markdown import render_prediction_report_markdown
from book_sim.scoring import (
    ScoringContext,
    score_controversy,
    score_dnf,
    score_quoteability,
    score_rating_distribution,
    score_viral_potential,
)
from book_sim.simulation import SimulationOrchestrator


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TinySwarmbookE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self._previous_env = {
            "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
            "NVIDIA_API_KEY": os.environ.get("NVIDIA_API_KEY"),
            "NVIDIA_BASE_URL": os.environ.get("NVIDIA_BASE_URL"),
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
            "BOOK_SIM_PROVIDER_TIMEOUT": os.environ.get("BOOK_SIM_PROVIDER_TIMEOUT"),
        }
        for key in ("GEMINI_API_KEY", "NVIDIA_API_KEY", "NVIDIA_BASE_URL", "OPENAI_API_KEY"):
            os.environ.pop(key, None)
        os.environ["BOOK_SIM_PROVIDER_TIMEOUT"] = "0.01"

    def tearDown(self) -> None:
        for key, value in self._previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_tiny_local_only_pipeline_exports_and_compares(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = LocalArtifactCache(base_dir=temp_dir)
            output_dir = Path(temp_dir) / "swarmbook_e2e_outputs"
            output_dir.mkdir()

            profile = LocalProfileLoader().get_profile("local_tiny")
            self.assertIsNotNone(profile)
            self.assertEqual(profile.privacy_mode, "local_only")
            self.assertFalse(profile.allow_external_models)

            router = BookSimProviderRouter(env=self._router_env())
            external_health = router.get_provider_for_route("gemini_fast").health_check()
            self.assertFalse(external_health["ok"])
            selection = router.select_route("gemini_deep", privacy_mode="local_only")
            self.assertEqual(selection.selected_route, "local_ollama")
            self.assertEqual(selection.provider_name, "ollama")

            project, pack, run = self._run_pipeline(
                cache=cache,
                manuscript_name="tiny_fiction_manuscript.txt",
                draft_id="draft_a",
                version="v1",
            )
            self.assertEqual(pack.privacy_mode, "local_only")
            self.assertGreaterEqual(len(pack.chapter_map.chapters), 1)

            dry_pack = BookGraphPersistence(dry_run=True).persist_evidence_pack(project, pack)
            self.assertTrue(dry_pack.dry_run)
            self.assertGreater(dry_pack.nodes_upserted, 0)

            self.assertEqual(run.privacy_mode, "local_only")
            self.assertEqual(run.provider_route, "local_ollama")
            self.assertEqual(run.personas_count, 4)
            self.assertEqual(run.total_rounds, 1)
            self.assertEqual(run.metadata["cross_reaction_posts"], 2)
            self.assertEqual(run.metadata["max_parallel_jobs"], 1)
            self.assertTrue(run.platform_posts)
            self.assertTrue({post.platform for post in run.platform_posts} <= {"goodreads", "reddit", "x"})

            dry_sim = BookGraphPersistence(dry_run=True).persist_simulation_artifacts(
                project=project,
                simulation_run=run,
                reader_personas=run.reader_personas,
                private_reactions=run.private_reactions,
                platform_posts=run.platform_posts,
                cross_reactions=run.cross_reactions,
            )
            self.assertTrue(dry_sim.dry_run)

            scorecard = self._scorecard(pack, run)
            self.assertTrue(1.0 <= scorecard["rating_mean"] <= 5.0)
            self.assertTrue(0.0 <= scorecard["dnf_risk"] <= 1.0)
            self.assertTrue(0.0 <= scorecard["controversy_risk"] <= 1.0)
            self.assertTrue(0.0 <= scorecard["quoteability_score"] <= 1.0)
            self.assertTrue(0.0 <= scorecard["viral_mean"] <= 1.0)

            report = build_prediction_report(project, pack, run)
            report_json = report.to_dict()
            report_markdown = render_prediction_report_markdown(report)
            self.assertIn("rating_distribution", report_json["scorecard"])
            self.assertIn("# Swarmbook Report", report_markdown)

            chat = PersonaInterrogator().interrogate(
                simulation_run=run,
                evidence_pack=pack,
                persona_id=run.reader_personas[0].persona_id,
                question="Why did you rate this book this way?",
            )
            self.assertEqual(chat.persona_id, run.reader_personas[0].persona_id)
            self.assertTrue(chat.based_on)

            compare_project, compare_pack, compare_run = self._run_pipeline(
                cache=cache,
                manuscript_name="tiny_fiction_manuscript_revised.txt",
                draft_id="draft_a",
                version="v2",
            )
            comparison = DraftComparator().compare(
                project_id=project.project_id,
                base_evidence_pack=pack,
                compare_evidence_pack=compare_pack,
                base_simulation_run=run,
                compare_simulation_run=compare_run,
                simulation_seed=12345,
            )
            self.assertEqual(comparison.report.privacy_mode, "local_only")
            for key in ("rating_mean", "dnf_risk", "controversy_risk", "viral_mean", "quoteability_score"):
                self.assertIn(key, comparison.report.delta_scores)
            self.assertIsInstance(comparison.report.what_improved, list)
            self.assertIsInstance(comparison.report.what_got_worse, list)
            self.assertIsInstance(comparison.report.still_blocking, list)
            self.assertIn("## What Improved", comparison.markdown)
            self.assertEqual(compare_project.project_id, project.project_id)

            (output_dir / "report.json").write_text(json.dumps(report_json, indent=2), encoding="utf-8")
            (output_dir / "report.md").write_text(report_markdown, encoding="utf-8")
            (output_dir / "comparison.json").write_text(
                json.dumps(comparison.report.to_dict(), indent=2),
                encoding="utf-8",
            )
            (output_dir / "comparison.md").write_text(comparison.markdown, encoding="utf-8")
            self.assertTrue((output_dir / "report.json").exists())
            self.assertTrue((output_dir / "comparison.md").exists())

    def test_tiny_nonfiction_ingestion_builds_claim_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = LocalArtifactCache(base_dir=temp_dir)
            project = self._project(draft_id="draft_nf", version="v1", title="The 20-Minute Creator System")
            manuscript = self._manuscript(project, "tiny_nonfiction_manuscript.txt", "The 20-Minute Creator System")
            pack = EvidencePackBuilder(cache=cache).build_from_manuscript(project, manuscript)
            self.assertEqual(pack.privacy_mode, "local_only")
            self.assertIsNotNone(pack.claim_map)
            self.assertGreaterEqual(len(pack.chapter_map.chapters), 1)

    def _run_pipeline(
        self,
        cache: LocalArtifactCache,
        manuscript_name: str,
        draft_id: str,
        version: str,
    ):
        project = self._project(draft_id=draft_id, version=version, title="The Clock Beneath the River")
        manuscript = self._manuscript(project, manuscript_name, "The Clock Beneath the River")
        pack = EvidencePackBuilder(cache=cache).build_from_manuscript(project, manuscript)
        run = SimulationOrchestrator(
            cache=cache,
            cross_reaction_posts=2,
            max_reaction_rounds=1,
            max_parallel_jobs=1,
        ).run(
            project=project,
            evidence_pack=pack,
            simulation_seed=12345,
            persona_overrides=PersonaGenerationOverrides(
                persona_count=4,
                allowed_platforms=["goodreads", "reddit", "x"],
            ),
        )
        run.provider_route = "local_ollama"
        return project, pack, run

    def _project(self, draft_id: str, version: str, title: str) -> BookProject:
        return BookProject(
            project_id="proj_tiny_e2e",
            name="Tiny E2E",
            privacy_mode="local_only",
            draft_id=draft_id,
            version=version,
            title=title,
            metadata={"local_profile": "local_tiny"},
        )

    def _manuscript(self, project: BookProject, fixture_name: str, title: str) -> ManuscriptInput:
        return ManuscriptInput(
            input_id=f"input_{project.draft_id}_{project.version}",
            project_id=project.project_id,
            title=title,
            text=(FIXTURES / fixture_name).read_text(encoding="utf-8"),
            privacy_mode="local_only",
            draft_id=project.draft_id,
            version=project.version,
        )

    def _scorecard(self, pack, run) -> dict[str, float]:
        context = ScoringContext(evidence_pack=pack, simulation_run=run)
        rating = score_rating_distribution(context)
        dnf = score_dnf(context)
        controversy = score_controversy(context)
        quoteability = score_quoteability(context)
        viral = score_viral_potential(context)
        viral_values = list(viral.platform_scores.values())
        return {
            "rating_mean": rating.predicted_mean_rating,
            "dnf_risk": dnf.dnf_risk,
            "controversy_risk": controversy.controversy_risk,
            "quoteability_score": quoteability.quoteability_score,
            "viral_mean": sum(viral_values) / max(len(viral_values), 1),
        }

    def _router_env(self) -> dict[str, str]:
        return {
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "GEMINI_API_KEY": "",
            "NVIDIA_API_KEY": "",
            "BOOK_SIM_PROVIDER_TIMEOUT": "0.01",
        }


if __name__ == "__main__":
    unittest.main()
