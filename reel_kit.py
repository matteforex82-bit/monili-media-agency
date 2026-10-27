"""
reel_kit.py - ricette, Modella Monili, copertina poster e controllo qualita per Reel Studio.

- Skill: ricette editoriali modificabili in skills/*.md (vedi skills_loader.py).
- Modella Monili: un solo personaggio AI ricorrente (descrizione + foto di riferimento).
- Copertina poster: stile editoriale serif su fondo crema, il piu riuscito del feed.
- QA: confronto visivo fotogramma AI vs foto reale prima di animarlo.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

import requests

import skills_loader as skills

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
QA_MIN_SCORE = int(os.environ.get("REEL_QA_MIN_SCORE", "8"))
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

# Le ricette ("skill") sono file Markdown modificabili in skills/: vedi skills_loader.py.
DEFAULT_RECIPE = skills.DEFAULT_SKILL


def select_recipe(requested: str = "") -> str:
    return skills.select_skill(requested)


def recipe_prompt_block(recipe_id: str) -> str:
    skill = skills.load_skill(select_recipe(recipe_id))
    structure = (skill or {}).get("sections", {}).get("structure", "")
    if not skill or not structure:
        return "RICETTA: regia libera - scegli tu la struttura migliore."
    return f"RICETTA OBBLIGATORIA \"{skill['label']}\" - segui questa struttura:\n{structure}"


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
    if model.startswith(OPENAI_DIRECT_PREFIX):
        return openai_edit(model, prompt, images, destination, aspect_ratio)
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


# ── OPENAI DIRETTO (GPT-Image-2.5) ───────────────────────────────────────────
# Su OpenRouter GPT-Image-2.5 non c'e: con OPENAI_API_KEY l'app chiama direttamente /v1/images/edits.
OPENAI_DIRECT_PREFIX = "openai-direct/"
OPENAI_DIRECT_MODELS = {
    "openai-direct/gpt-image-2.5-flare": "gpt-image-2.5-flare",
    "openai-direct/gpt-image-2.5-sunburst": "gpt-image-2.5-sunburst",
    "openai-direct/gpt-image-2": "gpt-image-2",
}
OPENAI_DEFAULT_KEYFRAME_MODEL = "openai-direct/gpt-image-2.5-flare"
OPENAI_DEFAULT_POSTER_MODEL = "openai-direct/gpt-image-2.5-sunburst"
# multipli di 16 come richiesto dall'API; si ritaglia poi a 1080x1920
OPENAI_SIZES = {"9:16": "1152x2048", "4:5": "1088x1360", "1:1": "1024x1024"}


def openai_configured() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def openai_edit(model: str, prompt: str, images: list[Path], destination: Path, aspect_ratio: str = "9:16") -> Path:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY non configurata")
    refs = []
    for image in images:
        if image and image.exists():
            data, media_type = encode_image(image)
            refs.append({"image_url": f"data:{media_type};base64,{data}"})
    payload = {
        "model": OPENAI_DIRECT_MODELS.get(model, model.removeprefix(OPENAI_DIRECT_PREFIX)),
        "prompt": prompt[:32000],
        "images": refs[:16],
        "size": OPENAI_SIZES.get(aspect_ratio, "1024x1536"),
        "quality": os.environ.get("OPENAI_IMAGE_QUALITY", "high"),
        "output_format": "png",
        "n": 1,
    }
    response = requests.post(
        "https://api.openai.com/v1/images/edits",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=300,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI HTTP {response.status_code}: {response.text[:300]}")
    data = (response.json().get("data") or [{}])[0]
    b64 = data.get("b64_json")
    if not b64 or not save_data_url_image(f"data:image/png;base64,{b64}", destination):
        raise RuntimeError("OpenAI: nessuna immagine nella risposta")
    return destination


# ── CONTROLLO QUALITA ────────────────────────────────────────────────────────

def check_keyframe(
    api_key: str,
    text_model: str,
    product_photo: Path,
    keyframe: Path,
    expected_text: str = "",
    scene_anchor: Path | None = None,
    scene_bible: str = "",
) -> dict:
    """Confronta il fotogramma con la foto reale (prodotto) e, se c'e, con il fotogramma guida (scena)."""
    images = [product_photo, keyframe]
    scene_rule = ""
    if scene_anchor and scene_anchor.exists() and scene_anchor != keyframe:
        images.append(scene_anchor)
        scene_rule = (
            "- Immagine 3 = fotogramma guida dello stesso video. L'immagine 2 deve avere lo STESSO luogo, la stessa luce, "
            "la stessa palette colori e (se c'e una donna) la stessa persona con gli stessi abiti.\n"
        )
    elif scene_bible:
        scene_rule = f"- La scena deve rispettare questa descrizione: {scene_bible[:600]}\n"
    text_rule = (
        f'- Il testo nell\'immagine deve essere esattamente "{expected_text}", senza errori di battitura.\n'
        if expected_text
        else ""
    )
    prompt = f"""Sei il controllo qualita severo di una boutique di gioielli. Immagine 1 = foto REALE del prodotto. Immagine 2 = immagine generata dall'AI.
Verifica:
- Il prodotto nell'immagine 2 e IDENTICO all'immagine 1? Forma, numero e taglio delle pietre, colori, metallo, proporzioni. Ogni differenza conta.
- Difetti di generazione: rettangoli/macchie nere, parti mancanti, dita o orecchie deformate, oggetti fusi, scritte strane.
{scene_rule}{text_rule}Rispondi SOLO con JSON: {{"score": 1-10, "same_product": true/false, "scene_consistent": true/false, "artifacts": true/false, "issues": "elenco breve in italiano o stringa vuota"}}"""
    try:
        payload = _chat(api_key, text_model, prompt, images, max_tokens=400)
        result = extract_json_object(extract_text_from_response(payload))
    except Exception as exc:
        return {"ok": False, "score": None, "issues": f"controllo non eseguito: {exc}", "checked": False}
    if not result:
        return {"ok": False, "score": None, "issues": "controllo non leggibile", "checked": False}
    try:
        score = int(result.get("score"))
    except (TypeError, ValueError):
        score = None
    same = result.get("same_product") is True
    scene_ok = result.get("scene_consistent") is not False
    artifacts = result.get("artifacts") is True
    ok = same and scene_ok and not artifacts and score is not None and score >= QA_MIN_SCORE
    return {
        "ok": ok,
        "score": score,
        "same_product": same,
        "scene_consistent": scene_ok,
        "issues": str(result.get("issues") or "").strip(),
        "checked": True,
    }


# ── COPERTINA POSTER ─────────────────────────────────────────────────────────

def poster_prompt(cover_text: str, subtitle: str = "", skill_id: str = "") -> str:
    template = skills.base_template("copertina")
    subtitle_line = f'Small italic subtitle under the headline, exactly once: "{subtitle}"' if subtitle else ""
    return skills.fill(
        template,
        cover_text=cover_text,
        subtitle_line=subtitle_line,
        skill_notes=skills.section(skill_id, "cover") if skill_id else "",
    )


def make_poster_cover(
    api_key: str,
    image_model: str,
    product_photo: Path,
    cover_text: str,
    destination: Path,
    subtitle: str = "",
    skill_id: str = "",
) -> Path:
    raw = destination.with_name(destination.stem + "_raw.png")
    generate_image_multi(api_key, image_model, poster_prompt(cover_text, subtitle, skill_id), [product_photo], raw, aspect_ratio="9:16")
    from PIL import Image, ImageOps

    with Image.open(raw) as img:
        ImageOps.fit(img.convert("RGB"), (1080, 1920), Image.LANCZOS).save(destination, "JPEG", quality=90, optimize=True)
    raw.unlink(missing_ok=True)
    return destination


def copy_file(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return destination
