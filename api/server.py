"""
api/server.py — FastAPI backend per Monili Media Agency
Riceve la foto + brief dal frontend, lancia main.py via subprocess,
restituisce SSE con gli aggiornamenti in tempo reale.
"""
import asyncio
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Monili Media Agency API")
load_dotenv(encoding="utf-8-sig")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).parent.parent


def _resolve_storage_root() -> Path:
    configured = os.environ.get("MONILI_STORAGE_DIR", "").strip()
    if not configured:
        return PROJECT_ROOT
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


STORAGE_ROOT = _resolve_storage_root()
INPUT_DIR    = STORAGE_ROOT / "input"
OUTPUT_DIR   = STORAGE_ROOT / "output"
SHOWCASE_DRAFTS_DIR = STORAGE_ROOT / "showcase-drafts"
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SHOWCASE_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/files", StaticFiles(directory=str(OUTPUT_DIR)), name="files")

# In-memory job store
jobs: dict[str, dict] = {}
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", "26214400"))  # 25 MB
READ_CHUNK_SIZE = 1024 * 1024
MAX_JOB_LOG_LINES = int(os.environ.get("MAX_JOB_LOG_LINES", "500"))
JOB_RETENTION_SECONDS = int(os.environ.get("JOB_RETENTION_SECONDS", "21600"))  # 6 hours
CLEANUP_INTERVAL_SECONDS = int(os.environ.get("CLEANUP_INTERVAL_SECONDS", "300"))
MISSION_TIMEOUT_SECONDS = int(os.environ.get("MISSION_TIMEOUT_SECONDS", "900"))
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
HEIC_EXTENSIONS = {".heic", ".heif"}
ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
    "image/heic-sequence",
    "image/heif-sequence",
}
MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
    "image/heic-sequence": ".heic",
    "image/heif-sequence": ".heif",
}
cleanup_task: asyncio.Task | None = None
DEFAULT_HISTORY_LIMIT = int(os.environ.get("HISTORY_LIMIT", "20"))
SUPPORTED_OPENROUTER_IMAGE_MODELS = [
    "openai/gpt-5.4-image-2",
    "google/gemini-3.1-flash-image-preview",
    "black-forest-labs/flux.2-klein-4b",
    "bytedance-seed/seedream-4.5",
]
DEFAULT_OPENROUTER_IMAGE_MODEL = SUPPORTED_OPENROUTER_IMAGE_MODELS[0]
SUPPORTED_OPENROUTER_TEXT_MODELS = [
    "openai/gpt-4.1-mini",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-3.7-sonnet",
]
DEFAULT_OPENROUTER_TEXT_MODEL = SUPPORTED_OPENROUTER_TEXT_MODELS[0]


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _prune_finished_jobs() -> int:
    cutoff = datetime.now() - timedelta(seconds=JOB_RETENTION_SECONDS)
    stale_job_ids: list[str] = []
    for job_id, job in jobs.items():
        if job.get("status") not in ("done", "error"):
            continue
        completed_at = _parse_dt(job.get("completed_at")) or _parse_dt(job.get("started_at"))
        if completed_at and completed_at < cutoff:
            stale_job_ids.append(job_id)

    for job_id in stale_job_ids:
        jobs.pop(job_id, None)

    return len(stale_job_ids)


def _is_supported_upload(content_type: str, ext: str) -> bool:
    if content_type in ALLOWED_IMAGE_CONTENT_TYPES:
        return True
    # Some mobile browsers upload HEIC photos as octet-stream.
    return content_type == "application/octet-stream" and ext in HEIC_EXTENSIONS


def _read_run_manifest(manifest_path: Path) -> dict | None:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


def _history_item_from_payload(payload: dict) -> dict | None:
    run_id = str(payload.get("run_id", "")).strip()
    output_dir = str(payload.get("output_dir", "")).strip()
    if not run_id or not output_dir:
        return None

    created_at = str(payload.get("created_at", "")).strip()
    brief = str(payload.get("brief", "")).strip()
    source_photo = str(payload.get("source_photo", "")).strip()
    results = payload.get("results")
    selected_format = ""
    if isinstance(results, dict):
        try:
            pack = json.loads(str(results.get("publish_pack_json", "{}")))
            if isinstance(pack, dict):
                selected_format = str(pack.get("selected_format", "")).strip()
        except Exception:
            selected_format = ""

    return {
        "run_id": run_id,
        "created_at": created_at,
        "brief": brief,
        "source_photo": Path(source_photo).name if source_photo else "",
        "output_dir": Path(output_dir).name,
        "selected_format": selected_format,
    }


