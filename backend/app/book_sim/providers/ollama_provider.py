"""Local Ollama provider for Swarmbook routes."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

try:
    import requests
except ImportError:  # pragma: no cover - depends on local environment
    requests = None
try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - depends on local environment
    OpenAI = None

from .base import BaseProvider


class OllamaProvider(BaseProvider):
    """Provider for local Ollama text and embedding calls."""

    def __init__(self, route, env: Mapping[str, str]) -> None:
        super().__init__(route, env)
        base = (env.get("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
        self.base_url = base
        self.openai_base_url = base if base.endswith("/v1") else f"{base}/v1"
        self.embedding_model = env.get("EMBEDDING_MODEL", "nomic-embed-text")
        self.timeout_s = float(env.get("BOOK_SIM_PROVIDER_TIMEOUT", "30"))
        self.num_ctx = int(env.get("OLLAMA_NUM_CTX", "8192"))
        self._client_error: Optional[str] = None
        self.client = None
        if OpenAI is None:
            self._client_error = "openai package is not installed"
        else:
            self.client = OpenAI(
                api_key=env.get("LLM_API_KEY", "ollama"),
                base_url=self.openai_base_url,
                timeout=self.timeout_s,
            )

    def is_available(self) -> bool:
        return self.client is not None

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        if self.client is None:
            raise RuntimeError(f"Ollama route unavailable: {self._client_error or 'unknown error'}")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.route.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body={"options": {"num_ctx": self.num_ctx}},
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
        system_text = f"{merged_system}\n{json_guard}".strip()

        raw = self.generate_text(
            prompt=prompt,
            system_prompt=system_text,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return self._parse_json_text(raw)

    def embed_text(self, text: str) -> list[float]:
        if requests is None:
            raise RuntimeError("requests package is required for Ollama embedding calls")
        response = requests.post(
            f"{self.base_url}/api/embed",
            json={"model": self.embedding_model, "input": text},
            timeout=self.timeout_s,
        )
        response.raise_for_status()
        payload = response.json()
        embeddings = payload.get("embeddings", [])
        if not embeddings:
            raise ValueError("Ollama embedding response missing embeddings field")
        vector = embeddings[0]
        if not isinstance(vector, list):
            raise ValueError("Ollama embedding vector is not a list")
        return [float(v) for v in vector]

    def health_check(self) -> Dict[str, Any]:
        if self.client is None:
            return {
                "ok": False,
                "provider": "ollama",
                "route": self.route.route_name,
                "error": self._client_error or "openai package missing",
                "model": self.route.model,
            }
        if requests is None:
            return {
                "ok": False,
                "provider": "ollama",
                "route": self.route.route_name,
                "error": "requests package is not installed",
                "model": self.route.model,
            }
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout_s)
            ok = response.status_code == 200
            return {
                "ok": ok,
                "provider": "ollama",
                "route": self.route.route_name,
                "status_code": response.status_code,
                "model": self.route.model,
            }
        except Exception as exc:  # pragma: no cover - network failure depends on environment
            return {
                "ok": False,
                "provider": "ollama",
                "route": self.route.route_name,
                "error": str(exc),
                "model": self.route.model,
            }
