"""
MiroFish Backend - Flask Application Factory
"""

import os
import warnings

# Suppress multiprocessing resource_tracker warnings (from third-party libraries like transformers)
# Must be set before all other imports
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request
from flask_cors import CORS

from .config import Config
from .utils.logger import setup_logger, get_logger


def create_app(config_class=Config):
    """Flask application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure JSON encoding: ensure Chinese displays directly (not as \uXXXX)
    # Flask >= 2.3 uses app.json.ensure_ascii, older versions use JSON_AS_ASCII config
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False

    # Setup logging
    logger = setup_logger('mirofish')

    # Only print startup info in reloader subprocess (avoid printing twice in debug mode)
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process

    if should_log_startup:
        logger.info("=" * 50)
        logger.info("MiroFish-Offline Backend starting...")
        logger.info("=" * 50)

    # Enable CORS with configurable allowed origins (default: localhost dev servers)
    CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})

    # --- Initialize Neo4jStorage singleton (DI via app.extensions) ---
    from .storage import Neo4jStorage
    try:
        neo4j_storage = Neo4jStorage()
        app.extensions['neo4j_storage'] = neo4j_storage
        if should_log_startup:
            logger.info("Neo4jStorage initialized (connected to %s)", Config.NEO4J_URI)
    except Exception as e:
        logger.error("Neo4jStorage initialization failed: %s", e)
        # Store None so endpoints can return 503 gracefully
        app.extensions['neo4j_storage'] = None

    # Register simulation process cleanup function (ensure all simulation processes terminate on server shutdown)
    from .services.simulation_runner import SimulationRunner
    SimulationRunner.register_cleanup()
    if should_log_startup:
        logger.info("Simulation process cleanup function registered")

    # Register Neo4j driver cleanup on app context teardown to prevent connection leaks
    @app.teardown_appcontext
    def close_neo4j_driver(exception=None):
        """Close Neo4j driver connection when app context tears down."""
        neo4j_storage = app.extensions.get('neo4j_storage')
        if neo4j_storage is not None:
            try:
                neo4j_storage.close()
            except Exception:
                pass  # Driver may already be closed

    # Request logging middleware
    @app.before_request
    def log_request():
        logger = get_logger('mirofish.request')
        logger.debug(f"Request: {request.method} {request.path}")
        if request.content_type and 'json' in request.content_type:
            logger.debug(f"Request body: {request.get_json(silent=True)}")

    @app.after_request
    def log_response(response):
        logger = get_logger('mirofish.request')
        logger.debug(f"Response: {response.status_code}")
        return response

    # Register blueprints
    from .api import book_sim_bp, graph_bp, simulation_bp, report_bp
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(book_sim_bp, url_prefix='/api/book-sim')

    # Health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'MiroFish-Offline Backend'}

    # Legacy system health check with component status details
    @app.route('/api/health')
    def legacy_health():
        """Health check for the legacy MiroFish system with component status."""
        import platform
        import shutil

        neo4j_ok = False
        neo4j_error = None
        neo4j_storage = app.extensions.get('neo4j_storage')
        if neo4j_storage:
            try:
                driver = getattr(neo4j_storage, '_driver', None)
                if driver:
                    driver.verify_connectivity()
                    neo4j_ok = True
            except Exception as e:
                neo4j_error = str(e)

        # Check disk space
        backend_dir = os.path.dirname(__file__)
        try:
            disk = shutil.disk_usage(backend_dir)
            disk_info = {
                "total_gb": round(disk.total / (1024 ** 3), 1),
                "free_gb": round(disk.free / (1024 ** 3), 1),
                "used_percent": round(disk.used / disk.total * 100, 1),
            }
        except Exception:
            disk_info = {"error": "Unable to determine disk usage"}

        return jsonify({
            "status": "ok" if neo4j_ok else "degraded",
            "service": "MiroFish-Offline Backend",
            "python_version": platform.python_version(),
            "neo4j": {"ok": neo4j_ok, "error": neo4j_error},
            "disk": disk_info,
        })

    if should_log_startup:
        logger.info("MiroFish-Offline Backend startup complete")

    return app