def _history_item_from_job(job: dict) -> dict | None:
    if job.get("status") != "done" or not isinstance(job.get("results"), dict):
        return None

    results = job["results"]
    payload = {
        "run_id": results.get("run_id") or job.get("run_id"),
        "created_at": job.get("completed_at") or job.get("started_at") or "",
        "brief": job.get("brief", ""),
        "source_photo": job.get("foto_path", ""),
        "output_dir": results.get("output_dir") or job.get("output_dir"),
        "results": results,
    }
    return _history_item_from_payload(payload)


def _collect_history(limit: int = DEFAULT_HISTORY_LIMIT) -> list[dict]:
    manifests: list[dict] = []
    for path in OUTPUT_DIR.glob("*/run_manifest.json"):
        payload = _read_run_manifest(path)
        if not payload:
            continue
        item = _history_item_from_payload(payload)
        if item:
            manifests.append(item)

    seen = {item["run_id"] for item in manifests}
    for job in jobs.values():
        item = _history_item_from_job(job)
        if item and item["run_id"] not in seen:
            manifests.append(item)
            seen.add(item["run_id"])

    manifests.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return manifests[: max(1, min(limit, 100))]


def _find_mission_payload(run_id: str) -> dict | None:
    run_id = run_id.strip()
    for path in OUTPUT_DIR.glob("*/run_manifest.json"):
        payload = _read_run_manifest(path)
        if payload and str(payload.get("run_id", "")).strip() == run_id:
            return payload

    for job in jobs.values():
        results = job.get("results")
        if not isinstance(results, dict):
            continue
        job_run_id = str(results.get("run_id") or job.get("run_id") or "").strip()
        if job_run_id == run_id:
            return {
                "run_id": run_id,
                "created_at": job.get("completed_at") or job.get("started_at"),
                "status": job.get("status", "done"),
                "results": results,
            }
    return None


def _showcase_image_candidates(results: dict) -> list[dict]:
    candidate_keys = [
        "image_feed",
        "image_stories",
        "image_story_1",
        "image_story_2",
        "image_story_3",
    ]
    candidate_keys.extend(sorted(key for key in results if key.startswith("image_ai_")))
    candidate_keys.extend(sorted(key for key in results if key.startswith("image_carousel_")))

    seen: set[str] = set()
    items: list[dict] = []
    for key in candidate_keys:
        src = str(results.get(key, "")).strip()
        if not src or src in seen:
            continue
        seen.add(src)
        file_path = OUTPUT_DIR / src
        available = file_path.exists() and file_path.is_file()
        items.append(
            {
                "src": src,
                "available": available,
                "recommended": key in {"image_feed", "image_stories", "image_story_1"},
                "kind": key,
                "error": None if available else "File non trovato nello storage locale.",
            }
        )
    return items


def _convert_heic_to_jpeg(source: Path) -> Path:
    try:
        import pillow_heif
        from PIL import Image

        pillow_heif.register_heif_opener()
        converted = source.with_suffix(".jpg")
        with Image.open(source) as image:
            image.convert("RGB").save(converted, "JPEG", quality=95, optimize=True)
        source.unlink(missing_ok=True)
        return converted
    except Exception as exc:
        raise RuntimeError(f"Conversione HEIC/HEIF non riuscita: {exc}") from exc


async def _cleanup_jobs_forever() -> None:
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
        _prune_finished_jobs()


@app.on_event("startup")
async def startup_event() -> None:
    global cleanup_task
    cleanup_task = asyncio.create_task(_cleanup_jobs_forever())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global cleanup_task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        cleanup_task = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "Monili Media Agency API"}


