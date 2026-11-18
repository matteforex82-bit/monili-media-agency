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


def test_woman_is_a_slot_the_owner_fills_by_hand(monkeypatch):
    _fake_agents(monkeypatch)
    draft = _draft()
    lab = client.post(f"/bozze/{draft['id']}/prompt", json={"category": "bijoux", "model": "Seedream"}).json()["lab"]
    worn = lab["prompts"]["worn"]["text"]
    assert lab["woman_token"] == "@MODELLA" and "The woman is @MODELLA" in worn and "short dark hair" not in worn
    assert "@MODELLA" not in lab["prompts"]["clean"]["text"]
    invented = client.post(f"/bozze/{draft['id']}/prompt", json={"category": "bijoux", "model": "Seedream", "woman": "invented"}).json()["lab"]
    assert invented["woman_token"] == "" and "short dark hair" in invented["prompts"]["worn"]["text"]
    assert "@MODELLA" in prompt_lab.scenes_prompt(lab, "", "") and "short dark hair" in prompt_lab.scenes_prompt(invented, "", "")
    client.delete(f"/bozze/{draft['id']}")


def test_analysis_shows_the_final_prompts_and_makes_no_image(monkeypatch):
    _fake_agents(monkeypatch)
    draft = _draft()
    result = client.post(f"/bozze/{draft['id']}/prompt", json={"category": "bijoux", "model": "Seedream"})
    assert result.status_code == 200
    lab = result.json()["lab"]
    assert lab["category"] == "bijoux" and set(lab["prompts"]) == {"clean", "worn"}
    assert "ring worn on a hand" in lab["prompts"]["worn"]["text"] and "source-of-truth" in lab["prompts"]["worn"]["text"]
    assert "@MODELLA" in lab["prompts"]["worn"]["text"]
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
    assert "GPT Image" in prompt_lab.model_knowledge("GPT Image", "")
    assert prompt_lab.model_knowledge("", "") == ""
    # every knowledge file the code points to exists and stays short (it goes whole into the prompt)
    for name in set(prompt_lab.MODEL_FILES.values()):
        text = (prompt_lab.KNOWLEDGE_DIR / name).read_text(encoding="utf-8")
        assert 80 < len(text.split()) < 1100, name


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
            '{"checklist": {"motivo_colori": {"esito": "ok", "nota": "3"}}, "giudizio": "bene", "voto_proposto": 4, '
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
    assert critique["voto_proposto"] == 4 and "motivo_colori" in critique["checklist"] and "pietre_numero" not in critique["checklist"] and "dettagli" in critique["checklist"]
    client.post(f"/bozze/{did}/prove/{scene_attempt['id']}/valuta", json={})
    assert len(seen["images"]) == 4 and "fotogrammi" in seen["prompt"]

    # edits reach the scenes too
    edited = client.put(f"/bozze/{did}/prompt/scena_2", json={"text": "closer on the embroidery"}).json()["lab"]
    assert edited["scenes"]["scena_2"]["edited"] is True
    client.delete(f"/bozze/{did}")


def test_progress_says_what_to_do_next(monkeypatch):
    assert prompt_lab.progress(None)["stage"] == "prompt"
    lab = {"prompts": {"worn": {"text": "x"}}, "attempts": []}
    assert prompt_lab.progress(lab)["stage"] == "crea" and prompt_lab.progress(lab)["done"]["prompt"] is True
    lab["attempts"].append({"id": "a", "result": "", "rating": 0})
    assert prompt_lab.progress(lab)["stage"] == "carica"
    lab["attempts"][0]["result"] = "r.jpg"
    assert prompt_lab.progress(lab)["stage"] == "valuta" and prompt_lab.progress(lab)["done"]["generare"] is True
    lab["attempts"][0]["rating"] = 4
    done = prompt_lab.progress(lab)
    assert done["stage"] == "fatto" and done["done"]["valutare"] is True and done["label"] == "Valutata"

    # the list of drafts and the lab payload carry it
    _fake_agents(monkeypatch)
    draft = _draft()
    listed = {i["id"]: i for i in client.get("/bozze").json()["items"]}[draft["id"]]
    assert listed["progress"]["stage"] == "prompt"
    client.post(f"/bozze/{draft['id']}/prompt", json={"category": "bijoux", "model": "Seedream"})
    payload = client.post(f"/bozze/{draft['id']}/prove", json={"shot": "worn"}).json()
    assert payload["progress"]["stage"] == "carica"
    listed = {i["id"]: i for i in client.get("/bozze").json()["items"]}[draft["id"]]
    assert listed["progress"]["stage"] == "carica"
    client.delete(f"/bozze/{draft['id']}")


