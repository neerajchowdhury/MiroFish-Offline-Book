"""Grounded reader-persona interrogation for completed Swarmbook simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ..models import (
    CrossReaction,
    EvidencePack,
    JsonDataclassMixin,
    PlatformPost,
    PrivateReaderReaction,
    ReaderPersona,
    SimulationRun,
)


@dataclass(frozen=True)
class GroundedPoint:
    """One answer ingredient tied to specific evidence references."""

    text: str
    refs: List[str] = field(default_factory=list)


@dataclass
class PersonaInterrogationResult(JsonDataclassMixin):
    """Structured reply from a simulated reader persona."""

    persona_id: str
    question: str
    intent: str
    answer: str
    review_style: str
    based_on: List[str] = field(default_factory=list)
    artifact_ids: Dict[str, List[str]] = field(default_factory=dict)
    signals: Dict[str, object] = field(default_factory=dict)
    confidence: Optional[float] = None


@dataclass(frozen=True)
class PersonaArtifactBundle:
    """Artifacts needed to interrogate one persona after a simulation."""

    persona: ReaderPersona
    private_reaction: PrivateReaderReaction
    platform_posts: Sequence[PlatformPost]
    cross_reactions: Sequence[CrossReaction]
    evidence_pack: EvidencePack


class PersonaInterrogator:
    """Answer reader questions without inventing details beyond stored artifacts."""

    def interrogate(
        self,
        simulation_run: SimulationRun,
        evidence_pack: EvidencePack,
        persona_id: str,
        question: str,
    ) -> PersonaInterrogationResult:
        prompt = (question or "").strip()
        if not prompt:
            raise ValueError("question is required")

        bundle = self._bundle_for_persona(simulation_run, evidence_pack, persona_id)
        intent = self._classify_intent(prompt)

        if intent == "rating_why":
            answer, points = self._answer_rating(bundle)
        elif intent == "dnf_why":
            answer, points = self._answer_dnf(bundle)
        elif intent == "raise_rating":
            answer, points = self._answer_raise_rating(bundle)
        elif intent == "recommend":
            answer, points = self._answer_recommend(bundle)
        elif intent == "audience_fit":
            answer, points = self._answer_audience_fit(bundle, simulation_run.reader_personas)
        elif intent == "trigger_reaction":
            answer, points = self._answer_triggers(bundle)
        else:
            answer, points = self._answer_generic(bundle)

        based_on = self._collect_refs(points, bundle.persona.evidence_refs, bundle.private_reaction.evidence_refs)
        return PersonaInterrogationResult(
            persona_id=bundle.persona.persona_id,
            question=prompt,
            intent=intent,
            answer=answer,
            review_style=bundle.persona.review_style,
            based_on=based_on,
            artifact_ids={
                "private_reaction_ids": [bundle.private_reaction.reaction_id],
                "platform_post_ids": [post.post_id for post in bundle.platform_posts],
                "cross_reaction_ids": [item.reaction_id for item in bundle.cross_reactions],
            },
            signals=self._signals(bundle),
            confidence=self._confidence(bundle),
        )

    def _bundle_for_persona(
        self,
        simulation_run: SimulationRun,
        evidence_pack: EvidencePack,
        persona_id: str,
    ) -> PersonaArtifactBundle:
        persona = next((item for item in simulation_run.reader_personas if item.persona_id == persona_id), None)
        if persona is None:
            raise ValueError(f"Unknown persona_id: {persona_id}")

        private_reaction = next((item for item in simulation_run.private_reactions if item.persona_id == persona_id), None)
        if private_reaction is None:
            raise ValueError(f"Missing private reaction for persona_id: {persona_id}")

        platform_posts = [item for item in simulation_run.platform_posts if item.persona_id == persona_id]
        cross_reactions = [item for item in simulation_run.cross_reactions if item.persona_id == persona_id]
        return PersonaArtifactBundle(
            persona=persona,
            private_reaction=private_reaction,
            platform_posts=platform_posts,
            cross_reactions=cross_reactions,
            evidence_pack=evidence_pack,
        )

    def _classify_intent(self, question: str) -> str:
        normalized = question.lower()
        if "dnf" in normalized or "didn't finish" in normalized or "did not finish" in normalized:
            return "dnf_why"
        if "raise" in normalized or "higher rating" in normalized or "go higher" in normalized:
            return "raise_rating"
        if "recommend" in normalized:
            return "recommend"
        if "which reader" in normalized or "who would love" in normalized or "who would hate" in normalized:
            return "audience_fit"
        if "trigger" in normalized or "what exactly" in normalized:
            return "trigger_reaction"
        if "rate" in normalized or "rating" in normalized or "stars" in normalized:
            return "rating_why"
        return "generic"

    def _answer_rating(self, bundle: PersonaArtifactBundle) -> Tuple[str, List[GroundedPoint]]:
        reaction = bundle.private_reaction
        praise = self._praise_points(bundle)
        friction = self._friction_points(bundle)
        peer = self._peer_points(bundle)
        rating = reaction.rating if reaction.rating is not None else 0.0
        answer = self._style_text(
            bundle.persona.review_style,
            (
                f"I landed at {rating:.2f} stars because {self._join_point_texts(praise[:2], 'the upside was hard to ignore')} "
                f"but {self._join_point_texts(friction[:2], 'the drag kept me from going higher')}."
            ),
            (
                f"The private reaction was {reaction.sentiment or 'mixed'}, and the score stayed bounded by "
                f"confusion at {self._score_text(reaction.confusion_score)} plus recommendation pull at "
                f"{self._score_text(reaction.recommendation_probability)}."
            ),
            self._peer_clause(peer),
        )
        return answer, praise + friction + peer

    def _answer_dnf(self, bundle: PersonaArtifactBundle) -> Tuple[str, List[GroundedPoint]]:
        reaction = bundle.private_reaction
        friction = self._friction_points(bundle)
        threshold = max(0.5, bundle.persona.dnf_threshold)
        likely_dnf = (reaction.dnf_probability or 0.0) >= threshold
        answer = self._style_text(
            bundle.persona.review_style,
            (
                f"{'I was in DNF territory' if likely_dnf else 'I was not a clean DNF, but I felt DNF pressure'} "
                f"because {self._join_point_texts(friction[:3], 'the stored friction signals stacked up')}."
            ),
            (
                f"The main pressure came from confusion at {self._score_text(reaction.confusion_score)} and a DNF probability of "
                f"{self._score_text(reaction.dnf_probability)} against my threshold of {bundle.persona.dnf_threshold:.2f}."
            ),
            "I am not claiming an unseen scene-level trigger beyond those stored signals.",
        )
        return answer, friction

    def _answer_raise_rating(self, bundle: PersonaArtifactBundle) -> Tuple[str, List[GroundedPoint]]:
        improvements = self._improvement_points(bundle)
        praise = self._praise_points(bundle)
        answer = self._style_text(
            bundle.persona.review_style,
            (
                f"My rating would rise if the draft solved {self._join_point_texts(improvements[:3], 'the main resistance points')}."
            ),
            (
                f"The book already has some lift from {self._join_point_texts(praise[:2], 'its stronger signals')}, "
                f"so tightening the drag points would matter more than rewriting the whole identity."
            ),
        )
        return answer, improvements + praise

    def _answer_recommend(self, bundle: PersonaArtifactBundle) -> Tuple[str, List[GroundedPoint]]:
        reaction = bundle.private_reaction
        recommendation_probability = reaction.recommendation_probability or 0.0
        stance = "yes" if recommendation_probability >= 0.68 else "maybe" if recommendation_probability >= 0.42 else "no"
        segments = self._segment_points(bundle)
        answer = self._style_text(
            bundle.persona.review_style,
            (
                f"I would {'recommend it' if stance == 'yes' else 'recommend it selectively' if stance == 'maybe' else 'be cautious recommending it'}, "
                f"because my recommendation signal sits at {self._score_text(recommendation_probability)}."
            ),
            (
                f"The best fit looks like {self._join_point_texts(segments[:2], 'readers who match the stored market and taste signals')}, "
                f"while readers sensitive to {self._join_point_texts(self._friction_points(bundle)[:2], 'those pressure points')} will bounce faster."
            ),
        )
        return answer, segments + self._friction_points(bundle)

    def _answer_audience_fit(
        self,
        bundle: PersonaArtifactBundle,
        personas: Sequence[ReaderPersona],
    ) -> Tuple[str, List[GroundedPoint]]:
        love_points, hate_points = self._audience_points(bundle, personas)
        answer = self._style_text(
            bundle.persona.review_style,
            (
                f"The likeliest love-it readers are {self._join_point_texts(love_points[:2], 'the readers whose tastes line up with the upside')}."
            ),
            (
                f"The likeliest hate-it or early-exit readers are {self._join_point_texts(hate_points[:2], 'the readers whose triggers line up with the drag')}."
            ),
        )
        return answer, love_points + hate_points

    def _answer_triggers(self, bundle: PersonaArtifactBundle) -> Tuple[str, List[GroundedPoint]]:
        praise = self._praise_points(bundle)
        friction = self._friction_points(bundle)
        peer = self._peer_points(bundle)
        answer = self._style_text(
            bundle.persona.review_style,
            (
                f"The clearest triggers were {self._join_point_texts((praise + friction)[:4], 'the stored reaction signals')}."
            ),
            (
                f"If you want the exact boundaries, I am grounding this in private praise/friction, public post payloads, "
                f"and peer-reaction shifts instead of inventing extra manuscript detail."
            ),
            self._peer_clause(peer),
        )
        return answer, praise + friction + peer

    def _answer_generic(self, bundle: PersonaArtifactBundle) -> Tuple[str, List[GroundedPoint]]:
        points = self._praise_points(bundle) + self._friction_points(bundle)
        answer = self._style_text(
            bundle.persona.review_style,
            (
                f"My read comes down to {self._join_point_texts(points[:4], 'a mixed set of stored signals')}."
            ),
            "If you want a sharper answer, ask about the rating, DNF pressure, recommendation fit, or exact triggers.",
        )
        return answer, points

    def _praise_points(self, bundle: PersonaArtifactBundle) -> List[GroundedPoint]:
        reaction = bundle.private_reaction
        persona = bundle.persona
        pack = bundle.evidence_pack
        points = [GroundedPoint(f"private praise around {item}", reaction.evidence_refs) for item in reaction.praise if item]
        points.extend(GroundedPoint(f"taste-match for {item}", persona.evidence_refs) for item in persona.delight_triggers[:2] if item)
        if pack.book_dna:
            points.extend(GroundedPoint(f"theme signal around {item}", pack.book_dna.evidence_refs) for item in pack.book_dna.themes[:2] if item)
        if pack.market_surface:
            points.extend(
                GroundedPoint(f"market hook around {item}", pack.market_surface.evidence_refs)
                for item in pack.market_surface.discoverability_hooks[:1]
                if item
            )
        if reaction.notable_quotes:
            points.extend(GroundedPoint(f"quote-level pull from '{item}'", reaction.evidence_refs) for item in reaction.notable_quotes[:1] if item)
        return self._dedupe_points(points)

    def _friction_points(self, bundle: PersonaArtifactBundle) -> List[GroundedPoint]:
        reaction = bundle.private_reaction
        persona = bundle.persona
        pack = bundle.evidence_pack
        points = [GroundedPoint(f"private friction around {item}", reaction.evidence_refs) for item in reaction.friction if item]
        points.extend(GroundedPoint(f"personal DNF trigger around {item}", persona.evidence_refs) for item in persona.dnf_triggers[:2] if item)
        if pack.risk_map:
            for risk in pack.risk_map.risks[:3]:
                label = risk.description or risk.risk_type
                points.append(GroundedPoint(f"risk signal around {label}", risk.evidence_refs or pack.risk_map.evidence_refs))
        if pack.chapter_map:
            for chapter in pack.chapter_map.chapters[:2]:
                for item in chapter.likely_reader_friction[:1]:
                    points.append(GroundedPoint(f"chapter-level friction around {item}", chapter.evidence_refs))
        return self._dedupe_points(points)

    def _peer_points(self, bundle: PersonaArtifactBundle) -> List[GroundedPoint]:
        points: List[GroundedPoint] = []
        for item in bundle.cross_reactions[:2]:
            if item.stance_shift and item.stance_shift != "stable":
                points.append(
                    GroundedPoint(
                        f"peer feedback shifted me {item.stance_shift.replace('_', ' ')}",
                        item.evidence_refs,
                    )
                )
        for post in bundle.platform_posts[:2]:
            title = post.title or post.payload.get("review_title") or post.payload.get("hook_line") or post.platform
            points.append(GroundedPoint(f"my public framing on {post.platform} centered '{title}'", post.evidence_refs))
        return self._dedupe_points(points)

    def _improvement_points(self, bundle: PersonaArtifactBundle) -> List[GroundedPoint]:
        persona = bundle.persona
        pack = bundle.evidence_pack
        improvements: List[GroundedPoint] = []
        for item in bundle.private_reaction.friction[:3]:
            suggestion = self._fix_for_signal(item)
            improvements.append(GroundedPoint(suggestion, bundle.private_reaction.evidence_refs))
        for item in persona.dnf_triggers[:2]:
            improvements.append(GroundedPoint(self._fix_for_signal(item), persona.evidence_refs))
        if pack.risk_map:
            for risk in pack.risk_map.risks[:2]:
                suggestion = risk.mitigation_hint or self._fix_for_signal(risk.risk_type)
                improvements.append(GroundedPoint(suggestion, risk.evidence_refs or pack.risk_map.evidence_refs))
        if pack.style_map and pack.style_map.style_notes:
            improvements.append(
                GroundedPoint(
                    f"keep the existing style strengths like {pack.style_map.style_notes[0]} while trimming drag elsewhere",
                    pack.style_map.evidence_refs,
                )
            )
        return self._dedupe_points(improvements)

    def _segment_points(self, bundle: PersonaArtifactBundle) -> List[GroundedPoint]:
        persona = bundle.persona
        pack = bundle.evidence_pack
        points = [GroundedPoint(f"readers who want {item}", persona.evidence_refs) for item in persona.favorite_genres[:2] if item]
        if pack.market_surface:
            points.extend(
                GroundedPoint(f"segment fit for {item}", pack.market_surface.evidence_refs)
                for item in pack.market_surface.target_segments[:3]
                if item
            )
        return self._dedupe_points(points)

    def _audience_points(
        self,
        bundle: PersonaArtifactBundle,
        personas: Sequence[ReaderPersona],
    ) -> Tuple[List[GroundedPoint], List[GroundedPoint]]:
        current = bundle.persona
        others = [item for item in personas if item.persona_id != current.persona_id]
        love_scored: List[Tuple[float, GroundedPoint]] = []
        hate_scored: List[Tuple[float, GroundedPoint]] = []

        friction_terms = {item.lower() for item in bundle.private_reaction.friction + current.dnf_triggers if item}
        praise_terms = {item.lower() for item in bundle.private_reaction.praise + current.delight_triggers if item}

        for persona in others:
            taste_overlap = len({item.lower() for item in persona.favorite_genres if item} & praise_terms)
            hate_overlap = len({item.lower() for item in persona.disliked_patterns + persona.dnf_triggers if item} & friction_terms)
            love_score = taste_overlap + persona.influence_weight + (persona.rating_bias * 0.2)
            hate_score = hate_overlap + (1.0 - persona.dnf_threshold)
            love_scored.append((love_score, GroundedPoint(f"{persona.display_name} ({persona.review_style})", persona.evidence_refs)))
            hate_scored.append((hate_score, GroundedPoint(f"{persona.display_name} ({persona.review_style})", persona.evidence_refs)))

        if not love_scored and bundle.evidence_pack.market_surface:
            love_scored.extend(
                (1.0, GroundedPoint(f"{item}", bundle.evidence_pack.market_surface.evidence_refs))
                for item in bundle.evidence_pack.market_surface.target_segments[:2]
            )
        if not hate_scored:
            hate_scored.extend((1.0, point) for point in self._friction_points(bundle)[:2])

        love_points = [item for _, item in sorted(love_scored, key=lambda entry: entry[0], reverse=True)[:2]]
        hate_points = [item for _, item in sorted(hate_scored, key=lambda entry: entry[0], reverse=True)[:2]]
        return self._dedupe_points(love_points), self._dedupe_points(hate_points)

    def _style_text(self, review_style: str, *parts: str) -> str:
        content = " ".join(part.strip() for part in parts if part and part.strip())
        if not content:
            return ""

        if review_style == "critical_balanced":
            return content
        if review_style == "genre_defense":
            return f"From a genre-expectation angle, {content}"
        if review_style == "emotional_confessional":
            return f"My gut reaction was this: {content}"
        if review_style == "trope_driven":
            return f"For me this lives or dies on the trope signals, and {content}"
        if review_style == "analytical_skeptical":
            return f"My read is signal-based: {content}"
        if review_style == "taxonomy_focused":
            return f"In category terms, {content}"
        if review_style == "aesthetic_curated":
            return f"The vibe matters here, and {content}"
        if review_style == "punchy_polarized":
            return f"Short version: {content}"
        if review_style == "pragmatic_plainspoken":
            return f"Plainly: {content}"
        if review_style == "reflective_critical":
            return f"What I kept returning to was this: {content}"
        if review_style == "utility_focused":
            return f"From a usefulness standpoint, {content}"
        if review_style == "source_auditor":
            return f"From an evidence-and-support standpoint, {content}"
        return content

    def _peer_clause(self, points: Sequence[GroundedPoint]) -> str:
        if not points:
            return ""
        return f"Peer spillover also mattered: {self._join_point_texts(points[:2], 'other readers did not materially move me')}."

    def _join_point_texts(self, points: Sequence[GroundedPoint], fallback: str) -> str:
        texts = [item.text for item in points if item.text]
        if not texts:
            return fallback
        if len(texts) == 1:
            return texts[0]
        if len(texts) == 2:
            return f"{texts[0]} and {texts[1]}"
        return f"{', '.join(texts[:-1])}, and {texts[-1]}"

    def _fix_for_signal(self, signal: str) -> str:
        normalized = signal.lower().replace("-", "_").strip()
        fixes = {
            "slow_start": "opening with a faster hook or earlier consequence",
            "padding": "cutting repetition and compressing the middle",
            "pacing_drag": "tightening pacing where momentum sags",
            "confusing_worldbuilding": "clarifying the world rules earlier",
            "logic_gap": "making the causal chain more explicit",
            "thin_support": "adding firmer support for the central claims",
            "unclear_scope": "narrowing the scope so the promises feel defensible",
        }
        return fixes.get(normalized, f"reducing the drag around {signal}")

    def _signals(self, bundle: PersonaArtifactBundle) -> Dict[str, object]:
        reaction = bundle.private_reaction
        return {
            "rating": reaction.rating,
            "dnf_probability": reaction.dnf_probability,
            "recommendation_probability": reaction.recommendation_probability,
            "sentiment": reaction.sentiment,
            "praise": list(reaction.praise),
            "friction": list(reaction.friction),
            "peer_shifts": [item.stance_shift for item in bundle.cross_reactions if item.stance_shift],
        }

    def _confidence(self, bundle: PersonaArtifactBundle) -> Optional[float]:
        values = [
            bundle.persona.confidence,
            bundle.private_reaction.confidence,
            bundle.evidence_pack.confidence,
        ]
        scores = [float(value) for value in values if value is not None]
        if not scores:
            return None
        return round(sum(scores) / len(scores), 3)

    def _collect_refs(self, points: Sequence[GroundedPoint], *extra_groups: Sequence[str]) -> List[str]:
        refs: List[str] = []
        for point in points:
            refs.extend(point.refs)
        for group in extra_groups:
            refs.extend(group)
        return self._unique(refs)

    def _dedupe_points(self, points: Sequence[GroundedPoint]) -> List[GroundedPoint]:
        seen = set()
        result: List[GroundedPoint] = []
        for point in points:
            key = point.text.strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            result.append(GroundedPoint(point.text, self._unique(point.refs)))
        return result

    def _score_text(self, value: Optional[float]) -> str:
        if value is None:
            return "unknown"
        return f"{value:.2f}"

    def _unique(self, values: Sequence[str]) -> List[str]:
        seen = set()
        result: List[str] = []
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result