@app.get("/openrouter/check")
def check_openrouter(
    image_model: str = DEFAULT_OPENROUTER_IMAGE_MODEL,
    text_model: str = DEFAULT_OPENROUTER_TEXT_MODEL,
):
    selected_image_model = image_model.strip() if image_model.strip() else DEFAULT_OPENROUTER_IMAGE_MODEL
    selected_text_model = text_model.strip() if text_model.strip() else DEFAULT_OPENROUTER_TEXT_MODEL
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return JSONResponse(
            {
                "ok": False,
                "error": "OPENROUTER_API_KEY non configurata",
                "selected_image_model": selected_image_model,
                "selected_text_model": selected_text_model,
            },
            status_code=400,
        )

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        key_response = requests.get("https://openrouter.ai/api/v1/key", headers=headers, timeout=15)
        if key_response.status_code >= 400:
            return JSONResponse(
                {
                    "ok": False,
                    "error": f"Verifica key fallita: HTTP {key_response.status_code}",
                    "details": key_response.text[:300],
                    "selected_image_model": selected_image_model,
                    "selected_text_model": selected_text_model,
                },
                status_code=401,
            )

        models_response = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=20)
        if models_response.status_code >= 400:
            return JSONResponse(
                {
                    "ok": False,
                    "error": f"Elenco modelli non disponibile: HTTP {models_response.status_code}",
                    "details": models_response.text[:300],
                    "selected_image_model": selected_image_model,
                    "selected_text_model": selected_text_model,
                },
                status_code=502,
            )

        image_models_response = requests.get(
            "https://openrouter.ai/api/v1/models?output_modality=image",
            headers=headers,
            timeout=20,
        )
        image_models_payload = image_models_response.json() if image_models_response.status_code < 400 else {"data": []}

        models_payload = models_response.json()
        model_ids = {item.get("id") for item in models_payload.get("data", []) if isinstance(item, dict)}
        image_model_ids = {item.get("id") for item in image_models_payload.get("data", []) if isinstance(item, dict)}
        image_supported = selected_image_model in image_model_ids if image_model_ids else selected_image_model in model_ids
        text_supported = selected_text_model in model_ids
        return {
            "ok": image_supported and text_supported,
            "selected_image_model": selected_image_model,
            "selected_text_model": selected_text_model,
            "image_model_supported": image_supported,
            "text_model_supported": text_supported,
            "available_count": len(model_ids),
            "available_image_count": len(image_model_ids),
        }
    except requests.RequestException as exc:
        return JSONResponse(
            {
                "ok": False,
                "error": f"Errore rete verso OpenRouter: {exc}",
                "selected_image_model": selected_image_model,
                "selected_text_model": selected_text_model,
            },
            status_code=502,
        )


@app.post("/mission/start")
async def start_mission(
    foto: UploadFile = File(...),
    brief: str = Form(default=""),
    image_model: str = Form(default=DEFAULT_OPENROUTER_IMAGE_MODEL),
    text_model: str = Form(default=DEFAULT_OPENROUTER_TEXT_MODEL),
):
    """Avvia una nuova missione. Salva la foto e lancia il processo."""
    selected_image_model = image_model.strip() if image_model.strip() else DEFAULT_OPENROUTER_IMAGE_MODEL
    selected_text_model = text_model.strip() if text_model.strip() else DEFAULT_OPENROUTER_TEXT_MODEL
    if not os.environ.get("OPENROUTER_API_KEY", "").strip():
        return JSONResponse(
            {"error": "OPENROUTER_API_KEY non configurata nel backend locale."},
            status_code=400,
        )

    job_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    content_type = (foto.content_type or "").lower().strip()
    original_ext = Path(foto.filename or "").suffix.lower()
    if not _is_supported_upload(content_type, original_ext):
        return JSONResponse(
            {"error": "Formato non supportato. Usa JPG, PNG, WEBP o HEIC/HEIF da iPhone."},
            status_code=415,
        )

    # Salva foto in input/
    ext = original_ext
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = MIME_TO_EXT.get(content_type, ".jpg")
    foto_path = INPUT_DIR / f"{timestamp}_{job_id}{ext}"
    total_bytes = 0
    try:
        with foto_path.open("wb") as out_file:
            while True:
                chunk = await foto.read(READ_CHUNK_SIZE)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_BYTES:
                    foto_path.unlink(missing_ok=True)
                    return JSONResponse(
                        {"error": f"File troppo grande. Massimo {MAX_UPLOAD_BYTES // (1024 * 1024)} MB."},
                        status_code=413,
                    )
                out_file.write(chunk)
    finally:
        await foto.close()

    if total_bytes == 0:
        foto_path.unlink(missing_ok=True)
        return JSONResponse({"error": "File immagine vuoto."}, status_code=400)

    if foto_path.suffix.lower() in HEIC_EXTENSIONS:
        try:
            foto_path = _convert_heic_to_jpeg(foto_path)
        except RuntimeError as exc:
            return JSONResponse({"error": str(exc)}, status_code=415)

    jobs[job_id] = {
        "id": job_id,
        "status": "running",
        "foto_path": str(foto_path),
        "brief": brief,
        "image_model": selected_image_model,
        "text_model": selected_text_model,
        "logs": [],
        "results": None,
        "output_dir": None,
        "started_at": datetime.now().isoformat(),
        "last_update": datetime.now().isoformat(),
        "completed_at": None,
    }

    # Lancia in background
    asyncio.create_task(_run_mission(job_id, foto_path, brief, selected_image_model, selected_text_model))

    return {"job_id": job_id, "image_model": selected_image_model, "text_model": selected_text_model}


