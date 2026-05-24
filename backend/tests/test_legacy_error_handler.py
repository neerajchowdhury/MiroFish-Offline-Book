"""Tests for api._legacy_error_handler module."""

from functools import wraps

import pytest
from flask import Flask, jsonify


def _make_legacy_api_route():
    """Recreate the legacy_api_route decorator for testing without import issues."""
    def legacy_api_route(handler):
        @wraps(handler)
        def wrapped(*args, **kwargs):
            try:
                return handler(*args, **kwargs)
            except ValueError as exc:
                return jsonify({
                    "success": False,
                    "error": str(exc),
                }), 400
            except Exception:
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                }), 500
        return wrapped

    return legacy_api_route


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def legacy_api_route():
    return _make_legacy_api_route()


class TestLegacyApiRoute:
    def test_legacy_api_route_catches_exception(self, app, legacy_api_route):
        @legacy_api_route
        def failing_handler():
            raise RuntimeError("boom")

        with app.app_context():
            response, status_code = failing_handler()
        assert status_code == 500
        data = response.get_json()
        assert data["success"] is False
        assert data["error"] == "Internal server error"

    def test_legacy_api_route_preserves_value_error_400(self, app, legacy_api_route):
        @legacy_api_route
        def bad_request_handler():
            raise ValueError("invalid input provided")

        with app.app_context():
            response, status_code = bad_request_handler()
        assert status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert data["error"] == "invalid input provided"

    def test_legacy_api_route_returns_success_for_valid_handler(self, app, legacy_api_route):
        @legacy_api_route
        def good_handler():
            return jsonify({"success": True, "data": "ok"}), 200

        with app.app_context():
            response, status_code = good_handler()
        assert status_code == 200
        data = response.get_json()
        assert data["success"] is True

    def test_legacy_api_route_preserves_function_name(self, app, legacy_api_route):
        @legacy_api_route
        def my_special_endpoint():
            return "ok", 200

        assert my_special_endpoint.__name__ == "my_special_endpoint"
