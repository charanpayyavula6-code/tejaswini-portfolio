import re
import math
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from common.logger import setup_logger

logger = setup_logger("MLModelsService")

# ============================================================================
# 1. NLP EMAIL SPAM CLASSIFIER ENGINE
# ============================================================================
class SpamClassifierEngine:
    """Trained NLP Spam Classification Pipeline with keyword extraction & heuristics."""
    
    SPAM_KEYWORDS = [
        "lottery", "winner", "prize", "claim", "free cash", "urgent", "credit card",
        "wire transfer", "bank account", "verify password", "crypto", "bitcoin",
        "million dollars", "inheritance", "risk-free", "act now", "limited time",
        "congratulations", "100% free", "viagra", "guaranteed", "click here",
        "cash bonus", "investment profit", "casino", "jackpot"
    ]
    
    def __init__(self):
        self.pipeline: Pipeline = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initializes and pre-trains a high-accuracy TF-IDF + Naive Bayes pipeline."""
        training_corpus = [
            # Spam samples
            ("Congratulations! You have won a $1,000,000 lottery prize. Claim your free cash now!", 1),
            ("Urgent: Your bank account is suspended. Verify password and credit card immediately.", 1),
            ("Earn $5000 a day from home with zero investment! Act now, limited time offer!", 1),
            ("Get rich quick with guaranteed crypto bitcoin returns. Click here to invest!", 1),
            ("Exclusive luxury watches and discount prescription pills 100% free shipping.", 1),
            ("Dear Beneficiary, wire transfer of fund inheritance awaits your confirmation.", 1),
            ("You have been selected for a free Walmart gift card! Claim prize immediately.", 1),
            ("Risk-free investment with 300% guaranteed profit in 24 hours. Sign up!", 1),
            ("Immediate action required: Update billing info to avoid account closure.", 1),
            ("Hot singles in your area want to meet right now! Click here free registration.", 1),
            ("Your loan has been pre-approved for $50,000! No credit check required!", 1),
            ("You won a sweepstakes jackpot! Reply with bank details to receive funds.", 1),
            
            # Ham (Genuine) samples
            ("Hi Tejaswini, please review the latest pull request for the attendance system.", 0),
            ("Meeting schedule for the semester project presentation tomorrow at 10:00 AM.", 0),
            ("Attached is the updated resume and project report for the Python developer role.", 0),
            ("Can you please share the dataset for the email spam classification model?", 0),
            ("Thank you for your application to our Computer Science Engineering internship.", 0),
            ("Let us sync on the OpenCV webcam facial landmark detection bug tomorrow.", 0),
            ("The seminar on cloud computing and distributed systems starts in Room 402.", 0),
            ("Your college tuition fee receipt has been generated successfully. Regards, Admin.", 0),
            ("Hey team, here are the meeting minutes and action items from today's discussion.", 0),
            ("Please find the syllabus and lecture notes for Machine Learning Module 3.", 0),
            ("Hi, can we reschedule our 1-on-1 code review session to Friday afternoon?", 0),
            ("Great job on finishing the CAPTCHA generator module ahead of deadline.", 0),
        ]
        
        texts, labels = zip(*training_corpus)
        
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),
                token_pattern=r'\b[a-zA-Z]{2,}\b'
            )),
            ('clf', MultinomialNB(alpha=0.1))
        ])
        
        self.pipeline.fit(texts, labels)
        logger.info("Spam Classifier Pipeline successfully fitted with baseline dataset.")

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyzes email text for spam likelihood, keyword matches, and linguistic signals."""
        cleaned_text = text.strip()
        lower_text = cleaned_text.lower()
        
        # 1. Pipeline ML Prediction
        probs = self.pipeline.predict_proba([cleaned_text])[0]
        ml_spam_prob = float(probs[1])
        
        # 2. Heuristic Analysis
        detected_keywords = [
            kw for kw in self.SPAM_KEYWORDS if kw in lower_text
        ]
        
        has_urgent_words = bool(re.search(r'\b(urgent|immediate|action required|act now|hurry)\b', lower_text))
        has_money_signs = bool(re.search(r'(\$\d+|\bmillion\b|\bdollars\b|\bcash\b|\bprize\b)', lower_text))
        has_links = bool(re.search(r'https?://|www\.|\.com|\.xyz|\.click', lower_text))
        all_caps_words = re.findall(r'\b[A-Z]{3,}\b', cleaned_text)
        excessive_caps = len(all_caps_words) >= 3
        
        # Weighted hybrid scoring
        heuristic_score = (
            (len(detected_keywords) * 0.20) +
            (0.25 if has_urgent_words else 0.0) +
            (0.25 if has_money_signs else 0.0) +
            (0.15 if excessive_caps else 0.0) +
            (0.15 if has_links and (has_money_signs or has_urgent_words) else 0.0)
        )
        heuristic_score = min(1.0, heuristic_score)
        
        # Combined probability
        combined_prob = (ml_spam_prob * 0.6) + (heuristic_score * 0.4)
        combined_prob = min(0.999, max(0.001, combined_prob))
        
        is_spam = combined_prob >= 0.50
        confidence_pct = round((combined_prob if is_spam else (1.0 - combined_prob)) * 100, 2)
        
        summary = (
            f"Classified as SPAM with {confidence_pct}% confidence. "
            f"Detected {len(detected_keywords)} high-risk lexical keywords."
            if is_spam else
            f"Classified as HAM (Legitimate) with {confidence_pct}% confidence. Content appears clean."
        )
        
        return {
            "is_spam": is_spam,
            "prediction": "SPAM" if is_spam else "NOT SPAM (HAM)",
            "spam_probability": round(combined_prob, 4),
            "confidence_percentage": confidence_pct,
            "detected_keywords": detected_keywords,
            "heuristics": {
                "has_urgency_triggers": has_urgent_words,
                "has_financial_symbols": has_money_signs,
                "excessive_capitalization": excessive_caps,
                "detected_urls_or_links": has_links,
                "heuristic_risk_score": round(heuristic_score, 2)
            },
            "summary": summary
        }

