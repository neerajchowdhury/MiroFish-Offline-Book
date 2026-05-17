"""Synthetic book club adapter."""

from __future__ import annotations

from .base import AdapterContext, BasePlatformAdapter
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class BookclubAdapter(BasePlatformAdapter):
    platform_name = "bookclub"

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> dict:
        book = self._book_signals(evidence_pack)
        tension = private_reaction.friction[:1] or book["risks"][:1] or ["the central decision"]
        return {
            "discussion_questions": [
                f"Which part of {book['title']} best delivers on {book['themes'][0] if book['themes'] else 'its premise'}?",
                f"Did {tension[0]} weaken the reading experience or sharpen the debate?",
                "Would you recommend this to someone outside your usual genre lane?",
            ],
            "moral_disagreement_points": [tension[0], "character responsibility", "ending fairness"],
            "ending_debate_hooks": [
                "Was the ending earned?",
                "Did the emotional payoff outweigh the structural risk?",
            ],
            "evidence_refs": self._evidence_refs(evidence_pack, private_reaction),
        }