def test_all_photos_of_the_piece_reach_the_analysis(monkeypatch):
    seen = {}

    def fake_analisi(model, key, look, brief):
        seen["look"] = look
        seen["brief"] = brief
        return "## IDENTIFICAZIONE"

    monkeypatch.setattr(studio_main, "agent_analisi", fake_analisi)
    monkeypatch.setattr(
        studio_main,
        "agent_scheda_plan",
        lambda model, key, look, analisi, brief, category, target="": {
            "styling": "", "woman": "w", "site_prompts": {"clean": "c", "worn": "w"}
        },
    )
    files = [("foto", (f"{n}.jpg", _jpeg((n * 40, 90, 160)), "image/jpeg")) for n in range(1, 4)]
    draft = client.post("/bozze", files=files, data={"nota": "giacca"}).json()
    client.post(f"/bozze/{draft['id']}/prompt", json={"category": "abbigliamento", "model": "Seedream"})
    assert isinstance(seen["look"], list) and len(seen["look"]) == 3
    assert seen["look"][0].name == draft["main"] and "FOTO ALLEGATE: 3" in seen["brief"]
    client.delete(f"/bozze/{draft['id']}")

    # a piece with one photo keeps the single-photo call
    one = client.post("/bozze", files=files[:1], data={"nota": "anello"}).json()
    client.post(f"/bozze/{one['id']}/prompt", json={"category": "bijoux", "model": "Seedream"})
    assert not isinstance(seen["look"], list) and "FOTO ALLEGATE" not in seen["brief"]
    client.delete(f"/bozze/{one['id']}")


def test_a_photo_made_elsewhere_can_be_rated_without_the_studio_prompt(monkeypatch):
    draft = _draft()
    did = draft["id"]
    assert client.get(f"/bozze/{did}/prompt").json()["progress"]["stage"] == "prompt"

    made = client.post(f"/bozze/{did}/prove", json={"external": True, "shot": "worn", "model": "Seedream", "prompt": "my own prompt"})
    assert made.status_code == 200
    payload = made.json()
    attempt = payload["lab"]["attempts"][0]
    assert attempt["external"] is True and attempt["prompt"] == "my own prompt" and payload["lab"]["prompts"] == {}
    assert payload["progress"]["stage"] == "carica" and payload["progress"]["done"]["prompt"] is False

    up = client.post(f"/bozze/{did}/prove/{attempt['id']}/risultato", files={"foto": ("r.jpg", _jpeg(), "image/jpeg")}).json()
    assert up["progress"]["stage"] == "valuta"

    # Codex can judge it: the prompt used is in its request
    seen = {}
    monkeypatch.setattr(server.fucina_codex, "run", lambda prompt, images, model="": seen.update(prompt=prompt) or '{"checklist": {}, "giudizio": "ok", "voto_proposto": 3, "correzione": "", "prompt_corretto": ""}')
    assert client.post(f"/bozze/{did}/prove/{attempt['id']}/valuta", json={}).status_code == 200
    assert "my own prompt" in seen["prompt"]
    rated = client.put(f"/bozze/{did}/prove/{attempt['id']}", json={"rating": 4, "note": ""}).json()
    assert rated["progress"]["stage"] == "fatto"

    # the Studio can still write its own prompts afterwards, and the attempt stays
    _fake_agents(monkeypatch)
    after = client.post(f"/bozze/{did}/prompt", json={"category": "bijoux", "model": "Seedream"}).json()
    assert len(after["lab"]["attempts"]) == 1 and set(after["lab"]["prompts"]) == {"clean", "worn"}
    client.delete(f"/bozze/{did}")


