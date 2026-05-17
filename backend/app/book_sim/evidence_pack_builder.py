"""End-to-end manuscript ingestion and evidence-pack generation for Swarmbook."""

from __future__ import annotations

import hashlib
from typing import Optional

from .book_dna_extractor import BookDNAExtractor
from .character_mapper import CharacterMapper
from .local_cache import LocalArtifactCache
from .manuscript_chunker import ManuscriptChunker
from .models import (
    BookProject,
    CharacterMap,
    ClaimMap,
    EvidencePack,
    ManuscriptInput,
    MarketSurface,
)
from .nonfiction_claim_extractor import NonfictionClaimExtractor
from .risk_detector import RiskDetector
from .style_analyzer import StyleAnalyzer


class EvidencePackBuilder:
    """Build cached evidence packs from full manuscripts."""

    def __init__(self, model_router=None, cache: Optional[LocalArtifactCache] = None) -> None:
        self.model_router = model_router
        self.cache = cache or LocalArtifactCache()
        self.chunker = ManuscriptChunker(model_router=model_router)
        self.book_dna_extractor = BookDNAExtractor(model_router=model_router)
        self.character_mapper = CharacterMapper()
        self.claim_extractor = NonfictionClaimExtractor()
        self.style_analyzer = StyleAnalyzer()
        self.risk_detector = RiskDetector()

    @staticmethod
    def _content_hash(manuscript: ManuscriptInput) -> str:
        raw = "|".join(
            [
                manuscript.project_id,
                manuscript.title,
                manuscript.draft_id or "",
                manuscript.version or "",
                manuscript.privacy_mode,
                manuscript.text,
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _build_market_surface(self, book_id: str, book_type: str, book_dna, style_map) -> MarketSurface:
        if book_type == "nonfiction":
            target_segments = ["non-fiction pragmatist", "non-fiction evidence skeptic"]
            packaging = ["clear promise", "framework-driven", "credible examples"]
        elif book_type == "fiction":
            target_segments = ["Goodreads genre loyalist", "casual Kindle reader", "literary reader"]
            packaging = ["clear genre signal", "emotion-rich blurb", "strong cover mood"]
        else:
            target_segments = ["curious early readers", "hybrid-genre readers"]
            packaging = ["set reader expectations carefully", "signal mixed structure"]

        discoverability_hooks = [book_dna.genre, *(book_dna.themes[:2] if book_dna.themes else [])]
        promise_gap = None
        if style_map.accessibility == "low" and "casual Kindle reader" in target_segments:
            promise_gap = "The prose may be denser than a casual-market package implies."

        return MarketSurface(
            book_id=book_id,
            target_segments=target_segments,
            comp_titles=book_dna.comparable_titles,
            positioning_summary=f"{book_dna.genre} with a {book_dna.book_type} reading experience.",
            discoverability_hooks=[hook for hook in discoverability_hooks if hook],
            packaging_expectations=packaging,
            promise_gap=promise_gap,
            audience_fit="medium_high" if style_map.clarity != "low" else "medium",
            evidence_refs=book_dna.evidence_refs + style_map.evidence_refs,
            confidence=0.66,
        )

    def build_from_manuscript(self, project: BookProject, manuscript: ManuscriptInput) -> EvidencePack:
        cache_key = self._content_hash(manuscript)
        cached = self.cache.get_json("evidence_pack", cache_key)
        if cached:
            return EvidencePack.from_dict(cached)

        cleaned_text = self.chunker.preprocess(manuscript.text)
        normalized_manuscript = ManuscriptInput.from_dict(
            {
                **manuscript.to_dict(),
                "text": cleaned_text,
            }
        )

        book_type = self.chunker.detect_book_type(cleaned_text)
        chapter_map = self.chunker.build_chapter_map(
            book_id=project.project_id,
            text=cleaned_text,
            privacy_mode=project.privacy_mode,
            book_type=book_type,
            chunk_size=manuscript.chunk_size * 8,
            overlap=max(100, manuscript.chunk_overlap * 4),
        )
        book_dna = self.book_dna_extractor.extract(
            manuscript=normalized_manuscript,
            book_type=book_type,
            chapter_map=chapter_map,
            privacy_mode=project.privacy_mode,
        )
        style_map = self.style_analyzer.analyze(book_id=project.project_id, text=cleaned_text)

        character_map = CharacterMap(book_id=project.project_id, confidence=0.35)
        claim_map = ClaimMap(book_id=project.project_id, confidence=0.35)
        if book_type == "fiction":
            character_map = self.character_mapper.build_character_map(project.project_id, cleaned_text, chapter_map)
        elif book_type == "nonfiction":
            claim_map = self.claim_extractor.build_claim_map(project.project_id, cleaned_text, chapter_map)
        else:
            character_map = self.character_mapper.build_character_map(project.project_id, cleaned_text, chapter_map)
            claim_map = self.claim_extractor.build_claim_map(project.project_id, cleaned_text, chapter_map)

        market_surface = self._build_market_surface(
            book_id=project.project_id,
            book_type=book_type,
            book_dna=book_dna,
            style_map=style_map,
        )
        risk_map = self.risk_detector.build_risk_map(
            book_id=project.project_id,
            book_type=book_type,
            chapter_map=chapter_map,
            style_map=style_map,
            market_surface=market_surface,
            character_map=character_map,
            claim_map=claim_map,
        )

        evidence_pack = EvidencePack(
            pack_id=f"pack_{cache_key[:12]}",
            project_id=project.project_id,
            draft_id=project.draft_id,
            version=project.version,
            privacy_mode=project.privacy_mode,
            manuscript_input=normalized_manuscript,
            book_dna=book_dna,
            chapter_map=chapter_map,
            character_map=character_map,
            claim_map=claim_map,
            risk_map=risk_map,
            style_map=style_map,
            market_surface=market_surface,
            evidence_refs=[cache_key] + book_dna.evidence_refs,
            confidence=0.74,
        )
        self.cache.set_json("evidence_pack", cache_key, evidence_pack.to_dict())
        return evidence_pack
