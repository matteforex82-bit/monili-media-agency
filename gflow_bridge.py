"""Local Google Flow CLI integration for Studio product images."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image


class FlowError(RuntimeError):
    pass


def executable() -> str | None:
    configured = os.environ.get("GFLOW_EXECUTABLE", "").strip()
    if configured and Path(configured).is_file():
        return configured
    found = shutil.which("gflow")
    if found:
        return found
    fallback = Path.home() / ".local" / "bin" / ("gflow.exe" if os.name == "nt" else "gflow")
    return str(fallback) if fallback.is_file() else None


def generate_image(prompt: str, image: Path, destination: Path, aspect: str, model: str) -> None:
    exe = executable()
    if not exe:
        raise FlowError("Google Flow CLI non è installata sul computer dello Studio.")
    if model not in {"nano2", "nano-pro", "nano2-lite"} or aspect not in {"4:3", "9:16"}:
        raise FlowError("Modello o formato non valido.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="monili-flow-") as work:
        requested = Path(work) / "generated.png"
        cmd = [exe, "image", "i2i", prompt, "--ref", str(image.resolve()), "--model", model, "--aspect", aspect, "--count", "1", "--out-file", str(requested), "--json"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600, stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except subprocess.TimeoutExpired as error:
            raise FlowError("Google Flow non ha risposto in tempo. Controlla Flow prima di riprovare.") from error
        candidates = [p for p in Path(work).glob("generated.*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and p.is_file()]
        if result.returncode != 0 or len(candidates) != 1:
            diagnostic = (result.stdout or "") + (result.stderr or "")
            if "SettingsPaneMixin" in diagnostic or "TimeoutError" in diagnostic:
                raise FlowError("Google Flow non ha risposto mentre venivano impostati modello e formato. Controlla il progetto su Flow prima di riprovare: la CLI non ha confermato se la richiesta sia stata avviata.")
            if "MediaUploadRejectedError" in diagnostic or "media-upload-rejected" in diagnostic:
                raise FlowError("Flow ha bloccato il caricamento della foto. Apri un progetto in Google Flow, carica manualmente una tua immagine e verifica l'eventuale richiesta sui diritti d'uso; poi riprova.")
            raise FlowError("Google Flow non ha creato l'immagine. Verifica l'accesso, il modello e l'eventuale quota disponibile su Flow.")
        try:
            with Image.open(candidates[0]) as im:
                im.load()
                im.convert("RGB").save(destination, "PNG")
        except (OSError, ValueError) as error:
            destination.unlink(missing_ok=True)
            raise FlowError("Google Flow ha restituito un file immagine non valido.") from error