def test_critique_judges_each_photo_against_its_goal():
    ring_worn = prompt_lab.critique_prompt({"category": "bijoux"}, {"shot": "worn", "model": "Seedream", "prompt": "p"})
    assert "mano realistica" in ring_worn and "cinque dita" in ring_worn
    ring_clean = prompt_lab.critique_prompt({"category": "bijoux"}, {"shot": "clean", "model": "Seedream", "prompt": "p"})
    assert "pulita per il sito" in ring_clean and "cinque dita" not in ring_clean
    clothes_clean = prompt_lab.critique_prompt({"category": "abbigliamento"}, {"shot": "clean", "model": "Seedream", "prompt": "p"})
    assert "da studio" in clothes_clean and "gruccia" in clothes_clean
    # no goal known (e.g. an unrated category): the checklist still works
    assert "COSA DEVE ESSERE" not in prompt_lab.critique_prompt({"category": ""}, {"shot": "worn", "model": "x", "prompt": "p"})


def test_clothing_is_judged_on_the_garment_not_on_stones_and_metal():
    clothes = prompt_lab.critique_prompt({"category": "abbigliamento"}, {"shot": "worn", "model": "Seedream", "prompt": "p"})
    assert "Motivo, colori e tessuto" in clothes and "Collo, chiusura" in clothes
    assert "Numero delle pietre" not in clothes and "Metallo e finitura" not in clothes
    assert "motivo, il colore o la forma del capo" in clothes
    # a photo of the garment alone has no hands or body to check
    clean = prompt_lab.critique_prompt({"category": "abbigliamento"}, {"shot": "clean", "model": "Seedream", "prompt": "p"})
    assert "Mani, dita" not in clean
    # jewellery keeps its stones and metal
    ring = prompt_lab.critique_prompt({"category": "bijoux"}, {"shot": "worn", "model": "Seedream", "prompt": "p"})
    assert "Numero delle pietre" in ring and "Metallo e finitura" in ring
    result = prompt_lab.normalize_critique({"checklist": {"motivo_colori": {"esito": "ok", "nota": "x"}}}, "m", prompt_lab.checklist_for("abbigliamento", "worn"))
    assert result["checklist"]["motivo_colori"]["label"] == "Motivo, colori e tessuto" and "pietre_numero" not in result["checklist"]


def test_the_corrected_prompt_keeps_the_woman_tag():
    original = "Keep the jacket. The woman is @MODELLA: use only her face and hair from that reference. No text."
    # the model dropped the tag: it is put back
    fixed = prompt_lab.keep_mentions("Keep the jacket, longer collar. No text.", original)
    assert "@MODELLA" in fixed and "use only her face and hair" in fixed
    # already there: untouched
    same = "Keep the jacket. The woman is @MODELLA: use only her face and hair."
    assert prompt_lab.keep_mentions(same, original) == same
    # a character picked by hand in an external prompt is kept too
    assert "@Modella-Monili-Denti" in prompt_lab.keep_mentions("new prompt", "Keep it on @Modella-Monili-Denti.")
    # no tag in the original (a clean photo): nothing added
    assert prompt_lab.keep_mentions("new prompt", "clean photo") == "new prompt"
    # and the review is told to keep it
    asked = prompt_lab.critique_prompt({"category": "abbigliamento"}, {"shot": "worn", "model": "Seedream", "prompt": original})
    assert "@MODELLA deve restare scritto così" in asked
    # end to end through the normalizer
    out = prompt_lab.normalize_critique({"prompt_corretto": "Better jacket prompt."}, "m", prompt_lab.CHECKLIST, original)
    assert "@MODELLA" in out["prompt_corretto"]


def test_external_photo_of_a_garment_is_reviewed_as_a_garment(monkeypatch):
    # bug: a photo made elsewhere on a piece never analysed had no category, so Codex used the jewellery checklist
    draft = _draft()
    did = draft["id"]
    made = client.post(f"/bozze/{did}/prove", json={"external": True, "shot": "worn", "model": "Seedream", "prompt": "", "category": "abbigliamento"}).json()
    assert made["lab"]["category"] == "abbigliamento"
    attempt = made["lab"]["attempts"][0]
    client.post(f"/bozze/{did}/prove/{attempt['id']}/risultato", files={"foto": ("r.jpg", _jpeg(), "image/jpeg")})
    seen = {}
    monkeypatch.setattr(server.fucina_codex, "run", lambda prompt, images, model="": seen.update(prompt=prompt) or '{"checklist": {}, "giudizio": "ok", "voto_proposto": 3, "correzione": "", "prompt_corretto": ""}')
    assert client.post(f"/bozze/{did}/prove/{attempt['id']}/valuta", json={}).status_code == 200
    assert "Motivo, colori e tessuto" in seen["prompt"] and "Numero delle pietre" not in seen["prompt"]
    assert "ORDINE DI IMPORTANZA" in seen["prompt"] and "fedeltà" in seen["prompt"]
    assert "Capo indossato" in seen["prompt"]  # the goal for the worn garment


