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
    "black-forest-labs/flux.2-klein-4b",
    "bytedance-seed/seedream-4.5",
]
DEFAULT_OPENROUTER_IMAGE_MODEL = SUPPORTED_OPENROUTER_IMAGE_MODELS[0]

SUPPORTED_OPENROUTER_TEXT_MODELS = [
    "openai/gpt-5.5",
    "openai/gpt-4.1-mini",
    "google/gemini-2.5-flash",
    "google/gemini-2.5-pro",
    "anthropic/claude-3.7-sonnet",
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


def extract_prompt_candidates(shooting_prompts: str, max_items: int = 2) -> list[str]:
    prompts: list[str] = []
    for line in shooting_prompts.splitlines():
        match = re.search(r"Prompt EN:\s*(.+)$", line, flags=re.IGNORECASE)
        if match:
            prompt = match.group(1).strip()
            if prompt:
                prompts.append(prompt)

    if not prompts:
        compact = " ".join(shooting_prompts.split()).strip()
        if compact:
            prompts.append(compact[:500])

    return prompts[:max_items]


def extract_labeled_prompt(raw_text: str, label: str) -> str:
    pattern = rf"{re.escape(label)}\s*:\s*(.+)"
    match = re.search(pattern, raw_text, flags=re.IGNORECASE)
    return match.group(1).strip() if match else ""


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


def to_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "si", "sì", "on"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def strategy_plan_defaults() -> dict:
    return {
        "product_type": "other",
        "product_category": "other",
        "campaign_angle": "new_arrival",
        "content_kit": "quick_static",
        "primary_output": "single_post",
        "secondary_output": "story_pack",
        "needs_carousel": False,
        "needs_story_pack": True,
        "needs_worn_visual": True,
        "needs_street_visual": True,
        "visual_count": 1,
        "visual_focus": ["hero_clean", "worn", "street_context"],
        "story_frames": [
            {"frame": 1, "purpose": "hook", "text_mode": "embedded_text", "text_lines": ["Nuovo arrivo", "I Monili Ravenna"]},
            {"frame": 2, "purpose": "detail", "text_mode": "clean", "text_lines": []},
            {"frame": 3, "purpose": "cta", "text_mode": "embedded_text", "text_lines": ["Scrivici su WhatsApp"]},
        ],
        "styling_items": [],
        "model_direction": "realistic adult model, natural pose",
        "scene_concepts": ["premium product hero", "worn lifestyle", "Italian street context"],
        "rationale": "Piano fallback: post statico con visual realistici.",
    }


def brief_requests_carousel(brief: str) -> bool:
    source = brief.lower()
    return any(token in source for token in ("carousel", "carosello", "slide"))


def strategy_plan_summary(plan: dict) -> str:
    primary = str(plan.get("primary_output", "single_post"))
    secondary = str(plan.get("secondary_output", "story_recall"))
    needs_carousel = to_bool(plan.get("needs_carousel"))
    needs_worn = to_bool(plan.get("needs_worn_visual"))
    needs_street = to_bool(plan.get("needs_street_visual"))
    visual_count = int(plan.get("visual_count", 3))
    visual_focus = normalize_string_list(plan.get("visual_focus"), max_items=8)
    scenes = normalize_string_list(plan.get("scene_concepts"), max_items=5)
    category = str(plan.get("product_category", plan.get("product_type", "other")))
    angle = str(plan.get("campaign_angle", "new_arrival"))
    return (
        f"product_category={category}; campaign_angle={angle}; "
        f"primary_output={primary}; secondary_output={secondary}; "
        f"needs_carousel={needs_carousel}; needs_worn_visual={needs_worn}; "
        f"needs_street_visual={needs_street}; visual_count={visual_count}; "
        f"visual_focus={','.join(visual_focus) if visual_focus else '-'}; "
        f"scene_concepts={'; '.join(scenes) if scenes else '-'}"
    )


def format_publish_pack_markdown(pack: dict) -> str:
    caption = str(pack.get("selected_caption", "")).strip()
    hashtags = normalize_string_list(pack.get("selected_hashtags"), max_items=30)
    whatsapp = str(pack.get("selected_whatsapp", "")).strip()
    gmb_title = str(pack.get("selected_gmb_title", "")).strip()
    gmb_text = str(pack.get("selected_gmb_text", "")).strip()
    selected_format = str(pack.get("selected_format", "")).strip()
    post_time = str(pack.get("selected_posting_time", "")).strip()
    cta = str(pack.get("selected_cta", "")).strip()

    hashtags_line = " ".join(tag for tag in hashtags if tag.startswith("#"))
    if not hashtags_line and hashtags:
        hashtags_line = " ".join(hashtags)

    return (
        "# Pronto Da Pubblicare\n\n"
        f"## Formato Scelto Dallo Strategist\n{selected_format or '-'}\n\n"
        f"## Caption Selezionata\n{caption or '-'}\n\n"
        f"## Hashtag Selezionati\n{hashtags_line or '-'}\n\n"
        f"## WhatsApp Broadcast\n{whatsapp or '-'}\n\n"
        f"## Google Business Post\nTitolo: {gmb_title or '-'}\n\nTesto: {gmb_text or '-'}\n\n"
        f"## CTA Locale\n{cta or '-'}\n\n"
        f"## Orario Consigliato\n{post_time or '-'}\n"
    )


BRAND = """
BRAND: I Monili Ravenna - negozio bijoux, accessori donna, abbigliamento
Location: Ravenna, centro storico (Emilia-Romagna)
Target: donna 25-45, urbana, fashion-forward, Ravenna e dintorni
Tono: caldo, complice, femminile - come un'amica che consiglia, non un brand che vende
Stagione: Primavera/Estate 2026
Hashtag fissi: #imoniliravenna #ravenna #romagnastyle
Palette: neutri caldi, bianco ottico, terracotta, oro
Posting top: Martedi/Giovedi/Sabato ore 18:30-20:00
"""


def agent_trend(text_model: str, api_key: str) -> str:
    log("TREND INTEL", "Ricerca trend hashtag bijoux Italia P/E 2026...")
    prompt = f"""Sei un esperto di social media marketing moda/bijoux in Italia.
{BRAND}

Genera un report completo sui trend P/E 2026:
1. Top 15 hashtag trending bijoux/gioielli/moda su Instagram Italia (con stima reach)
2. Top keyword e hook per post statici/carousel moda in Italia
3. Formato contenuto con piu engagement ora: carousel vs post statico vs stories vs Google Business Profile
4. Trend estetici P/E 2026: colori, stili, mood dominanti
5. Orari migliori Instagram per target donna 25-45 Emilia-Romagna
6. 3 competitor locali da monitorare (generici, non nominare brand reali)
7. Content ideas salvabili/condivisibili per bijoux
8. Spunti local SEO e Google Business Profile per negozi fisici

Formato markdown strutturato, tutto in italiano."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=1500)
    log("TREND INTEL", "Intelligence P/E 2026 completata", "success")
    return result


def agent_analisi(text_model: str, api_key: str, foto: Path, brief: str) -> str:
    log("ANALISTA", "Analisi multimodale foto prodotto...")
    log("ANALISTA", "Caricamento immagine in Vision AI...", "data")
    prompt = f"""Sei un esperto analista di prodotti fashion e bijoux.
{BRAND}
Brief aggiuntivo: {brief if brief else "Nessun brief - analizza autonomamente dalla foto"}

Analizza questa foto prodotto e crea una scheda completa:

## IDENTIFICAZIONE
- Categoria esatta
- Materiali identificati con certezza
- Colori principali con codici HEX stimati
- Dimensioni stimate
- Tecnica di realizzazione (se visibile)

## MOOD & POSIZIONAMENTO
- Stile/mood (minimal, boho, elegante, casual, statement...)
- Occasione d'uso consigliata
- Stagione P/E 2026: si/no e perche
- Fascia di prezzo stimata (se non nel brief)

## STRATEGIA CONTENUTO
- Formato consigliato: post statico / carousel prodotto / carousel informativo / stories / Google Business Profile (con motivazione)
- Punti di forza visivi da valorizzare
- Abbinamenti outfit suggeriti (3 look)

## DESCRIZIONE AI
Descrizione del prodotto in italiano utile per local SEO, scheda sito e alt text, max 100 parole.

Rispondi in italiano, formato markdown."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1800)
    log("ANALISTA", "Prodotto classificato - dati pronti per il team", "success")
    return result


def agent_strategy(text_model: str, api_key: str, foto: Path, analisi: str, brief: str, trend: str) -> str:
    log("STRATEGIST", "Scelta autonoma obiettivo, canali e formato migliore...")
    prompt = f"""Sei il marketing strategist di un piccolo negozio locale.
Devi decidere cosa conviene generare, evitando output ripetitivi.
{BRAND}

Analisi prodotto: {analisi[:1200]}
Brief: {brief if brief else "Nessun brief"}
Trend/local insight: {trend[:700]}

Decidi una strategia operativa per questo singolo prodotto.
Non proporre video AI generati. Se serve un Reel, suggerisci solo un video reale da girare col telefono.

Rispondi in italiano in markdown con queste sezioni:
## DECISIONE
- Obiettivo primario: visite in negozio / messaggi WhatsApp / awareness locale / vendita rapida / autorevolezza
- Formato principale consigliato: post statico / carousel prodotto / carousel informativo / story / WhatsApp / Google Business Profile
- Canali da usare oggi
- Canali da evitare oggi

## POTENZIALE DEL PRODOTTO
- Perche questo prodotto puo interessare
- Occasione d'uso o bisogno cliente
- Angolo creativo non banale

## PIANO CONTENUTO
- Output da generare ora
- Hook principale
- CTA locale
- Keyword locali target

## VARIETA
- Cosa evitare per non sembrare uguale agli altri post
- Variante alternativa se questo formato e gia stato usato spesso"""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1700)
    log("STRATEGIST", "Strategia 2.0 definita: formato e canali scelti", "success")
    return result


