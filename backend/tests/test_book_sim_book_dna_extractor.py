"""Tests for book_sim.book_dna_extractor module."""

import pytest

from book_sim.book_dna_extractor import BookDNAExtractor
from book_sim.models import BookDNA, ChapterMap, ChapterSummary, ManuscriptInput


@pytest.fixture
def extractor():
    return BookDNAExtractor()


@pytest.fixture
def sample_manuscript():
    return ManuscriptInput(
        input_id="input_001",
        project_id="proj_001",
        title="The Dragon Kingdom",
        text=(
            "The dragon flew over the ancient kingdom, casting a spell of magic.\n"
            "The wizard looked at the mysterious door and whispered a prayer.\n"
            "She walked into the dark room, afraid of what she might find."
        ),
    )


@pytest.fixture
def sample_nonfiction_manuscript():
    return ManuscriptInput(
        input_id="input_002",
        project_id="proj_002",
        title="Leadership Strategy",
        text=(
            "This book presents a framework for modern leadership strategy.\n"
            "Research shows that effective leadership requires a systematic method.\n"
            "The key principle is that every leader should follow a step-by-step approach."
        ),
    )


@pytest.fixture
def sample_chapter_map():
    chapter = ChapterSummary(
        chapter_id="chapter_001",
        chapter_number=1,
        title="The Beginning",
        summary="The story opens with a dragon flying over a kingdom.",
        pacing="measured",
        pacing_note="The chapter balances movement and reflection at a measured pace.",
        emotional_beats=["fear", "hope"],
        chapter_function="opening",
        evidence_refs=["chapter_001"],
    )
    return ChapterMap(book_id="test_book", chapters=[chapter], total_chapters=1)


class TestExtractReturnsBookDNA:
    def test_extract_returns_book_dna(self, extractor, sample_manuscript, sample_chapter_map):
        result = extractor.extract(
            manuscript=sample_manuscript,
            book_type="fiction",
            chapter_map=sample_chapter_map,
            privacy_mode="local_only",
        )
        assert isinstance(result, BookDNA)
        assert result.title == "The Dragon Kingdom"


class TestHeuristicGenreFiction:
    def test_heuristic_genre_fiction(self, extractor, sample_manuscript, sample_chapter_map):
        result = extractor.extract(
            manuscript=sample_manuscript,
            book_type="fiction",
            chapter_map=sample_chapter_map,
            privacy_mode="local_only",
        )
        assert result.genre == "fantasy"


class TestHeuristicGenreNonfiction:
    def test_heuristic_genre_nonfiction(self, extractor, sample_nonfiction_manuscript, sample_chapter_map):
        result = extractor.extract(
            manuscript=sample_nonfiction_manuscript,
            book_type="nonfiction",
            chapter_map=sample_chapter_map,
            privacy_mode="local_only",
        )
        assert "business" in result.genre or "nonfiction" in result.genre


class TestEmptyTextHandling:
    def test_empty_text_handling(self, extractor):
        manuscript = ManuscriptInput(
            input_id="input_empty",
            project_id="proj_empty",
            title="Empty Book",
            text="",
        )
        chapter_map = ChapterMap(book_id="empty_book")
        result = extractor.extract(
            manuscript=manuscript,
            book_type="mixed_unknown",
            chapter_map=chapter_map,
            privacy_mode="local_only",
        )
        assert isinstance(result, BookDNA)
        assert result.title == "Empty Book"