async def _run_mission(job_id: str, foto_path: Path, brief: str, image_model: str, text_model: str):
    """Esegue main.py in subprocess e cattura l'output riga per riga."""
    cmd = [sys.executable, str(PROJECT_ROOT / "main.py"),
           "--foto", str(foto_path),
           "--brief", brief or ""]
    if image_model:
        cmd.extend(["--image-model", image_model])
    if text_model:
        cmd.extend(["--text-model", text_model])

    def _consume_line(text: str):
        job = jobs.get(job_id)
        if not job or not text:
            return
        if text.startswith("__RESULTS_JSON__:"):
            try:
                job["results"] = json.loads(text[len("__RESULTS_JSON__:"):])
                if isinstance(job["results"], dict):
                    job["output_dir"] = job["results"].get("output_dir")
                    job["run_id"] = job["results"].get("run_id")
                job["last_update"] = datetime.now().isoformat()
            except Exception:
                pass
            return
        logs = job["logs"]
        logs.append(text)
        if len(logs) > MAX_JOB_LOG_LINES:
            del logs[:-MAX_JOB_LOG_LINES]
        job["last_update"] = datetime.now().isoformat()

    def _run_subprocess_blocking() -> int:
        child_env = os.environ.copy()
        child_env["MONILI_STORAGE_DIR"] = str(STORAGE_ROOT)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(PROJECT_ROOT),
            env=child_env,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            _consume_line(line.rstrip())
        return proc.wait()

    try:
        returncode = await asyncio.wait_for(
            asyncio.to_thread(_run_subprocess_blocking),
            timeout=MISSION_TIMEOUT_SECONDS,
        )
        job = jobs.get(job_id)
        if job:
            if returncode == 0 and not isinstance(job.get("results"), dict):
                logs = job["logs"]
                logs.append("ERRORE: processo terminato senza risultati JSON. Nessuna foto recuperabile.")
                job["status"] = "error"
            else:
                job["status"] = "done" if returncode == 0 else "error"
            job["completed_at"] = datetime.now().isoformat()
            job["last_update"] = datetime.now().isoformat()
    except asyncio.TimeoutError:
        job = jobs.get(job_id)
        if job:
            logs = job["logs"]
            logs.append(
                f"ERRORE: missione oltre {MISSION_TIMEOUT_SECONDS // 60} minuti. Riprova con kit rapido o modello immagini Gemini."
            )
            if len(logs) > MAX_JOB_LOG_LINES:
                del logs[:-MAX_JOB_LOG_LINES]
            job["status"] = "error"
            job["completed_at"] = datetime.now().isoformat()
            job["last_update"] = datetime.now().isoformat()
    except Exception as e:
        job = jobs.get(job_id)
        if job:
            logs = job["logs"]
            logs.append(f"ERRORE: {e}")
            if len(logs) > MAX_JOB_LOG_LINES:
                del logs[:-MAX_JOB_LOG_LINES]
            job["status"] = "error"
            job["completed_at"] = datetime.now().isoformat()
            job["last_update"] = datetime.now().isoformat()


