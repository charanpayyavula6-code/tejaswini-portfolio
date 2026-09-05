from flask import Blueprint, request, jsonify
from flask_gateway.client_fastapi import fastapi_client
from flask_gateway.database import db, AttendanceRecord
from common.logger import setup_logger

api_attendance_bp = Blueprint("api_attendance_bp", __name__)
logger = setup_logger("AttendanceRoute")

@api_attendance_bp.route("/api/attendance/verify-and-log", methods=["POST"])
def verify_and_log_attendance():
    """
    1. Forwards face image/credentials to FastAPI compute engine.
    2. If verified, persists attendance event record into SQLite database.
    3. Returns full audit record to client.
    """
    data = request.get_json() or {}
    student_id = data.get("student_id", "").strip()
    student_name = data.get("student_name", "").strip()
    image_base64 = data.get("image_base64")
    device_id = data.get("device_id", "CAM-GATE-01")
    
    if not student_id or not student_name:
        return jsonify({
            "error": True,
            "message": "Both 'student_id' and 'student_name' are required for biometric logging."
        }), 400
        
    # Call FastAPI microservice
    compute_result = fastapi_client.verify_face_attendance(
        student_id=student_id,
        student_name=student_name,
        image_base64=image_base64,
        device_id=device_id
    )
    
    if compute_result.get("error"):
        return jsonify(compute_result), compute_result.get("status_code", 500)
        
    # If verified, persist record
    if compute_result.get("verified"):
        try:
            record = AttendanceRecord(
                student_id=compute_result["student_id"],
                student_name=compute_result["student_name"],
                confidence_score=compute_result["confidence_score"],
                status=compute_result["status"],
                device_id=device_id
            )
            db.session.add(record)
            db.session.commit()
            compute_result["db_record_id"] = record.id
            logger.info(f"Biometric attendance committed to DB: Record #{record.id} for {student_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error persisting attendance log: {e}", exc_info=True)
            compute_result["db_persisted"] = False
            compute_result["db_error"] = str(e)
            
    return jsonify(compute_result), 200

@api_attendance_bp.route("/api/attendance/records", methods=["GET"])
def get_attendance_records():
    """Retrieves all timestamped biometric attendance entries."""
    try:
        limit = min(int(request.args.get("limit", 50)), 200)
        records = AttendanceRecord.query.order_by(AttendanceRecord.timestamp.desc()).limit(limit).all()
        return jsonify({
            "success": True,
            "total_records": len(records),
            "records": [r.to_dict() for r in records]
        }), 200
    except Exception as e:
        logger.error(f"Error reading attendance logs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
