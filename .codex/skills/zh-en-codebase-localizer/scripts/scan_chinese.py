#!/usr/bin/env python3
"""
Scan a repository for Chinese/CJK text and classify likely translation targets.
No third-party dependencies.

Usage:
  python .claude/skills/zh-en-codebase-localizer/scripts/scan_chinese.py . --format markdown
  python .claude/skills/zh-en-codebase-localizer/scripts/scan_chinese.py . --format json
"""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", ".next", ".nuxt",
    "coverage", ".cache", "target", "bin", "obj", ".venv", "venv", "__pycache__",
}

SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".pdf", ".zip", ".gz",
    ".tar", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib", ".class", ".jar", ".lock",
    ".min.js", ".map",
}

DOC_EXTS = {".md", ".mdx", ".txt", ".rst", ".adoc"}
LOCALE_EXTS = {".json", ".json5", ".yaml", ".yml", ".toml", ".po", ".properties", ".arb", ".strings", ".xml"}
CODE_EXTS = {
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".py", ".java", ".kt", ".go", ".rs",
    ".php", ".rb", ".cs", ".cpp", ".c", ".h", ".hpp", ".swift", ".dart",
}

UI_HINTS = re.compile(
    r"(label|title|placeholder|tooltip|message|error|success|warning|button|menu|toast|modal|dialog|empty|i18n|locale|lang|translation|translations)",
    re.IGNORECASE,
)
COMMENT_HINTS = re.compile(r"^\s*(//|#|/\*|\*|<!--|--|;)")

@dataclass
class Finding:
    file: str
    line: int
    category: str
    text: str


def should_skip_path(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    name = path.name.lower()
    return any(name.endswith(suffix) for suffix in SKIP_SUFFIXES)


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if not should_skip_path(path):
                yield path


def classify(path: Path, line: str) -> str:
    ext = path.suffix.lower()
    path_str = str(path).lower()
    if ext in DOC_EXTS:
        return "DOC"
    if ext in LOCALE_EXTS or UI_HINTS.search(path_str):
        return "LOCALE" if ext in LOCALE_EXTS else "UI"
    if ext in CODE_EXTS:
        if COMMENT_HINTS.search(line):
            return "COMMENT"
        if UI_HINTS.search(line):
            return "UI"
        # String-ish code line containing Chinese. Needs review.
        if any(q in line for q in ['"', "'", "`"]):
            return "UI_OR_STRING"
        return "COMMENT_OR_CODE"
    return "UNKNOWN"


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "big5"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root):
        text = read_text(path)
        if text is None or not CJK_RE.search(text):
            continue
        rel = path.relative_to(root).as_posix()
        for idx, line in enumerate(text.splitlines(), start=1):
            if CJK_RE.search(line):
                snippet = line.strip()
                if len(snippet) > 220:
                    snippet = snippet[:217] + "..."
                findings.append(Finding(rel, idx, classify(path, line), snippet))
    return findings


def output_markdown(findings: list[Finding]) -> str:
    lines = ["# Chinese/CJK Translation Scan", ""]
    lines.append(f"Total findings: {len(findings)}")
    lines.append("")
    if not findings:
        lines.append("No Chinese/CJK text found.")
        return "\n".join(lines)
    lines.append("| File | Line | Category | Text |")
    lines.append("|---|---:|---|---|")
    for f in findings:
        text = f.text.replace("|", "\\|")
        lines.append(f"| `{f.file}` | {f.line} | {f.category} | {text} |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan repo for Chinese/CJK text.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = scan(root)

    if args.format == "json":
        print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))
    else:
        print(output_markdown(findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
