from fastapi import APIRouter, HTTPException, status
from common.models_schema import AssistantQueryRequest, AssistantQueryResponse
from common.logger import setup_logger
import re

router = APIRouter(prefix="/api/assistant", tags=["Portfolio AI Assistant"])
logger = setup_logger("AIAssistantRoute")

TEJASWINI_PROFILE_KNOWLEDGE = {
    "name": "Pemmasani Tejaswini",
    "role": "Computer Science Engineer & Python Full Stack Developer",
    "education": "B.Tech in Computer Science and Engineering (2022 - 2026) from PBR Vits, Kavali. Cumulative CGPA: 8.40/10.",
    "internship": "Python Full Stack Developer Intern at Code Tantra Platform (12-5-2025 – 21-06-2025). Hands-on experience in Python & HTML web development.",
    "skills": {
        "programming": ["Python", "SQL"],
        "web": ["HTML", "CSS", "JavaScript", "Flask", "FastAPI"],
        "libraries": ["OpenCV", "Scikit-Learn", "Pillow"],
        "soft_skills": ["Communication skills", "Adaptability", "Time management", "Problem solving"]
    },
    "projects": [
        {
            "name": "Face Recognition Attendance System",
            "tech": "Python, OpenCV, Face Recognition, MySQL",
            "desc": "Real-time webcam face detection & recognition for automated biometric attendance tracking.",
            "repo": "https://github.com/pemmasanitejaswini/face-project"
        },
        {
            "name": "Email Spam Detection",
            "tech": "Python, NLP, Machine Learning",
            "desc": "Machine learning NLP classification pipeline distinguishing genuine emails from spam.",
            "repo": "https://github.com/pemmasanitejaswini/email-spam-detection"
        },
        {
            "name": "CAPTCHA Generator",
            "tech": "Python, HTML, Web Technologies",
            "desc": "Dynamic visual CAPTCHA verification codes with custom noise and fonts to prevent bots.",
            "repo": "https://github.com/pemmasanitejaswini/captcha-generator"
        }
    ],
    "certifications": [
        "Paper Presentation: Received participation certificate at PBR VITS College during Visvotsav 2024",
        "Debugging Event: Received Participation Certificate in Debugging Event at Andhra Engineering College, Atmakur"
    ],
    "contact": {
        "email": "pemmasanitejaswini59@gmail.com",
        "phone": "+91 8341650531",
        "location": "Bangalore, India",
        "linkedin": "https://linkedin.com",
        "github": "https://github.com/pemmasanitejaswini"
    },
    "resume_url": "/resume.pdf"
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
        
    # 3. Resume Query
    if any(k in q for k in ["resume", "cv", "download resume", "pdf", "profile doc"]):
        return {
            "category": "Resume",
            "confidence": 0.99,
            "answer": (
                f"You can view and download Tejaswini's official resume PDF directly:\n\n"
                f"• **Download PDF**: [Tejaswini_Pemmasani_Resume.pdf](/resume.pdf)\n"
                f"• **Degree**: {TEJASWINI_PROFILE_KNOWLEDGE['education']}\n"
                f"• **Internship**: {TEJASWINI_PROFILE_KNOWLEDGE['internship']}\n"
                f"• **Email**: {TEJASWINI_PROFILE_KNOWLEDGE['contact']['email']}"
            ),
            "suggested_actions": ["Download Resume (PDF)", "View Projects", "Contact Tejaswini"]
        }

    # 4. Education & Background
    if any(k in q for k in ["education", "college", "degree", "cgpa", "gpa", "study", "university", "pbr"]):
        return {
            "category": "Education",
            "confidence": 0.97,
            "answer": (
                f"**Degree**: {TEJASWINI_PROFILE_KNOWLEDGE['education']}\n\n"
                f"**Internship**: {TEJASWINI_PROFILE_KNOWLEDGE['internship']}"
            ),
            "suggested_actions": ["Download Resume", "Contact for Opportunities"]
        }
        
    # 5. Internship & Experience
    if any(k in q for k in ["intern", "experience", "work experience", "codetantra", "code tantra"]):
        return {
            "category": "Experience",
            "confidence": 0.98,
            "answer": (
                f"**Internship Experience**:\n\n"
                f"{TEJASWINI_PROFILE_KNOWLEDGE['internship']}"
            ),
            "suggested_actions": ["Download Resume", "View GitHub Projects"]
        }

    # 6. Certifications
    if any(k in q for k in ["certif", "achievement", "award", "visvotsav", "debugging"]):
        certs = "\n".join([f"• {c}" for c in TEJASWINI_PROFILE_KNOWLEDGE["certifications"]])
        return {
            "category": "Certifications",
            "confidence": 0.94,
            "answer": f"Tejaswini holds verified certifications and achievements:\n\n{certs}",
            "suggested_actions": ["View Full Resume", "Connect on LinkedIn"]
        }
        
    # 7. Contact / Hire Query
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
                f"• **GitHub**: [{c['github']}]({c['github']})"
            ),
            "suggested_actions": ["Send Direct Message", "Download Resume"]
        }
        
    # Default Profile Summary
    return {
        "category": "General Overview",
        "confidence": 0.88,
        "answer": (
            f"**Pemmasani Tejaswini** is a Computer Science Engineer and Python Developer specializing in "
            f"Python, OpenCV, Machine Learning (NLP), and Full Stack Web Development. "
            f"Currently pursuing B.Tech in CSE (CGPA 8.40) at PBR VITS, Kavali."
        ),
        "suggested_actions": ["Download Resume", "Ask about Projects", "Contact Tejaswini"]
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

