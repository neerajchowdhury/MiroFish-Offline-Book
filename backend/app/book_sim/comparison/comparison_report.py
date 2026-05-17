"""JSON and Markdown export helpers for draft comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from ..models import DraftComparisonReport, JsonDataclassMixin


@dataclass
class DraftComparisonExport(JsonDataclassMixin):
    """Serialized comparison output in both JSON and Markdown forms."""

    report: DraftComparisonReport
    markdown: str


def render_comparison_markdown(report: DraftComparisonReport) -> str:
    """Render the comparison report into stable Markdown."""
    lines: List[str] = []
    title = f"Draft Comparison: {report.base_draft_id or 'base'} vs {report.compare_draft_id or 'compare'}"
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## Summary")
    lines.append(report.summary or "No comparison summary available.")
    lines.append("")
    lines.append("## Score Movement")
    if report.delta_scores:
        for key, value in sorted(report.delta_scores.items()):
            lines.append(f"- **{_humanize(key)}**: {_format_value(value)}")
    else:
        lines.append("- No score movement was available.")
    lines.append("")
    lines.append("## Book DNA Changes")
    lines.extend(_render_mapping_list(report.book_dna_changes, fallback="- No book DNA changes were detected."))
    lines.append("")
    lines.append("## Chapter Map Changes")
    lines.extend(_render_mapping_list(report.chapter_deltas, fallback="- No chapter-level changes were detected."))
    lines.append("")
    lines.append("## Character Changes")
    lines.extend(_render_mapping_list(report.character_deltas, fallback="- No character changes were detected."))
    lines.append("")
    lines.append("## Claim Changes")
    lines.extend(_render_mapping_list(report.claim_deltas, fallback="- No claim changes were detected."))
    lines.append("")
    lines.append("## Reader Segment Movement")
    lines.extend(_render_mapping_list(report.reader_segment_movement, fallback="- No reader segment movement was available."))
    lines.append("")
    lines.append("## Revision Impact Summary")
    lines.extend(_render_string_list(report.revision_impact_summary, fallback="- No revision impact summary was generated."))
    lines.append("")
    lines.append("## What Improved")
    lines.extend(_render_string_list(report.what_improved, fallback="- No clear improvements were detected."))
    lines.append("")
    lines.append("## What Got Worse")
    lines.extend(_render_string_list(report.what_got_worse, fallback="- No regressions were detected."))
    lines.append("")
    lines.append("## What Still Blocks Publishing")
    lines.extend(_render_string_list(report.still_blocking, fallback="- No blocking issues were detected from the available signals."))
    lines.append("")
    lines.append("## Revision Priorities")
    lines.extend(_render_string_list(report.revision_priorities, fallback="- No revision priorities were generated."))
    return "\n".join(lines).strip() + "\n"


def _render_string_list(items: Iterable[str], fallback: str) -> List[str]:
    values = [item for item in items if item]
    if not values:
        return [fallback]
    return [f"- {item}" for item in values]


def _render_mapping_list(items: Iterable[dict], fallback: str) -> List[str]:
    values = [item for item in items if item]
    if not values:
        return [fallback]
    return [f"- {_format_mapping(item)}" for item in values]


def _format_mapping(item: dict) -> str:
    parts: List[str] = []
    for key in sorted(item):
        value = item[key]
        if value in (None, "", [], {}):
            continue
        parts.append(f"{_humanize(key)}={_format_value(value)}")
    return "; ".join(parts) if parts else "No details"


def _format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(f"{_humanize(str(key))}: {_format_value(item)}" for key, item in sorted(value.items()))
    return str(value)


def _humanize(raw: str) -> str:
    return raw.replace("_", " ").strip().title()
