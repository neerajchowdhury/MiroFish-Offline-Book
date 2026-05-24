"""Tests for book_sim.simulation.cross_reaction_pass.CrossReactionPass."""

import tempfile
import shutil

import pytest

from book_sim.models import (
    CrossReaction,
    EvidencePack,
    PlatformPost,
    PrivateReaderReaction,
    ReaderPersona,
)
from book_sim.local_cache import LocalArtifactCache
from book_sim.simulation.cross_reaction_pass import CrossReactionPass


def _make_persona(persona_id="persona_001", **kwargs):
    return ReaderPersona(
        persona_id=persona_id,
        archetype_id="critical_reader",
        display_name="Test Reader",
        platform_home="goodreads",
        review_style="analytical",
        **kwargs,
    )


def _make_private_reaction(persona_id="persona_001", simulation_id="sim_001", **kwargs):
    return PrivateReaderReaction(
        reaction_id=f"private_{persona_id}",
        simulation_id=simulation_id,
        persona_id=persona_id,
        rating=3.5,
        dnf_probability=0.2,
        sentiment="mixed",
        attachment_score=0.5,
        confusion_score=0.3,
        recommendation_probability=0.5,
        praise=["good pacing"],
        friction=["slow start"],
        notable_quotes=[],
        evidence_refs=["ref_1"],
        confidence=0.8,
        **kwargs,
    )


def _make_platform_post(post_id="post_001", persona_id="persona_001", **kwargs):
    defaults = {
        "simulation_id": "sim_001",
        "platform": "goodreads",
        "round_number": 1,
        "body": "Test post body",
        "rating": 3.5,
        "hashtags": ["#test"],
        "engagement_prediction": 0.6,
        "sentiment": "mixed",
        "evidence_refs": ["ref_1"],
        "confidence": 0.8,
    }
    defaults.update(kwargs)
    return PlatformPost(
        post_id=post_id,
        persona_id=persona_id,
        **defaults,
    )


