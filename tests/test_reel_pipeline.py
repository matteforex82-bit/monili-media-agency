import json

import pytest

import reel_kit as kit
import reel_studio as rs


@pytest.fixture()
def reel(product_photo):
    reel_id = rs.new_reel_id()
    input_dir = rs.reel_dir(reel_id) / "input"
    input_dir.mkdir(parents=True)
    photo = input_dir / "photo_1.jpg"
    photo.write_bytes(product_photo.read_bytes())
    # vecchio nome della skill "indossato": i Reel creati prima continuano a funzionare
    state = rs.create_reel(reel_id, [photo], [], "brief", "reel", 12, "kling-3-std", "", "gpt", recipe="modella_monili")
    return state


def test_normalize_storyboard_clamps_and_repairs(reel):
    raw = {
        "scene_bible": "cream boutique",
        "shots": [
            {"source": "clip", "clip_index": 3, "duration": 4},  # clip inesistente -> scena AI
            {"source": "ai", "duration": 40, "transition_out": "boh", "use_model": "true", "end_on_product": True},
        ],
    }
    sb = rs.normalize_storyboard(reel, raw)
    assert [s["source"] for s in sb["shots"]] == ["ai", "ai"]
    assert sb["shots"][1]["duration"] == 15 and sb["shots"][1]["transition_out"] == "dissolve"
    assert sb["shots"][1]["use_model"] is True and sb["shots"][1]["end_on_product"] is True
    assert sb["scene_bible"] == "cream boutique"
    with pytest.raises(RuntimeError):
        rs.normalize_storyboard(reel, {"shots": []})


def test_montage_durations(tmp_path, product_photo):
    a = rs.ken_burns_clip(product_photo, tmp_path / "a.mp4", 2)
    b = rs.ken_burns_clip(product_photo, tmp_path / "b.mp4", 2, zoom_in=False)
    final = rs.assemble([(a, 2), (b, 2)], ["dissolve"], tmp_path / "final.mp4")
    assert abs(rs.probe_duration(final) - (4 - rs.TRANSITION_SECONDS)) < 0.1


def test_coherent_keyframes_and_product_protection(reel, monkeypatch):
    rs.save_state({**rs.load_state(reel["id"]), "woman": "Donna di prova", "storyboard": rs.normalize_storyboard(reel, {
        "scene_bible": "warm cream counter, window light",
        "shots": [
            {"purpose": "hook", "keyframe_mode": "ai", "duration": 3},
            {"purpose": "indossato", "keyframe_mode": "ai", "use_model": True, "duration": 3},
            {"purpose": "cta", "keyframe_mode": "ai", "duration": 3},
        ],
    })})
    state = rs.load_state(reel["id"])
    calls, qa_calls = [], []

    def fake_img(api_key, model, prompt, images, destination, aspect_ratio="9:16"):
        calls.append((destination.name, [p.name for p in images], prompt))
        destination.write_bytes(_abs_photo(state).read_bytes())
        return destination

    def fake_qa(api_key, text_model, photo, keyframe, expected_text="", scene_anchor=None, scene_bible=""):
        qa_calls.append((keyframe.name, scene_anchor.name if scene_anchor else None))
        if keyframe.name.startswith("shot_3"):
            return {"ok": False, "score": 4, "issues": "pietra diversa", "checked": True}
        return {"ok": True, "score": 9, "issues": "", "checked": True}

    monkeypatch.setattr(kit, "generate_image_multi", fake_img)
    monkeypatch.setattr(kit, "check_keyframe", fake_qa)
    out = rs.reel_dir(reel["id"]) / "shots"
    out.mkdir(parents=True, exist_ok=True)
    frames = rs._make_keyframes(state, "k", out)

    # la scena con la donna fa da guida e viene generata per prima, ed è l'unica che la descrive
    assert calls[0][0].startswith("shot_2")
    assert state["woman"] in calls[0][2]
    assert all(state["woman"] not in prompt for name, _, prompt in calls[1:])
    assert all("shot_2_keyframe.jpg" in images for name, images, _ in calls[1:])
    assert all(anchor == "shot_2_keyframe.jpg" for name, anchor in qa_calls[1:])
    # la scena mai fedele viene ritentata e poi sostituita con la foto reale
    shot3 = [c for c in calls if c[0].startswith("shot_3")]
    assert len(shot3) == rs.KEYFRAME_ATTEMPTS
    assert "PREVIOUS ATTEMPT WAS REJECTED" in shot3[-1][2]
    assert frames["shot_3"][1]["replaced"] is True and frames["shot_3"][1]["source"] == "foto reale"
    assert "SAME SCENE FOR THE WHOLE REEL" in calls[0][2]


def test_estimate_has_poster_and_budget(reel):
    state = rs.load_state(reel["id"])
    state["storyboard"] = rs.normalize_storyboard(state, {"shots": [{"keyframe_mode": "ai", "duration": 5}] * 3})
    est = rs.estimate_reel(state)
    labels = [line["label"] for line in est["lines"]]
    assert "Copertina poster" in labels and est["preview_mode"] is True
    assert est["total_eur"] == round(est["total_usd"] * rs.EUR_PER_USD, 2)


def _abs_photo(state):
    return rs.OUTPUT_ROOT / state["photos"][0]


def test_state_file_is_valid_json(reel):
    data = json.loads((rs.reel_dir(reel["id"]) / "reel.json").read_text(encoding="utf-8"))
    assert data["recipe"] == "indossato" and data["status"] == "planning"
    assert data["woman"] is None  # senza Scheda pezzo la inventa il regista nello storyboard


def test_director_invents_the_woman_once(reel, monkeypatch):
    prompts = []

    def fake_storyboard(state, photo):
        prompts.append(rs._woman_block(state))
        return {"woman": "Donna inventata dal regista", "shots": [{"keyframe_mode": "ai", "use_model": True, "duration": 3}]}

    monkeypatch.setattr(rs, "agent_analisi", lambda *a, **k: "analisi")
    monkeypatch.setattr(rs, "agent_storyboard", fake_storyboard)
    rs.plan_reel(reel["id"], "k")
    assert "la inventi tu" in prompts[0]
    assert rs.load_state(reel["id"])["woman"] == "Donna inventata dal regista"
    # Ripianificando, la donna resta quella: il regista la riceve già scelta.
    rs.plan_reel(reel["id"], "k")
    assert "gia scelta" in prompts[1]
    assert rs.load_state(reel["id"])["woman"] == "Donna inventata dal regista"
