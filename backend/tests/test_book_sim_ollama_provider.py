"""Tests for book_sim.providers.ollama_provider.OllamaProvider."""

from unittest.mock import MagicMock, patch

import pytest

from book_sim.config_loader import ModelRouteEntry
from book_sim.providers.ollama_provider import OllamaProvider


def _make_route():
    return ModelRouteEntry(
        route_name="local_ollama",
        provider="ollama",
        model="llama3",
        purpose=["text", "json", "embedding"],
        max_input_tokens=8192,
        output_mode="structured_json",
        privacy_mode_allowlist=["local_only"],
    )


def _make_env(**overrides):
    env = {
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "BOOK_SIM_PROVIDER_TIMEOUT": "30",
        "OLLAMA_NUM_CTX": "8192",
        "LLM_API_KEY": "ollama",
    }
    env.update(overrides)
    return env


class TestOllamaProviderAvailability:
    @patch("book_sim.providers.ollama_provider.OpenAI")
    def test_is_available_when_ollama_running(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        assert provider.is_available() is True
        assert provider.client is not None

    @patch("book_sim.providers.ollama_provider.OpenAI", None)
    def test_is_available_false_when_not_running(self):
        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        assert provider.is_available() is False
        assert provider.client is None


class TestOllamaProviderGenerateText:
    @patch("book_sim.providers.ollama_provider.OpenAI")
    def test_generate_text_returns_string(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello, this is a test response."
        mock_client.chat.completions.create.return_value = mock_response

        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        result = provider.generate_text(
            prompt="Say hello",
            system_prompt="You are helpful",
            temperature=0.2,
            max_tokens=100,
        )

        assert isinstance(result, str)
        assert result == "Hello, this is a test response."
        mock_client.chat.completions.create.assert_called_once()


class TestOllamaProviderGenerateJson:
    @patch("book_sim.providers.ollama_provider.OpenAI")
    def test_generate_json_returns_dict(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value", "count": 42}'
        mock_client.chat.completions.create.return_value = mock_response

        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        result = provider.generate_json(
            prompt="Give me data",
            system_prompt="Return JSON",
            temperature=0.1,
            max_tokens=200,
        )

        assert isinstance(result, dict)
        assert result == {"key": "value", "count": 42}


class TestOllamaProviderEmbedText:
    @patch("book_sim.providers.ollama_provider.requests")
    @patch("book_sim.providers.ollama_provider.OpenAI")
    def test_embed_text_returns_list(self, mock_openai_cls, mock_requests):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "embeddings": [[0.1, 0.2, 0.3, 0.4, 0.5]]
        }
        mock_requests.post.return_value = mock_response

        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        result = provider.embed_text("test embedding input")

        assert isinstance(result, list)
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
        assert all(isinstance(v, float) for v in result)
        mock_requests.post.assert_called_once()


class TestOllamaProviderHealthCheck:
    @patch("book_sim.providers.ollama_provider.requests")
    @patch("book_sim.providers.ollama_provider.OpenAI")
    def test_health_check_ok_when_available(self, mock_openai_cls, mock_requests):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        result = provider.health_check()

        assert result["ok"] is True
        assert result["provider"] == "ollama"
        assert result["route"] == "local_ollama"
        assert result["model"] == "llama3"
        assert result["status_code"] == 200

    @patch("book_sim.providers.ollama_provider.requests")
    @patch("book_sim.providers.ollama_provider.OpenAI")
    def test_health_check_not_ok_when_unavailable(self, mock_openai_cls, mock_requests):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_requests.get.return_value = mock_response

        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        result = provider.health_check()

        assert result["ok"] is False
        assert result["provider"] == "ollama"
        assert result["route"] == "local_ollama"
        assert result["model"] == "llama3"

    @patch("book_sim.providers.ollama_provider.requests")
    @patch("book_sim.providers.ollama_provider.OpenAI")
    def test_health_check_not_ok_on_exception(self, mock_openai_cls, mock_requests):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_requests.get.side_effect = ConnectionError("Connection refused")

        route = _make_route()
        env = _make_env()
        provider = OllamaProvider(route, env)

        result = provider.health_check()

        assert result["ok"] is False
        assert "error" in result
        assert result["provider"] == "ollama"
        assert result["model"] == "llama3"
