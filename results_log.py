"""
results_log.py - diario dei risultati dei contenuti pubblicati.

Dopo la pubblicazione si inseriscono i numeri di ogni Reel/Story (dagli Insights di Instagram).
Il riepilogo dice quali skill, formati e giorni funzionano meglio e finisce nei prompt degli agenti.
File: <storage>/memory/risultati_contenuti.json
"""

import json
import threading
from datetime import date, datetime
from statistics import mean

from main import MEMORY_ROOT

RESULTS_FILE = MEMORY_ROOT / "risultati_contenuti.json"
METRICS = ("views", "reach", "likes", "comments", "saves", "sends", "dms", "store_visits", "sales_eur")
METRIC_LABELS = {
    "views": "visualizzazioni",
    "reach": "account raggiunti",
    "likes": "like",
    "comments": "commenti",
    "saves": "salvataggi",
    "sends": "invii",
    "dms": "DM ricevuti",
    "store_visits": "visite in negozio",
    "sales_eur": "vendite (EUR)",
}
WEEKDAYS = ["lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato", "domenica"]
MIN_SAMPLE = 2  # sotto questo numero di contenuti un gruppo non viene usato come "regola"

_lock = threading.Lock()


def _load() -> dict:
    try:
        data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("items"), dict):
            return data
    except Exception:
        pass
    return {"items": {}}


def _save(data: dict) -> None:
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESULTS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(RESULTS_FILE)


