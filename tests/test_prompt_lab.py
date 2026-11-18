"""Laboratorio dei prompt: analisi con prompt visibili, prove fatte a mano, voti, libreria. Senza rete e senza AI."""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import api.server as server
import main as studio_main
import prompt_lab

client = TestClient(server.app)


def _jpeg(color=(200, 120, 60), size=(600, 800)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "JPEG")
    return buffer.getvalue()


@pytest.fixture(autouse=True)
def isolated_library(tmp_path, monkeypatch):
    monkeypatch.setattr(prompt_lab, "LIBRARY_FILE", tmp_path / "prompt_lab.json")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")


def _draft() -> dict:
    return client.post(
        "/bozze", files=[("foto", ("a.jpg", _jpeg(), "image/jpeg"))], data={"nota": "anello argento ametista 159 euro"}
    ).json()


def _fake_agents(monkeypatch):
    monkeypatch.setattr(studio_main, "agent_analisi", lambda *a, **k: "## IDENTIFICAZIONE\n- Categoria: anello")
    monkeypatch.setattr(
        studio_main,
        "agent_scheda_plan",
        lambda *a, **k: {
            "styling": "con un abito semplice",
            "woman": "a woman in her forties, short dark hair",
            "site_prompts": {"clean": "clean ivory catalog photo", "worn": "ring worn on a hand, blurred wall"},
        },
    )


def test_controlled_prompt_adds_woman_and_fidelity_rules():
    worn = studio_main.controlled_site_prompt("ring worn", "worn", "a woman in her forties", "NEVER: logos")
    assert "ring worn" in worn and "a woman in her forties" in worn and "source-of-truth" in worn and "NEVER: logos" in worn
    clean = studio_main.controlled_site_prompt("clean photo", "clean", "a woman in her forties", "")
    assert "woman" not in clean.lower().split("use the uploaded")[0]


def test_analysis_shows_the_final_prompts_and_makes_no_image(monkeypatch):
    _fake_agents(monkeypatch)
    draft = _draft()
    result = client.post(f"/bozze/{draft['id']}/prompt", json={"category": "bijoux", "model": "Seedream"})
    assert result.status_code == 200
    lab = result.json()["lab"]
    assert lab["category"] == "bijoux" and set(lab["prompts"]) == {"clean", "worn"}
    assert "ring worn on a hand" in lab["prompts"]["worn"]["text"] and "source-of-truth" in lab["prompts"]["worn"]["text"]
    assert "short dark hair" in lab["prompts"]["worn"]["text"]
    assert client.get(f"/bozze/{draft['id']}/prompt").json()["lab"]["analisi"].startswith("## IDENTIFICAZIONE")
    client.delete(f"/bozze/{draft['id']}")


def test_attempt_result_rating_and_library(monkeypatch):
    _fake_agents(monkeypatch)
    draft = _draft()
    did = draft["id"]
    client.post(f"/bozze/{did}/prompt", json={"category": "bijoux", "model": "Seedream"})

    edited = client.put(f"/bozze/{did}/prompt/worn", json={"text": "ring worn, tighter framing"}).json()["lab"]
    assert edited["prompts"]["worn"]["edited"] is True

    lab = client.post(f"/bozze/{did}/prove", json={"shot": "worn", "model": "Seedream"}).json()["lab"]
    attempt = lab["attempts"][0]
    assert attempt["prompt"] == "ring worn, tighter framing" and attempt["model"] == "Seedream"

    # the prompt can change afterwards: the attempt keeps what was really used
    client.put(f"/bozze/{did}/prompt/worn", json={"text": "something else"})
    assert client.get(f"/bozze/{did}/prompt").json()["lab"]["attempts"][0]["prompt"] == "ring worn, tighter framing"

    up = client.post(f"/bozze/{did}/prove/{attempt['id']}/risultato", files={"foto": ("r.jpg", _jpeg(), "image/jpeg")})
    assert up.status_code == 200 and up.json()["lab"]["attempts"][0]["result"]
    thumb = client.get(f"/bozze/{did}/prove/{attempt['id']}/risultato?w=200")
    assert thumb.status_code == 200 and Image.open(io.BytesIO(thumb.content)).width <= 200

    assert prompt_lab.hints("bijoux", "Seedream") == ""  # nothing rated yet
    client.put(f"/bozze/{did}/prove/{attempt['id']}", json={"rating": 5, "note": "perfetta"})
    assert prompt_lab.library_summary() == {"total": 1, "good": 1, "bad": 0}
    assert "ring worn, tighter framing" in prompt_lab.hints("bijoux", "Seedream")

    # a bad rating replaces the good one and becomes a thing to avoid
    client.put(f"/bozze/{did}/prove/{attempt['id']}", json={"rating": 1, "note": "la pietra è diventata verde"})
    assert prompt_lab.library_summary() == {"total": 1, "good": 0, "bad": 1}
    hints = prompt_lab.hints("bijoux", "Seedream")
    assert "pietra è diventata verde" in hints and "ring worn, tighter framing" not in hints

    client.delete(f"/bozze/{did}/prove/{attempt['id']}")
    assert prompt_lab.library_summary()["total"] == 0
    client.delete(f"/bozze/{did}")


