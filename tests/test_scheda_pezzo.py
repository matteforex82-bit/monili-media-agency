"""Missione "scheda pezzo": 3 chiamate di testo, 2 foto AI + la foto reale, AI simulata."""
import base64
import io
import json

from PIL import Image, ImageDraw

import api.server as server
import main

ANALISI = """## IDENTIFICAZIONE
- Categoria esatta: Anello da donna con pietra cabochon viola.
- Materiali identificati con certezza: metallo argentato (probabilmente argento), pietra cabochon viola.

## DESCRIZIONE AI
Anello in metallo argentato con pietra cabochon viola, da I Monili Ravenna.
"""

PLAN = {
    "styling": "Con un maglione color cammello.",
    "woman": "A woman in her fifties with short grey hair and a linen dress.",
    "site_prompts": {"clean": "Ring on warm ivory background.", "worn": "Ring worn on a hand."},
}

PACK = {
    "product_name": "Anello con pietra viola",
    "seo_title": "Anello con pietra viola | I Monili Ravenna",
    "seo_description": "Anello in metallo argentato con pietra viola, in via Cavour a Ravenna.",
    "whatsapp_share": "Guarda questo anello: se ti piace te lo mettiamo da parte.",
    "gmb_title": "Anello con pietra viola",
    "gmb_text": "Nuovo in via Cavour a Ravenna.",
    "caption": "Viola come i mosaici.",
    "hashtags": ["#anello", "#ravenna", "#bijoux", "#viola"],
    "cta": "Scrivici in DM.",
}


def _striped_image(width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height), (240, 232, 220))
    draw = ImageDraw.Draw(img)
    for x in range(0, width, 24):
        draw.line([(x, 0), (x, height)], fill=(90, 60, 130), width=6)
    return img


def _fake_ai(monkeypatch, text_calls: list[str], image_calls: list[str]):
    def fake_text(api_key, model, prompt, image_path=None, max_tokens=2048):
        text_calls.append(prompt)
        if prompt.startswith("Scrivi i testi della scheda"):
            return json.dumps(PACK)
        if "art director del sito vetrina" in prompt:
            return json.dumps(PLAN)
        return ANALISI

    def fake_image(api_key, model, prompt, image_path=None, aspect_ratio="1:1"):
        image_calls.append(prompt)
        buffer = io.BytesIO()
        _striped_image(1200, 1500).save(buffer, "PNG")
        return ["data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")]

    monkeypatch.setattr(main, "generate_text_with_openrouter", fake_text)
    monkeypatch.setattr(main, "generate_image_with_openrouter", fake_image)


def _run(tmp_path, monkeypatch, capsys) -> tuple[dict, list[str], list[str]]:
    photo = tmp_path / "anello.jpg"
    _striped_image(1200, 1500).save(photo, "JPEG", quality=92)
    text_calls: list[str] = []
    image_calls: list[str] = []
    _fake_ai(monkeypatch, text_calls, image_calls)
    main.run_agency(str(photo))
    line = next(row for row in capsys.readouterr().out.splitlines() if row.startswith("__RESULTS_JSON__:"))
    return json.loads(line.split(":", 1)[1]), text_calls, image_calls


def test_mission_makes_only_what_the_site_needs(tmp_path, monkeypatch, capsys):
    results, text_calls, image_calls = _run(tmp_path, monkeypatch, capsys)
    assert len(text_calls) == 3 and len(image_calls) == 2
    assert results["kind"] == "scheda_pezzo"
    sites = [results[k] for k in ("image_site_1", "image_site_2", "image_site_3")]
    assert sites[2].endswith(main.REAL_PHOTO_NAME)
    assert not any(k.startswith(("image_story", "image_carousel", "image_feed")) for k in results)
    pack = json.loads(results["publish_pack_json"])
    assert pack["hashtags"] == ["#imoniliravenna", "#ravenna", "#romagnastyle", "#anello", "#bijoux"]
    assert pack["selected_whatsapp"] == PACK["whatsapp_share"]
    clean, worn = (next(p for p in image_calls if PLAN["site_prompts"][k] in p) for k in ("clean", "worn"))
    assert "WOMAN" in worn and "WOMAN" not in clean
    assert results["woman"] == PLAN["woman"] and PLAN["woman"] in worn  # la donna la inventa il piano, una per pezzo
    assert "NEVER SHOW" in worn and "NEVER SHOW" in clean
    assert "LA DONNA DI QUESTO PEZZO: la inventi tu" in text_calls[1]


