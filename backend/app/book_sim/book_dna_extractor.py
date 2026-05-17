"""Book DNA extraction with router-aware synthesis and heuristic fallback."""

from __future__ import annotations

import re
from typing import List, Optional

from .manuscript_chunker import ManuscriptChunker
from .models import BookDNA, ChapterMap, ManuscriptInput


class BookDNAExtractor:
    """Create Book DNA using router-backed synthesis when allowed."""

    def __init__(self, model_router=None) -> None:
        self.model_router = model_router

    def _heuristic_genre(self, text: str, book_type: str) -> tuple[str, Optional[str]]:
        lowered = text.lower()
        if book_type == "nonfiction":
            if "framework" in lowered or "strategy" in lowered:
                return "business nonfiction", "practical strategy"
            if "history" in lowered or "archive" in lowered:
                return "history nonfiction", None
            return "nonfiction", None
        if any(word in lowered for word in ("dragon", "magic", "spell", "kingdom")):
            return "fantasy", None
        if any(word in lowered for word in ("murder", "detective", "mystery", "clue")):
            return "mystery", None
        if any(word in lowered for word in ("love", "kiss", "romance", "heart")):
            return "romance", None
        return "fiction" if book_type == "fiction" else "mixed/unknown", None

    def _heuristic_book_dna(
        self,
        manuscript: ManuscriptInput,
        book_type: str,
        chapter_map: ChapterMap,
    ) -> BookDNA:
        first_summary = chapter_map.chapters[0].summary if chapter_map.chapters else manuscript.text[:240]
        genre, subgenre = self._heuristic_genre(manuscript.text, book_type)
        themes = []
        lowered = manuscript.text.lower()
        for theme in ("grief", "memory", "power", "identity", "ambition", "trust", "leadership", "change"):
            if theme in lowered:
                themes.append(theme)
        if not themes:
            themes = ["human change"] if book_type == "nonfiction" else ["identity"]

        target_reader = "broad readers"
        if book_type == "nonfiction":
            target_reader = "practical nonfiction readers"
        elif genre in ("mystery", "fantasy", "romance"):
            target_reader = f"{genre} readers"
        elif book_type == "fiction":
            target_reader = "fiction readers"

        return BookDNA(
            title=manuscript.title,
            premise=first_summary[:220],
            genre=genre,
            book_type=book_type,
            subgenre=subgenre,
            tone=chapter_map.chapters[0].pacing_note if chapter_map.chapters else None,
            emotional_promise=", ".join(chapter_map.chapters[0].emotional_beats[:2]) if chapter_map.chapters else None,
            narrative_engine=chapter_map.chapters[0].chapter_function if chapter_map.chapters else None,
            reading_difficulty="medium",
            target_reader=target_reader,
            comparable_titles=[],
            themes=themes[:5],
            spoilers_safe_summary=first_summary[:280],
            evidence_refs=["book_dna:heuristic"] + ([chapter_map.chapters[0].chapter_id] if chapter_map.chapters else []),
            confidence=0.6,
        )

    def extract(
        self,
        manuscript: ManuscriptInput,
        book_type: str,
        chapter_map: ChapterMap,
        privacy_mode: str,
    ) -> BookDNA:
        route_name = "local_ollama" if privacy_mode == "local_only" else "gemini_fast"
        if not self.model_router:
            return self._heuristic_book_dna(manuscript, book_type, chapter_map)

        first_chapters = [
            {
                "title": chapter.title,
                "summary": chapter.summary,
                "function": chapter.chapter_function,
                "emotional_beats": chapter.emotional_beats,
            }
            for chapter in chapter_map.chapters[:4]
        ]
        prompt = (
            "Create Book DNA JSON for a manuscript.\n"
            "Return keys: title, premise, genre, subgenre, tone, emotional_promise, narrative_engine, "
            "reading_difficulty, target_reader, comparable_titles, themes, spoilers_safe_summary, confidence.\n"
            f"Book type: {book_type}\n"
            f"Title: {manuscript.title}\n"
            f"Chapter evidence: {first_chapters}\n"
            f"Opening excerpt: {manuscript.text[:2500]}"
        )
        try:
            payload = self.model_router.generate_json(
                prompt=prompt,
                route_name=route_name,
                privacy_mode=privacy_mode,
                system_prompt="You produce compact book intelligence JSON. No markdown.",
                temperature=0.1,
                max_tokens=900,
            )
            return BookDNA(
                title=str(payload.get("title", manuscript.title)),
                premise=str(payload.get("premise", ""))[:300],
                genre=str(payload.get("genre", "mixed/unknown")),
                book_type=book_type,
                subgenre=payload.get("subgenre"),
                tone=payload.get("tone"),
                emotional_promise=payload.get("emotional_promise"),
                narrative_engine=payload.get("narrative_engine"),
                reading_difficulty=payload.get("reading_difficulty"),
                target_reader=payload.get("target_reader"),
                comparable_titles=list(payload.get("comparable_titles", []) or []),
                themes=list(payload.get("themes", []) or []),
                spoilers_safe_summary=payload.get("spoilers_safe_summary"),
                evidence_refs=["book_dna:llm"] + [chapter.chapter_id for chapter in chapter_map.chapters[:2]],
                confidence=float(payload.get("confidence", 0.8)),
            )
        except Exception:
            return self._heuristic_book_dna(manuscript, book_type, chapter_map)
