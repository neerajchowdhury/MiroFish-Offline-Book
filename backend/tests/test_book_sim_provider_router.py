"""Tests for Swarmbook provider-router foundation."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


BACKEND_APP_ROOT = Path(__file__).resolve().parents[1] / "app"
if str(BACKEND_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_APP_ROOT))

from book_sim.config_loader import BookSimRoutingConfig, ModelRouteEntry
from book_sim.provider_router import BookSimProviderRouter

try:
    import yaml as _yaml  # noqa: F401
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class TestBookSimConfigLoading(unittest.TestCase):
    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed in current Python environment")
    def test_model_routes_and_privacy_modes_load(self) -> None:
        config = BookSimRoutingConfig.from_yaml()
        self.assertIn("local_ollama", config.model_routes)
        self.assertIn("gemini_fast", config.model_routes)
        self.assertIn("gemini_deep", config.model_routes)
        self.assertIn("nvidia_fallback", config.model_routes)
        self.assertIn("local_only", config.privacy_modes)
        self.assertIn("hybrid_safe", config.privacy_modes)
        self.assertIn("cloud_quality", config.privacy_modes)


class TestBookSimProviderSelection(unittest.TestCase):
    def setUp(self) -> None:
        env = dict(os.environ)
        env.pop("GEMINI_API_KEY", None)
        env.pop("NVIDIA_API_KEY", None)
        env.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
        if YAML_AVAILABLE:
            self.router = BookSimProviderRouter(env=env)
            return

        manual_config = BookSimRoutingConfig(
            model_routes={
                "local_ollama": ModelRouteEntry(
                    route_name="local_ollama",
                    provider="ollama",
                    model="qwen2.5:32b",
                    privacy_mode_allowlist=["local_only", "hybrid_safe", "cloud_quality"],
                ),
                "gemini_fast": ModelRouteEntry(
                    route_name="gemini_fast",
                    provider="gemini",
                    model="gemini-2.5-flash",
                    privacy_mode_allowlist=["hybrid_safe", "cloud_quality"],
                ),
                "gemini_deep": ModelRouteEntry(
                    route_name="gemini_deep",
                    provider="gemini",
                    model="gemini-2.5-pro",
                    privacy_mode_allowlist=["cloud_quality"],
                ),
                "nvidia_fallback": ModelRouteEntry(
                    route_name="nvidia_fallback",
                    provider="nvidia",
                    model="nim-default",
                    privacy_mode_allowlist=["hybrid_safe", "cloud_quality"],
                ),
            },
            privacy_modes={
                "local_only": {},
                "hybrid_safe": {},
                "cloud_quality": {},
            },
            model_routes_path=Path("manual"),
            privacy_modes_path=Path("manual"),
        )
        self.router = BookSimProviderRouter(routing_config=manual_config, env=env)

    def test_local_route_selected_for_local_request(self) -> None:
        selection = self.router.select_route("local_ollama", privacy_mode="hybrid_safe")
        self.assertEqual(selection.selected_route, "local_ollama")
        self.assertEqual(selection.provider_name, "ollama")

    def test_missing_gemini_key_falls_back_to_local(self) -> None:
        selection = self.router.select_route("gemini_fast", privacy_mode="hybrid_safe")
        self.assertEqual(selection.selected_route, "local_ollama")
        self.assertIn("unavailable", selection.reason)

    def test_missing_nvidia_key_falls_back_to_local(self) -> None:
        selection = self.router.select_route("nvidia_fallback", privacy_mode="hybrid_safe")
        self.assertEqual(selection.selected_route, "local_ollama")
        self.assertIn("unavailable", selection.reason)

    def test_local_only_never_uses_external_provider(self) -> None:
        selection = self.router.select_route("gemini_deep", privacy_mode="local_only")
        self.assertEqual(selection.selected_route, "local_ollama")
        self.assertIn("local_only", selection.reason)

    def test_missing_api_key_health_is_graceful(self) -> None:
        provider = self.router.get_provider_for_route("gemini_fast")
        health = provider.health_check()
        self.assertFalse(health["ok"])
        self.assertIn("GEMINI_API_KEY", health["error"])


if __name__ == "__main__":
    unittest.main()
