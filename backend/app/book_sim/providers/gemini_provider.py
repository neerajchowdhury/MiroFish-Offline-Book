"""Gemini provider for Swarmbook routes."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

try:
    import requests
except ImportError:  # pragma: no cover - depends on local environment
    requests = None

from .base import BaseProvider


class GeminiProvider(BaseProvider):
    """Provider for Gemini REST API with graceful key handling."""

    def __init__(self, route, env: Mapping[str, str]) -> None:
        super().__init__(route, env)
        self.api_key = (env.get("GEMINI_API_KEY") or "").strip()
        self.base_url = (env.get("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com").rstrip("/")
        self.timeout_s = float(env.get("BOOK_SIM_PROVIDER_TIMEOUT", "30"))

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _require_key(self) -> None:
        if not self.api_key:
            raise RuntimeError("Gemini route is not available: GEMINI_API_KEY is missing")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        self._require_key()
        if requests is None:
            raise RuntimeError("requests package is required for Gemini API calls")
        prompt_text = prompt if not system_prompt else f"System:\n{system_prompt}\n\nUser:\n{prompt}"

        url = f"{self.base_url}/v1beta/models/{self.route.model}:generateContent"
        params = {"key": self.api_key}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt_text}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        response = requests.post(url, params=params, json=payload, timeout=self.timeout_s)
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return ""
        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
        return "\n".join([p for p in text_parts if p]).strip()

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
        if requests is None:
            raise RuntimeError("requests package is required for Gemini embedding calls")
        url = f"{self.base_url}/v1beta/models/text-embedding-004:embedContent"
        params = {"key": self.api_key}
        payload = {
            "content": {
                "parts": [{"text": text}],
            }
        }
        response = requests.post(url, params=params, json=payload, timeout=self.timeout_s)
        response.raise_for_status()
        data = response.json()
        values = data.get("embedding", {}).get("values", [])
        if not isinstance(values, list):
            raise ValueError("Gemini embedding response has invalid shape")
        return [float(v) for v in values]

    def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "ok": False,
                "provider": "gemini",
                "route": self.route.route_name,
                "error": "GEMINI_API_KEY is not set",
                "model": self.route.model,
            }
        if requests is None:
            return {
                "ok": False,
                "provider": "gemini",
                "route": self.route.route_name,
                "error": "requests package is not installed",
                "model": self.route.model,
            }
        try:
            response = requests.get(
                f"{self.base_url}/v1beta/models/{self.route.model}",
                params={"key": self.api_key},
                timeout=self.timeout_s,
            )
            return {
                "ok": response.status_code == 200,
                "provider": "gemini",
                "route": self.route.route_name,
                "status_code": response.status_code,
                "model": self.route.model,
            }
        except Exception as exc:  # pragma: no cover - network failure depends on environment
            return {
                "ok": False,
                "provider": "gemini",
                "route": self.route.route_name,
                "error": str(exc),
                "model": self.route.model,
            }