def agent_merchandising(text_model: str, api_key: str, foto: Path, analisi: str, brief: str) -> str:
    log("MERCHANDISER", "Valorizzazione prodotto, styling e scenari vendibili...")
    prompt = f"""Sei un merchandiser e stylist per un piccolo negozio moda/bijoux.
Il tuo compito e trasformare un oggetto fotografato male o in modo semplice in un contenuto desiderabile e vendibile.
{BRAND}
Analisi prodotto: {analisi[:1200]}
Brief: {brief if brief else "Nessun brief"}

Decidi tutto cio che serve per vendere meglio questo oggetto:

## POTENZIALE DI VENDITA
- Perche puo piacere
- Che desiderio risolve
- Cliente ideale

## STYLING
- 3 abbinamenti concreti con altri capi/accessori
- Colori e materiali da accostare
- Cosa evitare per non svalutare il prodotto

## VISUAL GENERATIVI CONSIGLIATI
- 4 scene fotorealistiche da creare con AI
- quando usare modella AI, mano, orecchio, collo, manichino o flat lay
- ambientazioni credibili anche inventate: boutique, strada italiana, caffe, portico, camera luminosa, vetrina

Regola centrale: l'ambiente, la modella e lo styling possono essere inventati e migliorati; il prodotto deve restare fedele a forma, colore, materiali, proporzioni e dettagli.
Rispondi in italiano, pratico, senza teoria."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1800)
    log("MERCHANDISER", "Styling e scenari vendibili pronti", "success")
    return result


def agent_strategy_plan(
    text_model: str,
    api_key: str,
    foto: Path,
    analisi: str,
    strategy: str,
    merchandising: str,
    brief: str,
) -> dict:
    log("STRATEGIST", "Piano strutturato dinamico (JSON) in corso...")
    prompt = f"""Sei lo strategist operativo di un'agenzia social per retail locale.
{BRAND}
Analisi prodotto: {analisi[:1100]}
Strategia testuale: {strategy[:1100]}
Merchandising/styling: {merchandising[:1100]}
Brief: {brief if brief else "Nessun brief"}

Restituisci SOLO JSON valido con queste chiavi:
{{
  "product_type": "jewelry|clothing|bag|belt|shoes|gift|accessory|other",
  "product_category": "ring|earrings|necklace|bracelet|bag|dress|shirt|kimono|coat|trousers|belt|shoes|gift|home_object|other",
  "campaign_angle": "new_arrival|gift_idea|ceremony|unique_piece|seasonal_outfit|material_detail|price_push|local_boutique",
  "content_kit": "quick_static|complete_static|stories_only|post_and_stories",
  "primary_output": "single_post|carousel_product|carousel_educational|gmb_post|story_pack",
  "secondary_output": "single_post|carousel_product|carousel_educational|gmb_post|story_pack",
  "needs_carousel": true/false,
  "needs_story_pack": true,
  "needs_worn_visual": true/false,
  "needs_street_visual": true/false,
  "visual_count": 1-3,
  "visual_focus": ["hero_clean","worn","street_context","material_closeup","outfit_match","local_store_context","editorial_detail","gift_context"],
  "story_frames": [
    {{"frame": 1, "purpose": "hook|new_arrival|gift|detail|cta", "text_mode": "embedded_text|clean", "text_lines": ["max 2 short Italian lines"]}},
    {{"frame": 2, "purpose": "detail|worn|outfit|material", "text_mode": "embedded_text|clean", "text_lines": []}},
    {{"frame": 3, "purpose": "cta|whatsapp|store_visit", "text_mode": "embedded_text|clean", "text_lines": ["max 2 short Italian lines"]}}
  ],
  "styling_items": ["item1", "item2", "item3"],
  "model_direction": "descrizione breve della modella/posa se utile",
  "scene_concepts": ["scena fotorealistica 1", "scena fotorealistica 2", "scena fotorealistica 3"],
  "rationale": "max 2 frasi"
}}

Regole:
- Questo sistema produce solo contenuti statici: post, stories, carousel, Google Business e sito.
- Le stories statiche sono parte del kit standard: needs_story_pack deve essere true.
- Se serve testo dentro alcune immagini, pianificalo in story_frames con text_mode=embedded_text. Non usare overlay lato frontend.
- Sii specifico per categoria: una borsa richiede proporzioni/manici, un anello macro e mano, un abito vestibilita e silhouette, una cintura fibbia e outfit.
- Se prodotto e abbigliamento, normalmente needs_worn_visual=true.
- Genera carousel per prodotti con dettagli, styling o storia utile; altrimenti puo essere false.
- Evita output ripetitivo, scegli il formato in base al prodotto ma consegna comunque post + stories.
- Puoi usare modella AI, location inventate, styling e props se aiutano a vendere, ma il prodotto deve restare identico.
- Nessun testo fuori JSON."""
    raw = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1200)
    parsed = extract_json_object(raw)
    if not parsed:
        log("STRATEGIST", "Piano JSON non valido, uso fallback", "warn")
        return strategy_plan_defaults()

    base = strategy_plan_defaults()
    base["product_type"] = str(parsed.get("product_type", base["product_type"])).strip() or base["product_type"]
    base["product_category"] = str(parsed.get("product_category", base["product_category"])).strip() or base["product_category"]
    base["campaign_angle"] = str(parsed.get("campaign_angle", base["campaign_angle"])).strip() or base["campaign_angle"]
    base["content_kit"] = str(parsed.get("content_kit", base["content_kit"])).strip() or base["content_kit"]
    base["primary_output"] = str(parsed.get("primary_output", base["primary_output"])).strip() or base["primary_output"]
    base["secondary_output"] = str(parsed.get("secondary_output", base["secondary_output"])).strip() or base["secondary_output"]
    base["needs_carousel"] = to_bool(parsed.get("needs_carousel"))
    base["needs_story_pack"] = True
    base["needs_worn_visual"] = to_bool(parsed.get("needs_worn_visual"))
    base["needs_street_visual"] = to_bool(parsed.get("needs_street_visual"))
    try:
        base["visual_count"] = max(1, min(3, int(parsed.get("visual_count", base["visual_count"]))))
    except Exception:
        pass
    focus = normalize_string_list(parsed.get("visual_focus"), max_items=8)
    if focus:
        base["visual_focus"] = focus
    styling_items = normalize_string_list(parsed.get("styling_items"), max_items=6)
    if styling_items:
        base["styling_items"] = styling_items
    model_direction = str(parsed.get("model_direction", base["model_direction"])).strip()
    if model_direction:
        base["model_direction"] = model_direction
    scene_concepts = normalize_string_list(parsed.get("scene_concepts"), max_items=5)
    if scene_concepts:
        base["scene_concepts"] = scene_concepts
    story_frames = parsed.get("story_frames")
    if isinstance(story_frames, list):
        clean_frames = []
        for idx, frame in enumerate(story_frames[:3], start=1):
            if not isinstance(frame, dict):
                continue
            clean_frames.append(
                {
                    "frame": int(frame.get("frame", idx)) if str(frame.get("frame", idx)).isdigit() else idx,
                    "purpose": str(frame.get("purpose", "story")).strip() or "story",
                    "text_mode": "embedded_text" if str(frame.get("text_mode", "")).strip() == "embedded_text" else "clean",
                    "text_lines": normalize_string_list(frame.get("text_lines"), max_items=2),
                }
            )
        if clean_frames:
            base["story_frames"] = clean_frames
    base["rationale"] = str(parsed.get("rationale", base["rationale"])).strip() or base["rationale"]

    primary = base["primary_output"]
    if primary in {"carousel_product", "carousel_educational"}:
        base["needs_carousel"] = True
    return base


def agent_shooting(text_model: str, api_key: str, foto: Path, analisi: str) -> str:
    log("FOTO DIR.", "Direzione foto reale e tagli statici...")
    prompt = f"""Sei un direttore fotografico specializzato in bijoux e accessori moda.
{BRAND}
Analisi prodotto: {analisi[:700]}

