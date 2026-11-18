"""
prompt_lab.py - Laboratorio dei prompt: lo Studio analizza il pezzo e mostra i prompt; le foto si creano a mano su
Higgsfield, poi si carica il risultato e si dà un voto. I prompt buoni diventano esempi per le analisi successive,
quelli brutti restano con la nota, per capire cosa correggere.

Per ogni bozza: <bozza>/lab.json e <bozza>/prove/ (i risultati caricati).
Libreria comune: <storage>/memory/prompt_lab.json
"""
from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime
from pathlib import Path

from main import MEMORY_ROOT

LAB_NAME = "lab.json"
RESULTS_DIR = "prove"
LIBRARY_FILE = MEMORY_ROOT / "prompt_lab.json"
SHOTS = ("clean", "worn", "worn_2")
MODELS = ("Seedream", "Nano Banana", "GPT Image", "Altro")
VIDEO_MODEL = "Seedance 2.5"
SCENES = ("scena_1", "scena_2", "scena_3")
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
AUTO_MODELS = ("Nano Banana", "GPT Image")  # i modelli del flusso automatico dello Studio
KNOWLEDGE_DIR = Path(__file__).parent / "knowledge" / "fucina"
MODEL_FILES = {"Seedream": "seedream.md", "Nano Banana": "nano-banana.md", "GPT Image": "nano-banana.md", "Seedance 2.5": "seedance.md"}
SHOT_LABELS = {"clean": "Foto catalogo", "worn": "Foto indossata", "worn_2": "Seconda indossata"}
CATEGORIES = ("bijoux", "abbigliamento", "accessori")
GOOD_FROM = 4  # voto da cui un prompt è «buono»
BAD_UNTIL = 2  # voto fino a cui è «da non ripetere»
HINTS_PER_KIND = 3
MAX_TEXT = 4000

_lock = threading.Lock()


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _clean(value: object, limit: int = MAX_TEXT) -> str:
    return str(value or "").strip()[:limit]


# -- libreria comune -------------------------------------------------------------------------------------------
def _load_library() -> dict:
    try:
        data = json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return data
    except Exception:
        pass
    return {"items": []}


def _save_library(data: dict) -> None:
    LIBRARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = LIBRARY_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(LIBRARY_FILE)


def record(attempt: dict, category: str, draft_id: str) -> None:
    """Keeps (or drops) the rated attempt in the shared library. A new rating of the same attempt replaces the old."""
    with _lock:
        data = _load_library()
        data["items"] = [item for item in data["items"] if item.get("attempt_id") != attempt["id"]]
        rating = attempt.get("rating")
        if isinstance(rating, int) and rating > 0:
            data["items"].append(
                {
                    "attempt_id": attempt["id"],
                    "draft_id": draft_id,
                    "category": category,
                    "shot": attempt.get("shot", ""),
                    "model": attempt.get("model", ""),
                    "prompt": attempt.get("prompt", ""),
                    "rating": rating,
                    "note": attempt.get("note", ""),
                    "rated_at": _now(),
                }
            )
        _save_library(data)


def library_items() -> list[dict]:
    with _lock:
        return _load_library()["items"]


def model_knowledge(model: str = "", category: str = "") -> str:
    """The vertical knowledge for the chosen image model and the kind of piece (knowledge/fucina/*.md)."""
    parts: list[str] = []
    for name in (MODEL_FILES.get(model, ""), f"ricetta-{category}.md" if category else ""):
        if not name:
            continue
        try:
            text = (KNOWLEDGE_DIR / name).read_text(encoding="utf-8").strip()
        except OSError:
            continue
        parts.append(text)
    return "\n\n".join(parts)


