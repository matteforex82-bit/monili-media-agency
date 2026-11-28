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


def guide_track(
    destination: Path, duration_ms: int, cuts_ms: list[int], bpm: int = 100,
    strong_ms: tuple[int, ...] = (),
) -> None:
    """Base sintetica con pulsazione e accenti editoriali indipendenti dal battito."""
    beat_ms = 60_000 / bpm
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

    for index in range(math.ceil(duration_ms / beat_ms)):
        accent(round(index * beat_ms), 64 if index % 4 == 0 else 84, 105, 0.21)
        accent(round((index + 0.5) * beat_ms), 680, 35, 0.06)
    for cut in cuts_ms:
        accent(cut, 390, 150, 0.13)
    for cut in strong_ms:
        accent(cut, 310, 185, 0.23)
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
        detail = any(term in framing for term in ("macro", "dettaglio", "primo piano", "close-up"))
        moving = any(term in camera for term in ("push", "dolly", "avvicin", "carrell", "scorr"))
        profile = {
            "scale": "macro" if "macro" in framing else "detail" if detail else "look",
            "reference_photo": int(reference[1]) if reference else 1,
            "focus_x": 0.5,
            "focus_y": 0.5,
            "lens_mm": 85 if detail else 50,
            "yaw_deg": 0,
            "pitch_deg": 0,
            "motion": "push" if moving else "fixed",
            "light": "texture" if detail else "soft",
            "key_side": "left",
            "accent": "soft" if result else "none",
            **(shot.get("design") or {}),
        }
        result.append({**profile, "end_ms": shot["end_ms"], "framing": shot["framing"]})
    frames = [round(shot["end_ms"] * FPS / 1000) for shot in result]
    if frames != sorted(set(frames)) or not frames or frames[0] < 1:
        raise ValueError("Alcuni tagli sono troppo ravvicinati per la timeline di Blender.")
    return result


KEYWORDS = (
    ("Anello", r"anell"), ("Orecchini", r"orecchin"), ("Bracciale", r"braccial"), ("Collana", r"collan|ciondol|girocoll"),
    ("Cavigliera", r"cavigli"), ("Pochette", r"pochette|clutch"), ("Borsa", r"bors|zain|tracoll"),
    ("Cintura", r"cintur"), ("Sciarpa, stola o scialle", r"sciarp|stola|scial"), ("Foulard o bandana", r"foulard|bandana"),
    ("Cappello", r"cappell|basco|berretto"), ("Giacca o gilet", r"giacc|gilet|blazer|cappott"),
    ("Outfit completo", r"outfit|completo"), ("Capo singolo", r"vestit|abito|gonn|camicia|top|maglia|pantalon"),
)


def template_for(draft: dict) -> str:
    """La scheda del prodotto: quella riconosciuta dalle foto, altrimenti dedotta dal nome e dal brief."""
    recognised = (draft.get("recognition") or {}).get("template")
    if recognised:
        return recognised
    text = f"{draft.get('product', '')} {draft.get('brief', '')}".casefold()
    for template, pattern in KEYWORDS:
        if re.search(pattern, text):
            return template
    return "Regia libera"


def score_accents(shots: list[dict]) -> list[tuple[int, str]]:
    starts = [0, *(shot["end_ms"] for shot in shots[:-1])]
    return [(start, shot["accent"]) for start, shot in zip(starts, shots) if shot["accent"] != "none"]


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
