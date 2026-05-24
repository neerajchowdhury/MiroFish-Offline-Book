"""Tests for book_sim.report_markdown module."""

import pytest

from book_sim.report_markdown import render_prediction_report_markdown
from book_sim.models import BookPredictionReport


@pytest.fixture
def full_report():
    return BookPredictionReport(
        report_id="report_001",
        project_id="proj_001",
        simulation_id="sim_001",
        privacy_mode="local_only",
        draft_id="draft_v1",
        version="1.0",
        title="Test Book Report",
        summary="This is a comprehensive test summary.",
        scorecard={
            "rating_distribution": {"score": 4.2},
            "dnf": {"score": 0.15},
            "controversy": {"score": 0.3},
            "viral": {"risk": "low"},
            "quoteability": {"score": 0.7},
            "polarization": {"score": 0.2},
        },
        revision_priorities=[
            "Tighten chapter 3 pacing",
            "Clarify character motivations",
        ],
        top_risks=[
            "Slow pacing in middle chapters",
            "Low accessibility in dense sections",
        ],
        top_strengths=[
            "Strong opening hook",
            "Clear character arcs",
        ],
        uncertainty_notes=[
            "Limited data on target audience",
        ],
    )


@pytest.fixture
def minimal_report():
    return BookPredictionReport(
        report_id="report_002",
        project_id="proj_002",
    )


class TestRenderPredictionReportMarkdownBasic:
    def test_render_prediction_report_markdown_basic(self, full_report):
        result = render_prediction_report_markdown(full_report)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "# Swarmbook Report:" in result
        assert "report_001" in result
        assert "proj_002" not in result


class TestRenderWithEmptySections:
    def test_render_with_empty_sections(self, minimal_report):
        result = render_prediction_report_markdown(minimal_report)
        assert isinstance(result, str)
        assert "## Summary" in result
        assert "## Key Scores" in result
        assert "## Revision Priorities" in result
        assert "## Top Risks" in result
        assert "## Top Strengths" in result
        assert "## Notes" in result
        assert "No summary available" in result


class TestRenderWithFullReport:
    def test_render_with_full_report(self, full_report):
        result = render_prediction_report_markdown(full_report)
        assert "Test Book Report" in result
        assert "sim_001" in result
        assert "local_only" in result
        assert "draft_v1" in result
        assert "comprehensive test summary" in result
        assert "rating_distribution" in result
        assert "4.2" in result
        assert "Tighten chapter 3 pacing" in result
        assert "Slow pacing in middle chapters" in result
        assert "Strong opening hook" in result
        assert "Limited data on target audience" in result
