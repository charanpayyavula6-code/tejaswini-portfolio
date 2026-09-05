from flask import Blueprint, request, jsonify
from flask_gateway.database import db, AnalyticsLog
from common.logger import setup_logger

api_analytics_bp = Blueprint("api_analytics_bp", __name__)
logger = setup_logger("AnalyticsRoute")

@api_analytics_bp.route("/api/analytics/track", methods=["POST"])
def track_event():
    """Logs client interaction events and page telemetry."""
    data = request.get_json() or {}
    endpoint = data.get("endpoint", "/home")
    method = data.get("method", "PAGEVIEW")
    status_code = data.get("status_code", 200)
    response_time = data.get("response_time_ms", 0.0)
    
    try:
        log = AnalyticsLog(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({"success": True, "log_id": log.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@api_analytics_bp.route("/api/analytics/stats", methods=["GET"])
def get_analytics_stats():
    """Returns aggregated site telemetry statistics."""
    try:
        total_requests = AnalyticsLog.query.count()
        recent_logs = AnalyticsLog.query.order_by(AnalyticsLog.timestamp.desc()).limit(25).all()
        
        return jsonify({
            "success": True,
            "total_logged_events": total_requests,
            "recent_events": [l.to_dict() for l in recent_logs]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
