from fastapi.testclient import TestClient

import api.server as server
import results_log as rl

client = TestClient(server.app)


def test_config_lists_skills_and_engines():
    cfg = client.get("/reel/config").json()
    ids = [r["id"] for r in cfg["recipes"]]
    assert ids[0] == "libera" and "idea-regalo" in ids
    assert cfg["openai_direct_configured"] is False
    assert not any(m.startswith("openai-direct/") for m in cfg["keyframe_models"])


def test_results_endpoints():
    rl.RESULTS_FILE.unlink(missing_ok=True)
    bad = client.put("/results/manuale-1", json={"metrics": {"views": "tante"}})
    assert bad.status_code == 400
    ok = client.put("/results/manuale-1", json={"title": "Post fuori app", "skill": "tre-modi", "metrics": {"views": 450}})
    assert ok.status_code == 200 and ok.json()["metrics"]["views"] == 450
    data = client.get("/results").json()
    assert data["summary"]["with_numbers"] == 1 and data["items"][0]["title"] == "Post fuori app"
    assert client.delete("/results/manuale-1").json() == {"deleted": True}


def test_skills_endpoints_roundtrip():
    original = client.get("/skills/libera").json()
    assert original["source"] == "originale"
    bad = client.put("/skills/libera", json={"text": "---\nlabel: x\n---\nniente"})
    assert bad.status_code == 400
    saved = client.put("/skills/libera", json={"text": original["text"] + "\nNota in piu."}).json()
    assert saved["source"] == "modificata"
    assert client.delete("/skills/libera").json()["source"] == "originale"
    base = client.get("/skills/fotogramma?base=true").json()
    assert "{scene}" in base["text"]


ANALISI_ANELLO = """# Scheda Prodotto

```markdown
## IDENTIFICAZIONE
- Categoria esatta: Anello da donna fashion, pietra centrale cabochon.
- Materiali identificati con certezza: metallo argentato (probabilmente argento o lega simil-argento), pietra cabochon viola.

## DESCRIZIONE AI
Anello in metallo argentato con pietra cabochon viola
circondata da zirconi bianchi e neri.
```
"""


def test_showcase_summary_uses_site_description():
    assert server._markdown_section(ANALISI_ANELLO, "DESCRIZIONE AI") == (
        "Anello in metallo argentato con pietra cabochon viola circondata da zirconi bianchi e neri."
    )
    assert server._markdown_section(ANALISI_ANELLO, "ASSENTE") == ""


def test_showcase_materials_skip_guesses():
    assert server._extract_materials(ANALISI_ANELLO) == ["metallo argentato"]
    assert server._extract_materials("- Materiali identificati: argento 925, pietra dura\n- Altro") == [
        "argento 925",
        "argento",
        "pietra dura",
    ]


def test_results_take_skill_from_reel(product_photo):
    import reel_studio as rs

    reel_id = rs.new_reel_id()
    (rs.reel_dir(reel_id) / "input").mkdir(parents=True)
    photo = rs.reel_dir(reel_id) / "input" / "p.jpg"
    photo.write_bytes(product_photo.read_bytes())
    rs.create_reel(reel_id, [photo], [], "", "story", 7, "", "", "", recipe="countdown-natale")
    entry = client.put(f"/results/{reel_id}", json={"skill": "", "title": "", "metrics": {"views": 10}}).json()
    assert entry["skill"] == "countdown-natale" and entry["format"] == "story"
    client.delete(f"/results/{reel_id}")
