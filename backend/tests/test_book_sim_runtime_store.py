"""Tests for book_sim.runtime_store.BookSimRuntimeStore."""

import pytest

from book_sim.local_cache import LocalArtifactCache
from book_sim.models import (
    BookPredictionReport,
    BookProject,
    DraftComparisonReport,
    EvidencePack,
    SimulationRun,
)
from book_sim.runtime_store import BookSimRuntimeStore


@pytest.fixture
def store(tmp_store_dir):
    """Create a BookSimRuntimeStore backed by a temporary directory."""
    cache = LocalArtifactCache(base_dir=tmp_store_dir)
    return BookSimRuntimeStore(cache=cache)


class TestRuntimeStoreProject:
    def test_save_and_get_project(self, store):
        project = BookProject(project_id="proj_001", name="Test Project")
        store.save_project(project)
        result = store.get_project("proj_001")
        assert result is not None
        assert result.project_id == "proj_001"
        assert result.name == "Test Project"

    def test_get_missing_project_returns_none(self, store):
        assert store.get_project("nonexistent") is None


class TestRuntimeStoreEvidencePack:
    def test_save_and_get_evidence_pack(self, store):
        pack = EvidencePack(pack_id="pack_001", project_id="proj_001")
        store.save_evidence_pack(pack)
        result = store.get_evidence_pack("pack_001")
        assert result is not None
        assert result.pack_id == "pack_001"

    def test_get_latest_evidence_pack(self, store):
        pack1 = EvidencePack(pack_id="pack_001", project_id="proj_001")
        pack2 = EvidencePack(pack_id="pack_002", project_id="proj_001")
        store.save_evidence_pack(pack1)
        store.save_evidence_pack(pack2)
        latest = store.get_latest_evidence_pack("proj_001")
        assert latest is not None
        assert latest.pack_id == "pack_002"


class TestRuntimeStoreSimulationRun:
    def test_save_and_get_simulation_run(self, store):
        run = SimulationRun(run_id="sim_001", project_id="proj_001")
        store.save_simulation_run(run)
        result = store.get_simulation_run("sim_001")
        assert result is not None
        assert result.run_id == "sim_001"

    def test_get_latest_simulation_run(self, store):
        run1 = SimulationRun(run_id="sim_001", project_id="proj_001")
        run2 = SimulationRun(run_id="sim_002", project_id="proj_001")
        store.save_simulation_run(run1)
        store.save_simulation_run(run2)
        latest = store.get_latest_simulation_run("proj_001")
        assert latest is not None
        assert latest.run_id == "sim_002"


class TestRuntimeStoreReport:
    def test_save_and_get_report(self, store):
        report = BookPredictionReport(report_id="rpt_001", project_id="proj_001")
        store.save_report(report)
        result = store.get_report("rpt_001")
        assert result is not None
        assert result.report_id == "rpt_001"

    def test_get_latest_report(self, store):
        report1 = BookPredictionReport(report_id="rpt_001", project_id="proj_001")
        report2 = BookPredictionReport(report_id="rpt_002", project_id="proj_001")
        store.save_report(report1)
        store.save_report(report2)
        latest = store.get_latest_report("proj_001")
        assert latest is not None
        assert latest.report_id == "rpt_002"


class TestRuntimeStoreComparison:
    def test_save_comparison(self, store):
        comparison = DraftComparisonReport(
            comparison_id="cmp_001",
            project_id="proj_001",
        )
        state = store.save_comparison(comparison)
        assert state is not None
        assert state.latest_comparison_id == "cmp_001"
        assert "cmp_001" in state.comparison_ids


class TestRuntimeStoreState:
    def test_project_state_tracks_ids(self, store):
        project = BookProject(project_id="proj_001", name="Track Test")
        store.save_project(project)

        pack = EvidencePack(pack_id="pack_001", project_id="proj_001")
        store.save_evidence_pack(pack)

        run = SimulationRun(run_id="sim_001", project_id="proj_001")
        store.save_simulation_run(run)

        report = BookPredictionReport(report_id="rpt_001", project_id="proj_001")
        store.save_report(report)

        state = store.get_project_state("proj_001")
        assert state is not None
        assert "pack_001" in state.evidence_pack_ids
        assert "sim_001" in state.simulation_ids
        assert "rpt_001" in state.report_ids


class TestRuntimeStoreTransaction:
    def test_transaction_commits_on_success(self, store):
        project = BookProject(project_id="proj_tx", name="Tx Test")
        store.save_project(project)

        with store.transaction("proj_tx") as txn:
            pack = EvidencePack(pack_id="pack_tx", project_id="proj_tx")
            txn.save_evidence_pack(pack)

        state = store.get_project_state("proj_tx")
        assert state is not None
        assert state.latest_evidence_pack_id == "pack_tx"

    def test_transaction_rolls_back_on_exception(self, store):
        project = BookProject(project_id="proj_rb", name="Rollback Test")
        store.save_project(project)

        pack = EvidencePack(pack_id="pack_before", project_id="proj_rb")
        store.save_evidence_pack(pack)

        with pytest.raises(RuntimeError):
            with store.transaction("proj_rb") as txn:
                bad_pack = EvidencePack(pack_id="pack_bad", project_id="proj_rb")
                txn.save_evidence_pack(bad_pack)
                raise RuntimeError("boom")

        state = store.get_project_state("proj_rb")
        assert state is not None
        assert state.latest_evidence_pack_id == "pack_before"
        assert "pack_bad" not in state.evidence_pack_ids


class TestRuntimeStoreAppendUnique:
    def test_append_unique_prevents_duplicates(self, store):
        pack1 = EvidencePack(pack_id="pack_dup", project_id="proj_001")
        state1 = store.save_evidence_pack(pack1)
        state2 = store.save_evidence_pack(pack1)

        assert state1.evidence_pack_ids.count("pack_dup") == 1
        assert state2.evidence_pack_ids.count("pack_dup") == 1
