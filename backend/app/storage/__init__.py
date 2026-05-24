"""
MiroFish-Offline Storage Layer

Local graph storage replacing Zep Cloud:
- Neo4j CE for graph persistence
- Ollama for embeddings (nomic-embed-text)
- LLM-based NER/RE extraction
- Hybrid search (vector + keyword)
"""

from .graph_storage import GraphStorage
from .embedding_service import EmbeddingService, EmbeddingError

# Neo4jStorage is optional — only imported when neo4j driver is installed
try:
    from .neo4j_storage import Neo4jStorage
except ImportError:
    Neo4jStorage = None  # type: ignore[misc,assignment]

from .ner_extractor import NERExtractor
from .search_service import SearchService

__all__ = [
    "GraphStorage",
    "Neo4jStorage",
    "EmbeddingService",
    "EmbeddingError",
    "NERExtractor",
    "SearchService",
]
