import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class AdminUser(db.Model):
    """Admin credentials and authorization records."""
    __tablename__ = "admin_users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(32), default="SUPER_ADMIN")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class ProjectItem(db.Model):
    """Dynamic project showcase and case studies."""
    __tablename__ = "portfolio_projects"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    problem = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    features_json = db.Column(db.Text, default="[]")       # Stored as JSON string
    technologies_json = db.Column(db.Text, default="[]")   # Stored as JSON string
    repo_url = db.Column(db.String(255), default="")
    live_url = db.Column(db.String(255), default="")
    is_featured = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        try:
            features = json.loads(self.features_json) if self.features_json else []
        except Exception:
            features = []
            
        try:
            technologies = json.loads(self.technologies_json) if self.technologies_json else []
        except Exception:
            technologies = []
            
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "category": self.category,
            "overview": self.overview,
            "problem": self.problem,
            "solution": self.solution,
            "features": features,
            "technologies": technologies,
            "repo_url": self.repo_url,
            "live_url": self.live_url,
            "is_featured": self.is_featured,
            "display_order": self.display_order,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else ""
        }

class SkillItem(db.Model):
    """Technical skill proficiencies and tool classifications."""
    __tablename__ = "portfolio_skills"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(80), nullable=False)  # Programming, Web & Backend, Databases, Tools & ML
    proficiency_pct = db.Column(db.Integer, default=85)
    icon_tag = db.Column(db.String(50), default="code")
    display_order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "proficiency_pct": self.proficiency_pct,
            "icon_tag": self.icon_tag,
            "display_order": self.display_order
        }

class ProfileConfig(db.Model):
    """Dynamic key-value settings for contact details and profile content."""
    __tablename__ = "profile_configs"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), default="")
    
    def to_dict(self):
        return {
            "key": self.config_key,
            "value": self.config_value,
            "description": self.description
        }

class ContactMessage(db.Model):
    """Stores inquiries submitted via the portfolio contact form."""
    __tablename__ = "contact_messages"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    subject = db.Column(db.String(255), default="General Inquiry")
    message = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(32), default="NEW")  # NEW, READ, RESPONDED, ARCHIVED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class AttendanceRecord(db.Model):
    """Stores real-time face biometric attendance entries."""
    __tablename__ = "attendance_records"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(64), nullable=False, index=True)
    student_name = db.Column(db.String(120), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(64), nullable=False)  # ATTENDANCE_MARKED_PRESENT, REJECTED
    device_id = db.Column(db.String(64), default="CAM-GATE-01")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "confidence_score": round(self.confidence_score, 4),
            "status": self.status,
            "device_id": self.device_id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

