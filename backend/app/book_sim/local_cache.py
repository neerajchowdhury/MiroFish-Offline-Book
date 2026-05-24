"""Simple local JSON cache for Swarmbook intermediate artifacts.

Uses atomic write (temp file + rename) to prevent data corruption
from crashes during writes, and per-key threading locks for
concurrent access safety.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class LocalArtifactCache:
    """Store cached Swarmbook artifacts by namespace and content hash.

    Thread-safe with per-key locks. Writes are atomic (temp file + rename)
    to prevent partial writes from corrupting cached data.
    """

    def __init__(self, base_dir: Optional[str] = None) -> None:
        default_root = Path(__file__).resolve().parents[1] / "uploads" / "book_sim_cache"
        cache_root = Path(base_dir) if base_dir else default_root
        self.base_dir = Path(cache_root)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()

    def _get_lock(self, namespace: str, cache_key: str) -> threading.Lock:
        """Get or create a per-key lock for thread-safe access."""
        lock_key = f"{namespace}:{cache_key}"
        with self._global_lock:
            if lock_key not in self._locks:
                self._locks[lock_key] = threading.Lock()
            return self._locks[lock_key]

    def _path_for(self, namespace: str, cache_key: str) -> Path:
        namespace_dir = self.base_dir / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        return namespace_dir / f"{cache_key}.json"

    def get_json(self, namespace: str, cache_key: str) -> Optional[Dict[str, Any]]:
        """Read a JSON artifact from the cache (thread-safe)."""
        path = self._path_for(namespace, cache_key)
        lock = self._get_lock(namespace, cache_key)
        with lock:
            if not path.exists():
                return None
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)

    def set_json(self, namespace: str, cache_key: str, payload: Dict[str, Any]) -> None:
        """Write a JSON artifact to the cache atomically (thread-safe).

        Uses a temporary file + os.replace() to ensure writes are atomic.
        If the write fails, the temp file is cleaned up and the original
        file (if any) is left intact.
        """
        path = self._path_for(namespace, cache_key)
        lock = self._get_lock(namespace, cache_key)
        with lock:
            dir_path = path.parent
            fd, tmp_path = tempfile.mkstemp(dir=str(dir_path), suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, ensure_ascii=False, indent=2)
                os.replace(tmp_path, str(path))
            except Exception:
                # Clean up temp file on failure
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise
