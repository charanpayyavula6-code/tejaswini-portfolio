import time
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from common.config import (
    SQLALCHEMY_DATABASE_URI,
    SECRET_KEY,
    CORS_ORIGINS,
    FLASK_HOST,
    FLASK_PORT
)
from common.logger import setup_logger
from flask_gateway.database import db, seed_initial_data
from flask_gateway.routes.health import health_bp
from flask_gateway.routes.api_portfolio import api_portfolio_bp
from flask_gateway.routes.api_contact import api_contact_bp
from flask_gateway.routes.api_attendance import api_attendance_bp
from flask_gateway.routes.api_analytics import api_analytics_bp
from flask_gateway.routes.api_admin import api_admin_bp

logger = setup_logger("FlaskGatewayApp")

# Root directory containing frontend assets (index.html, admin.html, styles.css, script.js)
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent

def create_app() -> Flask:
    """Application factory for Flask API Gateway & Unified Web Server."""
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path=""
    )
    
    # Configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["JSON_SORT_KEYS"] = False
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}}, supports_credentials=True)
    
    # Initialize Database & Seed initial tables
    db.init_app(app)
    with app.app_context():
        db.create_all()
        seed_initial_data()
        logger.info(f"SQLite database initialized and seeded at: {SQLALCHEMY_DATABASE_URI}")
        
    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(api_portfolio_bp)
    app.register_blueprint(api_contact_bp)
    app.register_blueprint(api_attendance_bp)
    app.register_blueprint(api_analytics_bp)
    app.register_blueprint(api_admin_bp)
    
    # Request Timing Hooks
    @app.before_request
    def record_start_time():
        request.start_time = time.time()
        
    @app.after_request
    def append_telemetry_headers(response):
        if hasattr(request, "start_time"):
            elapsed_ms = (time.time() - request.start_time) * 1000.0
            response.headers["X-Gateway-Latency-Ms"] = f"{elapsed_ms:.2f}"
        return response
        
    # Serve Frontend Portfolio Homepage
    @app.route("/", methods=["GET"])
    def serve_frontend():
        return send_from_directory(str(FRONTEND_DIR), "index.html")

    # Serve Admin Dashboard UI
    @app.route("/admin", methods=["GET"])
    @app.route("/admin.html", methods=["GET"])
    def serve_admin_portal():
        return send_from_directory(str(FRONTEND_DIR), "admin.html")

    # Serve Resume PDF & Download Endpoints
    @app.route("/resume.pdf", methods=["GET"])
    @app.route("/Tejaswini_Pemmasani_Resume.pdf", methods=["GET"])
    def serve_resume_pdf():
        return send_from_directory(
            str(FRONTEND_DIR),
            "Tejaswini_Pemmasani_Resume.pdf",
            mimetype="application/pdf"
        )

    @app.route("/download-resume", methods=["GET"])
    def download_resume():
        return send_from_directory(
            str(FRONTEND_DIR),
            "Tejaswini_Pemmasani_Resume.pdf",
            as_attachment=True,
            download_name="Pemmasani_Tejaswini_Resume.pdf",
            mimetype="application/pdf"
        )

    # API Overview endpoint
    @app.route("/api", methods=["GET"])
    def api_overview():
        return jsonify({
            "service": "Tejaswini Portfolio - Unified Flask Gateway & IT Admin Backend",
            "version": "1.0.0",
            "status": "ONLINE",
            "admin_portal": "/admin",
            "endpoints": {
                "health": "/api/health",
                "admin_login": "/api/admin/login",
                "admin_stats": "/api/admin/stats",
                "admin_projects": "/api/admin/projects",
                "admin_skills": "/api/admin/skills",
                "admin_contacts": "/api/admin/contacts",
                "admin_profile": "/api/admin/profile",
                "public_projects": "/api/public/projects",
                "public_skills": "/api/public/skills",
                "public_profile": "/api/public/profile",
                "contact_submit": "/api/contact/submit",
                "attendance_log": "/api/attendance/verify-and-log",
                "attendance_records": "/api/attendance/records"
            }
        }), 200

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({
                "error": True,
                "status_code": 404,
                "message": "The requested API endpoint was not found on Flask Gateway."
            }), 404
        return send_from_directory(str(FRONTEND_DIR), "index.html")

    @app.errorhandler(500)
    def handle_server_error(e):
        logger.error(f"Internal gateway error: {e}", exc_info=True)
        return jsonify({
            "error": True,
            "status_code": 500,
            "message": "Internal server error occurred within Flask Gateway."
        }), 500
        
    return app

if __name__ == "__main__":
    flask_app = create_app()
    logger.info(f"Starting Flask API Gateway on http://{FLASK_HOST}:{FLASK_PORT}")
    flask_app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
