import base64
import io

from PIL import Image

import higgsfield_client as hf
import reel_kit as kit
import reel_studio as rs


def test_build_video_body_end_frame_per_model():
    kling = hf.build_video_body("kling-3-std", "https://a/start.jpg", "move", 20, last_image_url="https://a/end.jpg")
    assert kling["duration"] == 15 and kling["last_image_url"] == "https://a/end.jpg" and kling["sound"] == "off"
    seed = hf.build_video_body("seedance-2.5", "https://a/start.jpg", "move", 2, last_image_url="https://a/end.jpg")
    assert seed["duration"] == 4 and seed["end_image_url"] == "https://a/end.jpg" and seed["generate_audio"] is False
    assert "last_image_url" not in hf.build_video_body("kling-3-std", "https://a/s.jpg", "m", 5)


def test_credentials(monkeypatch):
    assert not hf.is_configured()
    monkeypatch.setenv("HF_API_KEY_ID", "id")
    monkeypatch.setenv("HF_API_KEY_SECRET", "secret")
    assert hf.credentials() == "id:secret"


def test_keyframe_model_selection(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert not rs.select_keyframe_model().startswith(kit.OPENAI_DIRECT_PREFIX)
    assert not rs.select_keyframe_model("openai-direct/gpt-image-2.5-flare").startswith(kit.OPENAI_DIRECT_PREFIX)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert rs.select_keyframe_model() == "openai-direct/gpt-image-2.5-flare"
    assert rs.select_keyframe_model("google/gemini-3-pro-image") == "google/gemini-3-pro-image"
    assert rs.poster_model("openai-direct/gpt-image-2.5-flare") == "openai-direct/gpt-image-2.5-sunburst"


def test_openai_edit_payload(monkeypatch, tmp_path, product_photo):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    buf = io.BytesIO()
    Image.new("RGB", (1152, 2048), (200, 190, 170)).save(buf, "PNG")
    sent = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"data": [{"b64_json": base64.b64encode(buf.getvalue()).decode()}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        sent.update(url=url, headers=headers, json=json)
        return FakeResponse()

    monkeypatch.setattr(kit.requests, "post", fake_post)
    out = kit.generate_image_multi("unused", "openai-direct/gpt-image-2.5-sunburst", "prompt", [product_photo], tmp_path / "o.png")
    assert sent["url"].endswith("/v1/images/edits")
    assert sent["headers"]["Authorization"] == "Bearer sk-test"
    body = sent["json"]
    assert body["model"] == "gpt-image-2.5-sunburst" and body["size"] == "1152x2048"
    assert body["images"][0]["image_url"].startswith("data:image/jpeg;base64,")
    w, h = (int(x) for x in body["size"].split("x"))
    assert w % 16 == 0 and h % 16 == 0
    assert Image.open(out).size == (1152, 2048)


def test_qa_parsing(monkeypatch, product_photo):
    def answer(text):
        monkeypatch.setattr(kit, "_chat", lambda *a, **k: {"choices": [{"message": {"content": text}}]})
        return kit.check_keyframe("k", "m", product_photo, product_photo)

    assert answer('{"score": 9, "same_product": true, "scene_consistent": true, "artifacts": false}')["ok"]
    assert not answer('{"score": 9, "same_product": false}')["ok"]
    assert not answer('{"score": 9, "same_product": true, "artifacts": true}')["ok"]
    assert not answer('{"score": 7, "same_product": true}')["ok"]  # sotto la soglia 8
    unreadable = answer("non so")
    assert not unreadable["ok"] and not unreadable["checked"]
