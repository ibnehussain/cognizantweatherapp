"""
app.py — Flask application entry point.
Creates and configures the Flask app, registers blueprints,
enables CORS, and serves the frontend static files.
"""

import logging
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config, validate_config
from routes.weather import weather_bp

# ─── Logging ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_app(config_class: type = Config) -> Flask:
    """
    Application factory.
    Creates, configures, and returns the Flask application instance.
    """
    cfg = config_class()
    validate_config(cfg)

    app = Flask(
        __name__,
        static_folder="../frontend",    # serve index.html + assets
        static_url_path="",
    )

    # ── Load config into app ──────────────────────────────────
    app.config["SECRET_KEY"]         = cfg.SECRET_KEY
    app.config["DEBUG"]              = cfg.DEBUG
    app.config["OWM_API_KEY"]        = cfg.OWM_API_KEY
    app.config["OWM_BASE_URL"]       = cfg.OWM_BASE_URL
    app.config["OWM_TIMEOUT"]        = cfg.OWM_TIMEOUT
    app.config["CACHE_TTL_SECONDS"]  = cfg.CACHE_TTL_SECONDS

    # ── CORS ──────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": cfg.CORS_ORIGINS}})

    # ── Blueprints ────────────────────────────────────────────
    app.register_blueprint(weather_bp)

    # ── Serve frontend ────────────────────────────────────────
    @app.get("/")
    def serve_index():
        return send_from_directory(app.static_folder, "index.html")

    # ── Health check ──────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return {"status": "ok"}, 200

    logger.info("WeatherDash app created. Debug=%s", cfg.DEBUG)
    return app


# ─── Run directly (development only) ─────────────────────────
if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=flask_app.config["DEBUG"])
