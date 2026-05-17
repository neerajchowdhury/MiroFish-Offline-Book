"""Additive Swarmbook API routes."""

from __future__ import annotations

import traceback

from flask import jsonify, request

from . import book_sim_bp
from ..book_sim.interrogation import PersonaInterrogator
from ..book_sim.models import EvidencePack, SimulationRun
from ..utils.logger import get_logger


logger = get_logger("mirofish.api.book_sim")


@book_sim_bp.route("/interrogate", methods=["POST"])
def interrogate_persona():
    """Answer a grounded question from one simulated reader persona."""
    try:
        payload = request.get_json() or {}
        persona_id = str(payload.get("persona_id", "")).strip()
        question = str(payload.get("question", "")).strip()
        simulation_run_payload = payload.get("simulation_run")
        evidence_pack_payload = payload.get("evidence_pack")

        if not persona_id:
            return jsonify({"success": False, "error": "Please provide persona_id"}), 400
        if not question:
            return jsonify({"success": False, "error": "Please provide question"}), 400
        if not isinstance(simulation_run_payload, dict):
            return jsonify({"success": False, "error": "Please provide simulation_run"}), 400
        if not isinstance(evidence_pack_payload, dict):
            return jsonify({"success": False, "error": "Please provide evidence_pack"}), 400

        simulation_run = SimulationRun.from_dict(simulation_run_payload)
        evidence_pack = EvidencePack.from_dict(evidence_pack_payload)
        result = PersonaInterrogator().interrogate(
            simulation_run=simulation_run,
            evidence_pack=evidence_pack,
            persona_id=persona_id,
            question=question,
        )
        return jsonify({"success": True, "data": result.to_dict()})

    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - defensive API guard
        logger.error("Book-sim interrogation failed: %s", exc)
        return jsonify({
            "success": False,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }), 500
