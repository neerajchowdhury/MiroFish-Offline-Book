"""Provider router for Swarmbook model selection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from .config_loader import BookSimRoutingConfig, ModelRouteEntry
from .providers import BaseProvider, GeminiProvider, NvidiaProvider, OllamaProvider


@dataclass(frozen=True)
class RouteSelection:
    """Result of route selection with lightweight explainability."""

    requested_route: str
    selected_route: str
    provider_name: str
    privacy_mode: str
    reason: str


class BookSimProviderRouter:
    """Route requests to configured model providers without changing existing app LLM flows."""

    def __init__(
        self,
        routing_config: Optional[BookSimRoutingConfig] = None,
        env: Optional[Mapping[str, str]] = None,
    ) -> None:
        self.routing_config = routing_config or BookSimRoutingConfig.from_yaml()
        self.env: Mapping[str, str] = env or os.environ
        self._providers: Dict[str, BaseProvider] = {}

        for route_name, route in self.routing_config.model_routes.items():
            self._providers[route_name] = self._build_provider(route)

    def _build_provider(self, route: ModelRouteEntry) -> BaseProvider:
        """Create provider implementation for one route entry."""
        provider_name = route.provider.lower()
        if provider_name == "ollama":
            return OllamaProvider(route, self.env)
        if provider_name == "gemini":
            return GeminiProvider(route, self.env)
        if provider_name == "nvidia":
            return NvidiaProvider(route, self.env)
        raise ValueError(f"Unsupported provider in route '{route.route_name}': {route.provider}")

    def get_provider_for_route(self, route_name: str) -> BaseProvider:
        """Get provider by explicit route name without privacy fallback logic."""
        if route_name not in self._providers:
            raise KeyError(f"Unknown route: {route_name}")
        return self._providers[route_name]

    def select_route(self, route_name: str, privacy_mode: str = "hybrid_safe") -> RouteSelection:
        """Select a safe route based on privacy mode and provider availability."""
        default_route = "local_ollama"
        requested_route = route_name or default_route

        if requested_route not in self.routing_config.model_routes:
            requested_route = default_route
            reason = "requested route not found; using local_ollama"
        else:
            reason = "requested route accepted"

        chosen_route = requested_route
        chosen_entry = self.routing_config.model_routes[chosen_route]
        chosen_provider = self._providers[chosen_route]

        if privacy_mode == "local_only" and chosen_entry.provider.lower() != "ollama":
            chosen_route = default_route
            chosen_entry = self.routing_config.model_routes[chosen_route]
            chosen_provider = self._providers[chosen_route]
            reason = "privacy_mode local_only requires local provider"

        allowlist = chosen_entry.privacy_mode_allowlist
        if allowlist and privacy_mode not in allowlist:
            chosen_route = default_route
            chosen_entry = self.routing_config.model_routes[chosen_route]
            chosen_provider = self._providers[chosen_route]
            reason = "privacy mode not allowlisted for requested route"

        if not chosen_provider.is_available():
            if chosen_route != default_route:
                chosen_route = default_route
                chosen_entry = self.routing_config.model_routes[chosen_route]
                chosen_provider = self._providers[chosen_route]
                reason = "requested provider unavailable; using local_ollama"

        return RouteSelection(
            requested_route=route_name,
            selected_route=chosen_route,
            provider_name=chosen_entry.provider,
            privacy_mode=privacy_mode,
            reason=reason,
        )

    def generate_text(
        self,
        prompt: str,
        route_name: str = "local_ollama",
        privacy_mode: str = "hybrid_safe",
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Generate text using selected provider route."""
        selection = self.select_route(route_name=route_name, privacy_mode=privacy_mode)
        provider = self._providers[selection.selected_route]
        return provider.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_json(
        self,
        prompt: str,
        route_name: str = "local_ollama",
        privacy_mode: str = "hybrid_safe",
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate JSON output using selected provider route."""
        selection = self.select_route(route_name=route_name, privacy_mode=privacy_mode)
        provider = self._providers[selection.selected_route]
        return provider.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def embed_text(
        self,
        text: str,
        route_name: str = "local_ollama",
        privacy_mode: str = "hybrid_safe",
    ) -> list[float]:
        """Generate embedding vector using selected provider route."""
        selection = self.select_route(route_name=route_name, privacy_mode=privacy_mode)
        provider = self._providers[selection.selected_route]
        return provider.embed_text(text)

    def health_check(self, route_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get health details for one route or all configured routes."""
        if route_name:
            provider = self.get_provider_for_route(route_name)
            return {route_name: provider.health_check()}

        return {
            name: provider.health_check()
            for name, provider in self._providers.items()
        }
