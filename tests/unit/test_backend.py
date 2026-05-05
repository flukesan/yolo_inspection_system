"""Auth and API tests."""
import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

class TestAuth:
    def test_login_engineer(self):
        resp = client.post("/api/auth/login", json={"username":"engineer","password":"engineer123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "engineer"

    def test_login_wrong_password(self):
        resp = client.post("/api/auth/login", json={"username":"engineer","password":"wrongpass"})
        assert resp.status_code == 401

    def test_me_without_token(self):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_with_token(self):
        login_resp = client.post("/api/auth/login", json={"username":"operator","password":"operator123"})
        token = login_resp.json()["access_token"]
        resp = client.get("/api/auth/me", headers={"Authorization":f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["role"] == "operator"

    def test_protected_route_no_token(self):
        resp = client.get("/api/stats")
        assert resp.status_code == 401

class TestAPI:
    def _auth_header(self, role="engineer"):
        resp = client.post("/api/auth/login", json={"username":role,"password":f"{role}123"})
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    def test_health(self):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_stats(self):
        resp = client.get("/api/stats", headers=self._auth_header())
        assert resp.status_code == 200
        assert "rate" in resp.json()

    def test_create_inspection(self):
        resp = client.post("/api/inspection", json={"part_id":"T001","result":"OK","confidence":0.95}, headers=self._auth_header())
        assert resp.status_code == 200

    def test_plc_status(self):
        resp = client.get("/api/plc/status", headers=self._auth_header())
        assert resp.status_code == 200
        assert "connected" in resp.json()
