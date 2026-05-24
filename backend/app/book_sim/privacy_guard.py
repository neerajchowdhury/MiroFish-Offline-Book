"""System-wide privacy enforcement for Swarmbook.

Ensures that local_only mode never calls external providers,
regardless of which code path is used. This closes the gap where
privacy enforcement was previously only router-scoped.
"""

from __future__ import annotations

from typing import Optional


class PrivacyViolationError(Exception):
    """Raised when a cloud provider is requested in local_only mode."""


class PrivacyGuard:
    """Global privacy mode enforcer.

    All provider calls should pass through this guard to ensure
    local_only mode is never bypassed by code that does not use
    the BookSimProviderRouter.

    Usage:
        guard = PrivacyGuard.get_instance()
        guard.set_mode("local_only")
        guard.assert_local_provider("gemini")  # raises PrivacyViolationError
    """

    _instance: Optional["PrivacyGuard"] = None
    _privacy_mode: str = "hybrid_safe"

    LOCAL_PROVIDERS = {"ollama"}
    CLOUD_PROVIDERS = {"gemini", "nvidia"}

    @classmethod
    def get_instance(cls) -> "PrivacyGuard":
        """Get or create the singleton PrivacyGuard instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None

    def set_mode(self, mode: str) -> None:
        """Set the global privacy mode."""
        if mode not in ("local_only", "hybrid_safe", "cloud_quality"):
            raise ValueError(f"Invalid privacy mode: {mode}")
        self._privacy_mode = mode

    @property
    def mode(self) -> str:
        return self._privacy_mode

    def is_local_only(self) -> bool:
        """Check if the current mode restricts to local providers only."""
        return self._privacy_mode == "local_only"

    def assert_local_provider(self, provider_name: str) -> None:
        """Raise PrivacyViolationError if a cloud provider is used in local_only mode."""
        if self._privacy_mode == "local_only" and provider_name.lower() not in self.LOCAL_PROVIDERS:
            raise PrivacyViolationError(
                f"Provider '{provider_name}' is not allowed in local_only mode. "
                f"Only {sorted(self.LOCAL_PROVIDERS)} providers are permitted."
            )

    def can_use_provider(self, provider_name: str) -> bool:
        """Check if a provider is allowed under current privacy mode."""
        if self._privacy_mode == "local_only":
            return provider_name.lower() in self.LOCAL_PROVIDERS
        return True
