"""Base provider contract for Swarmbook model routing.

Defines the abstract interface that all LLM/embedding providers must
implement. Includes retry-with-backoff for transient network errors
and structured JSON parsing from model responses.
"""

from __future__ import annotations

import json
import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional

from ..config_loader import ModelRouteEntry

logger = logging.getLogger('mirofish.book_sim.provider')


class ProviderError(Exception):
    """Base exception for provider failures."""


class ProviderRetryError(ProviderError):
    """Raised when all retry attempts are exhausted."""


class BaseProvider(ABC):
    """Typed interface for provider implementations.

    All providers (Ollama, Gemini, NVIDIA) must implement this interface.
    The _retry_with_backoff method handles transient network failures
    with exponential backoff.
    """

    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 1.0  # seconds

    def __init__(self, route: ModelRouteEntry, env: Mapping[str, str]) -> None:
        self.route = route
        self.env = env

    @staticmethod
    def _parse_json_text(raw_text: str) -> Dict[str, Any]:
        """Extract and parse JSON from raw model text.

        Strips markdown code fences and leading/trailing whitespace
        before parsing. Raises ValueError if the result is empty or
        invalid JSON.
        """
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()
        if not cleaned:
            raise ValueError("Provider returned empty JSON payload")
        return json.loads(cleaned)

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute a function with exponential backoff retry.

        Retries on transient network errors (ConnectionError, TimeoutError,
        OSError) up to MAX_RETRIES times with exponentially increasing delays.
        Non-transient exceptions are raised immediately.
        """
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (ConnectionError, TimeoutError, OSError) as e:
                last_error = e
                wait = self.RETRY_DELAY_BASE * (2 ** attempt)
                logger.warning(
                    "Provider %s transient error (attempt %d/%d), retrying in %.1fs: %s",
                    self.route.provider, attempt + 1, self.MAX_RETRIES, wait, e,
                )
                time.sleep(wait)
            except Exception:
                raise
        raise ProviderRetryError(
            f"Provider {self.route.provider} failed after {self.MAX_RETRIES} attempts"
        ) from last_error

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
