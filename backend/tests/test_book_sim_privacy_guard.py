"""Tests for book_sim.privacy_guard.PrivacyGuard singleton and enforcement."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from book_sim.privacy_guard import PrivacyGuard, PrivacyViolationError
from book_sim.provider_router import BookSimProviderRouter


class TestPrivacyGuardSingleton(unittest.TestCase):
    def setUp(self) -> None:
        PrivacyGuard.reset()

    def tearDown(self) -> None:
        PrivacyGuard.reset()

    def test_get_instance_returns_singleton(self) -> None:
        instance1 = PrivacyGuard.get_instance()
        instance2 = PrivacyGuard.get_instance()
        self.assertIs(instance1, instance2)

    def test_set_mode_valid_modes(self) -> None:
        guard = PrivacyGuard.get_instance()
        for mode in ("local_only", "hybrid_safe", "cloud_quality"):
            guard.set_mode(mode)
            self.assertEqual(guard.mode, mode)

    def test_set_mode_invalid_raises(self) -> None:
        guard = PrivacyGuard.get_instance()
        with self.assertRaises(ValueError):
            guard.set_mode("invalid_mode")

    def test_is_local_only(self) -> None:
        guard = PrivacyGuard.get_instance()
        guard.set_mode("local_only")
        self.assertTrue(guard.is_local_only())
        guard.set_mode("hybrid_safe")
        self.assertFalse(guard.is_local_only())

    def test_assert_local_provider_passes_for_ollama_in_local_only(self) -> None:
        guard = PrivacyGuard.get_instance()
        guard.set_mode("local_only")
        guard.assert_local_provider("ollama")

    def test_assert_local_provider_raises_for_gemini_in_local_only(self) -> None:
        guard = PrivacyGuard.get_instance()
        guard.set_mode("local_only")
        with self.assertRaises(PrivacyViolationError) as ctx:
            guard.assert_local_provider("gemini")
        self.assertIn("gemini", str(ctx.exception).lower())

    def test_assert_local_provider_raises_for_nvidia_in_local_only(self) -> None:
        guard = PrivacyGuard.get_instance()
        guard.set_mode("local_only")
        with self.assertRaises(PrivacyViolationError) as ctx:
            guard.assert_local_provider("nvidia")
        self.assertIn("nvidia", str(ctx.exception).lower())

    def test_can_use_provider_all_modes(self) -> None:
        guard = PrivacyGuard.get_instance()
        guard.set_mode("local_only")
        self.assertTrue(guard.can_use_provider("ollama"))
        self.assertFalse(guard.can_use_provider("gemini"))
        self.assertFalse(guard.can_use_provider("nvidia"))

        guard.set_mode("hybrid_safe")
        self.assertTrue(guard.can_use_provider("ollama"))
        self.assertTrue(guard.can_use_provider("gemini"))
        self.assertTrue(guard.can_use_provider("nvidia"))

        guard.set_mode("cloud_quality")
        self.assertTrue(guard.can_use_provider("ollama"))
        self.assertTrue(guard.can_use_provider("gemini"))
        self.assertTrue(guard.can_use_provider("nvidia"))

    def test_reset_clears_singleton(self) -> None:
        instance1 = PrivacyGuard.get_instance()
        PrivacyGuard.reset()
        instance2 = PrivacyGuard.get_instance()
        self.assertIsNot(instance1, instance2)

    def test_integration_with_provider_router(self) -> None:
        """PrivacyGuard is checked during select_route."""
        from book_sim.config_loader import BookSimRoutingConfig, ModelRouteEntry

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            route_entry = ModelRouteEntry(
                route_name="local_ollama",
                provider="ollama",
                model="phi3",
            )
            routing_config = BookSimRoutingConfig(
                model_routes={"local_ollama": route_entry},
                privacy_modes={},
                model_routes_path=tmp / "routes.yaml",
                privacy_modes_path=tmp / "privacy.yaml",
            )

            guard = PrivacyGuard.get_instance()
            guard.set_mode("local_only")

            router = BookSimProviderRouter(routing_config=routing_config)
            selection = router.select_route("local_ollama", privacy_mode="local_only")
            self.assertEqual(selection.selected_route, "local_ollama")
            self.assertEqual(selection.provider_name, "ollama")

    def test_providers_raise_privacy_violation_when_local_only(self) -> None:
        """Gemini and Nvidia providers must raise PrivacyViolationError in local_only mode."""
        from book_sim.config_loader import ModelRouteEntry
        from book_sim.providers.gemini_provider import GeminiProvider
        from book_sim.providers.nvidia_provider import NvidiaProvider

        gemini_route = ModelRouteEntry(
            route_name="gemini_fast",
            provider="gemini",
            model="gemini-1.5-flash",
        )
        nvidia_route = ModelRouteEntry(
            route_name="nvidia_llama3",
            provider="nvidia",
            model="meta/llama3",
        )

        env = {"GEMINI_API_KEY": "test_gemini_key", "NVIDIA_API_KEY": "test_nvidia_key"}
        gemini_provider = GeminiProvider(gemini_route, env)
        nvidia_provider = NvidiaProvider(nvidia_route, env)

        guard = PrivacyGuard.get_instance()
        guard.set_mode("local_only")

        with self.assertRaises(PrivacyViolationError) as ctx:
            gemini_provider.generate_text("hello")
        self.assertIn("gemini", str(ctx.exception).lower())

        with self.assertRaises(PrivacyViolationError) as ctx:
            gemini_provider.generate_json("hello")
        self.assertIn("gemini", str(ctx.exception).lower())

        with self.assertRaises(PrivacyViolationError) as ctx:
            gemini_provider.embed_text("hello")
        self.assertIn("gemini", str(ctx.exception).lower())

        with self.assertRaises(PrivacyViolationError) as ctx:
            nvidia_provider.generate_text("hello")
        self.assertIn("nvidia", str(ctx.exception).lower())

        with self.assertRaises(PrivacyViolationError) as ctx:
            nvidia_provider.generate_json("hello")
        self.assertIn("nvidia", str(ctx.exception).lower())

        with self.assertRaises(PrivacyViolationError) as ctx:
            nvidia_provider.embed_text("hello")
        self.assertIn("nvidia", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
