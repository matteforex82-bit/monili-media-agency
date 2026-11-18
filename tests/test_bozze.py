"""Bozze veloci: foto e nota salvate in negozio, la Scheda pezzo si crea dopo. Senza rete e senza AI."""
import io

from fastapi.testclient import TestClient
from PIL import Image

import api.server as server
import bozze

client = TestClient(server.app)


def _jpeg(color=(200, 120, 60), size=(900, 1200)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, "JPEG")
    return buffer.getvalue()


def test_quick_facts_reads_price_size_and_stones():
    facts = bozze.quick_facts("anello argento, pietra ametista 159 euro, misura 13")
    assert facts == {"prezzo": 159, "misura": "13", "pietre": ["Ametista"]}
    assert bozze.quick_facts("giacca ricamata € 89,50 taglia m")["prezzo"] == 89.5
    assert bozze.quick_facts("giacca ricamata € 89,50 taglia m")["misura"] == "M"
    assert bozze.quick_facts("orecchini quarzo rosa 45€")["pietre"] == ["Quarzo rosa"]
    assert bozze.quick_facts("") == {}
    assert "prezzo" not in bozze.quick_facts("collana lunga 45 cm")


def test_store_lifecycle(tmp_path):
    store = bozze.BozzeStore(tmp_path / "bozze", trash=tmp_path / "cestino")
    draft_id, folder = store.new_folder()
    (folder / "foto-1.jpg").write_bytes(b"x")
    (folder / "foto-2.jpg").write_bytes(b"y")
    meta = store.create(folder, " ametista 159 euro ", ["foto-1.jpg", "foto-2.jpg"])
    assert meta["status"] == bozze.STATUS_TODO and meta["main"] == "foto-1.jpg" and meta["detail"] == "foto-2.jpg"
    assert meta["note"] == "ametista 159 euro" and meta["facts"]["prezzo"] == 159

    # the id is the only way in: no paths
    assert store.get("../x") is None and store.photo_path(draft_id, "../bozza.json") is None
    assert store.photo_path(draft_id, "foto-1.jpg") is not None

    assert store.update(draft_id, main="foto-2.jpg", detail="non-esiste.jpg")["detail"] == ""
    removed = store.remove_photo(draft_id, "foto-2.jpg")
    assert removed["photos"] == ["foto-1.jpg"] and removed["main"] == "foto-1.jpg"

    store.update(draft_id, status=bozze.STATUS_RUNNING, job_id="job1")
    assert store.reset_stale(set()) == 1 and store.get(draft_id)["status"] == bozze.STATUS_TODO
    assert store.delete(draft_id) is True and store.get(draft_id) is None
    assert any((tmp_path / "cestino").iterdir())


def test_list_puts_todo_first(tmp_path):
    store = bozze.BozzeStore(tmp_path / "bozze")
    ids = []
    for _ in range(3):
        draft_id, folder = store.new_folder()
        (folder / "foto-1.jpg").write_bytes(b"x")
        store.create(folder, "", ["foto-1.jpg"])
        ids.append(draft_id)
    store.update(ids[0], status=bozze.STATUS_DONE, run_id="r1")
    order = [item["id"] for item in store.list()]
    assert order[-1] == ids[0]


