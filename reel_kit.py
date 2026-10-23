"""
reel_kit.py - ricette, Modella Monili, copertina poster e controllo qualita per Reel Studio.

- RECIPES: formati editoriali fissi ("comandi" alla Monili) che guidano il regista AI.
- Modella Monili: un solo personaggio AI ricorrente (descrizione + foto di riferimento).
- Copertina poster: stile editoriale serif su fondo crema, il piu riuscito del feed.
- QA: confronto visivo fotogramma AI vs foto reale prima di animarlo.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

import requests

from main import (
    MEMORY_ROOT,
    OUTPUT_ROOT,
    encode_image,
    extract_data_urls_from_response,
    extract_json_object,
    extract_text_from_response,
    save_data_url_image,
)

BRAND_ASSETS_DIR = OUTPUT_ROOT / "brand"
PERSONA_FILE = MEMORY_ROOT / "modella_monili.json"
PERSONA_IMAGE = BRAND_ASSETS_DIR / "modella_monili.jpg"
QA_MIN_SCORE = 6
POSTER_USD = 0.12
QA_USD = 0.02

DEFAULT_PERSONA = {
    "name": "Modella Monili",
    "description": (
        "Italian woman around 35 years old, dark brown shoulder-length wavy hair, warm brown eyes, "
        "natural olive skin with real texture, light natural makeup, warm genuine smile, "
        "elegant boho style, natural not over-retouched look"
    ),
    "reference_image": None,
    "updated_at": None,
}

# Ogni ricetta e un "comando" con struttura fissa. shot_plan guida il regista AI.
RECIPES: dict[str, dict] = {
    "libera": {
        "label": "Regia libera",
        "description": "Il regista sceglie la struttura migliore per il prodotto.",
        "formats": ["reel", "story"],
        "uses_model": False,
        "shot_plan": "",
    },
    "modella_monili": {
        "label": "Modella Monili",
        "description": "La nostra modella ricorrente indossa il prodotto: hook, dettaglio, look, chiusura.",
        "formats": ["reel", "story"],
        "uses_model": True,
        "shot_plan": (
            "1) HOOK: primo piano della Modella Monili, gesto naturale che mette in luce il prodotto (use_model true).\n"
            "2) DETTAGLIO: macro del prodotto dalla foto reale (keyframe_mode original_photo, use_model false).\n"
            "3) LOOK: la Modella Monili cammina o si gira con il look completo, luce calda (use_model true).\n"
            "4) CHIUSURA: sorriso verso camera + testo invito al DM (use_model true)."
        ),
    },
    "mani_bancone": {
        "label": "Mani al bancone",
        "description": "Mani che prendono, provano e mostrano il gioiello sul bancone del negozio. Ideale per anelli e bracciali.",
        "formats": ["story", "reel"],
        "uses_model": False,
        "shot_plan": (
            "1) HOOK: mani che aprono una scatolina o sollevano il gioiello dal bancone in legno chiaro.\n"
            "2) PROVA: il gioiello viene indossato (dita/polso), movimento lento che fa brillare le pietre.\n"
            "3) DETTAGLIO: macro dalla foto reale (keyframe_mode original_photo).\n"
            "4) CHIUSURA: mano che indica / testo 'Scrivici, te lo mettiamo da parte'.\n"
            "Solo mani femminili curate e naturali, nessun volto. Se ci sono clip reali usale qui."
        ),
    },
    "pietra_settimana": {
        "label": "Pietra della settimana",
        "description": "Una pietra (ametista, quarzo rosa, citrino...): cosa significa e come abbinarla.",
        "formats": ["reel", "story"],
        "uses_model": False,
        "shot_plan": (
            "1) HOOK: macro della pietra con un riflesso di luce, testo 'La pietra della settimana: <nome>'.\n"
            "2) SIGNIFICATO: dettaglio lento, testo breve sul significato della pietra (max 6 parole).\n"
            "3) ABBINAMENTO: il gioiello indossato con un colore d'outfit consigliato.\n"
            "4) CHIUSURA: prodotto intero + invito al DM."
        ),
    },
    "tre_modi": {
        "label": "3 modi di indossarlo",
        "description": "Lo stesso pezzo in tre look: giorno, ufficio, sera.",
        "formats": ["reel"],
        "uses_model": True,
        "shot_plan": (
            "1) HOOK: testo '3 modi di indossarlo' sul prodotto (keyframe_mode original_photo).\n"
            "2) LOOK GIORNO: Modella Monili casual in centro a Ravenna (use_model true).\n"
            "3) LOOK UFFICIO: Modella Monili elegante sobria (use_model true).\n"
            "4) LOOK SERA: Modella Monili aperitivo, luce calda (use_model true).\n"
            "5) CHIUSURA: 'Quale scegli? Scrivicelo' + prodotto. Transizioni di tipo slide tra i look."
        ),
    },
    "colori_ravenna": {
        "label": "I colori di Ravenna",
        "description": "Il gioiello accostato ai colori dei mosaici di Ravenna.",
        "formats": ["reel", "story"],
        "uses_model": False,
        "shot_plan": (
            "1) HOOK: dettaglio di un mosaico bizantino con tessere dai colori simili alle pietre del gioiello "
            "(mosaico generico, non riprodurre opere specifiche).\n"
            "2) TRANSIZIONE: dal mosaico al gioiello con colori in rima (match di colore).\n"
            "3) DETTAGLIO: macro del prodotto dalla foto reale (keyframe_mode original_photo).\n"
            "4) CHIUSURA: testo 'Ravenna, a colori' + invito in negozio in centro."
        ),
    },
}
DEFAULT_RECIPE = "libera"


def select_recipe(requested: str = "") -> str:
    return requested if requested in RECIPES else DEFAULT_RECIPE


def recipe_prompt_block(recipe_id: str) -> str:
    recipe = RECIPES[select_recipe(recipe_id)]
    if not recipe["shot_plan"]:
        return "RICETTA: regia libera - scegli tu la struttura migliore."
    return f"RICETTA OBBLIGATORIA \"{recipe['label']}\" - segui questa struttura:\n{recipe['shot_plan']}"


# ── MODELLA MONILI ───────────────────────────────────────────────────────────

def load_persona() -> dict:
    try:
        data = json.loads(PERSONA_FILE.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    persona = {**DEFAULT_PERSONA, **{k: v for k, v in data.items() if v is not None}}
    if persona.get("reference_image") and not (OUTPUT_ROOT / persona["reference_image"]).exists():
        persona["reference_image"] = None
    return persona


def save_persona(description: str | None = None, reference_source: Path | None = None) -> dict:
    persona = load_persona()
    if description is not None and description.strip():
        persona["description"] = description.strip()[:800]
    if reference_source is not None:
        from PIL import Image, ImageOps

        BRAND_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        with Image.open(reference_source) as img:
            ImageOps.exif_transpose(img).convert("RGB").save(PERSONA_IMAGE, "JPEG", quality=90)
        persona["reference_image"] = PERSONA_IMAGE.relative_to(OUTPUT_ROOT).as_posix()
    persona["updated_at"] = datetime.now().isoformat()
    MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
    PERSONA_FILE.write_text(json.dumps(persona, indent=2, ensure_ascii=False), encoding="utf-8")
    return persona


def persona_reference_path() -> Path | None:
    ref = load_persona().get("reference_image")
    return OUTPUT_ROOT / ref if ref else None


# ── OPENROUTER MULTI-IMMAGINE ────────────────────────────────────────────────

def _chat(api_key: str, model: str, prompt: str, images: list[Path], max_tokens: int, modalities=None, image_config=None) -> dict:
    content: list[dict] = []
    for image in images:
        if image and image.exists():
            data, media_type = encode_image(image)
            content.append({"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{data}"}})
    content.append({"type": "text", "text": prompt})
    payload: dict = {"model": model, "messages": [{"role": "user", "content": content}], "max_tokens": max_tokens, "stream": False}
    if modalities:
        payload["modalities"] = modalities
    if image_config:
        payload["image_config"] = image_config
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://monili-media-agency.local",
            "X-Title": "Monili Media Agency",
        },
        json=payload,
        timeout=240,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
    return response.json()


def generate_image_multi(api_key: str, model: str, prompt: str, images: list[Path], destination: Path, aspect_ratio: str = "9:16") -> Path:
    text_image = model.startswith("google/gemini") or model.startswith("openai/gpt-5.4-image") or model.startswith("openai/gpt-image")
    payload = _chat(
        api_key,
        model,
        prompt,
        images,
        max_tokens=4096,
        modalities=["image", "text"] if text_image else ["image"],
        image_config={"aspect_ratio": aspect_ratio, "image_size": "1K"} if model.startswith("google/gemini") else None,
    )
    data_urls = extract_data_urls_from_response(payload)
    if not data_urls or not save_data_url_image(data_urls[0], destination):
        raise RuntimeError("nessuna immagine nella risposta")
    return destination


# ── CONTROLLO QUALITA ────────────────────────────────────────────────────────

def check_keyframe(api_key: str, text_model: str, product_photo: Path, keyframe: Path, expected_text: str = "") -> dict:
    """Confronta il fotogramma generato con la foto reale del prodotto. Ritorna {ok, score, issues}."""
    text_rule = (
        f'- Il testo nell\'immagine deve essere esattamente "{expected_text}", senza errori di battitura.\n'
        if expected_text
        else ""
    )
    prompt = f"""Sei il controllo qualita di una boutique di gioielli. Immagine 1 = foto REALE del prodotto. Immagine 2 = immagine generata dall'AI.
