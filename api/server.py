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
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Monili Media Agency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR    = PROJECT_ROOT / "input"
OUTPUT_DIR   = PROJECT_ROOT / "output"
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/files", StaticFiles(directory=str(OUTPUT_DIR)), name="files")

# In-memory job store
jobs: dict[str, dict] = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "Monili Media Agency API"}


@app.post("/mission/start")
async def start_mission(
    foto: UploadFile = File(...),
    brief: str = Form(default=""),
):
    """Avvia una nuova missione. Salva la foto e lancia il processo."""
    job_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Salva foto in input/
    ext = Path(foto.filename or "photo.jpg").suffix
    foto_path = INPUT_DIR / f"{timestamp}_{job_id}{ext}"
    content = await foto.read()
    foto_path.write_bytes(content)

    jobs[job_id] = {
        "id": job_id,
        "status": "running",
        "foto_path": str(foto_path),
        "brief": brief,
        "logs": [],
        "results": None,
        "output_dir": None,
        "started_at": datetime.now().isoformat(),
    }

    # Lancia in background
    asyncio.create_task(_run_mission(job_id, foto_path, brief))

    return {"job_id": job_id}


async def _run_mission(job_id: str, foto_path: Path, brief: str):
    """Esegue main.py in subprocess e cattura l'output riga per riga."""
    cmd = [sys.executable, str(PROJECT_ROOT / "main.py"),
           "--foto", str(foto_path),
           "--brief", brief or ""]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(PROJECT_ROOT),
        )
        async for line in proc.stdout:
            text = line.decode("utf-8", errors="replace").rstrip()
            if not text:
                continue
            # Cattura risultati strutturati
            if text.startswith("__RESULTS_JSON__:"):
                try:
                    import json
                    jobs[job_id]["results"] = json.loads(text[len("__RESULTS_JSON__:"):])
                except Exception:
                    pass
            else:
                jobs[job_id]["logs"].append(text)

        await proc.wait()
        jobs[job_id]["status"] = "done" if proc.returncode == 0 else "error"
    except Exception as e:
        jobs[job_id]["logs"].append(f"ERRORE: {e}")
        jobs[job_id]["status"] = "error"


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