Crea una guida di shooting reale, fattibile con smartphone in negozio.
Non proporre immagini AI finte.

Includi:
1. Foto principale per post statico
2. 5 scatti per carousel prodotto
3. 5 scatti per carousel informativo/educativo
4. Foto per Google Business Profile
5. Tagli consigliati: 1:1, 4:5, 9:16
6. Luce, sfondo, posa mano/modella/manichino se utile
7. Errori da evitare per non sembrare catalogo freddo

Stile: luminoso, naturale, autentico, locale."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=2000)
    log("FOTO DIR.", "Guida foto reale e asset statici pronta", "success")
    return result


def agent_visual_prompts(
    text_model: str,
    api_key: str,
    foto: Path,
    analisi: str,
    strategy: str,
    merchandising: str,
    shooting: str,
    plan: dict,
) -> str:
    log("VISUAL AI", "Brief fotorealistici per indossato, sfondo e contesto...")
    plan_summary = strategy_plan_summary(plan)
    visual_count = max(2, min(5, int(plan.get("visual_count", 3))))
    focus_list = normalize_string_list(plan.get("visual_focus"), max_items=8)
    focus_hint = ", ".join(focus_list) if focus_list else "hero_clean, worn, street_context"
    styling_items = normalize_string_list(plan.get("styling_items"), max_items=6)
    scene_concepts = normalize_string_list(plan.get("scene_concepts"), max_items=5)
    model_direction = str(plan.get("model_direction", "")).strip()
    prompt_knowledge = load_prompt_knowledge()
    prompt = f"""Sei un art director specializzato in visual AI fotorealistici per piccoli negozi locali.
{BRAND}
Knowledge prompt immagine:
{prompt_knowledge}

Analisi prodotto: {analisi[:900]}
Strategia: {strategy[:900]}
Merchandising/styling: {merchandising[:1200]}
Guida foto reale: {shooting[:700]}
Piano strategist: {plan_summary}
Styling items da usare se coerenti: {", ".join(styling_items) if styling_items else "scegli tu accessori/capi coerenti"}
Direzione modella/posa: {model_direction or "scegli tu in modo realistico"}
Scene consigliate: {"; ".join(scene_concepts) if scene_concepts else "premium hero, indossato, contesto italiano"}

Genera {visual_count} prompt in inglese per immagini statiche AI usando la foto caricata come riferimento.
Ogni prompt deve iniziare con "Prompt EN:".
Questi prompt sono VISUAL EXTRA esplorativi, diversi dal carousel e diversi dagli export Instagram finali.

Obiettivo: far vedere il prodotto in contesto reale senza farlo sembrare finto.
Usa AI generativa senza timidezza: puoi inventare modella, location, styling, props e atmosfera.
Puoi migliorare in modo deciso luce, composizione, sfondo, outfit e styling per ottenere uno scatto premium.
Il prodotto deve restare fedele all'originale al 100%.
Focus prioritari richiesti: {focus_hint}

Regole obbligatorie in ogni prompt:
- preserve the exact product shape, color, material, proportions, texture and distinctive details from the reference photo
- photorealistic, natural daylight, authentic small Italian boutique style
- improve lighting direction, depth, tonal contrast and framing for a premium editorial still photo
- clean and elevate background, avoid clutter, add realistic soft shadows and depth of field
- use complementary styling, invented realistic locations and AI models when they increase desire
- for clothing, show the garment worn naturally and styled as a complete outfit
- for jewelry, show realistic wear on hand/ear/neck plus one elegant product close-up
- do not include phones, fake chat screens, fake UI, fake packaging labels or readable text
- do not create carousel slides or multi-panel layouts here
- no plastic skin, no luxury stock-photo look, no unrealistic body, no fantasy jewelry
- do not change the product into a different item
- no text, no logos, no watermark
- if worn by a model, use a realistic adult model, natural pose, product visible but not exaggerated

Rispondi solo con i prompt richiesti, uno per blocco, senza spiegazioni."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1600)
    log("VISUAL AI", "Prompt visual controllati pronti", "success")
    return result


def agent_visual_gen(
    output_dir: Path,
    visual_prompts: str,
    selected_model: str,
    api_key: str,
    foto: Path,
    max_visuals_override: int | None = None,
) -> list[str]:
    visual_mode = os.environ.get("VISUAL_AI_MODE", "controlled").lower()
    if visual_mode in ("off", "false", "0", "none"):
        log("VISUAL GEN", "Visual AI disattivata da VISUAL_AI_MODE", "data")
        return []

    image_generator = os.environ.get("IMAGE_GENERATOR", "openrouter").lower()
    model = select_openrouter_image_model(selected_model)
    gen_dir = output_dir / "03_ASSET_STATICI" / "visual_ai"
    gen_dir.mkdir(parents=True, exist_ok=True)

    if image_generator != "openrouter":
        log("VISUAL GEN", "Modalita manuale - prompt pronti per uso esterno", "data")
        log("VISUAL GEN", "Prompt visual salvati per uso esterno", "success")
        return []

    if not api_key:
        log("VISUAL GEN", "OPENROUTER_API_KEY mancante - salto generazione immagini", "warn")
        return []

    max_visuals = max_visuals_override or int(os.environ.get("MAX_AI_VISUALS", "3"))
    max_visuals = max(1, min(5, max_visuals))
    prompts = extract_prompt_candidates(visual_prompts, max_items=max_visuals)
    if not prompts:
        log("VISUAL GEN", "Nessun prompt visual valido trovato", "warn")
        return []

    log("VISUAL GEN", f"Generazione visual AI controllata con {model}")
    generated_paths: list[str] = []
    for idx, prompt in enumerate(prompts, start=1):
        try:
            log("VISUAL GEN", f"Visual fotorealistico {idx}/{len(prompts)}", "data")
            controlled_prompt = f"""{prompt}

Use the uploaded reference image as the source of truth for the product.
Preserve the exact product shape, color, material, proportions and distinctive details.
You may invent the model, location, outfit, props and lighting to make the product more desirable.
Create a premium photorealistic static commercial photo, not a video frame."""
            data_urls = generate_image_with_openrouter(api_key, model, controlled_prompt, image_path=foto)
            for image_idx, data_url in enumerate(data_urls, start=1):
                filename = f"visual_ai_{idx}_{image_idx}.png"
                target = gen_dir / filename
                if save_data_url_image(data_url, target):
                    generated_paths.append(f"{output_dir.name}/03_ASSET_STATICI/visual_ai/{filename}")
        except Exception as e:
            log("VISUAL GEN", f"Visual AI non riuscito: {e}", "warn")

    if generated_paths:
        log("VISUAL GEN", f"{len(generated_paths)} visual AI creati in 03_ASSET_STATICI/visual_ai", "success")
        return generated_paths

    log("VISUAL GEN", "Nessuna immagine AI generata, ma prompt visual salvati", "warn")
    return []


def agent_instagram_visual_prompts(
    text_model: str,
    api_key: str,
    foto: Path,
    analisi: str,
    strategy: str,
    merchandising: str,
    plan: dict,
    brief: str,
) -> str:
    log("INSTAGRAM VISUAL", "Prompt dedicati post e stories statiche...")
    prompt_knowledge = load_prompt_knowledge()
    plan_summary = strategy_plan_summary(plan)
    story_frames = json.dumps(plan.get("story_frames", []), ensure_ascii=False)
    prompt = f"""Sei un senior art director per immagini Instagram fotorealistiche.
