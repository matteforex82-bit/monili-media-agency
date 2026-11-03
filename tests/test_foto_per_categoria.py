"""Le foto del sito seguono il tipo di pezzo: copertina vera, all'AI solo gli indossati."""
import base64
import io
import json

import pytest
from PIL import Image, ImageDraw

import api.server as server
import main

GIACCA = """## IDENTIFICAZIONE
### Categoria esatta
Giacca corta da donna stile kimono, ricamata.

## STYLING
Con orecchini pendenti e una collana lunga.
"""

ANELLO = """## IDENTIFICAZIONE
- Categoria esatta: Anello in argento con pietra viola.
"""

PLAN = {
    "styling": "Con jeans e stivali.",
    "woman": "A woman in her fifties with short grey hair.",
    "site_prompts": {
        "clean": "Product on ivory.",
        "worn": "WORN-ONE full figure.",
        "worn_2": "WORN-TWO back view in another street.",
    },
}

PACK = {"product_name": "Pezzo di prova", "caption": "Prova.", "hashtags": ["#prova"]}


def _photo(path, color=(240, 232, 220)):
    img = Image.new("RGB", (1200, 1500), color)
    ImageDraw.Draw(img).ellipse((300, 400, 900, 1100), fill=(90, 60, 130))
    img.save(path, "JPEG", quality=90)
    return path


def _mission(tmp_path, monkeypatch, capsys, analisi, clean_ok=True, detail=False):
    import photo_cleanup

    calls = {"text": [], "image": []}

    def fake_text(api_key, model, prompt, image_path=None, max_tokens=2048):
        calls["text"].append(prompt)
        if prompt.startswith("Scrivi i testi della scheda"):
            return json.dumps(PACK)
        if "art director del sito vetrina" in prompt:
            return json.dumps(PLAN)
        return analisi

    def fake_image(api_key, model, prompt, image_path=None, aspect_ratio="1:1"):
        calls["image"].append(prompt)
        buffer = io.BytesIO()
        Image.new("RGB", (1200, 1500), (200, 180, 150)).save(buffer, "PNG")
        return ["data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")]

    def fake_clean(photo, model_path, notify=None):
        return Image.new("RGB", (1200, 1500), (250, 247, 240)), ([] if clean_ok else ["bordi sporchi"])

    monkeypatch.setattr(main, "generate_text_with_openrouter", fake_text)
    monkeypatch.setattr(main, "generate_image_with_openrouter", fake_image)
    monkeypatch.setattr(photo_cleanup, "clean_photo", fake_clean)
    detail_path = str(_photo(tmp_path / "dettaglio.jpg", (30, 30, 30))) if detail else ""
    main.run_agency(str(_photo(tmp_path / "pezzo.jpg")), "", detail_path=detail_path)
    line = next(row for row in capsys.readouterr().out.splitlines() if row.startswith("__RESULTS_JSON__:"))
    results = json.loads(line.split(":", 1)[1])
    sites = [results[f"image_site_{i}"] for i in range(1, 9) if f"image_site_{i}" in results]
    return results, sites, calls


def test_clothing_gets_the_real_cover_and_two_worn_shots(tmp_path, monkeypatch, capsys):
    results, sites, calls = _mission(tmp_path, monkeypatch, capsys, GIACCA)
    assert results["category"] == "abbigliamento"
    assert [s.rsplit("/", 1)[1] for s in sites] == [main.REAL_PHOTO_NAME, main.WORN_PHOTO_NAME, "site_04_worn_2.jpg"]
    # No AI catalog photo: the real one came out clean. Two worn shots, same woman.
    assert len(calls["image"]) == 2 and all(PLAN["woman"] in prompt for prompt in calls["image"])
    assert "WORN-ONE" in calls["image"][0] and "WORN-TWO" in calls["image"][1]
    plan_prompt = next(p for p in calls["text"] if "art director del sito vetrina" in p)
    assert "CAPO DI ABBIGLIAMENTO" in plan_prompt and '"worn_2"' in plan_prompt


def test_jewelry_gets_one_close_worn_shot_and_the_real_detail(tmp_path, monkeypatch, capsys):
    results, sites, calls = _mission(tmp_path, monkeypatch, capsys, ANELLO, detail=True)
    assert results["category"] == "gioielli"
    assert [s.rsplit("/", 1)[1] for s in sites] == [main.REAL_PHOTO_NAME, main.WORN_PHOTO_NAME, main.DETAIL_PHOTO_NAME]
    assert len(calls["image"]) == 1
    plan_prompt = next(p for p in calls["text"] if "art director del sito vetrina" in p)
    assert "GIOIELLO" in plan_prompt and '"worn_2"' not in plan_prompt
    detail = next(c for c in server._showcase_image_candidates(results) if main.DETAIL_PHOTO_NAME in c["src"])
    assert detail["recommended"] is True and detail["available"] is True


def test_an_unclean_real_photo_brings_back_the_ai_catalog_cover(tmp_path, monkeypatch, capsys):
    _, sites, calls = _mission(tmp_path, monkeypatch, capsys, ANELLO, clean_ok=False)
    names = [s.rsplit("/", 1)[1] for s in sites]
    assert names == ["site_01_product_clean.jpg", main.WORN_PHOTO_NAME, main.REAL_PHOTO_NAME]
    assert len(calls["image"]) == 2


def test_the_detail_photo_reaches_the_mission(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient

    started = {}

    async def fake_run(job_id, foto_path, brief, image_model, text_model, detail_path=None):
        started["foto"], started["detail"] = foto_path, detail_path

    monkeypatch.setattr(server, "_run_mission", fake_run)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    buffer = io.BytesIO()
    Image.new("RGB", (40, 50), (10, 10, 10)).save(buffer, "JPEG")
    files = {
        "foto": ("anello.jpg", buffer.getvalue(), "image/jpeg"),
        "dettaglio": ("pietra.jpg", buffer.getvalue(), "image/jpeg"),
    }
    reply = TestClient(server.app).post("/mission/start", files=files, data={"brief": "Anello 35€"})
    assert reply.status_code == 200
    assert started["detail"] is not None and started["detail"].name.endswith("_dettaglio.jpg")


@pytest.mark.parametrize("category", ["abbigliamento", "gioielli", "bijoux", "accessori"])
def test_every_category_has_worn_shots_and_a_guide(category):
    import categorie

    assert categorie.AI_SHOTS[category][0] == "worn" and categorie.SHOT_GUIDE[category]
