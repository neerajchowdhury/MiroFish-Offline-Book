"""Risk detection for Swarmbook evidence packs."""

from __future__ import annotations

from typing import List

from .models import CharacterMap, ClaimMap, MarketSurface, RiskMap, RiskProfile, StyleMap, ChapterMap


class RiskDetector:
    """Derive pacing, evidence, and positioning risks from structured artifacts."""

    def build_risk_map(
        self,
        book_id: str,
        book_type: str,
        chapter_map: ChapterMap,
        style_map: StyleMap,
        market_surface: MarketSurface,
        character_map: CharacterMap,
        claim_map: ClaimMap,
    ) -> RiskMap:
        risks: List[RiskProfile] = []

        for chapter in chapter_map.chapters:
            if chapter.pacing == "slow" or chapter.likely_reader_friction:
                risks.append(
                    RiskProfile(
                        risk_id=f"risk_{len(risks) + 1:03d}",
                        risk_type="pacing_drag",
                        severity="medium" if chapter.pacing == "slow" else "low",
                        description=f"{chapter.title or chapter.chapter_id} may create drag or confusion.",
                        affected_segments=[chapter.chapter_id],
                        trigger_text=", ".join(chapter.likely_reader_friction) or "slow pacing note",
                        mitigation_hint="Tighten exposition or add clearer forward motion.",
                        evidence_refs=chapter.evidence_refs,
                        confidence=0.68,
                    )
                )

        if style_map.accessibility == "low":
            risks.append(
                RiskProfile(
                    risk_id=f"risk_{len(risks) + 1:03d}",
                    risk_type="style_accessibility",
                    severity="medium",
                    description="Dense or low-clarity prose may narrow the reachable audience.",
                    affected_segments=list(market_surface.target_segments),
                    trigger_text="style analysis indicates low accessibility",
                    mitigation_hint="Simplify sentence structure or vary paragraph length.",
                    evidence_refs=style_map.evidence_refs,
                    confidence=0.71,
                )
            )

        if claim_map.claims:
            for claim in claim_map.claims:
                if claim.factual_risk_flags:
                    risks.append(
                        RiskProfile(
                            risk_id=f"risk_{len(risks) + 1:03d}",
                            risk_type="factual_risk",
                            severity="high" if claim.support_quality == "low" else "medium",
                            description=f"Claim '{claim.claim_text[:90]}' may invite skepticism.",
                            affected_segments=["nonfiction_evidence_skeptic", "reddit_skeptic"],
                            trigger_text=", ".join(claim.factual_risk_flags),
                            mitigation_hint="Add stronger sourcing, examples, or caveats.",
                            evidence_refs=claim.evidence_refs,
                            confidence=0.77,
                        )
                    )

        if book_type == "fiction" and not character_map.characters:
            risks.append(
                RiskProfile(
                    risk_id=f"risk_{len(risks) + 1:03d}",
                    risk_type="character_clarity",
                    severity="medium",
                    description="Very few recurring characters were detected, which may signal a thin cast or weak naming clarity.",
                    affected_segments=["fiction_readers"],
                    trigger_text="character extraction returned sparse results",
                    mitigation_hint="Clarify major character identity and motivations earlier.",
                    evidence_refs=["character_map"],
                    confidence=0.55,
                )
            )

        if market_surface.promise_gap:
            risks.append(
                RiskProfile(
                    risk_id=f"risk_{len(risks) + 1:03d}",
                    risk_type="positioning_gap",
                    severity="medium",
                    description="Packaging promise may not match the on-page experience.",
                    affected_segments=market_surface.target_segments,
                    trigger_text=market_surface.promise_gap,
                    mitigation_hint="Align blurb, comps, and cover promise with the real reading experience.",
                    evidence_refs=market_surface.evidence_refs,
                    confidence=0.63,
                )
            )

        summary = f"Detected {len(risks)} evidence-based risk signals." if risks else "No major heuristic risks detected."
        return RiskMap(
            book_id=book_id,
            risks=risks,
            risk_summary=summary,
            evidence_refs=[risk.risk_id for risk in risks],
            confidence=0.7 if risks else 0.45,
        )
