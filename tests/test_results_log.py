import pytest

import results_log as rl


@pytest.fixture(autouse=True)
def clean_results():
    rl.RESULTS_FILE.unlink(missing_ok=True)
    yield
    rl.RESULTS_FILE.unlink(missing_ok=True)


def test_upsert_validates_input():
    with pytest.raises(ValueError, match="non numerico"):
        rl.upsert("a", {"metrics": {"views": "tante"}})
    with pytest.raises(ValueError, match="negativi"):
        rl.upsert("a", {"metrics": {"views": -3}})
    with pytest.raises(ValueError, match="Data"):
        rl.upsert("a", {"published_on": "31/10/2026"})
    with pytest.raises(ValueError, match="Ora"):
        rl.upsert("a", {"hour": 25})


def test_upsert_merges_metrics_and_accepts_commas():
    rl.upsert("r1", {"title": "Blu", "metrics": {"views": "1.200,5".replace(".", ""), "sends": 4}})
    entry = rl.upsert("r1", {"metrics": {"dms": 2}})
    assert entry["metrics"] == {"views": 1200.5, "sends": 4.0, "dms": 2.0}
    assert entry["title"] == "Blu"


def test_hints_need_enough_data():
    rl.upsert("r1", {"skill": "mani-bancone", "published_on": "2026-11-03", "hour": 19, "metrics": {"views": 900, "sends": 18}})
    assert rl.prompt_hints() == ""  # un solo contenuto: nessuna regola
    rl.upsert("r2", {"skill": "mani-bancone", "published_on": "2026-11-10", "hour": 19, "metrics": {"views": 700, "sends": 7}})
    rl.upsert("r3", {"skill": "tre-modi", "published_on": "2026-11-05", "hour": 12, "metrics": {"views": 300, "sends": 1}})
    rl.upsert("r4", {"skill": "tre-modi", "published_on": "2026-11-12", "hour": 12, "metrics": {"views": 200, "sends": 0}})
    summary = rl.summary()
    top = summary["by_skill"][0]
    assert top["key"] == "mani-bancone" and top["avg_views"] == 800 and top["reliable"]
    assert summary["by_weekday"][0]["key"] == "martedi"
    hints = rl.prompt_hints()
    assert "/mani-bancone" in hints and "/tre-modi" in hints and "18-21" in hints


def test_delete():
    rl.upsert("r1", {"metrics": {"views": 1}})
    assert rl.delete("r1") is True
    assert rl.delete("r1") is False
