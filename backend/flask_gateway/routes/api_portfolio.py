from flask import Blueprint, request, jsonify
from flask_gateway.client_fastapi import fastapi_client
from flask_gateway.database import ProjectItem, SkillItem, ProfileConfig
from common.logger import setup_logger

api_portfolio_bp = Blueprint("api_portfolio_bp", __name__)
logger = setup_logger("PortfolioGatewayRoute")

# ============================================================================
# 1. DYNAMIC PUBLIC MODULE DATA (Read-Only for Public Frontend)
# ============================================================================
@api_portfolio_bp.route("/api/public/projects", methods=["GET"])
def get_public_projects():
    """Returns active portfolio project case studies formatted for the frontend."""
    try:
        projects = ProjectItem.query.filter_by(is_featured=True).order_by(
            ProjectItem.display_order.asc(),
            ProjectItem.id.asc()
        ).all()
        return jsonify({
            "success": True,
            "count": len(projects),
            "projects": [p.to_dict() for p in projects]
        }), 200
    except Exception as e:
        logger.error(f"Error loading public projects: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_portfolio_bp.route("/api/public/skills", methods=["GET"])
def get_public_skills():
    """Returns categorized skills for the public skills matrix."""
    try:
        skills = SkillItem.query.order_by(SkillItem.category.asc(), SkillItem.display_order.asc()).all()
        # Group by category
        grouped = {}
        for s in skills:
            cat = s.category
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(s.to_dict())
            
        return jsonify({
            "success": True,
            "total_count": len(skills),
            "categories": grouped
        }), 200
    except Exception as e:
        logger.error(f"Error loading public skills: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_portfolio_bp.route("/api/public/profile", methods=["GET"])
def get_public_profile():
    """Returns candidate profile details."""
    try:
        configs = ProfileConfig.query.all()
        data = {c.config_key: c.config_value for c in configs}
        return jsonify({"success": True, "profile": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# 2. NLP EMAIL SPAM CLASSIFIER GATEWAY
# ============================================================================
@api_portfolio_bp.route("/api/spam/predict", methods=["POST"])
def gateway_spam_predict():
    data = request.get_json() or {}
    email_text = data.get("email_text", "").strip()
    
    if not email_text:
        return jsonify({
            "error": True,
            "message": "Validation error: 'email_text' is required."
        }), 400
        
    result = fastapi_client.analyze_spam(email_text)
    if result.get("error"):
        return jsonify(result), result.get("status_code", 500)
    return jsonify(result), 200

# ============================================================================
# 3. DYNAMIC PROCEDURAL CAPTCHA GATEWAY
# ============================================================================
@api_portfolio_bp.route("/api/captcha/generate", methods=["GET"])
def gateway_captcha_generate():
    result = fastapi_client.generate_captcha()
    if result.get("error"):
        return jsonify(result), result.get("status_code", 500)
    return jsonify(result), 200

@api_portfolio_bp.route("/api/captcha/verify", methods=["POST"])
def gateway_captcha_verify():
    data = request.get_json() or {}
    token = data.get("captcha_token", "").strip()
    solution = data.get("user_solution", "").strip()
    
    if not token or not solution:
        return jsonify({
            "error": True,
            "message": "Validation error: Both 'captcha_token' and 'user_solution' are required."
        }), 400
        
    result = fastapi_client.verify_captcha(token, solution)
    if result.get("error"):
        return jsonify(result), result.get("status_code", 500)
    return jsonify(result), 200

# ============================================================================
# 4. CLINICAL DISEASE PREDICTION GATEWAY
# ============================================================================
@api_portfolio_bp.route("/api/disease/predict-diabetes", methods=["POST"])
def gateway_predict_diabetes():
    data = request.get_json() or {}
    if "glucose" not in data or "bmi" not in data or "age" not in data or "blood_pressure" not in data:
        return jsonify({
            "error": True,
            "message": "Validation error: 'glucose', 'bmi', 'blood_pressure', and 'age' parameters are required."
        }), 400
        
    result = fastapi_client.predict_diabetes(data)
    if result.get("error"):
        return jsonify(result), result.get("status_code", 500)
    return jsonify(result), 200

@api_portfolio_bp.route("/api/disease/predict-heart", methods=["POST"])
def gateway_predict_heart():
    data = request.get_json() or {}
    required_fields = ["age", "sex", "chest_pain_type", "resting_bp", "cholesterol", "max_heart_rate"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({
            "error": True,
            "message": f"Validation error: Missing required fields: {', '.join(missing)}"
        }), 400
        
    result = fastapi_client.predict_heart_disease(data)
    if result.get("error"):
        return jsonify(result), result.get("status_code", 500)
    return jsonify(result), 200

# ============================================================================
# 5. PORTFOLIO AI ASSISTANT GATEWAY
# ============================================================================
@api_portfolio_bp.route("/api/assistant/chat", methods=["POST"])
def gateway_assistant_chat():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    
    if not query:
        return jsonify({
            "error": True,
            "message": "Validation error: 'query' parameter is required."
        }), 400
        
    result = fastapi_client.query_assistant(query)
    if result.get("error"):
        return jsonify(result), result.get("status_code", 500)
    return jsonify(result), 200