def hints(category: str = "", model: str = "") -> str:
    """Examples to put in front of the art director: what worked and what went wrong, from the owner's own ratings.
    Only the ones made for the same image model (the automatic flow sees the models it really uses)."""
    items = library_items()
    wanted = (model,) if model else AUTO_MODELS
    items = [i for i in items if i.get("model") in wanted]
    if not items:
        return ""
    same = [i for i in items if i.get("category") == category] or items

    def recent(selected: list[dict]) -> list[dict]:
        return sorted(selected, key=lambda i: i.get("rated_at", ""), reverse=True)[:HINTS_PER_KIND]

    good = recent([i for i in same if i.get("rating", 0) >= GOOD_FROM])
    bad = recent([i for i in same if i.get("rating", 0) <= BAD_UNTIL and i.get("note")])
    lines: list[str] = []
    if good:
        lines.append("PROMPT CHE HANNO DATO UN BUON RISULTATO (voti di Matteo), ispirati al loro modo di scrivere:")
        lines += [f'- ({i["rating"]}/5, {i.get("shot", "")}) {_clean(i["prompt"], 500)}' for i in good]
    if bad:
        lines.append("ERRORI GIA VISTI (voti bassi di Matteo): non ripeterli.")
        lines += [f'- ({i["rating"]}/5) {_clean(i["note"], 240)}' for i in bad]
    return "\n".join(lines)


def library_summary() -> dict:
    items = library_items()
    return {
        "total": len(items),
        "good": sum(1 for i in items if i.get("rating", 0) >= GOOD_FROM),
        "bad": sum(1 for i in items if i.get("rating", 0) <= BAD_UNTIL),
    }


