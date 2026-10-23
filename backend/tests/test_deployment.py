import os
import unittest
from unittest.mock import patch
os.environ["DATABASE_URL"] = "sqlite://"
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects import postgresql
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.db.engine import get_session
from app.models import User, SearchLog
from app.services.firebase_auth import verify_token
from app.core.config import settings


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        SQLModel.metadata.create_all(self.engine)
        def session_override():
            with Session(self.engine) as session:
                yield session
        app.dependency_overrides[get_session] = session_override
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()

    def login(self, role="student", active=True):
        with Session(self.engine) as session:
            session.add(User(firebase_uid="test-uid", email="test@example.com", full_name="Test", role=role, is_active=active))
            session.commit()
        app.dependency_overrides[verify_token] = lambda: {"uid": "test-uid", "email": "test@example.com"}

    def test_public_catalog_and_health(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/books/").json(), [])

    def test_anonymous_cannot_change_or_read_admin_data(self):
        for method, path in [("get", "/api/v1/admin/students"), ("post", "/api/v1/transactions/issue"), ("post", "/api/v1/admin/demo-presentation-seed"), ("put", "/api/v1/books/test/update-location")]:
            response = getattr(self.client, method)(path, json={} if method != "get" else None) if method != "get" else self.client.get(path)
            self.assertIn(response.status_code, [401, 403], path)

    def test_student_cannot_access_admin_or_circulation(self):
        self.login()
        self.assertEqual(self.client.get("/api/v1/admin/students").status_code, 403)
        self.assertEqual(self.client.post("/api/v1/transactions/return?rfid_tag=test").status_code, 403)

    def test_staff_cannot_access_admin_but_can_reach_circulation(self):
        self.login("staff")
        self.assertEqual(self.client.get("/api/v1/admin/students").status_code, 403)
        self.assertEqual(self.client.post("/api/v1/transactions/return?rfid_tag=test").status_code, 404)

    def test_admin_can_read_but_demo_operations_disabled(self):
        self.login("admin")
        self.assertEqual(self.client.get("/api/v1/admin/students").status_code, 200)
        self.assertEqual(self.client.post("/api/v1/admin/demo-presentation-seed").status_code, 403)

    def test_inactive_admin_denied(self):
        self.login("admin", False)
        self.assertEqual(self.client.get("/api/v1/admin/students").status_code, 403)

    def test_uuid_foreign_key_matches_postgres_user_id(self):
        dialect = postgresql.dialect()
        self.assertEqual(SearchLog.__table__.c.user_id.type.compile(dialect=dialect), User.__table__.c.id.type.compile(dialect=dialect))

    def test_cors_preflight(self):
        allowed = self.client.options("/api/v1/books/", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
        denied = self.client.options("/api/v1/books/", headers={"Origin": "https://untrusted.example", "Access-Control-Request-Method": "GET"})
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(denied.status_code, 400)

    def test_invalid_token_is_rejected(self):
        with patch("app.services.firebase_auth.auth.verify_id_token", side_effect=ValueError("test")):
            response = self.client.get("/api/v1/dashboard", headers={"Authorization": "Bearer invalid"})
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()