Devi creare prompt dedicati per contenuti statici, non riciclati da visual extra o carousel.
{BRAND}
Knowledge prompt immagine:
{prompt_knowledge}

Analisi prodotto: {analisi[:900]}
Strategia: {strategy[:900]}
Merchandising/styling: {merchandising[:1200]}
Piano strategist: {plan_summary}
Story frames pianificati: {story_frames}
Brief: {brief if brief else "Nessun brief"}

Restituisci solo queste quattro righe:
FEED_PROMPT_EN: ...
STORY_PROMPT_EN_1: ...
STORY_PROMPT_EN_2: ...
STORY_PROMPT_EN_3: ...

Regole:
- FEED_PROMPT_EN deve essere una singola immagine hero pubblicabile su Instagram feed, premium, desiderabile, senza testo.
- Ogni STORY_PROMPT_EN deve essere verticale 9:16, pronta da pubblicare come storia statica.
- Se lo story frame ha text_mode=embedded_text, chiedi a Images 2 di scrivere ESATTAMENTE quelle righe dentro l'immagine, in italiano, in spazio pulito e senza coprire il prodotto.
- Se lo story frame ha text_mode=clean, non inserire testo nell'immagine.
- Scrivi prompt diversi per categoria: gioiello macro/mano, borsa proporzioni/manici, abito vestibilita/silhouette, cintura fibbia/outfit, regalo still life.
- Puoi inventare modella, location, styling, props e luci se aiutano a vendere.
- Mantieni il prodotto identico alla foto reference: forma, colore, materiali, proporzioni, pietre, dettagli.
- Niente telefoni, chat screen, interfacce, loghi, watermark, packaging fake.
- Massimo fotorealismo, pelle naturale, mani realistiche, scala corretta."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1200)
    log("INSTAGRAM VISUAL", "Prompt feed/stories pronti", "success")
    return result


def generate_instagram_images(
    output_dir: Path,
    api_key: str,
    selected_model: str,
    foto: Path,
    instagram_prompts: str,
) -> dict[str, str]:
    if not api_key:
        log("INSTAGRAM VISUAL", "OPENROUTER_API_KEY mancante - salto immagini Instagram AI", "warn")
        return {}

    model = select_openrouter_image_model(selected_model)
    target_dir = output_dir / "05_FOTO_OTTIMIZZATE" / "ai_sources"
    target_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}

    prompt_specs = [
        ("feed_source", "FEED_PROMPT_EN", "4:5", "instagram_feed_source.png"),
        ("story_1_source", "STORY_PROMPT_EN_1", "9:16", "instagram_story_1_source.png"),
    ]
    if not model.startswith("openai/gpt-5.4-image") and not model.startswith("openai/gpt-image"):
        prompt_specs.extend(
            [
                ("story_2_source", "STORY_PROMPT_EN_2", "9:16", "instagram_story_2_source.png"),
                ("story_3_source", "STORY_PROMPT_EN_3", "9:16", "instagram_story_3_source.png"),
            ]
        )
    else:
        log("INSTAGRAM VISUAL", "Images 2 in modalita rapida: genero post + prima story, poi consegno il kit.", "data")
    for key, label, aspect_ratio, filename in prompt_specs:
        prompt = extract_labeled_prompt(instagram_prompts, label)
        if not prompt:
            log("INSTAGRAM VISUAL", f"Prompt mancante: {label}", "warn")
            continue
        try:
            log("INSTAGRAM VISUAL", f"Generazione {label}", "data")
            log("INSTAGRAM VISUAL", "Attendo OpenRouter: questa chiamata puo richiedere 1-3 minuti.", "data")
            controlled = f"""{prompt}

Use the uploaded reference photo as source-of-truth for the product.
Preserve exact product shape, color, material, proportions, stones and distinctive details.
Invent only model, setting, outfit, props and lighting.
No text, no logos, no watermark, no phone screens, no fake UI."""
            if label.startswith("STORY_PROMPT_EN"):
                controlled = f"""{prompt}

Use the uploaded reference photo as source-of-truth for the product.
Preserve exact product shape, color, material, proportions, stones and distinctive details.
Invent only model, setting, outfit, props and lighting.
If the prompt asks for embedded text, spell the text exactly and place it in clean negative space.
No logos, no watermark, no phone screens, no fake UI."""
            data_urls = generate_image_with_openrouter(
                api_key,
                model,
                controlled,
                image_path=foto,
                aspect_ratio=aspect_ratio,
            )
            if data_urls:
                target = target_dir / filename
                if save_data_url_image(data_urls[0], target):
                    outputs[key] = str(target)
                    if key == "story_1_source":
                        outputs["story_source"] = str(target)
        except Exception as e:
            log("INSTAGRAM VISUAL", f"{label} non generata: {e}", "warn")

    if outputs:
        log("INSTAGRAM VISUAL", f"{len(outputs)} immagini Instagram dedicate generate", "success")
    return outputs


def agent_showcase_visual_prompts(
    text_model: str,
    api_key: str,
    foto: Path,
    analisi: str,
    strategy: str,
    merchandising: str,
    brief: str,
) -> str:
    log("SITO VISUAL", "Prompt dedicati sito vetrina: prodotto, indossata, terza scelta...")
    prompt_knowledge = load_prompt_knowledge()
    prompt = f"""Sei un e-commerce art director per il sito vetrina I Monili Ravenna.
Devi creare 3 prompt in inglese per immagini prodotto dedicate al sito, non social.
{BRAND}
Knowledge prompt immagine:
{prompt_knowledge}

Analisi prodotto: {analisi[:1100]}
Strategia: {strategy[:700]}
Merchandising/styling: {merchandising[:1000]}
Brief utente: {brief if brief else "Nessun brief"}

Restituisci solo queste tre righe:
SITE_PROMPT_EN_1: ...
SITE_PROMPT_EN_2: ...
SITE_PROMPT_EN_3: ...

Obiettivo immagini:
1. SITE_PROMPT_EN_1 = clean product catalog photo, neutral warm ivory background, no model, product centered, premium boutique e-commerce, generous negative space.
2. SITE_PROMPT_EN_2 = product worn naturally by a realistic adult model or hand/ear/neck/body depending on product type, correct scale and fit.
3. SITE_PROMPT_EN_3 = decide based on the product: macro detail for jewelry, outfit/styling context for clothing, handle/texture detail for bag, buckle/outfit detail for belt, gift/lifestyle still life for accessories.

Regole obbligatorie:
- Use the uploaded reference photo as strict source of truth.
- Preserve exact product shape, color, material, proportions, stones, texture and distinctive details.
- Website-ready product photography, photorealistic, clean, sharp, premium but natural.
- Aspect ratio must work perfectly in 4:5 product cards, no important detail near edges.
- No readable text, no logo, no watermark, no fake label, no phone, no UI.
- No collage, no carousel layout, no multiple panels.
- Keep file result visually simple and fast-loading friendly, not overly busy.
"""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1200)
    log("SITO VISUAL", "Prompt sito pronti", "success")
    return result


def generate_showcase_images(
    output_dir: Path,
    api_key: str,
    selected_model: str,
    foto: Path,
    showcase_prompts: str,
) -> list[str]:
    if not api_key:
        log("SITO VISUAL", "OPENROUTER_API_KEY mancante - salto immagini sito dedicate", "warn")
        return []

    model = select_openrouter_image_model(selected_model)
    source_dir = output_dir / "07_SHOWCASE" / "sources"
    final_dir = output_dir / "07_SHOWCASE"
    source_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    specs = [
        ("SITE_PROMPT_EN_1", "site_product_clean_source.png", "site_01_product_clean.jpg"),
        ("SITE_PROMPT_EN_2", "site_worn_source.png", "site_02_worn.jpg"),
        ("SITE_PROMPT_EN_3", "site_context_source.png", "site_03_context.jpg"),
    ]
    generated: list[str] = []

    for index, (label, source_name, final_name) in enumerate(specs, start=1):
        prompt = extract_labeled_prompt(showcase_prompts, label)
        if not prompt:
            log("SITO VISUAL", f"Prompt mancante: {label}", "warn")
            continue
        try:
            log("SITO VISUAL", f"Generazione foto sito {index}/3", "data")
            controlled = f"""{prompt}

Use the uploaded reference photo as source-of-truth for the product.
Preserve exact product shape, color, material, proportions, stones and distinctive details.
Create a single website-ready product photograph, composed safely for 4:5 product cards.
No text, no logos, no watermark, no phone screens, no fake UI."""
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
            log("SITO VISUAL", f"{label} non generata: {e}", "warn")

    if generated:
        log("SITO VISUAL", f"{len(generated)} foto sito dedicate create in 07_SHOWCASE", "success")
    else:
        log("SITO VISUAL", "Nessuna foto sito dedicata generata", "warn")
    return generated