# -- laboratorio di una bozza ------------------------------------------------------------------------------------
class LabStore:
    """Works on the folder of a draft (the BozzeStore gives the folder)."""

    def read(self, folder: Path) -> dict | None:
        try:
            return json.loads((folder / LAB_NAME).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def _write(self, folder: Path, lab: dict) -> None:
        tmp = folder / (LAB_NAME + ".tmp")
        tmp.write_text(json.dumps(lab, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(folder / LAB_NAME)

    def save_analysis(
        self, folder: Path, category: str, analisi: str, plan: dict, final_prompts: dict[str, str], target_model: str = ""
    ) -> dict:
        """A new analysis replaces the prompts but keeps the attempts already made."""
        with _lock:
            old = self.read(folder) or {}
            lab = {
                "category": category,
                "target_model": target_model,
                "analisi": analisi,
                "styling": plan.get("styling", ""),
                "woman": plan.get("woman", ""),
                "prompts": {key: {"text": text, "edited": False} for key, text in final_prompts.items()},
                "attempts": old.get("attempts", []),
                "created_at": _now(),
            }
            self._write(folder, lab)
            return lab

    def edit_prompt(self, folder: Path, shot: str, text: str) -> dict | None:
        with _lock:
            lab = self.read(folder)
            if not lab:
                return None
            group = "scenes" if shot in lab.get("scenes", {}) else "prompts"
            if shot not in lab.get(group, {}):
                return None
            lab[group][shot] = {"text": _clean(text), "edited": True}
            self._write(folder, lab)
            return lab

    def save_scenes(self, folder: Path, source_attempt: str, scenes: dict[str, str], idea: str) -> dict | None:
        """The video scenes for the clothing worn by the woman: they start from one chosen photo (an attempt)."""
        with _lock:
            lab = self.read(folder)
            if not lab:
                return None
            lab["scenes"] = {key: {"text": text, "edited": False} for key, text in scenes.items()}
            lab["scenes_source"] = source_attempt
            lab["scenes_idea"] = idea
            # the scenes of a previous round stay in the attempts, so nothing already made is lost
            self._write(folder, lab)
            return lab

    def add_attempt(self, folder: Path, shot: str, model: str) -> dict | None:
        """«Fatta su Higgsfield»: freezes the prompt as it is now, with the model used."""
        with _lock:
            lab = self.read(folder)
            if not lab or shot not in {**lab.get("prompts", {}), **lab.get("scenes", {})}:
                return None
            text = (lab.get("prompts", {}).get(shot) or lab["scenes"][shot])["text"]
            is_scene = shot in lab.get("scenes", {})
            lab["attempts"].append(
                {
                    "id": uuid.uuid4().hex[:8],
                    "shot": shot,
                    "model": _clean(model, 60) or (VIDEO_MODEL if is_scene else lab.get("target_model")) or "Higgsfield",
                    "prompt": text,
                    "created_at": _now(),
                    "result": "",
                    "rating": 0,
                    "note": "",
                }
            )
            self._write(folder, lab)
            return lab

    def _attempt(self, lab: dict, attempt_id: str) -> dict | None:
        return next((a for a in lab.get("attempts", []) if a.get("id") == attempt_id), None)

    def get_attempt(self, folder: Path, attempt_id: str) -> dict | None:
        lab = self.read(folder)
        return self._attempt(lab, attempt_id) if lab else None

    def set_result(self, folder: Path, attempt_id: str, filename: str) -> dict | None:
        with _lock:
            lab = self.read(folder)
            attempt = self._attempt(lab, attempt_id) if lab else None
            if not attempt:
                return None
            old = attempt.get("result")
            attempt["result"] = filename
            self._write(folder, lab)
        if old and old != filename:
            (folder / RESULTS_DIR / old).unlink(missing_ok=True)
        return lab

    def set_critique(self, folder: Path, attempt_id: str, critique: dict) -> dict | None:
        with _lock:
            lab = self.read(folder)
            attempt = self._attempt(lab, attempt_id) if lab else None
            if not attempt:
                return None
            attempt["critique"] = critique
            self._write(folder, lab)
            return lab

    def rate(self, folder: Path, attempt_id: str, rating: int, note: str, draft_id: str) -> dict | None:
        with _lock:
            lab = self.read(folder)
            attempt = self._attempt(lab, attempt_id) if lab else None
            if not attempt:
                return None
            attempt["rating"] = max(0, min(int(rating or 0), 5))
            attempt["note"] = _clean(note, 600)
            attempt["rated_at"] = _now()
            self._write(folder, lab)
            snapshot = dict(attempt)
            category = lab.get("category", "bijoux")
        record(snapshot, category, draft_id)
        return lab

    def delete_attempt(self, folder: Path, attempt_id: str) -> dict | None:
        with _lock:
            lab = self.read(folder)
            attempt = self._attempt(lab, attempt_id) if lab else None
            if not attempt:
                return None
            lab["attempts"] = [a for a in lab["attempts"] if a.get("id") != attempt_id]
            self._write(folder, lab)
        if attempt.get("result"):
            (folder / RESULTS_DIR / attempt["result"]).unlink(missing_ok=True)
        record({"id": attempt_id}, "", "")  # tolto anche dalla libreria
        return lab


store = LabStore()


# -- giudizio di Codex sul risultato ----------------------------------------------------------------------------
CHECKLIST = (
    ("pietre_numero", "Numero delle pietre"),
    ("pietre_colore", "Colore e taglio delle pietre"),
    ("metallo", "Metallo e finitura"),
    ("forma", "Forma e proporzioni del pezzo"),
    ("mani_corpo", "Mani, dita e corpo naturali"),
    ("inquadratura", "Inquadratura, luce e sfondo"),
    ("extra", "Niente di aggiunto (testo, loghi, altri gioielli)"),
)


def critique_prompt(lab: dict, attempt: dict, is_video: bool = False) -> str:
    checks = "\n".join(f'- "{key}": {label}' for key, label in CHECKLIST)
    knowledge = model_knowledge(attempt.get("model", ""), lab.get("category", ""))
    return f"""Sei il revisore di immagini di I Monili Ravenna, una gioielleria di Ravenna.
{"Hai quattro immagini: la PRIMA è la foto vera del pezzo (la verità), le altre tre sono fotogrammi (inizio, metà, fine) di un video creato con l'AI (" + attempt.get("model", "") + "). Oltre al pezzo controlla che tra un fotogramma e l'altro il capo, la donna e i colori restino uguali, e che non ci siano deformazioni o sfarfallii." if is_video else "Hai due immagini: la PRIMA è la foto vera del pezzo (la verità), la SECONDA è la foto creata con l'AI (" + attempt.get("model", "") + ").\nConfrontale con occhio critico: il pezzo nella seconda deve essere identico a quello della prima."}

PROMPT USATO:
{attempt.get("prompt", "")}

CONOSCENZA SUL MODELLO (può aiutarti a capire cosa correggere nel prompt):
{knowledge or "nessuna"}

Per ogni punto dì "ok", "dubbio" o "problema" e spiega in una frase cosa vedi, citando numeri e colori:
{checks}

Rispondi SOLO con un JSON valido:
{{
  "checklist": {{"pietre_numero": {{"esito": "ok", "nota": "..."}}, ...tutti i punti sopra}},
  "giudizio": "2-3 frasi in italiano: com'è venuta e perché",
  "voto_proposto": 1-5,
  "correzione": "cosa cambiare nel prompt, in italiano, in una o due frasi",
  "prompt_corretto": "il prompt completo, in inglese, già corretto"
}}
Non essere indulgente: se una pietra cambia colore o numero, il voto è 2 o meno. Non scrivere altro fuori dal JSON."""


def normalize_critique(parsed: dict, model: str) -> dict:
    checklist = {}
    raw = parsed.get("checklist") if isinstance(parsed.get("checklist"), dict) else {}
    for key, label in CHECKLIST:
        item = raw.get(key) if isinstance(raw.get(key), dict) else {}
        esito = str(item.get("esito", "dubbio")).lower()
        checklist[key] = {
            "label": label,
            "esito": esito if esito in ("ok", "dubbio", "problema") else "dubbio",
            "nota": _clean(item.get("nota", ""), 300),
        }
    try:
        score = max(1, min(5, int(parsed.get("voto_proposto", 0))))
    except (TypeError, ValueError):
        score = 0
    return {
        "checklist": checklist,
        "giudizio": _clean(parsed.get("giudizio", ""), 800),
        "voto_proposto": score,
        "correzione": _clean(parsed.get("correzione", ""), 600),
        "prompt_corretto": _clean(parsed.get("prompt_corretto", "")),
        "codex_model": model,
        "created_at": _now(),
    }


# -- scene video (Seedance 2.5) per l'abbigliamento -----------------------------------------------------------------
SCENE_TAIL = (
    "PRESERVE: the garment keeps its exact shape, colours, embroidery, buttons and length in every frame; the woman keeps "
    "the same face, hair and build. One continuous shot, no cuts, no new objects. No text, no logos, no watermark."
)


def scenes_prompt(lab: dict, category_note: str, hints_text: str) -> str:
    knowledge = model_knowledge(VIDEO_MODEL, lab.get("category", ""))
    return f"""Sei il regista dei video Instagram di I Monili Ravenna, boutique di Ravenna. Devi restituire SOLO un JSON valido.
Hai in mano la foto del capo già indossato dalla donna di questo pezzo: sarà il PRIMO FOTOGRAMMA di ogni scena (Seedance 2.5, da immagine a video).

Analisi del capo: {str(lab.get("analisi", ""))[:1200]}
La donna: {lab.get("woman", "")}
Appunti del titolare: {category_note or "nessuno"}

{knowledge}
{hints_text}

Scrivi 3 scene diverse, da 4-5 secondi l'una, che si montano in un Reel 9:16. Ogni scena:
- prompt in inglese, in questo ordine: cosa NON cambia (capo, donna), una sola azione semplice, un solo movimento di camera lento, luce;
- azioni facili e naturali (camminare piano, girarsi, sistemarsi il capo, il vento sul tessuto): niente mani che maneggiano oggetti piccoli;
- la scena 1 mostra il capo intero, la 2 un dettaglio (tessuto, ricamo, bottoni), la 3 il movimento (si gira o cammina).

JSON esatto:
{{
  "idea": "una frase in italiano: il filo del video",
  "scene": {{"scena_1": "...", "scena_2": "...", "scena_3": "..."}}
}}"""
