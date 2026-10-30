"""
photo_cleanup.py - la foto vera del pezzo, ripulita per il sito senza ridisegnarla con l'AI.

- Scontorno: BiRefNet (modello ONNX, gira sul PC, gratis). Si scarica da solo la prima volta (~1 GB).
- Luce, bilanciamento del bianco e contrasto: corretti solo sul pezzo.
- Fondo avorio 4:5 con ombra morbida, come le altre foto del sito.
- I pixel del pezzo restano quelli della foto: niente viene inventato.
- Controllo: se lo scontorno tocca il bordo o non trova il pezzo, la foto non viene suggerita.
"""

import hashlib
import os
from pathlib import Path
from typing import Callable

import numpy as np
import requests
from PIL import Image, ImageEnhance, ImageFilter

MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-general-epoch_244.onnx"
MODEL_MD5 = "7a35a0141cbbc80de11d9c9a28f52697"
MODEL_FILENAME = "birefnet-general.onnx"
MODEL_INPUT = (1024, 1024)

CANVAS = (1200, 1500)
IVORY_CENTER = np.array([252, 249, 243], dtype=np.float32)
IVORY_EDGE = np.array([241, 235, 224], dtype=np.float32)
SHADOW_RGB = (110, 86, 62)

MIN_COVERAGE = 0.02
MAX_COVERAGE = 0.92
MAX_EDGE_TOUCH = 0.005

_SESSIONS: dict[str, object] = {}


class CleanupError(Exception):
    pass


def auto_download_enabled() -> bool:
    return os.environ.get("CUTOUT_MODEL_AUTO_DOWNLOAD", "1").strip() != "0"


def ensure_model(path: Path, notify: Callable[[str], None] | None = None) -> Path:
    """The cutout model on disk, downloaded and checked the first time it is needed."""
    if path.exists():
        return path
    if not auto_download_enabled():
        raise CleanupError(f"modello di scontorno assente ({path})")
    if notify:
        notify("Scarico il modello di scontorno (circa 1 GB, solo la prima volta)...")
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".part")
    digest = hashlib.md5()
    try:
        with requests.get(MODEL_URL, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(partial, "wb") as handle:
                for chunk in response.iter_content(chunk_size=1 << 20):
                    handle.write(chunk)
                    digest.update(chunk)
        if digest.hexdigest() != MODEL_MD5:
            raise CleanupError("modello di scontorno scaricato male (checksum diverso)")
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)
    return path


def _session(model_path: Path):
    key = str(model_path)
    if key not in _SESSIONS:
        import onnxruntime as ort

        _SESSIONS[key] = ort.InferenceSession(key, providers=["CPUExecutionProvider"])
    return _SESSIONS[key]


