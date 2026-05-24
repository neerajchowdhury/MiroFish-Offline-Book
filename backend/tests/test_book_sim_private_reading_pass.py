"""Tests for book_sim.simulation.private_reading_pass.PrivateReadingPass."""

import json
import tempfile
import shutil

import pytest

from book_sim.models import EvidencePack, BookDNA, ChapterMap, ChapterSummary, ReaderPersona, PrivateReaderReaction
from book_sim.local_cache import LocalArtifactCache
from book_sim.simulation.private_reading_pass import PrivateReadingPass


def _make_persona(persona_id="persona_001", **kwargs):
    return ReaderPersona(
        persona_id=persona_id,
        archetype_id="critical_reader",
        display_name="Test Reader",
        platform_home="goodreads",
        review_style="analytical",
        **kwargs,
    )


def _make_evidence_pack(pack_id="pack_001", **kwargs):
    return EvidencePack(
        pack_id=pack_id,
        project_id="proj_001",
        **kwargs,
    )


class TestPrivateReadingPassBasic:
    def test_run_returns_reactions_for_each_persona(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = PrivateReadingPass(cache=cache)
        personas = [
            _make_persona("persona_001", rating_bias=0.5),
            _make_persona("persona_002", rating_bias=-0.3),
            _make_persona("persona_003", rating_bias=0.0),
        ]
        evidence_pack = _make_evidence_pack()

        reactions = pass_obj.run(
            personas=personas,
            evidence_pack=evidence_pack,
            simulation_id="sim_001",
            simulation_seed=42,
        )

        assert len(reactions) == 3
        reaction_ids = {r.reaction_id for r in reactions}
        assert len(reaction_ids) == 3

    def test_reaction_has_required_fields(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = PrivateReadingPass(cache=cache)
        persona = _make_persona("persona_001", rating_bias=0.2)
        evidence_pack = _make_evidence_pack()

        reactions = pass_obj.run(
            personas=[persona],
            evidence_pack=evidence_pack,
            simulation_id="sim_001",
            simulation_seed=42,
        )

        reaction = reactions[0]
        assert isinstance(reaction, PrivateReaderReaction)
        assert reaction.reaction_id is not None
        assert reaction.simulation_id == "sim_001"
        assert reaction.persona_id == "persona_001"
        assert reaction.rating is not None
        assert 1.0 <= reaction.rating <= 5.0
        assert reaction.dnf_probability is not None
        assert 0.0 <= reaction.dnf_probability <= 1.0
        assert reaction.sentiment in ("positive", "negative", "mixed")
        assert reaction.attachment_score is not None
        assert reaction.confusion_score is not None
        assert reaction.recommendation_probability is not None
        assert isinstance(reaction.praise, list)
        assert isinstance(reaction.friction, list)
        assert isinstance(reaction.notable_quotes, list)
        assert isinstance(reaction.evidence_refs, list)


class TestPrivateReadingPassCaching:
    def test_caching_prevents_duplicate_calls(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = PrivateReadingPass(cache=cache)
        persona = _make_persona("persona_001", rating_bias=0.1)
        evidence_pack = _make_evidence_pack()

        reactions_1 = pass_obj.run(
            personas=[persona],
            evidence_pack=evidence_pack,
            simulation_id="sim_001",
            simulation_seed=42,
        )

        cached = cache.get_json("simulation_private_reading", pass_obj._cache_key(
            [persona], evidence_pack, "sim_001", 42,
        ))
        assert cached is not None
        assert "reactions" in cached

        reactions_2 = pass_obj.run(
            personas=[persona],
            evidence_pack=evidence_pack,
            simulation_id="sim_001",
            simulation_seed=42,
        )

        assert len(reactions_1) == len(reactions_2)
        for r1, r2 in zip(reactions_1, reactions_2):
            assert r1.to_dict() == r2.to_dict()


class TestPrivateReadingPassEdgeCases:
    def test_empty_personas_returns_empty_list(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj = PrivateReadingPass(cache=cache)
        evidence_pack = _make_evidence_pack()

        reactions = pass_obj.run(
            personas=[],
            evidence_pack=evidence_pack,
            simulation_id="sim_001",
            simulation_seed=42,
        )

        assert reactions == []


class TestPrivateReadingPassDeterminism:
    def test_deterministic_with_seed(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        pass_obj_a = PrivateReadingPass(cache=LocalArtifactCache(base_dir=tmp_cache_dir))
        pass_obj_b = PrivateReadingPass(cache=LocalArtifactCache(base_dir=tmp_cache_dir))

        personas = [
            _make_persona("persona_001", rating_bias=0.3),
            _make_persona("persona_002", rating_bias=-0.2),
        ]
        evidence_pack = _make_evidence_pack()

        reactions_a = pass_obj_a.run(
            personas=personas,
            evidence_pack=evidence_pack,
            simulation_id="sim_det",
            simulation_seed=12345,
        )
        reactions_b = pass_obj_b.run(
            personas=personas,
            evidence_pack=evidence_pack,
            simulation_id="sim_det",
            simulation_seed=12345,
        )

        assert len(reactions_a) == len(reactions_b)
        for ra, rb in zip(reactions_a, reactions_b):
            assert ra.rating == rb.rating
            assert ra.dnf_probability == rb.dnf_probability
            assert ra.sentiment == rb.sentiment
            assert ra.attachment_score == rb.attachment_score
            assert ra.confusion_score == rb.confusion_score
            assert ra.recommendation_probability == rb.recommendation_probability
