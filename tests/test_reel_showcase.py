"""Reel Studio → sito vetrina: versione leggera, invio multipart, collegamento al pezzo."""
import json

import pytest
from fastapi.testclient import TestClient

import api.server as server
import reel_studio as rs

client = TestClient(server.app)


@pytest.fixture()
def full_hd_video(tmp_path, product_photo):
    """Video 1080x1920 come quello del Reel Studio (anteprima Ken Burns, 4 secondi)."""
    return rs.ken_burns_clip(product_photo, tmp_path / "full.mp4", 4)


def test_web_video_fits_the_site_limit(full_hd_video, tmp_path):
    out = rs.make_web_video(full_hd_video, tmp_path / "web.mp4")
    assert out.stat().st_size <= rs.WEB_REEL_MAX_VIDEO_BYTES
    assert out.stat().st_size < full_hd_video.stat().st_size
    assert out.read_bytes()[4:8] == b"ftyp"  # il sito controlla i byte reali


def test_web_video_refuses_what_cannot_fit(full_hd_video, tmp_path):
    with pytest.raises(RuntimeError, match="accorcialo"):
        rs.make_web_video(full_hd_video, tmp_path / "web.mp4", max_bytes=1_000)


def test_web_poster_is_light(product_photo, tmp_path):
    out = rs.make_web_poster(product_photo, tmp_path / "poster.jpg")
    assert out.stat().st_size <= rs.WEB_REEL_MAX_POSTER_BYTES
    assert out.read_bytes()[:3] == b"\xff\xd8\xff"


def test_reel_ingest_url_follows_the_fiche_url(monkeypatch):
    monkeypatch.delenv("SHOWCASE_REEL_INGEST_URL", raising=False)
    monkeypatch.setenv("SHOWCASE_INGEST_URL", "https://sito.example/api/ingest/internal-webapp")
    assert server._reel_ingest_url() == "https://sito.example/api/ingest/reel"
    monkeypatch.setenv("SHOWCASE_REEL_INGEST_URL", "https://altro.example/x")
    assert server._reel_ingest_url() == "https://altro.example/x"
    monkeypatch.delenv("SHOWCASE_REEL_INGEST_URL")
    monkeypatch.delenv("SHOWCASE_INGEST_URL")
    assert server._reel_ingest_url() == ""


def _done_reel(full_hd_video, product_photo, preview_only=False):
    reel_id = rs.new_reel_id()
    folder = rs.reel_dir(reel_id)
    folder.mkdir(parents=True)
    final = folder / "final.mp4"
    final.write_bytes(full_hd_video.read_bytes())
    cover = folder / "cover.jpg"
    cover.write_bytes(product_photo.read_bytes())
    rs.save_state(
        {
            "id": reel_id,
            "status": "done",
            "photos": [rs.rel(cover)],
            "storyboard": {"title": "Anello Cavour in tre look"},
            "results": {
                "final_video": rs.rel(final),
                "cover": rs.rel(cover),
                "copy": {"caption_short": "Un anello che parla da solo."},
                "preview_only": preview_only,
            },
        }
    )
    return reel_id


def test_publish_sends_light_files_and_links_the_piece(full_hd_video, product_photo, monkeypatch):
    reel_id = _done_reel(full_hd_video, product_photo)
    monkeypatch.setenv("SHOWCASE_INGEST_URL", "https://sito.example/api/ingest/internal-webapp")
    sent = {}

    def fake_send(meta, video, poster):
        sent.update(meta=meta, video_size=video.stat().st_size, poster_size=poster.stat().st_size)
        return {"ok": True, "status_code": 201}

    monkeypatch.setattr(server, "_send_reel_to_showcase", fake_send)
    res = client.post(f"/reel/{reel_id}/showcase/publish", json={"product_id": "anello-cavour-123"})
    assert res.status_code == 200, res.text
    assert sent["meta"]["product_id"] == "anello-cavour-123"
    assert sent["meta"]["title"] == "Anello Cavour in tre look"
    assert sent["meta"]["caption"] == "Un anello che parla da solo."
    assert sent["video_size"] <= rs.WEB_REEL_MAX_VIDEO_BYTES
    assert rs.load_state(reel_id)["showcase"]["product_id"] == "anello-cavour-123"


def test_publish_refuses_preview_and_surfaces_site_errors(full_hd_video, product_photo, monkeypatch):
    monkeypatch.setenv("SHOWCASE_INGEST_URL", "https://sito.example/api/ingest/internal-webapp")
    preview = _done_reel(full_hd_video, product_photo, preview_only=True)
    assert client.post(f"/reel/{preview}/showcase/publish", json={}).status_code == 400

    real = _done_reel(full_hd_video, product_photo)
    monkeypatch.setattr(
        server, "_send_reel_to_showcase", lambda *a: {"ok": False, "status_code": 409, "error": "Esiste gia un Reel con questo id."}
    )
    res = client.post(f"/reel/{real}/showcase/publish", json={})
    assert res.status_code == 409 and "Esiste gia" in res.json()["error"]
    assert "showcase" not in rs.load_state(real)


def test_publish_is_off_without_site_url(monkeypatch):
    monkeypatch.delenv("SHOWCASE_INGEST_URL", raising=False)
    monkeypatch.delenv("SHOWCASE_REEL_INGEST_URL", raising=False)
    assert client.post("/reel/qualsiasi/showcase/publish", json={}).status_code == 503


def test_showcase_products_lists_pieces_sent_from_the_studio(storage_root):
    audit = server.SHOWCASE_DRAFTS_DIR / "showcase-run-test-reel.json"
    audit.write_text(
        json.dumps({"run_id": "run1", "product_id": "anello-x-run1", "product_title": "Anello X", "created_at": "2026-10-28T10:00:00"}),
        encoding="utf-8",
    )
    (server.SHOWCASE_DRAFTS_DIR / "showcase-vecchio.json").write_text(json.dumps({"run_id": "v"}), encoding="utf-8")
    items = client.get("/showcase/products").json()["items"]
    assert {"product_id": "anello-x-run1", "title": "Anello X", "created_at": "2026-10-28T10:00:00", "run_id": "run1"} in items
    assert all(item["product_id"] for item in items)