def create_showcase_fallback_images(output_dir: Path, source_path: Path, reason: str) -> list[str]:
    """
    Fallback anti-blocco: se Images 2 non consegna le foto sito dedicate,
    prepariamo comunque immagini sito leggere e proporzionate dalla foto originale.
    """
    log("SITO VISUAL", f"Fallback sito da foto originale: {reason}", "warn")
    final_dir = output_dir / "07_SHOWCASE"
    final_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("site_01_product_clean.jpg", "contain"),
        ("site_02_worn_fallback.jpg", "fit"),
        ("site_03_detail_fallback.jpg", "fit"),
    ]
    generated: list[str] = []
    for filename, mode in specs:
        final_path = final_dir / filename
        export_ratio_jpeg(source_path, final_path, (1200, 1500), mode=mode, target_kb=420)
        generated.append(f"{output_dir.name}/07_SHOWCASE/{filename}")
    return generated


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


def build_decision_summary(
    publish_pack: dict,
    showcase_images: list[str],
    carousel_images: list[str],
    story_image_count: int,
) -> str:
    selected_format = str(publish_pack.get("selected_format", "single_post")).strip() or "single_post"
    caption = str(publish_pack.get("selected_caption", "")).strip()
    whatsapp = str(publish_pack.get("selected_whatsapp", "")).strip()
    lines = [
        "COSA USARE ORA",
        f"Formato consigliato: {selected_format}",
        "Foto principale: usa il post Instagram 4:5.",
        f"Stories: {'pronte' if story_image_count else 'fallback 9:16 pronto dalla foto principale'}.",
        f"Sito vetrina: {'usa le foto dedicate 4:5' if showcase_images else 'usa il fallback sito 4:5'}.",
        f"Carousel: {'pronto' if carousel_images else 'non necessario/non generato in questa strategia'}.",
    ]
    if caption:
        lines.append(f"Caption scelta: {caption[:180]}")
    if whatsapp:
        lines.append(f"WhatsApp: {whatsapp[:180]}")
    return "\n".join(lines)


def agent_carousel_visual_prompts(
    text_model: str,
    api_key: str,
    analisi: str,
    strategy: str,
    merchandising: str,
    carousel: str,
    brief: str,
) -> str:
    log("CAROUSEL VISUAL", "Prompt per 5 slide carousel fotorealistico...")
    prompt_knowledge = load_prompt_knowledge()
    prompt = f"""Sei un visual strategist per Instagram carousel statici fotorealistici.
{BRAND}
Knowledge prompt immagine:
{prompt_knowledge}

Analisi prodotto: {analisi[:900]}
Strategia: {strategy[:900]}
Merchandising/styling: {merchandising[:1000]}
Struttura carousel: {carousel[:1200]}
Brief utente: {brief if brief else "Nessun brief"}

Genera ESATTAMENTE 5 prompt in inglese per 5 slide di un carousel pronto pubblicazione.
Ogni riga deve iniziare cosi:
SLIDE_PROMPT_EN_1:
SLIDE_PROMPT_EN_2:
SLIDE_PROMPT_EN_3:
SLIDE_PROMPT_EN_4:
SLIDE_PROMPT_EN_5:

Regole obbligatorie:
- Use the uploaded product photo as strict reference
- preserve exact product details, colors, shape and materials
- photorealistic, natural daylight, authentic Italian boutique mood
- For slide 1 only, if useful, include 1-2 very short Italian words directly inside the image, spelled exactly, placed in clean negative space.
- Slides 2-5 should normally be clean product/lifestyle photos without text.
- invent believable Ravenna/Italian boutique lifestyle scenes when useful, without recognizable fake landmarks
- use realistic model, hand, ear, neck, outfit, props and complementary products when they help sell the item
- make every slide look like a finished publishable photo, not a planning mockup
- no phones, no chat screens, no fake UI, no readable text, no fake labels
- no external overlay instructions, no logos, no watermark
- if model is present, realistic adult model only
- each slide must have different framing and purpose (hero, worn detail, context, mix&match, CTA-ready visual)

Rispondi solo con le 5 righe richieste, senza altro testo."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=1600)
    log("CAROUSEL VISUAL", "Prompt slide pronti", "success")
    return result


def extract_carousel_slide_prompts(raw_text: str, max_slides: int = 5) -> list[str]:
    prompts: list[str] = []
    for i in range(1, max_slides + 1):
        pattern = rf"SLIDE_PROMPT_EN_{i}:\s*(.+)"
        match = re.search(pattern, raw_text, flags=re.IGNORECASE)
        if match:
            prompt = match.group(1).strip()
            if prompt:
                prompts.append(prompt)
    return prompts


def desired_carousel_slide_count(plan: dict) -> int:
    product_category = str(plan.get("product_category", "")).lower()
    if product_category in {"ring", "earrings", "necklace", "bracelet", "belt"}:
        return 2
    return 3


def generate_carousel_images(
    output_dir: Path,
    api_key: str,
    selected_model: str,
    foto: Path,
    slide_prompts: list[str],
) -> list[str]:
    if not api_key:
        log("CAROUSEL VISUAL", "OPENROUTER_API_KEY mancante - salto immagini carousel", "warn")
        return []

    if not slide_prompts:
        log("CAROUSEL VISUAL", "Nessun prompt slide valido trovato", "warn")
        return []

    model = select_openrouter_image_model(selected_model)
    target_dir = output_dir / "04_CAROUSEL" / "images"
    target_dir.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    for idx, prompt in enumerate(slide_prompts, start=1):
        try:
            log("CAROUSEL VISUAL", f"Generazione slide {idx}/{len(slide_prompts)}", "data")
            log("CAROUSEL VISUAL", "Attendo OpenRouter per la slide: puo richiedere qualche minuto.", "data")
            controlled = f"""{prompt}

Use the uploaded reference photo as source-of-truth for the product.
The product must remain faithful to the reference.
You may invent model, location, outfit, props and lighting to make the slide more desirable.
If the prompt asks for embedded text, the text must be generated directly inside the image and spelled exactly.
The result must look like a finished premium photorealistic still photo for Instagram carousel."""
            data_urls = generate_image_with_openrouter(
                api_key,
                model,
                controlled,
                image_path=foto,
                aspect_ratio="4:5",
            )
            if not data_urls:
                continue
            source_path = target_dir / f"carousel_slide_{idx}_source.png"
            final_name = f"carousel_slide_{idx}_1080x1350.jpg"
            final_path = target_dir / final_name
            if save_data_url_image(data_urls[0], source_path):
                export_ratio_jpeg(source_path, final_path, (1080, 1350), mode="fit", target_kb=450)
                generated.append(f"{output_dir.name}/04_CAROUSEL/images/{final_name}")
        except Exception as e:
            log("CAROUSEL VISUAL", f"Slide {idx} non generata: {e}", "warn")

    if generated:
        log("CAROUSEL VISUAL", f"{len(generated)} slide carousel generate", "success")
    else:
        log("CAROUSEL VISUAL", "Nessuna slide carousel generata", "warn")
    return generated


def agent_carousel_slide_texts(
    text_model: str,
    api_key: str,
    analisi: str,
    strategy: str,
    carousel: str,
    publish_pack: dict,
) -> dict:
    log("CAROUSEL COPY", "Testi brevi per slide e caption unica...")
    prompt = f"""Sei una social media manager pratica.
{BRAND}
Analisi prodotto: {analisi[:700]}
Strategia: {strategy[:700]}
Carousel: {carousel[:1300]}
Caption scelta: {str(publish_pack.get("selected_caption", ""))[:700]}

Restituisci SOLO JSON valido:
{{
  "carousel_caption": "caption unica per tutto il carosello Instagram",
  "slide_texts": ["testo slide 1 max 65 caratteri", "testo slide 2 max 65 caratteri", "testo slide 3 max 65 caratteri", "testo slide 4 max 65 caratteri", "testo slide 5 max 65 caratteri"]
}}

