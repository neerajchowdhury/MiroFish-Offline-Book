"""Shared pytest fixtures and configuration for MiroFish-Offline-Book backend tests.

This conftest.py eliminates duplicated sys.path manipulation across test files
and provides reusable fixture factories for common test objects.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Ensure backend app is on the Python path
BACKEND_ROOT = Path(__file__).resolve().parent.parent
APP_ROOT = BACKEND_ROOT / "app"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


@pytest.fixture(scope="session")
def backend_root():
    """Root directory of the backend package."""
    return BACKEND_ROOT


@pytest.fixture(scope="session")
def fixtures_dir():
    """Directory containing test fixture files."""
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def tiny_fiction_text():
    """Minimal fiction manuscript text (4 lines)."""
    fixture_path = FIXTURES_DIR / "tiny_fiction_manuscript.txt"
    return fixture_path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def tiny_fiction_revised_text():
    """Revised fiction manuscript for comparison tests."""
    fixture_path = FIXTURES_DIR / "tiny_fiction_manuscript_revised.txt"
    return fixture_path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def tiny_nonfiction_text():
    """Minimal nonfiction manuscript text."""
    fixture_path = FIXTURES_DIR / "tiny_nonfiction_manuscript.txt"
    return fixture_path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def fiction_sample_text():
    """Longer fiction manuscript sample."""
    fixture_path = FIXTURES_DIR / "book_sim_fiction_sample.txt"
    return fixture_path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def nonfiction_sample_text():
    """Longer nonfiction manuscript sample."""
    fixture_path = FIXTURES_DIR / "book_sim_nonfiction_sample.txt"
    return fixture_path.read_text(encoding="utf-8")


@pytest.fixture
def tmp_cache_dir():
    """Temporary directory for LocalArtifactCache tests. Auto-cleaned."""
    d = tempfile.mkdtemp(prefix="book_sim_cache_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def tmp_store_dir():
    """Temporary directory for BookSimRuntimeStore tests. Auto-cleaned."""
    d = tempfile.mkdtemp(prefix="book_sim_store_test_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_manuscript_input():
    """Factory for creating ManuscriptInput test objects."""
    from book_sim.models import ManuscriptInput

    def _create(
        input_id="input_test123",
        project_id="proj_test123",
        title="Test Book",
        text="This is a test manuscript with some content.",
        **kwargs,
    ):
        return ManuscriptInput(
            input_id=input_id,
            project_id=project_id,
            title=title,
            text=text,
            **kwargs,
        )

    return _create


@pytest.fixture
def sample_book_project():
    """Factory for creating BookProject test objects."""
    from book_sim.models import BookProject

    def _create(
        project_id="proj_test123",
        name="Test Project",
        privacy_mode="local_only",
        **kwargs,
    ):
        return BookProject(
            project_id=project_id,
            name=name,
            privacy_mode=privacy_mode,
            **kwargs,
        )

    return _create


@pytest.fixture
def sample_evidence_pack():
    """Factory for creating EvidencePack test objects."""
    from book_sim.models import EvidencePack, BookDNA

    def _create(
        pack_id="pack_test123",
        project_id="proj_test123",
        book_dna=None,
        **kwargs,
    ):
        if book_dna is None:
            book_dna = BookDNA(
                title="Test Book",
                premise="A test premise",
                genre="fiction",
            )
        return EvidencePack(
            pack_id=pack_id,
            project_id=project_id,
            book_dna=book_dna,
            **kwargs,
        )

    return _create


@pytest.fixture
def sample_simulation_run():
    """Factory for creating SimulationRun test objects."""
    from book_sim.models import SimulationRun

    def _create(
        run_id="sim_test123",
        project_id="proj_test123",
        **kwargs,
    ):
        return SimulationRun(
            run_id=run_id,
            project_id=project_id,
            **kwargs,
        )

    return _create


@pytest.fixture
def sample_reader_persona():
    """Factory for creating ReaderPersona test objects."""
    from book_sim.models import ReaderPersona

    def _create(
        persona_id="persona_001",
        archetype_id="critical_reader",
        display_name="Test Reader",
        platform_home="goodreads",
        review_style="analytical",
        **kwargs,
    ):
        return ReaderPersona(
            persona_id=persona_id,
            archetype_id=archetype_id,
            display_name=display_name,
            platform_home=platform_home,
            review_style=review_style,
            **kwargs,
        )

    return _create


@pytest.fixture
def fake_provider_router():
    """A minimal fake provider router that returns canned responses."""
    from unittest.mock import MagicMock

    router = MagicMock()
    router.generate_text.return_value = "{}"
    router.generate_json.return_value = {}
    router.is_available.return_value = True
    return router
