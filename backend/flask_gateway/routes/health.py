from datetime import datetime
from flask import Blueprint, jsonify
from flask_gateway.client_fastapi import fastapi_client
from common.logger import setup_logger

health_bp = Blueprint("health_bp", __name__)
logger = setup_logger("HealthRoute")

@health_bp.route("/api/health", methods=["GET"])
def system_health():
    """
    Checks operational health of Flask Gateway and pings the FastAPI
    Compute Microservice to ensure full dual-service communication integrity.
    """
    flask_status = "HEALTHY"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    fastapi_health = fastapi_client.check_health()
    fastapi_healthy = not fastapi_health.get("error", False)
    
    overall_status = "HEALTHY" if fastapi_healthy else "DEGRADED"
    status_code = 200 if fastapi_healthy else 503
    
    return jsonify({
        "overall_status": overall_status,
        "timestamp": timestamp,
        "services": {
            "flask_gateway": {
                "name": "Flask API Gateway & Web Orchestrator",
                "status": flask_status,
                "port": 5000
            },
            "fastapi_engine": {
                "name": "FastAPI AI & Algorithmic Compute Engine",
                "status": "HEALTHY" if fastapi_healthy else "UNAVAILABLE",
                "details": fastapi_health,
                "port": 8000
            }
        },
        "communication_bridge": "ONLINE" if fastapi_healthy else "FAILED"
    }), status_code
