"""Heuristic fiction character extraction and relationship mapping."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Dict, List

from .manuscript_chunker import ManuscriptChunker
from .models import CharacterMap, CharacterProfile, ChapterMap


class CharacterMapper:
    """Build fiction character profiles from lightweight heuristics."""

    _NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b")
    _STOP_NAMES = {
        "Chapter", "Part", "The", "A", "An", "He", "She", "They", "I", "We", "It",
        "Monday", "Tuesday", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    }
    _RELATION_WORDS = ("friend", "sister", "brother", "mother", "father", "mentor", "ally", "enemy", "lover")

    @staticmethod
    def _sentences(text: str) -> List[str]:
        return ManuscriptChunker._sentences(text)

    def _extract_names(self, text: str) -> List[str]:
        counts = Counter()
        for match in self._NAME_RE.findall(text):
            cleaned = match.strip()
            if cleaned in self._STOP_NAMES:
                continue
            if len(cleaned) <= 2:
                continue
            counts[cleaned] += 1
        return [name for name, count in counts.items() if count >= 2][:12]

    def build_character_map(self, book_id: str, text: str, chapter_map: ChapterMap) -> CharacterMap:
        names = self._extract_names(text)
        sentences = self._sentences(text)
        profiles: List[CharacterProfile] = []
        relationship_map: Dict[str, Dict[str, str]] = defaultdict(dict)

        for sentence in sentences:
            present_names = [name for name in names if name in sentence]
            if len(present_names) < 2:
                continue
            lowered = sentence.lower()
            relation = "connected_to"
            for keyword in self._RELATION_WORDS:
                if keyword in lowered:
                    relation = keyword
                    break
            source = present_names[0]
            for target in present_names[1:]:
                relationship_map[source][target] = relation
                relationship_map[target][source] = relation

        for index, name in enumerate(names, start=1):
            name_sentences = [sentence for sentence in sentences if name in sentence][:8]
            lowered_sentences = [sentence.lower() for sentence in name_sentences]

            motivations = []
            contradictions = []
            conflicts = []
            for sentence, lowered in zip(name_sentences, lowered_sentences):
                if "wanted to" in lowered or "wants to" in lowered or "needs to" in lowered:
                    motivations.append(sentence[:160])
                if any(word in lowered for word in ("but ", "however", "although", "yet ")):
                    contradictions.append(sentence[:160])
                if any(word in lowered for word in ("against", "argued", "fear", "conflict", "refused")):
                    conflicts.append(sentence[:160])

            first_context = name_sentences[0][:160] if name_sentences else ""
            last_context = name_sentences[-1][:160] if name_sentences else ""
            arc_summary = None
            if first_context or last_context:
                arc_summary = f"{name} moves from '{first_context}' toward '{last_context}'."

            profiles.append(
                CharacterProfile(
                    character_id=f"character_{index:03d}",
                    name=name,
                    role="major" if len(name_sentences) >= 4 else "supporting",
                    motivations=motivations[:3],
                    goals=motivations[:3],
                    conflicts=conflicts[:3],
                    contradictions=contradictions[:3],
                    relationships=relationship_map.get(name, {}),
                    arc_summary=arc_summary,
                    attachment_potential=min(0.95, 0.3 + len(name_sentences) * 0.07),
                    reader_friction=["unclear_motivation"] if not motivations and len(name_sentences) >= 3 else [],
                    evidence_refs=[chapter.chapter_id for chapter in chapter_map.chapters if name in chapter.summary or name in " ".join(chapter.key_beats)],
                    confidence=0.62,
                )
            )

        summary = None
        if profiles:
            summary = f"Detected {len(profiles)} recurring named characters."

        return CharacterMap(
            book_id=book_id,
            characters=profiles,
            cast_size=len(profiles),
            relationship_graph_summary=summary,
            evidence_refs=[profile.character_id for profile in profiles],
            confidence=0.64 if profiles else 0.4,
        )
