"""Synthetic newsletter adapter."""

from __future__ import annotations

from .base import AdapterContext, BasePlatformAdapter
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class NewsletterAdapter(BasePlatformAdapter):
    platform_name = "newsletter"

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> dict:
        book = self._book_signals(evidence_pack)
        return {
            "recommendation_blurb": (
                f"If your subscribers respond to {book['genre']} with a strong thematic center, "
                f"{book['title']} is worth a look for {', '.join(private_reaction.praise[:2] or book['themes'][:2] or ['its clarity'])}."
            ),
            "target_subscriber_type": ", ".join(book["target_segments"][:2] or [persona.cohort or "engaged readers"]),
            "referral_likelihood": "high" if persona.influence_weight >= 0.65 else "medium",
            "evidence_refs": self._evidence_refs(evidence_pack, private_reaction),
        }