def test_unknown_things_give_404():
    assert client.get("/bozze/nope/prompt").status_code == 404
    draft = _draft()
    assert client.post(f"/bozze/{draft['id']}/prove", json={"shot": "worn"}).status_code == 404  # no analysis yet
    client.delete(f"/bozze/{draft['id']}")


def test_hints_are_kept_apart_by_model():
    prompt_lab.record({"id": "a", "shot": "worn", "model": "Seedream", "prompt": "SEEDREAM PROMPT", "rating": 5, "note": ""}, "bijoux", "d")
    prompt_lab.record({"id": "b", "shot": "worn", "model": "Nano Banana", "prompt": "BANANA PROMPT", "rating": 5, "note": ""}, "bijoux", "d")
    assert "SEEDREAM PROMPT" in prompt_lab.hints("bijoux", "Seedream") and "BANANA" not in prompt_lab.hints("bijoux", "Seedream")
    # the automatic flow only sees the models it really uses
    assert "BANANA PROMPT" in prompt_lab.hints("bijoux") and "SEEDREAM" not in prompt_lab.hints("bijoux")


def test_model_knowledge_loads_the_model_and_the_recipe():
    text = prompt_lab.model_knowledge("Seedream", "bijoux")
    assert "Seedream" in text and "Ricetta: bijoux" in text
    assert "Seedance 2.5" in prompt_lab.model_knowledge("Seedance 2.5", "abbigliamento")
    assert prompt_lab.model_knowledge("", "") == ""


def test_clothing_two_steps_photo_then_seedance_scenes_and_codex_critique(monkeypatch):
    _fake_agents(monkeypatch)
    monkeypatch.setattr(
        studio_main,
        "generate_text_with_openrouter",
        lambda *a, **k: '{"idea": "una passeggiata", "scene": {"scena_1": "full body", "scena_2": "fabric detail", "scena_3": "she turns"}}',
    )
    seen = {}

    def fake_codex(prompt, images, model=""):
        seen.update(prompt=prompt, images=images)
        return (
            '{"checklist": {"pietre_numero": {"esito": "ok", "nota": "3"}}, "giudizio": "bene", "voto_proposto": 4, '
            '"correzione": "niente", "prompt_corretto": "better prompt"}'
        )

    monkeypatch.setattr(server.fucina_codex, "run", fake_codex)
    monkeypatch.setattr(server, "_video_frames", lambda video, out, count=3: [video, video, video])

    draft = _draft()
    did = draft["id"]
    client.post(f"/bozze/{did}/prompt", json={"category": "abbigliamento", "model": "Seedream"})
    lab = client.post(f"/bozze/{did}/prove", json={"shot": "worn"}).json()["lab"]
    photo_attempt = lab["attempts"][0]["id"]

    # the scenes need a worn photo first
    assert client.post(f"/bozze/{did}/scene", json={"attempt_id": photo_attempt}).status_code == 400
    client.post(f"/bozze/{did}/prove/{photo_attempt}/risultato", files={"foto": ("w.jpg", _jpeg(), "image/jpeg")})
    scenes = client.post(f"/bozze/{did}/scene", json={"attempt_id": photo_attempt})
    assert scenes.status_code == 200
    lab = scenes.json()["lab"]
    assert set(lab["scenes"]) == {"scena_1", "scena_2", "scena_3"} and "PRESERVE" in lab["scenes"]["scena_3"]["text"]
    assert lab["scenes_source"] == photo_attempt

    # a scene is an attempt with Seedance 2.5, its result is a video
    lab = client.post(f"/bozze/{did}/prove", json={"shot": "scena_1"}).json()["lab"]
    scene_attempt = lab["attempts"][-1]
    assert scene_attempt["model"] == "Seedance 2.5"
    clip = b"\x00\x00\x00\x18ftypmp42" + b"0" * 100
    up = client.post(f"/bozze/{did}/prove/{scene_attempt['id']}/risultato", files={"foto": ("c.mp4", clip, "video/mp4")})
    assert up.status_code == 200 and up.json()["lab"]["attempts"][-1]["result"].endswith(".mp4")
    assert client.get(f"/bozze/{did}/prove/{scene_attempt['id']}/risultato").content == clip

    # Codex judges a photo with two images and a video with the real photo plus frames
    judged = client.post(f"/bozze/{did}/prove/{photo_attempt}/valuta", json={})
    assert judged.status_code == 200 and len(seen["images"]) == 2
    critique = judged.json()["lab"]["attempts"][0]["critique"]
    assert critique["voto_proposto"] == 4 and critique["checklist"]["pietre_numero"]["esito"] == "ok" and "metallo" in critique["checklist"]
    client.post(f"/bozze/{did}/prove/{scene_attempt['id']}/valuta", json={})
    assert len(seen["images"]) == 4 and "fotogrammi" in seen["prompt"]

    # edits reach the scenes too
    edited = client.put(f"/bozze/{did}/prompt/scena_2", json={"text": "closer on the embroidery"}).json()["lab"]
    assert edited["scenes"]["scena_2"]["edited"] is True
    client.delete(f"/bozze/{did}")
