"""Private reading pass for deterministic reader-first reactions."""

from __future__ import annotations

import hashlib
import json
import random
from typing import Dict, List, Optional, Sequence

from ..local_cache import LocalArtifactCache
from ..models import EvidencePack, PrivateReaderReaction, ReaderPersona


class PrivateReadingPass:
    """Generate private reactions from persona/evidence intersections."""

    def __init__(self, cache: Optional[LocalArtifactCache] = None) -> None:
        self.cache = cache or LocalArtifactCache()

    def run(
        self,
        personas: Sequence[ReaderPersona],
        evidence_pack: EvidencePack,
        simulation_id: str,
        simulation_seed: Optional[int] = None,
    ) -> List[PrivateReaderReaction]:
        cache_key = self._cache_key(personas, evidence_pack, simulation_id, simulation_seed)
        cached = self.cache.get_json("simulation_private_reading", cache_key)
        if cached:
            return [PrivateReaderReaction.from_dict(item) for item in cached.get("reactions", [])]

        reactions = [
            self._build_reaction(persona, evidence_pack, simulation_id, simulation_seed)
            for persona in personas
        ]
        self.cache.set_json(
            "simulation_private_reading",
            cache_key,
            {"reactions": [reaction.to_dict() for reaction in reactions]},
        )
        return reactions

    def _build_reaction(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        simulation_id: str,
        simulation_seed: Optional[int],
    ) -> PrivateReaderReaction:
        rng = self._rng(persona.persona_id, simulation_id, simulation_seed, "private")
        evidence_refs = self._relevant_evidence(persona, evidence_pack)
        praise = self._praise(persona, evidence_pack)
        friction = self._friction(persona, evidence_pack)
        attachment = round(min(1.0, 0.4 + len(praise) * 0.12 + rng.uniform(-0.08, 0.08)), 3)
        confusion = round(min(1.0, 0.15 + len(friction) * 0.1 + rng.uniform(0.0, 0.12)), 3)
        rating = round(
            max(
                1.0,
                min(
                    5.0,
                    3.3 + persona.rating_bias + attachment * 1.1 - confusion * 0.7 + rng.uniform(-0.35, 0.35),
                ),
            ),
            2,
        )
        recommendation_probability = round(max(0.0, min(1.0, (rating / 5.0) * 0.7 + attachment * 0.2)), 3)
        dnf_probability = round(max(0.0, min(1.0, confusion * 0.6 + (1.0 - persona.dnf_threshold) * 0.4)), 3)
        sentiment = self._sentiment(rating, confusion)

        return PrivateReaderReaction(
            reaction_id=self._reaction_id(simulation_id, persona.persona_id),
            simulation_id=simulation_id,
            persona_id=persona.persona_id,
            rating=rating,
            dnf_probability=dnf_probability,
            sentiment=sentiment,
            attachment_score=attachment,
            confusion_score=confusion,
            recommendation_probability=recommendation_probability,
            praise=praise,
            friction=friction,
            notable_quotes=self._quotes(evidence_pack),
            evidence_refs=evidence_refs,
            confidence=evidence_pack.confidence,
        )

    def _relevant_evidence(self, persona: ReaderPersona, evidence_pack: EvidencePack) -> List[str]:
        refs: List[str] = list(evidence_pack.evidence_refs[:4])
        if evidence_pack.book_dna:
            refs.extend(evidence_pack.book_dna.evidence_refs[:2])
        if "nonfiction" in persona.book_type_suitability and evidence_pack.claim_map:
            for claim in evidence_pack.claim_map.claims[:2]:
                refs.extend(claim.evidence_refs[:2])
        elif evidence_pack.character_map:
            for character in evidence_pack.character_map.characters[:2]:
                refs.extend(character.evidence_refs[:1])
        if evidence_pack.risk_map:
            for risk in evidence_pack.risk_map.risks[:2]:
                refs.extend(risk.evidence_refs[:1])
        return list(dict.fromkeys(refs))

    def _praise(self, persona: ReaderPersona, evidence_pack: EvidencePack) -> List[str]:
        praise = list(persona.delight_triggers[:2])
        if evidence_pack.book_dna:
            praise.extend(evidence_pack.book_dna.themes[:2])
        if evidence_pack.market_surface:
            praise.extend(evidence_pack.market_surface.discoverability_hooks[:1])
        return list(dict.fromkeys(item for item in praise if item))[:3]

    def _friction(self, persona: ReaderPersona, evidence_pack: EvidencePack) -> List[str]:
        friction = list(persona.disliked_patterns[:2])
        if evidence_pack.risk_map:
            friction.extend(risk.risk_type for risk in evidence_pack.risk_map.risks[:2])
        return list(dict.fromkeys(item for item in friction if item))[:3]

    def _quotes(self, evidence_pack: EvidencePack) -> List[str]:
        if evidence_pack.book_dna and evidence_pack.book_dna.spoilers_safe_summary:
            return [evidence_pack.book_dna.spoilers_safe_summary[:160]]
        if evidence_pack.chapter_map and evidence_pack.chapter_map.chapters:
            return [chapter.summary[:160] for chapter in evidence_pack.chapter_map.chapters[:2] if chapter.summary]
        return []

    def _sentiment(self, rating: float, confusion: float) -> str:
        if rating >= 4.2 and confusion < 0.4:
            return "positive"
        if rating <= 2.4 or confusion >= 0.7:
            return "negative"
        return "mixed"

    def _cache_key(
        self,
        personas: Sequence[ReaderPersona],
        evidence_pack: EvidencePack,
        simulation_id: str,
        simulation_seed: Optional[int],
    ) -> str:
        payload = {
            "simulation_id": simulation_id,
            "simulation_seed": simulation_seed,
            "personas": [persona.to_dict() for persona in personas],
            "evidence_pack": evidence_pack.to_dict(),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def _rng(self, *parts: object) -> random.Random:
        return random.Random("|".join(str(part) for part in parts))

    def _reaction_id(self, simulation_id: str, persona_id: str) -> str:
        digest = hashlib.sha256(f"{simulation_id}:{persona_id}:private".encode("utf-8")).hexdigest()
        return f"private_{digest[:12]}"
