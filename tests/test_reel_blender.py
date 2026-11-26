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
