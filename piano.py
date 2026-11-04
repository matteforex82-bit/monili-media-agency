"""Piano editoriale dello Studio: ogni settimana due proposte di contenuto (docs/piano-editoriale-studio.md).

Le proposte nascono da regole fisse e verificabili (test in tests/test_piano.py); l'AI al massimo rifinisce il
brief, e solo se il risultato passa gli stessi controlli. Il calendario degli eventi e' un file dati modificabile:
skills/_base/calendario-eventi.json.

Regole (le stesse del perimetro):
- 2 proposte a settimana: "scoperta" (chi non ci conosce) e "acquisto" (chi vuole comprare);
- mai la stessa skill della settimana prima (ne' della dopo) ne' due volte nella stessa settimana;
- mai lo stesso pezzo entro 3 settimane; due pezzi diversi nella stessa settimana;
- solo pezzi pubblicati sul sito, con prezzo e foto, non venduti;
- i due negozi si alternano; fascia di prezzo solo se c'e' un pezzo adatto;
- ogni brief ha la chiusura "Scrivici, ti diciamo se è disponibile" e, se c'e' un pezzo, prezzo e codice M-XXXXX;
- nessuna parola promozionale quando l'evento ha no_promo; nessun giorno o orario promesso.
Nel file di stato (memory/piano.json) non ci sono dati di clienti: solo settimane, proposte, stato e motivo del salto.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Callable

from main import MEMORY_ROOT
from piece_code import piece_code

BASE_DIR = Path(__file__).parent
CALENDAR_PATH = BASE_DIR / "skills" / "_base" / "calendario-eventi.json"
STATE_PATH = MEMORY_ROOT / "piano.json"

ROLES = ("scoperta", "acquisto")
CLOSING = "Scrivici, ti diciamo se è disponibile"
MIN_WEEKS_BETWEEN_SAME_PIECE = 3  # stesso pezzo solo a 3 settimane o piu' di distanza
PROVISIONAL_WEEKS = 2
MAX_SKIP_NOTE = 200
STATES = ("proposto", "creato", "pubblicato", "saltato")
LOCATIONS = {"via-cavour-17": "via Cavour 17", "via-cavour-21": "via Cavour 21"}

PROMO_RE = re.compile(r"scont|promo|offert|saldi|black\s*friday|outlet|%", re.IGNORECASE)
WEEKDAY_RE = re.compile(
    r"\b(luned[iì]|marted[iì]|mercoled[iì]|gioved[iì]|venerd[iì]|sabato|domenica)\b", re.IGNORECASE
)
MONTHS = (
    "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre"
).split()
DATE_RE = re.compile(
    r"\b\d{1,2}\s+(" + "|".join(MONTHS) + r")\b|\b\d{1,2}/\d{1,2}\b|\b(ore|alle)\s*\d", re.IGNORECASE
)


class PianoError(ValueError):
    def __init__(self, message: str, status: int = 409):
        super().__init__(message)
        self.status = status


# ---------------------------------------------------------------- calendario

def load_calendar(path: Path | None = None) -> dict:
    return json.loads((path or CALENDAR_PATH).read_text(encoding="utf-8"))


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def week_label(monday: date) -> str:
    end = monday + timedelta(days=6)
    if monday.month == end.month:
        return f"{monday.day}–{end.day} {MONTHS[end.month - 1]}"
    return f"{monday.day} {MONTHS[monday.month - 1]} – {end.day} {MONTHS[end.month - 1]}"


def event_for_week(calendar: dict, monday: date) -> dict:
    """L'evento che copre il giovedi' della settimana; se non c'e', la settimana libera."""
    probe = (monday + timedelta(days=3)).isoformat()
    for event in calendar.get("eventi", []):
        if event["dal"] <= probe <= event["al"]:
            return event
    return calendar["evento_generico"]


def _role_config(calendar: dict, event: dict, role: str) -> dict:
    base = dict(calendar["ruoli"][role])
    specific = (event.get("ruoli") or {}).get(role) or {}
    generic = (calendar["evento_generico"].get("ruoli") or {}).get(role) or {}
    merged = {**base, **generic, **specific}
    merged["pref"] = list(specific.get("skills") or [])
    merged["pool"] = list(base.get("skills") or [])
    return merged


# --------------------------------------------------------------------- stato

def empty_state() -> dict:
    return {"versione": 1, "settimane": {}}


def load_state(path: Path | None = None) -> dict:
    target = path or STATE_PATH
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return empty_state()
    if not isinstance(data, dict) or not isinstance(data.get("settimane"), dict):
        return empty_state()
    return data


def save_state(state: dict, path: Path | None = None) -> None:
    target = path or STATE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(target)


def _new_slot() -> dict:
    return {
        "stato": "proposto",
        "tentativo": 0,
        "scartate": [],
        "proposta": None,
        "reel_id": None,
        "creato_il": None,
        "pubblicato_il": None,
        "motivo_salto": "",
    }


def _week(state: dict, monday: date) -> dict:
    return state["settimane"].setdefault(monday.isoformat(), {})


def parse_ref(week: str, role: str) -> tuple[date, str]:
    try:
        monday = date.fromisoformat(week)
    except ValueError as exc:
        raise PianoError("Settimana non valida.", 400) from exc
    if monday.weekday() != 0:
        raise PianoError("La settimana si indica con il lunedì.", 400)
    if role not in ROLES:
        raise PianoError("Ruolo non valido.", 400)
    return monday, role


# ------------------------------------------------------------------- scelta

def _jitter(*parts) -> float:
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / 2**32


def eligible_pieces(catalog: list[dict]) -> list[dict]:
    """Solo pezzi pubblicati sul sito, con prezzo e foto, non venduti; i piu' recenti per primi."""
    rows = [
        p
        for p in catalog
        if p.get("published")
        and p.get("run_id")
        and isinstance(p.get("price"), (int, float))
        and p["price"] > 0
        and p.get("cover")
        and p.get("state") != "sold"
    ]
    return sorted(rows, key=lambda p: str(p.get("published_at") or ""), reverse=True)


