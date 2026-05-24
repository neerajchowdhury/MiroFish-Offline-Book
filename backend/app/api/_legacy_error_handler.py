"""Shared error handling for legacy MiroFish API endpoints.

Provides a decorator that catches exceptions, logs full tracebacks server-side,
and returns only safe error messages to clients. This prevents internal
implementation details from leaking to API consumers.
"""

from functools import wraps
from flask import jsonify

from ..utils.logger import get_logger

logger = get_logger('mirofish.api.error_handler')


def legacy_api_route(handler):
    """Wrap a legacy route with structured JSON error handling.

    Logs full tracebacks server-side via logger.exception() but returns
    only a generic 'Internal server error' message to clients.
    ValueError exceptions are returned as 400 with the original message.
    """
    @wraps(handler)
    def wrapped(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except ValueError as exc:
            return jsonify({
                "success": False,
                "error": str(exc),
            }), 400
        except Exception as exc:
            logger.exception("Legacy API endpoint failed: %s", handler.__name__)
            return jsonify({
                "success": False,
                "error": "Internal server error",
            }), 500
    return wrapped
