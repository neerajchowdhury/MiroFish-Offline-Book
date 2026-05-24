"""Tests for book_sim.nonfiction_claim_extractor module."""

import pytest

from book_sim.nonfiction_claim_extractor import NonfictionClaimExtractor
from book_sim.models import ChapterMap, ChapterSummary, ClaimMap


@pytest.fixture
def extractor():
    return NonfictionClaimExtractor()


@pytest.fixture
def empty_chapter_map():
    return ChapterMap(book_id="test_book")


@pytest.fixture
def sample_nonfiction_text():
    return (
        "This book argues that a new framework should be adopted by all teams.\n"
        "Research shows that this principle will improve productivity.\n"
        "For example, a study found that teams using this method saw gains.\n"
        "The key insight is that everyone must follow the step-by-step system.\n"
        "By the end, you will understand the model completely."
    )


class TestBuildClaimMapReturnsClaimMap:
    def test_build_claim_map_returns_claim_map(self, extractor, empty_chapter_map, sample_nonfiction_text):
        result = extractor.build_claim_map(
            book_id="test_book",
            text=sample_nonfiction_text,
            chapter_map=empty_chapter_map,
        )
        assert isinstance(result, ClaimMap)
        assert result.book_id == "test_book"


class TestClaimsHaveRequiredFields:
    def test_claims_have_required_fields(self, extractor, empty_chapter_map, sample_nonfiction_text):
        result = extractor.build_claim_map(
            book_id="test_book",
            text=sample_nonfiction_text,
            chapter_map=empty_chapter_map,
        )
        assert len(result.claims) > 0
        for claim in result.claims:
            assert claim.claim_id is not None
            assert claim.claim_text is not None
            assert claim.support_type is not None
            assert claim.support_quality is not None
            assert claim.evidence_strength is not None


class TestEmptyTextReturnsEmptyClaims:
    def test_empty_text_returns_empty_claims(self, extractor, empty_chapter_map):
        result = extractor.build_claim_map(
            book_id="test_book",
            text="",
            chapter_map=empty_chapter_map,
        )
        assert isinstance(result, ClaimMap)
        assert len(result.claims) == 0
        assert result.thesis_summary is None
