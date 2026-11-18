"""
fucina_codex.py - chiama Codex (il programma installato sul PC, con l'abbonamento di Matteo) per guardare le foto.

Serve a valutare un risultato: Codex vede la foto vera e la foto creata e compila una lista di controllo.
Nessuna chiave: usa il login di `codex` già fatto sul PC. Il prompt passa da stdin (niente limiti di riga di comando).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

CODEX_HOME = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
TIMEOUT_SECONDS = int(os.environ.get("CODEX_TIMEOUT_SECONDS", "300"))


# Provato il 18/11/2026 con Codex 0.144.1: i modelli gpt-6.x chiedono un Codex più recente, gpt-5.6-sol funziona e vede le immagini.
DEFAULT_MODEL = os.environ.get("FUCINA_CODEX_MODEL", "gpt-5.6-sol")


class CodexError(RuntimeError):
    pass


def executable() -> str | None:
    return shutil.which("codex")


def available_models() -> dict:
    """Models Codex lists for this account that can see images, and the one set as default."""
    models: list[dict] = []
    try:
        data = json.loads((CODEX_HOME / "models_cache.json").read_text(encoding="utf-8"))
        for item in data.get("models", []):
            if item.get("visibility") == "list" and "image" in (item.get("input_modalities") or []):
                models.append({"slug": item.get("slug", ""), "name": item.get("display_name") or item.get("slug", "")})
    except Exception:
        pass
    default = DEFAULT_MODEL
    return {"installed": bool(executable()), "models": models, "default": default}


def run(prompt: str, images: list[Path], model: str = "") -> str:
    """Runs one non-interactive Codex request (read-only, in an empty folder) and returns its last message."""
    exe = executable()
    if not exe:
        raise CodexError("Codex non è installato su questo PC.")
    with tempfile.TemporaryDirectory(prefix="fucina-") as work:
        answer = Path(work) / "risposta.txt"
        command = [exe, "exec", "--skip-git-repo-check", "-s", "read-only", "-C", work, "-o", str(answer)]
        command += ["-m", model or DEFAULT_MODEL]
        for image in images:
            command += ["-i", str(image)]
        command.append("-")  # the instructions come from stdin
        try:
            done = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as error:
            raise CodexError(f"Codex non ha risposto entro {TIMEOUT_SECONDS // 60} minuti.") from error
        text = answer.read_text(encoding="utf-8", errors="replace").strip() if answer.exists() else ""
        if "requires a newer version" in (done.stderr or "") + (done.stdout or ""):
            raise CodexError("Questo modello chiede un Codex più recente: aggiornalo (npm i -g @openai/codex) o scegli gpt-5.6-sol.")
        if done.returncode != 0 or not text:
            detail = (done.stderr or done.stdout or "").strip().splitlines()[-3:]
            raise CodexError("Codex non ha risposto: " + (" ".join(detail) or f"codice {done.returncode}"))
        return text
