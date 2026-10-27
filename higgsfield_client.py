"""
higgsfield_client.py - client REST minimale per Higgsfield (video AI).

Doc: https://docs.higgsfield.ai
- Auth:      Authorization: Key KEY_ID:KEY_SECRET (solo lato server)
- Upload:    POST /files/generate-upload-url -> PUT su upload_url -> public_url
- Submit:    POST /{endpoint_id} -> request_id + status_url
- Status:    GET  /requests/{id}/status  (queued | in_progress | completed | failed | nsfw | canceled)
- Stima:     POST /estimate/{endpoint_id} con lo stesso body -> {credits, usd}
I file generati restano su Higgsfield almeno 7 giorni: vanno scaricati subito.
"""

import os
import time
import uuid
from pathlib import Path

import requests

HIGGSFIELD_BASE_URL = os.environ.get("HIGGSFIELD_BASE_URL", "https://api.higgsfield.ai").rstrip("/")
TERMINAL_STATUSES = {"completed", "failed", "nsfw", "canceled"}

# Modelli video supportati: endpoint + costruzione del body specifico.
VIDEO_MODELS: dict[str, dict] = {
    "kling-3-std": {
        "label": "Kling 3.0 Standard",
        "endpoint": "kling-video/v3.0/std/image-to-video",
        "min_duration": 3,
        "max_duration": 15,
    },
    "kling-3-pro": {
        "label": "Kling 3.0 Pro",
        "endpoint": "kling-video/v3.0/pro/image-to-video",
        "min_duration": 3,
        "max_duration": 15,
    },
    "seedance-2.5": {
        "label": "Seedance 2.5",
        "endpoint": "bytedance/seedance-2.5/image-to-video",
        "min_duration": 4,
        "max_duration": 30,
    },
}
DEFAULT_VIDEO_MODEL = "kling-3-std"


class HiggsfieldError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def credentials() -> str:
    """Restituisce 'KEY_ID:KEY_SECRET' oppure stringa vuota se non configurata."""
    combined = os.environ.get("HIGGSFIELD_API_KEY", "").strip()
    if combined and ":" in combined:
        return combined
    key_id = os.environ.get("HF_API_KEY_ID", "").strip()
    secret = os.environ.get("HF_API_KEY_SECRET", "").strip()
    if key_id and secret:
        return f"{key_id}:{secret}"
    return ""


def is_configured() -> bool:
    return bool(credentials())


def select_video_model(requested: str = "") -> str:
    requested = (requested or "").strip()
    if requested in VIDEO_MODELS:
        return requested
    env_model = os.environ.get("HIGGSFIELD_VIDEO_MODEL", "").strip()
    if env_model in VIDEO_MODELS:
        return env_model
    return DEFAULT_VIDEO_MODEL


def clamp_duration(model_key: str, seconds: int) -> int:
    spec = VIDEO_MODELS[select_video_model(model_key)]
    return max(spec["min_duration"], min(spec["max_duration"], int(seconds)))


def build_video_body(
    model_key: str,
    image_url: str,
    prompt: str,
    duration: int,
    sound: bool = False,
    last_image_url: str = "",
) -> dict:
    """last_image_url: fotogramma finale (es. la foto vera del prodotto) per chiudere la scena sul pezzo esatto."""
    model_key = select_video_model(model_key)
    duration = clamp_duration(model_key, duration)
    prompt = (prompt or "Slow elegant camera movement, natural light.").strip()[:2400]
    if model_key.startswith("kling"):
        body = {
            "image_url": image_url,
            "prompt": prompt,
            "duration": duration,
            "sound": "on" if sound else "off",
            "cfg_scale": 0.5,
        }
        if last_image_url:
            body["last_image_url"] = last_image_url
        return body
    body = {
        "image_url": image_url,
        "prompt": prompt,
        "duration": duration,
        "resolution": os.environ.get("HIGGSFIELD_RESOLUTION", "720p"),
        "generate_audio": bool(sound),
    }
    if last_image_url:
        body["end_image_url"] = last_image_url
    return body


