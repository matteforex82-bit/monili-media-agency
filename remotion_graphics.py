"""Grafica Monili sopra un video già pronto, con Remotion (cartella `remotion/`).

Aggiunge una frase d'apertura, la targhetta col nome e il prezzo del pezzo e la chiusura animata
"Ti piace? Scrivici, ti diciamo se è disponibile." Remotion gira sul PC con il proprio browser
(scaricato da lui la prima volta). Se non è installato o il render fallisce, chi chiama ripiega
sul montaggio semplice con ffmpeg.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

REMOTION_DIR = Path(__file__).resolve().parent / "remotion"
COMPOSITION = "ReelGrafica"
RENDER_TIMEOUT_SECONDS = 900

PLACES = {
    "via-cavour-17": "Via Cavour 17, Ravenna",
    "via-cavour-21": "Via Cavour 21, Ravenna",
}
DEFAULT_PLACE = "Via Cavour, Ravenna"


def is_available() -> bool:
    """Vero se la cartella remotion/ ha le sue dipendenze e Node è installato."""
    return (REMOTION_DIR / "node_modules" / "@remotion" / "cli").exists() and bool(shutil.which("node"))


def place_label(location: str) -> str:
    return PLACES.get((location or "").strip(), DEFAULT_PLACE)


def render_graphics(
    source: Path,
    output: Path,
    seconds: float,
    *,
    hook: str = "",
    title: str = "",
    price: str = "",
    place: str = DEFAULT_PLACE,
    closing: bool = True,
) -> Path:
    """Render del video con la grafica. Solleva RuntimeError se non riesce."""
    if not is_available():
        raise RuntimeError("Remotion non è installato (cartella remotion/: eseguire npm install).")
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx:
        raise RuntimeError("npx non trovato: serve Node.js.")
    work = Path(tempfile.mkdtemp(prefix="remotion-"))
    try:
        public = work / "public"
        public.mkdir()
        name = f"video-{uuid.uuid4().hex[:8]}.mp4"
        shutil.copyfile(source, public / name)
        props = {
            "video": name,
            "videoSeconds": round(float(seconds), 2),
            "hook": (hook or "").strip()[:80],
            "title": (title or "").strip()[:70],
            "price": (price or "").strip()[:20],
            "place": place or DEFAULT_PLACE,
            "closing": bool(closing),
            "titleFrom": 2.5,
        }
        props_file = work / "props.json"
        props_file.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
        output.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            npx, "remotion", "render", "src/index.ts", COMPOSITION, str(output),
            f"--props={props_file}", f"--public-dir={public}", "--is-production=false", "--log=error",
        ]
        try:
            run = subprocess.run(cmd, cwd=REMOTION_DIR, capture_output=True, text=True, timeout=RENDER_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Remotion ci mette troppo: render interrotto.") from exc
        if run.returncode != 0 or not output.exists():
            tail = (run.stderr or run.stdout or "").strip()[-400:]
            raise RuntimeError(f"Render Remotion non riuscito: {tail}")
        return output
    finally:
        shutil.rmtree(work, ignore_errors=True)
