"""Synthetic X adapter."""

from __future__ import annotations

from .base import AdapterContext, BasePlatformAdapter
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class XPlatformAdapter(BasePlatformAdapter):
    platform_name = "x"

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> dict:
        book = self._book_signals(evidence_pack)
        controversy = private_reaction.friction[:1] or book["risks"][:1] or ["the pacing discourse"]
        return {
            "hot_take": f"{book['title']} is either a 5-star obsession or proof that {controversy[0]} kills momentum.",
            "quote_tweet": f"QT: the book absolutely delivers on {', '.join(private_reaction.praise[:1] or book['themes'][:1] or ['its promise'])}.",
            "controversy_compression": f"Compressed discourse: {controversy[0]} vs payoff.",
            "author_brand_reaction": "helps author brand if they lean into the strong opinion traffic",
            "evidence_refs": self._evidence_refs(evidence_pack, private_reaction),
        }