Regole:
- Instagram ha una caption unica: carousel_caption e quella da pubblicare.
- slide_texts sono micro-testi opzionali da mettere sotto ogni immagine nella UI o come overlay manuale.
- non generare testi lunghi
- niente markdown, solo JSON."""
    raw = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=900)
    parsed = extract_json_object(raw)
    if not parsed:
        return {"carousel_caption": str(publish_pack.get("selected_caption", "")), "slide_texts": []}
    parsed["slide_texts"] = normalize_string_list(parsed.get("slide_texts"), max_items=5)
    parsed["carousel_caption"] = str(parsed.get("carousel_caption", publish_pack.get("selected_caption", ""))).strip()
    log("CAROUSEL COPY", "Testi slide pronti", "success")
    return parsed


def agent_reel(text_model: str, api_key: str, analisi: str, trend: str) -> str:
    log("REEL DIR.", "Struttura Reel: hook 3s + scene + CTA...")
    prompt = f"""Sei un video director specializzato in Reels Instagram per brand moda.
{BRAND}
Analisi prodotto: {analisi[:600]}
Trend attuali: {trend[:400]}

Crea uno script Reel Instagram professionale (15-30 secondi), frame by frame, con CTA finale.
Includi 5 prompt in inglese per generare i frame con AI.
Rispondi in italiano (tranne i prompt AI)."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=1800)
    log("REEL DIR.", "Script completo + prompt frame AI pronti", "success")
    return result


def agent_copy(text_model: str, api_key: str, foto: Path, analisi: str, brief: str) -> str:
    log("COPY", "Scrittura 3 varianti caption Instagram...")
    prompt = f"""Sei una copywriter esperta di social media per brand moda/bijoux in Italia.
{BRAND}
Analisi prodotto: {analisi[:600]}
Brief: {brief if brief else "Analizza dalla foto"}

Scrivi il copy completo:
- 3 caption Instagram (casual, elegante, urgency)
- messaggio WhatsApp broadcast
- post Google My Business
- 3 slide stories (ultima con CTA)

Hashtag fissi da includere: #imoniliravenna #ravenna #romagnastyle
Tono: caldo, mai troppo commerciale."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=2000)
    log("COPY", "3 varianti caption + WhatsApp + GMB + Stories pronti", "success")
    return result


def agent_carousel(text_model: str, api_key: str, analisi: str, strategy: str, trend: str) -> str:
    log("CAROUSEL", "Creazione carousel statico strategico...")
    prompt = f"""Sei un content strategist per piccoli negozi locali.
{BRAND}
Strategia scelta: {strategy[:1000]}
Analisi prodotto: {analisi[:900]}
Trend/local insight: {trend[:500]}

Crea 2 carousel statici alternativi, pronti da impaginare:

## CAROUSEL A - prodotto/abbinamento
- 5 slide
- Testo breve per ogni slide
- Visual suggerito per ogni slide usando foto reali
- CTA finale locale

## CAROUSEL B - informativo/educativo
Scegli il tema piu adatto tra: pietre/materiali, come abbinarlo, idea regalo, cerimonia, cura del bijoux.
- 5 slide
- Testo breve per ogni slide
- Visual suggerito per ogni slide usando foto reali
- CTA finale locale

Regole:
- Niente frasi generiche tipo "eleganza senza tempo" se non motivate.
- Tono caldo, pratico, locale.
- Ogni slide deve avere una funzione chiara."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=2200)
    log("CAROUSEL", "2 carousel statici pronti per impaginazione", "success")
    return result


def agent_local_visibility(text_model: str, api_key: str, analisi: str, strategy: str, brief: str) -> str:
    log("LOCAL SEO", "Ricerca locale e asset per Ravenna...")
    prompt = f"""Sei un consulente di local SEO e AI search optimization per negozi fisici.
{BRAND}
Strategia scelta: {strategy[:900]}
Analisi prodotto: {analisi[:900]}
Brief: {brief if brief else "Nessun brief"}

Crea un pacchetto di visibilita locale per questo prodotto:

## QUERY LOCALI TARGET
- 8 ricerche realistiche che una cliente farebbe a Ravenna
- dividile per intento: regalo, cerimonia, accessorio outfit, vicino a me

## GOOGLE BUSINESS PROFILE
- Titolo post
- Testo post breve
- CTA consigliata
- Foto da usare
- 3 varianti di descrizione prodotto locale

## PAGINA VETRINA / SHOPIFY / SITO
- Titolo SEO locale
- Meta description
- H1
- Descrizione prodotto 120 parole
- Alt text immagine
- 5 FAQ brevi

## AI SEARCH
- Frase sintetica che aiuta le AI a capire cosa vende il negozio
- Dati prodotto da strutturare: categoria, colore, materiale, occasione, prezzo se presente, disponibilita, localita

Scrivi in italiano, pratico e pronto da usare."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=2200)
    log("LOCAL SEO", "Pacchetto local visibility pronto", "success")
    return result


def agent_distribution(
    text_model: str,
    api_key: str,
    analisi: str,
    strategy: str,
    strategy_plan: dict,
    carousel: str,
) -> str:
    log("DISTRIBUZIONE", "Caption, WhatsApp e piano 7 giorni...")
    plan_summary = strategy_plan_summary(strategy_plan)
    carousel_source = carousel[:900] if carousel else "Nessun carousel: primary output non carousel."
    prompt = f"""Sei una social media manager per piccoli negozi.
{BRAND}
Strategia scelta: {strategy[:900]}
Piano strategist: {plan_summary}
Analisi prodotto: {analisi[:700]}
Carousel generato: {carousel_source}

Genera:
## INSTAGRAM
- 3 caption diverse: utile, locale, vendita gentile
- keyword naturali nella caption
- CTA non aggressive

## HASHTAG
- 18 hashtag: branded, local, nicchia, occasione
- 5 hashtag da evitare perche troppo generici o incoerenti

## WHATSAPP
- messaggio broadcast breve
- variante per clienti affezionate

## STORIES
- 3 frame testuali con sticker/interazione suggerita

## PIANO 7 GIORNI
- Quando pubblicare il contenuto principale (se carousel ok, altrimenti post statico)
- Quando fare story di richiamo
- Quando pubblicare Google Business
- Come riutilizzare il contenuto senza sembrare ripetitivo"""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=2200)
    log("DISTRIBUZIONE", "Caption, hashtag, WhatsApp e piano 7 giorni pronti", "success")
    return result


def agent_publish_pack(
    text_model: str,
    api_key: str,
    analisi: str,
    strategy: str,
    strategy_plan: dict,
    carousel: str,
    local_visibility: str,
    distribution: str,
    brief: str,
) -> dict:
    log("PUBLISH PACK", "Selezione finale pronta da copiare e pubblicare...")
    plan_summary = strategy_plan_summary(strategy_plan)
    prompt = f"""Sei un social media manager operativo. Devi restituire SOLO un JSON valido.
{BRAND}
Analisi: {analisi[:900]}
Strategia: {strategy[:900]}
Piano strategist: {plan_summary}
Carousel: {carousel[:900]}
Local visibility: {local_visibility[:900]}
Distribuzione: {distribution[:1200]}
Brief utente: {brief if brief else "Nessun brief"}

Obiettivo: ridurre confusione e consegnare output pronto da usare.
Seleziona TU la versione migliore, non lasciare indecisione.

Rispondi con un JSON esatto con queste chiavi:
{{
  "selected_format": "single_post|carousel_product|carousel_educational|gmb_post|story_pack",
  "selected_caption": "stringa unica pronta Instagram",
  "caption_alternatives": ["stringa opzionale 1", "stringa opzionale 2"],
  "selected_hashtags": ["#tag1", "#tag2", "... max 18"],
  "hashtags_alternative_set": ["#tagA", "#tagB", "... max 18"],
  "selected_whatsapp": "messaggio broadcast pronto",
  "selected_gmb_title": "titolo post Google Business",
  "selected_gmb_text": "testo post Google Business",
  "selected_story_frames": ["frame1", "frame2", "frame3"],
  "selected_cta": "CTA locale breve",
  "selected_posting_time": "giorno + ora locale Italia",
  "notes_for_owner": "max 2 frasi pratiche"
}}

