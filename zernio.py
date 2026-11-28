"""
zernio.py - pubblica su Instagram tramite Zernio (https://zernio.com/api/v1).

Il video parte dal PC: si carica su uno spazio temporaneo di Zernio (presign), poi si crea il post.
Instagram deve essere collegato a Zernio dal profilo Business o Creator del negozio (una volta sola).
Niente dati di clienti: solo il video, la caption e il primo commento del Reel.
Ogni pubblicazione è un'azione esterna: il chiamante deve averla fatta confermare a Matteo.
"""

import hashlib
import mimetypes
import os
import uuid
from pathlib import Path

import requests

BASE_URL = "https://zernio.com/api/v1"
TIMEOUT = 60
UPLOAD_TIMEOUT = 600
CAPTION_LIMIT = 2200
STORY_MAX_BYTES = 100 * 1024 * 1024
REEL_MAX_BYTES = 300 * 1024 * 1024


class ZernioError(RuntimeError):
    """Errore da mostrare a Matteo, già in italiano."""


def api_key() -> str:
    return os.environ.get("ZERNIO_API_KEY", "").strip()


def configured() -> bool:
    return bool(api_key())


def _headers(extra: dict | None = None) -> dict:
    return {"Authorization": f"Bearer {api_key()}", "User-Agent": "monili-studio", **(extra or {})}


