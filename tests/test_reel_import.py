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


# ── Grafica Remotion: pre-passaggio, opzioni e versione Storia ───────────────

def _with_audio(video, tmp_path, source: str):
    """Aggiunge una traccia audio (sine = si sente, anullsrc = muto) al video di prova."""
    out = tmp_path / "con_audio.mp4"
    rs._run_ffmpeg(["-i", str(video), "-f", "lavfi", "-i", source, "-shortest", "-c:v", "copy", "-c:a", "aac", str(out)])
    return out


def test_enhance_clip_is_vertical_hd_and_keeps_length(vertical_video, tmp_path):
    out = rs.enhance_clip(vertical_video, tmp_path / "hd.mp4", 3)
    assert rs.probe_size(out) == rs.FRAME_SIZE
    assert abs(rs.probe_duration(out) - 3) < 0.15
    assert rs.audio_mean_db(out) is None  # di default niente audio


def test_enhance_clip_keeps_audio_only_when_asked(vertical_video, tmp_path):
    loud = _with_audio(vertical_video, tmp_path, "sine=frequency=440:duration=3")
    assert rs.audio_mean_db(rs.enhance_clip(loud, tmp_path / "a.mp4", 3, keep_audio=True)) is not None
    assert rs.audio_mean_db(rs.enhance_clip(loud, tmp_path / "b.mp4", 3, keep_audio=False)) is None


def test_graphics_options_keep_the_plate_inside_the_video():
    short = rs._graphics_options(3, "reel")
    assert short["titleFrom"] <= 1.0 and short["plateUntil"] > short["titleFrom"]
    long = rs._graphics_options(10, "story")
    assert long["titleFrom"] == 2.5 and long["plateUntil"] == 9.2
    assert long["layout"] == "story" and long["closingSeconds"] == rs.REMOTION_CLOSING_SECONDS


def test_import_with_graphics_renders_reel_and_story(vertical_video, monkeypatch):
    calls = []

    def fake_render(source, output, seconds, **kwargs):
        calls.append(kwargs)
        import shutil
        shutil.copyfile(source, output)
        return output

    monkeypatch.setattr(rs.remotion_graphics, "render_graphics", fake_render)
    state = rs.import_external_video(
        rs.new_reel_id(), vertical_video, "Anello argento 925", "anello con zaffiro",
        graphics=True, detail="Zaffiro cabochon · Misura 17,5", hook="Un blu che non passa inosservato.",
        location="via-cavour-17", story=True,
    )
    results = state["results"]
    assert results["graphics_applied"] is True and results["story_video"]
    assert rs._abs(results["story_video"]).exists()
    reel_call, story_call = calls
    assert reel_call["extra"]["layout"] == "reel" and story_call["extra"]["layout"] == "story"
    assert reel_call["detail"] == "Zaffiro cabochon · Misura 17,5"
    assert reel_call["hook"] == "Un blu che non passa inosservato."
    assert reel_call["place"] == "Via Cavour 17, Ravenna"


def test_story_failure_keeps_the_reel(vertical_video, monkeypatch):
    def flaky(source, output, seconds, **kwargs):
        if kwargs["extra"]["layout"] == "story":
            raise RuntimeError("boom")
        import shutil
        shutil.copyfile(source, output)

    monkeypatch.setattr(rs.remotion_graphics, "render_graphics", flaky)
    state = rs.import_external_video(rs.new_reel_id(), vertical_video, "x", graphics=True, story=True)
    assert state["status"] == "done" and state["results"]["graphics_applied"] is True
    assert "story_video" not in state["results"]


def test_failed_graphics_falls_back_to_simple_assembly(vertical_video, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("Remotion non parte")

    monkeypatch.setattr(rs.remotion_graphics, "render_graphics", broken)
    state = rs.import_external_video(rs.new_reel_id(), vertical_video, "x", graphics=True, story=True)
    assert state["status"] == "done" and state["results"]["graphics_applied"] is False
    assert "story_video" not in state["results"]


def test_ready_video_is_kept_as_is_and_the_ai_only_writes_the_texts(vertical_video, monkeypatch):
    import fucina_codex

    seen = {}

    def fake_codex(prompt, images, model=""):
        seen["images"] = [path.name for path in images]
        seen["prompt"] = prompt
        import json

        return json.dumps({
            "title": "Orecchini rubino",
            "caption": "Rubino al viso. Scrivici, ti diciamo se è disponibile",
            "hashtags": ["#rubino"],
            "first_comment": "Ti piacciono?",
        })

    monkeypatch.setattr(fucina_codex, "executable", lambda: "codex")
    monkeypatch.setattr(fucina_codex, "run", fake_codex)
    reel_id = rs.new_reel_id()
    state = rs.import_external_video(reel_id, vertical_video, "", "orecchini argento 925", True, as_is=True)
    results = state["results"]
    final = rs._abs(results["final_video"])
    assert state["status"] == "done" and results["ready_as_is"] is True and results["graphics_applied"] is False
    assert final.read_bytes() == vertical_video.read_bytes()  # il video non è stato toccato: niente chiusura, niente ricodifica
    assert abs(rs.probe_duration(final) - 3) < 0.15
    assert len(seen["images"]) == rs.READY_FRAMES and "orecchini argento 925" in seen["prompt"]
    assert results["copy"]["caption"].startswith("Rubino al viso")
    assert results["copy"]["hashtags"][: len(rs.FIXED_HASHTAGS)] == rs.FIXED_HASHTAGS and "#rubino" in results["copy"]["hashtags"]
    assert results["copy"]["first_comment"] == "Ti piacciono?"
    assert state["storyboard"]["title"] == "Orecchini rubino"  # titolo vuoto: lo sceglie l'AI


def test_ready_video_keeps_the_title_typed_by_the_owner(vertical_video, monkeypatch):
    import fucina_codex

    monkeypatch.setattr(fucina_codex, "executable", lambda: "codex")
    monkeypatch.setattr(fucina_codex, "run", lambda prompt, images, model="": '{"title": "Altro", "caption": "Testo"}')
    state = rs.import_external_video(rs.new_reel_id(), vertical_video, "Anello zaffiro", "", True, as_is=True)
    assert state["storyboard"]["title"] == "Anello zaffiro"


def test_ready_video_without_codex_fails_clearly_and_via_the_api(vertical_video, monkeypatch):
    import fucina_codex

    monkeypatch.setattr(fucina_codex, "executable", lambda: None)
    with pytest.raises(RuntimeError, match="Codex"):
        rs.import_external_video(rs.new_reel_id(), vertical_video, "", "", True, as_is=True)
    response = client.post(
        "/reel/import",
        files={"video": ("v.mp4", vertical_video.read_bytes(), "video/mp4")},
        data={"as_is": "true"},
    )
    assert response.status_code == 400 and "Codex" in response.json()["error"]
