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

    def generate(_key, _model, prompt, *, image_path, max_tokens):
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
