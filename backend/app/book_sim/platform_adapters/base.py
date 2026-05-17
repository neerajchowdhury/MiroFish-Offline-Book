"""Shared base utilities for synthetic Swarmbook platform adapters."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from ..config_loader import REPO_ROOT, _load_yaml_dict
from ..models import EvidencePack, PlatformPost, PrivateReaderReaction, ReaderPersona


DEFAULT_PLATFORM_STYLES_PATH = REPO_ROOT / "configs" / "book_sim" / "platform_styles.yaml"


def _parse_scalar(raw_value: str):
    value = raw_value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip() for item in inner.split(",") if item.strip()]
    return value


def _load_platform_styles_raw(path: Path) -> Dict[str, Any]:
    try:
        return _load_yaml_dict(path)
    except RuntimeError:
        styles: Dict[str, Dict[str, Any]] = {}
        current_platform: Optional[str] = None
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                if line.strip() == "platform_styles:":
                    continue
                if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(":"):
                    current_platform = line.strip()[:-1]
                    styles[current_platform] = {}
                    continue
                if current_platform and line.startswith("    ") and ":" in line:
                    key, raw_value = line.strip().split(":", 1)
                    styles[current_platform][key] = _parse_scalar(raw_value)
        return {"platform_styles": styles}


def _load_platform_styles(path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    payload = _load_platform_styles_raw(path or DEFAULT_PLATFORM_STYLES_PATH)
    styles = payload.get("platform_styles", {})
    if not isinstance(styles, dict):
        raise ValueError("platform_styles.yaml must contain top-level 'platform_styles' mapping")
    return styles


@dataclass(frozen=True)
class AdapterContext:
    """Minimal context shared across platform adapters."""

    simulation_id: str
    round_number: int
    privacy_mode: str
    simulation_seed: Optional[int] = None


class BasePlatformAdapter:
    """Generate structured, synthetic platform-native posts."""

    platform_name = "base"

    def __init__(
        self,
        styles: Optional[Mapping[str, Dict[str, Any]]] = None,
        model_router: Any = None,
    ) -> None:
        self.styles = dict(styles or _load_platform_styles())
        self.model_router = model_router
        self.style = self.styles.get(self.platform_name, {})

    def create_post(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> PlatformPost:
        payload = self.build_payload(persona, evidence_pack, private_reaction, context)
        return PlatformPost(
            post_id=self._stable_id(
                context.simulation_id,
                persona.persona_id,
                context.round_number,
                self.platform_name,
            ),
            simulation_id=context.simulation_id,
            persona_id=persona.persona_id,
            platform=self.platform_name,
            round_number=context.round_number,
            title=self._payload_title(payload),
            body=self._payload_body(payload),
            rating=private_reaction.rating,
            hashtags=list(payload.get("trope_tags", []) or payload.get("aesthetic_tags", []) or payload.get("hashtags", [])),
            shelf_tags=list(payload.get("shelf_tags", [])),
            payload=payload,
            engagement_prediction=self._engagement_prediction(persona, private_reaction),
            sentiment=private_reaction.sentiment,
            evidence_refs=self._evidence_refs(evidence_pack, private_reaction),
            confidence=private_reaction.confidence,
        )

    def build_payload(
        self,
        persona: ReaderPersona,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
        context: AdapterContext,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def _engagement_prediction(
        self,
        persona: ReaderPersona,
        private_reaction: PrivateReaderReaction,
    ) -> float:
        base = persona.influence_weight * 0.5 + persona.quote_sharing_probability * 0.2
        heat = (private_reaction.rating or 3.0) / 5.0
        return round(min(1.0, base + heat * 0.3), 3)

    def _payload_title(self, payload: Dict[str, Any]) -> Optional[str]:
        for key in ("review_title", "thread_title", "hook_line", "hot_take", "recommendation_blurb"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value[:120]
        return None

    def _payload_body(self, payload: Dict[str, Any]) -> str:
        body_parts: List[str] = []
        for key in (
            "review_body",
            "video_script",
            "top_comment",
            "caption",
            "quote_tweet",
            "recommendation_blurb",
            "discussion_questions",
        ):
            value = payload.get(key)
            if isinstance(value, str) and value:
                body_parts.append(value)
            elif isinstance(value, list) and value:
                body_parts.extend(str(item) for item in value[:3])
        return " | ".join(body_parts)[:500]

    def _stable_id(self, *parts: object) -> str:
        digest = hashlib.sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()
        return f"{self.platform_name}_{digest[:12]}"

    def _rng(self, persona: ReaderPersona, context: AdapterContext) -> random.Random:
        seed_parts = [
            context.simulation_seed or 0,
            persona.persona_id,
            context.simulation_id,
            context.round_number,
            self.platform_name,
        ]
        seed = "|".join(str(part) for part in seed_parts)
        return random.Random(seed)

    def _book_signals(self, evidence_pack: EvidencePack) -> Dict[str, Any]:
        book_dna = evidence_pack.book_dna
        style_map = evidence_pack.style_map
        market_surface = evidence_pack.market_surface
        risk_map = evidence_pack.risk_map
        chapter_map = evidence_pack.chapter_map
        return {
            "title": book_dna.title if book_dna else evidence_pack.project_id,
            "genre": book_dna.genre if book_dna else "book",
            "premise": book_dna.premise if book_dna else "",
            "themes": list(book_dna.themes if book_dna else []),
            "tone": book_dna.tone if book_dna else "",
            "style_notes": list(style_map.style_notes if style_map else []),
            "hooks": list(market_surface.discoverability_hooks if market_surface else []),
            "target_segments": list(market_surface.target_segments if market_surface else []),
            "risks": [risk.risk_type for risk in (risk_map.risks if risk_map else [])][:3],
            "chapter_titles": [chapter.title or f"Chapter {chapter.chapter_number}" for chapter in (chapter_map.chapters if chapter_map else [])][:3],
        }

    def _evidence_refs(
        self,
        evidence_pack: EvidencePack,
        private_reaction: PrivateReaderReaction,
    ) -> List[str]:
        refs = list(evidence_pack.evidence_refs)
        refs.extend(private_reaction.evidence_refs)
        refs.append(f"platform_style:{self.platform_name}")
        return list(dict.fromkeys(refs))