class AnalyticsLog(db.Model):
    """Tracks visitor interactions and endpoint performance telemetry."""
    __tablename__ = "analytics_logs"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    endpoint = db.Column(db.String(128), nullable=False, index=True)
    method = db.Column(db.String(16), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response_time_ms = db.Column(db.Float, nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "response_time_ms": round(self.response_time_ms, 2),
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

def seed_initial_data():
    """Populates database with default administrator and initial portfolio content if empty."""
    # 1. Seed Admin User
    if AdminUser.query.count() == 0:
        admin = AdminUser(
            username="admin",
            email="pemmasanitejaswini59@gmail.com",
            role="SUPER_ADMIN"
        )
        admin.set_password("TejaswiniAdmin2026!")
        db.session.add(admin)

    # 2. Seed Default Projects
    if ProjectItem.query.count() == 0:
        default_projects = [
            ProjectItem(
                slug="face-attendance",
                title="Face Recognition Attendance System",
                category="Computer Vision & Database",
                overview="Developed a system for real-time face detection and recognition through a webcam using OpenCV and Python. Automated attendance marking to reduce manual effort and prevent proxy attendance.",
                problem="Traditional manual and paper-based attendance systems are time-consuming, prone to human errors, and vulnerable to proxy attendance in academic and enterprise environments.",
                solution="Built an end-to-end computer vision application using Python and OpenCV that captures live webcam video streams, extracts facial feature embeddings, matches against registered records, and records verified timestamps directly into a MySQL database.",
                features_json=json.dumps([
                    "Real-time webcam video stream capture and frame-by-frame face detection.",
                    "High-accuracy facial landmark extraction and biometric matching.",
                    "Automated timestamp recording and attendance logging into MySQL.",
                    "Proxy attendance mitigation by requiring physical live camera presence."
                ]),
                technologies_json=json.dumps(["Python", "OpenCV", "Face Recognition", "MySQL"]),
                repo_url="https://github.com/tejaswini-pemmasani/face-attendance-system",
                live_url="",
                is_featured=True,
                display_order=1
            ),
            ProjectItem(
                slug="email-spam",
                title="Email Spam Detection",
                category="Machine Learning & NLP",
                overview="Built a machine-learning model to classify emails as Spam or Not Spam using email-content analysis and NLP preprocessing.",
                problem="The overwhelming volume of spam, phishing, and unwanted promotional emails clutters inboxes and poses significant digital security risks for users and organizations.",
                solution="Developed a machine learning classification pipeline with Natural Language Processing (NLP) techniques to analyze message semantics, clean textual features, remove stopwords, and reliably categorize incoming email content as Spam or Ham.",
                features_json=json.dumps([
                    "NLP preprocessing pipeline including tokenization, lowercasing, and stopword removal.",
                    "Text feature extraction and vectorization for numerical machine learning modeling.",
                    "Binary classification distinguishing genuine communications from malicious spam.",
                    "Rapid inference allowing fast classification of raw email bodies."
                ]),
                technologies_json=json.dumps(["Python", "Machine Learning", "NLP", "Scikit-Learn"]),
                repo_url="https://github.com/tejaswini-pemmasani/email-spam-detection",
                live_url="",
                is_featured=True,
                display_order=2
            ),
            ProjectItem(
                slug="captcha-gen",
                title="CAPTCHA Generator",
                category="Web Application & Security",
                overview="Developed a dynamic CAPTCHA generator to improve web-application security by preventing automated bot scripts.",
                problem="Automated bot crawlers, spam bots, and brute-force scripts exploit web forms, skewing analytics and exhausting server resources.",
                solution="Engineered a dynamic security verification tool that procedurally generates randomized alphanumeric visual verification codes layered with custom noise patterns, angular distortions, and custom fonts to ensure only human users can submit protected forms.",
                features_json=json.dumps([
                    "Dynamic procedural generation of randomized alphanumeric security strings.",
                    "Custom visual noise overlays and character rotation to defeat OCR bots.",
                    "User-friendly frontend verification interface for seamless user confirmation.",
                    "Lightweight integration suitable for web application forms and login gates."
                ]),
                technologies_json=json.dumps(["Python", "HTML", "Web Technologies", "Cryptography"]),
                repo_url="https://github.com/tejaswini-pemmasani/captcha-generator",
                live_url="",
                is_featured=True,
                display_order=3
            )
        ]
        db.session.add_all(default_projects)

    # 3. Seed Default Skills
    if SkillItem.query.count() == 0:
        default_skills = [
            # Programming
            SkillItem(name="Python (OOP, Scripting, Automation)", category="Programming", proficiency_pct=92, display_order=1),
            SkillItem(name="C Programming & Data Structures", category="Programming", proficiency_pct=84, display_order=2),
            # Web & Backend
            SkillItem(name="Flask & RESTful API Architecture", category="Web & Backend", proficiency_pct=90, display_order=3),
            SkillItem(name="FastAPI & Async Microservices", category="Web & Backend", proficiency_pct=88, display_order=4),
            SkillItem(name="HTML5, CSS3, Modern JavaScript", category="Web & Backend", proficiency_pct=86, display_order=5),
            # Databases
            SkillItem(name="MySQL (DDL, DML, Joins, Indexing)", category="Databases", proficiency_pct=88, display_order=6),
            SkillItem(name="SQLite & SQLAlchemy ORM", category="Databases", proficiency_pct=86, display_order=7),
            # Tools & ML
            SkillItem(name="OpenCV & Computer Vision", category="Tools & Machine Learning", proficiency_pct=88, display_order=8),
            SkillItem(name="Scikit-Learn (NLP, Classification)", category="Tools & Machine Learning", proficiency_pct=85, display_order=9),
            SkillItem(name="Git, GitHub & Version Control", category="Tools & Machine Learning", proficiency_pct=90, display_order=10),
            SkillItem(name="VS Code & Linux Environment", category="Tools & Machine Learning", proficiency_pct=88, display_order=11)
        ]
        db.session.add_all(default_skills)

    # 4. Seed Profile Config
    if ProfileConfig.query.count() == 0:
        default_configs = [
            ProfileConfig(config_key="full_name", config_value="Pemmasani Tejaswini", description="Full Candidate Name"),
            ProfileConfig(config_key="professional_title", config_value="Computer Science Engineer & Python Developer", description="Headline Title"),
            ProfileConfig(config_key="email", config_value="pemmasanitejaswini59@gmail.com", description="Primary Contact Email"),
            ProfileConfig(config_key="phone", config_value="+91 9392576974", description="Contact Phone Number"),
            ProfileConfig(config_key="location", config_value="Gudur, Andhra Pradesh, India", description="Current Location"),
            ProfileConfig(config_key="education_college", config_value="Audisankara College of Engineering & Technology, Gudur", description="Engineering College"),
            ProfileConfig(config_key="education_cgpa", config_value="8.5 / 10.0 CGPA", description="Undergraduate Score"),
            ProfileConfig(config_key="github_url", config_value="https://github.com/tejaswini-pemmasani", description="GitHub Profile URL"),
            ProfileConfig(config_key="linkedin_url", config_value="https://linkedin.com/in/tejaswini-pemmasani-cse", description="LinkedIn Profile URL")
        ]
        db.session.add_all(default_configs)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