def _live_slots(state: dict, monday: date, role: str | None = None):
    """Slot non saltati di una settimana (con proposta)."""
    for slot_role, slot in (state["settimane"].get(monday.isoformat()) or {}).items():
        if role and slot_role != role:
            continue
        if slot.get("proposta") and slot.get("stato") != "saltato":
            yield slot_role, slot


def _skills_nearby(state: dict, monday: date, role: str) -> set[str]:
    skills = set()
    for shift in (-7, 7):
        for _, slot in _live_slots(state, monday + timedelta(days=shift)):
            skills.add(slot["proposta"]["skill"]["id"])
    for other_role, slot in _live_slots(state, monday):
        if other_role != role:
            skills.add(slot["proposta"]["skill"]["id"])
    return skills


def _pieces_nearby(state: dict, monday: date, role: str) -> set[str]:
    used = set()
    for offset in range(-(MIN_WEEKS_BETWEEN_SAME_PIECE - 1), MIN_WEEKS_BETWEEN_SAME_PIECE):
        other = monday + timedelta(days=7 * offset)
        for slot_role, slot in _live_slots(state, other):
            if other == monday and slot_role == role:
                continue
            piece = slot["proposta"].get("pezzo")
            if piece:
                used.add(piece["run_id"])
    return used


def _last_location(state: dict, monday: date) -> str | None:
    previous = list(_live_slots(state, monday - timedelta(days=7)))
    for _, slot in reversed(previous):
        piece = slot["proposta"].get("pezzo")
        if piece:
            return piece["location"]
    return None


def _other_location(state: dict, monday: date, role: str) -> str | None:
    for other_role, slot in _live_slots(state, monday):
        if other_role != role and slot["proposta"].get("pezzo"):
            return slot["proposta"]["pezzo"]["location"]
    return None


def _skill_info(skill_id: str) -> dict | None:
    import skills_loader

    skill = skills_loader.load_skill(skill_id)
    if not skill:
        return None
    return {"id": skill["id"], "label": skill["label"], "uses_model": bool(skill["uses_model"])}


def format_price(price: float) -> str:
    value = float(price)
    if value == int(value):
        return f"{int(value)} €"
    return f"{value:.2f}".replace(".", ",") + " €"