Regole:
- italiano naturale
- niente markdown
- niente testo fuori JSON
- niente placeholder."""
    raw = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=1800)
    parsed = extract_json_object(raw)

    if not parsed:
        log("PUBLISH PACK", "JSON non valido, uso fallback minimale", "warn")
        return {
            "selected_format": str(strategy_plan.get("primary_output", "single_post")),
            "selected_caption": "Nuovo arrivo da I Monili Ravenna: passa in negozio per provarlo dal vivo.",
            "caption_alternatives": [],
            "selected_hashtags": ["#imoniliravenna", "#ravenna", "#romagnastyle"],
            "hashtags_alternative_set": [],
            "selected_whatsapp": "Nuovo arrivo disponibile da I Monili Ravenna. Se vuoi ti mando foto e taglie in chat.",
            "selected_gmb_title": "Nuovo arrivo in negozio - I Monili Ravenna",
            "selected_gmb_text": "Prodotto disponibile in boutique, vieni a provarlo in centro a Ravenna.",
            "selected_story_frames": ["Nuovo arrivo", "Dettaglio prodotto", "Scrivici su WhatsApp"],
            "selected_cta": "Scrivici su WhatsApp o passa in negozio in centro a Ravenna.",
            "selected_posting_time": "Martedi ore 19:00",
            "notes_for_owner": "Pubblica oggi il contenuto principale. Domani richiamo con 2 stories.",
        }

    parsed["selected_format"] = str(parsed.get("selected_format", strategy_plan.get("primary_output", "single_post"))).strip() or str(
        strategy_plan.get("primary_output", "single_post")
    )
    parsed["caption_alternatives"] = normalize_string_list(parsed.get("caption_alternatives"), max_items=2)
    parsed["selected_hashtags"] = normalize_string_list(parsed.get("selected_hashtags"), max_items=18)
    parsed["hashtags_alternative_set"] = normalize_string_list(parsed.get("hashtags_alternative_set"), max_items=18)
    parsed["selected_story_frames"] = normalize_string_list(parsed.get("selected_story_frames"), max_items=3)
    return parsed


def agent_hashtag(text_model: str, api_key: str, analisi: str, trend: str) -> str:
    log("HASHTAG", "Costruzione set 30 hashtag in 4 tier...")
    prompt = f"""Sei un esperto di hashtag strategy per Instagram moda/bijoux in Italia.
{BRAND}
Analisi prodotto: {analisi[:400]}
Trend rilevati: {trend[:400]}

