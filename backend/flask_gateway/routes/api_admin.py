import json
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from flask_gateway.database import (
    db,
    AdminUser,
    ProjectItem,
    SkillItem,
    ProfileConfig,
    ContactMessage,
    AttendanceRecord,
    AnalyticsLog
)
from flask_gateway.auth import generate_admin_token, admin_required
from common.logger import setup_logger

api_admin_bp = Blueprint("api_admin_bp", __name__)
logger = setup_logger("AdminAPIRoutes")

# ============================================================================
# 1. AUTHENTICATION & SESSION MANAGEMENT
# ============================================================================
@api_admin_bp.route("/api/admin/login", methods=["POST"])
def admin_login():
    """Authenticates admin credentials and issues a secure JWT token."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400
        
    user = AdminUser.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        logger.warning(f"Failed admin login attempt for username: '{username}' from IP {request.remote_addr}")
        return jsonify({
            "success": False,
            "message": "Invalid username or password. Please verify your credentials."
        }), 401
        
    token = generate_admin_token(user)
    logger.info(f"Admin login successful for user '{username}' (ID: {user.id})")
    
    return jsonify({
        "success": True,
        "token": token,
        "user": user.to_dict(),
        "message": "Authentication successful. Welcome to IT Admin Dashboard!"
    }), 200

@api_admin_bp.route("/api/admin/verify", methods=["GET"])
@admin_required
def admin_verify_token():
    """Validates active admin session token."""
    return jsonify({
        "success": True,
        "authenticated": True,
        "user": g.admin_user
    }), 200

@api_admin_bp.route("/api/admin/change-password", methods=["POST"])
@admin_required
def admin_change_password():
    """Allows authenticated admin to change master password."""
    data = request.get_json() or {}
    current_password = data.get("current_password", "").strip()
    new_password = data.get("new_password", "").strip()
    
    if len(new_password) < 8:
        return jsonify({
            "success": False,
            "message": "New password must be at least 8 characters in length."
        }), 400
        
    user = AdminUser.query.get(g.admin_user["user_id"])
    if not user or not user.check_password(current_password):
        return jsonify({
            "success": False,
            "message": "Incorrect current password."
        }), 400
        
    user.set_password(new_password)
    db.session.commit()
    logger.info(f"Admin password changed for user ID: {user.id}")
    
    return jsonify({
        "success": True,
        "message": "Admin master password successfully updated."
    }), 200

# ============================================================================
# 2. DASHBOARD OVERVIEW & METRICS
# ============================================================================
@api_admin_bp.route("/api/admin/stats", methods=["GET"])
@admin_required
def get_dashboard_stats():
    """Aggregates system-wide telemetry, message counts, and module metrics."""
    try:
        total_projects = ProjectItem.query.count()
        total_skills = SkillItem.query.count()
        total_inquiries = ContactMessage.query.count()
        new_inquiries = ContactMessage.query.filter_by(status="NEW").count()
        total_attendance = AttendanceRecord.query.count()
        total_analytics = AnalyticsLog.query.count()
        
        recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
        recent_attendance = AttendanceRecord.query.order_by(AttendanceRecord.timestamp.desc()).limit(5).all()
        
        return jsonify({
            "success": True,
            "metrics": {
                "total_projects": total_projects,
                "total_skills": total_skills,
                "total_inquiries": total_inquiries,
                "new_inquiries": new_inquiries,
                "total_attendance_logs": total_attendance,
                "total_page_events": total_analytics
            },
            "recent_messages": [m.to_dict() for m in recent_messages],
            "recent_attendance": [a.to_dict() for a in recent_attendance]
        }), 200
    except Exception as e:
        logger.error(f"Error compiling admin stats: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# 3. PROJECT SHOWCASE MANAGEMENT (CRUD)
# ============================================================================
@api_admin_bp.route("/api/admin/projects", methods=["GET", "POST"])
@admin_required
def admin_manage_projects():
    if request.method == "GET":
        projects = ProjectItem.query.order_by(ProjectItem.display_order.asc(), ProjectItem.id.asc()).all()
        return jsonify({
            "success": True,
            "count": len(projects),
            "projects": [p.to_dict() for p in projects]
        }), 200
        
    # POST: Add new project
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    category = data.get("category", "Software Engineering").strip()
    overview = data.get("overview", "").strip()
    problem = data.get("problem", "").strip()
    solution = data.get("solution", "").strip()
    slug = data.get("slug", "").strip() or title.lower().replace(" ", "-").replace("/", "-")
    
    if not title or not overview:
        return jsonify({
            "success": False,
            "message": "Title and Overview are mandatory fields."
        }), 400
        
    features = data.get("features", [])
    technologies = data.get("technologies", [])
    if isinstance(features, str):
        features = [f.strip() for f in features.split("\n") if f.strip()]
    if isinstance(technologies, str):
        technologies = [t.strip() for t in technologies.split(",") if t.strip()]

    # Ensure unique slug
    existing = ProjectItem.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        
    new_proj = ProjectItem(
        slug=slug,
        title=title,
        category=category,
        overview=overview,
        problem=problem,
        solution=solution,
        features_json=json.dumps(features),
        technologies_json=json.dumps(technologies),
        repo_url=data.get("repo_url", ""),
        live_url=data.get("live_url", ""),
        is_featured=data.get("is_featured", True),
        display_order=int(data.get("display_order", 0))
    )
    
    try:
        db.session.add(new_proj)
        db.session.commit()
        logger.info(f"Created new project #{new_proj.id}: '{title}' ({slug})")
        return jsonify({
            "success": True,
            "message": f"Project '{title}' created successfully.",
            "project": new_proj.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@api_admin_bp.route("/api/admin/projects/<int:project_id>", methods=["GET", "PUT", "DELETE"])
@admin_required
def admin_project_detail(project_id: int):
    project = ProjectItem.query.get(project_id)
    if not project:
        return jsonify({"success": False, "message": "Project not found."}), 404
        
    if request.method == "GET":
        return jsonify({"success": True, "project": project.to_dict()}), 200
        
    if request.method == "DELETE":
        try:
            db.session.delete(project)
            db.session.commit()
            logger.info(f"Deleted project #{project_id}")
            return jsonify({"success": True, "message": "Project successfully removed."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
            
    # PUT: Update project
    data = request.get_json() or {}
    if "title" in data: project.title = data["title"].strip()
    if "category" in data: project.category = data["category"].strip()
    if "overview" in data: project.overview = data["overview"].strip()
    if "problem" in data: project.problem = data["problem"].strip()
    if "solution" in data: project.solution = data["solution"].strip()
    if "repo_url" in data: project.repo_url = data["repo_url"].strip()
    if "live_url" in data: project.live_url = data["live_url"].strip()
    if "is_featured" in data: project.is_featured = bool(data["is_featured"])
    if "display_order" in data: project.display_order = int(data["display_order"])
    
    if "features" in data:
        features = data["features"]
        if isinstance(features, str):
            features = [f.strip() for f in features.split("\n") if f.strip()]
        project.features_json = json.dumps(features)
        
    if "technologies" in data:
        technologies = data["technologies"]
        if isinstance(technologies, str):
            technologies = [t.strip() for t in technologies.split(",") if t.strip()]
        project.technologies_json = json.dumps(technologies)
        
    try:
        db.session.commit()
        logger.info(f"Updated project #{project.id}: '{project.title}'")
        return jsonify({
            "success": True,
            "message": f"Project '{project.title}' updated successfully.",
            "project": project.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# 4. SKILLS & TECH STACK MANAGEMENT (CRUD)
# ============================================================================
@api_admin_bp.route("/api/admin/skills", methods=["GET", "POST"])
@admin_required
def admin_manage_skills():
    if request.method == "GET":
        skills = SkillItem.query.order_by(SkillItem.category.asc(), SkillItem.display_order.asc()).all()
        return jsonify({
            "success": True,
            "count": len(skills),
            "skills": [s.to_dict() for s in skills]
        }), 200
        
    # POST: Add skill
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    category = data.get("category", "Programming").strip()
    proficiency = int(data.get("proficiency_pct", 85))
    display_order = int(data.get("display_order", 0))
    
    if not name:
        return jsonify({"success": False, "message": "Skill name is required."}), 400
        
    new_skill = SkillItem(
        name=name,
        category=category,
        proficiency_pct=proficiency,
        icon_tag=data.get("icon_tag", "code"),
        display_order=display_order
    )
    
    try:
        db.session.add(new_skill)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Skill '{name}' added successfully.",
            "skill": new_skill.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@api_admin_bp.route("/api/admin/skills/<int:skill_id>", methods=["PUT", "DELETE"])
@admin_required
def admin_skill_detail(skill_id: int):
    skill = SkillItem.query.get(skill_id)
    if not skill:
        return jsonify({"success": False, "message": "Skill not found."}), 404
        
    if request.method == "DELETE":
        try:
            db.session.delete(skill)
            db.session.commit()
            return jsonify({"success": True, "message": "Skill removed successfully."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
            
    # PUT: Update skill
    data = request.get_json() or {}
    if "name" in data: skill.name = data["name"].strip()
    if "category" in data: skill.category = data["category"].strip()
    if "proficiency_pct" in data: skill.proficiency_pct = int(data["proficiency_pct"])
    if "display_order" in data: skill.display_order = int(data["display_order"])
    if "icon_tag" in data: skill.icon_tag = data["icon_tag"].strip()
    
    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Skill '{skill.name}' updated.",
            "skill": skill.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# 5. CONTACT INQUIRIES & RECRUITER LEADS
# ============================================================================
@api_admin_bp.route("/api/admin/contacts", methods=["GET"])
@admin_required
def admin_get_contacts():
    status_filter = request.args.get("status")
    query = ContactMessage.query
    if status_filter:
        query = query.filter_by(status=status_filter.upper())
    messages = query.order_by(ContactMessage.created_at.desc()).all()
    
    return jsonify({
        "success": True,
        "count": len(messages),
        "messages": [m.to_dict() for m in messages]
    }), 200

@api_admin_bp.route("/api/admin/contacts/<int:msg_id>", methods=["PUT", "DELETE"])
@admin_required
def admin_modify_contact(msg_id: int):
    msg = ContactMessage.query.get(msg_id)
    if not msg:
        return jsonify({"success": False, "message": "Message not found."}), 404
        
    if request.method == "DELETE":
        try:
            db.session.delete(msg)
            db.session.commit()
            return jsonify({"success": True, "message": "Inquiry record deleted."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
            
    # PUT: Update status
    data = request.get_json() or {}
    new_status = data.get("status", "").upper()
    if new_status in ["NEW", "READ", "RESPONDED", "ARCHIVED"]:
        msg.status = new_status
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Status updated to '{new_status}'.",
            "message_record": msg.to_dict()
        }), 200
    return jsonify({"success": False, "message": "Invalid status value."}), 400

# ============================================================================
# 6. PROFILE CONFIGURATIONS & SETTINGS
# ============================================================================
@api_admin_bp.route("/api/admin/profile", methods=["GET", "PUT"])
@admin_required
def admin_manage_profile():
    if request.method == "GET":
        configs = ProfileConfig.query.all()
        config_dict = {c.config_key: c.config_value for c in configs}
        return jsonify({"success": True, "profile": config_dict}), 200
        
    # PUT: Save key-value profile settings
    data = request.get_json() or {}
    for key, value in data.items():
        cfg = ProfileConfig.query.filter_by(config_key=key).first()
        if cfg:
            cfg.config_value = str(value)
        else:
            cfg = ProfileConfig(config_key=key, config_value=str(value))
            db.session.add(cfg)
            
    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Profile configuration updated."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
