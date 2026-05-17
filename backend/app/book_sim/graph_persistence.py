"""Swarmbook Neo4j persistence for book-specific artifacts.

This module is additive to the legacy graph storage layer. It writes Swarmbook
artifacts into a dedicated namespace and uses idempotent upserts so repeated
ingests do not duplicate nodes or relationships.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from .models import (
    BookDNA,
    BookPredictionReport,
    BookProject,
    ChapterMap,
    CharacterMap,
    ClaimMap,
    CrossReaction,
    EvidencePack,
    MarketSurface,
    PlatformPost,
    PrivateReaderReaction,
    ReaderPersona,
    RiskMap,
    SimulationRun,
    StyleMap,
)

logger = logging.getLogger("mirofish.book_sim.graph_persistence")


SUPPORTED_NODE_LABELS = {
    "Book",
    "Draft",
    "Chapter",
    "Character",
    "Theme",
    "Trope",
    "Claim",
    "Evidence",
    "Risk",
    "StyleSignal",
    "MarketSurface",
    "ReaderPersona",
    "PrivateReaction",
    "PlatformPost",
    "CrossReaction",
    "Report",
}


@dataclass
class PersistenceResult:
    """Outcome of a persistence run."""

    namespace: str
    dry_run: bool
    nodes_upserted: int = 0
    relationships_upserted: int = 0
    artifacts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BookGraphPersistence:
    """Persist Swarmbook artifacts into a dedicated Neo4j namespace."""

    def __init__(
        self,
        storage: Any = None,
        driver: Any = None,
        dry_run: bool = False,
        namespace_prefix: str = "book_sim",
    ) -> None:
        self._storage = storage
        self._driver = driver or getattr(storage, "_driver", None)
        self._dry_run = dry_run or self._driver is None
        self._namespace_prefix = namespace_prefix

    def persist_evidence_pack(
        self,
        project: BookProject,
        evidence_pack: EvidencePack,
        book_id: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> PersistenceResult:
        ns = namespace or self._namespace(project.project_id, book_id, evidence_pack.draft_id)
        payload = self._build_pack_payload(project, evidence_pack, book_id=book_id, namespace=ns)
        return self._commit(payload, ns)

    def persist_simulation_artifacts(
        self,
        project: BookProject,
        simulation_run: SimulationRun,
        reader_personas: Optional[Sequence[ReaderPersona]] = None,
        private_reactions: Optional[Sequence[PrivateReaderReaction]] = None,
        platform_posts: Optional[Sequence[PlatformPost]] = None,
        cross_reactions: Optional[Sequence[CrossReaction]] = None,
        report: Optional[BookPredictionReport] = None,
        namespace: Optional[str] = None,
    ) -> PersistenceResult:
        ns = namespace or self._namespace(project.project_id, simulation_run.draft_id, simulation_run.run_id)
        payload = self._build_simulation_payload(
            project=project,
            simulation_run=simulation_run,
            reader_personas=reader_personas or [],
            private_reactions=private_reactions or [],
            platform_posts=platform_posts or [],
            cross_reactions=cross_reactions or [],
            report=report,
            namespace=ns,
        )
        return self._commit(payload, ns)

    def _commit(self, payload: Dict[str, Any], namespace: str) -> PersistenceResult:
        if self._dry_run:
            return PersistenceResult(
                namespace=namespace,
                dry_run=True,
                nodes_upserted=len(payload["nodes"]),
                relationships_upserted=len(payload["relationships"]),
                artifacts=payload["artifacts"],
            )

        self._ensure_schema()
        self._write_nodes(payload["nodes"])
        self._write_relationships(payload["relationships"])
        return PersistenceResult(
            namespace=namespace,
            dry_run=False,
            nodes_upserted=len(payload["nodes"]),
            relationships_upserted=len(payload["relationships"]),
            artifacts=payload["artifacts"],
        )

    def _namespace(self, project_id: str, book_id: Optional[str], draft_id: Optional[str]) -> str:
        parts = [self._namespace_prefix, project_id]
        if book_id:
            parts.append(book_id)
        if draft_id:
            parts.append(draft_id)
        return ":".join(parts)

    def _ensure_schema(self) -> None:
        if self._dry_run or self._driver is None:
            return
        statements = [
            """
            CREATE CONSTRAINT book_sim_artifact_key IF NOT EXISTS
            FOR (n:Book) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_draft_key IF NOT EXISTS
            FOR (n:Draft) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_chapter_key IF NOT EXISTS
            FOR (n:Chapter) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_character_key IF NOT EXISTS
            FOR (n:Character) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_claim_key IF NOT EXISTS
            FOR (n:Claim) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_evidence_key IF NOT EXISTS
            FOR (n:Evidence) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_risk_key IF NOT EXISTS
            FOR (n:Risk) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_style_key IF NOT EXISTS
            FOR (n:StyleSignal) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
            """
            CREATE CONSTRAINT book_sim_market_key IF NOT EXISTS
            FOR (n:MarketSurface) REQUIRE (n.namespace, n.artifact_key) IS UNIQUE
            """,
        ]
        with self._driver.session() as session:
            for statement in statements:
                session.run(statement)

    def _write_nodes(self, nodes: Sequence[Dict[str, Any]]) -> None:
        with self._driver.session() as session:
            for node in nodes:
                session.execute_write(lambda tx, n=node: tx.run(self._merge_node_cypher(n), **self._node_params(n)))

    def _write_relationships(self, relationships: Sequence[Dict[str, Any]]) -> None:
        with self._driver.session() as session:
            for rel in relationships:
                session.execute_write(lambda tx, r=rel: tx.run(self._merge_rel_cypher(r), **r))

    def _merge_node_cypher(self, node: Dict[str, Any]) -> str:
        return (
            f"MERGE (n:`{node['label']}` {{namespace: $namespace, artifact_key: $artifact_key}}) "
            "SET n += $properties, "
            "n.namespace = $namespace, "
            "n.artifact_key = $artifact_key, "
            "n.project_id = $project_id, "
            "n.updated_at = $updated_at "
            "RETURN n"
        )

    def _merge_rel_cypher(self, rel: Dict[str, Any]) -> str:
        return (
            f"MATCH (src:`{rel['source_label']}` {{namespace: $namespace, artifact_key: $source_key}}) "
            f"MATCH (tgt:`{rel['target_label']}` {{namespace: $namespace, artifact_key: $target_key}}) "
            f"MERGE (src)-[r:`{rel['type']}` {{namespace: $namespace, source_key: $source_key, target_key: $target_key}}]->(tgt) "
            "SET r.updated_at = $updated_at "
            "RETURN r"
        )

    def _node_params(self, node: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "namespace": node["namespace"],
            "artifact_key": node["artifact_key"],
            "project_id": node["project_id"],
            "properties": node["properties"],
            "updated_at": self._now(),
        }

    def _build_pack_payload(
        self,
        project: BookProject,
        evidence_pack: EvidencePack,
        book_id: Optional[str],
        namespace: str,
    ) -> Dict[str, Any]:
        resolved_book_id = book_id or (evidence_pack.book_dna.title if evidence_pack.book_dna else project.project_id)
        nodes: List[Dict[str, Any]] = []
        relationships: List[Dict[str, Any]] = []
        artifacts = ["Book", "Draft", "Chapter", "Character", "Claim", "Evidence", "Risk", "StyleSignal", "MarketSurface"]

        if evidence_pack.book_dna:
            nodes.append(self._book_node(project.project_id, resolved_book_id, namespace, evidence_pack.book_dna, evidence_pack))
            if evidence_pack.book_dna.themes:
                theme_key = self._artifact_key("theme", namespace, project.project_id, resolved_book_id)
                nodes.append(
                    self._generic_node(
                        "Theme",
                        theme_key,
                        namespace,
                        project.project_id,
                        {
                            "project_id": project.project_id,
                            "book_id": resolved_book_id,
                            "themes": evidence_pack.book_dna.themes,
                        },
                    )
                )
                relationships.append(
                    self._rel(
                        "HAS_THEME",
                        "Book",
                        self._book_key(project.project_id, resolved_book_id),
                        "Theme",
                        theme_key,
                        namespace,
                    )
                )
        if evidence_pack.manuscript_input:
            nodes.append(self._draft_node(project.project_id, resolved_book_id, namespace, evidence_pack))
            relationships.append(self._rel("HAS_DRAFT", "Book", self._book_key(project.project_id, resolved_book_id), "Draft", evidence_pack.manuscript_input.input_id, namespace))
        if evidence_pack.chapter_map:
            chapter_nodes = self._chapter_nodes(project.project_id, resolved_book_id, namespace, evidence_pack.chapter_map)
            nodes.extend(chapter_nodes)
            relationships.extend(self._rel("HAS_CHAPTER", "Book", self._book_key(project.project_id, resolved_book_id), "Chapter", chapter["artifact_key"], namespace) for chapter in chapter_nodes)
        if evidence_pack.character_map:
            character_nodes = self._character_nodes(project.project_id, resolved_book_id, namespace, evidence_pack.character_map)
            nodes.extend(character_nodes)
            relationships.extend(self._rel("HAS_CHARACTER", "Book", self._book_key(project.project_id, resolved_book_id), "Character", character["artifact_key"], namespace) for character in character_nodes)
        if evidence_pack.claim_map:
            claim_nodes, evidence_nodes = self._claim_nodes(project.project_id, resolved_book_id, namespace, evidence_pack.claim_map)
            nodes.extend(claim_nodes)
            nodes.extend(evidence_nodes)
            relationships.extend(self._rel("HAS_CLAIM", "Book", self._book_key(project.project_id, resolved_book_id), "Claim", claim["artifact_key"], namespace) for claim in claim_nodes)
            relationships.extend(self._rel("SUPPORTS", "Claim", evidence["claim_ref"], "Evidence", evidence["artifact_key"], namespace) for evidence in evidence_nodes)
        if evidence_pack.risk_map:
            risk_nodes = self._risk_nodes(project.project_id, resolved_book_id, namespace, evidence_pack.risk_map)
            nodes.extend(risk_nodes)
            relationships.extend(self._rel("HAS_RISK", "Book", self._book_key(project.project_id, resolved_book_id), "Risk", risk["artifact_key"], namespace) for risk in risk_nodes)
        if evidence_pack.style_map:
            style_node = self._style_node(project.project_id, resolved_book_id, namespace, evidence_pack.style_map)
            nodes.append(style_node)
            relationships.append(self._rel("HAS_STYLE_SIGNAL", "Book", self._book_key(project.project_id, resolved_book_id), "StyleSignal", style_node["artifact_key"], namespace))
        if evidence_pack.market_surface:
            market_node = self._market_node(project.project_id, resolved_book_id, namespace, evidence_pack.market_surface)
            nodes.append(market_node)
            relationships.append(self._rel("HAS_MARKET_SURFACE", "Book", self._book_key(project.project_id, resolved_book_id), "MarketSurface", market_node["artifact_key"], namespace))

        return {"nodes": nodes, "relationships": relationships, "artifacts": artifacts}

    def _build_simulation_payload(
        self,
        project: BookProject,
        simulation_run: SimulationRun,
        reader_personas: Sequence[ReaderPersona],
        private_reactions: Sequence[PrivateReaderReaction],
        platform_posts: Sequence[PlatformPost],
        cross_reactions: Sequence[CrossReaction],
        report: Optional[BookPredictionReport],
        namespace: str,
    ) -> Dict[str, Any]:
        nodes: List[Dict[str, Any]] = [
            {
                "label": "Draft",
                "artifact_key": simulation_run.run_id,
                "namespace": namespace,
                "project_id": project.project_id,
                "properties": self._clean_properties(
                    {
                        "project_id": project.project_id,
                        "draft_id": simulation_run.draft_id,
                        "version": simulation_run.version,
                        "run_id": simulation_run.run_id,
                        "status": simulation_run.status,
                        "privacy_mode": simulation_run.privacy_mode,
                        "graph_id": simulation_run.graph_id,
                    }
                ),
            }
        ]
        relationships: List[Dict[str, Any]] = []
        artifacts = ["ReaderPersona", "PrivateReaction", "PlatformPost", "CrossReaction", "Report"]

        if report:
            report_node = {
                "label": "Report",
                "artifact_key": report.report_id,
                "namespace": namespace,
                "project_id": project.project_id,
                "properties": self._clean_properties(report.to_dict()),
            }
            nodes.append(report_node)
            relationships.append(self._rel("HAS_REPORT", "Draft", simulation_run.run_id, "Report", report.report_id, namespace))

        for persona in reader_personas:
            nodes.append(self._generic_node("ReaderPersona", persona.persona_id, namespace, project.project_id, persona.to_dict()))
            relationships.append(self._rel("HAS_PERSONA", "Draft", simulation_run.run_id, "ReaderPersona", persona.persona_id, namespace))
        for reaction in private_reactions:
            nodes.append(self._generic_node("PrivateReaction", reaction.reaction_id, namespace, project.project_id, reaction.to_dict()))
        for post in platform_posts:
            nodes.append(self._generic_node("PlatformPost", post.post_id, namespace, project.project_id, post.to_dict()))
        for cross in cross_reactions:
            nodes.append(self._generic_node("CrossReaction", cross.reaction_id, namespace, project.project_id, cross.to_dict()))

        return {"nodes": nodes, "relationships": relationships, "artifacts": artifacts}

    def _book_node(self, project_id: str, book_id: str, namespace: str, book_dna: BookDNA, evidence_pack: EvidencePack) -> Dict[str, Any]:
        return {
            "label": "Book",
            "artifact_key": self._book_key(project_id, book_id),
            "namespace": namespace,
            "project_id": project_id,
            "properties": self._clean_properties(
                {
                    "project_id": project_id,
                    "book_id": book_id,
                    "draft_id": evidence_pack.draft_id,
                    "version": evidence_pack.version,
                    "title": book_dna.title,
                    "premise": book_dna.premise,
                    "genre": book_dna.genre,
                    "book_type": book_dna.book_type,
                    "subgenre": book_dna.subgenre,
                    "tone": book_dna.tone,
                    "emotional_promise": book_dna.emotional_promise,
                    "narrative_engine": book_dna.narrative_engine,
                    "reading_difficulty": book_dna.reading_difficulty,
                    "target_reader": book_dna.target_reader,
                    "themes": book_dna.themes,
                    "comparable_titles": book_dna.comparable_titles,
                    "privacy_mode": evidence_pack.privacy_mode,
                    "confidence": evidence_pack.confidence,
                }
            ),
        }

    def _draft_node(self, project_id: str, book_id: str, namespace: str, evidence_pack: EvidencePack) -> Dict[str, Any]:
        manuscript = evidence_pack.manuscript_input
        return {
            "label": "Draft",
            "artifact_key": manuscript.input_id,
            "namespace": namespace,
            "project_id": project_id,
            "properties": self._clean_properties(
                {
                    "project_id": project_id,
                    "book_id": book_id,
                    "draft_id": evidence_pack.draft_id,
                    "version": evidence_pack.version,
                    "title": manuscript.title,
                    "filename": manuscript.filename,
                    "mime_type": manuscript.mime_type,
                    "privacy_mode": evidence_pack.privacy_mode,
                }
            ),
        }

    def _chapter_nodes(self, project_id: str, book_id: str, namespace: str, chapter_map: ChapterMap) -> List[Dict[str, Any]]:
        return [
            self._generic_node(
                "Chapter",
                chapter.chapter_id,
                namespace,
                project_id,
                {
                    "project_id": project_id,
                    "book_id": book_id,
                    "chapter_number": chapter.chapter_number,
                    "title": chapter.title,
                    "summary": chapter.summary,
                    "purpose": chapter.purpose,
                    "chapter_function": chapter.chapter_function,
                    "pacing": chapter.pacing,
                    "key_beats": chapter.key_beats,
                    "emotional_beats": chapter.emotional_beats,
                    "turning_points": chapter.turning_points,
                    "confidence": chapter.confidence,
                },
            )
            for chapter in chapter_map.chapters
        ]

    def _character_nodes(self, project_id: str, book_id: str, namespace: str, character_map: CharacterMap) -> List[Dict[str, Any]]:
        return [
            self._generic_node(
                "Character",
                character.character_id,
                namespace,
                project_id,
                {
                    "project_id": project_id,
                    "book_id": book_id,
                    "name": character.name,
                    "role": character.role,
                    "motivations": character.motivations,
                    "goals": character.goals,
                    "conflicts": character.conflicts,
                    "relationships": character.relationships,
                    "arc_summary": character.arc_summary,
                    "attachment_potential": character.attachment_potential,
                    "confidence": character.confidence,
                },
            )
            for character in character_map.characters
        ]

    def _claim_nodes(
        self,
        project_id: str,
        book_id: str,
        namespace: str,
        claim_map: ClaimMap,
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        claim_nodes: List[Dict[str, Any]] = []
        evidence_nodes: List[Dict[str, Any]] = []
        for claim in claim_map.claims:
            claim_nodes.append(
                self._generic_node(
                    "Claim",
                    claim.claim_id,
                    namespace,
                    project_id,
                    {
                        "project_id": project_id,
                        "book_id": book_id,
                        "claim_text": claim.claim_text,
                        "support_type": claim.support_type,
                        "support_quality": claim.support_quality,
                        "evidence_strength": claim.evidence_strength,
                        "examples": claim.examples,
                        "frameworks": claim.frameworks,
                        "promises": claim.promises,
                        "factual_risk_flags": claim.factual_risk_flags,
                        "counterarguments": claim.counterarguments,
                        "confidence": claim.confidence,
                    },
                )
            )
            for ref in claim.evidence_refs:
                evidence_nodes.append(
                    {
                        "label": "Evidence",
                        "artifact_key": self._artifact_key("claim_evidence", namespace, project_id, ref),
                        "namespace": namespace,
                        "project_id": project_id,
                        "claim_ref": claim.claim_id,
                        "properties": self._clean_properties(
                            {
                                "project_id": project_id,
                                "book_id": book_id,
                                "claim_id": claim.claim_id,
                                "reference": ref,
                            }
                        ),
                    }
                )
        return claim_nodes, evidence_nodes

    def _risk_nodes(self, project_id: str, book_id: str, namespace: str, risk_map: RiskMap) -> List[Dict[str, Any]]:
        return [
            self._generic_node(
                "Risk",
                risk.risk_id,
                namespace,
                project_id,
                {
                    "project_id": project_id,
                    "book_id": book_id,
                    "risk_type": risk.risk_type,
                    "severity": risk.severity,
                    "description": risk.description,
                    "affected_segments": risk.affected_segments,
                    "trigger_text": risk.trigger_text,
                    "mitigation_hint": risk.mitigation_hint,
                    "confidence": risk.confidence,
                },
            )
            for risk in risk_map.risks
        ]

    def _style_node(self, project_id: str, book_id: str, namespace: str, style_map: StyleMap) -> Dict[str, Any]:
        return self._generic_node(
            "StyleSignal",
            self._artifact_key("style", namespace, project_id, book_id),
            namespace,
            project_id,
            {
                "project_id": project_id,
                "book_id": book_id,
                "prose_density": style_map.prose_density,
                "clarity": style_map.clarity,
                "rhythm": style_map.rhythm,
                "voice_consistency": style_map.voice_consistency,
                "quoteability": style_map.quoteability,
                "accessibility": style_map.accessibility,
                "style_notes": style_map.style_notes,
                "confidence": style_map.confidence,
            },
        )

    def _market_node(self, project_id: str, book_id: str, namespace: str, market_surface: MarketSurface) -> Dict[str, Any]:
        return self._generic_node(
            "MarketSurface",
            self._artifact_key("market", namespace, project_id, book_id),
            namespace,
            project_id,
            {
                "project_id": project_id,
                "book_id": book_id,
                "target_segments": market_surface.target_segments,
                "comp_titles": market_surface.comp_titles,
                "positioning_summary": market_surface.positioning_summary,
                "discoverability_hooks": market_surface.discoverability_hooks,
                "packaging_expectations": market_surface.packaging_expectations,
                "promise_gap": market_surface.promise_gap,
                "audience_fit": market_surface.audience_fit,
                "confidence": market_surface.confidence,
            },
        )

    def _generic_node(self, label: str, artifact_key: str, namespace: str, project_id: str, props: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "label": label,
            "artifact_key": artifact_key,
            "namespace": namespace,
            "project_id": project_id,
            "properties": self._clean_properties(props),
        }

    def _rel(self, rel_type: str, source_label: str, source_key: str, target_label: str, target_key: str, namespace: str) -> Dict[str, Any]:
        return {
            "type": rel_type,
            "source_label": source_label,
            "source_key": source_key,
            "target_label": target_label,
            "target_key": target_key,
            "namespace": namespace,
            "updated_at": self._now(),
        }

    def _clean_properties(self, props: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in props.items():
            if value is None:
                continue
            if isinstance(value, (dict, list, tuple, set)):
                cleaned[key] = json.dumps(value, ensure_ascii=False)
            else:
                cleaned[key] = value
        cleaned["updated_at"] = self._now()
        return cleaned

    def _book_key(self, project_id: str, book_id: str) -> str:
        return f"book:{project_id}:{book_id}"

    def _artifact_key(self, kind: str, namespace: str, project_id: str, suffix: str) -> str:
        return f"{kind}:{namespace}:{project_id}:{suffix}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

