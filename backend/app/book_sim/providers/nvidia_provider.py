"""NVIDIA/NIM-compatible provider for Swarmbook routes."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - depends on local environment
    OpenAI = None

from .base import BaseProvider


class NvidiaProvider(BaseProvider):
    """Provider using OpenAI-compatible NVIDIA API/NIM endpoints."""

    def __init__(self, route, env: Mapping[str, str]) -> None:
        super().__init__(route, env)
        self.api_key = (env.get("NVIDIA_API_KEY") or "").strip()
        self.base_url = (env.get("NVIDIA_BASE_URL") or "https://integrate.api.nvidia.com/v1").rstrip("/")
        self.timeout_s = float(env.get("BOOK_SIM_PROVIDER_TIMEOUT", "30"))
        self.embedding_model = env.get("NVIDIA_EMBEDDING_MODEL", self.route.model)
        self._client_error: Optional[str] = None
        self.client = None
        if OpenAI is None:
            self._client_error = "openai package is not installed"
        else:
            self.client = OpenAI(
                api_key=self.api_key or "missing",
                base_url=self.base_url,
                timeout=self.timeout_s,
            )

    def is_available(self) -> bool:
        return bool(self.api_key) and self.client is not None

    def _require_key(self) -> None:
        if not self.api_key:
            raise RuntimeError("NVIDIA route is not available: NVIDIA_API_KEY is missing")
        if self.client is None:
            raise RuntimeError(f"NVIDIA route unavailable: {self._client_error or 'unknown error'}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        self._require_key()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.route.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        merged_system = (system_prompt or "").strip()
        json_guard = "Return only a valid JSON object with no markdown code fences."
        raw = self.generate_text(
            prompt=prompt,
            system_prompt=f"{merged_system}\n{json_guard}".strip(),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return self._parse_json_text(raw)

    def embed_text(self, text: str) -> list[float]:
        self._require_key()
        response = self.client.embeddings.create(model=self.embedding_model, input=[text])
        vector = response.data[0].embedding
        return [float(v) for v in vector]

    def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "ok": False,
                "provider": "nvidia",
                "route": self.route.route_name,
                "error": "NVIDIA_API_KEY is not set",
                "model": self.route.model,
            }
        if self.client is None:
            return {
                "ok": False,
                "provider": "nvidia",
                "route": self.route.route_name,
                "error": self._client_error or "openai package missing",
                "model": self.route.model,
            }
        try:
            # Lightweight compatibility check for OpenAI-style model listing.
            self.client.models.list()
            return {
                "ok": True,
                "provider": "nvidia",
                "route": self.route.route_name,
                "model": self.route.model,
            }
        except Exception as exc:  # pragma: no cover - network failure depends on environment
            return {
                "ok": False,
                "provider": "nvidia",
                "route": self.route.route_name,
                "error": str(exc),
                "model": self.route.model,
            }
