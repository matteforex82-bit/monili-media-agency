"""Pubblicazione su Instagram tramite Zernio: senza rete e senza chiavi vere."""

import pytest
from fastapi.testclient import TestClient

import reel_studio
import zernio
from api import server


class FakeResponse:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = body or {}
        self.ok = status < 400

    def json(self):
        return self._body


@pytest.fixture(autouse=True)
def key(monkeypatch):
    monkeypatch.setenv("ZERNIO_API_KEY", "sk_test")


def test_reel_payload_has_caption_first_comment_and_ai_label():
    payload = zernio.post_payload("reel", "acc1", "https://media/x.mp4", "Ciao #imoniliravenna", "Scrivici", True)
    data = payload["platforms"][0]["platformSpecificData"]
    assert payload["content"] == "Ciao #imoniliravenna"
    assert payload["publishNow"] is True
    assert data["firstComment"] == "Scrivici" and data["isAiGenerated"] is True
    assert "contentType" not in data  # un video senza contentType è un Reel


def test_story_payload_has_no_caption_and_no_first_comment():
    payload = zernio.post_payload("story", "acc1", "https://media/x.mp4", "testo", "commento", False)
    assert "content" not in payload
    data = payload["platforms"][0]["platformSpecificData"]
    assert data == {"contentType": "story"}


def test_caption_longer_than_instagram_allows_is_refused():
    with pytest.raises(zernio.ZernioError, match="2200"):
        zernio.post_payload("reel", "a", "u", "x" * 2201)


def test_without_a_key_nothing_is_called(monkeypatch):
    monkeypatch.delenv("ZERNIO_API_KEY")
    assert not zernio.configured()
    with pytest.raises(zernio.ZernioError, match="ZERNIO_API_KEY"):
        zernio.instagram_account()


def test_instagram_account_is_found_among_other_platforms(monkeypatch):
    accounts = {"accounts": [
        {"_id": "g1", "platform": "googlebusiness", "username": "I Monili Ravenna"},
        {"_id": "i1", "platform": "instagram", "username": "imoniliravenna", "isActive": True},
    ]}
    monkeypatch.setattr(zernio, "_call", lambda *a, **k: FakeResponse(200, accounts))
    assert zernio.instagram_account() == {"id": "i1", "username": "imoniliravenna"}
    monkeypatch.setattr(zernio, "_call", lambda *a, **k: FakeResponse(200, {"accounts": [accounts["accounts"][0]]}))
    assert zernio.instagram_account() is None


def test_publish_uploads_then_posts_with_an_idempotency_key(monkeypatch, tmp_path):
    video = tmp_path / "reel.mp4"
    video.write_bytes(b"0" * 2048)
    calls = []

    def fake_call(method, path, **kwargs):
        calls.append((method, path, kwargs))
        if path == "/accounts":
            return FakeResponse(200, {"accounts": [{"_id": "i1", "platform": "instagram", "username": "imoniliravenna"}]})
        if path == "/media/presign":
            return FakeResponse(200, {"uploadUrl": "https://up/put", "publicUrl": "https://media.zernio.com/temp/reel.mp4"})
        return FakeResponse(201, {"post": {"_id": "p1", "status": "publishing"}})

    puts = []
    monkeypatch.setattr(zernio, "_call", fake_call)
    monkeypatch.setattr(zernio.requests, "put", lambda url, **k: puts.append(url) or FakeResponse(200))
    sent = zernio.publish("reel", "reel123", video, "Caption", "Commento", False)
    assert sent["post_id"] == "p1" and puts == ["https://up/put"]
    post = [call for call in calls if call[1] == "/posts"][0]
    assert post[2]["json"]["mediaItems"][0]["url"] == "https://media.zernio.com/temp/reel.mp4"
    key_1 = post[2]["headers"]["Idempotency-Key"]
    assert key_1 == zernio.idempotency_key("reel123", "reel", video)


