from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# ============================================================================
# 1. Contact & Communication Schemas
# ============================================================================
class ContactFormRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Sender's full name")
    email: EmailStr = Field(..., description="Sender's email address")
    subject: Optional[str] = Field(default="General Inquiry", max_length=200)
    message: str = Field(..., min_length=8, max_length=5000, description="Inquiry content")

class ContactResponse(BaseModel):
    success: bool
    message: str
    inquiry_id: Optional[int] = None
    timestamp: str

# ============================================================================
# 2. Email Spam Detection Schemas
# ============================================================================
class SpamAnalysisRequest(BaseModel):
    email_text: str = Field(..., min_length=3, description="Raw email text to analyze")

class SpamAnalysisResponse(BaseModel):
    is_spam: bool
    prediction: str
    spam_probability: float
    confidence_percentage: float
    detected_keywords: List[str]
    heuristics: Dict[str, Any]
    summary: str

# ============================================================================
# 3. Biometric & Face Attendance Schemas
# ============================================================================
class FaceVerificationRequest(BaseModel):
    student_id: str = Field(..., min_length=1, description="Student registration ID (e.g., CSE2026-042)")
    student_name: str = Field(..., min_length=2, description="Student Full Name")
    image_base64: Optional[str] = Field(default=None, description="Base64 encoded webcam image frame")
    device_id: Optional[str] = Field(default="CAM-GATE-01")

class AttendanceRecordResponse(BaseModel):
    success: bool
    verified: bool
    student_id: str
    student_name: str
    confidence_score: float
    timestamp: str
    status: str
    message: str
    anti_spoof_passed: bool

# ============================================================================
# 4. CAPTCHA Security Schemas
# ============================================================================
class CaptchaGenerateResponse(BaseModel):
    captcha_token: str
    captcha_svg: str
    expires_in_seconds: int

class CaptchaVerifyRequest(BaseModel):
    captcha_token: str
    user_solution: str

class CaptchaVerifyResponse(BaseModel):
    valid: bool
    message: str

# ============================================================================
# 5. Disease Risk Prediction Schemas
# ============================================================================
class DiabetesPredictionRequest(BaseModel):
    pregnancies: int = Field(default=0, ge=0, le=20)
    glucose: float = Field(..., ge=0, le=400, description="Fasting plasma glucose (mg/dL)")
    blood_pressure: float = Field(..., ge=0, le=250, description="Diastolic blood pressure (mm Hg)")
    skin_thickness: float = Field(default=20.0, ge=0, le=100)
    insulin: float = Field(default=80.0, ge=0, le=900)
    bmi: float = Field(..., ge=10.0, le=70.0, description="Body mass index (kg/m²)")
    diabetes_pedigree: float = Field(default=0.45, ge=0.0, le=3.0)
    age: int = Field(..., ge=1, le=120)

class HeartDiseasePredictionRequest(BaseModel):
    age: int = Field(..., ge=18, le=110)
    sex: int = Field(..., ge=0, le=1, description="1=Male, 0=Female")
    chest_pain_type: int = Field(..., ge=0, le=3, description="0: Typical Angina, 1: Atypical, 2: Non-anginal, 3: Asymptomatic")
    resting_bp: float = Field(..., ge=80, le=250)
    cholesterol: float = Field(..., ge=100, le=600)
    fasting_blood_sugar: int = Field(default=0, ge=0, le=1)
    resting_ecg: int = Field(default=0, ge=0, le=2)
    max_heart_rate: float = Field(..., ge=50, le=240)
    exercise_induced_angina: int = Field(default=0, ge=0, le=1)
    st_depression: float = Field(default=0.0, ge=0.0, le=10.0)

class DiseaseRiskResponse(BaseModel):
    condition: str
    risk_level: str
    probability_percentage: float
    primary_risk_factors: List[str]
    recommendations: List[str]
    status: str

# ============================================================================
# 6. AI Assistant Schemas
# ============================================================================
class AssistantQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question about Tejaswini's profile or projects")

class AssistantQueryResponse(BaseModel):
    answer: str
    category: str
    confidence: float
    suggested_actions: List[str]
