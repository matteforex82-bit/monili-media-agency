"""Foto delle varianti di colore e scelta dei modelli immagine (OpenRouter, 07/11/2026)."""
import base64
import io
import json

import pytest
from PIL import Image, ImageDraw

import api.server as server
import main

PLAN = {
    "styling": "Con jeans.",
    "woman": "A woman in her forties.",
    "site_prompts": {"clean": "Product on ivory.", "worn": "WORN-ONE close-up."},
}
PACK = {"product_name": "Anello a colori", "caption": "Prova.", "hashtags": ["#prova"]}
ANELLO = "## IDENTIFICAZIONE\n- Categoria esatta: Anello regolabile in acciaio con tre pietre.\n"


def _photo(path, size=(1200, 1500)):
    img = Image.new("RGB", size, (240, 232, 220))
    ImageDraw.Draw(img).ellipse((300, 400, 900, 1100), fill=(90, 60, 130))
    img.save(path, "JPEG", quality=90)
    return path


def _png(color=(200, 180, 150)):
    buffer = io.BytesIO()
    Image.new("RGB", (1200, 1500), color).save(buffer, "PNG")
    return ["data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")]


def _mission(tmp_path, monkeypatch, capsys, variants_ok):
    import photo_cleanup

    calls = {"image": []}

    def fake_text(api_key, model, prompt, image_path=None, max_tokens=2048):
        if prompt.startswith("Scrivi i testi della scheda"):
            return json.dumps(PACK)
        if "art director del sito vetrina" in prompt:
            return json.dumps(PLAN)
        return ANELLO

    def fake_image(api_key, model, prompt, image_path=None, aspect_ratio="1:1"):
        calls["image"].append(prompt)
        return _png()

    def fake_clean(photo, model_path, notify=None, tight=False):
        if tight and not variants_ok:
            return Image.new("RGB", (1200, 1500), (250, 247, 240)), ["Il pezzo è lungo e stretto"]
        return Image.new("RGB", (1200, 1500), (250, 247, 240)), []

    monkeypatch.setattr(main, "generate_text_with_openrouter", fake_text)
    monkeypatch.setattr(main, "generate_image_with_openrouter", fake_image)
    monkeypatch.setattr(photo_cleanup, "clean_photo", fake_clean)
    variants = str(_photo(tmp_path / "varianti.jpg", (300, 1500)))
    main.run_agency(str(_photo(tmp_path / "anello.jpg")), "", variants_path=variants)
    line = next(row for row in capsys.readouterr().out.splitlines() if row.startswith("__RESULTS_JSON__:"))
    results = json.loads(line.split(":", 1)[1])
    sites = [results[f"image_site_{i}"].rsplit("/", 1)[1] for i in range(1, 9) if f"image_site_{i}" in results]
    return results, sites, calls


def test_a_variants_photo_that_fits_stays_the_real_one(tmp_path, monkeypatch, capsys):
    results, sites, calls = _mission(tmp_path, monkeypatch, capsys, variants_ok=True)
    assert sites == [main.REAL_PHOTO_NAME, main.WORN_PHOTO_NAME, main.VARIANTS_PHOTO_NAME]
    assert len(calls["image"]) == 1  # only the worn shot: no AI for the variants
    candidate = next(c for c in server._showcase_image_candidates(results) if main.VARIANTS_PHOTO_NAME in c["src"])
    assert candidate["recommended"] is True and candidate["available"] is True


def test_a_variants_photo_that_does_not_fit_is_tidied_by_the_ai_and_not_ticked(tmp_path, monkeypatch, capsys):
    results, sites, calls = _mission(tmp_path, monkeypatch, capsys, variants_ok=False)
    assert main.VARIANTS_AI_PHOTO_NAME in sites and main.VARIANTS_PHOTO_NAME in sites
    assert any("available colours" in prompt for prompt in calls["image"])
    candidates = server._showcase_image_candidates(results)
    ai = next(c for c in candidates if main.VARIANTS_AI_PHOTO_NAME in c["src"])
    real = next(c for c in candidates if main.VARIANTS_PHOTO_NAME in c["src"])
    assert ai["recommended"] is False and "controlla" in ai["note"]
    assert real["recommended"] is False  # long and narrow: small in the frame
    # Photos made by the AI are labelled "AI" on the site.
    assert main.VARIANTS_AI_PHOTO_NAME in main.AI_WORN_PHOTO_NAMES


