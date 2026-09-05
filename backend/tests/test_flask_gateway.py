import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask_gateway.app import create_app
from flask_gateway.database import db, ContactMessage

class TestFlaskGateway(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

    def test_root_index_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.content_type)

    def test_api_overview_json(self):
        response = self.client.get("/api")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ONLINE")
        self.assertIn("endpoints", data)

    def test_contact_form_submission_success(self):
        payload = {
            "name": "Jane Recruiter",
            "email": "jane.recruiter@techcompany.com",
            "subject": "Interview Invitation",
            "message": "We would love to discuss a Python Developer position at our firm."
        }
        response = self.client.post("/api/contact/submit", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("inquiry_id", data)

    def test_contact_form_validation_failure(self):
        payload = {
            "name": "J",
            "email": "invalid-email-address",
            "message": "Short"
        }
        response = self.client.post("/api/contact/submit", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertTrue(len(data["errors"]) >= 2)

    def test_contact_messages_list(self):
        response = self.client.get("/api/contact/messages")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])

    def test_analytics_tracking(self):
        payload = {
            "endpoint": "/projects",
            "method": "GET",
            "status_code": 200,
            "response_time_ms": 14.5
        }
        response = self.client.post("/api/analytics/track", json=payload)
        self.assertEqual(response.status_code, 201)
        
        stats_res = self.client.get("/api/analytics/stats")
        self.assertEqual(stats_res.status_code, 200)
        stats_data = stats_res.get_json()
        self.assertGreaterEqual(stats_data["total_logged_events"], 1)

if __name__ == "__main__":
    unittest.main()
