"""Tests for book_sim.config_loader module."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from book_sim.config_loader import (
    _clean_scalar,
    _load_yaml_dict,
)


class TestModelRoutes:
    def test_model_routes_load_from_yaml(self):
        from book_sim.config_loader import BookSimRoutingConfig, DEFAULT_MODEL_ROUTES_PATH, DEFAULT_PRIVACY_MODES_PATH

        config = BookSimRoutingConfig.from_yaml(
            model_routes_path=DEFAULT_MODEL_ROUTES_PATH,
            privacy_modes_path=DEFAULT_PRIVACY_MODES_PATH,
        )
        assert isinstance(config.model_routes, dict)
        assert "local_ollama" in config.model_routes


class TestPrivacyModes:
    def test_privacy_modes_load_from_yaml(self):
        from book_sim.config_loader import BookSimRoutingConfig, DEFAULT_MODEL_ROUTES_PATH, DEFAULT_PRIVACY_MODES_PATH

        config = BookSimRoutingConfig.from_yaml(
            model_routes_path=DEFAULT_MODEL_ROUTES_PATH,
            privacy_modes_path=DEFAULT_PRIVACY_MODES_PATH,
        )
        assert isinstance(config.privacy_modes, dict)
        assert len(config.privacy_modes) > 0


class TestCleanScalar:
    def test_clean_scalar_strings(self):
        assert _clean_scalar("hello") == "hello"
        assert _clean_scalar("  world  ") == "world"

    def test_clean_scalar_numbers(self):
        assert _clean_scalar("42") == 42
        assert _clean_scalar("  7  ") == 7

    def test_clean_scalar_booleans(self):
        assert _clean_scalar("true") is True
        assert _clean_scalar("True") is True
        assert _clean_scalar("false") is False
        assert _clean_scalar("FALSE") is False

    def test_clean_scalar_none_string(self):
        result = _clean_scalar("none")
        assert result == "none"


class TestLoadYamlDict:
    def test_load_yaml_dict_missing_file_returns_empty(self):
        missing_path = Path("/nonexistent/path/config.yaml")
        with pytest.raises(FileNotFoundError, match="Missing config file"):
            _load_yaml_dict(missing_path)

    def test_load_yaml_dict_invalid_yaml_returns_empty(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(":::invalid:::\n{{{{not yaml}}}}\n")
            f.flush()
            tmp_path = Path(f.name)
        try:
            with pytest.raises(Exception):
                _load_yaml_dict(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