def test_the_variants_photo_reaches_the_mission(monkeypatch):
    from fastapi.testclient import TestClient

    started = {}

    async def fake_run(job_id, foto_path, brief, image_model, text_model, detail_path=None, variants_path=None):
        started["variants"] = variants_path

    monkeypatch.setattr(server, "_run_mission", fake_run)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    buffer = io.BytesIO()
    Image.new("RGB", (40, 50), (10, 10, 10)).save(buffer, "JPEG")
    files = {
        "foto": ("anello.jpg", buffer.getvalue(), "image/jpeg"),
        "varianti": ("colori.jpg", buffer.getvalue(), "image/jpeg"),
    }
    assert TestClient(server.app).post("/mission/start", files=files).status_code == 200
    assert started["variants"] is not None and started["variants"].name.endswith("_varianti.jpg")


def test_a_failing_image_model_falls_back_to_the_next_one(monkeypatch):
    tried = []

    def fake_image(api_key, model, prompt, image_path=None, aspect_ratio="1:1"):
        tried.append(model)
        if model == "google/gemini-nano-banana-2.1":
            raise RuntimeError("provider error")
        return _png()

    monkeypatch.setattr(main, "generate_image_with_openrouter", fake_image)
    urls = main.generate_image_with_fallback("key", "google/gemini-nano-banana-2.1", "prompt", None, "Foto prova")
    assert urls and tried == ["google/gemini-nano-banana-2.1", "openai/gpt-image-2.6-sunburst"]


def test_a_retired_model_is_replaced_by_the_default(monkeypatch):
    monkeypatch.setenv("OPENROUTER_IMAGE_MODEL", "openai/gpt-5.4-image-2")
    assert main.select_openrouter_image_model("openai/gpt-5.4-image-2") == main.DEFAULT_OPENROUTER_IMAGE_MODEL
    assert main.select_openrouter_image_model("") == main.DEFAULT_OPENROUTER_IMAGE_MODEL
    assert main.select_openrouter_image_model("openai/gpt-image-2.6-sunburst") == "openai/gpt-image-2.6-sunburst"
    assert main.DEFAULT_OPENROUTER_IMAGE_MODEL == "google/gemini-nano-banana-2.1"
    assert main.SUPPORTED_OPENROUTER_IMAGE_MODELS == server.SUPPORTED_OPENROUTER_IMAGE_MODELS


def test_gpt_image_uses_the_image_api_with_the_photo_as_reference(monkeypatch, tmp_path):
    sent = {}

    class Reply:
        status_code = 200

        @staticmethod
        def json():
            return {"data": [{"b64_json": "QUJD", "media_type": "image/png"}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        sent["url"], sent["payload"] = url, json
        return Reply()

    monkeypatch.setattr(main.requests, "post", fake_post)
    photo = _photo(tmp_path / "anello.jpg", (200, 250))
    urls = main.generate_image_with_openrouter("key", "openai/gpt-image-2.6-sunburst", "prompt", photo, "4:5")
    assert sent["url"].endswith("/api/v1/images") and urls == ["data:image/png;base64,QUJD"]
    assert sent["payload"]["aspect_ratio"] == "3:4"  # GPT Image has no 4:5
    assert sent["payload"]["input_references"][0]["image_url"]["url"].startswith("data:image/")


def test_the_image_api_error_is_not_hidden(monkeypatch):
    class Reply:
        status_code = 400
        text = '{"error":{"message":"No provider supports aspect_ratio"}}'

    monkeypatch.setattr(main.requests, "post", lambda *a, **k: Reply())
    with pytest.raises(RuntimeError, match="No provider supports"):
        main.generate_image_with_image_api("key", "openai/gpt-image-2.6-sunburst", "prompt")


def test_a_provider_error_in_a_200_reply_is_reported(monkeypatch):
    monkeypatch.setattr(
        main,
        "openrouter_chat_completion",
        lambda **kwargs: {"error": {"message": "Complexity 'none' is not supported", "code": 502}},
    )
    with pytest.raises(RuntimeError, match="Complexity 'none'"):
        main.generate_image_with_openrouter("key", "google/gemini-nano-banana-2.1", "prompt")