def test_each_kind_of_piece_has_its_own_review_sheet():
    import categorie

    assert categorie.subtype_from("", "anello con ametista 159 euro") == "anello"
    assert categorie.subtype_from("", "orecchini a fiore smaltati") == "orecchini"
    assert categorie.subtype_from("", "gilet ricamato", category="abbigliamento") == "capo"
    assert categorie.subtype_from("", "qualcosa", category="accessori") == "foulard"
    ring = prompt_lab.goal_for({"shot": "worn"}, {"category": "bijoux", "subtype": "anello"})
    earring = prompt_lab.goal_for({"shot": "worn"}, {"category": "bijoux", "subtype": "orecchini"})
    assert "dito" in ring and "orecchio" in earring and ring != earring
    assert "fondo avorio" in prompt_lab.goal_for({"shot": "clean"}, {"category": "bijoux", "subtype": "collana"})
    # no subtype: falls back to the category goal
    assert prompt_lab.goal_for({"shot": "worn"}, {"category": "abbigliamento"}).startswith("Capo indossato")
    # every sheet has both sections
    for kind in ("anello", "orecchini", "collana", "bracciale", "capo", "borsa", "foulard"):
        assert prompt_lab.review_sheet(kind, "clean") and prompt_lab.review_sheet(kind, "worn"), kind


def test_brand_rules_come_from_one_file_and_promise_no_fixed_days():
    import main as studio_main

    text = studio_main.BRAND
    assert "I Monili Ravenna" in text and studio_main.SEASON in text and "{SEASON}" not in text
    assert "Martedi" not in text and "nessun giorno" in text.lower()
    assert all(tag in text for tag in studio_main.FIXED_HASHTAGS)
    import reel_studio

    assert reel_studio.FIXED_HASHTAGS is studio_main.FIXED_HASHTAGS
    assert studio_main.MAX_REEL_EXTRA_HASHTAGS == 5 and studio_main.MAX_EXTRA_HASHTAGS == 2
    assert "Mar/Gio/Sab" not in open("reel_studio.py", encoding="utf-8").read()


def test_an_approved_photo_is_exported_for_each_channel():
    import channels

    sizes = {c["id"]: (c["width"], c["height"]) for c in client.get("/canali").json()["channels"]}
    assert sizes["google-foto"] == (1200, 1200) and sizes["tripadvisor"] == (1800, 1200) and sizes["sito"] == (1080, 1350)
    draft = _draft()
    did = draft["id"]
    made = client.post(f"/bozze/{did}/prove", json={"external": True, "shot": "worn", "model": "Seedream", "prompt": "", "category": "bijoux"}).json()
    attempt = made["lab"]["attempts"][0]
    client.post(f"/bozze/{did}/prove/{attempt['id']}/risultato", files={"foto": ("r.jpg", _jpeg(), "image/jpeg")})
    from PIL import Image
    import io as _io

    for channel, size in sizes.items():
        res = client.get(f"/bozze/{did}/prove/{attempt['id']}/canale/{channel}")
        assert res.status_code == 200 and res.headers["content-type"] == "image/jpeg", channel
        assert Image.open(_io.BytesIO(res.content)).size == size, channel
    assert client.get(f"/bozze/{did}/prove/{attempt['id']}/canale/facebook").status_code == 404


def test_texts_follow_one_set_of_platform_rules():
    import main as studio_main

    rules = studio_main.platform_rules()
    for needle in ("non è X, ma Y", "Instagram", "WhatsApp", "Google Business", "Tripadvisor", "155 caratteri"):
        assert needle in rules, needle
    assert "tripadvisor_text" in studio_main.publish_pack_fallback()
    pack = studio_main.normalize_publish_pack({"tripadvisor_text": "Negozio in via Cavour."})
    assert pack["tripadvisor_text"] == "Negozio in via Cavour."
    assert "## Tripadvisor" in studio_main.format_publish_pack_markdown(pack)
