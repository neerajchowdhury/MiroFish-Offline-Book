"""Tests for book_sim.manuscript_chunker module."""

import pytest

from book_sim.manuscript_chunker import ManuscriptChunker


@pytest.fixture
def chunker():
    return ManuscriptChunker()


class TestDetectBookTypeFiction:
    def test_detect_book_type_fiction(self, chunker):
        text = (
            '"I don\'t believe you," she whispered, looking at the door.\n'
            "He walked across the room and sat down. The night was cold.\n"
            '"You always say that," he said. "But this time is different."\n'
            "She looked away, afraid of what might happen next."
        )
        result = chunker.detect_book_type(text)
        assert result == "fiction"


class TestDetectBookTypeNonfiction:
    def test_detect_book_type_nonfiction(self, chunker):
        text = (
            "This book argues that a new framework is essential for modern strategy.\n"
            "Research evidence shows that this principle improves outcomes.\n"
            "For example, a case study from 2020 demonstrates the strategy in action.\n"
            "In conclusion, the research supports this approach."
        )
        result = chunker.detect_book_type(text)
        assert result == "nonfiction"


class TestDetectChapterSegmentsWithHeadings:
    def test_detect_chapter_segments_with_headings(self, chunker):
        text = (
            "# Chapter One\n"
            "This is the first chapter content with some narrative.\n"
            "It continues for a few lines.\n\n"
            "## Chapter Two\n"
            "The second chapter begins here with different content.\n"
            "More text follows in this section."
        )
        segments = chunker.detect_chapter_segments(text)
        assert len(segments) == 2
        assert segments[0].chapter_id == "chapter_001"
        assert segments[0].chapter_number == 1
        assert segments[1].chapter_id == "chapter_002"
        assert segments[1].chapter_number == 2


class TestDetectChapterSegmentsWithoutHeadings:
    def test_detect_chapter_segments_without_headings(self, chunker):
        text = "This is a long text without any chapter headings. " * 200
        segments = chunker.detect_chapter_segments(text, chunk_size=500, overlap=50)
        assert len(segments) >= 1
        assert segments[0].chapter_id.startswith("chunk_")
        assert segments[0].title.startswith("Section ")


class TestFallbackSplitTextIntoChunks:
    def test_fallback_split_text_into_chunks(self, chunker):
        text = "Sentence one. Sentence two. Sentence three. " * 50
        chunks = chunker._fallback_split_text_into_chunks(text, chunk_size=200, overlap=30)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk) > 0


class TestEmptyTextHandling:
    def test_empty_text_handling(self, chunker):
        assert chunker.detect_book_type("") == "mixed_unknown"
        segments = chunker.detect_chapter_segments("")
        assert segments == []


class TestSingleParagraphText:
    def test_single_paragraph_text(self, chunker):
        text = "This is a single paragraph with no line breaks at all."
        result = chunker.detect_book_type(text)
        assert result == "mixed_unknown"
        segments = chunker.detect_chapter_segments(text)
        assert len(segments) >= 1


class TestVeryLongTextChunking:
    def test_very_long_text_chunking(self, chunker):
        text = "This is a paragraph. " * 2000
        segments = chunker.detect_chapter_segments(text, chunk_size=1000, overlap=100)
        assert len(segments) >= 1
        total_chars = sum(len(s.text) for s in segments)
        assert total_chars > 0
