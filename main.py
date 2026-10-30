"""
main.py - MONILI MEDIA AGENCY
Pipeline AI completa via OpenRouter (testo + immagini).
"""

import argparse
import base64
import json
import os
import re
import sys
import traceback
import uuid
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image, ImageOps

load_dotenv(encoding="utf-8-sig")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SUPPORTED_OPENROUTER_IMAGE_MODELS = [
    "openai/gpt-5.4-image-2",
    "google/gemini-3.1-flash-image-preview",
    "google/gemini-3.1-flash-image",
    "google/gemini-3-pro-image",
]
DEFAULT_OPENROUTER_IMAGE_MODEL = SUPPORTED_OPENROUTER_IMAGE_MODELS[0]

SUPPORTED_OPENROUTER_TEXT_MODELS = [
    "openai/gpt-5.5",
    "openai/gpt-4.1-mini",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-5.5",
]
DEFAULT_OPENROUTER_TEXT_MODEL = SUPPORTED_OPENROUTER_TEXT_MODELS[0]
PROJECT_ROOT = Path(__file__).parent


def resolve_storage_root() -> Path:
    configured = os.environ.get("MONILI_STORAGE_DIR", "").strip()
    if not configured:
        return PROJECT_ROOT
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


STORAGE_ROOT = resolve_storage_root()
OUTPUT_ROOT = STORAGE_ROOT / "output"
MEMORY_ROOT = STORAGE_ROOT / "memory"
CUTOUT_MODEL_PATH = Path(
    os.environ.get("CUTOUT_MODEL_PATH", "").strip() or STORAGE_ROOT / "models" / "birefnet-general.onnx"
)


def log(agent: str, msg: str, kind: str = "info"):
    icons = {"info": ">", "success": "[OK]", "data": "[DATA]", "warn": "!"}
    print(f"[{agent}] {icons.get(kind, '>')} {msg}", flush=True)


def encode_image(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    media_type = media_types.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def select_openrouter_image_model(requested_model: str = "") -> str:
    model = (requested_model or "").strip()
    if model:
        return model
    env_model = os.environ.get("OPENROUTER_IMAGE_MODEL", "").strip()
    if env_model:
        return env_model
    return DEFAULT_OPENROUTER_IMAGE_MODEL


def select_openrouter_text_model(requested_model: str = "") -> str:
    model = (requested_model or "").strip()
    if model:
        return model
    env_model = os.environ.get("OPENROUTER_TEXT_MODEL", "").strip()
    if env_model:
        return env_model
    return DEFAULT_OPENROUTER_TEXT_MODEL


def extract_text_from_response(payload: dict) -> str:
    choices = payload.get("choices", [])
    if not choices:
        return ""

    message = choices[0].get("message", {})
    content = message.get("content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
        return "\n".join(chunks).strip()

    return ""


def openrouter_chat_completion(
    api_key: str,
    model: str,
    prompt: str,
    image_path: Path | None = None,
    max_tokens: int = 2048,
    modalities: list[str] | None = None,
    image_config: dict | None = None,
) -> dict:
    if image_path and image_path.exists():
        image_data, media_type = encode_image(image_path)
        content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{image_data}"},
            },
            {"type": "text", "text": prompt},
        ]
    else:
        content = prompt

    payload: dict = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "stream": False,
    }

    if modalities:
        payload["modalities"] = modalities
    if image_config:
        payload["image_config"] = image_config

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://monili-media-agency.local",
        "X-Title": "Monili Media Agency",
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=180,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:350]}")
    return response.json()


def generate_text_with_openrouter(
    api_key: str,
    model: str,
    prompt: str,
    image_path: Path | None = None,
    max_tokens: int = 2048,
) -> str:
    try:
        payload = openrouter_chat_completion(
            api_key=api_key,
            model=model,
            prompt=prompt,
            image_path=image_path,
            max_tokens=max_tokens,
        )
        text = extract_text_from_response(payload)
        return text if text else "[Errore API: risposta testuale vuota]"
    except Exception as e:
        return f"[Errore API: {e}]"


