"""Tests for book_sim.risk_detector module."""

import pytest

from book_sim.risk_detector import RiskDetector
from book_sim.models import (
    ChapterMap,
    ChapterSummary,
    CharacterMap,
    ClaimMap,
    ClaimProfile,
    MarketSurface,
    RiskMap,
    StyleMap,
)


@pytest.fixture
def detector():
    return RiskDetector()


@pytest.fixture
def empty_chapter_map():
    return ChapterMap(book_id="test_book", chapters=[], total_chapters=0)


@pytest.fixture
def slow_chapter_map():
    chapter = ChapterSummary(
        chapter_id="chapter_001",
        chapter_number=1,
        title="Slow Chapter",
        summary="A very long and slow chapter.",
        pacing="slow",
        pacing_note="Long sentences or dense paragraphs suggest slower pacing.",
        likely_reader_friction=["long_dense_paragraphs"],
        evidence_refs=["chapter_001"],
    )
    return ChapterMap(book_id="test_book", chapters=[chapter], total_chapters=1)


@pytest.fixture
def low_accessibility_style_map():
    return StyleMap(
        book_id="test_book",
        prose_density="high",
        clarity="low",
        rhythm="rolling",
        accessibility="low",
        style_notes=["dense prose may slow some readers"],
        evidence_refs=["style:global"],
    )


@pytest.fixture
def empty_market_surface():
    return MarketSurface(book_id="test_book")


@pytest.fixture
def empty_character_map():
    return CharacterMap(book_id="test_book")


@pytest.fixture
def empty_claim_map():
    return ClaimMap(book_id="test_book")


@pytest.fixture
def claim_map_with_risks():
    claim = ClaimProfile(
        claim_id="claim_001",
        claim_text="This is a bold claim that should be verified.",
        support_quality="low",
        factual_risk_flags=["absolute_claim_without_visible_support"],
        evidence_refs=["claim_001"],
    )
    return ClaimMap(book_id="test_book", claims=[claim])


class TestBuildRiskMapReturnsRiskMap:
    def test_build_risk_map_returns_risk_map(
        self, detector, empty_chapter_map, empty_market_surface,
        empty_character_map, empty_claim_map,
    ):
        style_map = StyleMap(book_id="test_book")
        result = detector.build_risk_map(
            book_id="test_book",
            book_type="fiction",
            chapter_map=empty_chapter_map,
            style_map=style_map,
            market_surface=empty_market_surface,
            character_map=empty_character_map,
            claim_map=empty_claim_map,
        )
        assert isinstance(result, RiskMap)
        assert result.book_id == "test_book"


class TestPacingRiskDetectedForSlowText:
    def test_pacing_risk_detected_for_slow_text(
        self, detector, slow_chapter_map, empty_market_surface,
        empty_character_map, empty_claim_map,
    ):
        style_map = StyleMap(book_id="test_book")
        result = detector.build_risk_map(
            book_id="test_book",
            book_type="fiction",
            chapter_map=slow_chapter_map,
            style_map=style_map,
            market_surface=empty_market_surface,
            character_map=empty_character_map,
            claim_map=empty_claim_map,
        )
        pacing_risks = [r for r in result.risks if r.risk_type == "pacing_drag"]
        assert len(pacing_risks) >= 1


class TestStyleRiskDetected:
    def test_style_risk_detected(
        self, detector, empty_chapter_map, empty_market_surface,
        empty_character_map, empty_claim_map, low_accessibility_style_map,
    ):
        result = detector.build_risk_map(
            book_id="test_book",
            book_type="fiction",
            chapter_map=empty_chapter_map,
            style_map=low_accessibility_style_map,
            market_surface=empty_market_surface,
            character_map=empty_character_map,
            claim_map=empty_claim_map,
        )
        style_risks = [r for r in result.risks if r.risk_type == "style_accessibility"]
        assert len(style_risks) >= 1


class TestPositioningRiskDetected:
    def test_positioning_risk_detected(
        self, detector, empty_chapter_map, empty_character_map,
        empty_claim_map,
    ):
        market_surface = MarketSurface(
            book_id="test_book",
            promise_gap="Blurb promises action but text is slow.",
            target_segments=["fiction_readers"],
            evidence_refs=["market:001"],
        )
        style_map = StyleMap(book_id="test_book")
        result = detector.build_risk_map(
            book_id="test_book",
            book_type="fiction",
            chapter_map=empty_chapter_map,
            style_map=style_map,
            market_surface=market_surface,
            character_map=empty_character_map,
            claim_map=empty_claim_map,
        )
        positioning_risks = [r for r in result.risks if r.risk_type == "positioning_gap"]
        assert len(positioning_risks) >= 1


class TestEmptyTextReturnsEmptyRisks:
    def test_empty_text_returns_empty_risks(
        self, detector, empty_chapter_map, empty_market_surface,
        empty_character_map, empty_claim_map,
    ):
        style_map = StyleMap(book_id="test_book")
        result = detector.build_risk_map(
            book_id="test_book",
            book_type="nonfiction",
            chapter_map=empty_chapter_map,
            style_map=style_map,
            market_surface=empty_market_surface,
            character_map=empty_character_map,
            claim_map=empty_claim_map,
        )
        assert len(result.risks) == 0
        assert "No major" in result.risk_summary