def test_new_mission_builds_the_site_card(tmp_path, monkeypatch, capsys):
    results, _, _ = _run(tmp_path, monkeypatch, capsys)
    fiche = server._build_showcase_payload(
        results["run_id"], [results["image_site_1"], results["image_site_3"]], price=45, location="via-cavour-17"
    )["payload"]["product_fiche"]
    assert fiche["title"] == "Anello con pietra viola"
    assert fiche["availableAt"] == ["via-cavour-17"] and "size" not in fiche
    assert fiche["seo"] == {"title": PACK["seo_title"], "description": PACK["seo_description"]}
    assert fiche["summary"].startswith("Anello in metallo argentato")
    assert fiche["materials"] == ["metallo argentato"]
    assert len(fiche["images"]) == 2 and fiche["state"] == "disp"


def _real_photo_candidate(results: dict) -> dict:
    return next(item for item in server._showcase_image_candidates(results) if "real_photo" in item["src"])


def test_real_photo_without_cutout_is_cropped_but_not_suggested(tmp_path, monkeypatch, capsys):
    # Nei test il modello di scontorno non c'è: resta il ritaglio, non spuntato, con il motivo.
    results, _, _ = _run(tmp_path, monkeypatch, capsys)
    check = json.loads(results["real_photo_check"])
    assert check["cleaned"] is False and check["ok"] is False
    real = _real_photo_candidate(results)
    assert real["recommended"] is False and "solo il ritaglio" in real["note"]
    ai = [item for item in server._showcase_image_candidates(results) if "real_photo" not in item["src"]]
    assert len(ai) == 2 and all(item["recommended"] for item in ai)
    assert "Foto reale non spuntata" in results["decision_summary"]


def test_clean_real_photo_is_suggested(tmp_path, monkeypatch, capsys):
    import photo_cleanup

    monkeypatch.setattr(
        photo_cleanup, "clean_photo", lambda photo, model_path, notify=None: (Image.new("RGB", (1200, 1500), (250, 247, 240)), [])
    )
    results, _, _ = _run(tmp_path, monkeypatch, capsys)
    assert json.loads(results["real_photo_check"]) == {"cleaned": True, "ok": True, "issues": []}
    real = _real_photo_candidate(results)
    assert real["recommended"] is True and real["note"] is None


def test_scheda_plan_falls_back_on_bad_json(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "generate_text_with_openrouter", lambda *a, **k: "[Errore API: timeout]")
    plan = main.agent_scheda_plan("m", "k", tmp_path / "x.jpg", ANALISI, "")
    assert plan["site_prompts"]["clean"] and plan["site_prompts"]["worn"]


def test_publish_pack_fallback_keeps_legacy_keys():
    pack = main.normalize_publish_pack({})
    assert pack["hashtags"] == main.FIXED_HASHTAGS
    assert pack["selected_caption"] == pack["caption"] and pack["selected_gmb_text"] == pack["gmb_text"]


def test_reel_of_this_piece_keeps_the_same_woman(tmp_path, monkeypatch, capsys):
    """Un pezzo, una donna: il Reel fatto dalla scheda usa la stessa donna e la sua foto indossata."""
    import reel_kit as kit
    import reel_studio as rs

    results, _, image_calls = _run(tmp_path, monkeypatch, capsys)
    assert results["woman"] in next(p for p in image_calls if "WOMAN" in p)
    worn = next(v for k, v in results.items() if k.startswith("image_site_") and v.endswith(main.WORN_PHOTO_NAME))

    reel_id = rs.new_reel_id()
    input_dir = rs.reel_dir(reel_id) / "input"
    input_dir.mkdir(parents=True)
    photo = input_dir / "photo_1.jpg"
    _striped_image(1200, 1500).save(photo, "JPEG")
    woman, reference = server._scheda_woman(results["run_id"], input_dir)
    assert woman == results["woman"]
    assert reference.read_bytes() == (main.OUTPUT_ROOT / worn).read_bytes()

    state = rs.create_reel(
        reel_id, [photo], [], "", "reel", 12, "kling-3-std", "", "gpt",
        recipe="indossato", woman=woman, woman_reference=reference, scheda_run_id=results["run_id"],
    )
    state["storyboard"] = rs.normalize_storyboard(state, {"shots": [{"keyframe_mode": "ai", "use_model": True, "duration": 3}]})
    seen = []

    def fake_img(api_key, model, prompt, images, destination, aspect_ratio="9:16"):
        seen.append((prompt, [p.name for p in images]))
        destination.write_bytes(photo.read_bytes())
        return destination

    monkeypatch.setattr(kit, "generate_image_multi", fake_img)
    monkeypatch.setattr(kit, "check_keyframe", lambda *a, **k: {"ok": True, "score": 9, "issues": "", "checked": True})
    out = rs.reel_dir(reel_id) / "shots"
    out.mkdir(parents=True, exist_ok=True)
    rs._make_keyframes(state, "k", out)
    prompt, images = seen[0]
    assert woman in prompt and "donna.jpg" in images


def test_reel_without_a_piece_gets_a_new_woman(tmp_path):
    woman, reference = server._scheda_woman("", tmp_path)
    assert woman == "" and reference is None
