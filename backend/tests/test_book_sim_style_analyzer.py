"""Tests for book_sim.style_analyzer module."""

import pytest

from book_sim.style_analyzer import StyleAnalyzer
from book_sim.models import StyleMap


@pytest.fixture
def analyzer():
    return StyleAnalyzer()


class TestAnalyzeReturnsStyleMap:
    def test_analyze_returns_style_map(self, analyzer):
        text = "This is a simple sentence. Here is another one."
        result = analyzer.analyze(book_id="test_book", text=text)
        assert isinstance(result, StyleMap)
        assert result.book_id == "test_book"


class TestStyleHasRequiredFields:
    def test_style_has_required_fields(self, analyzer):
        text = (
            "The quick brown fox jumped over the lazy dog. "
            "It was a beautiful day. The sun shone brightly. "
            "Birds sang in the trees. Everything felt peaceful."
        )
        result = analyzer.analyze(book_id="test_book", text=text)
        assert result.prose_density is not None
        assert result.clarity is not None
        assert result.rhythm is not None
        assert result.voice_consistency is not None
        assert result.quoteability is not None
        assert result.accessibility is not None
        assert len(result.style_notes) > 0


class TestEmptyTextReturnsDefaults:
    def test_empty_text_returns_defaults(self, analyzer):
        result = analyzer.analyze(book_id="test_book", text="")
        assert isinstance(result, StyleMap)
        assert result.prose_density == "low"
        assert result.clarity == "high"
        assert result.rhythm == "staccato"
        assert result.quoteability == "low"
        assert result.accessibility == "high"
        assert len(result.style_notes) > 0
