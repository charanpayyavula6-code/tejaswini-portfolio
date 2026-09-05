"""
Cloud Database (MongoDB Atlas) Manager & Microservice Data Synchronizer.
Provides robust cloud database connectivity, connection pooling, health checks,
fallback capabilities, and dual-sync helpers for Flask and FastAPI microservices.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("tejaswini_portfolio.cloud_db")

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.warning("pymongo is not installed. Cloud database features will operate in fallback mode.")

from backend.common.config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_TIMEOUT_MS

class CloudDatabaseManager:
    """Universal MongoDB Atlas Manager with auto-reconnection and health telemetry."""
    
    _instance: Optional["CloudDatabaseManager"] = None
    _client: Optional[Any] = None
    _active_uri: str = ""
    _is_connected: bool = False
    _last_error: str = ""
    _last_ping_latency_ms: float = 0.0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CloudDatabaseManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self._active_uri = MONGODB_URI.strip()
        self._db_name = MONGODB_DB_NAME
        self._timeout_ms = MONGODB_TIMEOUT_MS
        if self._active_uri and PYMONGO_AVAILABLE:
            self._connect(self._active_uri)

    def _connect(self, uri: str) -> bool:
        """Attempts to establish connection to MongoDB Atlas."""
        if not PYMONGO_AVAILABLE:
            self._is_connected = False
            self._last_error = "pymongo driver not available"
            return False
            
        if not uri or not (uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")):
            self._is_connected = False
            self._last_error = "Invalid MongoDB connection URI"
            return False

        try:
            start_t = time.perf_counter()
            client = MongoClient(
                uri,
                serverSelectionTimeoutMS=self._timeout_ms,
                connectTimeoutMS=self._timeout_ms,
                socketTimeoutMS=self._timeout_ms,
                appname="TejaswiniPortfolioGateway"
            )
            # Ping database to verify connection
            client.admin.command('ping')
            self._last_ping_latency_ms = round((time.perf_counter() - start_t) * 1000, 2)
            self._client = client
            self._active_uri = uri
            self._is_connected = True
            self._last_error = ""
            logger.info(f"Connected to MongoDB Atlas ({self._last_ping_latency_ms}ms ping)")
            
            # Ensure collections and initial data are seeded in MongoDB Atlas
            self._seed_mongo_defaults()
            return True
        except Exception as e:
            self._is_connected = False
            self._client = None
            self._last_error = str(e)
            logger.warning(f"MongoDB Atlas connection failed: {e}")
            return False

    def _seed_mongo_defaults(self):
        """Seeds default project, skill, and config documents into MongoDB Atlas if empty."""
        try:
            db = self.get_database()
            if db is None:
                return

            # 1. Projects
            if db["portfolio_projects"].count_documents({}) == 0:
                default_projects = [
                    {
                        "slug": "face-attendance",
                        "title": "Face Recognition Attendance System",
                        "category": "Computer Vision & Database",
                        "overview": "Developed a system for real-time face detection and recognition through a webcam using OpenCV and Python. Automated attendance marking to reduce manual effort and prevent proxy attendance.",
                        "problem": "Traditional manual attendance systems are time-consuming and vulnerable to proxy attendance.",
                        "solution": "Built an end-to-end computer vision application using Python and OpenCV that captures webcam streams, extracts facial features, and logs verified records directly into the database.",
                        "features": [
                            "Real-time webcam video stream capture and frame-by-frame face detection.",
                            "High-accuracy facial landmark extraction and biometric matching.",
                            "Automated timestamp recording and attendance logging into database.",
                            "Proxy attendance mitigation by requiring physical live camera presence."
                        ],
                        "technologies": ["Python", "OpenCV", "Face Recognition", "MySQL", "MongoDB"],
                        "repo_url": "https://github.com/tejaswini-pemmasani/face-attendance-system",
                        "live_url": "",
                        "is_featured": True,
                        "display_order": 1
                    },
                    {
                        "slug": "email-spam",
                        "title": "Email Spam Detection",
                        "category": "Machine Learning & NLP",
                        "overview": "Built a machine-learning model to classify emails as Spam or Not Spam using NLP preprocessing and scikit-learn classifiers.",
                        "problem": "Unwanted spam and phishing emails clutter inboxes and pose security threats.",
                        "solution": "Engineered an NLP pipeline to preprocess email bodies, extract TF-IDF features, and accurately detect spam messages.",
                        "features": [
                            "NLP preprocessing pipeline including tokenization, lowercasing, and stopword removal.",
                            "Text feature extraction and vectorization for machine learning classification.",
                            "Binary classification distinguishing genuine communications from malicious spam.",
                            "Rapid inference allowing fast classification of raw email bodies."
                        ],
                        "technologies": ["Python", "Machine Learning", "NLP", "Scikit-Learn"],
                        "repo_url": "https://github.com/tejaswini-pemmasani/email-spam-detection",
                        "live_url": "",
                        "is_featured": True,
                        "display_order": 2
                    },
                    {
                        "slug": "captcha-gen",
                        "title": "CAPTCHA Generator",
                        "category": "Web Application & Security",
                        "overview": "Developed a dynamic CAPTCHA generator to improve web-application security by preventing automated bot scripts.",
                        "problem": "Automated bot crawlers and spam scripts exhaust server resources and exploit unprotected forms.",
                        "solution": "Engineered dynamic visual CAPTCHA generation with noise overlays and character rotation to ensure human verification.",
                        "features": [
                            "Dynamic procedural generation of randomized alphanumeric security strings.",
                            "Custom visual noise overlays and character rotation to defeat OCR bots.",
                            "User-friendly frontend verification interface for seamless confirmation.",
                            "Lightweight integration suitable for web application forms."
                        ],
                        "technologies": ["Python", "HTML", "Web Technologies", "Cryptography"],
                        "repo_url": "https://github.com/tejaswini-pemmasani/captcha-generator",
                        "live_url": "",
                        "is_featured": True,
                        "display_order": 3
                    }
                ]
                db["portfolio_projects"].insert_many(default_projects)
                logger.info("Seeded default projects into MongoDB Atlas.")

            # 2. Skills
            if db["portfolio_skills"].count_documents({}) == 0:
                default_skills = [
                    {"name": "Python (OOP, Scripting, Automation)", "category": "Programming", "proficiency_pct": 92, "display_order": 1},
                    {"name": "C Programming & Data Structures", "category": "Programming", "proficiency_pct": 84, "display_order": 2},
                    {"name": "Flask & RESTful API Architecture", "category": "Web & Backend", "proficiency_pct": 90, "display_order": 3},
                    {"name": "FastAPI & Async Microservices", "category": "Web & Backend", "proficiency_pct": 88, "display_order": 4},
                    {"name": "HTML5, CSS3, Modern JavaScript", "category": "Web & Backend", "proficiency_pct": 86, "display_order": 5},
                    {"name": "MongoDB & PyMongo ODM", "category": "Databases", "proficiency_pct": 90, "display_order": 6},
                    {"name": "MySQL & SQLite Database Design", "category": "Databases", "proficiency_pct": 88, "display_order": 7},
                    {"name": "OpenCV & Computer Vision", "category": "Tools & Machine Learning", "proficiency_pct": 88, "display_order": 8},
                    {"name": "Scikit-Learn (NLP, Classification)", "category": "Tools & Machine Learning", "proficiency_pct": 85, "display_order": 9},
                    {"name": "Git, GitHub & Version Control", "category": "Tools & Machine Learning", "proficiency_pct": 90, "display_order": 10}
                ]
                db["portfolio_skills"].insert_many(default_skills)
                logger.info("Seeded default skills into MongoDB Atlas.")

            # 3. Profile configs
            if db["profile_configs"].count_documents({}) == 0:
                default_configs = [
                    {"key": "full_name", "value": "Pemmasani Tejaswini", "description": "Full legal/professional name"},
                    {"key": "professional_title", "value": "Computer Science Engineer | Python & Backend Developer", "description": "Hero headline"},
                    {"key": "email", "value": "pemmasanitejaswini59@gmail.com", "description": "Primary contact email"},
                    {"key": "phone", "value": "+91 9392576974", "description": "Primary phone number"},
                    {"key": "location", "value": "Gudur, Andhra Pradesh, India", "description": "Geographic location"},
                    {"key": "education_degree", "value": "B.Tech in Computer Science and Engineering", "description": "Degree title"},
                    {"key": "education_college", "value": "Audisankara College of Engineering & Technology, Gudur", "description": "College"},
                    {"key": "education_cgpa", "value": "8.5 / 10.0 CGPA (2022 - 2026)", "description": "Academic standing"},
                    {"key": "github_url", "value": "https://github.com/tejaswini-pemmasani", "description": "GitHub profile link"},
                    {"key": "linkedin_url", "value": "https://linkedin.com/in/tejaswini-pemmasani-cse", "description": "LinkedIn profile link"}
                ]
                db["profile_configs"].insert_many(default_configs)
                logger.info("Seeded default profile configs into MongoDB Atlas.")
        except Exception as seed_err:
            logger.warning(f"Error while seeding MongoDB Atlas: {seed_err}")


    def is_connected(self) -> bool:
        """Returns True if connected to MongoDB Atlas."""
        return self._is_connected and self._client is not None

    def get_client(self) -> Optional[Any]:
        return self._client

    def get_database(self, db_name: Optional[str] = None):
        """Returns the active MongoDB database object or None."""
        if self.is_connected() and self._client:
            return self._client[db_name or self._db_name]
        return None

    def test_connection(self, uri: Optional[str] = None) -> Dict[str, Any]:
        """Tests connectivity against a provided or configured MongoDB Atlas URI."""
        test_uri = (uri or self._active_uri or MONGODB_URI).strip()
        if not test_uri:
            return {
                "success": False,
                "connected": False,
                "type": "LOCAL_SQLITE_FALLBACK",
                "message": "No MongoDB Atlas URI configured. Operating on high-performance local SQLite database.",
                "latency_ms": 0,
                "database": self._db_name,
                "collections": []
            }

        if not PYMONGO_AVAILABLE:
            return {
                "success": False,
                "connected": False,
                "type": "ERROR",
                "message": "PyMongo driver is not installed in the environment.",
                "latency_ms": 0,
                "database": self._db_name,
                "collections": []
            }

        try:
            start_t = time.perf_counter()
            test_client = MongoClient(
                test_uri,
                serverSelectionTimeoutMS=4000,
                connectTimeoutMS=4000,
                appname="TejaswiniPortfolioConnectionTester"
            )
            test_client.admin.command('ping')
            latency = round((time.perf_counter() - start_t) * 1000, 2)
            
            db = test_client[self._db_name]
            cols = db.list_collection_names()
            
            # If tested URI is valid, update active client
            self._client = test_client
            self._active_uri = test_uri
            self._is_connected = True
            self._last_error = ""
            self._last_ping_latency_ms = latency

            # Redact password in URI for safe display
            safe_uri = self.mask_uri(test_uri)

            return {
                "success": True,
                "connected": True,
                "type": "MONGODB_ATLAS_CLOUD",
                "message": f"Successfully connected to MongoDB Atlas Cloud Cluster ({latency}ms ping).",
                "latency_ms": latency,
                "database": self._db_name,
                "collections": cols,
                "masked_uri": safe_uri
            }
        except Exception as ex:
            return {
                "success": False,
                "connected": False,
                "type": "ERROR",
                "message": f"Connection failed: {str(ex)}",
                "latency_ms": 0,
                "database": self._db_name,
                "collections": []
            }

    def get_status(self) -> Dict[str, Any]:
        """Returns full database health status for IT Admin portal."""
        if self.is_connected() and self._client:
            try:
                db = self.get_database()
                cols = db.list_collection_names() if db is not None else []
                stats = {}
                if db is not None:
                    for c in cols:
                        stats[c] = db[c].count_documents({})
                return {
                    "mode": "MONGODB_ATLAS_CLOUD",
                    "connected": True,
                    "database_name": self._db_name,
                    "masked_uri": self.mask_uri(self._active_uri),
                    "latency_ms": self._last_ping_latency_ms,
                    "collections_count": len(cols),
                    "collections": cols,
                    "collection_stats": stats,
                    "status_label": "🟢 MongoDB Atlas Active"
                }
            except Exception as e:
                self._is_connected = False
                self._last_error = str(e)
                
        return {
            "mode": "SQLITE_LOCAL_FALLBACK",
            "connected": False,
            "database_name": "portfolio.db (SQLite)",
            "masked_uri": "sqlite:///instance/portfolio.db",
            "latency_ms": 0.1,
            "collections_count": 7,
            "collections": [
                "admin_users", "portfolio_projects", "portfolio_skills", 
                "contact_messages", "attendance_records", "profile_configs", "analytics_logs"
            ],
            "collection_stats": {},
            "status_label": "🟡 Local / Serverless Database Active",
            "last_error": self._last_error
        }

    @staticmethod
    def mask_uri(uri: str) -> str:
        """Masks sensitive credentials inside connection strings."""
        if not uri or "@" not in uri:
            return uri
        try:
            prefix, rest = uri.split("://", 1)
            creds, host = rest.split("@", 1)
            if ":" in creds:
                user = creds.split(":", 1)[0]
                return f"{prefix}://{user}:******@{host}"
            return f"{prefix}://******@{host}"
        except Exception:
            return "mongodb+srv://******"

    # -------------------------------------------------------------
    # Collection CRUD Helpers for Connected Microservices
    # -------------------------------------------------------------

    def record_attendance(self, student_id: str, student_name: str, confidence: float, status: str, device_id: str = "CAM-GATE-01") -> bool:
        """Writes verified biometric attendance event to Cloud DB."""
        if not self.is_connected():
            return False
        try:
            db = self.get_database()
            if db is not None:
                doc = {
                    "student_id": student_id,
                    "student_name": student_name,
                    "confidence_score": confidence,
                    "status": status,
                    "device_id": device_id,
                    "timestamp": datetime.utcnow()
                }
                db["attendance_records"].insert_one(doc)
                return True
        except Exception as e:
            logger.error(f"Failed to record attendance to MongoDB: {e}")
        return False

    def save_inquiry(self, name: str, email: str, subject: str, message: str, ip: str = "", user_agent: str = "") -> bool:
        """Writes recruiter message to Cloud DB."""
        if not self.is_connected():
            return False
        try:
            db = self.get_database()
            if db is not None:
                doc = {
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                    "ip_address": ip,
                    "user_agent": user_agent,
                    "status": "NEW",
                    "created_at": datetime.utcnow()
                }
                db["contact_messages"].insert_one(doc)
                return True
        except Exception as e:
            logger.error(f"Failed to save inquiry to MongoDB: {e}")
        return False

    def record_ai_telemetry(self, module: str, request_data: Dict[str, Any], response_data: Dict[str, Any], latency_ms: float) -> bool:
        """Writes AI/ML inference logs to Cloud DB."""
        if not self.is_connected():
            return False
        try:
            db = self.get_database()
            if db is not None:
                doc = {
                    "module": module,
                    "request": request_data,
                    "response": response_data,
                    "latency_ms": latency_ms,
                    "timestamp": datetime.utcnow()
                }
                db["ai_telemetry"].insert_one(doc)
                return True
        except Exception as e:
            logger.error(f"Failed to record AI telemetry to MongoDB: {e}")
        return False

    def sync_all_from_sql(self, projects: List[Dict], skills: List[Dict], inquiries: List[Dict], attendance: List[Dict], configs: List[Dict]) -> Dict[str, Any]:
        """Syncs all SQL records into MongoDB Atlas collections with bulk upserts."""
        if not self.is_connected():
            return {"success": False, "message": "MongoDB Atlas is not connected."}
            
        try:
            db = self.get_database()
            if db is None:
                return {"success": False, "message": "Could not acquire database handle."}

            synced_counts = {}

            # 1. Projects
            if projects:
                for p in projects:
                    db["portfolio_projects"].update_one(
                        {"slug": p.get("slug")},
                        {"$set": p},
                        upsert=True
                    )
                synced_counts["projects"] = len(projects)

            # 2. Skills
            if skills:
                for s in skills:
                    db["portfolio_skills"].update_one(
                        {"name": s.get("name")},
                        {"$set": s},
                        upsert=True
                    )
                synced_counts["skills"] = len(skills)

            # 3. Inquiries
            if inquiries:
                for inq in inquiries:
                    db["contact_messages"].update_one(
                        {"id": inq.get("id"), "email": inq.get("email")},
                        {"$set": inq},
                        upsert=True
                    )
                synced_counts["inquiries"] = len(inquiries)

            # 4. Attendance
            if attendance:
                for a in attendance:
                    db["attendance_records"].update_one(
                        {"student_id": a.get("student_id"), "timestamp": a.get("timestamp")},
                        {"$set": a},
                        upsert=True
                    )
                synced_counts["attendance"] = len(attendance)

            # 5. Configs
            if configs:
                for cfg in configs:
                    db["profile_configs"].update_one(
                        {"key": cfg.get("key")},
                        {"$set": cfg},
                        upsert=True
                    )
                synced_counts["configs"] = len(configs)

            return {
                "success": True,
                "message": "Successfully synchronized all modules with MongoDB Atlas Cloud Database.",
                "synced_counts": synced_counts
            }
        except Exception as e:
            return {"success": False, "message": f"Sync failed: {str(e)}"}

# Global Singleton
cloud_db = CloudDatabaseManager()