Crea 30 hashtag divisi in 4 tier (broad, niche, local, branded),
piu 3 hashtag emergenti, hashtag da evitare e strategia di rotazione su 4 post."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=1500)
    log("HASHTAG", "30 hashtag + strategia rotazione completati", "success")
    return result


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

    print("\nMONILI MEDIA AGENCY - avvio pipeline AI", flush=True)
    print(f"Foto: {foto_path}", flush=True)
    print(f"Brief: {brief or 'auto-analisi'}", flush=True)
    print(f"Modello testo: {selected_text_model}", flush=True)
    print(f"Modello immagini: {selected_image_model}", flush=True)
    print(f"Output: {output_dir}\n", flush=True)

    log("SUPERVISOR", "Missione ricevuta. Avvio orchestrazione team.")
    log("SUPERVISOR", "Team 2.0 attivo: strategia, statico, local SEO, distribuzione.", "data")

    trend = ""
    analisi = ""
    strategy = ""
    strategy_plan = strategy_plan_defaults()
    merchandising = ""
    shooting = ""
    visual_prompts = ""
    ai_images: list[str] = []
    instagram_visual_prompts = ""
    instagram_sources: dict[str, str] = {}
    carousel = ""
    carousel_slide_texts: dict = {}
    local_visibility = ""
    distribution = ""
    publish_pack: dict = {}
    publish_pack_md = ""
    copy = ""
    hashtag = ""
    image_feed = ""
    image_stories = ""
    carousel_visual_prompts = ""
    carousel_images: list[str] = []
    showcase_visual_prompts = ""
    showcase_images: list[str] = []

    def safe_write(path: Path, content: str):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            log("SISTEMA", f"Scrittura file fallita ({path.name}): {e}", "warn")

    trend = "Flusso rapido Static Content Studio: focus su post, stories, carousel copy, WhatsApp e sito."
    log("TREND INTEL", "Saltato nel flusso rapido: uso regole brand/locali gia memorizzate.", "data")

    try:
        analisi = agent_analisi(selected_text_model, api_key, foto, brief)
        safe_write(output_dir / "01_ANALISI" / "product_card.md", f"# Scheda Prodotto\n\n{analisi}")
    except Exception as e:
        log("ANALISTA", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    strategy = (
        "Strategia rapida: creare un kit statico pronto per negozio locale "
        "con post Instagram, stories, eventuale carousel copy, WhatsApp, Google Business e sito vetrina."
    )
    safe_write(output_dir / "02_STRATEGIA" / "strategy.md", f"# Strategia Rapida\n\n{strategy}")
    log("STRATEGIST", "Strategia rapida impostata senza report lungo.", "success")

    try:
        merchandising = agent_merchandising(selected_text_model, api_key, foto, analisi, brief)
        safe_write(output_dir / "02_STRATEGIA" / "merchandising_styling.md", f"# Merchandising e Styling\n\n{merchandising}")
    except Exception as e:
        log("MERCHANDISER", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        strategy_plan = agent_strategy_plan(selected_text_model, api_key, foto, analisi, strategy, merchandising, brief)
        if brief_requests_carousel(brief):
            strategy_plan["needs_carousel"] = True
            strategy_plan["primary_output"] = "carousel_product"
        safe_write(output_dir / "02_STRATEGIA" / "strategy_plan.json", json.dumps(strategy_plan, indent=2, ensure_ascii=False))
        log("STRATEGIST", f"Piano dinamico: {strategy_plan_summary(strategy_plan)}", "data")
    except Exception as e:
        log("STRATEGIST", f"ERRORE piano dinamico: {e}\n{traceback.format_exc()}", "warn")

    log("FOTO DIR.", "Guida foto reale saltata nel flusso rapido: creo direttamente asset statici AI.", "data")

    try:
        visual_prompts = agent_visual_prompts(
            selected_text_model,
            api_key,
            foto,
            analisi,
            strategy,
            merchandising,
            shooting,
            strategy_plan,
        )
        safe_write(output_dir / "03_ASSET_STATICI" / "visual_ai_prompts.md", f"# Prompt Visual AI Fotorealistici\n\n{visual_prompts}")
        log("VISUAL GEN", "Visual extra saltati: priorita a post, stories e carousel.", "data")
    except Exception as e:
        log("VISUAL GEN", f"ERRORE: {e}", "warn")

    try:
        instagram_visual_prompts = agent_instagram_visual_prompts(
            selected_text_model,
            api_key,
            foto,
            analisi,
            strategy,
            merchandising,
            strategy_plan,
            brief,
        )
        safe_write(
            output_dir / "05_FOTO_OTTIMIZZATE" / "instagram_visual_prompts.txt",
            instagram_visual_prompts,
        )
        instagram_sources = generate_instagram_images(
            output_dir,
            api_key,
            selected_image_model,
            foto,
            instagram_visual_prompts,
        )
    except Exception as e:
        log("INSTAGRAM VISUAL", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        showcase_visual_prompts = agent_showcase_visual_prompts(
            selected_text_model,
            api_key,
            foto,
            analisi,
            strategy,
            merchandising,
            brief,
        )
        safe_write(output_dir / "07_SHOWCASE" / "showcase_visual_prompts.txt", showcase_visual_prompts)
        showcase_images = generate_showcase_images(
            output_dir,
            api_key,
            selected_image_model,
            foto,
            showcase_visual_prompts,
        )
        if not showcase_images:
            showcase_images = create_showcase_fallback_images(output_dir, foto, "Images 2 non ha restituito foto sito dedicate")
    except Exception as e:
        log("SITO VISUAL", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")
        showcase_images = create_showcase_fallback_images(output_dir, foto, "errore generazione immagini sito")

    should_generate_carousel = to_bool(strategy_plan.get("needs_carousel"))
    should_generate_carousel_images = should_generate_carousel and os.environ.get("MAX_CAROUSEL_IMAGES", "1").strip() != "0"
    if should_generate_carousel:
        try:
            carousel = agent_carousel(selected_text_model, api_key, analisi, strategy, trend)
            safe_write(output_dir / "04_CAROUSEL" / "carousel_statici.md", f"# Carousel Statici\n\n{carousel}")
        except Exception as e:
            log("CAROUSEL", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    if should_generate_carousel and not should_generate_carousel_images:
        log("CAROUSEL VISUAL", "CAROSELLO non generato: immagini carousel disattivate da MAX_CAROUSEL_IMAGES=0.", "data")

    if should_generate_carousel_images:
        try:
            carousel_visual_prompts = agent_carousel_visual_prompts(
                selected_text_model,
                api_key,
                analisi,
                strategy,
                merchandising,
                carousel,
                brief,
            )
            safe_write(
                output_dir / "04_CAROUSEL" / "carousel_visual_prompts.txt",
                carousel_visual_prompts,
            )
            slide_prompts = extract_carousel_slide_prompts(
                carousel_visual_prompts,
                max_slides=desired_carousel_slide_count(strategy_plan),
            )
            carousel_images = generate_carousel_images(
                output_dir,
                api_key,
                selected_image_model,
                foto,
                slide_prompts,
            )
        except Exception as e:
            log("CAROUSEL VISUAL", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")
    else:
        log("CAROUSEL", "CAROSELLO non presente nella strategia: lo strategist ha scelto un formato non-carousel per questo prodotto.", "data")

    local_visibility = (
        "Usa sempre local intent: I Monili Ravenna, centro storico, Via Cavour, "
        "WhatsApp e passaggio in negozio."
    )
    distribution = (
        "Distribuzione rapida: pubblica il post oggi, usa 3 stories statiche come richiamo, "
        "riusa il testo breve su Google Business e WhatsApp."
    )
    safe_write(output_dir / "05_LOCAL_VISIBILITY" / "local_visibility.md", f"# Local Visibility Rapida\n\n{local_visibility}")
    safe_write(output_dir / "06_DISTRIBUZIONE" / "caption_whatsapp_piano.md", f"# Distribuzione Rapida\n\n{distribution}")
    log("DISTRIBUZIONE", "Piano rapido creato senza chiamata lunga.", "success")

    try:
        publish_pack = agent_publish_pack(
            selected_text_model,
            api_key,
            analisi,
            strategy,
            strategy_plan,
            carousel,
            local_visibility,
            distribution,
            brief,
        )
        publish_pack_md = format_publish_pack_markdown(publish_pack)
        safe_write(output_dir / "06_DISTRIBUZIONE" / "publish_pack.json", json.dumps(publish_pack, indent=2, ensure_ascii=False))
        safe_write(output_dir / "06_DISTRIBUZIONE" / "publish_pack.md", publish_pack_md)
        log("PUBLISH PACK", "Output pronto pubblicazione completato", "success")
    except Exception as e:
        log("PUBLISH PACK", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    if should_generate_carousel:
        try:
            carousel_slide_texts = agent_carousel_slide_texts(
                selected_text_model,
                api_key,
                analisi,
                strategy,
                carousel,
                publish_pack,
            )
            safe_write(
                output_dir / "04_CAROUSEL" / "carousel_slide_texts.json",
                json.dumps(carousel_slide_texts, indent=2, ensure_ascii=False),
            )
        except Exception as e:
            log("CAROUSEL COPY", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # Backward-compatible legacy outputs while the 2.0 UI migrates.
    copy = distribution
    hashtag = distribution

    log("FOTO OTT.", "Ottimizzazione foto per Instagram (feed 1:1 + Stories 9:16)...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        from optimize_image import optimize, optimize_from_sources

        instagram_source = foto
        stories_source = foto
        source_kind = "foto originale"
        if instagram_sources.get("feed_source") or instagram_sources.get("story_source"):
            instagram_source = Path(instagram_sources.get("feed_source") or instagram_sources.get("story_source") or str(foto))
            stories_source = Path(instagram_sources.get("story_source") or instagram_sources.get("feed_source") or str(foto))
            source_kind = "visual Instagram AI dedicati"
        elif ai_images:
            candidate_rel = ai_images[0]
            candidate_abs = OUTPUT_ROOT / candidate_rel
            if candidate_abs.exists():
                instagram_source = candidate_abs
                stories_source = candidate_abs
                source_kind = "visual AI migliorato"
        elif carousel_images:
            candidate_rel = carousel_images[0]
            candidate_abs = Path("output") / candidate_rel
            if candidate_abs.exists():
                instagram_source = candidate_abs
                stories_source = candidate_abs
                source_kind = "slide AI carousel"

        log("FOTO OTT.", f"Base Instagram: {source_kind}", "data")
        if source_kind == "visual Instagram AI dedicati":
            optimize_from_sources(str(instagram_source), str(stories_source), str(output_dir / "05_FOTO_OTTIMIZZATE"))
        else:
            optimize(str(instagram_source), str(output_dir / "05_FOTO_OTTIMIZZATE"))
        output_subdir = output_dir.name
        image_feed = f"{output_subdir}/05_FOTO_OTTIMIZZATE/post_1080x1350.jpg"
        image_stories = f"{output_subdir}/05_FOTO_OTTIMIZZATE/stories_1080x1920.jpg"
        log("FOTO OTT.", "Post 1080x1350 e Stories 1080x1920 salvate leggere", "success")
    except Exception as e:
        log("FOTO OTT.", f"Ottimizzazione non riuscita: {e}\n{traceback.format_exc()}", "warn")

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
                "strategy": strategy[:1200],
                "strategy_plan": strategy_plan,
                "merchandising": merchandising[:1200],
                "ai_images": ai_images,
                "instagram_sources": instagram_sources,
                "showcase_images": showcase_images,
                "carousel_slide_texts": carousel_slide_texts,
            }
        )
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text(json.dumps(log_data, indent=2, ensure_ascii=False), encoding="utf-8")
        log("MEMORIA", "Sessione loggata. Memoria persistente aggiornata.", "success")
    except Exception as e:
        log("MEMORIA", f"Log non salvato: {e}", "warn")

    print("\nMISSIONE COMPLETATA!", flush=True)
    print(f"Output: {output_dir}", flush=True)

    results = {
        "run_id": run_id,
        "output_dir": output_dir.name,
        "publish_pack": publish_pack_md,
        "publish_pack_json": json.dumps(publish_pack, ensure_ascii=False),
        "strategy": f"# Strategia 2.0\n\n{strategy}",
        "strategy_plan": json.dumps(strategy_plan, indent=2, ensure_ascii=False),
        "merchandising": f"# Merchandising e Styling\n\n{merchandising}",
        "analisi": f"# Scheda Prodotto\n\n{analisi}",
        "shooting": f"# Guida Foto Reale\n\n{shooting}",
        "visual_prompts": f"# Prompt Visual AI Fotorealistici\n\n{visual_prompts}",
        "instagram_visual_prompts": instagram_visual_prompts,
        "showcase_visual_prompts": showcase_visual_prompts,
        "carousel_visual_prompts": carousel_visual_prompts,
        "carousel_slide_texts_json": json.dumps(carousel_slide_texts, ensure_ascii=False),
        "carousel": f"# Carousel Statici\n\n{carousel}",
        "local_visibility": f"# Local Visibility\n\n{local_visibility}",
        "distribution": f"# Distribuzione\n\n{distribution}",
        "copy": f"# Caption, WhatsApp e Piano 7 Giorni\n\n{copy}",
        "hashtag": f"# Hashtag e Rotazione\n\n{hashtag}",
        "image_feed": image_feed,
        "image_stories": image_stories,
    }
    for idx, image_path in enumerate(showcase_images, start=1):
        results[f"image_site_{idx}"] = image_path
    for idx, image_path in enumerate(ai_images, start=1):
        results[f"image_ai_{idx}"] = image_path
    for idx, image_path in enumerate(carousel_images, start=1):
        results[f"image_carousel_{idx}"] = image_path
    for idx in range(1, 4):
        story_source = instagram_sources.get(f"story_{idx}_source")
        if story_source:
            story_path = Path(story_source)
            try:
                results[f"image_story_{idx}"] = f"{output_dir.name}/{story_path.relative_to(output_dir).as_posix()}"
            except ValueError:
                results[f"image_story_{idx}"] = str(story_path)

    story_image_count = len([key for key in results if key.startswith("image_story_")])
    asset_reports = []
    for key, value in results.items():
        if key.startswith("image_") and isinstance(value, str) and value:
            asset_reports.append(image_file_report(value))
    results["decision_summary"] = build_decision_summary(
        publish_pack,
        showcase_images,
        carousel_images,
        story_image_count,
    )
    results["asset_report_json"] = json.dumps(asset_reports, ensure_ascii=False)

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
    parser = argparse.ArgumentParser(description="Monili Media Agency - Kit marketing da foto prodotto")
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
