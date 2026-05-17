"""Platform-native post generation pass."""

from __future__ import annotations

import hashlib
import json
from typing import Dict, List, Optional, Sequence

from ..local_cache import LocalArtifactCache
from ..models import EvidencePack, PlatformPost, PrivateReaderReaction, ReaderPersona
from ..platform_adapters import AdapterContext, PLATFORM_ADAPTERS


class PlatformReactionPass:
    """Generate platform-native public posts from private reactions."""

    def __init__(self, cache: Optional[LocalArtifactCache] = None, model_router: object = None) -> None:
        self.cache = cache or LocalArtifactCache()
        self.model_router = model_router

    def run(
        self,
        personas: Sequence[ReaderPersona],
        private_reactions: Sequence[PrivateReaderReaction],
        evidence_pack: EvidencePack,
        simulation_id: str,
        round_number: int = 1,
        privacy_mode: str = "hybrid_safe",
        simulation_seed: Optional[int] = None,
    ) -> List[PlatformPost]:
        cache_key = self._cache_key(personas, private_reactions, evidence_pack, simulation_id, round_number, privacy_mode, simulation_seed)
        cached = self.cache.get_json("simulation_platform_reactions", cache_key)
        if cached:
            return [PlatformPost.from_dict(item) for item in cached.get("posts", [])]

        reaction_by_persona = {reaction.persona_id: reaction for reaction in private_reactions}
        posts: List[PlatformPost] = []
        for persona in personas:
            reaction = reaction_by_persona[persona.persona_id]
            adapter = self._adapter_for(persona.platform or persona.platform_home)
            context = AdapterContext(
                simulation_id=simulation_id,
                round_number=round_number,
                privacy_mode=privacy_mode,
                simulation_seed=simulation_seed,
            )
            posts.append(adapter.create_post(persona, evidence_pack, reaction, context))

        self.cache.set_json(
            "simulation_platform_reactions",
            cache_key,
            {"posts": [post.to_dict() for post in posts]},
        )
        return posts

    def _adapter_for(self, platform: str):
        adapter_cls = PLATFORM_ADAPTERS.get(platform.lower(), PLATFORM_ADAPTERS["goodreads"])
        return adapter_cls(model_router=self.model_router)

    def _cache_key(
        self,
        personas: Sequence[ReaderPersona],
        private_reactions: Sequence[PrivateReaderReaction],
        evidence_pack: EvidencePack,
        simulation_id: str,
        round_number: int,
        privacy_mode: str,
        simulation_seed: Optional[int],
    ) -> str:
        payload = {
            "simulation_id": simulation_id,
            "round_number": round_number,
            "privacy_mode": privacy_mode,
            "simulation_seed": simulation_seed,
            "personas": [persona.to_dict() for persona in personas],
            "private_reactions": [reaction.to_dict() for reaction in private_reactions],
            "evidence_pack": evidence_pack.to_dict(),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
