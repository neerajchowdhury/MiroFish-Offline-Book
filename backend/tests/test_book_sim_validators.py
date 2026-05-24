"""Tests for book_sim.validators module."""

import pytest

from book_sim.validators import (
    ALLOWED_PRIVACY_MODES,
    validate_max_length,
    validate_non_empty_string,
    validate_positive_int,
    validate_privacy_mode,
)


class TestValidatePrivacyMode:
    def test_validate_privacy_mode_valid_values(self):
        for mode in ALLOWED_PRIVACY_MODES:
            assert validate_privacy_mode(mode) == mode

    def test_validate_privacy_mode_invalid_raises(self):
        with pytest.raises(ValueError, match="Unsupported privacy_mode"):
            validate_privacy_mode("invalid_mode")

    def test_validate_privacy_mode_default(self):
        assert validate_privacy_mode(None) == "hybrid_safe"
        assert validate_privacy_mode("") == "hybrid_safe"

    def test_validate_privacy_mode_strips_whitespace(self):
        assert validate_privacy_mode("  local_only  ") == "local_only"
        assert validate_privacy_mode("\tcloud_quality\n") == "cloud_quality"


class TestValidatePositiveInt:
    def test_validate_positive_int_valid(self):
        assert validate_positive_int(5, "count") == 5
        assert validate_positive_int("10", "count") == 10
        assert validate_positive_int(1, "count", minimum=1) == 1

    def test_validate_positive_int_below_minimum_raises(self):
        with pytest.raises(ValueError, match="must be >= 1"):
            validate_positive_int(0, "count")
        with pytest.raises(ValueError, match="must be >= 5"):
            validate_positive_int(3, "count", minimum=5)

    def test_validate_positive_int_non_numeric_raises(self):
        with pytest.raises(ValueError, match="must be an integer"):
            validate_positive_int("abc", "count")
        with pytest.raises(ValueError, match="must be an integer"):
            validate_positive_int(None, "count")


class TestValidateNonEmptyString:
    def test_validate_non_empty_string_valid(self):
        assert validate_non_empty_string("hello", "name") == "hello"
        assert validate_non_empty_string(123, "name") == "123"

    def test_validate_non_empty_string_none_raises(self):
        with pytest.raises(ValueError, match="is required"):
            validate_non_empty_string(None, "name")

    def test_validate_non_empty_string_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            validate_non_empty_string("", "name")
        with pytest.raises(ValueError, match="must not be empty"):
            validate_non_empty_string("   ", "name")


class TestValidateMaxLength:
    def test_validate_max_length_within_limit(self):
        assert validate_max_length("hello", "name", 10) == "hello"
        assert validate_max_length("a" * 50, "text", 50) == "a" * 50

    def test_validate_max_length_exceeds_raises(self):
        with pytest.raises(ValueError, match="exceeds maximum length"):
            validate_max_length("a" * 101, "text", 100)
