"""Tests for new route behavior: refresh, persistence, image flow, plc heartbeat, ws auth."""
import io
import pytest
from fastapi.testclient import TestClient

from server.main import app
from server.store import store


client = TestClient(app)


def _login(role: str = "engineer") -> str:
    resp = client.post("/api/auth/login", json={"username": role, "password": f"{role}123"})
    return resp.json()["access_token"]


def _auth(role: str = "engineer") -> dict:
    return {"Authorization": f"Bearer {_login(role)}"}


@pytest.fixture(autouse=True)
def _reset_store():
    # Reset in-memory store between tests so totals are deterministic.
    store._mem.clear()
    store._next_id = 1
    yield


class TestRefresh:
    def test_refresh_returns_new_access_token(self):
        login = client.post(
            "/api/auth/login", json={"username": "operator", "password": "operator123"}
        ).json()
        resp = client.post("/api/auth/refresh", json={"refresh_token": login["refresh_token"]})
        assert resp.status_code == 200
        body = resp.json()
        assert body["access_token"] and body["user"]["username"] == "operator"

    def test_refresh_with_access_token_rejected(self):
        login = client.post(
            "/api/auth/login", json={"username": "operator", "password": "operator123"}
        ).json()
        resp = client.post("/api/auth/refresh", json={"refresh_token": login["access_token"]})
        assert resp.status_code == 401

    def test_access_token_cannot_be_used_as_refresh_via_me(self):
        # Conversely, a refresh token should not authorize protected endpoints.
        login = client.post(
            "/api/auth/login", json={"username": "operator", "password": "operator123"}
        ).json()
        resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {login['refresh_token']}"},
        )
        assert resp.status_code == 401


class TestInspectionFlow:
    def test_create_then_list_and_get(self):
        h = _auth()
        r = client.post(
            "/api/inspection",
            json={"part_id": "PT-001", "result": "OK", "confidence": 0.92},
            headers=h,
        )
        assert r.status_code == 200
        insp = r.json()
        assert insp["id"] >= 1 and insp["result"] == "OK"

        listed = client.get("/api/inspections", headers=h).json()
        assert listed["total"] == 1 and listed["items"][0]["part_id"] == "PT-001"

        single = client.get(f"/api/inspection/{insp['id']}", headers=h).json()
        assert single["part_id"] == "PT-001"

    def test_list_filters_by_result(self):
        h = _auth()
        client.post("/api/inspection", json={"part_id": "A", "result": "OK"}, headers=h)
        client.post(
            "/api/inspection",
            json={"part_id": "B", "result": "NG", "defect_class": "Scratch"},
            headers=h,
        )
        ng = client.get("/api/inspections?result=NG", headers=h).json()
        assert ng["total"] == 1 and ng["items"][0]["defect_class"] == "Scratch"

    def test_invalid_result_rejected(self):
        r = client.post(
            "/api/inspection",
            json={"part_id": "X", "result": "BAD"},
            headers=_auth(),
        )
        assert r.status_code == 422

    def test_get_unknown_inspection_404(self):
        r = client.get("/api/inspection/999999", headers=_auth())
        assert r.status_code == 404

    def test_stats_reflect_persisted_data(self):
        h = _auth()
        for _ in range(3):
            client.post("/api/inspection", json={"part_id": "P", "result": "OK"}, headers=h)
        client.post(
            "/api/inspection",
            json={"part_id": "P", "result": "NG", "defect_class": "Dent"},
            headers=h,
        )
        s = client.get("/api/stats", headers=h).json()
        assert s["total"] == 4 and s["ok"] == 3 and s["ng"] == 1
        assert s["rate"] == 75.0

    def test_defect_breakdown(self):
        h = _auth()
        client.post(
            "/api/inspection",
            json={"part_id": "P", "result": "NG", "defect_class": "Scratch"},
            headers=h,
        )
        client.post(
            "/api/inspection",
            json={"part_id": "P", "result": "NG", "defect_class": "Scratch"},
            headers=h,
        )
        client.post(
            "/api/inspection",
            json={"part_id": "P", "result": "NG", "defect_class": "Dent"},
            headers=h,
        )
        out = client.get("/api/stats/defects", headers=h).json()
        names = {row["name"]: row["value"] for row in out}
        assert names == {"Scratch": 2, "Dent": 1}

    def test_trend_returns_24_buckets(self):
        out = client.get("/api/stats/trend", headers=_auth()).json()
        assert len(out) == 24


class TestImages:
    def test_upload_and_fetch_local_fallback(self):
        h = _auth()
        files = {"file": ("test.jpg", b"\xff\xd8\xff\xd9", "image/jpeg")}
        r = client.post("/api/images/upload", headers=h, files=files)
        assert r.status_code == 200, r.text
        name = r.json()["name"]
        # fetch raw bytes via fallback streaming endpoint
        r2 = client.get(f"/api/images/{name}/data", headers=h)
        assert r2.status_code == 200
        assert r2.content == b"\xff\xd8\xff\xd9"

    def test_upload_rejects_unsupported_type(self):
        files = {"file": ("a.txt", b"hello", "text/plain")}
        r = client.post("/api/images/upload", headers=_auth(), files=files)
        assert r.status_code == 415


class TestPLCHeartbeat:
    def test_heartbeat_updates_status(self):
        h = _auth()
        r = client.post(
            "/api/plc/heartbeat",
            json={"connected": True, "state": "IDLE", "last_error": None},
            headers=h,
        )
        assert r.status_code == 200
        snap = client.get("/api/plc/status", headers=h).json()
        assert snap["connected"] is True and snap["state"] == "IDLE"

    def test_status_requires_auth(self):
        r = client.get("/api/plc/status")
        assert r.status_code == 401


class TestWebSocketAuth:
    def test_live_ws_rejects_missing_token(self):
        with pytest.raises(Exception):
            with client.websocket_connect("/api/ws/live") as ws:
                ws.receive_text()

    def test_live_ws_accepts_valid_token(self):
        token = _login("operator")
        with client.websocket_connect(f"/api/ws/live?token={token}") as ws:
            msg = ws.receive_json()
            assert msg["type"] in ("plc_status", "ping")


class TestHealth:
    def test_health_reports_store_mode(self):
        body = client.get("/api/health").json()
        assert body["store"] in ("in-memory", "postgres")
        assert "postgres" in body and "redis" in body and "minio" in body