def test_publish_refuses_when_instagram_is_not_connected(monkeypatch, tmp_path):
    video = tmp_path / "reel.mp4"
    video.write_bytes(b"0")
    monkeypatch.setattr(zernio, "_call", lambda *a, **k: FakeResponse(200, {"accounts": []}))
    with pytest.raises(zernio.ZernioError, match="non è ancora collegato"):
        zernio.publish("reel", "r", video, "c", "", False)


def test_story_over_100_mb_is_refused_before_uploading(monkeypatch, tmp_path):
    video = tmp_path / "storia.mp4"
    video.write_bytes(b"0")
    monkeypatch.setattr(zernio, "STORY_MAX_BYTES", 0)
    monkeypatch.setattr(zernio, "instagram_account", lambda: {"id": "i1", "username": "x"})
    monkeypatch.setattr(zernio, "_call", lambda *a, **k: pytest.fail("non deve chiamare Zernio"))
    with pytest.raises(zernio.ZernioError, match="MB"):
        zernio.publish("story", "r", video, "", "", False)


def test_duplicate_content_is_reported_not_published_twice(monkeypatch, tmp_path):
    video = tmp_path / "reel.mp4"
    video.write_bytes(b"0")

    def fake_call(method, path, **kwargs):
        if path == "/accounts":
            return FakeResponse(200, {"accounts": [{"_id": "i1", "platform": "instagram"}]})
        if path == "/media/presign":
            return FakeResponse(200, {"uploadUrl": "https://up", "publicUrl": "https://m/x.mp4"})
        return FakeResponse(409, {"error": "duplicato", "details": {"existingPostId": "p9"}})

    monkeypatch.setattr(zernio, "_call", fake_call)
    monkeypatch.setattr(zernio.requests, "put", lambda *a, **k: FakeResponse(200))
    with pytest.raises(zernio.ZernioError, match="già pubblicato"):
        zernio.publish("reel", "r", video, "c", "", False)


def _reel_with_video(monkeypatch, tmp_path):
    monkeypatch.setattr(reel_studio, "OUTPUT_ROOT", tmp_path)
    monkeypatch.setattr(reel_studio, "REELS_ROOT", tmp_path / "reels")
    folder = reel_studio.reel_dir("abcd1234")
    folder.mkdir(parents=True)
    video = folder / "monili.mp4"
    video.write_bytes(b"0" * 100)
    reel_studio.save_state({"id": "abcd1234", "results": {"final_video": reel_studio.rel(video)}})
    return video


def test_endpoint_needs_confirmation_and_never_publishes_twice(monkeypatch, tmp_path):
    _reel_with_video(monkeypatch, tmp_path)
    client = TestClient(server.app)
    body = {"kind": "reel", "caption": "Ciao", "first_comment": "x"}
    assert client.post("/reel/abcd1234/instagram", json=body).status_code == 400  # niente conferma

    monkeypatch.setattr(zernio, "publish", lambda *a, **k: {"post_id": "p1", "status": "publishing", "account": "imoniliravenna"})
    first = client.post("/reel/abcd1234/instagram", json={**body, "confirm": True})
    assert first.status_code == 200 and first.json()["post_id"] == "p1"
    assert client.get("/reel/abcd1234/instagram").json()["reel"]["post_id"] == "p1"
    again = client.post("/reel/abcd1234/instagram", json={**body, "confirm": True})
    assert again.status_code == 409


def test_endpoint_without_a_story_video_and_unknown_reel(monkeypatch, tmp_path):
    _reel_with_video(monkeypatch, tmp_path)
    client = TestClient(server.app)
    assert client.post("/reel/abcd1234/instagram", json={"kind": "story", "confirm": True}).status_code == 409
    assert client.post("/reel/nonesiste/instagram", json={"kind": "reel", "confirm": True}).status_code == 404


def test_status_endpoint_reports_not_configured_without_a_key(monkeypatch):
    monkeypatch.delenv("ZERNIO_API_KEY")
    assert TestClient(server.app).get("/instagram/status").json() == {"configured": False, "connected": False}
