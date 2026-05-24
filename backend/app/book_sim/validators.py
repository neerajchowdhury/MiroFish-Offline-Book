"""Input validation for Swarmbook API endpoints.

Provides reusable validation functions that raise ValueError on invalid
input. Used by the _api_route decorator in book_sim.py to validate
request parameters before processing.
"""

from __future__ import annotations

from typing import Optional

ALLOWED_PRIVACY_MODES = {"local_only", "hybrid_safe", "cloud_quality"}


def validate_privacy_mode(value: Optional[str], default: str = "hybrid_safe") -> str:
    """Validate and normalize a privacy mode string."""
    mode = (value or default).strip() or default
    if mode not in ALLOWED_PRIVACY_MODES:
        raise ValueError(
            f"Unsupported privacy_mode: {mode}. "
            f"Allowed: {sorted(ALLOWED_PRIVACY_MODES)}"
        )
    return mode


def validate_positive_int(value, field_name: str, minimum: int = 1) -> int:
    """Validate that a value is a positive integer >= minimum."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer")
    if n < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}")
    return n


def validate_non_empty_string(value, field_name: str) -> str:
    """Validate that a value is a non-empty string."""
    if value is None:
        raise ValueError(f"{field_name} is required")
    s = str(value).strip()
    if not s:
        raise ValueError(f"{field_name} must not be empty")
    return s


def validate_max_length(value: str, field_name: str, max_length: int) -> str:
    """Validate that a string does not exceed the maximum length."""
    if len(value) > max_length:
        raise ValueError(
            f"{field_name} exceeds maximum length of {max_length} "
            f"(got {len(value)})"
        )
    return value
