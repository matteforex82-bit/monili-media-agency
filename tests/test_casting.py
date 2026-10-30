"""Libertà all'AI su donne, luoghi e pose: fissi solo i divieti e "una donna per pezzo"."""
import json

import casting
import skills_loader as sk

DIVIETI = """Istruzioni: questa riga non finisce nel prompt.

## Mai
- scritte neon
- glitter
"""


def test_never_show_reads_only_the_list(monkeypatch):
    monkeypatch.setattr(sk, "base_template", lambda name: DIVIETI if name == "divieti" else "")
    assert casting.never_show() == ["scritte neon", "glitter"]
    assert casting.never_line() == "NEVER SHOW: scritte neon; glitter."
    assert casting.woman_guide() == casting.DEFAULT_GUIDE


def test_repo_rules_exist():
    assert casting.never_show()
    assert "not a fashion model" in casting.woman_guide()


def test_no_rules_no_never_line(monkeypatch):
    monkeypatch.setattr(sk, "base_template", lambda name: "")
    assert casting.never_line() == ""


def test_recent_women_and_scenes_come_from_schede_and_reels(storage_root):
    scheda = casting.OUTPUT_ROOT / "run_casting_test"
    scheda.mkdir(parents=True, exist_ok=True)
    (scheda / "run_manifest.json").write_text(json.dumps({"results": {"woman": "Donna A"}}), encoding="utf-8")
    reel = casting.OUTPUT_ROOT / "reels" / "reel_casting_test"
    reel.mkdir(parents=True, exist_ok=True)
    (reel / "reel.json").write_text(
        json.dumps({"id": "reel_casting_test", "woman": "Donna B", "storyboard": {"scene_bible": "Darsena al tramonto"}}),
        encoding="utf-8",
    )
    assert {"Donna A", "Donna B"} <= set(casting.recent_women(limit=50))
    assert "Darsena al tramonto" in casting.recent_scenes(limit=50)
    assert "Darsena al tramonto" not in casting.recent_scenes(limit=50, exclude_reel="reel_casting_test")
    assert "non ripeterle" in casting.avoid_block("SCENE", ["x"]) and casting.avoid_block("SCENE", []) == ""
