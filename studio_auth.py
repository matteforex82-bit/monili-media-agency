"""Studio access PIN.

The Studio listens on the home network and on Tailscale, so without a lock
anyone on the same Wi-Fi could read the pieces, spend AI credits or publish to
the site. Every API call now needs a session cookie, obtained with the PIN.

- The PIN is chosen once, from the PC itself (localhost), on first start.
- It is stored as a salted PBKDF2 hash in <storage>/memory/studio_access.json,
  together with the random secret that signs the session cookies.
- The cookie lasts 90 days; 5 wrong PINs from the same address lock it out
  for 15 minutes.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

COOKIE_NAME = "studio_session"
SESSION_SECONDS = 90 * 24 * 3600
PIN_MIN_LENGTH = 6
PIN_MAX_LENGTH = 12
MAX_FAILURES = 5
LOCKOUT_SECONDS = 15 * 60
PBKDF2_ROUNDS = 200_000
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}
# Calls that work without a session: they are how a session is obtained.
OPEN_PATHS = {"/auth/status", "/auth/setup", "/auth/login", "/auth/logout"}

# Turned off only by the test suite (tests/conftest.py), never by an env var.
REQUIRED = True

_store_path: Path | None = None
_failures: dict[str, tuple[int, float]] = {}


def configure(storage_root: Path) -> None:
    global _store_path
    _store_path = storage_root / "memory" / "studio_access.json"


def _load() -> dict:
    if _store_path and _store_path.is_file():
        try:
            data = json.loads(_store_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            return {}
    return {}


def _hash(pin: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ROUNDS).hex()


def is_configured() -> bool:
    data = _load()
    return bool(data.get("pin_hash") and data.get("salt") and data.get("secret"))


def is_local(request: Request) -> bool:
    return bool(request.client and request.client.host in LOCAL_HOSTS)


def valid_pin_format(pin: str) -> bool:
    return pin.isdigit() and PIN_MIN_LENGTH <= len(pin) <= PIN_MAX_LENGTH


def set_pin(pin: str) -> None:
    if _store_path is None:
        raise RuntimeError("studio_auth non configurato")
    salt = secrets.token_hex(16)
    data = {"pin_hash": _hash(pin, salt), "salt": salt, "secret": secrets.token_hex(32)}
    _store_path.parent.mkdir(parents=True, exist_ok=True)
    _store_path.write_text(json.dumps(data), encoding="utf-8")


def verify_pin(pin: str) -> bool:
    data = _load()
    if not data.get("pin_hash") or not data.get("salt"):
        return False
    return hmac.compare_digest(_hash(pin, data["salt"]), data["pin_hash"])


def make_session() -> str:
    expires = int(time.time()) + SESSION_SECONDS
    signature = hmac.new(bytes.fromhex(_load()["secret"]), str(expires).encode(), hashlib.sha256).hexdigest()
    return f"{expires}.{signature}"


def session_valid(value: str | None) -> bool:
    data = _load()
    if not value or not data.get("secret") or "." not in value:
        return False
    expires, signature = value.split(".", 1)
    if not expires.isdigit() or int(expires) < time.time():
        return False
    expected = hmac.new(bytes.fromhex(data["secret"]), expires.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def lockout_seconds(address: str) -> int:
    count, since = _failures.get(address, (0, 0.0))
    if count >= MAX_FAILURES and time.time() - since < LOCKOUT_SECONDS:
        return int(LOCKOUT_SECONDS - (time.time() - since)) + 1
    return 0


def record_failure(address: str) -> None:
    count, since = _failures.get(address, (0, 0.0))
    if time.time() - since > LOCKOUT_SECONDS:
        count, since = 0, time.time()
    _failures[address] = (count + 1, since)


def clear_failures(address: str) -> None:
    _failures.pop(address, None)


def set_cookie(response, request: Request) -> None:
    response.set_cookie(
        COOKIE_NAME,
        make_session(),
        max_age=SESSION_SECONDS,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
        path="/",
    )


class StudioAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if (
            not REQUIRED
            or request.method == "OPTIONS"
            or request.url.path in OPEN_PATHS
            or session_valid(request.cookies.get(COOKIE_NAME))
        ):
            response = await call_next(request)
        else:
            response = JSONResponse({"error": "Studio protetto: serve il PIN.", "auth": "required"}, status_code=401)
        # A photo first loaded by an <img> (no Origin, so no CORS headers) must not
        # be reused from the browser cache when the share button fetches it.
        if "origin" not in response.headers.get("vary", "").lower():
            response.headers.append("Vary", "Origin")
        return response
