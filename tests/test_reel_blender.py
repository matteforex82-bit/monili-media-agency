from uuid import uuid4

from fastapi.testclient import TestClient

from api import server


def test_blender_brief_can_be_saved_reopened_and_edited_without_a_photo(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    payload = {
        "product": " Giacca ricamata ",
        "brief": "Mostrare ricamo e vestibilità",
        "target_seconds": 12,
        "scheda_run_id": "scheda-esempio",
    }
    with TestClient(server.app) as client:
        response = client.post("/reel-blender/drafts", json=payload)
        assert response.status_code == 201
        draft = response.json()
        assert draft["product"] == "Giacca ricamata"
        assert draft["scheda_run_id"] == "scheda-esempio"
        assert (tmp_path / "reel-blender" / f"{draft['id']}.json").is_file()
        assert not any(item["id"] == draft["id"] for item in client.get("/reels").json()["items"])

    with TestClient(server.app) as client:
        assert client.get("/reel-blender/drafts").json() == {"items": [draft]}
        edited = client.put(f"/reel-blender/drafts/{draft['id']}", json={**payload, "target_seconds": 15})
        assert edited.status_code == 200
        assert edited.json()["id"] == draft["id"]
        assert edited.json()["target_seconds"] == 15
        assert client.get("/reel-blender/drafts").json() == {"items": [edited.json()]}


def test_blender_brief_rejects_invalid_input_and_unknown_draft(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    client = TestClient(server.app)
    assert client.post("/reel-blender/drafts", json={"product": "  "}).status_code == 400
    assert client.post("/reel-blender/drafts", json={"product": "Giacca", "target_seconds": 9}).status_code == 422
    assert client.put(f"/reel-blender/drafts/{uuid4()}", json={"product": "Giacca"}).status_code == 404
    assert client.get("/reel-blender/drafts").json() == {"items": []}


def test_blender_concepts_and_package_survive_reopen_and_export(monkeypatch, tmp_path):
    import json

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    concepts = {
        "concepts": [
            {"title": title, "hook": title, "sequence": "Dettaglio e forma", "risk": "Controlla la luce"}
            for title in ("Ricamo", "Silhouette", "Gesto")
        ],
        "recommended": 0,
    }
    package = {
        "storyboard": "Dettaglio, tre quarti, chiusura.",
        "assets": "Scatta un tre quarti.",
        "audio": "Accento sul taglio.",
        "blender": "Camera e marker.",
        "higgsfield": "Prova una clip.",
        "shots": [
            {"end_ms": end, "framing": "Tre quarti", "camera": "Ferma",
             "lighting": "Laterale", "action": "Posa", "cut": "Secco"}
            for end in (1200, 5500, 12000)
        ],
    }
    responses = iter([concepts, {**package, "shots": package["shots"][:-1]}, package])

    def generate(_key, _model, prompt, *, image_path, max_tokens, all_images):
        assert image_path is None
        assert "Giacca" in prompt
        return json.dumps(next(responses))

    monkeypatch.setattr(server.reel_blender, "generate_text_with_openrouter", generate)
    client = TestClient(server.app)
    payload = {"product": "Giacca", "brief": "Mostra il ricamo"}
    draft = client.post("/reel-blender/drafts", json=payload).json()
    url = f"/reel-blender/drafts/{draft['id']}"
    assert client.post(url + "/package", json={"index": 0}).status_code == 409
    assert client.post(url + "/concepts").json()["concepts"] == concepts["concepts"]
    assert client.post(url + "/package", json={"index": 1}).status_code == 502
    assert client.get(url + "/package.md").status_code == 404
    response = client.post(url + "/package", json={"index": 1})
    assert response.status_code == 200
    assert response.json()["selected"] == 1
    assert client.get("/reel-blender/drafts").json()["items"] == [response.json()]
    export = client.get(url + "/package.md")
    assert "**Silhouette**" in export.text
    assert "00:05.500–00:12.000" in export.text
    assert "Scheda per Claude e Blender" in export.text
    assert client.put(url, json=payload).json()["package"] == package
    assert client.post(url + "/package", json={"index": 1}).json()["package"] == package
    assert "package" not in client.put(url, json={**payload, "target_seconds": 15}).json()


def test_blender_previsualization_preserves_audio_and_keeps_reviews_with_each_version(monkeypatch, tmp_path):
    import json

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    client = TestClient(server.app)
    draft = client.post("/reel-blender/drafts", json={"product": "Giacca"}).json()
    url = f"/reel-blender/drafts/{draft['id']}"
    assert client.post(url + "/previews", files={"video": ("shot.mp4", b"test")}).status_code == 409

    # A package already approved in the previous step, without a revision from an older draft.
    draft_path = tmp_path / "reel-blender" / f"{draft['id']}.json"
    draft["package"] = {"storyboard": "Tre quarti"}
    draft_path.write_text(json.dumps(draft), encoding="utf-8")

    assert client.post(url + "/previews", files={"video": ("shot.mov", b"test")}).status_code == 400
    assert client.post(url + "/previews", files={"video": ("shot.mp4", b"test")}).status_code == 400

    path = tmp_path / "blender.mp4"
    server.reel_studio._run_ffmpeg([
        "-f", "lavfi", "-i", "color=c=red:s=180x320:r=24",
        "-f", "lavfi", "-i", "sine=frequency=440", "-t", "1",
        "-c:v", "libx264", "-c:a", "aac", str(path),
    ])
    source = path.read_bytes()
    first = client.post(url + "/previews", files={"video": ("shot.mp4", source)}, data={"kind": "shot"})
    assert first.status_code == 201
    preview = first.json()["previews"][0]
    assert preview["duration_ms"] == 1000
    assert preview["status"] == "to_review"
    review_url = url + f"/previews/{preview['id']}/review"

    assert client.put(review_url, json={"status": "changes_requested"}).status_code == 400
    assert client.put(review_url, json={"note": {"time_ms": 2000, "text": "Fuori durata"}}).status_code == 400
    note = {"time_ms": 500, "text": "Rallenta la rotazione"}
    assert client.put(review_url, json={"status": "changes_requested", "note": note}).status_code == 200
    retry = client.put(review_url, json={"note": note}).json()["previews"][0]
    assert retry["notes"] == [note]
    assert retry["status"] == "changes_requested"

    second = client.post(url + "/previews", files={"video": ("shot-v2.mp4", source)})
    latest, previous = second.json()["previews"]
    assert previous["id"] == preview["id"] and previous["notes"] == [note]
    assert latest["notes"] == [] and latest["status"] == "to_review"
    media_url = url + f"/previews/{latest['id']}/video"
    assert client.get(media_url).content == source
    assert client.get(media_url, headers={"Range": "bytes=0-9"}).status_code == 206
    assert "attachment" in client.get(media_url + "?download=true").headers["content-disposition"]
    approve = client.put(url + f"/previews/{latest['id']}/review", json={"status": "approved"})
    assert approve.json()["previews"][0]["status"] == "approved"
    assert client.get("/reel-blender/drafts").json()["items"] == [approve.json()]
    edited = client.put(url, json={"product": "Giacca", "brief": "Nuova scena"}).json()
    assert edited["previews"] == approve.json()["previews"]
    assert client.put(review_url, json={"status": "approved"}).status_code == 409
    assert client.get(media_url).content == source


def test_blender_brief_saves_reopens_and_sends_all_reference_photos(monkeypatch, tmp_path, product_photo):
    import json
    from PIL import Image
    import main

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = TestClient(server.app)
    photo_bytes = product_photo.read_bytes()
    base = "/reel-blender/drafts"
    result = client.post(base + "/with-photos", data={"product": "Anello", "target_seconds": 12},
                         files=[("photos", ("fronte.jpg", photo_bytes)), ("photos", ("dettaglio.jpg", photo_bytes))])
    assert result.status_code == 200
    draft = result.json()
    url = f"{base}/{draft['id']}"
    first, second = draft["photos"]
    assert [item["filename"] for item in draft["photos"]] == ["fronte.jpg", "dettaglio.jpg"]
    assert client.get(base).json()["items"] == [draft]
    assert client.get(f"{url}/photos/{second['id']}").headers["content-type"] == "image/jpeg"

    def generate(**kwargs):
        images = kwargs["image_path"]
        assert len(images) == 2
        for photo in images:
            with Image.open(photo) as image:
                assert image.size == (900, 1200)
        response = {
            "concepts": [
                {"title": title, "hook": title, "sequence": "Tre quarti", "risk": "Luce"}
                for title in ("A", "B", "C")
            ],
            "recommended": 0,
        }
        return {"choices": [{"message": {"content": json.dumps(response)}}]}

    monkeypatch.setattr(main, "openrouter_chat_completion", generate)
    planned = client.post(url + "/concepts")
    assert planned.status_code == 200
    stored = planned.json()
    common = {"draft_id": draft["id"], "product": "Anello", "keep_photo_ids": second["id"]}
    assert client.post(base + "/with-photos", data={**common, "expected_updated_at": draft["updated_at"]}).status_code == 409
    bad = client.post(base + "/with-photos", data=common, files={"photos": ("errore.jpg", b"not a photo")})
    assert bad.status_code == 400
    assert client.get(base).json()["items"] == [stored]
    edited = client.post(base + "/with-photos", data={**common, "expected_updated_at": stored["updated_at"]})
    assert edited.status_code == 200
    assert edited.json()["photos"] == [second]
    assert "concepts" not in edited.json()
    assert client.get(f"{url}/photos/{first['id']}").status_code == 404
    assert client.put(url, json={"product": "Anello nuovo"}).json()["photos"] == [second]


def test_blender_scene_uses_local_cli_and_preserves_package_state(monkeypatch, tmp_path, product_photo):
    import json
    import wave

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    client = TestClient(server.app)
    response = client.post("/reel-blender/drafts/with-photos", data={"product": "Giacca"}, files={
        "photos": ("giacca.jpg", product_photo.read_bytes()),
    })
    draft = response.json()
    url = f"/reel-blender/drafts/{draft['id']}/scene"
    assert client.post(url).status_code == 409

    path = tmp_path / "reel-blender" / f"{draft['id']}.json"
    draft.update({
        "concepts": [{"title": "Ricamo", "hook": "Dettaglio", "sequence": "Da vicino"}],
        "selected": 0,
        "package": {
            "storyboard": "Macrodettaglio",
            "assets": "Foto vera",
            "audio": "Accento al taglio",
            "blender": "Set di prova",
            "higgsfield": "Prova una clip",
            "shots": [
                {"end_ms": end, "framing": framing, "camera": "micro push-in", "lighting": "Laterale",
                 "action": "Foto 1", "cut": "Secco"}
                for end, framing in ((1200, "Macro"), (5000, "Tre quarti"), (12000, "Frontale"))
            ],
        },
    })
    path.write_text(json.dumps(draft), encoding="utf-8")
    monkeypatch.setattr(server.blender_scene, "executable", lambda: None)
    assert client.post(url).status_code == 503
    monkeypatch.setattr(server.blender_scene, "executable", lambda: "blender-test")
    built = []

    def build(binary, destination, spec):
        assert binary == "blender-test"
        json.dumps(spec)
        assert spec["shots"][0]["detail"] and spec["shots"][0]["move"]
        assert [shot["end_ms"] for shot in spec["shots"]] == [1200, 5000, 12000]
        assert len(spec["photos"]) == 1
        with wave.open(spec["audio"], "rb") as audio:
            assert audio.getnframes() == 12 * audio.getframerate()
            assert any(audio.readframes(audio.getnframes()))
        built.append(spec["audio_title"])
        destination.write_bytes(b"BLENDER-test-file")

    monkeypatch.setattr(server.blender_scene, "build", build)
    launched = []
    monkeypatch.setattr(server.blender_scene, "open_scene", lambda binary, scene: launched.append(scene))
    assert client.post(url, files={"music": ("brano.mp3", b"non audio")}).status_code == 400
    created = client.post(url)
    assert created.status_code == 201
    scene = created.json()["scene"]
    assert scene["music"] == "Guida ritmica originale · 100 BPM"
    assert scene["shot_count"] == 3
    scene_url = f"{url}/{scene['id']}"
    assert client.get(scene_url).content == b"BLENDER-test-file"
    assert client.post(scene_url + "/open").json() == {"launched": True}
    assert launched[0].name == f"{scene['id']}.blend"

    wav = tmp_path / "musica.wav"
    server.blender_scene.guide_track(wav, 1000, [350])
    uploaded = client.post(url, files={"music": ("musica.wav", wav.read_bytes())})
    assert uploaded.status_code == 201
    assert uploaded.json()["scene"]["music"] == "musica.wav"
    assert client.get(scene_url).status_code == 200
    assert built == ["Guida ritmica originale · 100 BPM", "musica.wav"]
