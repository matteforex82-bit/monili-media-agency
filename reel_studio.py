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

import higgsfield_client as hf
import reel_kit as kit
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
) -> dict:
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
        "poster_cover": bool(poster_cover),
        "target_seconds": target_seconds,
        "video_model": hf.select_video_model(video_model),
        "keyframe_model": select_openrouter_image_model(keyframe_model),
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
    return "\n".join(hints)


def agent_storyboard(state: dict, photo: Path) -> dict:
    fmt = FORMATS[state["format"]]
    clips = state.get("clips") or []
    clip_lines = "\n".join(f"- clip_index {i}: durata {c['duration']}s" for i, c in enumerate(clips)) or "- nessuna clip reale caricata"
    n_photos = len(state.get("photos") or [])
    persona = kit.load_persona()
    prompt = f"""Sei il direttore creativo video di I Monili Ravenna: crei Reel e Story video Instagram che fermano lo scroll.
{BRAND}

ANALISI PRODOTTO:
{state.get('analysis', '')[:2500]}

BRIEF: {state.get('brief') or 'nessuno - decidi tu'}
FORMATO: {fmt['label']} - durata totale circa {state['target_seconds']} secondi, {fmt['shots']} inquadrature.
FOTO PRODOTTO DISPONIBILI: {n_photos} (photo_index da 0 a {max(0, n_photos - 1)})
CLIP REALI CARICATE DALL'UTENTE:
{clip_lines}

{kit.recipe_prompt_block(state.get('recipe', ''))}

MODELLA MONILI (volto ricorrente del brand, sempre la stessa donna): {persona['description']}
Usa use_model true nelle inquadrature dove compare una donna: sara sempre la Modella Monili.

REGOLE:
- I primi 1.5 secondi sono un HOOK visivo forte (movimento, luce che colpisce le pietre, gesto).
- Se ci sono clip reali usale (source "clip") dove rendono di piu: l'autenticita del negozio vende.
- Le inquadrature AI partono da un fotogramma chiave generato dalla foto reale: il prodotto deve restare identico.
- Gioielli piccoli: preferisci movimenti lenti (slow push-in, orbit leggero, rack focus), evita rotazioni veloci.
- Luce coerente col brand: calda, naturale, golden hour Ravenna o interno caldo del negozio.
- Ogni inquadratura AI dura 3-6 secondi; l'ultima chiude SEMPRE con invito concreto: "Scrivici, te lo mettiamo da parte" o "Ti aspettiamo in centro a Ravenna".
- Stile: luce naturale calda, sfondi crema/neutri che fanno risaltare i colori del prodotto. Mai effetti pacchiani.
- on_screen_text in italiano, max 6 parole, tono da amica.
- keyframe_prompt_en e motion_prompt_en in inglese, concreti e visivi.
- keyframe_mode "original_photo" = usa la foto reale cosi com'e (massima fedelta, utile per il dettaglio prodotto).

Rispondi SOLO con JSON valido:
{{
  "title": "titolo breve interno",
  "concept": "idea in una frase",
  "hook": "cosa succede nei primi 1.5s",
  "music_mood": "mood musicale da cercare tra gli audio di tendenza Instagram",
  "cover_text": "testo copertina max 5 parole",
  "shots": [
    {{
      "purpose": "hook|dettaglio|indossato|lifestyle|outfit|cta",
      "source": "ai|clip",
      "clip_index": null,
      "clip_start": 0,
      "photo_index": 0,
      "keyframe_mode": "ai|original_photo",
      "use_model": false,
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
            label = "Fotogramma AI" + (" con Modella Monili" if shot.get("use_model") else "") + " + controllo qualita"
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
        poster_usd = kit.POSTER_USD + kit.QA_USD
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
        storyboard = normalize_storyboard(state, agent_storyboard(state, photo))
        state.pop("api_key", None)
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

def _keyframe(state: dict, shot: dict, api_key: str, out_dir: Path) -> tuple[Path, dict | None]:
    """Fotogramma chiave 9:16 + controllo qualita contro la foto reale (1 nuovo tentativo se fallisce)."""
    reel_id = state["id"]
    photo = _abs(state["photos"][shot["photo_index"]])
    keyframe = out_dir / f"{shot['id']}_keyframe.jpg"
    if shot["keyframe_mode"] == "original_photo":
        make_cover(photo, keyframe)
        return keyframe, None

    images = [photo]
    model_line = ""
    if shot.get("use_model"):
        persona = kit.load_persona()
        reference = kit.persona_reference_path()
        model_line = f"The woman is the brand's recurring model: {persona['description']}.\n"
        if reference:
            images.append(reference)
            model_line += "She must be the SAME woman as in the second reference image (same face, hair, skin tone).\n"
    prompt = (
        f"Create a photorealistic vertical 9:16 Instagram Reel first frame using the product in the first reference photo.\n"
        f"Scene: {shot['keyframe_prompt_en'] or shot['action']}\n"
        f"Camera angle: {shot['angle']}. Lighting: {shot['lighting']}.\n"
        f"{model_line}"
        f"Brand look: warm natural light, cream and warm neutral backgrounds that make the product colors stand out, "
        f"terracotta and gold accents, authentic and not over-retouched.\n"
        f"{PRODUCT_FIDELITY_RULES}\nNo text, no logos, no watermark."
    )
    qa = None
    for attempt in (1, 2):
        try:
            raw_path = out_dir / f"{shot['id']}_keyframe_raw.png"
            kit.generate_image_multi(api_key, state["keyframe_model"], prompt, images, raw_path, aspect_ratio="9:16")
            make_cover(raw_path, keyframe)
            raw_path.unlink(missing_ok=True)
        except Exception as exc:
            log(reel_id, "FOTOGRAMMI", f"{shot['id']}: fotogramma AI non riuscito ({exc}), uso la foto reale", "warn")
            make_cover(photo, keyframe)
            return keyframe, None
        qa = kit.check_keyframe(api_key, state["text_model"], photo, keyframe)
        if qa["ok"]:
            if qa.get("checked"):
                log(reel_id, "QUALITA", f"{shot['id']}: prodotto fedele ({qa.get('score')}/10)", "success")
            break
        log(
            reel_id,
            "QUALITA",
            f"{shot['id']}: controllo {qa.get('score')}/10 - {qa.get('issues') or 'prodotto diverso'}"
            + (" - rigenero" if attempt == 1 else " - DA CONTROLLARE prima di pubblicare"),
            "warn",
        )
    return keyframe, qa


def _ai_shot_video(state: dict, shot: dict, keyframe: Path, out_dir: Path) -> tuple[Path, str]:
    reel_id = state["id"]
    final = out_dir / f"{shot['id']}.mp4"
    duration = float(shot["duration"])
    if not hf.is_configured():
        ken_burns_clip(keyframe, final, duration, zoom_in=shot["purpose"] != "cta")
        return final, "preview"

    model_key = state["video_model"]
    motion = (
        f"{shot['motion_prompt_en'] or shot['action']}. Camera: {shot['camera']}. Lighting: {shot['lighting']}. "
        f"{MOTION_FIDELITY_RULES}"
    )
    try:
        image_url = hf.upload_file(keyframe, "image/jpeg")
        body = hf.build_video_body(model_key, image_url, motion, int(duration))
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


def _produce_shot(state: dict, shot: dict, api_key: str, out_dir: Path) -> dict:
    reel_id = state["id"]
    if shot["source"] == "clip":
        clip = state["clips"][shot["clip_index"]]
        source = _abs(clip["src"])
        clip_length = float(clip.get("duration") or 0) or probe_duration(source)
        start = min(shot["clip_start"], max(0.0, clip_length - 1.0))
        duration = max(1.0, min(float(shot["duration"]), clip_length - start))
        final = normalize_clip(source, out_dir / f"{shot['id']}.mp4", duration, start=start)
        log(reel_id, "MONTAGGIO", f"{shot['id']}: clip reale pronta ({duration:.1f}s)", "success")
        return {"id": shot["id"], "video": rel(final), "keyframe": None, "duration": duration, "engine": "clip"}

    log(reel_id, "FOTOGRAMMI", f"{shot['id']}: fotogramma chiave ({shot['purpose']})...")
    keyframe, qa = _keyframe(state, shot, api_key, out_dir)
    video, engine = _ai_shot_video(state, shot, keyframe, out_dir)
    log(reel_id, "VIDEO", f"{shot['id']}: pronto ({engine})", "success")
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

REGOLE: tono caldo e complice da amica, mai formale; max 2-3 emoji per caption; la prima riga e un hook che fa fermare;
hashtag: sempre #imoniliravenna #ravenna #romagnastyle + 6-9 hashtag pertinenti (mix nicchia/locale);
chiudi SEMPRE con invito concreto al DM ("scrivici, te lo mettiamo da parte") o a passare in negozio in centro a Ravenna.

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

        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_SHOTS) as pool:
            futures = [pool.submit(_produce_shot, state, shot, api_key, out_dir) for shot in storyboard["shots"]]
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
                cover = kit.make_poster_cover(api_key, state["keyframe_model"], product_photo, cover_text, reel_dir(reel_id) / "cover.jpg")
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
                    if item.get("qa") and not item["qa"].get("ok")
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