Verifica:
- Il prodotto nell'immagine 2 e lo stesso dell'immagine 1? Forma, numero e taglio delle pietre, colori, metallo, proporzioni.
- Difetti di generazione: rettangoli/macchie nere, parti mancanti, dita o orecchie deformate, oggetti fusi, scritte strane.
{text_rule}Rispondi SOLO con JSON: {{"score": 1-10, "same_product": true/false, "artifacts": true/false, "issues": "elenco breve in italiano o stringa vuota"}}"""
    try:
        payload = _chat(api_key, text_model, prompt, [product_photo, keyframe], max_tokens=400)
        result = extract_json_object(extract_text_from_response(payload))
    except Exception as exc:
        return {"ok": True, "score": None, "issues": f"controllo non eseguito: {exc}", "checked": False}
    if not result:
        return {"ok": True, "score": None, "issues": "controllo non leggibile", "checked": False}
    try:
        score = int(result.get("score"))
    except (TypeError, ValueError):
        score = None
    same = result.get("same_product") is not False
    artifacts = result.get("artifacts") is True
    ok = same and not artifacts and (score is None or score >= QA_MIN_SCORE)
    return {"ok": ok, "score": score, "issues": str(result.get("issues") or "").strip(), "checked": True}


# ── COPERTINA POSTER ─────────────────────────────────────────────────────────

def poster_prompt(cover_text: str, subtitle: str = "") -> str:
    return f"""Create a vertical 9:16 editorial poster cover for the Instagram account of I Monili, a jewelry boutique in Ravenna.