def _public_piece(piece: dict) -> dict:
    return {
        "run_id": piece["run_id"],
        "product_id": piece.get("product_id", ""),
        "title": piece.get("title", ""),
        "price": float(piece["price"]),
        "price_text": format_price(piece["price"]),
        "location": piece.get("location") or "",
        "location_label": LOCATIONS.get(piece.get("location") or "", ""),
        "category": piece.get("category", ""),
        "cover": piece["cover"],
        "code": piece_code(piece["run_id"]),
    }


def standard_brief(skill: dict, piece: dict | None, angle: str, calendar: dict) -> str:
    parts = [angle.strip()]
    note = (calendar.get("note_skill") or {}).get(skill["id"], "")
    if note:
        parts.append(note)
    if piece:
        where = f", in {piece['location_label']}" if piece["location_label"] else ""
        parts.append(f"Pezzo: {piece['title']}, {piece['price_text']}, riferimento {piece['code']}{where}.")
    else:
        parts.append("Scegli un pezzo pubblicato con prezzo e foto.")
    parts.append(f"Chiudi con: «{CLOSING}».")
    return " ".join(p for p in parts if p)


def validate_brief(text: str, piece: dict | None, no_promo: bool) -> list[str]:
    """Problemi di un brief; lista vuota = va bene. Vale per i brief standard e per quelli rifiniti dall'AI."""
    problems = []
    if CLOSING.lower() not in text.lower():
        problems.append("manca la chiusura")
    if piece:
        if piece["price_text"] not in text:
            problems.append("manca il prezzo")
        if piece["code"] not in text:
            problems.append("manca il codice del pezzo")
    if no_promo and PROMO_RE.search(text):
        problems.append("parole promozionali")
    if WEEKDAY_RE.search(text) or DATE_RE.search(text):
        problems.append("giorno o orario promesso")
    if len(text) > 700:
        problems.append("troppo lungo")
    return problems


Refiner = Callable[[str, dict], "str | None"]


