"""Markdown export helper for Swarmbook prediction reports.

The API stores reports as JSON dataclasses for stability. This helper renders a
human-readable Markdown summary without requiring any external provider calls.
"""

from __future__ import annotations

from typing import Iterable, List

from .models import BookPredictionReport


def render_prediction_report_markdown(report: BookPredictionReport) -> str:
    """Render a prediction report into stable Markdown."""
    lines: List[str] = []
    lines.append(f"# Swarmbook Report: {report.title or report.project_id}")
    lines.append("")
    lines.append(f"- Report ID: `{report.report_id}`")
    lines.append(f"- Project ID: `{report.project_id}`")
    if report.simulation_id:
        lines.append(f"- Simulation ID: `{report.simulation_id}`")
    if report.privacy_mode:
        lines.append(f"- Privacy Mode: `{report.privacy_mode}`")
    if report.draft_id or report.version:
        lines.append(f"- Draft: `{report.draft_id or 'unknown'}` / `{report.version or 'unknown'}`")
    lines.append("")
    lines.append("## Summary")
    lines.append(report.summary or "No summary available.")
    lines.append("")
    lines.append("## Key Scores")
    for key in ("rating_distribution", "dnf", "controversy", "viral", "quoteability", "polarization"):
        payload = (report.scorecard or {}).get(key) or {}
        score = payload.get("score")
        risk = payload.get("risk") if "risk" in payload else None
        headline = score if score is not None else risk
        if headline is None:
            continue
        lines.append(f"- {key}: {headline}")
    lines.append("")
    lines.append("## Revision Priorities")
    lines.extend(_render_list(report.revision_priorities, fallback="- No revision priorities were generated."))
    lines.append("")
    lines.append("## Top Risks")
    lines.extend(_render_list(report.top_risks, fallback="- No top risks were detected."))
    lines.append("")
    lines.append("## Top Strengths")
    lines.extend(_render_list(report.top_strengths, fallback="- No top strengths were detected."))
    lines.append("")
    lines.append("## Notes")
    lines.extend(_render_list(report.uncertainty_notes, fallback="- No uncertainty notes were recorded."))
    return "\n".join(lines).strip() + "\n"


def _render_list(items: Iterable[str] | None, fallback: str) -> List[str]:
    values = [str(item).strip() for item in (items or []) if str(item).strip()]
    if not values:
        return [fallback]
    return [f"- {value}" for value in values]

