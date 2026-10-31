"""Video esterno (Gemini/Veo, telefono) importato come Reel finito: chiusura, copertina, testi."""
import pytest
from fastapi.testclient import TestClient
from PIL import Image

import api.server as server
import reel_studio as rs

client = TestClient(server.app)


@pytest.fixture()
def vertical_video(tmp_path, product_photo):
    return rs.ken_burns_clip(product_photo, tmp_path / "verticale.mp4", 3)


@pytest.fixture()
def horizontal_video(tmp_path, product_photo):
    path = tmp_path / "orizzontale.mp4"
    rs._run_ffmpeg(["-loop", "1", "-i", str(product_photo), "-t", "2", "-vf", "scale=1280:720,format=yuv420p", "-an", str(path)])
    return path


def test_closing_card_is_cream_and_vertical(tmp_path):
    card = rs.make_closing_card(tmp_path / "chiusura.png")
    with Image.open(card) as img:
        assert img.size == rs.FRAME_SIZE
        assert img.getpixel((20, 20)) == (246, 241, 230)
        assert img.getpixel((20, 1880)) == (246, 241, 230)  # la fascia della caption Instagram resta vuota


def test_import_adds_closing_cover_and_texts(vertical_video):
    reel_id = rs.new_reel_id()
    state = rs.import_external_video(reel_id, vertical_video, "Bomber ricamato", "bomber tortora con ricami")
    results = state["results"]
    assert state["status"] == "done" and state["source"] == "esterno" and results["external"] is True
    final = rs._abs(results["final_video"])
    expected = 3 + rs.CLOSING_SECONDS - rs.TRANSITIONS[rs.CLOSING_FADE][1]
    assert abs(rs.probe_duration(final) - expected) < 0.15
    assert rs.probe_size(final) == rs.FRAME_SIZE
    assert rs._abs(results["cover"]).exists() and not results["preview_only"]
    # senza chiave OpenRouter i testi sono la descrizione, con gli hashtag fissi
    assert results["copy"]["caption"] == "bomber tortora con ricami"
    assert results["copy"]["hashtags"] == rs.FIXED_HASHTAGS
    assert state["storyboard"]["title"] == "Bomber ricamato" and state["storyboard"]["shots"] == []


def test_import_without_closing_keeps_the_length(vertical_video):
    state = rs.import_external_video(rs.new_reel_id(), vertical_video, "", add_closing=False)
    assert abs(rs.probe_duration(rs._abs(state["results"]["final_video"])) - 3) < 0.15
    assert state["storyboard"]["title"] == "Reel I Monili"


def test_horizontal_video_is_refused(horizontal_video):
    with pytest.raises(ValueError, match="verticale"):
        rs.import_external_video(rs.new_reel_id(), horizontal_video, "x")


def test_import_endpoint(vertical_video, horizontal_video, monkeypatch):
    monkeypatch.setattr(rs, "agent_copy", lambda state, api_key: {"caption": "Testo AI", "hashtags": rs.FIXED_HASHTAGS})
    with vertical_video.open("rb") as video:
        res = client.post(
            "/reel/import",
            files={"video": ("veo.mp4", video, "video/mp4")},
            data={"title": "Bomber", "note": "bomber", "add_closing": "true"},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "done" and body["results"]["copy"]["caption"] == "Testo AI"
    assert rs.load_state(body["id"])["source"] == "esterno"

    before = set(rs.REELS_ROOT.iterdir())
    with horizontal_video.open("rb") as video:
        res = client.post("/reel/import", files={"video": ("veo.mp4", video, "video/mp4")}, data={"title": "x"})
    assert res.status_code == 400 and "verticale" in res.json()["error"]
    assert set(rs.REELS_ROOT.iterdir()) == before  # nessuna cartella lasciata a metà

    res = client.post("/reel/import", files={"video": ("foto.jpg", b"jpeg", "image/jpeg")}, data={})
    assert res.status_code == 400
