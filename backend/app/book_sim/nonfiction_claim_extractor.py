"""Nonfiction claim and evidence extraction heuristics."""

from __future__ import annotations

import re
from typing import List

from .manuscript_chunker import ManuscriptChunker
from .models import ChapterMap, ClaimMap, ClaimProfile


class NonfictionClaimExtractor:
    """Extract claims, evidence, frameworks, and factual-risk flags."""

    _CLAIM_MARKERS = ("should", "must", "will", "can", "argues", "shows", "means", "the key", "principle")
    _EVIDENCE_MARKERS = ("for example", "for instance", "study", "research", "data", "survey", "%")
    _FRAMEWORK_MARKERS = ("framework", "model", "system", "method", "step")
    _PROMISE_MARKERS = ("you will", "this book will", "by the end", "you can")
    _ABSOLUTES = ("always", "never", "everyone", "nobody", "all", "none")

    @staticmethod
    def _sentences(text: str) -> List[str]:
        return ManuscriptChunker._sentences(text)

    def build_claim_map(self, book_id: str, text: str, chapter_map: ChapterMap) -> ClaimMap:
        sentences = self._sentences(text)
        claims: List[ClaimProfile] = []

        for index, sentence in enumerate(sentences):
            lowered = sentence.lower()
            if not any(marker in lowered for marker in self._CLAIM_MARKERS):
                continue

            nearby = sentences[index:index + 3]
            evidence_items = [part[:160] for part in nearby if any(marker in part.lower() for marker in self._EVIDENCE_MARKERS)]
            examples = [part[:160] for part in nearby if "for example" in part.lower() or "for instance" in part.lower()]
            frameworks = [part[:120] for part in nearby if any(marker in part.lower() for marker in self._FRAMEWORK_MARKERS)]
            promises = [part[:120] for part in nearby if any(marker in part.lower() for marker in self._PROMISE_MARKERS)]

            risk_flags = []
            if any(token in lowered for token in self._ABSOLUTES) and not evidence_items:
                risk_flags.append("absolute_claim_without_visible_support")
            if any(char.isdigit() for char in sentence) is False and ("research" in lowered or "data" in lowered):
                risk_flags.append("cited_evidence_without_specifics")

            support_quality = "high" if len(evidence_items) >= 2 else "moderate" if evidence_items else "low"
            evidence_strength = 0.85 if support_quality == "high" else 0.62 if support_quality == "moderate" else 0.32

            claims.append(
                ClaimProfile(
                    claim_id=f"claim_{len(claims) + 1:03d}",
                    claim_text=sentence[:240],
                    support_type="framework" if frameworks else "argument",
                    support_quality=support_quality,
                    evidence_strength=evidence_strength,
                    evidence_items=evidence_items[:3],
                    examples=examples[:3],
                    frameworks=frameworks[:3],
                    promises=promises[:3],
                    factual_risk_flags=risk_flags,
                    counterarguments=[],
                    reader_trust_sensitivity=0.74 if risk_flags else 0.41,
                    evidence_refs=[chapter.chapter_id for chapter in chapter_map.chapters if sentence[:60] in chapter.summary or any(word in chapter.summary.lower() for word in sentence.lower().split()[:4])][:2],
                    confidence=0.66,
                )
            )

        strength_summary = "No strong nonfiction claims detected."
        if claims:
            low_support = sum(1 for claim in claims if claim.support_quality == "low")
            strength_summary = (
                f"Detected {len(claims)} claim units; {low_support} have low visible support."
            )

        thesis_summary = claims[0].claim_text if claims else None
        return ClaimMap(
            book_id=book_id,
            claims=claims,
            thesis_summary=thesis_summary,
            argument_strength_summary=strength_summary,
            evidence_refs=[claim.claim_id for claim in claims],
            confidence=0.67 if claims else 0.42,
        )
