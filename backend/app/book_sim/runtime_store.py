"""Local artifact persistence for Swarmbook API endpoints.

Provides a file-backed store for projects, evidence packs, simulation runs,
reports, and comparisons. Supports transactional operations via the
transaction() context manager for atomic multi-step saves.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional

from .local_cache import LocalArtifactCache
from .models import (
    BookPredictionReport,
    BookProject,
    DraftComparisonReport,
    EvidencePack,
    JsonDataclassMixin,
    SimulationRun,
)


@dataclass
class ProjectArtifactState(JsonDataclassMixin):
    """Track the latest stored Swarmbook artifacts for one project."""

    project_id: str
    project: Optional[BookProject] = None
    latest_evidence_pack_id: Optional[str] = None
    latest_simulation_id: Optional[str] = None
    latest_report_id: Optional[str] = None
    latest_comparison_id: Optional[str] = None
    evidence_pack_ids: list[str] = field(default_factory=list)
    simulation_ids: list[str] = field(default_factory=list)
    report_ids: list[str] = field(default_factory=list)
    comparison_ids: list[str] = field(default_factory=list)


class BookSimRuntimeStore:
    """Persist API-facing Swarmbook artifacts in the local cache tree."""

    PROJECTS_NS = "runtime_projects"
    STATES_NS = "runtime_project_states"
    PACKS_NS = "runtime_evidence_packs"
    RUNS_NS = "runtime_simulation_runs"
    REPORTS_NS = "runtime_reports"
    COMPARISONS_NS = "runtime_comparisons"

    def __init__(self, cache: Optional[LocalArtifactCache] = None) -> None:
        self.cache = cache or LocalArtifactCache()

    def save_project(self, project: BookProject) -> ProjectArtifactState:
        self.cache.set_json(self.PROJECTS_NS, project.project_id, project.to_dict())
        state = self._load_state(project.project_id)
        state.project = project
        self._save_state(state)
        return state

    def get_project(self, project_id: str) -> Optional[BookProject]:
        payload = self.cache.get_json(self.PROJECTS_NS, project_id)
        return BookProject.from_dict(payload) if payload else None

    def save_evidence_pack(self, evidence_pack: EvidencePack) -> ProjectArtifactState:
        self.cache.set_json(self.PACKS_NS, evidence_pack.pack_id, evidence_pack.to_dict())
        state = self._load_state(evidence_pack.project_id)
        state.latest_evidence_pack_id = evidence_pack.pack_id
        state.evidence_pack_ids = self._append_unique(state.evidence_pack_ids, evidence_pack.pack_id)
        self._save_state(state)
        return state

    def get_evidence_pack(self, pack_id: str) -> Optional[EvidencePack]:
        payload = self.cache.get_json(self.PACKS_NS, pack_id)
        return EvidencePack.from_dict(payload) if payload else None

    def get_latest_evidence_pack(self, project_id: str) -> Optional[EvidencePack]:
        state = self.get_project_state(project_id)
        if not state or not state.latest_evidence_pack_id:
            return None
        return self.get_evidence_pack(state.latest_evidence_pack_id)

    def save_simulation_run(self, simulation_run: SimulationRun) -> ProjectArtifactState:
        self.cache.set_json(self.RUNS_NS, simulation_run.run_id, simulation_run.to_dict())
        state = self._load_state(simulation_run.project_id)
        state.latest_simulation_id = simulation_run.run_id
        state.simulation_ids = self._append_unique(state.simulation_ids, simulation_run.run_id)
        self._save_state(state)
        return state

    def get_simulation_run(self, run_id: str) -> Optional[SimulationRun]:
        payload = self.cache.get_json(self.RUNS_NS, run_id)
        return SimulationRun.from_dict(payload) if payload else None

    def get_latest_simulation_run(self, project_id: str) -> Optional[SimulationRun]:
        state = self.get_project_state(project_id)
        if not state or not state.latest_simulation_id:
            return None
        return self.get_simulation_run(state.latest_simulation_id)

    def save_report(self, report: BookPredictionReport) -> ProjectArtifactState:
        self.cache.set_json(self.REPORTS_NS, report.report_id, report.to_dict())
        state = self._load_state(report.project_id)
        state.latest_report_id = report.report_id
        state.report_ids = self._append_unique(state.report_ids, report.report_id)
        self._save_state(state)
        return state

    def get_report(self, report_id: str) -> Optional[BookPredictionReport]:
        payload = self.cache.get_json(self.REPORTS_NS, report_id)
        return BookPredictionReport.from_dict(payload) if payload else None

    def get_latest_report(self, project_id: str) -> Optional[BookPredictionReport]:
        state = self.get_project_state(project_id)
        if not state or not state.latest_report_id:
            return None
        return self.get_report(state.latest_report_id)

    def save_comparison(self, comparison: DraftComparisonReport) -> Optional[ProjectArtifactState]:
        self.cache.set_json(self.COMPARISONS_NS, comparison.comparison_id, comparison.to_dict())
        if not comparison.project_id:
            return None
        state = self._load_state(comparison.project_id)
        state.latest_comparison_id = comparison.comparison_id
        state.comparison_ids = self._append_unique(state.comparison_ids, comparison.comparison_id)
        self._save_state(state)
        return state

    def get_project_state(self, project_id: str) -> Optional[ProjectArtifactState]:
        payload = self.cache.get_json(self.STATES_NS, project_id)
        return ProjectArtifactState.from_dict(payload) if payload else None

    def _load_state(self, project_id: str) -> ProjectArtifactState:
        return self.get_project_state(project_id) or ProjectArtifactState(project_id=project_id)

    def _save_state(self, state: ProjectArtifactState) -> None:
        self.cache.set_json(self.STATES_NS, state.project_id, state.to_dict())

    def _append_unique(self, values: list[str], item: str) -> list[str]:
        if not item:
            return list(values)
        if item in values:
            return list(values)
        return list(values) + [item]

    @contextmanager
    def transaction(self, project_id: str):
        """Context manager for atomic multi-step operations.

        If an exception occurs within the context, the project state
        is rolled back to its pre-transaction snapshot. Note that
        individual artifact files (evidence packs, simulations, etc.)
        are not rolled back — only the project state index is.

        Usage:
            with store.transaction(project_id) as txn:
                txn.save_project(project)
                txn.save_evidence_pack(pack)
        """
        state = self._load_state(project_id)
        snapshot = state.to_dict()
        try:
            yield self
        except Exception:
            self._save_state(ProjectArtifactState.from_dict(snapshot))
            raise
