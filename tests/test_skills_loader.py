import pytest

import skills_loader as sk


def test_repo_skills_are_valid():
    skills = sk.list_skills()
    ids = [s["id"] for s in skills]
    assert ids[0] == "libera"
    for expected in ("modella-monili", "mani-bancone", "idea-regalo", "countdown-natale"):
        assert expected in ids
    for skill in skills:
        assert skill["sections"].get("structure"), f"{skill['id']} senza ## Struttura"
        assert set(skill["formats"]) <= {"reel", "story"}


def test_base_templates_have_placeholders():
    assert "{scene}" in sk.base_template("fotogramma")
    assert "{camera}" in sk.base_template("movimento")
    assert "{cover_text}" in sk.base_template("copertina")
    assert sk.base_template("testi")


def test_select_skill_normalizes_ids():
    assert sk.select_skill("modella_monili") == "modella-monili"
    assert sk.select_skill("/Tre-Modi") == "tre-modi"
    assert sk.select_skill("non-esiste") == "libera"


def test_fill_leaves_unknown_placeholders_empty():
    assert sk.fill("A {scene} B {missing}", scene="x") == "A x B"
    assert sk.fill("graffe {non chiuse", scene="x") == "graffe {non chiuse"


@pytest.mark.parametrize(
    "text, message",
    [
        ("---\nlabel x\n---\n## Struttura\n1.", "chiave: valore"),
        ("---\nlabel: x\n---\n## Testi\nciao", "Struttura"),
        ("---\nlabel: x\n## Struttura\n1.", "non chiusa"),
    ],
)
def test_save_rejects_invalid_text(text, message):
    with pytest.raises(sk.SkillError, match=message):
        sk.save_text("prova-errori", text)


def test_save_and_reset_never_touch_repo_files():
    original = (sk.REPO_SKILLS_DIR / "mani-bancone.md").read_text(encoding="utf-8")
    edited = original.replace("Mani al bancone", "Mani al bancone v2")
    saved = sk.save_text("mani-bancone", edited)
    assert saved["source"] == "modificata"
    assert sk.load_skill("mani-bancone")["label"] == "Mani al bancone v2"
    assert (sk.REPO_SKILLS_DIR / "mani-bancone.md").read_text(encoding="utf-8") == original
    reset = sk.reset("mani-bancone")
    assert reset["source"] == "originale"
    assert (sk.REPO_SKILLS_DIR / "mani-bancone.md").exists()


def test_new_skill_and_bad_id():
    sk.save_text("saldi-inverno", "---\nlabel: Saldi inverno\nformats: story\n---\n## Struttura\n1. HOOK")
    assert "saldi-inverno" in [s["id"] for s in sk.list_skills()]
    sk.reset("saldi-inverno")
    with pytest.raises(sk.SkillError):
        sk.save_text("Nome Brutto!", "---\nlabel: x\n---\n## Struttura\n1.")
