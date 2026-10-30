"""
reel_studio.py - MONILI REEL STUDIO
Pipeline video-first: foto prodotto (+ clip reali opzionali) -> storyboard approvabile
-> fotogrammi chiave fedeli al prodotto -> video Higgsfield -> montaggio 9:16 -> testi.

Stati reel: planning -> storyboard_ready -> rendering -> done | error
Ogni reel vive in OUTPUT_ROOT/reels/<id>/ con reel.json come unica fonte di verita.
"""

import json
import os
import shutil
import subprocess
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

import casting
import higgsfield_client as hf
import reel_kit as kit
import results_log
import skills_loader as skills
from main import (
    BRAND,
    MEMORY_ROOT,
    OUTPUT_ROOT,
    SEASON,
    agent_analisi,
    extract_json_object,
    generate_text_with_openrouter,
    select_openrouter_image_model,
    select_openrouter_text_model,
)

REELS_ROOT = OUTPUT_ROOT / "reels"
REELS_ROOT.mkdir(parents=True, exist_ok=True)

FRAME_SIZE = (1080, 1920)
FPS = 30
TRANSITION_SECONDS = 0.35
MAX_PARALLEL_SHOTS = int(os.environ.get("REEL_MAX_PARALLEL_SHOTS", "3"))
KEYFRAME_ATTEMPTS = max(1, int(os.environ.get("REEL_KEYFRAME_ATTEMPTS", "3")))
VIDEO_TIMEOUT_SECONDS = int(os.environ.get("HIGGSFIELD_VIDEO_TIMEOUT_SECONDS", "900"))

FORMATS = {
    "reel": {"label": "Reel 9:16", "min_seconds": 8, "max_seconds": 20, "default_seconds": 12, "shots": "3-5"},
    "story": {"label": "Story video 9:16", "min_seconds": 5, "max_seconds": 10, "default_seconds": 7, "shots": "1-2"},
}
TRANSITIONS = {
    "cut": ("fade", 0.04),
    "dissolve": ("dissolve", TRANSITION_SECONDS),
    "fade": ("fade", TRANSITION_SECONDS),
    "slide": ("slideleft", TRANSITION_SECONDS),
    "slide_up": ("smoothup", TRANSITION_SECONDS),
    "zoom": ("zoomin", TRANSITION_SECONDS),
    "wipe": ("wipeleft", TRANSITION_SECONDS),
    "circle": ("circleopen", TRANSITION_SECONDS),
}
SHOT_PURPOSES = ["hook", "dettaglio", "indossato", "lifestyle", "outfit", "cta"]

# Stime di costo usate quando la stima Higgsfield non e disponibile (USD).
FALLBACK_USD_PER_SECOND = {
    "kling-3-std": float(os.environ.get("HF_FALLBACK_USD_PER_SEC_KLING_STD", "0.10")),
    "kling-3-pro": float(os.environ.get("HF_FALLBACK_USD_PER_SEC_KLING_PRO", "0.16")),
    "seedance-2.5": float(os.environ.get("HF_FALLBACK_USD_PER_SEC_SEEDANCE", "0.12")),
}
KEYFRAME_USD = {
    "openai/gpt-5.4-image-2": 0.12,
    "google/gemini-3-pro-image": 0.14,
    "openai-direct/gpt-image-2.5-flare": 0.12,
    "openai-direct/gpt-image-2.5-sunburst": 0.20,
    "openai-direct/gpt-image-2": 0.12,
}
KEYFRAME_USD_DEFAULT = 0.07
TEXT_USD_ESTIMATE = 0.10
EUR_PER_USD = float(os.environ.get("EUR_PER_USD", "0.88"))
REEL_BUDGET_EUR = float(os.environ.get("REEL_BUDGET_EUR", "2.0"))

PRODUCT_FIDELITY_RULES = (
    "The product must stay IDENTICAL to the reference photo: same shape, same stones and their exact cut, "
    "same colors, same metal finish, same proportions and number of elements. Do not redesign, simplify or add details."
)
MOTION_FIDELITY_RULES = (
    "Slow, smooth, elegant camera motion. The jewelry/product keeps its exact shape, stones and details in every frame, "
    "no morphing, no melting, no extra elements, no text overlays, no logos."
)

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


# ── STATO ────────────────────────────────────────────────────────────────────

def select_keyframe_model(requested: str = "") -> str:
    """OpenRouter come prima; con OPENAI_API_KEY si possono usare (e diventano default) i modelli OpenAI diretti."""
    requested = (requested or "").strip()
    if requested in kit.OPENAI_DIRECT_MODELS:
        return requested if kit.openai_configured() else select_openrouter_image_model("")
    if not requested and kit.openai_configured() and os.environ.get("REEL_PREFER_OPENAI_DIRECT", "1") != "0":
        return kit.OPENAI_DEFAULT_KEYFRAME_MODEL
    return select_openrouter_image_model(requested)


def poster_model(keyframe_model: str) -> str:
    if keyframe_model.startswith(kit.OPENAI_DIRECT_PREFIX):
        return kit.OPENAI_DEFAULT_POSTER_MODEL
    return keyframe_model


def _lock(reel_id: str) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(reel_id, threading.Lock())


def reel_dir(reel_id: str) -> Path:
    return REELS_ROOT / reel_id


def _state_path(reel_id: str) -> Path:
    return reel_dir(reel_id) / "reel.json"


def rel(path: Path) -> str:
    """Percorso relativo a OUTPUT_ROOT, servito dal backend sotto /files/."""
    return path.resolve().relative_to(OUTPUT_ROOT.resolve()).as_posix()