def _explain(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return f"HTTP {response.status_code}"
    code = body.get("code") or body.get("type") or ""
    message = body.get("error") or body.get("message") or ""
    return f"{message} ({code})".strip() if code else str(message or f"HTTP {response.status_code}")


def _call(method: str, path: str, **kwargs) -> requests.Response:
    if not configured():
        raise ZernioError("Zernio non è configurato: manca ZERNIO_API_KEY nel file .env.")
    try:
        return requests.request(method, BASE_URL + path, headers=_headers(kwargs.pop("headers", None)), timeout=TIMEOUT, **kwargs)
    except requests.RequestException as error:
        raise ZernioError("Non riesco a raggiungere Zernio. Controlla la connessione e riprova.") from error


def instagram_account() -> dict | None:
    """L'account Instagram collegato a Zernio (id, username) oppure None se non è ancora collegato."""
    response = _call("GET", "/accounts", params={"platform": "instagram"})
    if response.status_code == 401:
        raise ZernioError("La chiave di Zernio non è valida o è scaduta.")
    if not response.ok:
        raise ZernioError(f"Zernio ha risposto con un errore: {_explain(response)}")
    for account in response.json().get("accounts", []):
        if account.get("platform") == "instagram" and account.get("isActive", True):
            return {"id": account["_id"], "username": account.get("username") or account.get("displayName") or ""}
    return None


def connect_url(profile_id: str | None = None) -> str:
    """Il link che Matteo apre una volta per collegare Instagram a Zernio."""
    if not profile_id:
        accounts = _call("GET", "/accounts")
        for account in accounts.json().get("accounts", []) if accounts.ok else []:
            profile = account.get("profileId")
            profile_id = profile.get("_id") if isinstance(profile, dict) else profile
            if profile_id:
                break
    if not profile_id:
        raise ZernioError("Non trovo il profilo Zernio a cui collegare Instagram.")
    response = _call("GET", "/connect/instagram", params={"profileId": profile_id})
    if not response.ok or "authUrl" not in response.json():
        raise ZernioError(f"Zernio non ha dato il link di collegamento: {_explain(response)}")
    return response.json()["authUrl"]


def upload_video(path: Path, max_bytes: int) -> str:
    """Carica il file su Zernio e restituisce l'indirizzo pubblico da usare nel post."""
    if not path.is_file():
        raise ZernioError("Il video non c'è più sul PC: rigenera il Reel.")
    size = path.stat().st_size
    if size > max_bytes:
        raise ZernioError(f"Il video pesa {size // (1024 * 1024)} MB: Instagram accetta al massimo {max_bytes // (1024 * 1024)} MB.")
    content_type = mimetypes.guess_type(path.name)[0] or "video/mp4"
    response = _call("POST", "/media/presign", json={"filename": path.name, "contentType": content_type})
    if not response.ok:
        raise ZernioError(f"Zernio non ha accettato il caricamento del video: {_explain(response)}")
    slot = response.json()
    try:
        with path.open("rb") as handle:
            sent = requests.put(slot["uploadUrl"], data=handle, headers={"Content-Type": content_type}, timeout=UPLOAD_TIMEOUT)
    except requests.RequestException as error:
        raise ZernioError("Il caricamento del video su Zernio si è interrotto. Riprova.") from error
    if not sent.ok:
        raise ZernioError(f"Il caricamento del video è fallito (HTTP {sent.status_code}).")
    return slot["publicUrl"]


def post_payload(kind: str, account_id: str, video_url: str, caption: str = "", first_comment: str = "",
                 ai_generated: bool = False) -> dict:
    """Il corpo della richiesta POST /posts: Reel con caption e primo commento, oppure Storia senza testo."""
    if kind not in ("reel", "story"):
        raise ZernioError("Si può pubblicare un Reel o una Storia.")
    media = [{"type": "video", "url": video_url}]
    if kind == "story":
        data: dict = {"contentType": "story"}
        if ai_generated:
            data["isAiGenerated"] = True
        return {
            "mediaItems": media,
            "platforms": [{"platform": "instagram", "accountId": account_id, "platformSpecificData": data}],
            "publishNow": True,
        }
    caption = caption.strip()
    if len(caption) > CAPTION_LIMIT:
        raise ZernioError(f"La caption è lunga {len(caption)} caratteri: Instagram ne accetta {CAPTION_LIMIT}.")
    data = {"shareToFeed": True}
    if first_comment.strip():
        data["firstComment"] = first_comment.strip()
    if ai_generated:
        data["isAiGenerated"] = True
    return {
        "content": caption,
        "mediaItems": media,
        "platforms": [{"platform": "instagram", "accountId": account_id, "platformSpecificData": data}],
        "publishNow": True,
    }


def idempotency_key(reel_id: str, kind: str, path: Path) -> str:
    """Stessa richiesta due volte = un solo post: la chiave dipende dal Reel, dal tipo e dal file."""
    stat = path.stat()
    digest = hashlib.sha256(f"{reel_id}|{kind}|{path.name}|{stat.st_size}|{int(stat.st_mtime)}".encode()).hexdigest()
    return str(uuid.UUID(digest[:32]))


def publish(kind: str, reel_id: str, video: Path, caption: str, first_comment: str, ai_generated: bool) -> dict:
    """Carica il video e pubblica subito. Restituisce {post_id, status}."""
    account = instagram_account()
    if not account:
        raise ZernioError("Instagram non è ancora collegato a Zernio. Collegalo una volta e riprova.")
    url = upload_video(video, STORY_MAX_BYTES if kind == "story" else REEL_MAX_BYTES)
    payload = post_payload(kind, account["id"], url, caption, first_comment, ai_generated)
    response = _call("POST", "/posts", json=payload, headers={"Idempotency-Key": idempotency_key(reel_id, kind, video)})
    if response.status_code == 409:
        existing = (response.json().get("details") or {}).get("existingPostId") or response.json().get("existingPostId")
        raise ZernioError("Questo contenuto risulta già pubblicato (o in pubblicazione) su Instagram negli ultimi giorni."
                          + (f" Codice Zernio: {existing}." if existing else ""))
    if response.status_code not in (200, 201, 207):
        raise ZernioError(f"Instagram non ha accettato la pubblicazione: {_explain(response)}")
    post = response.json().get("post") or {}
    return {"post_id": post.get("_id", ""), "status": post.get("status", "publishing"), "account": account["username"]}


def post_status(post_id: str) -> dict:
    """Stato del post e, a pubblicazione finita, il link su Instagram."""
    response = _call("GET", f"/posts/{post_id}")
    if not response.ok:
        raise ZernioError(f"Non riesco a leggere lo stato della pubblicazione: {_explain(response)}")
    post = response.json().get("post") or response.json()
    platforms = post.get("platforms") or [{}]
    first = platforms[0]
    return {
        "status": post.get("status", ""),
        "url": first.get("platformPostUrl", ""),
        "error": first.get("errorMessage", ""),
    }