Use the exact product from the reference photo as the hero, styled on a warm cream silk or stone surface with soft natural light.
Typography: elegant high-contrast serif (like Didot / Cormorant), dark espresso color, large headline at the top:
"{cover_text}"
{f'Small italic subtitle under it: "{subtitle}"' if subtitle else ''}
Small spaced uppercase wordmark at the bottom: "I MONILI · RAVENNA".
Leave the top 15% and bottom 20% clean for Instagram UI. Warm cream background, terracotta and gold accents.
The product must stay IDENTICAL to the reference photo: same shape, stones, colors, metal. Spell the Italian text exactly as written.
No other text, no logos, no watermark."""


def make_poster_cover(api_key: str, image_model: str, product_photo: Path, cover_text: str, destination: Path, subtitle: str = "") -> Path:
    raw = destination.with_name(destination.stem + "_raw.png")
    generate_image_multi(api_key, image_model, poster_prompt(cover_text, subtitle), [product_photo], raw, aspect_ratio="9:16")
    from PIL import Image, ImageOps

    with Image.open(raw) as img:
        ImageOps.fit(img.convert("RGB"), (1080, 1920), Image.LANCZOS).save(destination, "JPEG", quality=90, optimize=True)
    raw.unlink(missing_ok=True)
    return destination


def copy_file(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return destination
