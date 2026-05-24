"""Swarmbook scoring package -- deterministic analysis of simulated reader reactions.

This package exposes seven independent scoring modules, each measuring a
different dimension of how a manuscript is likely to perform in the market.
All scorers share a common pattern:

1. Accept a ``ScoringContext`` (evidence pack + simulation run).
2. Load configurable weights from ``scoring_weights.yaml``.
3. Compute component sub-scores from manuscript artifacts and reader reactions.
4. Combine components via weighted sum or weighted average.
5. Return a result dataclass with the primary score, components, confidence
   band, evidence references, and human-readable notes.

Score range convention
----------------------
Most scores are normalized to [0.0, 1.0] via ``clamp()``.  Higher values
indicate stronger presence of the measured trait (more controversy, more
viral potential, more DNF risk, etc.).  The rating distribution scorer is
the exception: its ``predicted_mean_rating`` is on a 1-5 star scale.

Public API
----------
score_rating_distribution  -- Predicted star-rating mean and distribution.
score_dnf                  -- Risk that readers abandon the book (Did Not Finish).
score_controversy          -- Ideological/moral backlash risk radar.
score_quoteability         -- How easily the book yields reusable quotes.
score_polarization         -- Likelihood of sharply divided reader reviews.
score_viral_potential      -- Per-platform spread likelihood.
score_revision_priority    -- Ranked list of highest-value revision targets.
"""

from ._shared import ConfidenceBand, ScoringContext, load_scoring_weights, scoring_weights
from .controversy_score import ControversyScoreResult, score_controversy
from .dnf_score import DNFScoreResult, score_dnf
from .polarization_score import PolarizationScoreResult, score_polarization
from .quoteability_score import QuoteabilityScoreResult, score_quoteability
from .rating_distribution import RatingDistributionResult, score_rating_distribution
from .revision_priority import RevisionPriorityItem, RevisionPriorityResult, score_revision_priority
from .viral_score import ViralScoreResult, score_viral_potential

__all__ = [
    "ConfidenceBand",
    "ScoringContext",
    "load_scoring_weights",
    "scoring_weights",
    "RatingDistributionResult",
    "DNFScoreResult",
    "ViralScoreResult",
    "ControversyScoreResult",
    "QuoteabilityScoreResult",
    "PolarizationScoreResult",
    "RevisionPriorityItem",
    "RevisionPriorityResult",
    "score_rating_distribution",
    "score_dnf",
    "score_viral_potential",
    "score_controversy",
    "score_quoteability",
    "score_polarization",
    "score_revision_priority",
]
