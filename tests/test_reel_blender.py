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
        "direction": {"set_mood": "deep_charcoal", "set_design": "Fondale scuro", "continuity": "Stessa luce",
                      "music_bpm": 96, "music_feel": "Percussione morbida"},
        "shots": [
            {"end_ms": end, "framing": "Tre quarti", "camera": "Ferma",
             "lighting": "Laterale", "action": "Posa", "cut": "Secco",
             "design": {"purpose": "Mostra il volume", "scale": "medium", "sound": "Fruscio"}}
            for end in (1200, 5500, 12000)
        ],
    }
    package = server.reel_blender.Handoff.model_validate(package).model_dump(exclude_none=True)
    responses = iter([concepts, {**package, "shots": package["shots"][:-1]}, package, package])

    def generate(prompt, images):
        assert images == []
        assert "Giacca" in prompt
        assert "GIA, fotografia" in prompt and "continuità" in prompt
        return json.dumps(next(responses))

    monkeypatch.setattr(server.fucina_codex, "run", generate)
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
    assert "96 BPM" in export.text and "Funzione — Mostra il volume" in export.text
    assert client.put(url, json=payload).json()["package"] == package
    assert client.post(url + "/package", json={"index": 1}).json()["package"] == package
    refreshed = client.post(url + "/package", json={"index": 1, "refresh_direction": True}).json()
    assert refreshed["selected"] == 1 and refreshed["package_revision"] != response.json()["package_revision"]
    assert "package" not in client.put(url, json={**payload, "target_seconds": 15}).json()


