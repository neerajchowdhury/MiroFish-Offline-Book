"""Deterministic Swarmbook simulation orchestration."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Optional

from ..graph_persistence import BookGraphPersistence
from ..local_cache import LocalArtifactCache
from ..models import BookProject, EvidencePack, SimulationRun
from ..provider_router import BookSimProviderRouter
from ..reader_persona_generator import PersonaGenerationOverrides, ReaderPersonaGenerator
from .cross_reaction_pass import CrossReactionPass
from .platform_reaction_pass import PlatformReactionPass
from .private_reading_pass import PrivateReadingPass


class SimulationOrchestrator:
    """Run the private, platform, and cross-reaction passes in order."""

    def __init__(
        self,
        persona_generator: Optional[ReaderPersonaGenerator] = None,
        cache: Optional[LocalArtifactCache] = None,
        graph_persistence: Optional[BookGraphPersistence] = None,
        model_router: Optional[BookSimProviderRouter] = None,
        cross_reaction_posts: int = 8,
        max_reaction_rounds: int = 2,
        max_parallel_jobs: int = 1,
    ) -> None:
        self.cache = cache or LocalArtifactCache()
        self.model_router = model_router
        self.persona_generator = persona_generator or ReaderPersonaGenerator(model_router=model_router)
        self.private_pass = PrivateReadingPass(cache=self.cache)
        self.platform_pass = PlatformReactionPass(cache=self.cache, model_router=model_router)
        self.cross_pass = CrossReactionPass(
            cache=self.cache,
            cross_reaction_posts=cross_reaction_posts,
            max_reaction_rounds=max_reaction_rounds,
        )
        self.graph_persistence = graph_persistence
        self.cross_reaction_posts = cross_reaction_posts
        self.max_reaction_rounds = max_reaction_rounds
        self.max_parallel_jobs = max_parallel_jobs

    def run(
        self,
        project: BookProject,
        evidence_pack: EvidencePack,
        simulation_seed: Optional[int] = None,
        persona_overrides: Optional[PersonaGenerationOverrides] = None,
    ) -> SimulationRun:
        simulation_id = self._simulation_id(project.project_id, evidence_pack.pack_id, simulation_seed)
        cache_key = self._cache_key(project, evidence_pack, simulation_seed, persona_overrides)
        cached = self.cache.get_json("simulation_orchestrator", cache_key)
        if cached:
            return SimulationRun.from_dict(cached["simulation_run"])

        started_at = datetime.now().isoformat()
        personas = self.persona_generator.generate(
            book_type=evidence_pack.book_dna.book_type if evidence_pack.book_dna else "mixed_unknown",
            privacy_mode=evidence_pack.privacy_mode,
            simulation_seed=simulation_seed,
            overrides=persona_overrides,
        )
        private_reactions = self.private_pass.run(
            personas=personas,
            evidence_pack=evidence_pack,
            simulation_id=simulation_id,
            simulation_seed=simulation_seed,
        )
        platform_posts = self.platform_pass.run(
            personas=personas,
            private_reactions=private_reactions,
            evidence_pack=evidence_pack,
            simulation_id=simulation_id,
            round_number=1,
            privacy_mode=evidence_pack.privacy_mode,
            simulation_seed=simulation_seed,
        )

        current_private = private_reactions
        all_cross_reactions = []
        for round_number in range(1, self.max_reaction_rounds + 1):
            cross_reactions, current_private = self.cross_pass.run(
                personas=personas,
                private_reactions=current_private,
                platform_posts=platform_posts,
                simulation_id=simulation_id,
                simulation_seed=simulation_seed,
                round_number=round_number,
            )
            all_cross_reactions.extend(cross_reactions)

        simulation_run = SimulationRun(
            run_id=simulation_id,
            project_id=project.project_id,
            privacy_mode=evidence_pack.privacy_mode,
            draft_id=evidence_pack.draft_id,
            version=evidence_pack.version,
            provider_route="local_ollama" if evidence_pack.privacy_mode == "local_only" else None,
            status="completed",
            started_at=started_at,
            ended_at=datetime.now().isoformat(),
            total_rounds=self.max_reaction_rounds,
            current_round=self.max_reaction_rounds,
            personas_count=len(personas),
            reactions_count=len(current_private),
            posts_count=len(platform_posts),
            reader_personas=list(personas),
            private_reactions=current_private,
            platform_posts=platform_posts,
            cross_reactions=all_cross_reactions,
            evidence_refs=list(dict.fromkeys(evidence_pack.evidence_refs + [evidence_pack.pack_id])),
            confidence=evidence_pack.confidence,
            metadata={
                "cross_reaction_posts": self.cross_reaction_posts,
                "max_reaction_rounds": self.max_reaction_rounds,
                # Intentionally fixed to 1 by default to prevent local CPU overcommit.
                "max_parallel_jobs": self.max_parallel_jobs,
            },
        )

        if self.graph_persistence:
            self.graph_persistence.persist_simulation_artifacts(
                project=project,
                simulation_run=simulation_run,
                reader_personas=personas,
                private_reactions=current_private,
                platform_posts=platform_posts,
                cross_reactions=all_cross_reactions,
            )

        self.cache.set_json(
            "simulation_orchestrator",
            cache_key,
            {"simulation_run": simulation_run.to_dict()},
        )
        return simulation_run

    def _simulation_id(self, project_id: str, pack_id: str, simulation_seed: Optional[int]) -> str:
        digest = hashlib.sha256(
            json.dumps(
                {"project_id": project_id, "pack_id": pack_id, "simulation_seed": simulation_seed},
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        return f"sim_{digest[:12]}"

    def _cache_key(
        self,
        project: BookProject,
        evidence_pack: EvidencePack,
        simulation_seed: Optional[int],
        persona_overrides: Optional[PersonaGenerationOverrides],
    ) -> str:
        payload = {
            "project": project.to_dict(),
            "evidence_pack": evidence_pack.to_dict(),
            "simulation_seed": simulation_seed,
            "persona_overrides": persona_overrides.__dict__ if persona_overrides else {},
            "cross_reaction_posts": self.cross_reaction_posts,
            "max_reaction_rounds": self.max_reaction_rounds,
            "max_parallel_jobs": self.max_parallel_jobs,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