def test_api_save_list_photo_and_delete():
    files = [("foto", ("a.jpg", _jpeg(), "image/jpeg")), ("foto", ("b.jpg", _jpeg((10, 90, 160)), "image/jpeg"))]
    created = client.post("/bozze", files=files, data={"nota": "anello ametista 159 euro misura 13"})
    assert created.status_code == 200
    draft = created.json()
    assert len(draft["photos"]) == 2 and draft["facts"]["misura"] == "13"

    listed = client.get("/bozze").json()["items"]
    assert any(item["id"] == draft["id"] for item in listed)

    thumb = client.get(f"/bozze/{draft['id']}/foto/{draft['photos'][0]}?w=300")
    assert thumb.status_code == 200 and thumb.headers["content-type"] == "image/jpeg"
    assert Image.open(io.BytesIO(thumb.content)).width <= 300
    assert client.get(f"/bozze/{draft['id']}/foto/..%2Fbozza.json").status_code == 404

    more = client.post(f"/bozze/{draft['id']}/foto", files=[("foto", ("c.jpg", _jpeg(), "image/jpeg"))]).json()
    assert len(more["photos"]) == 3
    saved = client.put(f"/bozze/{draft['id']}", json={"note": "anello opale 120 euro", "main": more["photos"][2]}).json()
    assert saved["note"].startswith("anello opale") and saved["main"] == more["photos"][2]

    assert client.delete(f"/bozze/{draft['id']}").json() == {"deleted": draft["id"]}
    assert client.get(f"/bozze/{draft['id']}/foto/{draft['photos'][0]}").status_code == 404


def test_download_gives_the_original_bytes_and_a_zip():
    import zipfile

    original = _jpeg((50, 60, 70), size=(3000, 4000))
    draft = client.post("/bozze", files=[("foto", ("a.jpg", original, "image/jpeg"))], data={"nota": ""}).json()
    single = client.get(f"/bozze/{draft['id']}/foto/{draft['photos'][0]}?scarica=1")
    assert single.status_code == 200 and single.content == original
    assert "attachment" in single.headers["content-disposition"]

    archive = client.get(f"/bozze/{draft['id']}/scarica")
    assert archive.status_code == 200 and archive.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(archive.content)) as z:
        assert len(z.namelist()) == 1 and z.read(z.namelist()[0]) == original
    assert client.get("/bozze/inesistente/scarica").status_code == 404
    client.delete(f"/bozze/{draft['id']}")


def test_api_rejects_empty_and_wrong_files():
    assert client.post("/bozze", files=[("foto", ("a.txt", b"ciao", "text/plain"))]).status_code in (400, 415)


def test_make_piece_starts_the_mission_with_the_note(monkeypatch):
    launched = {}

    def fake_launch(job_id, foto_path, brief, image_model, text_model, detail_path=None, variants_path=None, draft_id=""):
        launched.update(job_id=job_id, foto=foto_path, brief=brief, detail=detail_path, draft_id=draft_id)

    monkeypatch.setattr(server, "_launch_job", fake_launch)
    files = [("foto", ("a.jpg", _jpeg(), "image/jpeg")), ("foto", ("b.jpg", _jpeg((10, 90, 160)), "image/jpeg"))]
    draft = client.post("/bozze", files=files, data={"nota": "anello ametista 159 euro"}).json()

    result = client.post(f"/bozze/{draft['id']}/crea", json={})
    assert result.status_code == 200
    assert launched["brief"] == "anello ametista 159 euro" and launched["draft_id"] == draft["id"]
    assert launched["foto"].exists() and launched["detail"].exists()
    # the draft keeps its own photos, and cannot be started twice at once
    assert client.get(f"/bozze/{draft['id']}/foto/{draft['photos'][0]}").status_code == 200
    assert client.post(f"/bozze/{draft['id']}/crea", json={}).status_code == 409

    # a finished mission marks the draft as ready, a failed one puts it back to do
    server.jobs[launched["job_id"]] = {"draft_id": draft["id"], "status": "done", "results": {"run_id": "run-9"}, "logs": []}
    server._sync_draft(launched["job_id"])
    done = server.bozze_store.get(draft["id"])
    assert done["status"] == bozze.STATUS_DONE and done["run_id"] == "run-9"
    server.bozze_store.update(draft["id"], status=bozze.STATUS_RUNNING)
    server.jobs[launched["job_id"]] = {"draft_id": draft["id"], "status": "error", "results": None, "logs": ["ERRORE: chiave"]}
    server._sync_draft(launched["job_id"])
    failed = server.bozze_store.get(draft["id"])
    assert failed["status"] == bozze.STATUS_TODO and "chiave" in failed["error"]
    client.delete(f"/bozze/{draft['id']}")
