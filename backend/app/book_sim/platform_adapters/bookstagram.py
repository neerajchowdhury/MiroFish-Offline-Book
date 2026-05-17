"""Synthetic Bookstagram adapter."""

from __future__ import annotations

from .base import AdapterContext, BasePlatformAdapter
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class BookstagramAdapter(BasePlatformAdapter):
    platform_name = "bookstagram"

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> dict:
        book = self._book_signals(evidence_pack)
        return {
            "caption": (
                f"{book['title']} looks like {book['tone'] or 'a mood'} and reads like "
                f"{', '.join(private_reaction.praise[:2] or book['themes'][:2] or ['a marked-up favorite'])}."
            ),
            "carousel_idea": [
                "cover shot with tabs",
                f"quote slide featuring {book['themes'][0] if book['themes'] else 'the strongest line'}",
                "final slide with shelf verdict",
            ],
            "aesthetic_tags": [book["genre"].replace(" ", "_"), "annotated_copy", "reading_night"],
            "quote_card_candidates": private_reaction.notable_quotes[:3] or [book["premise"][:140]],
            "save_share_reason": "save for vibes and share for the quote density",
            "evidence_refs": self._evidence_refs(evidence_pack, private_reaction),
        }