def test_blender_photo_only_recognizes_routes_and_resolves_ambiguity(monkeypatch, tmp_path, product_photo):
    import json

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    jacket = {"product": "Giacca ricamata", "template": "Giacca o gilet", "detail": "Motivo sulle maniche"}
    jacket_ideas = {
        "concepts": [
            {"title": title, "hook": title, "sequence": "Ricamo e silhouette", "risk": "Controlla l'orlo"}
            for title in ("Ricamo", "Silhouette", "Profilo")
        ],
        "recommended": 1,
        "recognition": jacket,
    }
    package = {
        "storyboard": "Ricamo, giacca in posa, frontale", "assets": "Usa il frontale", "audio": "Accento sullo stacco",
        "blender": "Camere controllate", "higgsfield": "Prova il tre quarti",
        "direction": {"set_design": "Fondale avorio", "continuity": "Stessa luce", "music_feel": "Morbida"},
        "shots": [
            {"end_ms": end, "framing": title, "camera": "Ferma", "lighting": "Laterale",
             "action": "In posa", "cut": "Secco", "design": {"purpose": title, "scale": "detail", "sound": "Musica"}}
            for end, title in ((1200, "Ricamo"), (6000, "Tre quarti"), (12000, "Frontale"))
        ],
    }
    question = "Vuoi mettere in evidenza la giacca o la borsa?"
    responses = iter([jacket_ideas, package, {"clarification": question}, jacket_ideas])
    prompts = []

    def generate(prompt, images):
        assert len(images) == 1 and images[0].is_file()
        prompts.append(prompt)
        return json.dumps(next(responses))

    client = TestClient(server.app)
    base = "/reel-blender/drafts"
    upload = {"photos": ("fronte.jpg", product_photo.read_bytes(), "image/jpeg")}
    assert client.post(base + "/with-photos").status_code == 400
    draft = client.post(base + "/with-photos", files=upload).raise_for_status().json()
    assert draft["product"] == ""
    url = f"{base}/{draft['id']}"
    monkeypatch.setattr(server.fucina_codex, "executable", lambda: None)
    unavailable = client.post(url + "/concepts")
    assert unavailable.status_code == 502
    assert "Codex non è installato" in unavailable.json()["error"]
    assert client.get(base).json()["items"] == [draft]

    monkeypatch.setattr(server.fucina_codex, "run", generate)
    recognized = client.post(url + "/concepts").raise_for_status().json()
    assert recognized["recognition"] == jacket and recognized["recommended"] == 1
    assert len(prompts) == 1 and '"product": ""' in prompts[0]

    planned = client.post(url + "/package", json={"index": 1}).raise_for_status().json()
    assert planned["selected"] == 1
    assert '"product": "Giacca ricamata"' in prompts[1]
    assert "\n## Giacca o gilet\n" in prompts[1] and "\n## Anello\n" not in prompts[1]
    assert client.get(url + "/package.md").text.startswith("# Giacca ricamata · Reel Blender")
    assert client.put(url, json={}).raise_for_status().json()["package"] == planned["package"]

    unclear = client.post(base + "/with-photos", files=upload).raise_for_status().json()
    unclear_url = f"{base}/{unclear['id']}"
    paused = client.post(unclear_url + "/concepts").raise_for_status().json()
    assert paused["clarification"] == question and not paused["concepts"]
    assert client.post(unclear_url + "/package", json={"index": 0}).json()["error"] == question
    named = client.put(unclear_url, json={"product": "Giacca"}).raise_for_status().json()
    assert named["photos"] == unclear["photos"] and not named.get("clarification")
    assert client.post(unclear_url + "/concepts").raise_for_status().json()["recommended"] == 1


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

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
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

    def generate(prompt, images):
        assert len(images) == 2
        assert '"foto_in_ordine": ["fronte.jpg", "dettaglio.jpg"]' in prompt
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
        return json.dumps(response)

    monkeypatch.setattr(server.fucina_codex, "run", generate)
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
        assert spec["shots"][0]["scale"] == "macro" and spec["shots"][0]["motion"] == "push"
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

    advanced = uploaded.json()
    advanced["package"]["direction"] = {
        "set_mood": "deep_charcoal", "set_design": "Fondale", "continuity": "Luce coerente",
        "music_bpm": 96, "music_feel": "Leggera",
    }
    advanced["package"]["shots"][1]["design"] = {
        "motion": "slide", "light": "jewelry", "key_side": "right", "lens_mm": 85,
        "purpose": "Mostra il volume", "sound": "Fruscio", "reference_photo": 2, "accent": "strong",
    }
    path.write_text(json.dumps(advanced), encoding="utf-8")

    def advanced_build(binary, destination, spec):
        assert spec["set_mood"] == "deep_charcoal"
        assert spec["audio_accents"] == [(1200, "strong"), (5000, "soft")]
        shot = spec["shots"][1]
        assert (shot["motion"], shot["light"], shot["key_side"], shot["lens_mm"]) == ("slide", "jewelry", "right", 85)
        build(binary, destination, spec)

    monkeypatch.setattr(server.blender_scene, "build", advanced_build)
    assert client.post(url).json()["scene"]["music"] == "Guida ritmica originale · 96 BPM"


