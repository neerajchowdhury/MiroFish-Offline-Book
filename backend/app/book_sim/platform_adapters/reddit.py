"""Synthetic Reddit adapter."""

from __future__ import annotations

from .base import AdapterContext, BasePlatformAdapter
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class RedditAdapter(BasePlatformAdapter):
    platform_name = "reddit"

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> dict:
        book = self._book_signals(evidence_pack)
        logic_objection = (private_reaction.friction[:1] or book["risks"][:1] or ["the central framing"]) [0]
        return {
            "thread_title": f"[Discussion] {book['title']} works until {logic_objection}",
            "top_comment": (
                f"My thesis: the book succeeds because of {', '.join(private_reaction.praise[:2] or book['themes'][:2] or ['its internal logic'])}, "
                f"but it asks you to forgive {', '.join(private_reaction.friction[:2] or book['risks'][:2] or ['a weak section'])}."
            ),
            "skeptical_comment": f"I still don't buy the framing around {logic_objection}.",
            "debate_branch": [
                f"User A defends the {book['genre']} expectations.",
                "User B says the payoff earns the setup.",
                "User C argues the momentum collapses in the middle.",
            ],
            "logic_framing_objection": f"The sharpest objection is whether {logic_objection} is actually supported on the page.",
            "evidence_refs": self._evidence_refs(evidence_pack, private_reaction),
        }
