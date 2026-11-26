"""Avvio locale di Blender e preparazione della traccia guida."""

from array import array
import json
import math
import os
from pathlib import Path
import shutil
import re
import subprocess
import sys
import wave

FPS = 30
SCRIPT = Path(__file__).resolve().parent / "scripts" / "build_reel_scene.py"


def executable() -> str | None:
    explicit = os.environ.get("BLENDER_BIN", "").strip().strip('"')
    if explicit:
        return shutil.which(explicit)
    installed = shutil.which("blender")
    if installed:
        return installed
    if sys.platform == "win32":
        program_files = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        candidates = sorted((program_files / "Blender Foundation").glob("Blender */blender.exe"), reverse=True)
        if candidates:
            return str(candidates[0])
    elif sys.platform == "darwin":
        app = Path("/Applications/Blender.app/Contents/MacOS/Blender")
        if app.is_file():
            return str(app)
    return None


def guide_track(destination: Path, duration_ms: int, cuts_ms: list[int]) -> None:
    """Una base sintetica originale a 100 BPM, con accenti sui tagli."""
    rate = 24000
    samples = [0.0] * (duration_ms * rate // 1000)

    def accent(at_ms: int, frequency: float, length_ms: int, gain: float) -> None:
        start = at_ms * rate // 1000
        length = length_ms * rate // 1000
        if start >= len(samples):
            return
        for index in range(min(length, len(samples) - start)):
            t = index / rate
            envelope = min(index / 80, 1) * (1 - index / length) ** 2
            samples[start + index] += gain * envelope * math.sin(2 * math.pi * frequency * t)

    for beat in range(0, duration_ms, 600):
        accent(beat, 84 if beat % 2400 else 64, 105, 0.21)
        accent(beat + 300, 680, 35, 0.06)
    for cut in cuts_ms:
        accent(cut, 390, 150, 0.13)
    signal = array("h", (round(max(-1, min(1, value)) * 32767) for value in samples))
    if sys.byteorder != "little":
        signal.byteswap()
    with wave.open(str(destination), "wb") as wav:
        wav.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        wav.writeframes(signal.tobytes())


def shot_settings(shots: list[dict]) -> list[dict]:
    result = []
    for shot in shots:
        framing = shot["framing"].casefold()
        camera = shot["camera"].casefold()
        description = " ".join(str(shot.get(key, "")) for key in ("framing", "camera", "action"))
        reference = re.search(r"\bfoto\s*(?:n[.°]?\s*)?([1-3])\b", description, flags=re.IGNORECASE)
        result.append({
            "end_ms": shot["end_ms"],
            "framing": shot["framing"],
            "detail": any(term in framing for term in ("macro", "dettaglio", "primo piano", "close-up")),
            "move": any(term in camera for term in ("push", "dolly", "avvicin", "carrell", "scorr")),
            "reference": int(reference[1]) - 1 if reference else 0,
        })
    frames = [round(shot["end_ms"] * FPS / 1000) for shot in result]
    if frames != sorted(set(frames)) or not frames or frames[0] < 1:
        raise ValueError("Alcuni tagli sono troppo ravvicinati per la timeline di Blender.")
    return result


def build(binary: str, destination: Path, specification: dict) -> None:
    spec = destination.parent / "regia.json"
    spec.write_text(json.dumps(specification, ensure_ascii=False), encoding="utf-8")
    completed = subprocess.run(
        [binary, "--background", "--factory-startup", "--disable-autoexec",
         "--python-exit-code", "1", "--python", str(SCRIPT), "--", str(spec), str(destination)],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    if completed.returncode or not destination.is_file():
        raise RuntimeError("Blender non è riuscito a creare la scena.")


def open_scene(binary: str, path: Path) -> None:
    options = {}
    if sys.platform == "win32":
        options["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        [binary, "--disable-autoexec", str(path)],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        **options,
    )