def test_higgsfield_handoff_exports_a_muted_shot_and_keeps_results_with_it(monkeypatch, tmp_path, product_photo):
    import io
    import json
    import subprocess
    import zipfile

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    client = TestClient(server.app)
    response = client.post("/reel-blender/drafts/with-photos", data={"product": "Giacca"}, files={
        "photos": ("giacca.jpg", product_photo.read_bytes()),
    })
    draft = response.json()
    url = f"/reel-blender/drafts/{draft['id']}"
    path = tmp_path / "reel-blender" / f"{draft['id']}.json"
    draft.update({
        "package_revision": "regia-attuale",
        "package": {
            "higgsfield": "Mantieni ricamo e zip.",
            "shots": [
                {"end_ms": 1200, "framing": "Ricamo", "camera": "Macro", "lighting": "Radente",
                 "action": "Segui il filo", "cut": "Stacco netto"},
                {"end_ms": 5000, "framing": "Tre quarti", "camera": "Ferma", "lighting": "Laterale",
                 "action": "Posa stabile", "cut": "Secco", "video_prompt_en": "Keep the jacket still at three quarters."},
            ],
        },
    })
    path.write_text(json.dumps(draft), encoding="utf-8")
    source_path = tmp_path / "blender.mp4"
    server.reel_studio._run_ffmpeg([
        "-f", "lavfi", "-i", "color=c=blue:s=180x320:r=24",
        "-f", "lavfi", "-i", "sine=frequency=440", "-t", "1",
        "-c:v", "libx264", "-c:a", "aac", str(source_path),
    ])
    source = source_path.read_bytes()
    upload = client.post(url + "/previews", files={"video": ("shot.mp4", source)}, data={"shot_index": 1})
    assert upload.status_code == 201
    preview = upload.json()["previews"][0]
    assert preview["shot_index"] == 1
    base = url + f"/previews/{preview['id']}"
    assert client.post(base + "/higgsfield/package", json={"shot_index": 1}).status_code == 409
    assert client.put(base + "/review", json={"status": "approved"}).status_code == 200
    assert client.post(base + "/higgsfield/package", json={"shot_index": 0}).status_code == 409
    download = client.post(base + "/higgsfield/package", json={"shot_index": 1})
    assert download.status_code == 200
    assert "shot-02.zip" in download.headers["content-disposition"]
    with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
        assert set(archive.namelist()) == {
            "riferimento-blender.mp4", "LEGGIMI.md", "prompt-en.txt", "foto-en.txt", "composizione.jpg", "foto-prodotto/foto-1.jpg",
        }
        readme = archive.read("LEGGIMI.md").decode()
        assert "Inquadratura 2 · Tre quarti" in readme and "00:01.200–00:05.000" in readme
        assert "Seedance" in readme and "Kling" not in readme
        assert archive.read("prompt-en.txt").startswith(b"Keep the jacket still at three quarters.")
        exported = tmp_path / "muto.mp4"
        exported.write_bytes(archive.read("riferimento-blender.mp4"))
    probe = subprocess.run([server.reel_studio.ffmpeg_exe(), "-i", str(exported)], capture_output=True, text=True)
    assert "Video: h264" in probe.stderr and "720x1280" in probe.stderr and "Audio:" not in probe.stderr
    assert client.get(base + "/video").content == source

    result_url = base + "/higgsfield/results"
    assert client.post(result_url, files={"video": ("output.mp4", source)}, data={"shot_index": 0}).status_code == 409
    comparison = client.post(result_url, files={"video": ("output.mp4", source)}, data={"shot_index": 1})
    assert comparison.status_code == 201
    saved = comparison.json()["previews"][0]["higgsfield_results"][0]
    assert saved["shot_index"] == 1
    assert client.get(result_url + f"/{saved['id']}").content == source
    assert client.get("/reel-blender/drafts").json()["items"] == [comparison.json()]

    changed = client.put(url, json={"product": "Giacca nuova"})
    assert changed.status_code == 200
    assert client.post(base + "/higgsfield/package", json={"shot_index": 1}).status_code == 409


