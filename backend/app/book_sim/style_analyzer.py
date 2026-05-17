"""Style analysis for Swarmbook evidence-pack generation."""

from __future__ import annotations

from typing import List

from .manuscript_chunker import ManuscriptChunker
from .models import StyleMap


class StyleAnalyzer:
    """Analyze prose density, clarity, rhythm, and accessibility."""

    def analyze(self, book_id: str, text: str) -> StyleMap:
        sentences = ManuscriptChunker._sentences(text)
        paragraphs = ManuscriptChunker._paragraphs(text)
        word_count = len(text.split())
        avg_sentence = sum(len(sentence.split()) for sentence in sentences) / max(len(sentences), 1)
        avg_paragraph = sum(len(paragraph.split()) for paragraph in paragraphs) / max(len(paragraphs), 1)
        quote_count = text.count('"') + text.count("'")

        prose_density = "high" if avg_sentence >= 22 or avg_paragraph >= 110 else "medium" if avg_sentence >= 14 else "low"
        clarity = "high" if avg_sentence <= 18 else "medium" if avg_sentence <= 26 else "low"
        rhythm = "staccato" if avg_sentence <= 12 else "rolling" if avg_sentence >= 24 else "balanced"
        quoteability = "high" if quote_count >= max(4, word_count // 250) else "medium" if quote_count >= 2 else "low"
        accessibility = "high" if clarity == "high" and prose_density != "high" else "medium" if clarity != "low" else "low"

        style_notes: List[str] = []
        if prose_density == "high":
            style_notes.append("dense prose may slow some readers")
        if quoteability == "high":
            style_notes.append("contains excerpt-friendly lines or dialogue")
        if avg_paragraph >= 120:
            style_notes.append("long paragraphs may increase reading friction")
        if not style_notes:
            style_notes.append("style appears steady and readable")

        return StyleMap(
            book_id=book_id,
            prose_density=prose_density,
            clarity=clarity,
            rhythm=rhythm,
            voice_consistency="steady",
            quoteability=quoteability,
            accessibility=accessibility,
            style_notes=style_notes,
            evidence_refs=["style:global"],
            confidence=0.72,
        )
