"""Render in background sul PC dello Studio, con stato recuperabile dopo il refresh."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
import uuid

import blender_scene
import reel_seedance_kit

SCRIPT = Path(__file__).resolve().parent / "scripts" / "render_reel_scene.py"
_lock = threading.Lock()
_active: Path | None = None
_process: subprocess.Popen | None = None


class RenderBusy(RuntimeError):
    pass


def _save(root: Path, state: dict) -> dict:
    target = root / "status.json"
    temp = target.with_suffix(".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    temp.replace(target)
    return state


def _read(root: Path) -> dict:
    try:
        return json.loads((root / "status.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"status": "idle"}


def status(root: Path) -> dict:
    with _lock:
        state = _read(root)
        if state["status"] not in {"queued", "rendering", "packing"}:
            return state
        if _active != root:
            return {**state, "status": "error", "error": "Render interrotto dallo spegnimento dello Studio. Puoi rilanciarlo."}
    if state["status"] == "rendering":
        log = root / state["id"] / "blender.log"
        try:
            with log.open("rb") as stream:
                total = re.search(rb"MONILI_TOTAL (\d+)", stream.read(8192))
                if total:
                    state["frames"] = int(total[1])
                stream.seek(max(0, log.stat().st_size - 32_768))
                frames = re.findall(rb"MONILI_FRAME (\d+)", stream.read())
            if frames:
                state["frame"] = int(frames[-1])
        except FileNotFoundError:
            pass
    return state


def _render_source(binary: str, source: Path, directory: Path, log: Path) -> None:
    global _process
    # Conserva la base dei percorsi relativi // di texture o librerie aggiunte in Blender.
    snapshot = source.with_name(f".render-{uuid.uuid4().hex}.blend")
    try:
        shutil.copyfile(source, snapshot)
        with log.open("wb") as stream:
            with _lock:
                process = subprocess.Popen(
                    [binary, "--background", "--disable-autoexec", str(snapshot),
                     "--python-exit-code", "1", "--python", str(SCRIPT), "--", str(directory)],
                    stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT,
                )
                _process = process
            try:
                exit_code = process.wait(timeout=1800)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise ValueError("Il render ha superato 30 minuti. Riduci la risoluzione di prova in Blender e riprova.")
            finally:
                with _lock:
                    _process = None
    finally:
        snapshot.unlink(missing_ok=True)
    if exit_code:
        raise ValueError("Blender ha interrotto il render. Controlla che il file salvato si apra e che le camere e la musica siano in timeline.")


def _work(root: Path, identifier: str, binary: str, source: Path, draft: dict, photos: list[tuple[str, bytes]]) -> None:
    global _active
    result = root / identifier
    state = {"id": identifier, "status": "rendering", "frames": round(draft["target_seconds"] * blender_scene.FPS)}
    try:
        with _lock:
            _save(root, state)
        with tempfile.TemporaryDirectory(prefix=".render-", dir=result) as work:
            directory = Path(work)
            _render_source(binary, source, directory, result / "blender.log")
            with _lock:
                _save(root, {**state, "status": "packing"})
            photo_paths = []
            for number, (ext, content) in enumerate(photos, 1):
                path = directory / f"foto-{number}{ext}"
                path.write_bytes(content)
                photo_paths.append(path)
            summary = reel_seedance_kit.assemble(directory, result, draft, photo_paths)
            (result / "ready").touch()
        with _lock:
            _save(root, {**state, **summary, "status": "ready"})
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
        for name in ("reel-blender.mp4", "kit-seedance.zip", "ready"):
            (result / name).unlink(missing_ok=True)
        detail = str(error) if type(error) is ValueError else "Non riesco a preparare il render. Controlla lo spazio sul PC e riprova."
        with _lock:
            _save(root, {**state, "status": "error", "error": detail})
    finally:
        with _lock:
            _active = None


def start(root: Path, binary: str, source: Path, draft: dict, photos: list[tuple[str, bytes]]) -> dict:
    global _active
    with _lock:
        if _active == root:
            return _read(root)
        if _active is not None:
            raise RenderBusy("C’è già un render Blender in corso sul PC.")
        identifier = str(uuid.uuid4())
        (root / identifier).mkdir(parents=True)
        queued = _save(root, {"id": identifier, "status": "queued"})
        _active = root
        worker = threading.Thread(target=_work, args=(root, identifier, binary, source, draft, photos), daemon=True)
        try:
            worker.start()
        except RuntimeError:
            _active = None
            return _save(root, {**queued, "status": "error", "error": "Non riesco ad avviare il render."})
        return queued


def stop() -> None:
    with _lock:
        if _process:
            try:
                _process.kill()
            except OSError:
                pass