def make_proposal(
    monday: date,
    role: str,
    state: dict,
    catalog: list[dict],
    calendar: dict,
    attempt: int = 0,
    rejected: list | None = None,
    avoid: tuple[str, str] | None = None,
    refiner: Refiner | None = None,
) -> dict:
    event = event_for_week(calendar, monday)
    cfg = _role_config(calendar, event, role)
    no_promo = bool(event.get("no_promo", True))
    rejected_pairs = {tuple(pair) for pair in (rejected or [])}

    def candidates(use_rejected: bool):
        blocked_skills = _skills_nearby(state, monday, role)
        pool = [s for s in cfg["pool"] if s not in blocked_skills]
        if not pool:  # ruoli senza alternative: si pesca anche dall'altro ruolo
            other = [r for r in ROLES if r != role][0]
            pool = [s for s in calendar["ruoli"][other]["skills"] if s not in blocked_skills]
        pool = [s for s in pool if _skill_info(s)]
        used_pieces = _pieces_nearby(state, monday, role)
        pieces = [p for p in eligible_pieces(catalog) if p["run_id"] not in used_pieces]
        cap = cfg.get("prezzo_max")
        applied = False
        if cap and any(p["price"] <= cap for p in pieces):
            pieces = [p for p in pieces if p["price"] <= cap]
            applied = True
        pairs = []
        for skill_id in pool:
            options = pieces or [None]
            for piece in options:
                key = (skill_id, piece["run_id"] if piece else "")
                if avoid and key == tuple(avoid):
                    continue
                if use_rejected and key in rejected_pairs:
                    continue
                pairs.append((skill_id, piece))
        return pairs, applied

    pairs, cap_applied = candidates(True)
    repeated = False
    if not pairs:
        pairs, cap_applied = candidates(False)
        repeated = True
    if not pairs:
        raise PianoError("Non ho altre idee diverse per questa settimana.")

    pieces_all = eligible_pieces(catalog)
    rank = {p["run_id"]: 1 - i / max(len(pieces_all), 1) for i, p in enumerate(pieces_all)}
    other_loc = _other_location(state, monday, role)
    last_loc = _last_location(state, monday)
    prefs = calendar.get("preferenze_pezzo") or {}

    def score(pair) -> float:
        skill_id, piece = pair
        pref = cfg["pref"]
        total = 0.0
        if skill_id in pref:
            total += 1.0 + 0.2 * (1 - pref.index(skill_id) / max(len(pref), 1))
        if piece:
            total += rank.get(piece["run_id"], 0)
            loc = piece.get("location")
            if loc and other_loc and loc != other_loc:
                total += 0.6
            if loc and last_loc and loc != last_loc:
                total += 0.3
            title = str(piece.get("title", "")).lower()
            if any(word in title for word in prefs.get(skill_id, [])):
                total += 0.6
        total += 0.4 * _jitter(monday, role, attempt, skill_id, piece["run_id"] if piece else "")
        return total

    skill_id, raw_piece = max(pairs, key=score)
    skill = _skill_info(skill_id)
    piece = _public_piece(raw_piece) if raw_piece else None

    angle = cfg.get("angolo", "")
    if cfg.get("prezzo_max") and not cap_applied:
        angle = cfg.get("angolo_senza_fascia") or angle.replace("sotto i 50 euro", "").replace("  ", " ")
    brief = standard_brief(skill, piece, angle, calendar)
    ai_used = False
    if refiner:
        candidate = None
        try:
            candidate = refiner(brief, {"skill": skill, "pezzo": piece, "tema": event["tema"], "angolo": angle})
        except Exception:
            candidate = None
        if candidate and not validate_brief(candidate, piece, no_promo):
            brief, ai_used = candidate.strip(), True

    notes = []
    if not piece:
        notes.append("Non c'è un pezzo pubblicato con prezzo e foto: pubblicane uno sul sito e riapri il Piano.")
    if repeated:
        notes.append("Non c'erano altre combinazioni diverse: questa è già stata proposta.")
    if skill["uses_model"]:
        notes.append("Compare una donna creata dall'AI: quando pubblichi attiva «Info sull'AI».")
    why_piece = ""
    if piece:
        bits = ["tra i pezzi pubblicati di recente"]
        if cap_applied:
            bits.append(f"nella fascia fino a {int(cfg['prezzo_max'])} €")
        if other_loc and piece["location"] != other_loc:
            bits.append("alterna i due negozi")
        why_piece = "Scelto perché è " + ", ".join(bits) + "."

    return {
        "ruolo": role,
        "ruolo_etichetta": calendar["ruoli"][role]["etichetta"],
        "tema": event["tema"],
        "skill": skill,
        "pezzo": piece,
        "motivo": f"{event['tema']}: {calendar['ruoli'][role]['motivo']}",
        "motivo_pezzo": why_piece,
        "brief": brief,
        "brief_ai": ai_used,
        "storie": event.get("storie") or calendar["evento_generico"]["storie"],
        "storie_promemoria": "Riusa il contenuto nelle Storie nei 3 giorni dopo la pubblicazione: nessuna produzione nuova.",
        "avvisi": notes,
    }


# ------------------------------------------------------------------ settimane

def _proposal_is_stale(proposal: dict, catalog: list[dict]) -> bool:
    """La proposta non e' piu' valida se il pezzo e' sparito o venduto, o se ora ci sono pezzi e lei non ne ha."""
    eligible = {p["run_id"] for p in eligible_pieces(catalog)}
    piece = proposal.get("pezzo")
    if piece:
        return piece["run_id"] not in eligible
    return bool(eligible)


def ensure_week(
    state: dict,
    monday: date,
    catalog: list[dict],
    calendar: dict,
    refiner: Refiner | None = None,
) -> dict:
    week = _week(state, monday)
    for role in ROLES:
        slot = week.get(role)
        if slot is None:
            slot = week[role] = _new_slot()
        if slot["stato"] in ("creato", "pubblicato", "saltato"):
            continue
        if slot["proposta"] and not _proposal_is_stale(slot["proposta"], catalog):
            continue
        slot["proposta"] = None  # cosi' i vincoli non contano la proposta da sostituire
        slot["proposta"] = make_proposal(
            monday, role, state, catalog, calendar, slot["tentativo"], slot["scartate"], refiner=refiner
        )
    return week


