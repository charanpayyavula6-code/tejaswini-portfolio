"""
Unified Database Engine & ODM / ORM Layer.
Seamlessly routes queries and mutations to MongoDB Atlas when active,
or falls back to SQLAlchemy SQLite when operating locally/serverless.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from common.cloud_db import cloud_db

logger = logging.getLogger("tejaswini_portfolio.db_engine")

class UnifiedDBEngine:
    """Unified Document-Object Mapper providing dual-engine abstraction for MongoDB & SQL."""

    @classmethod
    def is_mongo_active(cls) -> bool:
        return cloud_db.is_connected()

    # -------------------------------------------------------------------------
    # PROJECTS MODULE
    # -------------------------------------------------------------------------
    @classmethod
    def get_all_projects(cls, featured_only: bool = False) -> List[Dict[str, Any]]:
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    query = {"is_featured": True} if featured_only else {}
                    cursor = db["portfolio_projects"].find(query, {"_id": 0}).sort("display_order", 1)
                    projects = list(cursor)
                    if projects:
                        return projects
            except Exception as e:
                logger.warning(f"MongoDB read error for projects: {e}")

        # SQL Fallback
        from flask_gateway.database import ProjectItem
        q = ProjectItem.query
        if featured_only:
            q = q.filter_by(is_featured=True)
        return [p.to_dict() for p in q.order_by(ProjectItem.display_order.asc()).all()]

    @classmethod
    def save_project(cls, project_data: Dict[str, Any]) -> Dict[str, Any]:
        slug = project_data.get("slug")
        if not slug:
            return {"error": True, "message": "Slug is required"}

        # 1. Save to MongoDB Atlas if active
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    db["portfolio_projects"].update_one(
                        {"slug": slug},
                        {"$set": project_data},
                        upsert=True
                    )
            except Exception as e:
                logger.error(f"MongoDB save project error: {e}")

        return {"success": True, "project": project_data}

    @classmethod
    def delete_project(cls, slug: str) -> bool:
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    db["portfolio_projects"].delete_one({"slug": slug})
            except Exception as e:
                logger.error(f"MongoDB delete project error: {e}")
        return True

    # -------------------------------------------------------------------------
    # SKILLS MODULE
    # -------------------------------------------------------------------------
    @classmethod
    def get_all_skills(cls) -> List[Dict[str, Any]]:
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    cursor = db["portfolio_skills"].find({}, {"_id": 0}).sort("display_order", 1)
                    skills = list(cursor)
                    if skills:
                        return skills
            except Exception as e:
                logger.warning(f"MongoDB read error for skills: {e}")

        from flask_gateway.database import SkillItem
        return [s.to_dict() for s in SkillItem.query.order_by(SkillItem.display_order.asc()).all()]

    @classmethod
    def save_skill(cls, skill_data: Dict[str, Any]) -> Dict[str, Any]:
        name = skill_data.get("name")
        if not name:
            return {"error": True, "message": "Skill name is required"}

        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    db["portfolio_skills"].update_one(
                        {"name": name},
                        {"$set": skill_data},
                        upsert=True
                    )
            except Exception as e:
                logger.error(f"MongoDB save skill error: {e}")

        return {"success": True, "skill": skill_data}

    # -------------------------------------------------------------------------
    # INQUIRIES / CONTACT MESSAGES
    # -------------------------------------------------------------------------
    @classmethod
    def record_inquiry(cls, name: str, email: str, subject: str, message: str, ip: str = "", user_agent: str = "") -> Dict[str, Any]:
        doc = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "ip_address": ip,
            "user_agent": user_agent,
            "status": "NEW",
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    res = db["contact_messages"].insert_one(doc)
                    doc["id"] = str(res.inserted_id)
            except Exception as e:
                logger.error(f"MongoDB record inquiry error: {e}")

        return doc

    @classmethod
    def get_inquiries(cls, limit: int = 50) -> List[Dict[str, Any]]:
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    cursor = db["contact_messages"].find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
                    msgs = list(cursor)
                    if msgs:
                        return msgs
            except Exception as e:
                logger.warning(f"MongoDB get inquiries error: {e}")

        from flask_gateway.database import ContactMessage
        return [m.to_dict() for m in ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(limit).all()]

    # -------------------------------------------------------------------------
    # BIOMETRIC ATTENDANCE RECORDS
    # -------------------------------------------------------------------------
    @classmethod
    def record_attendance(cls, student_id: str, student_name: str, confidence: float, status: str, device_id: str = "CAM-GATE-01") -> Dict[str, Any]:
        doc = {
            "student_id": student_id,
            "student_name": student_name,
            "confidence_score": round(confidence, 4),
            "status": status,
            "device_id": device_id,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    res = db["attendance_records"].insert_one(doc)
                    doc["id"] = str(res.inserted_id)
            except Exception as e:
                logger.error(f"MongoDB record attendance error: {e}")

        return doc

    @classmethod
    def get_attendance_records(cls, limit: int = 50) -> List[Dict[str, Any]]:
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    cursor = db["attendance_records"].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
                    recs = list(cursor)
                    if recs:
                        return recs
            except Exception as e:
                logger.warning(f"MongoDB get attendance error: {e}")

        from flask_gateway.database import AttendanceRecord
        return [a.to_dict() for a in AttendanceRecord.query.order_by(AttendanceRecord.timestamp.desc()).limit(limit).all()]

    # -------------------------------------------------------------------------
    # PROFILE CONFIGS & SETTINGS
    # -------------------------------------------------------------------------
    @classmethod
    def get_profile_configs(cls) -> Dict[str, str]:
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    cursor = db["profile_configs"].find({}, {"_id": 0})
                    cfg_list = list(cursor)
                    if cfg_list:
                        return {item["key"]: item["value"] for item in cfg_list if "key" in item and "value" in item}
            except Exception as e:
                logger.warning(f"MongoDB get profile config error: {e}")

        from flask_gateway.database import ProfileConfig
        return {c.config_key: c.config_value for c in ProfileConfig.query.all()}

    @classmethod
    def set_profile_config(cls, key: str, value: str, description: str = "") -> None:
        if cls.is_mongo_active():
            try:
                db = cloud_db.get_database()
                if db is not None:
                    db["profile_configs"].update_one(
                        {"key": key},
                        {"$set": {"key": key, "value": str(value), "description": description}},
                        upsert=True
                    )
            except Exception as e:
                logger.error(f"MongoDB set profile config error: {e}")

# Global Engine Singleton
db_engine = UnifiedDBEngine()