@app.get("/mission/{job_id}/stream")
async def stream_mission(job_id: str):
    """SSE stream: invia aggiornamenti di stato al frontend."""
    if job_id not in jobs:
        return JSONResponse({"error": "Job non trovato"}, status_code=404)

    async def event_generator():
        last_log_idx = 0
        while True:
            job = jobs.get(job_id, {})
            new_logs = job.get("logs", [])[last_log_idx:]
            for log in new_logs:
                yield f"data: {json.dumps({'type': 'log', 'msg': log})}\n\n"
            last_log_idx += len(new_logs)

            status = job.get("status", "running")
            if status in ("done", "error"):
                yield f"data: {json.dumps({'type': 'status', 'status': status})}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/mission/{job_id}/status")
def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Job non trovato"}, status_code=404)
    return {
        "status": job["status"],
        "logs": job["logs"],
        "results": job.get("results"),
    }


@app.get("/missions/history")
def missions_history(limit: int = DEFAULT_HISTORY_LIMIT):
    return {"items": _collect_history(limit=limit)}


@app.get("/ops/jobs")
def active_jobs():
    items = []
    for job in jobs.values():
        logs = job.get("logs", [])
        items.append(
            {
                "id": job.get("id"),
                "status": job.get("status"),
                "image_model": job.get("image_model"),
                "text_model": job.get("text_model"),
                "started_at": job.get("started_at"),
                "last_update": job.get("last_update"),
                "completed_at": job.get("completed_at"),
                "run_id": job.get("run_id"),
                "output_dir": job.get("output_dir"),
                "log_tail": logs[-12:] if isinstance(logs, list) else [],
            }
        )
    return {"items": items}


@app.get("/missions/{run_id}")
def mission_by_run_id(run_id: str):
    run_id = run_id.strip()
    if not run_id:
        return JSONResponse({"error": "run_id mancante"}, status_code=400)

    payload = _find_mission_payload(run_id)
    if payload:
        return {
            "run_id": run_id,
            "status": payload.get("status", "done"),
            "created_at": payload.get("created_at"),
            "results": payload.get("results", {}),
        }
    return JSONResponse({"error": "Run non trovato"}, status_code=404)


@app.get("/missions/{run_id}/showcase/candidates")
def showcase_candidates(run_id: str):
    payload = _find_mission_payload(run_id)
    if not payload:
        return JSONResponse({"error": "Run non trovato"}, status_code=404)
    results = payload.get("results", {})
    if not isinstance(results, dict):
        return JSONResponse({"error": "Risultati missione non disponibili."}, status_code=404)

    return {
        "run_id": run_id,
        "items": _showcase_image_candidates(results),
    }


@app.post("/missions/{run_id}/showcase/publish")
async def showcase_publish(run_id: str, body: dict | None = None):
    payload = _find_mission_payload(run_id)
    if not payload:
        return JSONResponse({"error": "Run non trovato"}, status_code=404)
    results = payload.get("results", {})
    if not isinstance(results, dict):
        return JSONResponse({"error": "Risultati missione non disponibili."}, status_code=404)

    selected = []
    if isinstance(body, dict) and isinstance(body.get("selected_images"), list):
        selected = [str(item).strip() for item in body["selected_images"] if str(item).strip()]

    available = {item["src"] for item in _showcase_image_candidates(results) if item.get("available")}
    selected = [src for src in selected if src in available]
    if not selected:
        return JSONResponse({"error": "Seleziona almeno una foto disponibile."}, status_code=400)

    draft_id = f"draft-{run_id}"
    draft = {
        "id": draft_id,
        "run_id": run_id,
        "created_at": datetime.now().isoformat(),
        "selected_images": selected,
        "publish_pack_json": results.get("publish_pack_json", ""),
        "publish_pack": results.get("publish_pack", ""),
        "source": "local-content-app",
        "status": "local-draft",
        "note": "Draft locale salvato dall'agenzia. Collegare SHOWCASE_INGEST_URL per inviarlo automaticamente al sito vetrina.",
    }
    target = SHOWCASE_DRAFTS_DIR / f"{draft_id}.json"
    target.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "mode": "local-draft",
        "draft_path": str(target),
        "ingest": {
            "ok": True,
            "created_id": draft_id,
            "status": "saved-local",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
