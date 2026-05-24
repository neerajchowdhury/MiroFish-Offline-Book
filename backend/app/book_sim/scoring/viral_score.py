"""Viral potential scoring by platform.

What this score measures
------------------------
How likely the book is to spread organically across different social and
reading platforms.  Each platform has its own scoring function that weights
viral drivers differently, reflecting the unique culture and mechanics of
that platform.

How it's calculated
-------------------
Six global component scores are computed first:

emotional_spike       -- Average reader attachment score, measuring how
                         strongly readers connect emotionally.
trope_visibility      -- Count of discoverability hooks and themes that
                         map to recognizable genre tropes.
novelty               -- Diversity of chapter functions and character count,
                         measuring how fresh the book feels.
controversy           -- Proxy from reader confusion and cross-reaction
                         rating shifts (see controversy_score for full logic).
quoteability          -- Proxy from style map quoteability rating, summary
                         presence, and quote card candidates in posts.
concise_explainability -- Whether the premise can be stated in under 30
                         words and whether claims are extractable.

These components form a base score, which is then adjusted per platform:

goodreads    -- Weighted toward sentiment and shelf signals (praise).
booktok      -- Weighted toward emotional spike, quoteability, and video
                signals (viral triggers, hook lines).
reddit       -- Weighted toward controversy and concise explainability;
                skepticism (confusion) is a factor.
bookstagram  -- Weighted toward quoteability and aesthetic appeal.
x            -- Weighted toward controversy and "hot take" signals.
newsletter   -- Weighted toward recommendation probability and market fit.
bookclub     -- Weighted toward controversy, open questions, and risks
                (discussion fuel).

Score range meaning
-------------------
platform_scores: 0.0 - 1.0 per platform
  0.0-0.2  -- Unlikely to gain traction on this platform.
  0.2-0.4  -- Low potential; may reach niche audiences.
  0.4-0.6  -- Moderate potential; could see steady organic spread.
  0.6-0.8  -- High potential; likely to trend in relevant communities.
  0.8-1.0  -- Very high potential; strong viral trajectory expected.

The top_platforms list ranks the three platforms with the highest scores,
guiding where marketing efforts should focus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..models import JsonDataclassMixin
from ._shared import ScoringContext, clamp, confidence_band_from_sample, evidence_refs, mean, scoring_weights


@dataclass
class ViralScoreResult(JsonDataclassMixin):
    """Platform-aware viral potential result."""

    platform_scores: Dict[str, float] = field(default_factory=dict)
    top_platforms: List[str] = field(default_factory=list)
    confidence_band: Dict[str, float | str] = field(default_factory=dict)
    component_scores: Dict[str, float] = field(default_factory=dict)
    evidence_refs: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def score_viral_potential(context: ScoringContext) -> ViralScoreResult:
    """Score how likely the book is to travel on each synthetic platform."""
    weights = scoring_weights()["viral_potential"]
    components = _component_scores(context)
    platform_scores = _platform_scores(context, components, weights)
    ordered = sorted(platform_scores.items(), key=lambda item: item[1], reverse=True)
    top_platforms = [platform for platform, _ in ordered[:3]]
    mid = mean(list(platform_scores.values())) if platform_scores else 0.0
    variability = max(platform_scores.values()) - min(platform_scores.values()) if platform_scores else 0.0
    band = confidence_band_from_sample(mid, max(1, len(context.platform_posts)), variability, "moderate")

    return ViralScoreResult(
        platform_scores={key: round(value, 3) for key, value in platform_scores.items()},
        top_platforms=top_platforms,
        confidence_band=band.to_dict(),
        component_scores=components,
        evidence_refs=evidence_refs(
            context.evidence_pack.evidence_refs,
            context.evidence_pack.book_dna.evidence_refs if context.evidence_pack.book_dna else [],
            (post.evidence_refs for post in context.platform_posts),
        ),
        notes=[
            "Platform scores are synthetic and should not be read as market certainty.",
        ],
    )


def _component_scores(context: ScoringContext) -> Dict[str, float]:
    platform_posts = list(context.platform_posts)
    private_reactions = list(context.private_reactions)
    evidence_pack = context.evidence_pack
    style_map = evidence_pack.style_map
    market_surface = evidence_pack.market_surface
    chapter_map = evidence_pack.chapter_map
    cross_reactions = list(context.cross_reactions)

    quoteability = _quoteability_proxy(style_map, evidence_pack, platform_posts)
    controversy = _controversy_proxy(private_reactions, cross_reactions)
    emotional_spike = clamp(mean([reaction.attachment_score or 0.0 for reaction in private_reactions]) + 0.15)
    trope_visibility = _trope_visibility(market_surface, evidence_pack)
    novelty = _novelty(chapter_map, evidence_pack)
    concise_explainability = _concise_explainability(evidence_pack)

    return {
        "emotional_spike": round(emotional_spike, 3),
        "trope_visibility": round(trope_visibility, 3),
        "novelty": round(novelty, 3),
        "controversy": round(controversy, 3),
        "quoteability": round(quoteability, 3),
        "concise_explainability": round(concise_explainability, 3),
    }


def _platform_scores(context: ScoringContext, components: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
    private_reactions = list(context.private_reactions)
    platform_posts = list(context.platform_posts)
    evidence_pack = context.evidence_pack
    base = clamp(
        (
            components["emotional_spike"] * 0.2
            + components["trope_visibility"] * 0.15
            + components["novelty"] * 0.15
            + components["controversy"] * 0.2
            + components["quoteability"] * 0.15
            + components["concise_explainability"] * 0.15
        )
    )

    platform_presence = {
        "goodreads": _goodreads_score(base, private_reactions, evidence_pack),
        "booktok": _booktok_score(base, components, platform_posts),
        "reddit": _reddit_score(base, components, private_reactions),
        "bookstagram": _bookstagram_score(base, components, evidence_pack),
        "x": _x_score(base, components, platform_posts),
        "newsletter": _newsletter_score(base, private_reactions, evidence_pack),
        "bookclub": _bookclub_score(base, components, evidence_pack),
    }
    return {platform: clamp(score) for platform, score in platform_presence.items()}


def _goodreads_score(base: float, private_reactions, evidence_pack) -> float:
    shelf_signal = 0.05 if any(reaction.praise for reaction in private_reactions) else 0.0
    sentiment = mean([1.0 if reaction.sentiment == "positive" else 0.55 if reaction.sentiment == "mixed" else 0.25 for reaction in private_reactions])
    return base * 0.55 + sentiment * 0.25 + shelf_signal + (0.05 if evidence_pack.market_surface else 0.0)


def _booktok_score(base: float, components: Dict[str, float], platform_posts) -> float:
    video_signals = mean([1.0 if (post.payload.get("viral_trigger") or post.payload.get("hook_line")) else 0.6 for post in platform_posts if post.platform == "booktok"] or [0.6])
    return base * 0.45 + components["emotional_spike"] * 0.2 + components["quoteability"] * 0.2 + video_signals * 0.15


def _reddit_score(base: float, components: Dict[str, float], private_reactions) -> float:
    skepticism = mean([reaction.confusion_score or 0.0 for reaction in private_reactions])
    return base * 0.35 + components["controversy"] * 0.35 + skepticism * 0.2 + components["concise_explainability"] * 0.1


def _bookstagram_score(base: float, components: Dict[str, float], evidence_pack) -> float:
    aesthetic = 0.4
    if evidence_pack.style_map and evidence_pack.style_map.quoteability == "high":
        aesthetic += 0.2
    if evidence_pack.market_surface and evidence_pack.market_surface.target_segments:
        aesthetic += 0.1
    return base * 0.4 + components["quoteability"] * 0.25 + aesthetic * 0.35


def _x_score(base: float, components: Dict[str, float], platform_posts) -> float:
    hot_take = mean([1.0 if post.payload.get("hot_take") else 0.5 for post in platform_posts if post.platform == "x"] or [0.5])
    return base * 0.3 + components["controversy"] * 0.4 + hot_take * 0.3


def _newsletter_score(base: float, private_reactions, evidence_pack) -> float:
    recommendation = mean([reaction.recommendation_probability or 0.0 for reaction in private_reactions]) if private_reactions else 0.45
    fit = 0.55 if evidence_pack.market_surface else 0.4
    return base * 0.35 + recommendation * 0.4 + fit * 0.25


def _bookclub_score(base: float, components: Dict[str, float], evidence_pack) -> float:
    discussion = 0.35
    if evidence_pack.chapter_map and any(chapter.open_questions for chapter in evidence_pack.chapter_map.chapters):
        discussion += 0.2
    if evidence_pack.risk_map and evidence_pack.risk_map.risks:
        discussion += 0.1
    return base * 0.4 + components["controversy"] * 0.2 + discussion * 0.4


def _quoteability_proxy(style_map, evidence_pack, platform_posts) -> float:
    score = 0.45
    if style_map and style_map.quoteability == "high":
        score += 0.25
    if evidence_pack.book_dna and evidence_pack.book_dna.spoilers_safe_summary:
        score += 0.1
    quote_cards = sum(1 for post in platform_posts if post.payload.get("quote_card_candidates"))
    score += min(0.12, quote_cards * 0.03)
    return clamp(score)


def _controversy_proxy(private_reactions, cross_reactions) -> float:
    signal = mean([reaction.confusion_score or 0.0 for reaction in private_reactions]) * 0.35
    signal += mean([abs(reaction.rating_shift or 0.0) for reaction in cross_reactions]) * 0.5 if cross_reactions else 0.0
    return clamp(0.25 + signal)


def _trope_visibility(market_surface, evidence_pack) -> float:
    score = 0.4
    if market_surface and market_surface.discoverability_hooks:
        score += min(0.2, len(market_surface.discoverability_hooks) * 0.04)
    if evidence_pack.book_dna and evidence_pack.book_dna.themes:
        score += min(0.15, len(evidence_pack.book_dna.themes) * 0.03)
    return clamp(score)


def _novelty(chapter_map, evidence_pack) -> float:
    score = 0.35
    if chapter_map and chapter_map.chapters:
        score += min(0.2, len({chapter.chapter_function for chapter in chapter_map.chapters if chapter.chapter_function}) * 0.05)
    if evidence_pack.character_map and evidence_pack.character_map.characters:
        score += min(0.15, len(evidence_pack.character_map.characters) * 0.01)
    return clamp(score)


def _concise_explainability(evidence_pack) -> float:
    score = 0.4
    if evidence_pack.book_dna and len(evidence_pack.book_dna.premise.split()) < 30:
        score += 0.15
    if evidence_pack.claim_map and evidence_pack.claim_map.claims:
        score += 0.08
    return clamp(score)
