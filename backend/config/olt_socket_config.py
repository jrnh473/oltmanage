import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv

from models.olt_models import db
from routes.olt_routes import olt_bp

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def init_olt_app(app: Flask):

    # =========================
    # DATABASE INIT
    # =========================
    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ DB Error: {e}")

    # =========================
    # CORS CONFIG
    # =========================
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://10.100.93.129:3000",
                os.getenv("FRONTEND_URL", "*")
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # =========================
    # SOCKET.IO INIT (IMPORTANT FIX)
    # =========================
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        ping_timeout=60,
        ping_interval=25
    )

    # =========================
    # IMPORT EVENTS (NO CIRCULAR IMPORT)
    # =========================
    from services.socketio_events import register_socketio_events
    register_socketio_events(socketio)

    # =========================
    # ROUTES
    # =========================
    app.register_blueprint(olt_bp)

    # =========================
    # HEALTH CHECK
    # =========================
    @app.route("/api/health", methods=["GET"])
    def health():
        return {
            "status": "ok",
            "service": "OLT Management System"
        }

    # =========================
    # ERROR HANDLERS
    # =========================
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not Found"}, 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(str(e))
        return {"error": "Internal Server Error"}, 500

    logger.info("🚀 OLT System Initialized")

    return socketio