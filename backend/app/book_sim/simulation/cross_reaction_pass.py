"""Bounded cross-reaction pass to avoid many-to-many explosion."""

from __future__ import annotations

import hashlib
import json
import random
from typing import List, Optional, Sequence, Tuple

from ..local_cache import LocalArtifactCache
from ..models import CrossReaction, PlatformPost, PrivateReaderReaction, ReaderPersona


class CrossReactionPass:
    """Generate bounded cross-reader reactions from top-signal posts."""

    def __init__(
        self,
        cache: Optional[LocalArtifactCache] = None,
        cross_reaction_posts: int = 8,
        max_reaction_rounds: int = 2,
    ) -> None:
        self.cache = cache or LocalArtifactCache()
        self.cross_reaction_posts = cross_reaction_posts
        self.max_reaction_rounds = max_reaction_rounds

    def run(
        self,
        personas: Sequence[ReaderPersona],
        private_reactions: Sequence[PrivateReaderReaction],
        platform_posts: Sequence[PlatformPost],
        simulation_id: str,
        simulation_seed: Optional[int] = None,
        round_number: int = 1,
    ) -> Tuple[List[CrossReaction], List[PrivateReaderReaction]]:
        cache_key = self._cache_key(personas, private_reactions, platform_posts, simulation_id, simulation_seed, round_number)
        cached = self.cache.get_json("simulation_cross_reactions", cache_key)
        if cached:
            reactions = [CrossReaction.from_dict(item) for item in cached.get("cross_reactions", [])]
            updated = [PrivateReaderReaction.from_dict(item) for item in cached.get("updated_private_reactions", [])]
            return reactions, updated

        top_posts = self._top_posts(platform_posts)
        updated_private_reactions = {reaction.persona_id: PrivateReaderReaction.from_dict(reaction.to_dict()) for reaction in private_reactions}
        cross_reactions: List[CrossReaction] = []

        # One summary reaction per persona per round keeps the reaction graph bounded.
        for persona in personas:
            available_posts = [post for post in top_posts if post.persona_id != persona.persona_id]
            if not available_posts:
                continue
            rng = random.Random(f"{simulation_seed}|{simulation_id}|{round_number}|{persona.persona_id}")
            posts_to_sample = min(len(available_posts), rng.randint(3, 7))
            sampled_posts = rng.sample(available_posts, posts_to_sample)
            rating_shift = round(sum((post.rating or 3.0) - 3.0 for post in sampled_posts) / (posts_to_sample * 10.0), 3)
            recommendation_shift = round(sum(post.engagement_prediction or 0.0 for post in sampled_posts) / (posts_to_sample * 4.0), 3)
            stance_shift = "more_positive" if rating_shift > 0.05 else "more_negative" if rating_shift < -0.05 else "stable"
            agree_probability = round(max(0.0, min(1.0, 0.45 + persona.susceptibility_to_peer_reaction * 0.4 + rating_shift)), 3)
            disagree_probability = round(max(0.0, min(1.0, 1.0 - agree_probability)), 3)

            current = updated_private_reactions[persona.persona_id]
            current.rating = round(max(1.0, min(5.0, (current.rating or 3.0) + rating_shift)), 2)
            current.recommendation_probability = round(
                max(0.0, min(1.0, (current.recommendation_probability or 0.5) + recommendation_shift)),
                3,
            )
            current.sentiment = self._shift_sentiment(current.sentiment or "mixed", stance_shift)
            current.evidence_refs = list(dict.fromkeys(list(current.evidence_refs) + [post.post_id for post in sampled_posts]))

            cross_reactions.append(
                CrossReaction(
                    reaction_id=self._reaction_id(simulation_id, persona.persona_id, round_number),
                    simulation_id=simulation_id,
                    source_post_id=sampled_posts[0].post_id,
                    target_post_id=sampled_posts[-1].post_id,
                    persona_id=persona.persona_id,
                    platform=persona.platform or persona.platform_home,
                    reacted_post_ids=[post.post_id for post in sampled_posts],
                    stance_shift=stance_shift,
                    agree_probability=agree_probability,
                    disagree_probability=disagree_probability,
                    reply_likelihood=round(max(0.0, min(1.0, persona.controversy_sensitivity * 0.5 + agree_probability * 0.3)), 3),
                    rating_shift=rating_shift,
                    recommendation_shift=recommendation_shift,
                    sentiment=current.sentiment,
                    evidence_refs=list(dict.fromkeys([ref for post in sampled_posts for ref in post.evidence_refs])),
                    confidence=current.confidence,
                )
            )

        updated_list = list(updated_private_reactions.values())
        self.cache.set_json(
            "simulation_cross_reactions",
            cache_key,
            {
                "cross_reactions": [reaction.to_dict() for reaction in cross_reactions],
                "updated_private_reactions": [reaction.to_dict() for reaction in updated_list],
            },
        )
        return cross_reactions, updated_list

    def _top_posts(self, platform_posts: Sequence[PlatformPost]) -> List[PlatformPost]:
        ranked = sorted(
            platform_posts,
            key=lambda post: ((post.engagement_prediction or 0.0), abs((post.rating or 3.0) - 3.0)),
            reverse=True,
        )
        return ranked[: self.cross_reaction_posts]

    def _shift_sentiment(self, current_sentiment: str, stance_shift: str) -> str:
        if stance_shift == "more_positive":
            return "positive" if current_sentiment != "positive" else current_sentiment
        if stance_shift == "more_negative":
            return "negative" if current_sentiment != "negative" else current_sentiment
        return current_sentiment

    def _cache_key(
        self,
        personas: Sequence[ReaderPersona],
        private_reactions: Sequence[PrivateReaderReaction],
        platform_posts: Sequence[PlatformPost],
        simulation_id: str,
        simulation_seed: Optional[int],
        round_number: int,
    ) -> str:
        payload = {
            "simulation_id": simulation_id,
            "simulation_seed": simulation_seed,
            "round_number": round_number,
            "personas": [persona.to_dict() for persona in personas],
            "private_reactions": [reaction.to_dict() for reaction in private_reactions],
            "platform_posts": [post.to_dict() for post in platform_posts],
            "cross_reaction_posts": self.cross_reaction_posts,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def _reaction_id(self, simulation_id: str, persona_id: str, round_number: int) -> str:
        digest = hashlib.sha256(f"{simulation_id}:{persona_id}:{round_number}:cross".encode("utf-8")).hexdigest()
        return f"cross_{digest[:12]}"