def extract_data_urls_from_response(payload: dict) -> list[str]:
    choices = payload.get("choices", [])
    if not choices:
        return []

    message = choices[0].get("message", {})
    urls: list[str] = []

    for image in message.get("images", []) or []:
        image_url = image.get("image_url", {})
        url = image_url.get("url")
        if isinstance(url, str) and url.startswith("data:image/"):
            urls.append(url)

    content = message.get("content", [])
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            image_url = part.get("image_url", {})
            url = image_url.get("url")
            if isinstance(url, str) and url.startswith("data:image/"):
                urls.append(url)

    return urls


def save_data_url_image(data_url: str, destination: Path) -> bool:
    if "," not in data_url:
        return False
    header, b64_data = data_url.split(",", 1)
    if ";base64" not in header:
        return False

    try:
        raw_bytes = base64.b64decode(b64_data)
    except Exception:
        return False

    destination.write_bytes(raw_bytes)
    return True


def save_jpeg_budget(img: Image.Image, destination: Path, target_kb: int = 420) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    for quality in (88, 84, 80, 76, 72):
        img.save(destination, "JPEG", quality=quality, optimize=True, progressive=True)
        if destination.stat().st_size <= target_kb * 1024:
            return destination
    return destination


def export_ratio_jpeg(
    source_path: Path,
    destination: Path,
    size: tuple[int, int],
    mode: str = "fit",
    target_kb: int = 420,
) -> Path:
    with Image.open(source_path) as source:
        image = source.convert("RGB")
        if mode == "contain":
            image.thumbnail((size[0] - 80, size[1] - 80), Image.LANCZOS)
            canvas = Image.new("RGB", size, (250, 247, 240))
            offset = ((size[0] - image.width) // 2, (size[1] - image.height) // 2)
            canvas.paste(image, offset)
            final = canvas
        else:
            final = ImageOps.fit(image, size, Image.LANCZOS, centering=(0.5, 0.5))
    return save_jpeg_budget(final, destination, target_kb=target_kb)


def generate_image_with_openrouter(
    api_key: str,
    model: str,
    prompt: str,
    image_path: Path | None = None,
    aspect_ratio: str = "1:1",
) -> list[str]:
    text_image_models = (
        model.startswith("google/gemini")
        or model.startswith("openai/gpt-5.4-image")
        or model.startswith("openai/gpt-image")
    )
    modalities = ["image", "text"] if text_image_models else ["image"]
    image_config = {"aspect_ratio": aspect_ratio, "image_size": "1K"} if model.startswith("google/gemini") else None

    payload = openrouter_chat_completion(
        api_key=api_key,
        model=model,
        prompt=prompt,
        image_path=image_path,
        modalities=modalities,
        image_config=image_config,
    )

    data_urls = extract_data_urls_from_response(payload)
    if not data_urls:
        raise RuntimeError("Nessuna immagine trovata nella risposta OpenRouter")
    return data_urls


def load_prompt_knowledge() -> str:
    path = Path(__file__).parent / "knowledge" / "nano_banana_2_prompts.md"
    try:
        return path.read_text(encoding="utf-8")[:3500]
    except Exception:
        return ""


def extract_json_object(raw_text: str) -> dict:
    if not raw_text:
        return {}

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        pass

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        return {}

    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def normalize_string_list(value: object, max_items: int = 30) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value[:max_items]:
        if isinstance(item, str):
            v = item.strip()
            if v:
                out.append(v)
    return out


def current_season_label(now: datetime | None = None) -> str:
    now = now or datetime.now()
    if 3 <= now.month <= 8:
        return f"Primavera/Estate {now.year}"
    start_year = now.year if now.month >= 9 else now.year - 1
    return f"Autunno/Inverno {start_year}/{str(start_year + 1)[-2:]}"


SEASON = current_season_label()

BRAND = f"""
BRAND: I Monili Ravenna - boutique in centro storico a Ravenna (Emilia-Romagna)
Prodotti: bijoux artigianali in argento con pietre colorate (ametista, quarzo rosa, citrino, turchese, opale),
orecchini smaltati a fiore, giacche e gilet ricamati, borse in cuoio, abbigliamento dal gusto boho-etnico
Identita: colorata, artigianale, eclettica, pezzi particolari che non si trovano nelle catene
Target: donna 30-55, Ravenna e dintorni, ama i pezzi unici e il colore
Tono: caldo, complice, femminile - come un'amica che consiglia, non un brand che vende
Stagione: {SEASON}
Hashtag fissi: #imoniliravenna #ravenna #romagnastyle
Stile visivo: luce naturale calda, sfondi crema/neutri che fanno risaltare i colori dei prodotti;
testi in stile editoriale (serif elegante su fondo crema), mai scritte stile fumetto o neon
Formati prioritari: Story video e Reel (i post statici fanno il 4% delle visualizzazioni)
Chiusura di ogni contenuto: invito concreto al DM ("scrivici, te lo mettiamo da parte") o a passare in negozio
Ravenna: citta dei mosaici - il legame colori/pietre/mosaico e un tema naturale
Posting: Martedi/Giovedi/Sabato (orari in verifica sugli Insights)
"""


FIXED_HASHTAGS = ["#imoniliravenna", "#ravenna", "#romagnastyle"]
MAX_EXTRA_HASHTAGS = 2


def agent_analisi(text_model: str, api_key: str, foto: Path, brief: str) -> str:
    log("ANALISTA", "Analisi multimodale foto prodotto...")
    log("ANALISTA", "Caricamento immagine in Vision AI...", "data")
    prompt = f"""Sei un esperto analista di prodotti fashion e bijoux.
{BRAND}
Brief aggiuntivo: {brief if brief else "Nessun brief - analizza autonomamente dalla foto"}

Analizza questa foto prodotto e crea una scheda completa:

## IDENTIFICAZIONE
- Categoria esatta
- Materiali identificati con certezza: scrivi solo quelli sicuri; le ipotesi vanno tra parentesi con "probabilmente"
- Colori principali con codici HEX stimati
- Dimensioni stimate
- Tecnica di realizzazione (se visibile)

## MOOD & POSIZIONAMENTO
- Stile/mood (minimal, boho, elegante, casual, statement...)
- Occasione d'uso consigliata
- Adatto alla stagione {SEASON}: si/no e perche
- Fascia di prezzo stimata (se non nel brief)
- Punti di forza visivi da valorizzare
- Abbinamenti outfit suggeriti (3 look)

## DESCRIZIONE AI
Descrizione del prodotto in italiano utile per local SEO, scheda sito e alt text, max 100 parole.

Rispondi in italiano, formato markdown."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1800)
    log("ANALISTA", "Prodotto classificato - dati pronti per il team", "success")
    return result


def scheda_plan_defaults() -> dict:
    return {
        "styling": "",
        "woman": "",
        "site_prompts": {
            "clean": (
                "Clean premium catalog photo of the product, centered on a warm ivory background, "
                "soft natural light, generous negative space, no model."
            ),
            "worn": (
                "The product worn naturally by the woman described below, warm natural boutique light, "
                "correct scale and fit, product in sharp focus."
            ),
        },
    }


def agent_scheda_plan(text_model: str, api_key: str, foto: Path, analisi: str, brief: str) -> dict:
    """One call for styling notes and the two site photo prompts (it replaces four agents)."""
    log("PIANO SCHEDA", "Styling e prompt delle foto sito (catalogo + indossato)...")
    import casting

    prompt = f"""Sei l'art director del sito vetrina di I Monili Ravenna. Devi restituire SOLO un JSON valido.
{BRAND}
Knowledge prompt immagine:
{load_prompt_knowledge()}

Analisi prodotto: {analisi[:1400]}
Brief utente: {brief if brief else "Nessun brief"}

LA DONNA DI QUESTO PEZZO: la inventi tu. {casting.woman_guide()}
Sara lei anche nei Reel di questo pezzo, come una modella ingaggiata per lui.
{casting.avoid_block("DONNE GIA USATE DI RECENTE", casting.recent_women())}
COSE DA NON MOSTRARE MAI: {"; ".join(casting.never_show()) or "nessuna"}

JSON esatto:
{{
  "styling": "2-3 frasi in italiano: come si indossa e con cosa abbinarlo",
  "woman": "in inglese, 1-2 frasi: eta, corporatura, viso, capelli e stile della donna che inventi per questo pezzo",
  "site_prompts": {{
    "clean": "prompt in inglese: clean product catalog photo, warm ivory background, no model, product centered, generous negative space",
    "worn": "prompt in inglese: product worn naturally by the woman (hand/ear/neck/body depending on the product), correct scale and fit; luogo, posa, luce e abiti li inventi tu, adatti al pezzo e allo stile del negozio"
  }}
}}

Regole per i prompt:
- Nel prompt "worn" sii creativo su luogo e posa, ma la donna descrivila solo nel campo "woman": lo Studio la aggiunge al prompt.
- La foto caricata e la fonte di verita: forma, colore, materiale, proporzioni, pietre e dettagli identici.
- Fotorealistico, pulito, nitido, composizione sicura per card 4:5.
- Niente testo leggibile, loghi, watermark, telefoni, UI, collage o pannelli multipli.
- Niente testo fuori dal JSON."""
    raw = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1200)
    parsed = extract_json_object(raw)
    plan = scheda_plan_defaults()
    if not parsed:
        log("PIANO SCHEDA", "JSON non valido, uso prompt standard", "warn")
        return plan
    plan["styling"] = str(parsed.get("styling", "")).strip()
    plan["woman"] = " ".join(str(parsed.get("woman", "")).split())[:600]
    prompts = parsed.get("site_prompts") if isinstance(parsed.get("site_prompts"), dict) else {}
    for key in ("clean", "worn"):
        value = str(prompts.get(key, "")).strip()
        if value:
            plan["site_prompts"][key] = value
    log("PIANO SCHEDA", "Styling e prompt foto sito pronti", "success")
    return plan


WORN_PHOTO_NAME = "site_02_worn.jpg"
SITE_IMAGE_SPECS = [
    ("clean", "site_product_clean_source.png", "site_01_product_clean.jpg"),
    ("worn", "site_worn_source.png", WORN_PHOTO_NAME),
]
REAL_PHOTO_NAME = "site_03_real_photo.jpg"


def generate_showcase_images(
    output_dir: Path,
    api_key: str,
    selected_model: str,
    foto: Path,
    site_prompts: dict,
    woman: str = "",
) -> list[str]:
    if not api_key:
        log("SITO VISUAL", "OPENROUTER_API_KEY mancante - salto immagini sito dedicate", "warn")
        return []

    import casting

    model = select_openrouter_image_model(selected_model)
    never = casting.never_line()
    source_dir = output_dir / "07_SHOWCASE" / "sources"
    final_dir = output_dir / "07_SHOWCASE"
    source_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []

    for index, (key, source_name, final_name) in enumerate(SITE_IMAGE_SPECS, start=1):
        prompt = str(site_prompts.get(key, "")).strip()
        if not prompt:
            log("SITO VISUAL", f"Prompt mancante: {key}", "warn")
            continue
        if key == "worn" and woman:
            prompt = f"{prompt}\nWOMAN (this replaces any other description of her): {woman}"
        try:
            log("SITO VISUAL", f"Generazione foto sito {index}/{len(SITE_IMAGE_SPECS)}", "data")
            controlled = f"""{prompt}

Use the uploaded reference photo as source-of-truth for the product.
Preserve exact product shape, color, material, proportions, stones and distinctive details.
Create a single website-ready product photograph, composed safely for 4:5 product cards.
No text, no logos, no watermark, no phone screens, no fake UI.
{never}"""
            data_urls = generate_image_with_openrouter(
                api_key,
                model,
                controlled,
                image_path=foto,
                aspect_ratio="4:5",
            )
            if not data_urls:
                continue
            source_path = source_dir / source_name
            if not save_data_url_image(data_urls[0], source_path):
                continue
            final_path = final_dir / final_name
            export_ratio_jpeg(source_path, final_path, (1200, 1500), mode="fit", target_kb=420)
            generated.append(f"{output_dir.name}/07_SHOWCASE/{final_name}")
        except Exception as e:
            log("SITO VISUAL", f"Foto {key} non generata: {e}", "warn")

    if generated:
        log("SITO VISUAL", f"{len(generated)} foto sito dedicate create in 07_SHOWCASE", "success")
    else:
        log("SITO VISUAL", "Nessuna foto sito dedicata generata", "warn")
    return generated


def create_real_photo_image(output_dir: Path, source_path: Path) -> tuple[str, dict]:
    """The real photo cut out, with light fixed, on the ivory 4:5 background (free, done on the PC).

    The piece is never redrawn by AI. If the cleanup fails, the plain 4:5 crop is kept,
    and in both cases the photo is suggested for the site only when the cutout looks clean."""
    final_dir = output_dir / "07_SHOWCASE"
    final_dir.mkdir(parents=True, exist_ok=True)
    destination = final_dir / REAL_PHOTO_NAME
    try:
        import photo_cleanup

        with Image.open(source_path) as source:
            photo = ImageOps.exif_transpose(source).convert("RGB")
        cleaned, issues = photo_cleanup.clean_photo(
            photo, CUTOUT_MODEL_PATH, notify=lambda msg: log("SITO VISUAL", msg, "data")
        )
        save_jpeg_budget(cleaned, destination, target_kb=420)
        check = {"cleaned": True, "ok": not issues, "issues": issues}
        if issues:
            log("SITO VISUAL", f"Foto reale ripulita ma non suggerita: {issues[0]}", "warn")
        else:
            log("SITO VISUAL", "Foto reale ripulita: fondo avorio, luce e colore sistemati", "success")
    except Exception as e:
        export_ratio_jpeg(source_path, destination, (1200, 1500), mode="fit", target_kb=420)
        check = {"cleaned": False, "ok": False, "issues": [f"Foto reale non ripulita ({e}): c'è solo il ritaglio"]}
        log("SITO VISUAL", check["issues"][0], "warn")
    return f"{output_dir.name}/07_SHOWCASE/{REAL_PHOTO_NAME}", check


def image_file_report(relative_path: str) -> dict:
    path = OUTPUT_ROOT / relative_path
    if not path.exists() or not path.is_file():
        return {"src": relative_path, "ok": False, "reason": "missing"}
    try:
        with Image.open(path) as img:
            width, height = img.size
        return {
            "src": relative_path,
            "ok": True,
            "width": width,
            "height": height,
            "ratio": round(width / height, 4) if height else 0,
            "kb": round(path.stat().st_size / 1024, 1),
        }
    except Exception as exc:
        return {"src": relative_path, "ok": False, "reason": str(exc)}


def build_decision_summary(publish_pack: dict, ai_site_images: list[str], real_photo_check: dict | None = None) -> str:
    lines = [
        "COSA FARE ORA",
        "1. Scegli le foto, metti il prezzo e premi \"Pubblica sul sito vetrina\".",
        "2. Gira il link del pezzo su WhatsApp con il messaggio pronto.",
        "3. Pubblica il post su Google Business.",
        "4. Per Instagram fai il Reel o la Storia di questo pezzo nel Reel Studio.",
    ]
    if not ai_site_images:
        lines.append("Foto AI non riuscite: per il sito c'è solo la foto reale.")
    if real_photo_check and not real_photo_check.get("ok"):
        issue = (real_photo_check.get("issues") or ["da controllare"])[0]
        lines.append(f"Foto reale non spuntata: {issue}. Guardala prima di aggiungerla.")
    whatsapp = str(publish_pack.get("whatsapp_share", "")).strip()
    if whatsapp:
        lines.append(f"WhatsApp: {whatsapp[:180]}")
    return "\n".join(lines)


def normalize_hashtags(tags: object) -> list[str]:
    """The three brand hashtags always, plus at most two about the piece."""
    extra: list[str] = []
    for tag in normalize_string_list(tags, max_items=10):
        clean = "#" + re.sub(r"\s+", "", tag.lstrip("#")).lower()
        if clean != "#" and clean not in FIXED_HASHTAGS and clean not in extra:
            extra.append(clean)
    return FIXED_HASHTAGS + extra[:MAX_EXTRA_HASHTAGS]


def publish_pack_fallback() -> dict:
    return {
        "product_name": "",
        "seo_title": "",
        "seo_description": "",
        "whatsapp_share": "Guarda questo pezzo da I Monili Ravenna: se ti piace scrivici, te lo mettiamo da parte.",
        "gmb_title": "Nuovo arrivo in negozio",
        "gmb_text": "Pezzo disponibile in boutique in via Cavour, nel centro di Ravenna: passa a provarlo.",
        "caption": "Nuovo arrivo da I Monili Ravenna: scrivici, te lo mettiamo da parte.",
        "hashtags": [],
        "cta": "Scrivici su WhatsApp o passa in via Cavour, te lo mettiamo da parte.",
    }


def with_legacy_keys(pack: dict) -> dict:
    """Old key names still read by api/server.py, the vetrina and old missions."""
    pack["selected_format"] = "scheda_pezzo"
    pack["selected_caption"] = pack.get("caption", "")
    pack["selected_hashtags"] = pack.get("hashtags", [])
    pack["selected_whatsapp"] = pack.get("whatsapp_share", "")
    pack["selected_gmb_title"] = pack.get("gmb_title", "")
    pack["selected_gmb_text"] = pack.get("gmb_text", "")
    pack["selected_cta"] = pack.get("cta", "")
    return pack


def normalize_publish_pack(parsed: dict) -> dict:
    pack = publish_pack_fallback()
    for key in pack:
        if key == "hashtags":
            continue
        value = str(parsed.get(key, "")).strip()
        if value:
            pack[key] = value
    pack["hashtags"] = normalize_hashtags(parsed.get("hashtags"))
    return with_legacy_keys(pack)


def agent_publish_pack(text_model: str, api_key: str, analisi: str, plan: dict, brief: str) -> dict:
    log("PUBLISH PACK", "Testi per sito, WhatsApp e Google Business...")
    prompt = f"""Scrivi i testi della scheda di un pezzo per il sito vetrina. Restituisci SOLO un JSON valido.
{BRAND}
Analisi: {analisi[:1400]}
Styling: {plan.get("styling", "")}
Brief utente: {brief if brief else "Nessun brief"}

A cosa servono: far trovare il pezzo su Google e dalle AI, dare un link da girare su WhatsApp,
portare la gente nei due negozi di via Cavour a Ravenna. La vendita avviene su WhatsApp e DM.

JSON esatto:
{{
  "product_name": "nome breve e concreto del pezzo, es. Anello in argento con ametista",
  "seo_title": "max 60 caratteri, nome del pezzo + I Monili Ravenna",
  "seo_description": "max 155 caratteri, cosa e, materiali certi, dove si trova a Ravenna",
  "whatsapp_share": "messaggio breve da mandare insieme al link del pezzo, chiude con 'te lo mettiamo da parte'",
  "gmb_title": "titolo post Google Business",
  "gmb_text": "testo post Google Business, max 80 parole, con via Cavour e Ravenna",
  "caption": "una caption breve per la storia che rimanda al pezzo, max 2 emoji",
  "hashtags": ["max 2 hashtag specifici del pezzo, i 3 fissi li aggiungo io"],
  "cta": "invito breve: scrivici in DM o passa in negozio"
}}

Regole:
- italiano naturale, tono da amica che consiglia
- materiali solo se certi nell'analisi: niente "argento" se e metallo argentato
- stagione {SEASON}
- niente markdown, niente testo fuori dal JSON, niente placeholder."""
    raw = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=1400)
    parsed = extract_json_object(raw)
    if not parsed:
        log("PUBLISH PACK", "JSON non valido, uso testi standard", "warn")
    return normalize_publish_pack(parsed)


def format_publish_pack_markdown(pack: dict) -> str:
    return (
        "# Scheda pezzo\n\n"
        f"## Nome\n{pack.get('product_name') or '-'}\n\n"
        f"## Google (titolo e descrizione)\n{pack.get('seo_title') or '-'}\n\n{pack.get('seo_description') or '-'}\n\n"
        f"## WhatsApp\n{pack.get('whatsapp_share') or '-'}\n\n"
        f"## Google Business Post\nTitolo: {pack.get('gmb_title') or '-'}\n\nTesto: {pack.get('gmb_text') or '-'}\n\n"
        f"## Caption storia\n{pack.get('caption') or '-'}\n\n{' '.join(pack.get('hashtags') or [])}\n\n"
        f"## Invito\n{pack.get('cta') or '-'}\n"
    )


def run_agency(foto_path: str, brief: str = "", image_model: str = "", text_model: str = "") -> None:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("OPENROUTER_API_KEY non trovata. Impostala nelle variabili d'ambiente.", flush=True)
        sys.exit(1)

    foto = Path(foto_path)
    if not foto.exists():
        print(f"Foto non trovata: {foto_path}", flush=True)
        sys.exit(1)

    selected_image_model = select_openrouter_image_model(image_model)
    selected_text_model = select_openrouter_text_model(text_model)

    nome = foto.stem.lower().replace(" ", "-")
    run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    output_dir = OUTPUT_ROOT / f"{run_id}_{nome}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nMONILI MEDIA AGENCY - scheda pezzo", flush=True)
    print(f"Foto: {foto_path}", flush=True)
    print(f"Brief: {brief or 'auto-analisi'}", flush=True)
    print(f"Modello testo: {selected_text_model}", flush=True)
    print(f"Modello immagini: {selected_image_model}", flush=True)
    print(f"Output: {output_dir}\n", flush=True)

    log("SUPERVISOR", "Missione ricevuta: scheda pezzo per sito, WhatsApp e Google.")

    analisi = ""
    plan = scheda_plan_defaults()
    ai_site_images: list[str] = []
    woman = ""
    publish_pack: dict = {}
    publish_pack_md = ""

    def safe_write(path: Path, content: str):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            log("SISTEMA", f"Scrittura file fallita ({path.name}): {e}", "warn")

    try:
        analisi = agent_analisi(selected_text_model, api_key, foto, brief)
        safe_write(output_dir / "01_ANALISI" / "product_card.md", f"# Scheda Prodotto\n\n{analisi}")
    except Exception as e:
        log("ANALISTA", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        plan = agent_scheda_plan(selected_text_model, api_key, foto, analisi, brief)
        safe_write(output_dir / "02_PIANO" / "scheda_plan.json", json.dumps(plan, indent=2, ensure_ascii=False))
    except Exception as e:
        log("PIANO SCHEDA", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        import casting

        woman = plan.get("woman") or casting.FALLBACK_WOMAN
        log("SITO VISUAL", f"La donna di questo pezzo: {woman}", "data")
        ai_site_images = generate_showcase_images(output_dir, api_key, selected_image_model, foto, plan["site_prompts"], woman)
    except Exception as e:
        log("SITO VISUAL", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")
    site_images = list(ai_site_images)
    real_photo_check: dict = {}
    try:
        real_photo, real_photo_check = create_real_photo_image(output_dir, foto)
        site_images.append(real_photo)
    except Exception as e:
        log("SITO VISUAL", f"Foto reale non preparata: {e}", "warn")

    try:
        publish_pack = agent_publish_pack(selected_text_model, api_key, analisi, plan, brief)
        publish_pack_md = format_publish_pack_markdown(publish_pack)
        safe_write(output_dir / "03_TESTI" / "publish_pack.json", json.dumps(publish_pack, indent=2, ensure_ascii=False))
        safe_write(output_dir / "03_TESTI" / "publish_pack.md", publish_pack_md)
        log("PUBLISH PACK", "Testi pronti", "success")
    except Exception as e:
        log("PUBLISH PACK", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    log("MEMORIA", "Aggiornamento performance_log.json...")
    try:
        memory_path = MEMORY_ROOT / "performance_log.json"
        log_data = json.loads(memory_path.read_text(encoding="utf-8")) if memory_path.exists() else {"sessions": []}
        sessions = log_data.get("sessions")
        if not isinstance(sessions, list):
            sessions = []
            log_data["sessions"] = sessions
        sessions.append(
            {
                "timestamp": datetime.now().isoformat(),
                "foto": str(foto),
                "brief": brief,
                "output_dir": str(output_dir),
                "text_model": selected_text_model,
                "image_model": selected_image_model,
                "kind": "scheda_pezzo",
                "showcase_images": site_images,
            }
        )
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text(json.dumps(log_data, indent=2, ensure_ascii=False), encoding="utf-8")
        log("MEMORIA", "Sessione loggata. Memoria persistente aggiornata.", "success")
    except Exception as e:
        log("MEMORIA", f"Log non salvato: {e}", "warn")

    print("\nMISSIONE COMPLETATA!", flush=True)
    print(f"Output: {output_dir}", flush=True)

    plan_json = json.dumps(plan, indent=2, ensure_ascii=False)
    results = {
        "run_id": run_id,
        "output_dir": output_dir.name,
        "kind": "scheda_pezzo",
        "publish_pack": publish_pack_md,
        "publish_pack_json": json.dumps(publish_pack, ensure_ascii=False),
        "scheda_plan": plan_json,
        "strategy_plan": plan_json,
        "analisi": f"# Scheda Prodotto\n\n{analisi}",
    }
    for idx, image_path in enumerate(site_images, start=1):
        results[f"image_site_{idx}"] = image_path
    if woman:
        # La donna di questo pezzo: i Reel fatti partendo da questa scheda usano lei.
        results["woman"] = woman
    if real_photo_check:
        results["real_photo_check"] = json.dumps(real_photo_check, ensure_ascii=False)

    results["decision_summary"] = build_decision_summary(publish_pack, ai_site_images, real_photo_check)
    results["asset_report_json"] = json.dumps(
        [image_file_report(value) for key, value in results.items() if key.startswith("image_")],
        ensure_ascii=False,
    )

    # Persist full recoverable manifest for frontend history.
    manifest = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(),
        "source_photo": str(foto),
        "brief": brief,
        "output_dir": str(output_dir),
        "text_model": selected_text_model,
        "image_model": selected_image_model,
        "status": "done",
        "results": results,
    }
    safe_write(output_dir / "run_manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"__RESULTS_JSON__:{json.dumps(results, ensure_ascii=False)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Monili Media Agency - Scheda pezzo da foto prodotto")
    parser.add_argument("--foto", "-f", default="input/prodotto.jpg")
    parser.add_argument("--brief", "-b", default="")
    parser.add_argument("--image-model", default="")
    parser.add_argument("--text-model", default="")
    args = parser.parse_args()
    try:
        run_agency(args.foto, args.brief, args.image_model, args.text_model)
    except Exception as e:
        print(f"\nCRASH FATALE: {e}", flush=True)
        print(traceback.format_exc(), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
