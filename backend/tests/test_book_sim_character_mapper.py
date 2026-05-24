"""Tests for book_sim.character_mapper module."""

import pytest

from book_sim.character_mapper import CharacterMapper
from book_sim.models import ChapterMap, ChapterSummary, CharacterMap


@pytest.fixture
def mapper():
    return CharacterMapper()


@pytest.fixture
def empty_chapter_map():
    return ChapterMap(book_id="test_book")


@pytest.fixture
def fiction_text_with_characters():
    return (
        "Alice walked into the room and looked at Bob.\n"
        "Bob said he was afraid of what might happen.\n"
        "Alice told Bob that everything would be fine.\n"
        "Bob looked at the door and whispered a prayer.\n"
        "Alice wanted to help Bob escape the situation.\n"
        "But Bob refused to leave without his sister Carol.\n"
        "Carol arrived and argued with Alice about the plan.\n"
        "Alice said Carol should trust her judgment.\n"
        "Bob and Carol walked together into the night.\n"
        "Alice watched them go, feeling a sense of grief."
    )


class TestBuildCharacterMapReturnsCharacterMap:
    def test_build_character_map_returns_character_map(self, mapper, empty_chapter_map, fiction_text_with_characters):
        result = mapper.build_character_map(
            book_id="test_book",
            text=fiction_text_with_characters,
            chapter_map=empty_chapter_map,
        )
        assert isinstance(result, CharacterMap)
        assert result.book_id == "test_book"


class TestCharactersExtractedFromFictionText:
    def test_characters_extracted_from_fiction_text(self, mapper, empty_chapter_map, fiction_text_with_characters):
        result = mapper.build_character_map(
            book_id="test_book",
            text=fiction_text_with_characters,
            chapter_map=empty_chapter_map,
        )
        names = [char.name for char in result.characters]
        assert "Alice" in names
        assert "Bob" in names


class TestEmptyTextReturnsEmptyCharacters:
    def test_empty_text_returns_empty_characters(self, mapper, empty_chapter_map):
        result = mapper.build_character_map(
            book_id="test_book",
            text="",
            chapter_map=empty_chapter_map,
        )
        assert isinstance(result, CharacterMap)
        assert len(result.characters) == 0
        assert result.cast_size == 0
