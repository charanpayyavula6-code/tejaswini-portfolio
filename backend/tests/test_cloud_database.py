import unittest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from common.cloud_db import CloudDatabaseManager, cloud_db
from flask_gateway.app import create_app

class CloudDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def _get_auth_header(self, username="admin", password="TejaswiniAdmin2026!"):
        login_res = self.client.post("/api/admin/login", json={
            "username": username,
            "password": password
        })
        token = login_res.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}


    def test_uri_masking(self):
        uri = "mongodb+srv://admin_user:SuperSecretPassword123@cluster0.abcde.mongodb.net/testdb"
        masked = CloudDatabaseManager.mask_uri(uri)
        self.assertIn("admin_user:******@cluster0.abcde.mongodb.net", masked)
        self.assertNotIn("SuperSecretPassword123", masked)

    def test_database_status_endpoint(self):
        res = self.client.get("/api/admin/database/status", headers=self._get_auth_header())
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("database_status", data)
        status = data["database_status"]
        self.assertIn("mode", status)
        self.assertIn("local_counts", status)

    def test_test_connection_endpoint_empty_uri(self):
        res = self.client.post(
            "/api/admin/database/test-connection",
            headers=self._get_auth_header(),
            json={"uri": ""}
        )
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("LOCAL_SQLITE_FALLBACK", data.get("type", ""))

    @patch("common.cloud_db.MongoClient")
    def test_test_connection_endpoint_mock_success(self, mock_mongo):
        mock_instance = MagicMock()
        mock_instance.admin.command.return_value = {"ok": 1}
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["portfolio_projects", "contact_messages"]
        mock_instance.__getitem__.return_value = mock_db
        mock_mongo.return_value = mock_instance

        res = self.client.post(
            "/api/admin/database/test-connection",
            headers=self._get_auth_header(),
            json={"uri": "mongodb+srv://user:pass@cluster0.xyz.mongodb.net/tejaswini_portfolio"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["connected"])
        self.assertEqual(data["type"], "MONGODB_ATLAS_CLOUD")

    def test_cloud_db_telemetry_and_inquiry_helpers(self):
        # Test helper functions execute gracefully without errors even in fallback mode
        inquiry_result = cloud_db.save_inquiry(
            name="Recruiter Jane",
            email="jane@techcorp.com",
            subject="Python Role",
            message="Hi Tejaswini, interested in your profile."
        )
        self.assertIsInstance(inquiry_result, bool)

        att_result = cloud_db.record_attendance(
            student_id="STU-2026-001",
            student_name="Pemmasani Tejaswini",
            confidence=0.965,
            status="ATTENDANCE_MARKED_PRESENT"
        )
        self.assertIsInstance(att_result, bool)

        ai_result = cloud_db.record_ai_telemetry(
            module="ai_assistant",
            request_data={"query": "projects"},
            response_data={"category": "Projects"},
            latency_ms=1.2
        )
        self.assertIsInstance(ai_result, bool)

if __name__ == "__main__":
    unittest.main()
