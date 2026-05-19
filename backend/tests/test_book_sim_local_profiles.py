"""Tests for Swarmbook local profile configuration and loader behavior."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.local_profiles import DEFAULT_LOCAL_PROFILES_PATH, LocalProfileLoader


class TestLocalProfilesLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = LocalProfileLoader()
        self.catalog = self.loader.load()

    def test_local_profiles_yaml_exists(self) -> None:
        self.assertTrue(DEFAULT_LOCAL_PROFILES_PATH.exists())

    def test_default_profile_is_hybrid_safe_default(self) -> None:
        self.assertEqual(self.catalog.default_profile, "hybrid_safe_default")
        self.assertEqual(self.loader.get_default_profile().profile_name, "hybrid_safe_default")

    def test_required_profiles_exist(self) -> None:
        self.assertIsNotNone(self.loader.get_profile("local_tiny"))
        self.assertIsNotNone(self.loader.get_profile("hybrid_safe_default"))
        self.assertIsNotNone(self.loader.get_profile("cloud_quality"))

    def test_local_parallel_jobs_defaults_to_one(self) -> None:
        for profile in self.catalog.profiles.values():
            self.assertEqual(profile.local_parallel_jobs, 1)

    def test_local_tiny_disables_external_models(self) -> None:
        local_tiny = self.loader.get_profile("local_tiny")
        self.assertIsNotNone(local_tiny)
        self.assertFalse(local_tiny.allow_external_models)

    def test_hybrid_safe_default_disables_full_manuscript_cloud(self) -> None:
        hybrid_safe = self.loader.get_profile("hybrid_safe_default")
        self.assertIsNotNone(hybrid_safe)
        self.assertFalse(hybrid_safe.allow_full_manuscript_to_cloud)

    def test_cloud_quality_warning_mentions_heavy_and_privacy(self) -> None:
        warnings = self.loader.get_profile_warnings("cloud_quality")
        messages = " ".join(item["message"].lower() for item in warnings)
        self.assertIn("slower", messages)
        self.assertIn("manuscript", messages)
        self.assertIn("cloud", messages)

    def test_unknown_profile_is_handled_gracefully(self) -> None:
        self.assertIsNone(self.loader.get_profile("does_not_exist"))
        warnings = self.loader.get_profile_warnings("does_not_exist")
        self.assertEqual(warnings[0]["code"], "unknown_profile")


if __name__ == "__main__":
    unittest.main()
