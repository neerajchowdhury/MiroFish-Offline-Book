"""
Minimal local smoke checks for MiroFish-Offline.

This script does not modify application state. It only verifies that the
existing local-first services are reachable with the current configuration:
1. Backend health endpoint
2. Frontend dev server
3. Neo4j Bolt connectivity
4. Ollama HTTP connectivity
"""

from __future__ import annotations

import argparse
import json
import importlib.util
import os
import sys
from dataclasses import dataclass
from typing import Callable
from urllib import request


BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)


def _load_config_class():
    """Load Config without importing app package (which requires Flask)."""
    config_path = os.path.join(BACKEND_ROOT, "app", "config.py")
    spec = importlib.util.spec_from_file_location("mirofish_backend_config", config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load config module from: {config_path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module.Config
    except Exception:
        class _FallbackConfig:
            EMBEDDING_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
            NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687")
            NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
            NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

            @staticmethod
            def validate():
                return []

        return _FallbackConfig


Config = _load_config_class()


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    """Fetch a URL and return status plus a small response snippet."""
    req = request.Request(url, headers={"User-Agent": "MiroFish-SmokeCheck/1.0"})
    with request.urlopen(req, timeout=timeout) as resp:
        body = resp.read(512).decode("utf-8", errors="replace")
        return resp.status, body


def check_backend_health(base_url: str) -> CheckResult:
    url = f"{base_url.rstrip('/')}/health"
    try:
        status, body = http_get(url)
        payload = json.loads(body)
        ok = status == 200 and payload.get("status") == "ok"
        detail = f"status={status}, payload={payload}"
        return CheckResult("backend", ok, detail)
    except Exception as exc:
        return CheckResult("backend", False, f"{url} -> {exc}")


def check_frontend(frontend_url: str) -> CheckResult:
    try:
        status, body = http_get(frontend_url)
        ok = status == 200 and ("<div id=\"app\">" in body or "vite" in body.lower())
        detail = f"status={status}, title_snippet={body[:120]!r}"
        return CheckResult("frontend", ok, detail)
    except Exception as exc:
        return CheckResult("frontend", False, f"{frontend_url} -> {exc}")


def check_ollama(base_url: str) -> CheckResult:
    url = f"{base_url.rstrip('/')}/api/tags"
    try:
        status, body = http_get(url)
        payload = json.loads(body)
        ok = status == 200 and isinstance(payload.get("models"), list)
        detail = f"status={status}, models={len(payload.get('models', []))}"
        return CheckResult("ollama", ok, detail)
    except Exception as exc:
        return CheckResult("ollama", False, f"{url} -> {exc}")


def check_neo4j() -> CheckResult:
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            Config.NEO4J_URI,
            auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
        )
        try:
            driver.verify_connectivity()
            return CheckResult("neo4j", True, f"uri={Config.NEO4J_URI}")
        finally:
            driver.close()
    except Exception as exc:
        return CheckResult("neo4j", False, f"{Config.NEO4J_URI} -> {exc}")


def run_checks(checks: list[Callable[[], CheckResult]]) -> list[CheckResult]:
    return [check() for check in checks]


def print_results(results: list[CheckResult]) -> int:
    failures = 0
    print("=" * 72)
    print("MiroFish-Offline smoke checks")
    print("=" * 72)

    for result in results:
        status = "PASS" if result.ok else "FAIL"
        if not result.ok:
            failures += 1
        print(f"[{status}] {result.name}: {result.detail}")

    print("=" * 72)
    print(f"Summary: {len(results) - failures} passed, {failures} failed")
    return 0 if failures == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local smoke checks")
    parser.add_argument(
        "--backend-url",
        default="http://127.0.0.1:5001",
        help="Backend base URL (default: http://127.0.0.1:5001)",
    )
    parser.add_argument(
        "--frontend-url",
        default="http://127.0.0.1:3000",
        help="Frontend base URL (default: http://127.0.0.1:3000)",
    )
    parser.add_argument(
        "--ollama-url",
        default=Config.EMBEDDING_BASE_URL,
        help="Ollama base URL (default: EMBEDDING_BASE_URL)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    config_errors = Config.validate()
    if config_errors:
        print("Config validation warnings:")
        for err in config_errors:
            print(f"  - {err}")
        print()

    results = run_checks(
        [
            lambda: check_backend_health(args.backend_url),
            lambda: check_frontend(args.frontend_url),
            check_neo4j,
            lambda: check_ollama(args.ollama_url),
        ]
    )
    return print_results(results)


if __name__ == "__main__":
    raise SystemExit(main())