def _number(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(str(value).replace(",", ".").replace(" ", ""))
    except ValueError:
        raise ValueError(f"Valore non numerico: {value}")
    if number < 0:
        raise ValueError("I numeri non possono essere negativi.")
    return number


def _parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        return date.fromisoformat(str(value)[:10]).isoformat()
    except ValueError:
        raise ValueError("Data non valida: usa il formato AAAA-MM-GG.")


def upsert(entry_id: str, payload: dict) -> dict:
    """Crea o aggiorna i numeri di un contenuto. entry_id = id del reel oppure 'manuale-...'."""
    entry_id = str(entry_id or "").strip()
    if not entry_id or len(entry_id) > 80:
        raise ValueError("Id contenuto non valido.")
    metrics = {}
    for key in METRICS:
        if key in (payload.get("metrics") or {}):
            metrics[key] = _number(payload["metrics"][key])
    hour = payload.get("hour")
    if hour not in (None, ""):
        try:
            hour = int(hour)
        except (TypeError, ValueError):
            raise ValueError("Ora non valida (0-23).")
        if not 0 <= hour <= 23:
            raise ValueError("Ora non valida (0-23).")
    else:
        hour = None
    with _lock:
        data = _load()
        current = data["items"].get(entry_id, {})
        entry = {
            **current,
            "id": entry_id,
            "title": str(payload.get("title", current.get("title", "")))[:120],
            "skill": str(payload.get("skill", current.get("skill", "")) or "")[:40],
            "format": fmt if (fmt := payload.get("format", current.get("format", "reel"))) in ("reel", "story", "post") else "reel",
            "published_on": _parse_date(payload.get("published_on", current.get("published_on", ""))),
            "hour": hour if "hour" in payload else current.get("hour"),
            "metrics": {**current.get("metrics", {}), **metrics},
            "notes": str(payload.get("notes", current.get("notes", "")))[:500],
            "cover": payload.get("cover", current.get("cover")),
            "updated_at": datetime.now().isoformat(),
        }
        data["items"][entry_id] = entry
        _save(data)
    return entry


def delete(entry_id: str) -> bool:
    with _lock:
        data = _load()
        removed = data["items"].pop(entry_id, None) is not None
        if removed:
            _save(data)
    return removed


def items() -> list[dict]:
    entries = list(_load()["items"].values())
    return sorted(entries, key=lambda e: (e.get("published_on") or "", e.get("updated_at") or ""), reverse=True)


def _value(entry: dict, key: str) -> float | None:
    value = (entry.get("metrics") or {}).get(key)
    return float(value) if isinstance(value, (int, float)) else None


def _send_rate(entry: dict) -> float | None:
    views, sends = _value(entry, "views"), _value(entry, "sends")
    if views and sends is not None:
        return sends / views
    return None


def _group(entries: list[dict], key_fn) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        key = key_fn(entry)
        if key:
            groups.setdefault(key, []).append(entry)
    rows = []
    for key, group in groups.items():
        views = [v for v in (_value(e, "views") for e in group) if v is not None]
        rates = [r for r in (_send_rate(e) for e in group) if r is not None]
        dms = [v for v in (_value(e, "dms") for e in group) if v is not None]
        rows.append(
            {
                "key": key,
                "count": len(group),
                "avg_views": round(mean(views)) if views else None,
                "send_rate": round(mean(rates) * 100, 2) if rates else None,
                "avg_dms": round(mean(dms), 1) if dms else None,
                "reliable": len(group) >= MIN_SAMPLE,
            }
        )
    return sorted(rows, key=lambda r: (r["avg_views"] or 0), reverse=True)


def _weekday(entry: dict) -> str:
    try:
        return WEEKDAYS[date.fromisoformat(entry["published_on"]).weekday()]
    except Exception:
        return ""


def _hour_band(entry: dict) -> str:
    hour = entry.get("hour")
    if hour is None:
        return ""
    start = (int(hour) // 3) * 3
    return f"{start:02d}-{start + 3:02d}"


def summary() -> dict:
    entries = [e for e in items() if _value(e, "views") is not None]
    totals = {key: sum(_value(e, key) or 0 for e in items()) for key in METRICS}
    return {
        "count": len(items()),
        "with_numbers": len(entries),
        "totals": {k: round(v, 2) for k, v in totals.items()},
        "by_skill": _group(entries, lambda e: e.get("skill") or "altro"),
        "by_format": _group(entries, lambda e: e.get("format")),
        "by_weekday": _group(entries, _weekday),
        "by_hour": _group(entries, _hour_band),
        "best": sorted(entries, key=lambda e: _value(e, "views") or 0, reverse=True)[:3],
        "min_sample": MIN_SAMPLE,
    }


def prompt_hints() -> str:
    """Righe brevi per i prompt: solo gruppi con abbastanza contenuti per essere affidabili."""
    data = summary()
    if data["with_numbers"] < MIN_SAMPLE:
        return ""
    lines = [f"Risultati reali di {data['with_numbers']} contenuti pubblicati:"]
    skills = [r for r in data["by_skill"] if r["reliable"] and r["avg_views"] is not None]
    if skills:
        best, worst = skills[0], skills[-1]
        lines.append(f"- Skill che rende di piu: /{best['key']} (media {best['avg_views']} visualizzazioni su {best['count']} contenuti)")
        if worst is not best:
            lines.append(f"- Skill che rende di meno: /{worst['key']} (media {worst['avg_views']})")
    by_send = sorted(
        [r for r in data["by_skill"] if r["reliable"] and r["send_rate"] is not None], key=lambda r: r["send_rate"], reverse=True
    )
    if by_send:
        lines.append(f"- Piu condivisa in DM: /{by_send[0]['key']} ({by_send[0]['send_rate']}% invii per visualizzazione)")
    days = [r for r in data["by_weekday"] if r["reliable"] and r["avg_views"] is not None]
    if days:
        lines.append(f"- Giorno migliore: {days[0]['key']} (media {days[0]['avg_views']})")
    hours = [r for r in data["by_hour"] if r["reliable"] and r["avg_views"] is not None]
    if hours:
        lines.append(f"- Fascia oraria migliore: {hours[0]['key']}")
    for entry in data["best"][:2]:
        lines.append(f"- Top: \"{entry.get('title') or entry['id']}\" ({int(_value(entry, 'views') or 0)} visualizzazioni)")
    return "\n".join(lines) if len(lines) > 1 else ""
