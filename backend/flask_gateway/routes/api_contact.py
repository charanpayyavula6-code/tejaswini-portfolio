import re
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_gateway.database import db, ContactMessage
from common.logger import setup_logger

api_contact_bp = Blueprint("api_contact_bp", __name__)
logger = setup_logger("ContactRoute")

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

@api_contact_bp.route("/api/contact/submit", methods=["POST"])
def submit_contact_form():
    """
    Validates, sanitizes, and records visitor inquiries into SQLite database.
    """
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "Portfolio Inquiry").strip()
    message = data.get("message", "").strip()
    
    # Validation checks
    errors = []
    if len(name) < 2:
        errors.append("Name must contain at least 2 characters.")
    if not EMAIL_REGEX.match(email):
        errors.append("Please provide a valid email address.")
    if len(message) < 8:
        errors.append("Message must contain at least 8 characters.")
        
    if errors:
        return jsonify({
            "success": False,
            "errors": errors,
            "message": "Validation failed on submitted contact form fields."
        }), 400
        
    try:
        new_inquiry = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "Unknown")
        )
        db.session.add(new_inquiry)
        db.session.commit()
        
        logger.info(f"New contact submission recorded: ID={new_inquiry.id} from {name} <{email}>")
        
        return jsonify({
            "success": True,
            "message": "Your message has been securely submitted and logged. Thank you for connecting!",
            "inquiry_id": new_inquiry.id,
            "timestamp": new_inquiry.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to record contact inquiry: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Database transaction error while saving contact message."
        }), 500

@api_contact_bp.route("/api/contact/messages", methods=["GET"])
def list_contact_messages():
    """Retrieves recent contact inquiries (for administrative dashboard viewing)."""
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(limit).all()
        return jsonify({
            "success": True,
            "total_count": len(messages),
            "messages": [m.to_dict() for m in messages]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching contact messages: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