def _headers(extra: dict | None = None) -> dict:
    creds = credentials()
    if not creds:
        raise HiggsfieldError("Credenziali Higgsfield non configurate (HF_API_KEY_ID / HF_API_KEY_SECRET).")
    headers = {"Authorization": f"Key {creds}", "Content-Type": "application/json"}
    if extra:
        headers.update(extra)
    return headers


def _raise_for_status(response: requests.Response, action: str) -> None:
    if response.status_code < 400:
        return
    hints = {
        401: "credenziali non valide",
        403: "crediti Higgsfield insufficienti",
        404: "modello non disponibile per questo account",
        422: "parametri non validi",
        423: "modello temporaneamente bloccato",
        429: "limite richieste raggiunto",
        503: "modello non pronto",
    }
    hint = hints.get(response.status_code, "errore")
    raise HiggsfieldError(
        f"Higgsfield {action}: HTTP {response.status_code} ({hint}) {response.text[:300]}",
        status_code=response.status_code,
    )


def upload_file(path: Path, content_type: str = "image/jpeg") -> str:
    """Carica un file locale e restituisce il public_url da usare come image_url."""
    response = requests.post(
        f"{HIGGSFIELD_BASE_URL}/files/generate-upload-url",
        headers=_headers(),
        json={"content_type": content_type},
        timeout=30,
    )
    _raise_for_status(response, "upload-url")
    data = response.json()
    upload_headers = data.get("upload_headers") or {"Content-Type": content_type}
    with open(path, "rb") as handle:
        put = requests.put(data["upload_url"], data=handle, headers=upload_headers, timeout=120)
    if put.status_code >= 400:
        raise HiggsfieldError(f"Upload file fallito: HTTP {put.status_code} {put.text[:200]}", put.status_code)
    return data["public_url"]


def submit(endpoint: str, body: dict, idempotency_key: str | None = None) -> dict:
    response = requests.post(
        f"{HIGGSFIELD_BASE_URL}/{endpoint.strip('/')}",
        headers=_headers({"Idempotency-Key": idempotency_key or str(uuid.uuid4())}),
        json=body,
        timeout=60,
    )
    _raise_for_status(response, "submit")
    return response.json()


def get_status(request_id: str, status_url: str = "") -> dict:
    url = status_url or f"{HIGGSFIELD_BASE_URL}/requests/{request_id}/status"
    response = requests.get(url, headers=_headers(), timeout=30)
    _raise_for_status(response, "status")
    return response.json()


def wait_for_result(
    request_id: str,
    status_url: str = "",
    timeout_seconds: int = 900,
    poll_seconds: int = 8,
    on_update=None,
) -> dict:
    deadline = time.time() + timeout_seconds
    last_status = ""
    while True:
        try:
            payload = get_status(request_id, status_url)
        except HiggsfieldError as exc:
            # errori transitori del polling: riprova finche c'e tempo
            if exc.status_code not in (429, 500, 502, 503) or time.time() > deadline:
                raise
            time.sleep(poll_seconds)
            continue
        status = str(payload.get("status", ""))
        if status != last_status and on_update:
            on_update(status)
        last_status = status
        if status in TERMINAL_STATUSES:
            return payload
        if time.time() > deadline:
            raise HiggsfieldError(f"Timeout: video ancora '{status}' dopo {timeout_seconds // 60} minuti.")
        time.sleep(poll_seconds)


def estimate(endpoint: str, body: dict) -> dict:
    """Restituisce {'credits': float, 'usd': float}."""
    response = requests.post(
        f"{HIGGSFIELD_BASE_URL}/estimate/{endpoint.strip('/')}",
        headers=_headers(),
        json=body,
        timeout=30,
    )
    _raise_for_status(response, "estimate")
    data = response.json()
    return {"credits": float(data.get("credits") or 0), "usd": float(data.get("usd") or 0)}


def download(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=180) as response:
        if response.status_code >= 400:
            raise HiggsfieldError(f"Download video fallito: HTTP {response.status_code}", response.status_code)
        with open(destination, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if chunk:
                    handle.write(chunk)
    return destination
