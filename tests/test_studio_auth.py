"""PIN dello Studio: senza sessione non passa niente, il PIN si sceglie solo dal PC."""
import pytest
from fastapi.testclient import TestClient

import api.server as server
import studio_auth

STUDIO = "http://192.168.1.20:3000"


@pytest.fixture()
def client(monkeypatch):
    # Every test starts with no PIN chosen and no failed attempts.
    studio_auth._store_path.unlink(missing_ok=True)
    studio_auth._failures.clear()
    yield TestClient(server.app)
    studio_auth._store_path.unlink(missing_ok=True)


def _as_pc(monkeypatch):
    # TestClient calls from "testclient": make it count as the PC itself.
    monkeypatch.setattr(studio_auth, "LOCAL_HOSTS", studio_auth.LOCAL_HOSTS | {"testclient"})


def test_without_the_pin_nothing_comes_through(client):
    for path in ("/pieces", "/history", "/files/qualsiasi.jpg", "/skills"):
        assert client.get(path).status_code == 401
    assert client.delete("/pieces/qualsiasi").status_code == 401
    assert client.get("/auth/status").json() == {"configured": False, "logged_in": False, "can_setup": False}


def test_the_pin_is_chosen_only_from_the_pc(client, monkeypatch):
    assert client.post("/auth/setup", json={"pin": "482913"}).status_code == 403
    _as_pc(monkeypatch)
    assert client.post("/auth/setup", json={"pin": "12345"}).status_code == 400
    assert client.post("/auth/setup", json={"pin": "48a913"}).status_code == 400
    assert client.post("/auth/setup", json={"pin": "482913"}).status_code == 200
    assert client.get("/pieces").status_code == 200  # the PC is signed in right away
    assert client.post("/auth/setup", json={"pin": "000000"}).status_code == 409
    assert "482913" not in studio_auth._store_path.read_text(encoding="utf-8")


def test_another_device_signs_in_with_the_pin(client, monkeypatch):
    _as_pc(monkeypatch)
    TestClient(server.app).post("/auth/setup", json={"pin": "482913"})
    monkeypatch.setattr(studio_auth, "LOCAL_HOSTS", {"127.0.0.1"})

    assert client.post("/auth/login", json={"pin": "000000"}).status_code == 401
    assert client.get("/pieces").status_code == 401
    assert client.post("/auth/login", json={"pin": "482913"}).status_code == 200
    assert client.get("/pieces").status_code == 200
    assert client.get("/auth/status").json()["logged_in"] is True
    client.post("/auth/logout")
    assert client.get("/pieces").status_code == 401


def test_five_wrong_pins_lock_the_door(client, monkeypatch):
    _as_pc(monkeypatch)
    TestClient(server.app).post("/auth/setup", json={"pin": "482913"})
    for _ in range(studio_auth.MAX_FAILURES):
        assert client.post("/auth/login", json={"pin": "111111"}).status_code == 401
    # Locked: even the right PIN waits.
    assert client.post("/auth/login", json={"pin": "482913"}).status_code == 429


def test_a_forged_or_expired_cookie_does_not_open(client, monkeypatch):
    _as_pc(monkeypatch)
    TestClient(server.app).post("/auth/setup", json={"pin": "482913"})
    client.cookies.set(studio_auth.COOKIE_NAME, "9999999999.firma-inventata")
    assert client.get("/pieces").status_code == 401
    client.cookies.set(studio_auth.COOKIE_NAME, "1.abc")
    assert client.get("/pieces").status_code == 401


def test_only_the_studio_pages_may_call_the_api(client):
    ask = {"Access-Control-Request-Method": "DELETE"}
    allowed = client.options("/pieces/x", headers={"Origin": STUDIO, **ask})
    assert allowed.headers.get("access-control-allow-origin") == STUDIO
    assert allowed.headers.get("access-control-allow-credentials") == "true"
    for origin in ("https://sito-qualunque.com", "http://100.64.1.2.evil.com:3000"):
        refused = client.options("/pieces/x", headers={"Origin": origin, **ask})
        assert "access-control-allow-origin" not in refused.headers
    # A 401 still carries CORS, so the Studio page can show the PIN screen.
    locked = client.get("/pieces", headers={"Origin": STUDIO})
    assert locked.status_code == 401 and locked.headers.get("access-control-allow-origin") == STUDIO
    # Without Origin (an <img>) the answer still says it varies by Origin, so the
    # browser does not reuse it for the share button's fetch.
    assert "origin" in client.get("/pieces").headers.get("vary", "").lower()
