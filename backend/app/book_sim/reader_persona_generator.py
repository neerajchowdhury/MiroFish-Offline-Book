"""Generate deterministic reader personas from archetype templates."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence

from .models import ReaderArchetype, ReaderPersona
from .provider_router import BookSimProviderRouter
from .reader_archetype_loader import ReaderArchetypeCatalog, ReaderArchetypeLoader


_NAME_POOLS: Dict[str, List[str]] = {
    "community_reviewers": ["Avery", "Morgan", "Parker", "Quinn", "Jordan", "Riley"],
    "viral_emotion_seekers": ["Skye", "Nova", "Harper", "Lena", "Milo", "Sage"],
    "skeptical_forum_readers": ["Casey", "Drew", "Elliot", "Robin", "Shawn", "Taylor"],
    "aesthetic_curators": ["Ivy", "Celeste", "Maren", "June", "Thea", "Esme"],
    "hot_take_amplifiers": ["Blair", "Jules", "Remy", "Kai", "Micah", "Tatum"],
    "casual_volume_readers": ["Noah", "Emma", "Lucas", "Maya", "Owen", "Nina"],
    "craft_conscious_readers": ["Ada", "Simon", "Clara", "Jonah", "Leah", "Hugo"],
    "discussion_driven_readers": ["Priya", "Daniel", "Rosa", "Ben", "Elena", "Marcus"],
}

_LAST_INITIALS = list("BCDFGHJKLMNPRSTW")

_PRIVACY_MODE_DEFAULT_COUNTS = {
    "local_only": 16,
    "hybrid_safe": 30,
    "cloud_quality": 36,
}

_BOOK_TYPE_BONUS_GENRES = {
    "fiction": ["character-driven fiction", "storytelling", "narrative immersion"],
    "nonfiction": ["clear frameworks", "practical insight", "credible sourcing"],
}


@dataclass(frozen=True)
class PersonaGenerationOverrides:
    """Optional persona generation overrides."""

    persona_count: Optional[int] = None
    archetype_weight_overrides: Dict[str, float] = field(default_factory=dict)
    allowed_platforms: List[str] = field(default_factory=list)
    include_archetypes: List[str] = field(default_factory=list)
    exclude_archetypes: List[str] = field(default_factory=list)


class ReaderPersonaGenerator:
    """Generate reader personas from loaded archetype templates."""

    def __init__(
        self,
        catalog: Optional[ReaderArchetypeCatalog] = None,
        model_router: Optional[BookSimProviderRouter] = None,
    ) -> None:
        self.catalog = catalog or ReaderArchetypeLoader.from_yaml()
        self.model_router = model_router

    def generate(
        self,
        book_type: str,
        privacy_mode: str = "hybrid_safe",
        simulation_seed: Optional[int] = None,
        overrides: Optional[PersonaGenerationOverrides] = None,
        enrich_with_llm: bool = False,
        enrichment_route: str = "local_ollama",
    ) -> List[ReaderPersona]:
        rng = random.Random(simulation_seed)
        effective_overrides = overrides or PersonaGenerationOverrides()
        archetypes = self._select_archetypes(book_type, effective_overrides)
        persona_count = self._resolve_persona_count(privacy_mode, effective_overrides)
        weighted_archetypes = self._weighted_pool(archetypes, effective_overrides)

        personas: List[ReaderPersona] = []
        for index in range(persona_count):
            archetype = rng.choices(
                population=weighted_archetypes["items"],
                weights=weighted_archetypes["weights"],
                k=1,
            )[0]
            personas.append(
                self._build_persona(
                    archetype=archetype,
                    index=index,
                    rng=rng,
                    book_type=book_type,
                    privacy_mode=privacy_mode,
                )
            )

        if enrich_with_llm and self.model_router and simulation_seed is None:
            personas = [self._enrich_persona(persona, privacy_mode, enrichment_route) for persona in personas]

        return personas

    def _select_archetypes(
        self,
        book_type: str,
        overrides: PersonaGenerationOverrides,
    ) -> List[ReaderArchetype]:
        archetypes = self.catalog.for_book_type(book_type)
        if overrides.allowed_platforms:
            allowed = {platform.lower() for platform in overrides.allowed_platforms}
            archetypes = [item for item in archetypes if item.platform_home in allowed]
        if overrides.include_archetypes:
            included = set(overrides.include_archetypes)
            archetypes = [item for item in archetypes if item.archetype_id in included]
        if overrides.exclude_archetypes:
            excluded = set(overrides.exclude_archetypes)
            archetypes = [item for item in archetypes if item.archetype_id not in excluded]
        if not archetypes:
            raise ValueError("No reader archetypes matched the requested book type and overrides")
        return archetypes

    def _resolve_persona_count(self, privacy_mode: str, overrides: PersonaGenerationOverrides) -> int:
        if overrides.persona_count is not None:
            return int(overrides.persona_count)
        return _PRIVACY_MODE_DEFAULT_COUNTS.get(privacy_mode, 30)

    def _weighted_pool(
        self,
        archetypes: Sequence[ReaderArchetype],
        overrides: PersonaGenerationOverrides,
    ) -> Dict[str, List[object]]:
        items: List[ReaderArchetype] = []
        weights: List[float] = []
        for archetype in archetypes:
            override_weight = overrides.archetype_weight_overrides.get(archetype.archetype_id)
            items.append(archetype)
            weights.append(max(0.01, override_weight if override_weight is not None else archetype.selection_weight))
        return {"items": items, "weights": weights}

    def _build_persona(
        self,
        archetype: ReaderArchetype,
        index: int,
        rng: random.Random,
        book_type: str,
        privacy_mode: str,
    ) -> ReaderPersona:
        base_name = rng.choice(_NAME_POOLS.get(archetype.cohort or archetype.platform_home, ["Avery"]))
        full_name = f"{base_name} {rng.choice(_LAST_INITIALS)}."
        persona_id = f"{archetype.archetype_id}_{index + 1:02d}_{rng.randint(1000, 9999)}"
        favorite_genres = self._favorite_genres(archetype, book_type, rng)
        disliked_patterns = self._dedupe(archetype.disliked_patterns or archetype.dnf_triggers)
        delight_triggers = self._dedupe(archetype.delight_triggers)

        return ReaderPersona(
            persona_id=persona_id,
            archetype_id=archetype.archetype_id,
            display_name=full_name,
            platform_home=archetype.platform_home,
            review_style=archetype.review_style,
            id=persona_id,
            name=full_name,
            cohort=archetype.cohort,
            platform=archetype.platform_home,
            favorite_genres=favorite_genres,
            disliked_patterns=disliked_patterns,
            dnf_threshold=self._vary(rng, archetype.dnf_threshold, 0.08),
            controversy_sensitivity=self._vary(rng, archetype.controversy_sensitivity, 0.1),
            rating_bias=self._vary(rng, archetype.rating_bias, 0.12, min_value=-1.0, max_value=1.0),
            influence_weight=self._vary(rng, archetype.influence_weight, 0.1),
            susceptibility_to_peer_reaction=self._vary(rng, archetype.susceptibility_to_peer_reaction, 0.08),
            quote_sharing_probability=self._vary(rng, archetype.quote_sharing_probability, 0.1),
            evidence_focus=self._vary(rng, archetype.evidence_focus, 0.08),
            privacy_constraints=self._privacy_constraints(archetype, privacy_mode),
            book_type_suitability=list(archetype.book_type_suitability),
            reading_preferences=favorite_genres,
            dnf_triggers=disliked_patterns,
            delight_triggers=delight_triggers,
            private_bias=archetype.genre_bias,
            influence_score=archetype.influence_weight,
            spoiler_tolerance=archetype.spoiler_tolerance,
            evidence_refs=[
                f"reader_archetype:{archetype.archetype_id}",
                f"privacy_mode:{privacy_mode}",
                f"book_type:{book_type}",
            ],
            confidence=archetype.confidence,
        )

    def _favorite_genres(self, archetype: ReaderArchetype, book_type: str, rng: random.Random) -> List[str]:
        base = list(archetype.favorite_genres)
        base.extend(_BOOK_TYPE_BONUS_GENRES.get(self._normalize_book_type(book_type), []))
        if len(base) > 4:
            rng.shuffle(base)
            base = base[:4]
        return self._dedupe(base)

    def _privacy_constraints(self, archetype: ReaderArchetype, privacy_mode: str) -> List[str]:
        constraints = list(archetype.privacy_constraints)
        if privacy_mode == "local_only":
            constraints.append("local_processing_only")
            constraints.append("no_external_enrichment")
        elif privacy_mode == "hybrid_safe":
            constraints.append("redaction_before_cloud_optional")
        else:
            constraints.append("cloud_allowed_via_router")
        return self._dedupe(constraints)

    def _enrich_persona(
        self,
        persona: ReaderPersona,
        privacy_mode: str,
        enrichment_route: str,
    ) -> ReaderPersona:
        route_name = "local_ollama" if privacy_mode == "local_only" else enrichment_route
        prompt = (
            "Return JSON with optional keys private_bias, reading_preferences, "
            "delight_triggers, disliked_patterns. Keep changes minimal and consistent "
            "with this persona: "
            f"{persona.to_json(indent=0)}"
        )
        payload = self.model_router.generate_json(
            prompt=prompt,
            route_name=route_name,
            privacy_mode=privacy_mode,
            system_prompt="You enrich synthetic book-reader personas. Return compact JSON only.",
            temperature=0.0,
            max_tokens=400,
        )
        data = persona.to_dict()
        for key in ("private_bias", "reading_preferences", "delight_triggers", "disliked_patterns"):
            if key in payload and payload[key]:
                data[key] = payload[key]
        return ReaderPersona.from_dict(data)

    def _vary(
        self,
        rng: random.Random,
        base: float,
        delta: float,
        min_value: float = 0.0,
        max_value: float = 1.0,
    ) -> float:
        value = base + rng.uniform(-delta, delta)
        return round(max(min_value, min(max_value, value)), 3)

    def _normalize_book_type(self, book_type: str) -> str:
        lowered = (book_type or "").strip().lower()
        if "nonfiction" in lowered:
            return "nonfiction"
        if "fiction" in lowered:
            return "fiction"
        return "mixed_unknown"

    def _dedupe(self, values: Sequence[str]) -> List[str]:
        seen = set()
        result: List[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result
