"""
skills_loader.py - carica le skill dei contenuti da file Markdown modificabili.

- skills/<id>.md            skill di base (nel repo)
- skills/_base/<nome>.md    modelli comuni (fotogramma, movimento, copertina, testi)
- <storage>/skills/...      modifiche fatte dall'app: hanno la precedenza sui file del repo

Formato: frontmatter "chiave: valore" tra righe '---', poi sezioni '## Titolo'.
"""

import re
from collections import defaultdict
from pathlib import Path

from main import STORAGE_ROOT

REPO_SKILLS_DIR = Path(__file__).parent / "skills"
# Le modifiche dall'app non devono mai sovrascrivere i file del repo (succederebbe se lo storage
# coincide con la cartella del progetto, es. su Render): in quel caso usano skills_custom/.
_override = STORAGE_ROOT / "skills"
OVERRIDE_SKILLS_DIR = (
    STORAGE_ROOT / "skills_custom" if _override.resolve() == REPO_SKILLS_DIR.resolve() else _override
)
BASE_NAMES = ("fotogramma", "movimento", "copertina", "testi")
DEFAULT_SKILL = "libera"
SECTION_KEYS = {
    "struttura": "structure",
    "fotogramma": "keyframe",
    "movimento": "motion",
    "testi": "copy",
    "copertina": "cover",
}
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")


class SkillError(ValueError):
    pass


def normalize_id(skill_id: str) -> str:
    return (skill_id or "").strip().lower().lstrip("/").replace("_", "-")


def parse_skill(text: str) -> dict:
    """Restituisce {meta: {...}, sections: {...}, body: str}. Solleva SkillError se il formato non va."""
    text = (text or "").replace("\r\n", "\n")
    meta: dict = {}
    body = text
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) < 2:
            raise SkillError("Intestazione aperta con '---' ma non chiusa.")
        header = parts[0][3:]
        body = parts[1].lstrip("-").lstrip("\n")
        for line in header.splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if ":" not in line:
                raise SkillError(f"Riga dell'intestazione non valida: '{line}' (serve 'chiave: valore').")
            key, value = line.split(":", 1)
            meta[key.strip().lower()] = value.strip()
    sections: dict[str, str] = {}
    current = None
    buffer: list[str] = []
    for line in body.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            if current:
                sections[current] = "\n".join(buffer).strip()
            title = heading.group(1).strip().lower()
            current = SECTION_KEYS.get(title, title)
            buffer = []
        elif current:
            buffer.append(line)
    if current:
        sections[current] = "\n".join(buffer).strip()
    return {"meta": meta, "sections": sections, "body": body.strip()}


def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in ("true", "si", "sì", "yes", "1")


def _read(skill_id: str, base: bool = False) -> tuple[str, str] | None:
    """Testo della skill e sorgente ('modificata' | 'originale')."""
    rel = Path("_base") / f"{skill_id}.md" if base else Path(f"{skill_id}.md")
    override = OVERRIDE_SKILLS_DIR / rel
    if override.exists():
        return override.read_text(encoding="utf-8"), "modificata"
    original = REPO_SKILLS_DIR / rel
    if original.exists():
        return original.read_text(encoding="utf-8"), "originale"
    return None


def _skill_ids() -> list[str]:
    ids = set()
    for folder in (REPO_SKILLS_DIR, OVERRIDE_SKILLS_DIR):
        if folder.exists():
            ids.update(p.stem for p in folder.glob("*.md") if p.stem.lower() != "readme")
    ordered = sorted(ids - {DEFAULT_SKILL})
    return ([DEFAULT_SKILL] if DEFAULT_SKILL in ids else []) + ordered


def load_skill(skill_id: str) -> dict | None:
    skill_id = normalize_id(skill_id)
    found = _read(skill_id)
    if not found:
        return None
    text, source = found
    try:
        parsed = parse_skill(text)
    except SkillError:
        return None
    meta = parsed["meta"]
    formats = [f.strip() for f in meta.get("formats", "reel, story").split(",") if f.strip() in ("reel", "story")]
    try:
        default_seconds = int(meta.get("default_seconds") or 0)
    except ValueError:
        default_seconds = 0
    return {
        "id": skill_id,
        "label": meta.get("label") or skill_id,
        "description": meta.get("description", ""),
        "formats": formats or ["reel", "story"],
        "uses_model": _to_bool(meta.get("uses_model", "false")),
        "default_seconds": default_seconds,
        "sections": parsed["sections"],
        "source": source,
        "has_original": (REPO_SKILLS_DIR / f"{skill_id}.md").exists(),
    }


def list_skills() -> list[dict]:
    return [skill for skill in (load_skill(i) for i in _skill_ids()) if skill]


def select_skill(requested: str = "") -> str:
    skill_id = normalize_id(requested)
    return skill_id if load_skill(skill_id) else DEFAULT_SKILL


def section(skill_id: str, key: str) -> str:
    skill = load_skill(skill_id)
    return (skill or {}).get("sections", {}).get(key, "") if skill else ""


def base_template(name: str) -> str:
    found = _read(name, base=True)
    if not found:
        return ""
    try:
        return parse_skill(found[0])["body"]
    except SkillError:
        return ""


def fill(template: str, **values) -> str:
    """Riempie i segnaposto {nome}; quelli sconosciuti restano vuoti, le righe vuote doppie si compattano."""
    safe = defaultdict(str, {k: (v or "") for k, v in values.items()})
    try:
        text = template.format_map(safe)
    except (ValueError, IndexError):
        text = template
    return re.sub(r"\n{3,}", "\n\n", "\n".join(line.rstrip() for line in text.splitlines())).strip()


# ── EDITOR ───────────────────────────────────────────────────────────────────

def raw_text(skill_id: str, base: bool = False) -> dict | None:
    skill_id = normalize_id(skill_id)
    found = _read(skill_id, base=base)
    if not found:
        return None
    original = REPO_SKILLS_DIR / ("_base" if base else "") / f"{skill_id}.md"
    return {"id": skill_id, "base": base, "text": found[0], "source": found[1], "has_original": original.exists()}


def save_text(skill_id: str, text: str, base: bool = False) -> dict:
    skill_id = normalize_id(skill_id)
    if base and skill_id not in BASE_NAMES:
        raise SkillError("Modello base sconosciuto.")
    if not base and not _ID_RE.match(skill_id):
        raise SkillError("Nome skill non valido: usa lettere minuscole, numeri e trattini (es. 'saldi-inverno').")
    parsed = parse_skill(text)
    if not base and not parsed["sections"].get("structure"):
        raise SkillError("Manca la sezione '## Struttura'.")
    if len(text) > 20000:
        raise SkillError("Testo troppo lungo (max 20.000 caratteri).")
    target = OVERRIDE_SKILLS_DIR / ("_base" if base else "") / f"{skill_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.replace("\r\n", "\n"), encoding="utf-8")
    return raw_text(skill_id, base=base)


def reset(skill_id: str, base: bool = False) -> dict | None:
    """Elimina la modifica fatta dall'app e torna all'originale del repo (se esiste)."""
    skill_id = normalize_id(skill_id)
    target = OVERRIDE_SKILLS_DIR / ("_base" if base else "") / f"{skill_id}.md"
    target.unlink(missing_ok=True)
    return raw_text(skill_id, base=base)