class TestCrossReactionPassBasic:
    def test_run_returns_cross_reactions(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = CrossReactionPass(cache=cache, cross_reaction_posts=8, max_reaction_rounds=2)

        personas = [
            _make_persona("persona_001"),
            _make_persona("persona_002"),
        ]
        private_reactions = [
            _make_private_reaction("persona_001"),
            _make_private_reaction("persona_002"),
        ]
        platform_posts = [
            _make_platform_post("post_001", "persona_001", engagement_prediction=0.8),
            _make_platform_post("post_002", "persona_002", engagement_prediction=0.5),
            _make_platform_post("post_003", "persona_001", engagement_prediction=0.7),
            _make_platform_post("post_004", "persona_002", engagement_prediction=0.9),
        ]

        cross_reactions, updated_private = pass_obj.run(
            personas=personas,
            private_reactions=private_reactions,
            platform_posts=platform_posts,
            simulation_id="sim_001",
            simulation_seed=42,
            round_number=1,
        )

        assert isinstance(cross_reactions, list)
        assert len(cross_reactions) > 0
        assert isinstance(updated_private, list)
        assert len(updated_private) == len(private_reactions)

    def test_cross_reaction_has_required_fields(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = CrossReactionPass(cache=cache, cross_reaction_posts=8, max_reaction_rounds=2)

        personas = [_make_persona("persona_001"), _make_persona("persona_002")]
        private_reactions = [
            _make_private_reaction("persona_001"),
            _make_private_reaction("persona_002"),
        ]
        platform_posts = [
            _make_platform_post("post_001", "persona_001", engagement_prediction=0.8),
            _make_platform_post("post_002", "persona_002", engagement_prediction=0.5),
        ]

        cross_reactions, _ = pass_obj.run(
            personas=personas,
            private_reactions=private_reactions,
            platform_posts=platform_posts,
            simulation_id="sim_001",
            simulation_seed=42,
            round_number=1,
        )

        assert len(cross_reactions) > 0
        reaction = cross_reactions[0]
        assert isinstance(reaction, CrossReaction)
        assert reaction.reaction_id is not None
        assert reaction.simulation_id == "sim_001"
        assert reaction.source_post_id is not None
        assert reaction.target_post_id is not None
        assert reaction.persona_id is not None
        assert reaction.platform is not None
        assert isinstance(reaction.reacted_post_ids, list)
        assert reaction.stance_shift in ("more_positive", "more_negative", "stable")
        assert reaction.agree_probability is not None
        assert reaction.disagree_probability is not None
        assert reaction.reply_likelihood is not None
        assert reaction.rating_shift is not None
        assert reaction.recommendation_shift is not None
        assert reaction.sentiment is not None
        assert isinstance(reaction.evidence_refs, list)


class TestCrossReactionPassLimits:
    def test_round_limits_respected(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = CrossReactionPass(cache=cache, cross_reaction_posts=4, max_reaction_rounds=2)

        personas = [
            _make_persona("persona_001"),
            _make_persona("persona_002"),
            _make_persona("persona_003"),
        ]
        private_reactions = [
            _make_private_reaction("persona_001"),
            _make_private_reaction("persona_002"),
            _make_private_reaction("persona_003"),
        ]
        platform_posts = [
            _make_platform_post(f"post_{i:03d}", f"persona_{(i % 3) + 1:03d}", engagement_prediction=0.5 + i * 0.05)
            for i in range(10)
        ]

        cross_reactions, updated_private = pass_obj.run(
            personas=personas,
            private_reactions=private_reactions,
            platform_posts=platform_posts,
            simulation_id="sim_001",
            simulation_seed=42,
            round_number=1,
        )

        assert len(cross_reactions) <= len(personas)
        assert len(updated_private) == len(personas)

        top_posts = pass_obj._top_posts(platform_posts)
        assert len(top_posts) <= 4


class TestCrossReactionPassEdgeCases:
    def test_empty_posts_returns_no_reactions(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = CrossReactionPass(cache=cache, cross_reaction_posts=8, max_reaction_rounds=2)

        personas = [_make_persona("persona_001"), _make_persona("persona_002")]
        private_reactions = [
            _make_private_reaction("persona_001"),
            _make_private_reaction("persona_002"),
        ]

        cross_reactions, updated_private = pass_obj.run(
            personas=personas,
            private_reactions=private_reactions,
            platform_posts=[],
            simulation_id="sim_001",
            simulation_seed=42,
            round_number=1,
        )

        assert cross_reactions == []
        assert len(updated_private) == len(private_reactions)


class TestCrossReactionPassDeterminism:
    def test_deterministic_with_seed(self, tmp_cache_dir):
        cache_a = LocalArtifactCache(base_dir=tmp_cache_dir)
        cache_b = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj_a = CrossReactionPass(cache=cache_a, cross_reaction_posts=8, max_reaction_rounds=2)
        pass_obj_b = CrossReactionPass(cache=cache_b, cross_reaction_posts=8, max_reaction_rounds=2)

        personas = [_make_persona("persona_001"), _make_persona("persona_002")]
        private_reactions = [
            _make_private_reaction("persona_001"),
            _make_private_reaction("persona_002"),
        ]
        platform_posts = [
            _make_platform_post("post_001", "persona_001", engagement_prediction=0.8),
            _make_platform_post("post_002", "persona_002", engagement_prediction=0.5),
            _make_platform_post("post_003", "persona_001", engagement_prediction=0.7),
        ]

        cross_a, updated_a = pass_obj_a.run(
            personas=personas,
            private_reactions=private_reactions,
            platform_posts=platform_posts,
            simulation_id="sim_det",
            simulation_seed=99999,
            round_number=1,
        )
        cross_b, updated_b = pass_obj_b.run(
            personas=personas,
            private_reactions=private_reactions,
            platform_posts=platform_posts,
            simulation_id="sim_det",
            simulation_seed=99999,
            round_number=1,
        )

        assert len(cross_a) == len(cross_b)
        for ca, cb in zip(cross_a, cross_b):
            assert ca.rating_shift == cb.rating_shift
            assert ca.recommendation_shift == cb.recommendation_shift
            assert ca.stance_shift == cb.stance_shift
            assert ca.agree_probability == cb.agree_probability
            assert ca.disagree_probability == cb.disagree_probability

        assert len(updated_a) == len(updated_b)
        for ua, ub in zip(updated_a, updated_b):
            assert ua.rating == ub.rating
            assert ua.sentiment == ub.sentiment