def test_blender_render_packages_music_and_individual_seedance_shots(monkeypatch, tmp_path, product_photo):
    import io
    import json
    import shutil
    import subprocess
    import threading
    import time
    import uuid
    import zipfile

    monkeypatch.setattr(server, "STORAGE_ROOT", tmp_path)
    monkeypatch.setattr(server.blender_scene, "executable", lambda: "blender-test")
    client = TestClient(server.app)
    draft = client.post("/reel-blender/drafts/with-photos", data={"product": "Giacca"}, files={
        "photos": ("ricamo.jpg", product_photo.read_bytes()),
    }).json()
    draft_id = uuid.UUID(draft["id"])
    scene_id = uuid.uuid4()
    blend = server._blender_scene_path(draft_id, scene_id)
    blend.parent.mkdir(parents=True)
    blend.write_bytes(b"scene")
    draft.update({
        "scene": {"id": str(scene_id)},
        "package_revision": "regia-renderizzata",
        "package": {"shots": [
            {"framing": "Ricamo", "design": {"scale": "macro"}, "photo_prompt_en": "Frame the blue embroidery."},
            {"framing": "Tre quarti", "design": {"scale": "look", "motion": "fixed"}},
        ]},
    })
    meta = tmp_path / "reel-blender" / f"{draft_id}.json"
    meta.write_text(json.dumps(draft), encoding="utf-8")
    base = f"/reel-blender/drafts/{draft_id}"
    render = f"{base}/scene/{scene_id}/render"
    prompt_plan = client.get(base + "/seedance-prompts").json()["items"]
    assert prompt_plan[0]["photo_en"].startswith("Frame the blue embroidery.")
    assert prompt_plan[1]["video_en"].startswith("Keep the camera locked off")
    assert prompt_plan[0]["product_reference"] == 1

    video = tmp_path / "fake-render.mp4"
    server.reel_studio._run_ffmpeg([
        "-f", "lavfi", "-i", "color=c=blue:s=180x320:r=30", "-t", "0.6",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(video),
    ])
    gate = threading.Event()
    entered = threading.Event()

    def fake_render(binary, source, folder, log):
        assert binary == "blender-test" and source == blend
        log.write_text("MONILI_TOTAL 18\nMONILI_FRAME 8\n", encoding="utf-8")
        entered.set()
        assert gate.wait(5)
        shutil.copyfile(video, folder / "video-0001-0018.mp4")
        server.blender_scene.guide_track(folder / "musica.wav", 600, [300])
        (folder / "timeline.json").write_text(json.dumps({
            "fps": 30, "frames": 18,
            "shots": [
                {"camera": "02 Tre quarti", "start_frame": 0, "end_frame": 9},
                {"camera": "01 Ricamo", "start_frame": 9, "end_frame": 18},
            ],
        }), encoding="utf-8")

    monkeypatch.setattr(server.reel_blender_render, "_render_source", fake_render)
    assert client.get(render).json() == {"status": "idle"}
    queued = client.post(render)
    assert queued.status_code == 202
    render_id = queued.json()["id"]
    assert entered.wait(5)
    try:
        assert client.post(render).json()["id"] == render_id
        progress = client.get(render).json()
        assert progress["frame"] == 8 and progress["frames"] == 18
        assert client.get(f"{render}/{render_id}/video").status_code == 404
    finally:
        gate.set()

    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        state = client.get(render).json()
        if state["status"] in {"ready", "error"}:
            break
        time.sleep(0.03)
    assert state["status"] == "ready", state
    assert state["duration_ms"] == 600 and state["review_available"]
    video_response = client.get(f"{render}/{render_id}/video")
    assert video_response.status_code == 200
    master = tmp_path / "master.mp4"
    master.write_bytes(video_response.content)
    kit = client.get(f"{render}/{render_id}/kit")
    assert kit.status_code == 200
    with zipfile.ZipFile(io.BytesIO(kit.content)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        first, second = manifest["shots"]
        assert manifest["model_family"] == "seedance" and manifest["workflow"] == "manual"
        assert first["title"] == "Tre quarti" and first["end_ms"] == 300
        assert second["title"] == "Ricamo" and second["start_ms"] == 300
        assert second["source_image"] is None
        assert archive.read(second["photo_prompt"]).startswith(b"Frame the blue embroidery.")
        assert all(path in archive.namelist() for path in (first["composition_image"], first["product_reference"], manifest["soundtrack"]))
        shot = tmp_path / "shot.mp4"
        shot.write_bytes(archive.read(first["video_reference"]))
    ffmpeg = server.reel_studio.ffmpeg_exe()
    master_probe = subprocess.run([ffmpeg, "-i", str(master)], capture_output=True, text=True)
    shot_probe = subprocess.run([ffmpeg, "-i", str(shot)], capture_output=True, text=True)
    assert "Audio: aac" in master_probe.stderr
    assert "Audio:" not in shot_probe.stderr
    assert server.reel_studio.probe_duration(shot) == 0.3

    review = f"{render}/{render_id}/review"
    assert client.post(review, json={"shot_index": 2}).status_code == 404
    opened = client.post(review, json={"shot_index": 1})
    assert opened.status_code == 200
    data = opened.json()
    preview = data["draft"]["previews"][0]
    assert preview["id"] == data["preview_id"] and preview["shot_index"] == 1
    assert preview["timeline_start_ms"] == 0 and preview["timeline_end_ms"] == 300
    preview_url = f"{base}/previews/{data['preview_id']}"
    assert client.get(preview_url + "/video").content == shot.read_bytes()
    assert client.put(preview_url + "/review", json={"status": "approved"}).status_code == 200
    reopened = client.post(review, json={"shot_index": 1}).json()
    assert reopened["preview_id"] == data["preview_id"]
    assert [item["status"] for item in reopened["draft"]["previews"]] == ["approved"]

    newer = {**reopened["draft"], "package_revision": "regia-aggiornata"}
    meta.write_text(json.dumps(newer), encoding="utf-8")
    assert client.post(review, json={"shot_index": 1}).status_code == 409


def test_blender_template_is_taken_from_recognition_or_guessed_from_the_name():
    import blender_scene

    assert blender_scene.template_for({"recognition": {"template": "Borsa"}, "product": "Anello"}) == "Borsa"
    assert blender_scene.template_for({"product": "Anello con pietre viola", "brief": ""}) == "Anello"
    assert blender_scene.template_for({"product": "Girocollo in argento"}) == "Collana"
    assert blender_scene.template_for({"product": "Qualcosa di strano", "brief": ""}) == "Regia libera"


def test_every_product_template_has_a_3d_stage_and_a_stage_action_sequence():
    import re
    import sys
    from pathlib import Path

    templates = re.findall(r"^## (.+)$", Path("knowledge/reel-blender-template-prodotti.md").read_text(encoding="utf-8"), flags=re.M)
    templates = [name for name in templates if name != "Procedura comune"]
    sys.path.insert(0, str(Path("scripts").resolve()))
    # reel_props usa bpy: leggiamo la tabella senza importarlo
    source = Path("scripts/reel_props.py").read_text(encoding="utf-8")
    for name in templates:
        assert f'"{name}":' in source, name
    assert "Occhiali" not in source
    from reel_blender import Template
    assert set(Template.__args__) == set(templates) | {"Regia libera"}


def test_blender_builds_a_3d_set_for_each_kind_of_accessory(tmp_path):
    import json
    import subprocess

    import blender_scene

    binary = blender_scene.executable()
    if not binary:
        import pytest
        pytest.skip("Blender non installato")
    shots = blender_scene.shot_settings([
        {"end_ms": 2000, "framing": "macro", "camera": "fisso", "action": "", "design": {"scale": "macro", "stage_action": "reveal"}},
        {"end_ms": 5000, "framing": "medio", "camera": "push", "action": "", "design": {"scale": "medium", "stage_action": "handle"}},
        {"end_ms": 8000, "framing": "indossato", "camera": "fisso", "action": "", "design": {"scale": "detail", "stage_action": "worn"}},
    ])
    audio = tmp_path / "musica.wav"
    blender_scene.guide_track(audio, 8000, [], 100)
    for template in ("Anello", "Giacca o gilet"):
        spec = {"shots": shots, "fps": 30, "photos": [], "audio": str(audio), "audio_title": "t", "audio_accents": [],
                "set_mood": "warm_cream", "notes": "x", "template": template}
        destination = tmp_path / f"{template[:4]}.blend"
        blender_scene.build(binary, destination, spec)
        check = tmp_path / "check.py"
        check.write_text(
            "import bpy\nscene = bpy.data.scenes['Set e camere']\n"
            "print('CAMERE', len([m for m in scene.timeline_markers if m.camera]))\n"
            "print('OGGETTI', len([o for o in scene.objects if o.type == 'MESH']))\n", encoding="utf-8",
        )
        out = subprocess.run([binary, "-b", str(destination), "--python", str(check)], capture_output=True, text=True, timeout=120).stdout
        assert "CAMERE 3" in out
        meshes = int(out.split("OGGETTI")[1].split()[0])
        assert meshes > 30, f"{template}: scena troppo povera ({meshes} oggetti)"
