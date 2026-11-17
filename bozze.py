"""Bozze veloci: le foto e la nota scritte in negozio, da trasformare in Scheda pezzo più tardi.

In negozio si fotografa il pezzo e si scrive due righe («ametista, 159 euro, misura 13»): lo Studio salva tutto
senza chiamare nessuna AI. Più tardi, dal PC o dal telefono, ogni bozza diventa una Scheda pezzo con un tocco.

Ogni bozza è una cartella `bozze/<id>/` nello storage con `bozza.json` e le foto. Questo modulo conosce solo i
file: non sa niente di FastAPI né di Higgsfield, così si prova senza rete (`tests/test_bozze.py`).
"""

from __future__ import annotations

import json
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path

META_NAME = "bozza.json"
THUMB_DIR = "miniature"
STATUS_TODO = "da_lavorare"
STATUS_RUNNING = "in_corso"
STATUS_DONE = "scheda_pronta"

# Pietre che si riconoscono nella nota (solo per mostrare i dati in evidenza: la nota resta com'è).
STONES = [
    "quarzo rosa", "quarzo ialino", "quarzo fumé", "quarzo fume", "occhio di tigre", "occhio di falco", "occhio di bue",
    "pietra di luna", "pietra di sole", "lapislazzuli", "acquamarina", "labradorite", "aventurina", "calcedonio",
    "crisoprasio", "crisoberillo", "rodocrosite", "ametista", "citrino", "turchese", "opale", "agata", "corniola",
    "diaspro", "ematite", "fluorite", "giada", "granato", "malachite", "onice", "ossidiana", "rodonite", "sodalite",
    "tormalina", "zaffiro", "rubino", "smeraldo", "topazio", "peridoto", "morganite", "perla", "perle", "zircone",
    "zirconi", "corallo", "ambra",
]
_PRICE_RE = re.compile(r"(?:€\s*(\d+(?:[.,]\d{1,2})?))|(?:(\d+(?:[.,]\d{1,2})?)\s*(?:€|euro|eur)\b)", re.IGNORECASE)
_SIZE_RE = re.compile(r"\b(?:misura|mis\.?|taglia|tg\.?|n\.?)\s*([0-9]{1,2}(?:[.,]5)?|xxs|xs|s|m|l|xl|xxl|unica)\b", re.IGNORECASE)


def quick_facts(note: str) -> dict:
    """Prezzo, misura e pietre riconosciuti nella nota ({} per quello che non si trova)."""
    text = (note or "").strip()
    facts: dict = {}
    match = _PRICE_RE.search(text)
    if match:
        raw = (match.group(1) or match.group(2) or "").replace(",", ".")
        try:
            value = float(raw)
            facts["prezzo"] = int(value) if value == int(value) else value
        except ValueError:
            pass
    size = _SIZE_RE.search(text)
    if size:
        facts["misura"] = size.group(1).upper() if size.group(1).isalpha() else size.group(1)
    lowered = text.lower()
    found: list[str] = []
    for stone in STONES:
        if re.search(rf"\b{re.escape(stone)}\b", lowered) and not any(stone in other for other in found):
            found.append(stone)
    if found:
        facts["pietre"] = [stone.capitalize() for stone in found]
    return facts


