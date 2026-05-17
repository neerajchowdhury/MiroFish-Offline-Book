"""Synthetic BookTok adapter."""

from __future__ import annotations

from .base import AdapterContext, BasePlatformAdapter
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class BookTokAdapter(BasePlatformAdapter):
    platform_name = "booktok"

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> dict:
        book = self._book_signals(evidence_pack)
        hook = (private_reaction.notable_quotes[:1] or book["hooks"][:1] or [book["premise"][:80]])[0]
        return {
            "video_script": (
                f"Stop scrolling if you want {book['genre']} with {book['tone'] or 'big feelings'}. "
                f"Act one: {hook}. Act two: why I couldn't stop thinking about "
                f"{', '.join(private_reaction.praise[:2] or book['themes'][:2] or ['the ending'])}."
            ),
            "trope_tags": [item.replace(" ", "_") for item in (persona.delight_triggers[:3] or book["themes"][:3] or ["big_emotions"])],
            "hook_line": f"If {book['title']} broke me in 15 seconds, that's your warning.",
            "visual_motif": ", ".join(book["chapter_titles"][:2] or book["themes"][:2] or ["annotated pages"]),
            "viral_trigger": "high" if persona.quote_sharing_probability >= 0.6 else "medium",
            "cringe_mockery_risk": "high" if persona.controversy_sensitivity >= 0.7 else "medium_low",
            "evidence_refs": self._evidence_refs(evidence_pack, private_reaction),
        }