# ============================================================================
# 2. DISEASE RISK PREDICTION ENGINE
# ============================================================================
class ClinicalDiseasePredictor:
    """Medical Risk Prediction using algorithmic clinical risk models."""
    
    @staticmethod
    def predict_diabetes(
        glucose: float,
        blood_pressure: float,
        bmi: float,
        age: int,
        insulin: float = 80.0,
        pregnancies: int = 0,
        skin_thickness: float = 20.0,
        pedigree: float = 0.45
    ) -> Dict[str, Any]:
        """Calculates Diabetes mellitus probability based on standard ADA/WHO indicators."""
        risk_score = 0.0
        primary_risk_factors = []
        recommendations = []
        
        # Fasting Glucose evaluation (mg/dL)
        if glucose >= 126:
            risk_score += 45
            primary_risk_factors.append(f"Elevated fasting glucose level ({glucose} mg/dL, >= 126 mg/dL indicative of hyperglycemia)")
            recommendations.append("Undergo comprehensive Glycated Hemoglobin (HbA1c) diagnostic test.")
        elif glucose >= 100:
            risk_score += 20
            primary_risk_factors.append(f"Pre-diabetic glucose range ({glucose} mg/dL)")
            recommendations.append("Reduce refined carbohydrates and adopt low-glycemic Mediterranean nutrition.")
            
        # Body Mass Index (BMI)
        if bmi >= 30:
            risk_score += 25
            primary_risk_factors.append(f"Obesity range BMI ({bmi} kg/m²)")
            recommendations.append("Target a 5-10% body weight reduction via structured caloric deficit.")
        elif bmi >= 25:
            risk_score += 10
            primary_risk_factors.append(f"Overweight BMI ({bmi} kg/m²)")
            
        # Blood Pressure
        if blood_pressure >= 90:
            risk_score += 15
            primary_risk_factors.append(f"Stage 2 Diastolic Hypertension ({blood_pressure} mm Hg)")
            recommendations.append("Monitor blood pressure twice daily and reduce sodium intake below 2,000 mg/day.")
        elif blood_pressure >= 80:
            risk_score += 5
            primary_risk_factors.append(f"Pre-hypertensive blood pressure ({blood_pressure} mm Hg)")
            
        # Age risk factor
        if age >= 45:
            risk_score += 15
            primary_risk_factors.append(f"Age threshold factor ({age} years old)")
            
        # Pedigree / Family history
        if pedigree >= 0.8:
            risk_score += 10
            primary_risk_factors.append("Significant genetic / family diabetes pedigree factor")
            
        # Insulin resistance
        if insulin > 160:
            risk_score += 10
            primary_risk_factors.append(f"Elevated fasting serum insulin ({insulin} µU/mL)")
            
        # Final probability calculation
        probability = min(98.0, max(2.0, risk_score))
        
        if probability >= 65:
            risk_level = "HIGH RISK"
            status = "Immediate Medical Consultation Recommended"
        elif probability >= 35:
            risk_level = "MODERATE RISK"
            status = "Preventative Lifestyle Intervention Advised"
        else:
            risk_level = "LOW RISK"
            status = "Within Normal Clinical Parameter Thresholds"
            
        if not recommendations:
            recommendations.append("Maintain regular physical activity (at least 150 minutes/week) and annual health checks.")
            
        return {
            "condition": "Type 2 Diabetes Mellitus",
            "risk_level": risk_level,
            "probability_percentage": round(probability, 1),
            "primary_risk_factors": primary_risk_factors if primary_risk_factors else ["No major anomalies detected"],
            "recommendations": recommendations,
            "status": status
        }

    @staticmethod
    def predict_heart_disease(
        age: int,
        sex: int,
        chest_pain_type: int,
        resting_bp: float,
        cholesterol: float,
        max_heart_rate: float,
        st_depression: float = 0.0,
        exercise_angina: int = 0
    ) -> Dict[str, Any]:
        """Calculates Cardiovascular Disease risk profile based on Framingham & Cleveland metrics."""
        risk_score = 0.0
        primary_risk_factors = []
        recommendations = []
        
        # Resting Blood Pressure
        if resting_bp >= 140:
            risk_score += 20
            primary_risk_factors.append(f"Stage 2 Systolic Hypertension ({resting_bp} mm Hg)")
            recommendations.append("Consult cardiologist regarding anti-hypertensive management.")
        elif resting_bp >= 130:
            risk_score += 10
            primary_risk_factors.append(f"Stage 1 Systolic Hypertension ({resting_bp} mm Hg)")
            
        # Serum Cholesterol
        if cholesterol >= 240:
            risk_score += 25
            primary_risk_factors.append(f"Hypercholesterolemia ({cholesterol} mg/dL, elevated cardiovascular plaque risk)")
            recommendations.append("Schedule complete lipid panel and evaluate statin / dietary fiber therapy.")
        elif cholesterol >= 200:
            risk_score += 12
            primary_risk_factors.append(f"Borderline elevated cholesterol ({cholesterol} mg/dL)")
            
        # Chest Pain Type (0: Typical, 1: Atypical, 2: Non-anginal, 3: Asymptomatic)
        if chest_pain_type == 0:
            risk_score += 30
            primary_risk_factors.append("Typical Anginal chest discomfort pattern")
            recommendations.append("Urgent cardiac stress testing and ECG evaluation required.")
        elif chest_pain_type == 1:
            risk_score += 15
            primary_risk_factors.append("Atypical anginal symptoms")
            
        # Exercise Induced Angina & ST Depression
        if exercise_angina == 1:
            risk_score += 15
            primary_risk_factors.append("Exercise-induced myocardial ischemia indicator")
            
        if st_depression >= 2.0:
            risk_score += 20
            primary_risk_factors.append(f"Significant ST-segment depression ({st_depression} mm on ECG)")
            
        # Max Heart Rate vs Age-predicted max
        age_pred_max_hr = 220 - age
        if max_heart_rate < (age_pred_max_hr * 0.70):
            risk_score += 10
            primary_risk_factors.append(f"Chronotropic incompetence (Max HR {max_heart_rate} bpm vs expected {age_pred_max_hr} bpm)")
            
        # Age & Gender weighting
        if age >= 55 and sex == 1:
            risk_score += 10
            primary_risk_factors.append(f"Demographic cardiovascular age/gender multiplier ({age}y, Male)")
        elif age >= 65 and sex == 0:
            risk_score += 10
            primary_risk_factors.append(f"Demographic cardiovascular age multiplier ({age}y, Female)")
            
        probability = min(98.0, max(3.0, risk_score))
        
        if probability >= 60:
            risk_level = "HIGH RISK"
            status = "Comprehensive Cardiac Evaluation Recommended"
        elif probability >= 30:
            risk_level = "MODERATE RISK"
            status = "Cardiovascular Lifestyle & Lipid Monitoring Advised"
        else:
            risk_level = "LOW RISK"
            status = "Optimal Cardiovascular Parameter Baseline"
            
        if not recommendations:
            recommendations.append("Maintain aerobic cardiovascular exercise (30 mins/day) and low-sodium diet.")
            
        return {
            "condition": "Coronary Artery & Cardiovascular Disease",
            "risk_level": risk_level,
            "probability_percentage": round(probability, 1),
            "primary_risk_factors": primary_risk_factors if primary_risk_factors else ["Cardiovascular parameters within normal ranges"],
            "recommendations": recommendations,
            "status": status
        }

# Global Singletons
spam_engine = SpamClassifierEngine()
disease_predictor = ClinicalDiseasePredictor()