def _slot_view(slot: dict) -> dict:
    return {
        "stato": slot["stato"],
        "proposta": slot["proposta"],
        "reel_id": slot["reel_id"],
        "pubblicato_il": slot["pubblicato_il"],
        "motivo_salto": slot["motivo_salto"],
        "tentativo": slot["tentativo"],
    }


def build_view(
    state: dict, catalog: list[dict], calendar: dict, today: date, refiner: Refiner | None = None
) -> dict:
    """Mostra la settimana corrente (salvata nello stato) e le due successive (provvisorie, non salvate)."""
    current = monday_of(today)
    ensure_week(state, current, catalog, calendar, refiner)
    simulated = copy.deepcopy(state)
    weeks = []
    for index in range(PROVISIONAL_WEEKS + 1):
        monday = current + timedelta(days=7 * index)
        if index:
            ensure_week(simulated, monday, catalog, calendar, None)
        source = state if index == 0 else simulated
        week = source["settimane"][monday.isoformat()]
        event = event_for_week(calendar, monday)
        weeks.append(
            {
                "inizio": monday.isoformat(),
                "etichetta": week_label(monday),
                "tema": event["tema"],
                "corrente": index == 0,
                "provvisoria": index > 0,
                "slot": {role: _slot_view(week[role]) for role in ROLES},
            }
        )
    return {
        "oggi": today.isoformat(),
        "settimane": weeks,
        "regole": [
            "2 contenuti a settimana, nessun giorno promesso",
            "Chiusura: " + CLOSING,
            "Pezzo con prezzo e codice nel brief",
            "Storie: riuso nei 3 giorni dopo, non produzione nuova",
        ],
    }


# ------------------------------------------------------------------ azioni

def _slot(state: dict, monday: date, role: str) -> dict:
    slot = (state["settimane"].get(monday.isoformat()) or {}).get(role)
    if not slot:
        raise PianoError("Questa settimana non è ancora aperta: compare solo come anteprima.")
    return slot


def altra_idea(
    state: dict, monday: date, role: str, catalog: list[dict], calendar: dict, refiner: Refiner | None = None
) -> dict:
    slot = _slot(state, monday, role)
    if slot["stato"] != "proposto":
        raise PianoError("Si può cambiare idea solo finché il contenuto è solo proposto.")
    current = slot["proposta"]
    if current:
        slot["scartate"].append([current["skill"]["id"], (current.get("pezzo") or {}).get("run_id", "")])
    slot["tentativo"] += 1
    avoid = None
    if current:
        avoid = (current["skill"]["id"], (current.get("pezzo") or {}).get("run_id", ""))
    slot["proposta"] = None
    slot["proposta"] = make_proposal(
        monday, role, state, catalog, calendar, slot["tentativo"], slot["scartate"], avoid=avoid, refiner=refiner
    )
    return slot


def salta(state: dict, monday: date, role: str, motivo: str = "") -> dict:
    slot = _slot(state, monday, role)
    if slot["stato"] in ("creato", "pubblicato"):
        raise PianoError("Il contenuto è già stato creato: non si può saltare.")
    slot["stato"] = "saltato"
    slot["motivo_salto"] = (motivo or "").strip()[:MAX_SKIP_NOTE]
    return slot


def segna_pubblicato(state: dict, monday: date, role: str, today: date) -> dict:
    slot = _slot(state, monday, role)
    if slot["stato"] == "saltato":
        raise PianoError("Questo contenuto è stato saltato.")
    if not slot["proposta"]:
        raise PianoError("Non c'è una proposta da segnare.")
    slot["stato"] = "pubblicato"
    slot["pubblicato_il"] = today.isoformat()
    return slot


def collega_reel(state: dict, reference: str, reel_id: str, today: date) -> bool:
    """Chiamata alla creazione di un Reel partito da 'Crea': segna il contenuto come creato."""
    week, _, role = (reference or "").partition(":")
    try:
        monday, role = parse_ref(week, role)
    except PianoError:
        return False
    slot = (state["settimane"].get(monday.isoformat()) or {}).get(role)
    if not slot or slot["stato"] in ("saltato", "pubblicato"):
        return False
    slot["stato"] = "creato"
    slot["reel_id"] = reel_id
    slot["creato_il"] = today.isoformat()
    return True
