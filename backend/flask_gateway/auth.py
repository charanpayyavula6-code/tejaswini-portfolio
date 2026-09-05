import time
import hmac
import hashlib
import base64
import json
from functools import wraps
from flask import request, jsonify, g
from common.config import SECRET_KEY
from flask_gateway.database import AdminUser
from common.logger import setup_logger

logger = setup_logger("AdminAuth")

TOKEN_EXPIRATION_SECONDS = 86400 * 7  # 7 Days Token Validity

def generate_admin_token(user: AdminUser) -> str:
    """Generates a tamper-proof cryptographically signed JWT-like token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": int(time.time()) + TOKEN_EXPIRATION_SECONDS
    }
    
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_base = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_base, hashlib.sha256).digest()
    encoded_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{encoded_header}.{encoded_payload}.{encoded_sig}"

def verify_admin_token(token: str) -> dict:
    """Verifies HMAC signature, timestamp expiration, and extracts user payload."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
            
        encoded_header, encoded_payload, encoded_sig = parts
        
        # Verify signature
        signature_base = f"{encoded_header}.{encoded_payload}".encode()
        expected_sig = hmac.new(SECRET_KEY.encode(), signature_base, hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(encoded_sig + "==")
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            logger.warning("Token verification failed: Invalid cryptographic signature.")
            return None
            
        payload_json = base64.urlsafe_b64decode(encoded_payload + "==").decode()
        payload = json.loads(payload_json)
        
        # Verify expiration
        if int(time.time()) > payload.get("exp", 0):
            logger.warning("Token verification failed: Token expired.")
            return None
            
        return payload
    except Exception as e:
        logger.error(f"Error decoding admin token: {e}")
        return None

def admin_required(f):
    """Decorator to enforce Admin Authentication on API routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = ""
        
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
        elif "admin_token" in request.cookies:
            token = request.cookies.get("admin_token")
            
        if not token:
            return jsonify({
                "error": True,
                "status_code": 401,
                "message": "Authorization required: Missing or invalid Bearer token."
            }), 401
            
        payload = verify_admin_token(token)
        if not payload:
            return jsonify({
                "error": True,
                "status_code": 401,
                "message": "Session expired or invalid token. Please log in again."
            }), 401
            
        g.admin_user = payload
        return f(*args, **kwargs)
    return decorated_function
