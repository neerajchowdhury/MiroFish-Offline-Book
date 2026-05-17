"""Base provider contract for Swarmbook model routing."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional

from ..config_loader import ModelRouteEntry


class BaseProvider(ABC):
    """Typed interface for provider implementations."""

    def __init__(self, route: ModelRouteEntry, env: Mapping[str, str]) -> None:
        self.route = route
        self.env = env

    @staticmethod
    def _parse_json_text(raw_text: str) -> Dict[str, Any]:
        """Extract and parse JSON from raw model text."""
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()
        if not cleaned:
            raise ValueError("Provider returned empty JSON payload")
        return json.loads(cleaned)

    @abstractmethod
    def is_available(self) -> bool:
        """Return True when provider is configured enough to receive calls."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Generate natural language text."""

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Generate structured JSON response."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector."""

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return provider health status without raising on missing keys."""
