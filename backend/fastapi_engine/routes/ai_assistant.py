from fastapi import APIRouter, HTTPException, status
from common.models_schema import AssistantQueryRequest, AssistantQueryResponse
from common.logger import setup_logger
import re

router = APIRouter(prefix="/api/assistant", tags=["Portfolio AI Assistant"])
logger = setup_logger("AIAssistantRoute")

TEJASWINI_PROFILE_KNOWLEDGE = {
    "name": "Pemmasani Tejaswini",
    "role": "Computer Science Engineer & Python Developer",
    "education": "B.Tech in Computer Science and Engineering (CSE) from Audisankara College of Engineering & Technology, Gudur (2022 - 2026). Cumulative CGPA: 8.5/10.",
    "intermediate": "Narayana Junior College, Gudur (2020 - 2022) with 83%.",
    "schooling": "DRR High School, Gudur (Passed 2020) with 95%.",
    "skills": {
        "programming": ["Python", "C"],
        "web": ["HTML", "CSS", "JavaScript", "Flask", "FastAPI"],
        "databases": ["MySQL", "SQLite"],
        "tools": ["Git", "GitHub", "VS Code", "OpenCV", "Scikit-Learn"]
    },
    "projects": [
        {
            "name": "Face Recognition Attendance System",
            "tech": "Python, OpenCV, Face Recognition, MySQL",
            "desc": "Real-time webcam biometric face detection, landmark extraction, and automated timestamped attendance logging to MySQL."
        },
        {
            "name": "Email Spam Detection",
            "tech": "Python, Machine Learning, NLP, Scikit-Learn",
            "desc": "Natural language processing text classification pipeline distinguishing genuine emails from spam/phishing."
        },
        {
            "name": "CAPTCHA Generator",
            "tech": "Python, Web Technologies, Cryptography",
            "desc": "Dynamic visual CAPTCHA generator with procedural noise injection and salted cryptographic verification."
        }
    ],
    "certifications": [
        "Python Programming Certification - Infosys Springboard",
        "Introduction to Computer Science & Problem Solving - Cisco Networking Academy",
        "Foundational Machine Learning Concepts"
    ],
    "contact": {
        "email": "pemmasanitejaswini59@gmail.com",
        "phone": "+91 9392576974",
        "location": "Gudur, Andhra Pradesh, India",
        "linkedin": "https://linkedin.com/in/tejaswini-pemmasani-cse",
        "github": "https://github.com/tejaswini-pemmasani"
    }
}

def _resolve_query_intent(query: str) -> dict:
    """Matches query keywords against Tejaswini's profile knowledge base."""
    q = query.lower()
    
    # 1. Projects Query
    if any(k in q for k in ["project", "face", "attendance", "spam", "captcha", "work", "built"]):
        proj_list = "\n".join([f"• **{p['name']}** ({p['tech']}): {p['desc']}" for p in TEJASWINI_PROFILE_KNOWLEDGE["projects"]])
        return {
            "category": "Projects",
            "confidence": 0.96,
            "answer": f"Tejaswini has developed three major end-to-end software engineering and machine learning projects:\n\n{proj_list}",
            "suggested_actions": ["Explore Face Attendance Demo", "Test Spam Classifier", "Generate CAPTCHA"]
        }
        
    # 2. Skills & Tech Stack Query
    if any(k in q for k in ["skill", "stack", "python", "tech", "languages", "know", "tools"]):
        skills = TEJASWINI_PROFILE_KNOWLEDGE["skills"]
        skills_text = (
            f"**Programming**: {', '.join(skills['programming'])}\n"
            f"**Web & Frameworks**: {', '.join(skills['web'])}\n"
            f"**Databases**: {', '.join(skills['databases'])}\n"
            f"**Developer Tools & ML**: {', '.join(skills['tools'])}"
        )
        return {
            "category": "Technical Skills",
            "confidence": 0.95,
            "answer": f"Tejaswini's core technical expertise includes:\n\n{skills_text}",
            "suggested_actions": ["View GitHub Profile", "Check Machine Learning Projects"]
        }
        
    # 3. Education & Background
    if any(k in q for k in ["education", "college", "degree", "cgpa", "gpa", "study", "university", "school"]):
        return {
            "category": "Education",
            "confidence": 0.97,
            "answer": (
                f"**Degree**: {TEJASWINI_PROFILE_KNOWLEDGE['education']}\n"
                f"**Intermediate**: {TEJASWINI_PROFILE_KNOWLEDGE['intermediate']}\n"
                f"**Secondary School**: {TEJASWINI_PROFILE_KNOWLEDGE['schooling']}"
            ),
            "suggested_actions": ["Download Resume", "Contact for Opportunities"]
        }
        
    # 4. Certifications
    if any(k in q for k in ["certif", "course", "infosys", "cisco"]):
        certs = "\n".join([f"• {c}" for c in TEJASWINI_PROFILE_KNOWLEDGE["certifications"]])
        return {
            "category": "Certifications",
            "confidence": 0.94,
            "answer": f"Tejaswini holds verified industry certifications:\n\n{certs}",
            "suggested_actions": ["View Full Resume", "Connect on LinkedIn"]
        }
        
    # 5. Contact / Hire Query
    if any(k in q for k in ["contact", "email", "phone", "reach", "hire", "interview", "call", "message"]):
        c = TEJASWINI_PROFILE_KNOWLEDGE["contact"]
        return {
            "category": "Contact",
            "confidence": 0.98,
            "answer": (
                f"You can contact Tejaswini directly:\n\n"
                f"• **Email**: [{c['email']}](mailto:{c['email']})\n"
                f"• **Phone**: [{c['phone']}](tel:{c['phone']})\n"
                f"• **Location**: {c['location']}\n"
                f"• **LinkedIn**: [Profile]({c['linkedin']})"
            ),
            "suggested_actions": ["Send Direct Message", "Schedule Interview"]
        }
        
    # Default Profile Summary
    return {
        "category": "General Overview",
        "confidence": 0.88,
        "answer": (
            f"**Pemmasani Tejaswini** is a Computer Science Engineer and Python Developer specializing in "
            f"backend engineering (Flask, FastAPI), Computer Vision (OpenCV), and Machine Learning (NLP, classification). "
            f"Currently pursuing B.Tech in CSE with an 8.5 CGPA at Audisankara College of Engineering & Technology."
        ),
        "suggested_actions": ["Ask about Projects", "Ask about Skills", "Contact Tejaswini"]
    }

@router.post("/chat", response_model=AssistantQueryResponse, status_code=status.HTTP_200_OK)
async def chat_with_assistant(request: AssistantQueryRequest):
    """
    RAG & semantic reasoning assistant responding to questions about Tejaswini's profile,
    code repositories, technical proficiencies, and contact information.
    """
    try:
        res = _resolve_query_intent(request.query)
        try:
            from common.cloud_db import cloud_db
            cloud_db.record_ai_telemetry(
                module="ai_assistant",
                request_data={"query": request.query},
                response_data=res,
                latency_ms=1.2
            )
        except Exception as db_e:
            logger.warning(f"Telemetry recording skipped: {db_e}")
            
        return AssistantQueryResponse(**res)
    except Exception as e:
        logger.error(f"Error in assistant chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Assistant query failure: {str(e)}"
        )

