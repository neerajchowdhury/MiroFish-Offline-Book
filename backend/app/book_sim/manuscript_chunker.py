"""Manuscript chunking, book-type detection, and chapter summarization."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence

from .models import ChapterMap, ChapterSummary


@dataclass
class ChapterSegment:
    """Internal representation of a detected chapter or fallback chunk."""

    chapter_id: str
    chapter_number: int
    title: str
    text: str
    evidence_ref: str


class ManuscriptChunker:
    """Detect book type, chapter boundaries, and chapter summaries."""

    _CHAPTER_HEADING_RE = re.compile(
        r"^(?:chapter|chap\.|part)\s+[\divxlcm]+(?:\s*[:.\-]\s*|\s+)?(.+)?$",
        re.IGNORECASE,
    )
    _MARKDOWN_HEADING_RE = re.compile(r"^#{1,3}\s+(.+)$")
    _FICTION_MARKERS = (
        "said", "looked", "walked", "whispered", "door", "night", "room", "\"", "'",
    )
    _NONFICTION_MARKERS = (
        "framework", "principle", "research", "evidence", "strategy", "case study",
        "for example", "in conclusion", "this book", "step ",
    )
    _EMOTION_LEXICON = {
        "fear": ("fear", "afraid", "anxious", "panic"),
        "hope": ("hope", "promise", "chance", "future"),
        "grief": ("grief", "loss", "mourning", "sad"),
        "joy": ("joy", "relief", "delight", "happy"),
        "anger": ("anger", "furious", "rage", "resent"),
        "love": ("love", "care", "tender", "devotion"),
        "tension": ("tension", "strain", "conflict", "argument"),
    }

    def __init__(self, model_router=None) -> None:
        self.model_router = model_router

    @staticmethod
    def _sentences(text: str) -> List[str]:
        parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
        return [part.strip() for part in parts if part.strip()]

    @staticmethod
    def _paragraphs(text: str) -> List[str]:
        return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]

    def preprocess(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def _fallback_split_text_into_chunks(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> List[str]:
        if len(text) <= chunk_size:
            return [text] if text.strip() else []

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end < len(text):
                for separator in (".\n", "!\n", "?\n", "\n\n", ". ", "! ", "? "):
                    last_sep = text[start:end].rfind(separator)
                    if last_sep != -1 and last_sep > chunk_size * 0.3:
                        end = start + last_sep + len(separator)
                        break
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap if end < len(text) else len(text)
        return chunks

    def detect_book_type(self, text: str) -> str:
        """Classify manuscript as fiction, nonfiction, or mixed/unknown."""
        lowered = text.lower()
        fiction_score = sum(lowered.count(marker) for marker in self._FICTION_MARKERS)
        nonfiction_score = sum(lowered.count(marker) for marker in self._NONFICTION_MARKERS)

        if nonfiction_score >= fiction_score * 1.35 and nonfiction_score >= 3:
            return "nonfiction"
        if fiction_score >= nonfiction_score * 1.35 and fiction_score >= 3:
            return "fiction"
        return "mixed_unknown"

    def detect_chapter_segments(
        self,
        text: str,
        chunk_size: int = 4000,
        overlap: int = 250,
    ) -> List[ChapterSegment]:
        """Detect chapter boundaries from headings, then fall back to chunking."""
        cleaned = self.preprocess(text)
        lines = cleaned.split("\n")

        headings: List[tuple[int, str]] = []
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            markdown_match = self._MARKDOWN_HEADING_RE.match(stripped)
            chapter_match = self._CHAPTER_HEADING_RE.match(stripped)
            short_upper = stripped.isupper() and 3 <= len(stripped) <= 80 and len(stripped.split()) <= 8
            if markdown_match:
                headings.append((index, markdown_match.group(1).strip()))
            elif chapter_match:
                title = stripped if not chapter_match.group(1) else chapter_match.group(1).strip()
                headings.append((index, title))
            elif short_upper:
                headings.append((index, stripped.title()))

        if headings:
            segments: List[ChapterSegment] = []
            for idx, (line_index, title) in enumerate(headings):
                start = line_index + 1
                end = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
                chapter_text = "\n".join(lines[start:end]).strip()
                if not chapter_text:
                    continue
                chapter_id = f"chapter_{idx + 1:03d}"
                segments.append(
                    ChapterSegment(
                        chapter_id=chapter_id,
                        chapter_number=idx + 1,
                        title=title or f"Chapter {idx + 1}",
                        text=chapter_text,
                        evidence_ref=f"chapter:{chapter_id}",
                    )
                )
            if segments:
                return segments

        chunks = self._fallback_split_text_into_chunks(cleaned, chunk_size=chunk_size, overlap=overlap)
        segments = []
        for idx, chunk in enumerate(chunks, start=1):
            chapter_id = f"chunk_{idx:03d}"
            segments.append(
                ChapterSegment(
                    chapter_id=chapter_id,
                    chapter_number=idx,
                    title=f"Section {idx}",
                    text=chunk,
                    evidence_ref=f"chapter:{chapter_id}",
                )
            )
        return segments

    def _detect_emotional_beats(self, text: str) -> List[str]:
        lowered = text.lower()
        beats = [
            label
            for label, markers in self._EMOTION_LEXICON.items()
            if any(marker in lowered for marker in markers)
        ]
        return beats[:4]

    def _detect_chapter_function(self, chapter_number: int, total: int, text: str, book_type: str) -> str:
        lowered = text.lower()
        if chapter_number == 1:
            return "opening"
        if chapter_number == total:
            return "resolution" if book_type == "fiction" else "conclusion"
        if book_type == "nonfiction" and any(marker in lowered for marker in ("framework", "principle", "step")):
            return "framework_definition"
        if "for example" in lowered or "case study" in lowered:
            return "case_study"
        if any(marker in lowered for marker in ("however", "but", "yet", "suddenly", "revealed")):
            return "turning_point"
        return "escalation"

    def _detect_pacing(self, text: str) -> tuple[str, str]:
        sentences = self._sentences(text)
        paragraphs = self._paragraphs(text)
        average_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        average_paragraph_length = sum(len(p.split()) for p in paragraphs) / max(len(paragraphs), 1)

        if average_sentence_length <= 13 and average_paragraph_length <= 70:
            return "fast", "Short sentences and quick paragraph turns suggest fast pacing."
        if average_sentence_length >= 24 or average_paragraph_length >= 120:
            return "slow", "Long sentences or dense paragraphs suggest slower pacing."
        return "measured", "The chapter balances movement and reflection at a measured pace."

    def _detect_friction(self, text: str, book_type: str) -> List[str]:
        friction: List[str] = []
        paragraphs = self._paragraphs(text)
        if any(len(paragraph.split()) > 180 for paragraph in paragraphs):
            friction.append("long_dense_paragraphs")
        if text.count("?") >= 4:
            friction.append("too_many_open_questions")
        if len(self._sentences(text)) <= 2 and len(text.split()) > 250:
            friction.append("summary_like_density")
        if book_type == "nonfiction" and sum(ch.isdigit() for ch in text) == 0 and "research" in text.lower():
            friction.append("claims_without_visible_support")
        if book_type == "fiction" and text.count('"') + text.count("'") == 0 and len(text.split()) > 500:
            friction.append("limited_dialogue_relief")
        return friction[:4]

    def _fallback_summary(
        self,
        segment: ChapterSegment,
        total_chapters: int,
        book_type: str,
    ) -> ChapterSummary:
        sentences = self._sentences(segment.text)
        summary = " ".join(sentences[:2]) if sentences else segment.text[:240]
        key_beats = [sentence[:140] for sentence in sentences[:3]]
        pacing, pacing_note = self._detect_pacing(segment.text)
        chapter_function = self._detect_chapter_function(
            segment.chapter_number, total_chapters, segment.text, book_type
        )
        return ChapterSummary(
            chapter_id=segment.chapter_id,
            chapter_number=segment.chapter_number,
            title=segment.title,
            summary=summary[:400],
            purpose=chapter_function,
            chapter_function=chapter_function,
            pacing=pacing,
            pacing_note=pacing_note,
            key_beats=key_beats,
            emotional_beats=self._detect_emotional_beats(segment.text),
            turning_points=key_beats[1:2],
            open_questions=[s for s in sentences if s.endswith("?")][:3],
            likely_reader_friction=self._detect_friction(segment.text, book_type),
            spoiler_notes=[],
            evidence_refs=[segment.evidence_ref],
            confidence=0.58,
        )

    def _llm_summary(
        self,
        segment: ChapterSegment,
        total_chapters: int,
        privacy_mode: str,
        book_type: str,
    ) -> Optional[ChapterSummary]:
        if not self.model_router:
            return None

        prompt = (
            "Create a chapter summary JSON for a book manuscript.\n"
            "Return keys: summary, emotional_beats, chapter_function, pacing_note, likely_reader_friction, key_beats.\n"
            f"Book type: {book_type}\n"
            f"Chapter title: {segment.title}\n"
            f"Chapter text:\n{segment.text[:3000]}"
        )
        try:
            payload = self.model_router.generate_json(
                prompt=prompt,
                route_name="local_ollama",
                privacy_mode=privacy_mode,
                system_prompt="You summarize manuscripts into compact JSON. No markdown.",
                temperature=0.1,
                max_tokens=700,
            )
        except Exception:
            return None

        pacing = payload.get("pacing", None)
        chapter_function = payload.get("chapter_function") or self._detect_chapter_function(
            segment.chapter_number, total_chapters, segment.text, book_type
        )
        return ChapterSummary(
            chapter_id=segment.chapter_id,
            chapter_number=segment.chapter_number,
            title=segment.title,
            summary=str(payload.get("summary", "")).strip()[:400],
            purpose=chapter_function,
            chapter_function=chapter_function,
            pacing=pacing,
            pacing_note=payload.get("pacing_note"),
            key_beats=list(payload.get("key_beats", []) or []),
            emotional_beats=list(payload.get("emotional_beats", []) or []),
            turning_points=list(payload.get("turning_points", []) or []),
            open_questions=list(payload.get("open_questions", []) or []),
            likely_reader_friction=list(payload.get("likely_reader_friction", []) or []),
            spoiler_notes=list(payload.get("spoiler_notes", []) or []),
            evidence_refs=[segment.evidence_ref],
            confidence=float(payload.get("confidence", 0.72)),
        )

    def build_chapter_map(
        self,
        book_id: str,
        text: str,
        privacy_mode: str,
        book_type: str,
        chunk_size: int = 4000,
        overlap: int = 250,
    ) -> ChapterMap:
        segments = self.detect_chapter_segments(text=text, chunk_size=chunk_size, overlap=overlap)
        chapters: List[ChapterSummary] = []
        for segment in segments:
            summary = self._llm_summary(segment, len(segments), privacy_mode, book_type)
            if summary is None:
                summary = self._fallback_summary(segment, len(segments), book_type)
            chapters.append(summary)

        pacing_profile = "measured"
        if chapters:
            slow_count = sum(1 for chapter in chapters if chapter.pacing == "slow")
            fast_count = sum(1 for chapter in chapters if chapter.pacing == "fast")
            if slow_count > fast_count:
                pacing_profile = "slow-leaning"
            elif fast_count > slow_count:
                pacing_profile = "fast-leaning"

        return ChapterMap(
            book_id=book_id,
            chapters=chapters,
            total_chapters=len(chapters),
            pacing_profile=pacing_profile,
            structural_notes=[f"Detected {len(chapters)} chapter sections."],
            evidence_refs=[chapter.chapter_id for chapter in chapters],
            confidence=0.7,
        )