def predict_alpha(photo: Image.Image, model_path: Path) -> np.ndarray:
    """Cutout mask, 0..1, the size of the photo."""
    session = _session(model_path)
    small = photo.resize(MODEL_INPUT, Image.Resampling.LANCZOS)
    ary = np.asarray(small, dtype=np.float32)
    ary = ary / max(float(ary.max()), 1e-6)
    ary = (ary - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    tensor = ary.transpose(2, 0, 1)[None].astype(np.float32)
    out = session.run(None, {session.get_inputs()[0].name: tensor})[0][0, 0]
    pred = 1 / (1 + np.exp(-out))
    pred = (pred - pred.min()) / max(float(pred.max() - pred.min()), 1e-6)
    mask = Image.fromarray((pred * 255).astype("uint8")).resize(photo.size, Image.Resampling.LANCZOS)
    # Bordi un po' più decisi: niente alone grigio intorno al pezzo.
    alpha = np.asarray(mask, dtype=np.float32) / 255
    return np.clip((alpha - 0.08) / 0.84, 0, 1)


def check_cutout(alpha: np.ndarray) -> list[str]:
    """Reasons not to suggest the photo; empty when the cutout looks clean."""
    solid = alpha > 0.5
    coverage = float(solid.mean())
    if coverage < MIN_COVERAGE:
        return ["Lo scontorno non ha trovato il pezzo"]
    if coverage > MAX_COVERAGE:
        return ["Lo scontorno ha preso quasi tutta la foto"]
    edges = (solid[0], solid[-1], solid[:, 0], solid[:, -1])
    if max(float(edge.mean()) for edge in edges) > MAX_EDGE_TOUCH:
        return ["Il pezzo tocca il bordo della foto: forse c'è un oggetto attaccato o il pezzo è tagliato"]
    return []


def white_balance_gains(photo: Image.Image, alpha: np.ndarray) -> np.ndarray:
    """Colour cast measured on a light, neutral background (wall or white sheet).

    With a coloured background (e.g. an orange wall) nothing is corrected."""
    rgb = np.asarray(photo, dtype=np.float32)
    lum = rgb.mean(axis=2)
    spread = rgb.max(axis=2) - rgb.min(axis=2)
    candidates = (alpha < 0.05) & (lum > 150) & (spread < 0.22 * lum)
    if candidates.sum() < 0.03 * alpha.size:
        return np.ones(3, dtype=np.float32)
    ref = rgb[candidates].mean(axis=0)
    return np.clip(ref.mean() / ref, 0.88, 1.12).astype(np.float32)


def correct_product(photo: Image.Image, alpha: np.ndarray) -> Image.Image:
    rgb = np.asarray(photo, dtype=np.float32) * white_balance_gains(photo, alpha)
    product = alpha > 0.5
    lum = rgb.mean(axis=2)
    lo, hi = np.percentile(lum[product], [0.5, 99.5]) if product.any() else (0.0, 255.0)
    # Livelli: allunga il contrasto del pezzo, ma con calma (70% della correzione piena).
    stretched = (rgb - lo) * (248.0 / max(float(hi - lo), 1.0)) + 4
    rgb = 0.3 * rgb + 0.7 * stretched

    # Esposizione: se il pezzo è scuro, alza i mezzi toni senza bruciare le luci.
    median = float(np.median(np.clip(rgb, 0, 255).mean(axis=2)[product])) if product.any() else 128.0
    if median < 115:
        gamma = float(np.interp(median, [60, 115], [0.78, 0.95]))
        rgb = 255 * (np.clip(rgb, 0, 255) / 255) ** gamma

    out = Image.fromarray(np.clip(rgb, 0, 255).astype("uint8"))
    out = ImageEnhance.Color(out).enhance(1.06)
    return out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=3))


def ivory_background() -> Image.Image:
    w, h = CANVAS
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    distance = np.sqrt(((xx - w / 2) / (w * 0.75)) ** 2 + ((yy - h * 0.45) / (h * 0.75)) ** 2)
    t = np.clip(distance, 0, 1)[..., None]
    return Image.fromarray((IVORY_CENTER * (1 - t) + IVORY_EDGE * t).astype("uint8"))


def compose(product: Image.Image, mask: Image.Image) -> Image.Image:
    box = mask.point(lambda v: 255 if v > 20 else 0).getbbox()
    if not box:
        raise CleanupError("scontorno vuoto")
    product, mask = product.crop(box), mask.crop(box)

    scale = min(CANVAS[0] * 0.80 / product.width, CANVAS[1] * 0.76 / product.height)
    size = (max(1, round(product.width * scale)), max(1, round(product.height * scale)))
    product = product.resize(size, Image.Resampling.LANCZOS)
    mask = mask.resize(size, Image.Resampling.LANCZOS)

    canvas = ivory_background()
    x = (CANVAS[0] - size[0]) // 2
    y = int((CANVAS[1] - size[1]) * 0.46)

    # Ombra morbida che segue la forma del pezzo, appena spostata in basso: niente ombra "a terra",
    # così capi appesi e gioielli non sembrano sospesi.
    shadow = Image.new("L", CANVAS, 0)
    shadow.paste(mask, (x + 6, y + 10))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.30))
    canvas = Image.composite(Image.new("RGB", CANVAS, SHADOW_RGB), canvas, shadow)

    canvas.paste(product, (x, y), mask)
    return canvas


def clean_photo(
    photo: Image.Image, model_path: Path, notify: Callable[[str], None] | None = None
) -> tuple[Image.Image, list[str]]:
    """The real photo on the ivory 4:5 background, plus the reasons not to suggest it (if any)."""
    photo = photo.convert("RGB")
    alpha = predict_alpha(photo, ensure_model(model_path, notify))
    issues = check_cutout(alpha)
    mask = Image.fromarray((alpha * 255).astype("uint8"))
    return compose(correct_product(photo, alpha), mask), issues