def load_state(reel_id: str) -> dict | None:
    path = _state_path(reel_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_state(state: dict) -> None:
    path = _state_path(state["id"])
    state["updated_at"] = datetime.now().isoformat()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def _mutate(reel_id: str, fn) -> dict:
    with _lock(reel_id):
        state = load_state(reel_id) or {}
        fn(state)
        save_state(state)
        return state


def log(reel_id: str, agent: str, msg: str, kind: str = "info") -> None:
    line = {"time": datetime.now().strftime("%H:%M:%S"), "agent": agent, "msg": msg, "type": kind}
    print(f"[REEL {reel_id}] [{agent}] {msg}", flush=True)

    def _append(state: dict):
        logs = state.setdefault("logs", [])
        logs.append(line)
        del logs[:-400]

    _mutate(reel_id, _append)


def list_reels(limit: int = 20) -> list[dict]:
    items = []
    for path in sorted(REELS_ROOT.glob("*/reel.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        items.append(
            {
                "id": state.get("id"),
                "status": state.get("status"),
                "format": state.get("format"),
                "title": (state.get("storyboard") or {}).get("title") or state.get("brief", "")[:60],
                "created_at": state.get("created_at"),
                "final_video": (state.get("results") or {}).get("final_video"),
                "cover": (state.get("results") or {}).get("cover"),
            }
        )
    return items


def recover_interrupted() -> int:
    """Al riavvio del backend i lavori in corso sono persi: li segna come interrotti."""
    count = 0
    for path in REELS_ROOT.glob("*/reel.json"):
        reel_id = path.parent.name
        state = load_state(reel_id)
        if not state or state.get("status") not in ("planning", "rendering"):
            continue
        was_rendering = state["status"] == "rendering" and state.get("storyboard")

        def _mark(s: dict, was_rendering=was_rendering):
            s["status"] = "storyboard_ready" if was_rendering else "error"
            s["error"] = "Lavoro interrotto dal riavvio del server: puoi rilanciarlo."
            s.setdefault("logs", []).append(
                {"time": datetime.now().strftime("%H:%M:%S"), "agent": "SISTEMA", "msg": s["error"], "type": "warn"}
            )

        _mutate(reel_id, _mark)
        count += 1
    return count


def new_reel_id() -> str:
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"


def create_reel(
    reel_id: str,
    photos: list[Path],
    clips: list[Path],
    brief: str,
    fmt: str,
    target_seconds: int,
    video_model: str,
    keyframe_model: str,
    text_model: str,
    recipe: str = "",
    poster_cover: bool = True,
    woman: str = "",
    woman_reference: Path | None = None,
    scheda_run_id: str = "",
) -> dict:
    """woman / woman_reference: la donna della Scheda pezzo dello stesso pezzo (descrizione e foto indossata).
    Senza, la inventa il regista nello storyboard: una per pezzo, mai due donne diverse con lo stesso pezzo."""
    fmt = fmt if fmt in FORMATS else "reel"
    spec = FORMATS[fmt]
    target_seconds = max(spec["min_seconds"], min(spec["max_seconds"], int(target_seconds or spec["default_seconds"])))
    clip_infos = []
    for path in clips:
        try:
            duration = probe_duration(path)
        except Exception:
            duration = 0.0
        clip_infos.append({"src": rel(path), "duration": round(duration, 2)})

    state = {
        "id": reel_id,
        "status": "planning",
        "created_at": datetime.now().isoformat(),
        "brief": brief,
        "format": fmt,
        "recipe": kit.select_recipe(recipe),
        "woman": woman or None,
        "woman_reference": rel(woman_reference) if woman_reference else None,
        "scheda_run_id": scheda_run_id or None,
        "poster_cover": bool(poster_cover),
        "target_seconds": target_seconds,
        "video_model": hf.select_video_model(video_model),
        "keyframe_model": select_keyframe_model(keyframe_model),
        "text_model": select_openrouter_text_model(text_model),
        "higgsfield_configured": hf.is_configured(),
        "photos": [rel(p) for p in photos],
        "clips": clip_infos,
        "analysis": "",
        "storyboard": None,
        "estimate": None,
        "results": {},
        "logs": [],
        "error": None,
    }
    with _lock(reel_id):
        save_state(state)
    return state


def _abs(relative: str) -> Path:
    return OUTPUT_ROOT / relative


def _fail(reel_id: str, agent: str, exc: Exception) -> None:
    log(reel_id, agent, f"ERRORE: {exc}", "warn")
    print(traceback.format_exc(), flush=True)

    def _set(state: dict):
        state["status"] = "error"
        state["error"] = str(exc)

    _mutate(reel_id, _set)


# ── FFMPEG ───────────────────────────────────────────────────────────────────

def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        found = shutil.which("ffmpeg")
        if not found:
            raise RuntimeError("ffmpeg non disponibile: installa imageio-ffmpeg (pip install -r requirements.txt).")
        return found


def _run_ffmpeg(args: list[str]) -> None:
    cmd = [ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg: {proc.stderr.strip()[-600:]}")


def probe_duration(path: Path) -> float:
    import imageio_ffmpeg

    _frames, seconds = imageio_ffmpeg.count_frames_and_secs(str(path))
    return float(seconds)


VERTICAL_FILTER = (
    f"scale={FRAME_SIZE[0]}:{FRAME_SIZE[1]}:force_original_aspect_ratio=increase,"
    f"crop={FRAME_SIZE[0]}:{FRAME_SIZE[1]},fps={FPS},format=yuv420p,setsar=1"
)
X264_ARGS = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-movflags", "+faststart"]


def normalize_clip(source: Path, destination: Path, seconds: float, start: float = 0.0) -> Path:
    """Porta qualsiasi clip a 1080x1920, 30fps, senza audio, durata esatta (allunga l'ultimo frame se serve)."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    vf = f"{VERTICAL_FILTER},tpad=stop_mode=clone:stop_duration={seconds:.2f}"
    _run_ffmpeg(["-ss", f"{max(0.0, start):.2f}", "-i", str(source), "-t", f"{seconds:.2f}", "-vf", vf, "-an", *X264_ARGS, str(destination)])
    try:
        valid = probe_duration(destination) > 0
    except Exception:
        valid = False
    if not valid:
        raise RuntimeError(f"Clip {source.name}: nessun fotogramma utile dal secondo {start:.1f} (controlla 'Parti dal secondo').")
    return destination


def ken_burns_clip(image: Path, destination: Path, seconds: float, zoom_in: bool = True) -> Path:
    """Anteprima senza Higgsfield: lento zoom sul fotogramma chiave."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    frames = max(1, int(round(seconds * FPS)))
    step = 0.10 / frames
    zoom = f"min(1+{step:.6f}*on,1.10)" if zoom_in else f"max(1.10-{step:.6f}*on,1.0)"
    vf = (
        f"scale={FRAME_SIZE[0] * 2}:{FRAME_SIZE[1] * 2},"
        f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={FRAME_SIZE[0]}x{FRAME_SIZE[1]}:fps={FPS},"
        "format=yuv420p,setsar=1"
    )
    _run_ffmpeg(["-loop", "1", "-i", str(image), "-t", f"{seconds:.2f}", "-vf", vf, "-an", *X264_ARGS, str(destination)])
    return destination


def assemble(clips: list[tuple[Path, float]], transitions: list[str], destination: Path) -> Path:
    """Unisce le clip normalizzate con transizioni xfade. transitions[i] = transizione tra clip i e i+1."""
    if not clips:
        raise RuntimeError("Nessuna clip da montare.")
    if len(clips) == 1:
        shutil.copyfile(clips[0][0], destination)
        return destination

    inputs: list[str] = []
    for path, _ in clips:
        inputs.extend(["-i", str(path)])
    parts = []
    current = "[0:v]"
    length = clips[0][1]
    for index in range(1, len(clips)):
        name, duration = TRANSITIONS.get(transitions[index - 1] if index - 1 < len(transitions) else "dissolve", TRANSITIONS["dissolve"])
        duration = min(duration, clips[index][1] / 2, length / 2)
        offset = max(0.0, length - duration)
        label = f"[v{index}]"
        parts.append(f"{current}[{index}:v]xfade=transition={name}:duration={duration:.2f}:offset={offset:.2f}{label}")
        current = label
        length = length + clips[index][1] - duration
    _run_ffmpeg([*inputs, "-filter_complex", ";".join(parts), "-map", current, "-an", *X264_ARGS, str(destination)])
    return destination


def make_cover(source_image: Path, destination: Path) -> Path:
    with Image.open(source_image) as img:
        cover = ImageOps.fit(img.convert("RGB"), FRAME_SIZE, Image.LANCZOS)
        cover.save(destination, "JPEG", quality=88, optimize=True, progressive=True)
    return destination


# Versione leggera per il sito vetrina: Vercel non accetta richieste sopra 4,5 MB, quindi
# il video 1080x1920 del Reel Studio non può andare così com'è. Limiti uguali a quelli
# del sito (apps/web/src/lib/reel.ts): se cambiano di là, cambiano anche qui.
WEB_REEL_MAX_VIDEO_BYTES = 4_000_000
WEB_REEL_MAX_POSTER_BYTES = 600_000
WEB_REEL_MAX_SECONDS = 60
# (larghezza, altezza, crf): dal migliore al più leggero, si ferma al primo che sta nel limite.
WEB_REEL_STEPS = [(720, 1280, 26), (720, 1280, 30), (720, 1280, 34), (540, 960, 32), (540, 960, 36)]


def make_web_video(source: Path, destination: Path, max_bytes: int = WEB_REEL_MAX_VIDEO_BYTES) -> Path:
    """MP4 9:16 leggero e senza audio, sotto `max_bytes`. Errore chiaro se non ci sta."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if probe_duration(source) > WEB_REEL_MAX_SECONDS:
        raise RuntimeError(f"Reel troppo lungo per il sito (massimo {WEB_REEL_MAX_SECONDS} secondi).")
    for width, height, crf in WEB_REEL_STEPS:
        vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps=30,format=yuv420p,setsar=1"
        _run_ffmpeg([
            "-i", str(source), "-vf", vf, "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
            "-maxrate", "2M", "-bufsize", "4M", "-movflags", "+faststart", str(destination),
        ])
        if destination.stat().st_size <= max_bytes:
            return destination
    raise RuntimeError(
        f"Il Reel resta sopra {max_bytes / 1_000_000:.0f} MB anche alla qualità minima: accorcialo e riprova."
    )


def make_web_poster(source: Path, destination: Path, max_bytes: int = WEB_REEL_MAX_POSTER_BYTES) -> Path:
    """Copertina JPEG 540x960 sotto `max_bytes`."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as img:
        cover = ImageOps.fit(img.convert("RGB"), (540, 960), Image.LANCZOS)
    for quality in (82, 72, 62, 50, 40):
        cover.save(destination, "JPEG", quality=quality, optimize=True, progressive=True)
        if destination.stat().st_size <= max_bytes:
            return destination
    raise RuntimeError("Copertina troppo pesante per il sito.")


# ── STORYBOARD ───────────────────────────────────────────────────────────────

def _performance_hints() -> str:
    path = MEMORY_ROOT / "performance_log.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    hints = []
    top_hashtags = (data.get("hashtag_performance") or {}).get("top_reach") or []
    if top_hashtags:
        hints.append(f"Hashtag con piu reach storico: {', '.join(map(str, top_hashtags[:10]))}")
    best_caption = (data.get("caption_performance") or {}).get("variante_migliore_storica")
    if best_caption:
        hints.append(f"Variante caption migliore storica: {best_caption}")
    insights = data.get("insight_brand") or []
    if insights:
        hints.append("Insight: " + "; ".join(map(str, insights[:5])))
    measured = results_log.prompt_hints()
    if measured:
        hints.append(measured)
    return "\n".join(hints)


def _woman(state: dict) -> str:
    """La donna di questo Reel: quella della Scheda pezzo o quella inventata dal regista, uguale in ogni scena."""
    return state.get("woman") or casting.FALLBACK_WOMAN


def _woman_block(state: dict) -> str:
    same_woman = "Usa use_model true nelle inquadrature dove compare lei: in tutto il Reel e sempre la stessa donna."
    if state.get("woman"):
        return f"DONNA DI QUESTO PEZZO (gia scelta nella Scheda pezzo, non cambiarla): {state['woman']}\n{same_woman}"
    lines = (
        f"LA DONNA DI QUESTO REEL: la inventi tu e la descrivi nel campo \"woman\". {casting.woman_guide()}",
        same_woman,
        casting.avoid_block("DONNE GIA USATE DI RECENTE", casting.recent_women()),
    )
    return "\n".join(line for line in lines if line)


def agent_storyboard(state: dict, photo: Path) -> dict:
    fmt = FORMATS[state["format"]]
    clips = state.get("clips") or []
    clip_lines = "\n".join(f"- clip_index {i}: durata {c['duration']}s" for i, c in enumerate(clips)) or "- nessuna clip reale caricata"
    n_photos = len(state.get("photos") or [])
    hints = _performance_hints()
    prompt = f"""Sei il direttore creativo video di I Monili Ravenna: crei Reel e Story video Instagram che fermano lo scroll.
{BRAND}

ANALISI PRODOTTO:
{state.get('analysis', '')[:2500]}

BRIEF: {state.get('brief') or 'nessuno - decidi tu'}
{('COSA HA FUNZIONATO FINORA (usalo per decidere hook e struttura):' + chr(10) + hints) if hints else ''}
FORMATO: {fmt['label']} - durata totale circa {state['target_seconds']} secondi, {fmt['shots']} inquadrature.
FOTO PRODOTTO DISPONIBILI: {n_photos} (photo_index da 0 a {max(0, n_photos - 1)})
CLIP REALI CARICATE DALL'UTENTE:
{clip_lines}

{kit.recipe_prompt_block(state.get('recipe', ''))}

{_woman_block(state)}

LIBERTA CREATIVA: luogo, persone, pose, abiti e accessori li inventi tu, adatti al pezzo e allo stile colorato,
artigianale e boho del negozio. Sorprendi: non ripartire sempre dal solito bancone con luce calda.
{casting.avoid_block("SCENE DEGLI ULTIMI REEL", casting.recent_scenes(exclude_reel=state.get("id", "")))}
COSE DA NON MOSTRARE MAI: {"; ".join(casting.never_show()) or "nessuna"}

REGOLE:
- I primi 1.5 secondi sono un HOOK visivo forte (movimento, luce che colpisce le pietre, gesto).
- Se ci sono clip reali usale (source "clip") dove rendono di piu: l'autenticita del negozio vende.
- Le inquadrature AI partono da un fotogramma chiave generato dalla foto reale: il prodotto deve restare identico.
- Gioielli piccoli: preferisci movimenti lenti (slow push-in, orbit leggero, rack focus), evita rotazioni veloci.
- Luce naturale e bella, adatta alla scena che inventi.
- Ogni inquadratura AI dura 3-6 secondi; l'ultima chiude SEMPRE con invito concreto: "Scrivici, te lo mettiamo da parte" o "Ti aspettiamo in centro a Ravenna".
- Stile: autentico ed elegante, colori e sfondi che fanno risaltare il prodotto. Mai effetti pacchiani.
- on_screen_text in italiano, max 6 parole, tono da amica.
- keyframe_prompt_en e motion_prompt_en in inglese, concreti e visivi.
- keyframe_mode "original_photo" = usa la foto reale cosi com'e (massima fedelta, utile per il dettaglio prodotto).
- COERENZA AL 100%: tutte le inquadrature AI avvengono nella STESSA scena descritta in scene_bible (stesso luogo,
  stessa luce, stessa palette, stessa donna con gli stessi abiti). Cambiano solo inquadratura, distanza e azione.
- end_on_product true = la scena si chiude sulla foto vera del prodotto (usalo per dettaglio e chiusura).

Rispondi SOLO con JSON valido:
{{
  "title": "titolo breve interno",
  "concept": "idea in una frase",
  "hook": "cosa succede nei primi 1.5s",
  "music_mood": "mood musicale da cercare tra gli audio di tendenza Instagram",
  "cover_text": "testo copertina max 5 parole",
  "woman": "solo se la donna la inventi tu: in inglese, eta, corporatura, viso, capelli e stile; altrimenti vuoto",
  "scene_bible": "UNA sola scena coerente per tutto il video, in inglese: luogo preciso, superficie, sfondo, luce (direzione, colore, ora), palette colori, e se c'e la donna: capelli, trucco e abiti esatti",
  "shots": [
    {{
      "purpose": "hook|dettaglio|indossato|lifestyle|outfit|cta",
      "source": "ai|clip",
      "clip_index": null,
      "clip_start": 0,
      "photo_index": 0,
      "keyframe_mode": "ai|original_photo",
      "use_model": false,
      "end_on_product": false,
      "duration": 4,
      "camera": "es. slow push-in macro",
      "angle": "es. 45 gradi dall'alto",
      "lighting": "es. golden hour laterale calda",
      "action": "cosa succede in scena",
      "transition_out": "cut|dissolve|fade|slide|slide_up|zoom|wipe|circle",
      "on_screen_text": "testo breve o vuoto",
      "keyframe_prompt_en": "vertical 9:16 scene description for the first frame",
      "motion_prompt_en": "camera and subject motion for the video model"
    }}
  ]
}}"""
    raw = generate_text_with_openrouter(state["api_key"], state["text_model"], prompt, image_path=photo, max_tokens=2600)
    storyboard = extract_json_object(raw)
    if not storyboard.get("shots"):
        raise RuntimeError(f"Storyboard non valido dal modello testo: {raw[:300]}")
    return storyboard


def normalize_storyboard(state: dict, storyboard: dict) -> dict:
    n_photos = max(1, len(state.get("photos") or []))
    clips = state.get("clips") or []
    video_model = state.get("video_model") or hf.DEFAULT_VIDEO_MODEL
    shots_in = storyboard.get("shots") if isinstance(storyboard.get("shots"), list) else []
    shots = []
    for index, raw in enumerate(shots_in[:6]):
        if not isinstance(raw, dict):
            continue
        source = "clip" if raw.get("source") == "clip" else "ai"
        clip_index = raw.get("clip_index")
        try:
            clip_index = int(clip_index) if clip_index is not None else None
        except (TypeError, ValueError):
            clip_index = None
        if source == "clip" and (clip_index is None or not 0 <= clip_index < len(clips)):
            source, clip_index = "ai", None
        try:
            duration = float(raw.get("duration") or 4)
        except (TypeError, ValueError):
            duration = 4.0
        if source == "ai":
            duration = float(hf.clamp_duration(video_model, int(round(duration))))
        else:
            duration = max(1.0, min(duration, 10.0))
        try:
            photo_index = int(raw.get("photo_index") or 0)
        except (TypeError, ValueError):
            photo_index = 0
        try:
            clip_start = max(0.0, float(raw.get("clip_start") or 0))
        except (TypeError, ValueError):
            clip_start = 0.0
        if source == "clip":
            clip_length = float(clips[clip_index].get("duration") or 0)
            if clip_length > 0:
                # almeno 1 secondo utile dopo il punto di partenza
                clip_start = min(clip_start, max(0.0, clip_length - 1.0))
                duration = min(duration, clip_length - clip_start)
        transition = str(raw.get("transition_out") or "dissolve").strip().lower()
        shots.append(
            {
                "id": f"shot_{index + 1}",
                "purpose": str(raw.get("purpose") or "lifestyle").strip().lower(),
                "source": source,
                "clip_index": clip_index,
                "clip_start": clip_start,
                "photo_index": min(max(photo_index, 0), n_photos - 1),
                "keyframe_mode": "original_photo" if raw.get("keyframe_mode") == "original_photo" else "ai",
                "use_model": raw.get("use_model") is True or str(raw.get("use_model")).lower() == "true",
                "end_on_product": raw.get("end_on_product") is True or str(raw.get("end_on_product")).lower() == "true",
                "duration": duration,
                "camera": str(raw.get("camera") or "").strip(),
                "angle": str(raw.get("angle") or "").strip(),
                "lighting": str(raw.get("lighting") or "").strip(),
                "action": str(raw.get("action") or "").strip(),
                "transition_out": transition if transition in TRANSITIONS else "dissolve",
                "on_screen_text": str(raw.get("on_screen_text") or "").strip()[:80],
                "keyframe_prompt_en": str(raw.get("keyframe_prompt_en") or "").strip(),
                "motion_prompt_en": str(raw.get("motion_prompt_en") or "").strip(),
            }
        )
    if not shots:
        raise RuntimeError("Lo storyboard non contiene inquadrature valide.")
    return {
        "title": str(storyboard.get("title") or "Reel Monili").strip(),
        "concept": str(storyboard.get("concept") or "").strip(),
        "hook": str(storyboard.get("hook") or "").strip(),
        "music_mood": str(storyboard.get("music_mood") or "").strip(),
        "cover_text": str(storyboard.get("cover_text") or "").strip(),
        "scene_bible": str(storyboard.get("scene_bible") or "").strip()[:1200],
        "shots": shots,
    }


# ── STIMA COSTI ──────────────────────────────────────────────────────────────

def estimate_reel(state: dict) -> dict:
    storyboard = state.get("storyboard") or {}
    video_model = state.get("video_model") or hf.DEFAULT_VIDEO_MODEL
    endpoint = hf.VIDEO_MODELS[video_model]["endpoint"]
    lines = []
    total_usd = TEXT_USD_ESTIMATE
    exact = hf.is_configured()
    for shot in storyboard.get("shots", []):
        if shot["source"] != "ai":
            lines.append({"shot": shot["id"], "label": "Clip reale", "usd": 0.0})
            continue
        if shot["keyframe_mode"] == "ai":
            keyframe_usd = KEYFRAME_USD.get(state.get("keyframe_model", ""), KEYFRAME_USD_DEFAULT) + kit.QA_USD
            label = "Fotogramma AI" + (" con la donna del Reel" if shot.get("use_model") else "") + " + controllo qualita"
            lines.append({"shot": shot["id"], "label": label, "usd": keyframe_usd})
            total_usd += keyframe_usd
        video_usd = None
        credits = None
        if hf.is_configured():
            try:
                body = hf.build_video_body(video_model, "https://example.com/keyframe.jpg", shot["motion_prompt_en"], int(shot["duration"]))
                result = hf.estimate(endpoint, body)
                video_usd, credits = result["usd"], result["credits"]
            except Exception:
                exact = False
        if video_usd is None:
            video_usd = FALLBACK_USD_PER_SECOND.get(video_model, 0.12) * shot["duration"]
        lines.append(
            {
                "shot": shot["id"],
                "label": f"Video {hf.VIDEO_MODELS[video_model]['label']} {int(shot['duration'])}s",
                "usd": round(video_usd, 3),
                "credits": credits,
            }
        )
        total_usd += video_usd
    if state.get("poster_cover", True):
        poster_usd = KEYFRAME_USD.get(poster_model(state.get("keyframe_model", "")), kit.POSTER_USD) + kit.QA_USD
        lines.append({"shot": "-", "label": "Copertina poster", "usd": poster_usd})
        total_usd += poster_usd
    lines.append({"shot": "-", "label": "Testi e regia AI", "usd": TEXT_USD_ESTIMATE})
    for line in lines:
        line["eur"] = round(line["usd"] * EUR_PER_USD, 2)
    total_eur = round(total_usd * EUR_PER_USD, 2)
    return {
        "exact": exact,
        "lines": lines,
        "total_usd": round(total_usd, 2),
        "total_eur": total_eur,
        "budget_eur": REEL_BUDGET_EUR,
        "over_budget": total_eur > REEL_BUDGET_EUR,
        "preview_mode": not hf.is_configured(),
        "note": (
            "Stima ufficiale Higgsfield."
            if exact
            else "Stima indicativa: diventa precisa quando colleghi la API key Higgsfield."
        ),
    }


# ── FASE 1: PIANIFICAZIONE ───────────────────────────────────────────────────

def plan_reel(reel_id: str, api_key: str) -> None:
    try:
        state = load_state(reel_id)
        photo = _abs(state["photos"][0])
        log(reel_id, "ANALISTA", "Analisi del prodotto dalla foto...")
        analysis = agent_analisi(state["text_model"], api_key, photo, state.get("brief", ""))
        _mutate(reel_id, lambda s: s.update({"analysis": analysis}))
        log(reel_id, "ANALISTA", "Prodotto analizzato", "success")

        log(reel_id, "REGISTA", "Creo lo storyboard: hook, inquadrature, luce, transizioni...")
        state = load_state(reel_id)
        state["api_key"] = api_key
        raw_storyboard = agent_storyboard(state, photo)
        storyboard = normalize_storyboard(state, raw_storyboard)
        state.pop("api_key", None)
        # La donna inventata dal regista (se il pezzo non ne aveva già una): da qui in poi è lei.
        woman = state.get("woman") or " ".join(str(raw_storyboard.get("woman") or "").split())[:600] or None
        state["storyboard"] = storyboard
        state["estimate"] = estimate_reel(state)
        log(reel_id, "REGISTA", f"Storyboard pronto: {len(storyboard['shots'])} inquadrature", "success")
        log(
            reel_id,
            "PRODUZIONE",
            f"Costo stimato: {state['estimate']['total_eur']:.2f} EUR"
            + (" - SOPRA il budget" if state["estimate"]["over_budget"] else ""),
            "warn" if state["estimate"]["over_budget"] else "data",
        )

        def _ready(s: dict):
            s["storyboard"] = storyboard
            s["woman"] = woman
            s["estimate"] = state["estimate"]
            s["status"] = "storyboard_ready"

        _mutate(reel_id, _ready)
    except Exception as exc:
        _fail(reel_id, "REGISTA", exc)


def update_storyboard(reel_id: str, storyboard: dict, video_model: str = "") -> dict:
    state = load_state(reel_id)
    if not state:
        raise ValueError("Reel non trovato.")
    if state.get("status") not in ("storyboard_ready", "done", "error"):
        raise ValueError("Lo storyboard si puo modificare solo quando la generazione non e in corso.")
    if video_model:
        state["video_model"] = hf.select_video_model(video_model)
    normalized = normalize_storyboard(state, storyboard)
    state["storyboard"] = normalized
    estimate = estimate_reel(state)

    def _apply(s: dict):
        s["storyboard"] = normalized
        s["estimate"] = estimate
        s["video_model"] = state["video_model"]
        if s.get("status") == "error" and s.get("storyboard"):
            s["status"] = "storyboard_ready"
            s["error"] = None

    return _mutate(reel_id, _apply)


# ── FASE 2: PRODUZIONE ───────────────────────────────────────────────────────

def _keyframe(
    state: dict,
    shot: dict,
    api_key: str,
    out_dir: Path,
    anchor: Path | None = None,
) -> tuple[Path, dict | None]:
    """
    Fotogramma chiave 9:16 coerente con prodotto e scena.
    Image 1 = foto reale (verita sul prodotto), Image 2 = la donna gia fotografata con questo pezzo (se il Reel
    parte da una Scheda pezzo), Image 3 = fotogramma guida della scena. Ogni tentativo passa dal controllo
    qualita; se nessuno passa si usa la foto reale.
    """
    reel_id = state["id"]
    photo = _abs(state["photos"][shot["photo_index"]])
    keyframe = out_dir / f"{shot['id']}_keyframe.jpg"
    if shot["keyframe_mode"] == "original_photo":
        make_cover(photo, keyframe)
        return keyframe, {"ok": True, "score": 10, "issues": "", "checked": False, "source": "foto reale"}

    storyboard = state.get("storyboard") or {}
    scene_bible = storyboard.get("scene_bible", "")
    images = [photo]
    image_lines = ["IMAGE 1: the real product photo - the exact piece, it is the truth for shape, stones, colors and metal."]
    model_line = ""
    if shot.get("use_model"):
        model_line = f"WOMAN (the same in the whole Reel, do not change her age, body or face): {_woman(state)}"
        reference = _abs(state["woman_reference"]) if state.get("woman_reference") else None
        if reference and reference.exists():
            images.append(reference)
            image_lines.append(
                f"IMAGE {len(images)}: the same woman, already photographed wearing this piece - she is the model "
                "of this product: keep exactly her face, hair, skin tone and body. Ignore that photo's background."
            )
    if anchor and anchor.exists():
        images.append(anchor)
        image_lines.append(
            f"IMAGE {len(images)}: a previous frame of this same Reel - keep EXACTLY the same location, surfaces, "
            "light direction and color, color grading and (if present) the same woman with the same outfit. "
            "Change only framing, distance and action."
        )
    scene = shot["keyframe_prompt_en"] or shot["action"]
    if scene_bible:
        scene = f"{scene}\nSAME SCENE FOR THE WHOLE REEL: {scene_bible}"
    prompt = skills.fill(
        skills.base_template("fotogramma"),
        images_line="\n".join(image_lines),
        scene=scene,
        angle=shot["angle"] or "eye level",
        lighting=shot["lighting"] or "warm natural window light",
        model_line=model_line,
        skill_notes="\n".join(filter(None, (skills.section(state.get("recipe", ""), "keyframe"), casting.never_line()))),
    )
    qa = None
    for attempt in range(1, KEYFRAME_ATTEMPTS + 1):
        try:
            raw_path = out_dir / f"{shot['id']}_keyframe_raw.png"
            kit.generate_image_multi(api_key, state["keyframe_model"], prompt, images, raw_path, aspect_ratio="9:16")
            make_cover(raw_path, keyframe)
            raw_path.unlink(missing_ok=True)
        except Exception as exc:
            log(reel_id, "FOTOGRAMMI", f"{shot['id']}: fotogramma AI non riuscito ({exc}), uso la foto reale", "warn")
            make_cover(photo, keyframe)
            return keyframe, {"ok": True, "score": None, "issues": "fotogramma AI non riuscito: usata la foto reale", "checked": False, "source": "foto reale"}
        qa = kit.check_keyframe(api_key, state["text_model"], photo, keyframe, scene_anchor=anchor, scene_bible=scene_bible)
        if qa["ok"]:
            log(reel_id, "QUALITA", f"{shot['id']}: prodotto e scena coerenti ({qa.get('score')}/10)", "success")
            qa["source"] = "ai"
            return keyframe, qa
        if not qa.get("checked"):
            log(reel_id, "QUALITA", f"{shot['id']}: {qa.get('issues')} - fotogramma NON verificato, controllalo tu", "warn")
            qa["source"] = "ai"
            return keyframe, qa
        log(
            reel_id,
            "QUALITA",
            f"{shot['id']}: tentativo {attempt}/{KEYFRAME_ATTEMPTS} scartato ({qa.get('score')}/10) - {qa.get('issues') or 'non coerente'}",
            "warn",
        )
        prompt += f"\nPREVIOUS ATTEMPT WAS REJECTED because: {qa.get('issues') or 'product or scene not identical'}. Fix exactly this."
    log(reel_id, "QUALITA", f"{shot['id']}: nessun fotogramma AI abbastanza fedele - uso la foto reale del prodotto", "warn")
    make_cover(photo, keyframe)
    return keyframe, {
        "ok": True,
        "score": qa.get("score") if qa else None,
        "issues": f"AI scartata ({qa.get('issues') if qa else ''}): usata la foto reale",
        "checked": True,
        "source": "foto reale",
        "replaced": True,
    }


def _ai_shot_video(state: dict, shot: dict, keyframe: Path, out_dir: Path) -> tuple[Path, str]:
    reel_id = state["id"]
    final = out_dir / f"{shot['id']}.mp4"
    duration = float(shot["duration"])
    if not hf.is_configured():
        ken_burns_clip(keyframe, final, duration, zoom_in=shot["purpose"] != "cta")
        return final, "preview"

    model_key = state["video_model"]
    motion = skills.fill(
        skills.base_template("movimento") or MOTION_FIDELITY_RULES,
        action=shot["motion_prompt_en"] or shot["action"],
        camera=shot["camera"] or "slow push-in",
        lighting=shot["lighting"] or "warm natural light",
        skill_notes=skills.section(state.get("recipe", ""), "motion"),
    )
    if shot.get("end_on_product"):
        motion += "\nThe shot ends exactly on the final frame provided: the real product photo."
    try:
        image_url = hf.upload_file(keyframe, "image/jpeg")
        last_image_url = ""
        if shot.get("end_on_product"):
            end_frame = make_cover(_abs(state["photos"][shot["photo_index"]]), out_dir / f"{shot['id']}_end.jpg")
            last_image_url = hf.upload_file(end_frame, "image/jpeg")
        body = hf.build_video_body(model_key, image_url, motion, int(duration), last_image_url=last_image_url)
        accepted = hf.submit(hf.VIDEO_MODELS[model_key]["endpoint"], body, idempotency_key=f"{reel_id}-{shot['id']}-{uuid.uuid4().hex[:6]}")
        request_id = accepted.get("request_id", "")
        log(reel_id, "VIDEO", f"{shot['id']}: inviato a {hf.VIDEO_MODELS[model_key]['label']} ({request_id[:8]})", "data")
        result = hf.wait_for_result(
            request_id,
            accepted.get("status_url", ""),
            timeout_seconds=VIDEO_TIMEOUT_SECONDS,
            on_update=lambda status: log(reel_id, "VIDEO", f"{shot['id']}: {status}", "data"),
        )
        if result.get("status") != "completed":
            raise RuntimeError(f"stato finale '{result.get('status')}' {result.get('error') or ''}".strip())
        video_url = (result.get("video") or {}).get("url")
        if not video_url:
            raise RuntimeError("nessun URL video nella risposta")
        raw = hf.download(video_url, out_dir / f"{shot['id']}_raw.mp4")
        normalize_clip(raw, final, duration)
        return final, "higgsfield"
    except Exception as exc:
        log(reel_id, "VIDEO", f"{shot['id']}: video AI non riuscito ({exc}), uso animazione del fotogramma", "warn")
        ken_burns_clip(keyframe, final, duration)
        return final, "fallback"


def _produce_clip_shot(state: dict, shot: dict, out_dir: Path) -> dict:
    reel_id = state["id"]
    clip = state["clips"][shot["clip_index"]]
    source = _abs(clip["src"])
    clip_length = float(clip.get("duration") or 0) or probe_duration(source)
    start = min(shot["clip_start"], max(0.0, clip_length - 1.0))
    duration = max(1.0, min(float(shot["duration"]), clip_length - start))
    final = normalize_clip(source, out_dir / f"{shot['id']}.mp4", duration, start=start)
    log(reel_id, "MONTAGGIO", f"{shot['id']}: clip reale pronta ({duration:.1f}s)", "success")
    return {"id": shot["id"], "video": rel(final), "keyframe": None, "duration": duration, "engine": "clip", "qa": None}


def _anchor_order(shots: list[dict]) -> list[dict]:
    """Prima l'inquadratura che fa da guida alla scena (preferibilmente con la donna), poi le altre."""
    ai_shots = [s for s in shots if s["source"] == "ai" and s["keyframe_mode"] == "ai"]
    if not ai_shots:
        return ai_shots
    lead = next((s for s in ai_shots if s.get("use_model")), ai_shots[0])
    return [lead] + [s for s in ai_shots if s is not lead]


def _make_keyframes(state: dict, api_key: str, out_dir: Path) -> dict[str, tuple[Path, dict | None]]:
    """Fotogrammi in sequenza: il primo AI riuscito diventa la guida della scena per tutti gli altri."""
    shots = state["storyboard"]["shots"]
    results: dict[str, tuple[Path, dict | None]] = {}
    anchor: Path | None = None
    for shot in _anchor_order(shots):
        log(state["id"], "FOTOGRAMMI", f"{shot['id']}: fotogramma ({shot['purpose']})" + (" con guida scena" if anchor else " guida della scena"))
        keyframe, qa = _keyframe(state, shot, api_key, out_dir, anchor=anchor)
        results[shot["id"]] = (keyframe, qa)
        if anchor is None and qa and qa.get("source") == "ai":
            anchor = keyframe
    for shot in shots:
        if shot["source"] == "ai" and shot["id"] not in results:
            results[shot["id"]] = _keyframe(state, shot, api_key, out_dir)
    return results


def _produce_ai_video(state: dict, shot: dict, keyframe: Path, qa: dict | None, out_dir: Path) -> dict:
    video, engine = _ai_shot_video(state, shot, keyframe, out_dir)
    log(state["id"], "VIDEO", f"{shot['id']}: pronto ({engine})", "success")
    return {
        "id": shot["id"],
        "video": rel(video),
        "keyframe": rel(keyframe),
        "duration": float(shot["duration"]),
        "engine": engine,
        "qa": qa,
    }


def agent_copy(state: dict, api_key: str) -> dict:
    storyboard = state.get("storyboard") or {}
    shots_text = "\n".join(f"- {s['purpose']}: {s['action']} | testo: {s['on_screen_text']}" for s in storyboard.get("shots", []))
    hints = _performance_hints()
    prompt = f"""Sei la social media manager di I Monili Ravenna. Scrivi i testi per questo {FORMATS[state['format']]['label']}.
{BRAND}
Stagione: {SEASON}

CONCEPT: {storyboard.get('concept', '')}
HOOK: {storyboard.get('hook', '')}
INQUADRATURE:
{shots_text}

ANALISI PRODOTTO (estratto):
{state.get('analysis', '')[:1500]}
{('DATI PERFORMANCE STORICI:' + chr(10) + hints) if hints else ''}

REGOLE:
{skills.base_template("testi")}
{skills.section(state.get("recipe", ""), "copy")}

Rispondi SOLO con JSON valido:
{{
  "caption": "caption principale completa con a capo",
  "caption_short": "versione breve per story/condivisione",
  "hashtags": ["#imoniliravenna", "#ravenna", "#romagnastyle"],
  "cover_text": "testo copertina max 5 parole",
  "first_comment": "primo commento da pubblicare",
  "story_stickers": ["idea sticker sondaggio/domanda 1", "idea 2"],
  "music_suggestion": "che tipo di audio di tendenza cercare su Instagram",
  "best_slot": "giorno e ora consigliati (Mar/Gio/Sab 18:30-20:00)",
  "alt_text": "descrizione accessibile del video"
}}"""
    raw = generate_text_with_openrouter(api_key, state["text_model"], prompt, max_tokens=1600)
    copy = extract_json_object(raw)
    if not copy:
        copy = {"caption": raw}
    fixed = ["#imoniliravenna", "#ravenna", "#romagnastyle"]
    tags = [str(t).strip() for t in copy.get("hashtags") or [] if str(t).strip()]
    copy["hashtags"] = (fixed + [t for t in tags if t.lower() not in fixed])[:14]
    return copy


def _copy_markdown(state: dict, copy: dict) -> str:
    storyboard = state.get("storyboard") or {}
    lines = [
        f"# {storyboard.get('title', 'Reel Monili')}",
        "",
        f"**Formato:** {FORMATS[state['format']]['label']}  ",
        f"**Orario consigliato:** {copy.get('best_slot', '')}  ",
        f"**Audio:** {copy.get('music_suggestion') or storyboard.get('music_mood', '')}",
        "",
        "## Caption",
        copy.get("caption", ""),
        "",
        " ".join(copy.get("hashtags", [])),
        "",
        "## Primo commento",
        copy.get("first_comment", ""),
        "",
        "## Testi a schermo",
    ]
    for shot in storyboard.get("shots", []):
        if shot.get("on_screen_text"):
            lines.append(f"- {shot['id']} ({shot['purpose']}): {shot['on_screen_text']}")
    lines += ["", "## Copertina", copy.get("cover_text") or storyboard.get("cover_text", ""), "", "## Sticker stories"]
    lines += [f"- {item}" for item in copy.get("story_stickers", [])]
    return "\n".join(lines) + "\n"


def render_reel(reel_id: str, api_key: str) -> None:
    try:
        state = load_state(reel_id)
        storyboard = state["storyboard"]
        out_dir = reel_dir(reel_id) / "shots"
        out_dir.mkdir(parents=True, exist_ok=True)
        mode = "Higgsfield" if hf.is_configured() else "ANTEPRIMA (senza Higgsfield: fotogrammi animati)"
        log(reel_id, "PRODUZIONE", f"Avvio produzione {len(storyboard['shots'])} inquadrature - motore: {mode}")

        keyframes = _make_keyframes(state, api_key, out_dir)
        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_SHOTS) as pool:
            futures = []
            for shot in storyboard["shots"]:
                if shot["source"] == "clip":
                    futures.append(pool.submit(_produce_clip_shot, state, shot, out_dir))
                else:
                    keyframe, qa = keyframes[shot["id"]]
                    futures.append(pool.submit(_produce_ai_video, state, shot, keyframe, qa, out_dir))
            produced = [future.result() for future in futures]

        log(reel_id, "MONTAGGIO", "Montaggio finale 9:16 con transizioni...")
        final_video = reel_dir(reel_id) / f"monili_{state['format']}_{reel_id}.mp4"
        assemble(
            [(_abs(item["video"]), item["duration"]) for item in produced],
            [shot["transition_out"] for shot in storyboard["shots"][:-1]],
            final_video,
        )
        cover_source = next((_abs(item["keyframe"]) for item in produced if item.get("keyframe")), _abs(state["photos"][0]))
        cover_plain = make_cover(cover_source, reel_dir(reel_id) / "cover_foto.jpg")
        cover, cover_qa = cover_plain, None
        cover_text = storyboard.get("cover_text") or storyboard.get("title") or ""
        if state.get("poster_cover", True) and cover_text:
            log(reel_id, "COPERTINA", f"Copertina poster: \"{cover_text}\"...")
            try:
                product_photo = _abs(state["photos"][0])
                cover = kit.make_poster_cover(
                    api_key, poster_model(state["keyframe_model"]), product_photo, cover_text, reel_dir(reel_id) / "cover.jpg",
                    skill_id=state.get("recipe", ""),
                )
                cover_qa = kit.check_keyframe(api_key, state["text_model"], product_photo, cover, expected_text=cover_text)
                if cover_qa["ok"]:
                    log(reel_id, "COPERTINA", "Copertina poster pronta", "success")
                else:
                    log(reel_id, "COPERTINA", f"Copertina da controllare: {cover_qa.get('issues')}", "warn")
            except Exception as exc:
                log(reel_id, "COPERTINA", f"Poster non riuscito ({exc}), uso la copertina foto", "warn")
                cover, cover_qa = cover_plain, None
        log(reel_id, "MONTAGGIO", f"Video pronto ({probe_duration(final_video):.1f}s)", "success")

        log(reel_id, "COPY", "Caption, hashtag, copertina e sticker...")
        copy = agent_copy(state, api_key)
        (reel_dir(reel_id) / "testi.md").write_text(_copy_markdown(state, copy), encoding="utf-8")
        log(reel_id, "COPY", "Testi pronti", "success")

        engines = {item["engine"] for item in produced}

        def _done(s: dict):
            s["status"] = "done"
            s["error"] = None
            s["results"] = {
                "final_video": rel(final_video),
                "cover": rel(cover),
                "cover_plain": rel(cover_plain),
                "cover_qa": cover_qa,
                "qa_warnings": [
                    {"id": item["id"], "score": item["qa"].get("score"), "issues": item["qa"].get("issues")}
                    for item in produced
                    if item.get("qa") and (not item["qa"].get("ok") or not item["qa"].get("checked") and item["qa"].get("source") == "ai")
                ],
                "qa_replaced": [
                    {"id": item["id"], "issues": item["qa"].get("issues")}
                    for item in produced
                    if item.get("qa") and item["qa"].get("replaced")
                ],
                "copy_markdown": rel(reel_dir(reel_id) / "testi.md"),
                "shots": produced,
                "copy": copy,
                "preview_only": engines <= {"preview", "clip"} and "preview" in engines,
                "fallback_used": "fallback" in engines,
                "completed_at": datetime.now().isoformat(),
            }

        _mutate(reel_id, _done)
        log(reel_id, "PRODUZIONE", "Reel completato!", "success")
    except Exception as exc:
        _fail(reel_id, "PRODUZIONE", exc)


def start_render(reel_id: str) -> dict:
    """Valida e porta lo stato in 'rendering'. Il lavoro vero lo fa render_reel."""
    def _start(s: dict):
        if not s:
            raise ValueError("Reel non trovato.")
        if s.get("status") == "rendering":
            raise ValueError("Generazione gia in corso.")
        if not s.get("storyboard"):
            raise ValueError("Storyboard non ancora pronto.")
        s["status"] = "rendering"
        s["error"] = None
        s["results"] = {}

    return _mutate(reel_id, _start)
