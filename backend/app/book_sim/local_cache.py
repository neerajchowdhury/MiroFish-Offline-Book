"""Simple local JSON cache for Swarmbook intermediate artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

class LocalArtifactCache:
    """Store cached Swarmbook artifacts by namespace and content hash."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        default_root = Path(__file__).resolve().parents[1] / "uploads" / "book_sim_cache"
        cache_root = Path(base_dir) if base_dir else default_root
        self.base_dir = Path(cache_root)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, namespace: str, cache_key: str) -> Path:
        namespace_dir = self.base_dir / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)
        return namespace_dir / f"{cache_key}.json"

    def get_json(self, namespace: str, cache_key: str) -> Optional[Dict[str, Any]]:
        path = self._path_for(namespace, cache_key)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def set_json(self, namespace: str, cache_key: str, payload: Dict[str, Any]) -> None:
        path = self._path_for(namespace, cache_key)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
