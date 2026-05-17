"""Synthetic Goodreads adapter."""

from __future__ import annotations

from .base import AdapterContext, BasePlatformAdapter
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class GoodreadsAdapter(BasePlatformAdapter):
    platform_name = "goodreads"

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> dict:
        book = self._book_signals(evidence_pack)
        rating = round(private_reaction.rating or 3.5)
        dnf_probability = private_reaction.dnf_probability or 0.0
        return {
            "star_rating": max(1, min(5, int(rating))),
            "review_title": f"{book['title']}: strong {book['tone'] or 'reader'} payoff",
            "review_body": (
                f"I came for the {book['genre']} promise and stayed for "
                f"{', '.join(private_reaction.praise[:2] or book['themes'][:2] or ['the momentum'])}. "
                f"My main friction was {', '.join(private_reaction.friction[:2] or book['risks'][:2] or ['the pacing'])}."
            ),
            "shelf_tags": [book["genre"].replace(" ", "-"), persona.cohort or "reader-cohort", "swarmbook-simulated"],
            "dnf_note": "Considered DNF" if dnf_probability >= persona.dnf_threshold else "Finished the book",
            "quote_highlights": private_reaction.notable_quotes[:3] or [book["premise"][:140]],
            "evidence_refs": self._evidence_refs(evidence_pack, private_reaction),
        }
