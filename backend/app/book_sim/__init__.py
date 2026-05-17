"""Swarmbook additive modules."""

from .config_loader import BookSimRoutingConfig
from .evidence_pack_builder import EvidencePackBuilder
from .graph_persistence import BookGraphPersistence, PersistenceResult
from .local_cache import LocalArtifactCache
from .manuscript_chunker import ManuscriptChunker
from .platform_adapters import PLATFORM_ADAPTERS
from .reader_archetype_loader import ReaderArchetypeCatalog, ReaderArchetypeLoader
from .reader_persona_generator import PersonaGenerationOverrides, ReaderPersonaGenerator
from .simulation import CrossReactionPass, PlatformReactionPass, PrivateReadingPass, SimulationOrchestrator
from .models import (
    BookDNA,
    BookPredictionReport,
    BookProject,
    ChapterMap,
    ChapterSummary,
    CharacterMap,
    CharacterProfile,
    ClaimMap,
    ClaimProfile,
    CrossReaction,
    DraftComparisonReport,
    EvidencePack,
    ManuscriptInput,
    MarketSurface,
    PlatformPost,
    PrivateReaderReaction,
    ReaderArchetype,
    ReaderPersona,
    RiskMap,
    RiskProfile,
    SimulationRun,
    StyleMap,
)
from .provider_router import BookSimProviderRouter, RouteSelection

__all__ = [
    "BookSimRoutingConfig",
    "LocalArtifactCache",
    "ManuscriptChunker",
    "EvidencePackBuilder",
    "BookGraphPersistence",
    "PersistenceResult",
    "PLATFORM_ADAPTERS",
    "ReaderArchetypeCatalog",
    "ReaderArchetypeLoader",
    "ReaderPersonaGenerator",
    "PersonaGenerationOverrides",
    "PrivateReadingPass",
    "PlatformReactionPass",
    "CrossReactionPass",
    "SimulationOrchestrator",
    "BookProject",
    "ManuscriptInput",
    "BookDNA",
    "ChapterMap",
    "ChapterSummary",
    "CharacterMap",
    "CharacterProfile",
    "ClaimMap",
    "ClaimProfile",
    "RiskMap",
    "RiskProfile",
    "StyleMap",
    "MarketSurface",
    "EvidencePack",
    "ReaderArchetype",
    "ReaderPersona",
    "PrivateReaderReaction",
    "PlatformPost",
    "CrossReaction",
    "SimulationRun",
    "BookPredictionReport",
    "DraftComparisonReport",
    "BookSimProviderRouter",
    "RouteSelection",
]