class BozzeStore:
    def __init__(self, root: Path, trash: Path | None = None):
        self.root = Path(root)
        self.trash = Path(trash) if trash else None
        self.root.mkdir(parents=True, exist_ok=True)

    # -- percorsi ------------------------------------------------------------------------------
    def folder(self, draft_id: str) -> Path | None:
        """Cartella della bozza, solo se l'id è fatto come quelli che creiamo (niente percorsi strani)."""
        if not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[0-9a-f]{6}", draft_id or ""):
            return None
        path = self.root / draft_id
        return path if path.is_dir() else None

    def photo_path(self, draft_id: str, name: str) -> Path | None:
        folder = self.folder(draft_id)
        if not folder or Path(name).name != name:
            return None
        path = folder / name
        return path if path.is_file() else None

    def new_folder(self) -> tuple[str, Path]:
        draft_id = f"{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
        path = self.root / draft_id
        path.mkdir(parents=True)
        return draft_id, path

    # -- dati ------------------------------------------------------------------------------------
    def _read(self, folder: Path) -> dict | None:
        try:
            return json.loads((folder / META_NAME).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def _write(self, folder: Path, meta: dict) -> None:
        tmp = folder / (META_NAME + ".tmp")
        tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(folder / META_NAME)

    def create(self, folder: Path, note: str, photos: list[str]) -> dict:
        meta = {
            "id": folder.name,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "note": (note or "").strip(),
            "photos": list(photos),
            "main": photos[0] if photos else "",
            "detail": photos[1] if len(photos) > 1 else "",
            "status": STATUS_TODO,
            "job_id": "",
            "run_id": "",
            "error": "",
        }
        self._write(folder, meta)
        return self.public(meta)

    def public(self, meta: dict) -> dict:
        out = dict(meta)
        out["facts"] = quick_facts(meta.get("note", ""))
        return out

    def get(self, draft_id: str) -> dict | None:
        folder = self.folder(draft_id)
        meta = self._read(folder) if folder else None
        return self.public(meta) if meta else None

    def list(self, limit: int = 100) -> list[dict]:
        items: list[dict] = []
        for folder in sorted(self.root.iterdir(), reverse=True):
            if not folder.is_dir():
                continue
            meta = self._read(folder)
            if meta:
                items.append(self.public(meta))
        # Da lavorare in cima (le più recenti prima), poi in corso, poi quelle con la scheda già pronta.
        order = {STATUS_TODO: 0, STATUS_RUNNING: 1, STATUS_DONE: 2}
        items.sort(key=lambda item: (order.get(item["status"], 3), -_stamp(item["created_at"])))
        return items[:limit]

    def update(self, draft_id: str, **fields) -> dict | None:
        folder = self.folder(draft_id)
        meta = self._read(folder) if folder else None
        if not meta:
            return None
        if "note" in fields and fields["note"] is not None:
            meta["note"] = str(fields["note"]).strip()
        for key in ("main", "detail"):
            if key in fields and fields[key] is not None:
                value = str(fields[key])
                meta[key] = value if value in meta["photos"] else ""
        for key in ("status", "job_id", "run_id", "error"):
            if key in fields and fields[key] is not None:
                meta[key] = fields[key]
        self._write(folder, meta)
        return self.public(meta)

    def add_photos(self, draft_id: str, names: list[str]) -> dict | None:
        folder = self.folder(draft_id)
        meta = self._read(folder) if folder else None
        if not meta:
            return None
        meta["photos"].extend(name for name in names if name not in meta["photos"])
        if not meta.get("main") and meta["photos"]:
            meta["main"] = meta["photos"][0]
        if not meta.get("detail") and len(meta["photos"]) > 1:
            meta["detail"] = next((p for p in meta["photos"] if p != meta["main"]), "")
        self._write(folder, meta)
        return self.public(meta)

    def remove_photo(self, draft_id: str, name: str) -> dict | None:
        folder = self.folder(draft_id)
        meta = self._read(folder) if folder else None
        if not meta or name not in meta["photos"]:
            return None
        meta["photos"].remove(name)
        (folder / name).unlink(missing_ok=True)
        (folder / THUMB_DIR / name).unlink(missing_ok=True)
        if meta.get("main") == name:
            meta["main"] = meta["photos"][0] if meta["photos"] else ""
        if meta.get("detail") == name or meta.get("detail") == meta.get("main"):
            meta["detail"] = next((p for p in meta["photos"] if p != meta["main"]), "")
        self._write(folder, meta)
        return self.public(meta)

    def delete(self, draft_id: str) -> bool:
        """Sposta la bozza nel cestino dello Studio (non la cancella davvero)."""
        folder = self.folder(draft_id)
        if not folder:
            return False
        if self.trash:
            self.trash.mkdir(parents=True, exist_ok=True)
            target = self.trash / f"bozza-{folder.name}"
            suffix = 2
            while target.exists():
                target = self.trash / f"bozza-{folder.name}-{suffix}"
                suffix += 1
            shutil.move(str(folder), str(target))
        else:
            shutil.rmtree(folder)
        return True

    def reset_stale(self, running_job_ids: set[str]) -> int:
        """Dopo un riavvio dello Studio: le bozze «in corso» il cui lavoro non esiste più tornano da lavorare."""
        fixed = 0
        for folder in self.root.iterdir():
            meta = self._read(folder) if folder.is_dir() else None
            if meta and meta.get("status") == STATUS_RUNNING and meta.get("job_id") not in running_job_ids:
                meta["status"] = STATUS_TODO
                meta["error"] = "Il lavoro si è interrotto (lo Studio è stato riavviato). Riprova."
                self._write(folder, meta)
                fixed += 1
        return fixed


def _stamp(value: str) -> float:
    try:
        return datetime.fromisoformat(value).timestamp()
    except (TypeError, ValueError):
        return 0.0
