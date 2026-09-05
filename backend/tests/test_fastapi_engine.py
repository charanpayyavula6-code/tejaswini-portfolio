import unittest
import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from starlette.testclient import TestClient
from fastapi_engine.main import app

class TestFastAPIEngine(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "HEALTHY")

    def test_spam_detection_spam(self):
        payload = {"email_text": "Congratulations! You won a $1,000,000 lottery cash prize! Click here to claim your bitcoin wire transfer now!"}
        response = self.client.post("/api/spam/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_spam"])
        self.assertEqual(data["prediction"], "SPAM")
        self.assertGreater(data["confidence_percentage"], 50.0)
        self.assertTrue(len(data["detected_keywords"]) > 0)

    def test_spam_detection_ham(self):
        payload = {"email_text": "Hi Tejaswini, please review the latest pull request for the attendance system code review."}
        response = self.client.post("/api/spam/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_spam"])
        self.assertEqual(data["prediction"], "NOT SPAM (HAM)")

    def test_face_biometric_verification(self):
        payload = {
            "student_id": "CSE2026-001",
            "student_name": "Pemmasani Tejaswini",
            "device_id": "TEST-CAM-01"
        }
        response = self.client.post("/api/face/verify-attendance", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["verified"])
        self.assertEqual(data["status"], "ATTENDANCE_MARKED_PRESENT")
        self.assertGreater(data["confidence_score"], 0.80)

    def test_captcha_generation_and_verification(self):
        # 1. Generate
        gen_response = self.client.get("/api/captcha/generate")
        self.assertEqual(gen_response.status_code, 200)
        gen_data = gen_response.json()
        self.assertIn("captcha_token", gen_data)
        self.assertIn("<svg", gen_data["captcha_svg"])
        
        token = gen_data["captcha_token"]
        
        # 2. Verify invalid response
        bad_verify = self.client.post("/api/captcha/verify", json={
            "captcha_token": token,
            "user_solution": "WRONG1"
        })
        self.assertEqual(bad_verify.status_code, 200)
        self.assertFalse(bad_verify.json()["valid"])

    def test_diabetes_prediction(self):
        payload = {
            "glucose": 155.0,
            "blood_pressure": 88.0,
            "bmi": 32.5,
            "age": 52
        }
        response = self.client.post("/api/disease/predict-diabetes", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["condition"], "Type 2 Diabetes Mellitus")
        self.assertIn(data["risk_level"], ["HIGH RISK", "MODERATE RISK"])

    def test_heart_disease_prediction(self):
        payload = {
            "age": 60,
            "sex": 1,
            "chest_pain_type": 0,
            "resting_bp": 150.0,
            "cholesterol": 260.0,
            "max_heart_rate": 110.0,
            "st_depression": 2.5,
            "exercise_induced_angina": 1
        }
        response = self.client.post("/api/disease/predict-heart", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["condition"], "Coronary Artery & Cardiovascular Disease")
        self.assertEqual(data["risk_level"], "HIGH RISK")

    def test_ai_assistant_chat(self):
        payload = {"query": "Tell me about Tejaswini's projects and skills"}
        response = self.client.post("/api/assistant/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Face Recognition", data["answer"])
        self.assertGreater(data["confidence"], 0.80)

if __name__ == "__main__":
    unittest.main()
