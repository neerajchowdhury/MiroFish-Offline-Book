"""Entity reading endpoints for simulation API."""

from flask import request, jsonify, current_app

from . import simulation_bp
from .._legacy_error_handler import legacy_api_route
from ...services.entity_reader import EntityReader
from ...utils.logger import get_logger

logger = get_logger('mirofish.api.simulation')


@simulation_bp.route('/entities/<graph_id>', methods=['GET'])
@legacy_api_route
def get_graph_entities(graph_id: str):
    """Get all entities from the knowledge graph (filtered)."""
    try:
        entity_types_str = request.args.get('entity_types', '')
        entity_types = [t.strip() for t in entity_types_str.split(',') if t.strip()] if entity_types_str else None
        enrich = request.args.get('enrich', 'true').lower() == 'true'

        logger.info(f"Get knowledge graph entities: graph_id={graph_id}, entity_types={entity_types}, enrich={enrich}")

        storage = current_app.extensions.get('neo4j_storage')
        if not storage:
            raise ValueError("GraphStorage not initialized")
        reader = EntityReader(storage)
        result = reader.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=entity_types,
            enrich_with_edges=enrich
        )

        return jsonify({
            "success": True,
            "data": result.to_dict()
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@simulation_bp.route('/entities/<graph_id>/<entity_uuid>', methods=['GET'])
@legacy_api_route
def get_entity_detail(graph_id: str, entity_uuid: str):
    """Get detailed information of a single entity."""
    try:
        storage = current_app.extensions.get('neo4j_storage')
        if not storage:
            raise ValueError("GraphStorage not initialized")
        reader = EntityReader(storage)
        entity = reader.get_entity_with_context(graph_id, entity_uuid)

        if not entity:
            return jsonify({
                "success": False,
                "error": f"Entity does not exist: {entity_uuid}"
            }), 404

        return jsonify({
            "success": True,
            "data": entity.to_dict()
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@simulation_bp.route('/entities/<graph_id>/by-type/<entity_type>', methods=['GET'])
@legacy_api_route
def get_entities_by_type(graph_id: str, entity_type: str):
    """Get all entities of specified type."""
    try:
        enrich = request.args.get('enrich', 'true').lower() == 'true'

        storage = current_app.extensions.get('neo4j_storage')
        if not storage:
            raise ValueError("GraphStorage not initialized")
        reader = EntityReader(storage)
        entities = reader.get_entities_by_type(
            graph_id=graph_id,
            entity_type=entity_type,
            enrich_with_edges=enrich
        )

        return jsonify({
            "success": True,
            "data": {
                "entity_type": entity_type,
                "count": len(entities),
                "entities": [e.to_dict() for e in entities]
            }
        })

    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
