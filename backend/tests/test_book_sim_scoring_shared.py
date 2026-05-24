"""Tests for book_sim.scoring._shared utilities."""

import pytest

from book_sim.scoring._shared import (
    clamp,
    confidence_band,
    load_scoring_weights,
    sorted_unique,
    stable_digest,
    weighted_average,
    weighted_mean,
)


class TestClamp:
    def test_clamp_bounds(self):
        assert clamp(0.5) == 0.5
        assert clamp(0.0) == 0.0
        assert clamp(1.0) == 1.0

    def test_clamp_below_minimum(self):
        assert clamp(-0.5) == 0.0
        assert clamp(-10.0) == 0.0

    def test_clamp_above_maximum(self):
        assert clamp(1.5) == 1.0
        assert clamp(99.0) == 1.0


class TestWeightedAverage:
    def test_weighted_average_basic(self):
        values = {"a": 1.0, "b": 2.0}
        weights = {"a": 1.0, "b": 1.0}
        assert weighted_average(values, weights) == 1.5

    def test_weighted_average_empty(self):
        assert weighted_average({}, {}) == 0.0
        assert weighted_average({"a": 1.0}, {}) == 0.0


class TestWeightedMean:
    def test_weighted_mean_basic(self):
        assert weighted_mean([1.0, 2.0, 3.0], [1.0, 1.0, 1.0]) == 2.0
        assert weighted_mean([1.0, 3.0], [1.0, 3.0]) == 2.5

    def test_weighted_mean_empty(self):
        assert weighted_mean([], []) == 0.0
        assert weighted_mean([1.0], []) == 0.0


class TestConfidenceBand:
    def test_confidence_band_basic(self):
        band = confidence_band(mid=0.5, spread=0.1, label="moderate")
        assert band.low == 0.4
        assert band.mid == 0.5
        assert band.high == 0.6
        assert band.label == "moderate"


class TestStableDigest:
    def test_stable_digest_deterministic(self):
        d1 = stable_digest("a", "b", "c")
        d2 = stable_digest("a", "b", "c")
        assert d1 == d2
        assert len(d1) == 64

    def test_stable_digest_different_inputs(self):
        d1 = stable_digest("a", "b")
        d2 = stable_digest("x", "y")
        assert d1 != d2


class TestSortedUnique:
    def test_sorted_unique_removes_duplicates(self):
        assert sorted_unique(["b", "a", "b", "a"]) == ["b", "a"]

    def test_sorted_unique_already_sorted(self):
        assert sorted_unique(["a", "b", "c"]) == ["a", "b", "c"]


class TestLoadScoringWeights:
    def test_load_scoring_weights_returns_dict(self):
        weights = load_scoring_weights()
        assert isinstance(weights, dict)
