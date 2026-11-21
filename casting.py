"""
casting.py - chi indossa il pezzo, cosa non deve comparire mai, e cosa abbiamo già usato.

Scelta di Matteo (30/10/2026): l'AI resta libera di inventare donne, luoghi e pose adatti al pezzo e allo
stile del negozio. Le regole fisse sono solo due:
- una donna per pezzo: la inventa la Scheda pezzo, i Reel di quel pezzo usano lei; il pezzo dopo ne ha un'altra;
- l'elenco "Mai nei contenuti" (skills/_base/divieti.md).
Per non diventare monotoni, ai prompt passano le donne e le scene usate di recente, da non ripetere.
Le regole si cambiano in skills/_base/donne.md e divieti.md, anche dalla pagina Skill, non qui.
"""

import json
from pathlib import Path

import skills_loader as skills
from main import OUTPUT_ROOT, STORAGE_ROOT

DEFAULT_GUIDE = (
    "Invent a real woman who suits this piece, elegant in a natural everyday way, not a fashion model: "
    "real skin texture, light makeup, relaxed genuine expression."
)
_PLAIN_FALLBACK = "a real elegant woman from around Ravenna, not a fashion model, natural skin and light makeup"


def _sections(name: str) -> dict:
    return skills.parse_skill(skills.base_template(name))["sections"]


def testimonial() -> str:
    """The shop's fixed testimonial (Aurora), same face in every content; empty if the section is removed (then the AI invents)."""
    return " ".join(_sections("donne").get("testimonial", "").split())


TESTIMONIAL_PHOTOS_DIR = STORAGE_ROOT / "aurora-riferimenti"
MAX_TESTIMONIAL_PHOTOS = 2  # la ricerca: da 2 a 4 riferimenti in tutto, compreso il pezzo


def testimonial_photos() -> list[Path]:
    """The testimonial's master photos (neutral face, no jewellery), chosen by Matteo and copied into
    <storage>/aurora-riferimenti. They go to the image model before the product so the face stays the same.
    Empty folder: only the written description is used, as before."""
    try:
        files = sorted(p for p in TESTIMONIAL_PHOTOS_DIR.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))
    except OSError:
        return []
    return files[:MAX_TESTIMONIAL_PHOTOS]


def fallback_woman() -> str:
    """When the AI gave no valid woman: the testimonial, otherwise a real person, not a model."""
    return testimonial() or _PLAIN_FALLBACK


def woman_guide() -> str:
    return " ".join(_sections("donne").get("linee guida", "").split()) or DEFAULT_GUIDE


def never_show() -> list[str]:
    text = _sections("divieti").get("mai", "")
    return [line.strip()[1:].strip() for line in text.splitlines() if line.strip()[:1] in ("-", "*")]


def never_line() -> str:
    """Una riga per i prompt; vuota se non ci sono divieti."""
    items = never_show()
    return f"NEVER SHOW: {'; '.join(items)}." if items else ""


def _recent_files(limit: int) -> list[dict]:
    files = list(OUTPUT_ROOT.glob("*/run_manifest.json")) + list((OUTPUT_ROOT / "reels").glob("*/reel.json"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for path in files[: limit * 3]:
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def _unique(values, limit: int) -> list[str]:
    seen: list[str] = []
    for value in values:
        value = " ".join(str(value or "").split())
        if value and value not in seen:
            seen.append(value[:300])
    return seen[:limit]


def recent_women(limit: int = 6) -> list[str]:
    """Le donne degli ultimi pezzi (Schede e Reel), dalla più recente."""
    data = _recent_files(limit)
    return _unique(((d.get("results") or {}).get("woman") or d.get("woman") for d in data), limit)


def recent_scenes(limit: int = 6, exclude_reel: str = "") -> list[str]:
    """Le scene degli ultimi Reel, dalla più recente."""
    data = [d for d in _recent_files(limit) if d.get("id") != exclude_reel]
    return _unique(((d.get("storyboard") or {}).get("scene_bible") for d in data), limit)


def avoid_block(title: str, items: list[str]) -> str:
    if not items:
        return ""
    return f"{title} (inventa qualcosa di diverso, non ripeterle):\n" + "\n".join(f"- {item}" for item in items)