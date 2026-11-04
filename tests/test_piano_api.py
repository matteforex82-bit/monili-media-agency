"""Rotte /piano: stato salvato, azioni, collegamento con la creazione del Reel e catalogo del Piano."""
import json
from datetime import date

import pytest
from fastapi.testclient import TestClient

import api.server as server
import piano
from test_piano import make_catalog

client = TestClient(server.app)
REAL_CATALOG = server._piano_catalog  # il fixture sotto sostituisce quella usata dalle rotte
REAL_SITE_LOOKUP = server._piano_site_product
TODAY = date(2026, 11, 4)


@pytest.fixture(autouse=True)
def plan_environment(tmp_path, monkeypatch):
    monkeypatch.setattr(piano, "STATE_PATH", tmp_path / "piano.json")
    monkeypatch.setattr(server, "_piano_today", lambda: TODAY)
    monkeypatch.setattr(server, "_piano_catalog", lambda: make_catalog())
    monkeypatch.setattr(server, "_piano_refiner", lambda: None)
    return tmp_path


def test_get_plan_shows_the_current_week_and_two_previews():
    data = client.get("/piano").json()
    assert [w["provvisoria"] for w in data["settimane"]] == [False, True, True]
    current = data["settimane"][0]
    assert current["inizio"] == "2026-11-02"
    for role in ("scoperta", "acquisto"):
        proposal = current["slot"][role]["proposta"]
        assert proposal["pezzo"]["code"].startswith("M-") and proposal["brief"] and proposal["storie_promemoria"]
    saved = json.loads(piano.STATE_PATH.read_text(encoding="utf-8"))
    assert list(saved["settimane"]) == ["2026-11-02"]
    assert client.get("/piano").json()["settimane"][0] == current  # stabile tra una visita e l'altra


def test_another_idea_skip_and_published_through_the_api():
    first = client.get("/piano").json()["settimane"][0]["slot"]["acquisto"]["proposta"]
    changed = client.post("/piano/2026-11-02/acquisto/altra-idea").json()["settimane"][0]["slot"]["acquisto"]["proposta"]
    assert (changed["skill"]["id"], changed["pezzo"]["run_id"]) != (first["skill"]["id"], first["pezzo"]["run_id"])

    skipped = client.post("/piano/2026-11-02/scoperta/salta", json={"motivo": "Negozio chiuso"}).json()
    assert skipped["settimane"][0]["slot"]["scoperta"]["stato"] == "saltato"
    assert skipped["settimane"][0]["slot"]["scoperta"]["motivo_salto"] == "Negozio chiuso"
    assert client.post("/piano/2026-11-02/scoperta/altra-idea").status_code == 409

    done = client.post("/piano/2026-11-02/acquisto/pubblicato").json()
    assert done["settimane"][0]["slot"]["acquisto"]["stato"] == "pubblicato"
    assert done["settimane"][0]["slot"]["acquisto"]["pubblicato_il"] == "2026-11-04"


def test_invalid_references_and_previews_are_refused():
    client.get("/piano")
    assert client.post("/piano/2026-11-03/acquisto/altra-idea").status_code == 400  # non e' un lunedi'
    assert client.post("/piano/2026-11-02/altro/altra-idea").status_code == 400
    assert client.post("/piano/2026-11-09/acquisto/salta", json={}).status_code == 409  # anteprima


def test_creating_a_reel_from_the_plan_marks_the_content_as_created(monkeypatch):
    client.get("/piano")
    server._piano_link_reel("2026-11-02:acquisto", "reel-demo")
    data = client.get("/piano").json()["settimane"][0]["slot"]["acquisto"]
    assert data["stato"] == "creato" and data["reel_id"] == "reel-demo"
    server._piano_link_reel("riferimento-sbagliato", "reel-x")  # non rompe nulla
    server._piano_link_reel("", "reel-y")


