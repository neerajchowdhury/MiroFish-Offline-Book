"""Tests for book_sim.local_cache.LocalArtifactCache."""

import json
import threading
from pathlib import Path

import pytest

from book_sim.local_cache import LocalArtifactCache


class TestLocalArtifactCacheBasic:
    def test_set_and_get_json(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        payload = {"key": "value", "number": 42}
        cache.set_json("ns1", "item1", payload)
        result = cache.get_json("ns1", "item1")
        assert result == payload

    def test_get_missing_key_returns_none(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        assert cache.get_json("ns1", "nonexistent") is None

    def test_overwrite_existing_key(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        cache.set_json("ns1", "item1", {"version": 1})
        cache.set_json("ns1", "item1", {"version": 2})
        result = cache.get_json("ns1", "item1")
        assert result == {"version": 2}


class TestLocalArtifactCacheAtomicWrite:
    def test_atomic_write_survives_crash(self, tmp_cache_dir):
        """Write completes, file is valid JSON."""
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        payload = {"data": [1, 2, 3], "meta": "test"}
        cache.set_json("atomic_ns", "atomic_key", payload)

        file_path = Path(tmp_cache_dir) / "atomic_ns" / "atomic_key.json"
        assert file_path.exists()

        with file_path.open("r", encoding="utf-8") as f:
            content = json.load(f)
        assert content == payload


class TestLocalArtifactCacheThreadSafety:
    def test_thread_safety_concurrent_writes(self, tmp_cache_dir):
        """Multiple threads write same key, no corruption."""
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        errors = []

        def writer(thread_id):
            try:
                for i in range(20):
                    cache.set_json("concurrent_ns", "shared_key", {"thread": thread_id, "iteration": i})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(tid,)) for tid in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"

        result = cache.get_json("concurrent_ns", "shared_key")
        assert result is not None
        assert "thread" in result
        assert "iteration" in result


class TestLocalArtifactCacheNamespaces:
    def test_different_namespaces_isolated(self, tmp_cache_dir):
        cache = LocalArtifactCache(base_dir=tmp_cache_dir)
        cache.set_json("ns_a", "key1", {"namespace": "a"})
        cache.set_json("ns_b", "key1", {"namespace": "b"})

        result_a = cache.get_json("ns_a", "key1")
        result_b = cache.get_json("ns_b", "key1")

        assert result_a == {"namespace": "a"}
        assert result_b == {"namespace": "b"}


class TestLocalArtifactCacheDirectoryCreation:
    def test_creates_directory_if_missing(self, tmp_cache_dir):
        nested_dir = Path(tmp_cache_dir) / "deep" / "nested" / "dir"
        cache = LocalArtifactCache(base_dir=str(nested_dir))
        cache.set_json("ns1", "item1", {"created": True})
        result = cache.get_json("ns1", "item1")
        assert result == {"created": True}
        assert nested_dir.exists()
