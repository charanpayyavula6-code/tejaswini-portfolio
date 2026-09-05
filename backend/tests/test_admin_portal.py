import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask_gateway.app import create_app
from flask_gateway.database import db, ContactMessage

class TestAdminPortal(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

    def _get_auth_header(self, username="admin", password="TejaswiniAdmin2026!"):
        login_res = self.client.post("/api/admin/login", json={
            "username": username,
            "password": password
        })
        token = login_res.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_admin_login_success(self):
        response = self.client.post("/api/admin/login", json={
            "username": "admin",
            "password": "TejaswiniAdmin2026!"
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)

    def test_admin_login_invalid_password(self):
        response = self.client.post("/api/admin/login", json={
            "username": "admin",
            "password": "WrongPassword123"
        })
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.get_json()["success"])

    def test_protected_route_without_token(self):
        response = self.client.get("/api/admin/stats")
        self.assertEqual(response.status_code, 401)

    def test_admin_dashboard_stats(self):
        headers = self._get_auth_header()
        response = self.client.get("/api/admin/stats", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("metrics", data)

    def test_project_crud_lifecycle(self):
        headers = self._get_auth_header()
        
        # 1. CREATE
        new_proj = {
            "title": "Autonomous AI Drone",
            "slug": "autonomous-ai-drone-test",
            "category": "Robotics & AI",
            "overview": "Real-time drone obstacle navigation using YOLOv8.",
            "problem": "Autonomous navigation in unstructured environments.",
            "solution": "Embedded neural networks for edge vision inference.",
            "features": ["Obstacle avoidance", "Live video feed"],
            "technologies": ["Python", "PyTorch", "OpenCV"],
            "repo_url": "https://github.com/teja/drone",
            "is_featured": True,
            "display_order": 5
        }
        create_res = self.client.post("/api/admin/projects", json=new_proj, headers=headers)
        self.assertEqual(create_res.status_code, 201)
        proj_id = create_res.get_json()["project"]["id"]

        # 2. READ via Public API
        pub_res = self.client.get("/api/public/projects")
        self.assertEqual(pub_res.status_code, 200)
        pub_data = pub_res.get_json()
        titles = [p["title"] for p in pub_data["projects"]]
        self.assertIn("Autonomous AI Drone", titles)

        # 3. UPDATE
        update_res = self.client.put(f"/api/admin/projects/{proj_id}", json={
            "title": "Autonomous AI Drone v2 (Enhanced)",
            "display_order": 1
        }, headers=headers)
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()["project"]["title"], "Autonomous AI Drone v2 (Enhanced)")

        # 4. DELETE
        del_res = self.client.delete(f"/api/admin/projects/{proj_id}", headers=headers)
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(del_res.get_json()["success"])

    def test_skill_crud_lifecycle(self):
        headers = self._get_auth_header()
        
        # CREATE
        create_res = self.client.post("/api/admin/skills", json={
            "name": "Docker & Containerization",
            "category": "Tools & Machine Learning",
            "proficiency_pct": 85,
            "display_order": 8
        }, headers=headers)
        self.assertEqual(create_res.status_code, 201)
        skill_id = create_res.get_json()["skill"]["id"]

        # UPDATE
        update_res = self.client.put(f"/api/admin/skills/{skill_id}", json={
            "proficiency_pct": 92
        }, headers=headers)
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()["skill"]["proficiency_pct"], 92)

        # DELETE
        del_res = self.client.delete(f"/api/admin/skills/{skill_id}", headers=headers)
        self.assertEqual(del_res.status_code, 200)

    def test_contact_status_update(self):
        headers = self._get_auth_header()
        with self.app.app_context():
            msg = ContactMessage(
                name="Google Recruiter",
                email="recruiter@google.com",
                subject="Interview",
                message="Invitation to discuss Software Engineer role."
            )
            db.session.add(msg)
            db.session.commit()
            msg_id = msg.id

        update_res = self.client.put(f"/api/admin/contacts/{msg_id}", json={
            "status": "RESPONDED"
        }, headers=headers)
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()["message_record"]["status"], "RESPONDED")

if __name__ == "__main__":
    unittest.main()