def test_catalog_uses_the_snapshot_when_the_site_does_not_answer(tmp_path, monkeypatch):
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    audit = {
        "run_id": "20261101_100000_abc123",
        "product_id": "anello-ametista-20261101",
        "product_title": "Anello con ametista",
        "sent_at": "2026-11-01T10:00:00",
        "published": True,
        "snapshot": {
            "title": "Anello con ametista", "price": 45, "category": "bijoux",
            "location": "via-cavour-17", "state": "unique", "published_at": "2026-11-01T10:00:00",
        },
    }
    (drafts / "showcase-20261101_100000_abc123.json").write_text(json.dumps(audit), encoding="utf-8")
    (drafts / "showcase-non-inviato.json").write_text(json.dumps(dict(audit, run_id="x", sent_at=None)), encoding="utf-8")
    monkeypatch.setattr(server, "SHOWCASE_DRAFTS_DIR", drafts)
    monkeypatch.setattr(server, "_piano_site_product", lambda product_id: None)
    monkeypatch.setattr(server, "_find_mission_payload", lambda run_id: {"results": {}})
    monkeypatch.setattr(server, "_piece_cover", lambda results: "20261101/foto.jpg")
    monkeypatch.setattr(server, "_resolve_output_relative_path", lambda raw: tmp_path / raw)
    rows = REAL_CATALOG()
    assert len(rows) == 1  # il pezzo non inviato al sito non conta
    row = rows[0]
    assert (row["price"], row["location"], row["published"], row["cover"]) == (45, "via-cavour-17", True, "20261101/foto.jpg")
    assert [p["run_id"] for p in piano.eligible_pieces(rows)] == ["20261101_100000_abc123"]

    # se il sito risponde 404 il pezzo non e' piu' pubblicato; se risponde "venduto" non si propone
    monkeypatch.setattr(server, "_piano_site_product", lambda product_id: {"_missing": True})
    assert piano.eligible_pieces(REAL_CATALOG()) == []
    monkeypatch.setattr(server, "_piano_site_product", lambda product_id: {"publicationStatus": "published", "state": "sold", "price": 45, "availableAt": ["via-cavour-21"]})
    sold = REAL_CATALOG()[0]
    assert sold["location"] == "via-cavour-21" and piano.eligible_pieces([sold]) == []


def test_site_lookup_gives_up_for_a_minute_when_the_site_is_down(monkeypatch):
    calls = []

    def broken(url, timeout):
        calls.append(url)
        raise OSError("sito spento")

    monkeypatch.setattr(server, "_showcase_site_url", lambda: "https://sito.example")
    monkeypatch.setattr(server.requests, "get", broken)
    monkeypatch.setattr(server, "_PIANO_SITE_DOWN_UNTIL", 0.0)
    monkeypatch.setattr(server, "_PIANO_SITE_CACHE", {})
    assert REAL_SITE_LOOKUP("a") is None and REAL_SITE_LOOKUP("b") is None and REAL_SITE_LOOKUP("c") is None
    assert len(calls) == 1  # dopo il primo errore non si insiste con gli altri pezzi


def test_reel_create_accepts_the_plan_reference_and_marks_the_content_created(monkeypatch, product_photo):
    client.get("/piano")
    monkeypatch.setattr(server.reel_studio, "create_reel", lambda reel_id, *args, **kwargs: {"id": reel_id})
    monkeypatch.setattr(server.reel_studio, "plan_reel", lambda *args, **kwargs: None)
    monkeypatch.setattr(server, "_public_reel", lambda state: {"id": state["id"]})
    with open(product_photo, "rb") as handle:
        response = client.post(
            "/reel/create",
            data={"brief": "Brief dal Piano", "recipe": "idea-regalo", "piano": "2026-11-02:scoperta"},
            files={"photos": ("foto.jpg", handle, "image/jpeg")},
        )
    assert response.status_code == 200, response.text
    slot = client.get("/piano").json()["settimane"][0]["slot"]["scoperta"]
    assert slot["stato"] == "creato" and slot["reel_id"] == response.json()["id"]
