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

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SUPPORTED_OPENROUTER_IMAGE_MODELS = [
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


def generate_image_with_openrouter(api_key: str, model: str, prompt: str, image_path: Path | None = None) -> list[str]:
    modalities = ["image", "text"] if model.startswith("google/gemini") else ["image"]
    image_config = {"aspect_ratio": "1:1", "image_size": "1K"} if model.startswith("google/gemini") else None

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
        "product_type": "unknown",
        "primary_output": "single_post",
        "secondary_output": "story_recall",
        "needs_carousel": False,
        "needs_worn_visual": True,
        "needs_street_visual": True,
        "visual_count": 3,
        "visual_focus": ["hero_clean", "worn", "street_context"],
        "styling_items": [],
        "model_direction": "realistic adult model, natural pose",
        "scene_concepts": ["premium product hero", "worn lifestyle", "Italian street context"],
        "rationale": "Piano fallback: post statico con visual realistici.",
    }


def strategy_plan_summary(plan: dict) -> str:
    primary = str(plan.get("primary_output", "single_post"))
    secondary = str(plan.get("secondary_output", "story_recall"))
    needs_carousel = to_bool(plan.get("needs_carousel"))
    needs_worn = to_bool(plan.get("needs_worn_visual"))
    needs_street = to_bool(plan.get("needs_street_visual"))
    visual_count = int(plan.get("visual_count", 3))
    visual_focus = normalize_string_list(plan.get("visual_focus"), max_items=8)
    scenes = normalize_string_list(plan.get("scene_concepts"), max_items=5)
    return (
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
  "product_type": "jewelry|clothing|accessory|other",
  "primary_output": "single_post|carousel_product|carousel_educational|gmb_post|story_pack",
  "secondary_output": "single_post|carousel_product|carousel_educational|gmb_post|story_pack",
  "needs_carousel": true/false,
  "needs_worn_visual": true/false,
  "needs_street_visual": true/false,
  "visual_count": 2-5,
  "visual_focus": ["hero_clean","worn","street_context","material_closeup","outfit_match","local_store_context","editorial_detail","gift_context"],
  "styling_items": ["item1", "item2", "item3"],
  "model_direction": "descrizione breve della modella/posa se utile",
  "scene_concepts": ["scena fotorealistica 1", "scena fotorealistica 2", "scena fotorealistica 3"],
  "rationale": "max 2 frasi"
}}

Regole:
- Se prodotto e abbigliamento, normalmente needs_worn_visual=true.
- Se primary_output non e carousel, needs_carousel=false.
- Evita output ripetitivo, scegli il formato in base al prodotto.
- Puoi usare modella AI, location inventate, styling e props se aiutano a vendere, ma il prodotto deve restare identico.
- Nessun testo fuori JSON."""
    raw = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1200)
    parsed = extract_json_object(raw)
    if not parsed:
        log("STRATEGIST", "Piano JSON non valido, uso fallback", "warn")
        return strategy_plan_defaults()

    base = strategy_plan_defaults()
    base["product_type"] = str(parsed.get("product_type", base["product_type"])).strip() or base["product_type"]
    base["primary_output"] = str(parsed.get("primary_output", base["primary_output"])).strip() or base["primary_output"]
    base["secondary_output"] = str(parsed.get("secondary_output", base["secondary_output"])).strip() or base["secondary_output"]
    base["needs_carousel"] = to_bool(parsed.get("needs_carousel"))
    base["needs_worn_visual"] = to_bool(parsed.get("needs_worn_visual"))
    base["needs_street_visual"] = to_bool(parsed.get("needs_street_visual"))
    try:
        base["visual_count"] = max(2, min(5, int(parsed.get("visual_count", base["visual_count"]))))
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
    base["rationale"] = str(parsed.get("rationale", base["rationale"])).strip() or base["rationale"]

    primary = base["primary_output"]
    if primary not in {"carousel_product", "carousel_educational"}:
        base["needs_carousel"] = False
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
    prompt = f"""Sei un art director specializzato in visual AI fotorealistici per piccoli negozi locali.
{BRAND}
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
Il primo prompt deve essere la migliore immagine finale per Instagram feed.

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
    prompt = f"""Sei un visual strategist per Instagram carousel statici fotorealistici.
{BRAND}
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
- invent believable Ravenna/Italian boutique lifestyle scenes when useful, without recognizable fake landmarks
- use realistic model, hand, ear, neck, outfit, props and complementary products when they help sell the item
- make every slide look like a finished publishable photo, not a planning mockup
- no text overlays, no logos, no watermark
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
            controlled = f"""{prompt}

Use the uploaded reference photo as source-of-truth for the product.
The product must remain faithful to the reference.
You may invent model, location, outfit, props and lighting to make the slide more desirable.
The result must look like a finished premium photorealistic still photo for Instagram carousel."""
            data_urls = generate_image_with_openrouter(api_key, model, controlled, image_path=foto)
            if not data_urls:
                continue
            filename = f"carousel_slide_{idx}.png"
            file_path = target_dir / filename
            if save_data_url_image(data_urls[0], file_path):
                generated.append(f"{output_dir.name}/04_CAROUSEL/images/{filename}")
        except Exception as e:
            log("CAROUSEL VISUAL", f"Slide {idx} non generata: {e}", "warn")

    if generated:
        log("CAROUSEL VISUAL", f"{len(generated)} slide carousel generate", "success")
    else:
        log("CAROUSEL VISUAL", "Nessuna slide carousel generata", "warn")
    return generated


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
    output_dir = Path(f"output/{run_id}_{nome}")
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
    carousel = ""
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

    def safe_write(path: Path, content: str):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            log("SISTEMA", f"Scrittura file fallita ({path.name}): {e}", "warn")

    try:
        trend = agent_trend(selected_text_model, api_key)
        safe_write(output_dir / "00_TREND" / "trend_report.md", f"# Trend Report P/E 2026\n\n{trend}")
    except Exception as e:
        log("TREND", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        analisi = agent_analisi(selected_text_model, api_key, foto, brief)
        safe_write(output_dir / "01_ANALISI" / "product_card.md", f"# Scheda Prodotto\n\n{analisi}")
    except Exception as e:
        log("ANALISTA", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        strategy = agent_strategy(selected_text_model, api_key, foto, analisi, brief, trend)
        safe_write(output_dir / "02_STRATEGIA" / "strategy.md", f"# Strategia 2.0\n\n{strategy}")
    except Exception as e:
        log("STRATEGIST", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        merchandising = agent_merchandising(selected_text_model, api_key, foto, analisi, brief)
        safe_write(output_dir / "02_STRATEGIA" / "merchandising_styling.md", f"# Merchandising e Styling\n\n{merchandising}")
    except Exception as e:
        log("MERCHANDISER", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        strategy_plan = agent_strategy_plan(selected_text_model, api_key, foto, analisi, strategy, merchandising, brief)
        safe_write(output_dir / "02_STRATEGIA" / "strategy_plan.json", json.dumps(strategy_plan, indent=2, ensure_ascii=False))
        log("STRATEGIST", f"Piano dinamico: {strategy_plan_summary(strategy_plan)}", "data")
    except Exception as e:
        log("STRATEGIST", f"ERRORE piano dinamico: {e}\n{traceback.format_exc()}", "warn")

    try:
        shooting = agent_shooting(selected_text_model, api_key, foto, analisi)
        safe_write(output_dir / "03_ASSET_STATICI" / "guida_foto_reale.md", f"# Guida Foto Reale\n\n{shooting}")
    except Exception as e:
        log("FOTO DIR.", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

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
        ai_images = agent_visual_gen(
            output_dir,
            visual_prompts,
            selected_image_model,
            api_key,
            foto,
            max_visuals_override=int(strategy_plan.get("visual_count", 3)),
        )
    except Exception as e:
        log("VISUAL GEN", f"ERRORE: {e}", "warn")

    should_generate_carousel = to_bool(strategy_plan.get("needs_carousel"))
    if should_generate_carousel:
        try:
            carousel = agent_carousel(selected_text_model, api_key, analisi, strategy, trend)
            safe_write(output_dir / "04_CAROUSEL" / "carousel_statici.md", f"# Carousel Statici\n\n{carousel}")
        except Exception as e:
            log("CAROUSEL", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

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
            slide_prompts = extract_carousel_slide_prompts(carousel_visual_prompts, max_slides=5)
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
        log("CAROUSEL", "Saltato: strategist ha scelto formato non-carousel per questo prodotto.", "data")

    try:
        local_visibility = agent_local_visibility(selected_text_model, api_key, analisi, strategy, brief)
        safe_write(output_dir / "05_LOCAL_VISIBILITY" / "local_visibility.md", f"# Local Visibility\n\n{local_visibility}")
    except Exception as e:
        log("LOCAL SEO", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        distribution = agent_distribution(selected_text_model, api_key, analisi, strategy, strategy_plan, carousel)
        safe_write(output_dir / "06_DISTRIBUZIONE" / "caption_whatsapp_piano.md", f"# Distribuzione\n\n{distribution}")
    except Exception as e:
        log("DISTRIBUZIONE", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

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

    # Backward-compatible legacy outputs while the 2.0 UI migrates.
    copy = distribution
    hashtag = distribution

    log("FOTO OTT.", "Ottimizzazione foto per Instagram (feed 1:1 + Stories 9:16)...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        from optimize_image import optimize

        instagram_source = foto
        source_kind = "foto originale"
        if ai_images:
            candidate_rel = ai_images[0]
            candidate_abs = Path("output") / candidate_rel
            if candidate_abs.exists():
                instagram_source = candidate_abs
                source_kind = "visual AI migliorato"
        elif carousel_images:
            candidate_rel = carousel_images[0]
            candidate_abs = Path("output") / candidate_rel
            if candidate_abs.exists():
                instagram_source = candidate_abs
                source_kind = "slide AI carousel"

        log("FOTO OTT.", f"Base Instagram: {source_kind}", "data")
        optimize(str(instagram_source), str(output_dir / "05_FOTO_OTTIMIZZATE"))
        output_subdir = output_dir.name
        image_feed = f"{output_subdir}/05_FOTO_OTTIMIZZATE/feed_1080x1080.jpg"
        image_stories = f"{output_subdir}/05_FOTO_OTTIMIZZATE/stories_1080x1920.jpg"
        log("FOTO OTT.", "Feed 1080x1080 e Stories 1080x1920 salvate", "success")
    except Exception as e:
        log("FOTO OTT.", f"Ottimizzazione non riuscita: {e}\n{traceback.format_exc()}", "warn")

    log("MEMORIA", "Aggiornamento performance_log.json...")
    try:
        memory_path = Path("memory/performance_log.json")
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
            }
        )
        memory_path.parent.mkdir(exist_ok=True)
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
        "carousel_visual_prompts": carousel_visual_prompts,
        "carousel": f"# Carousel Statici\n\n{carousel}",
        "local_visibility": f"# Local Visibility\n\n{local_visibility}",
        "distribution": f"# Distribuzione\n\n{distribution}",
        "copy": f"# Caption, WhatsApp e Piano 7 Giorni\n\n{copy}",
        "hashtag": f"# Hashtag e Rotazione\n\n{hashtag}",
        "image_feed": image_feed,
        "image_stories": image_stories,
    }
    for idx, image_path in enumerate(ai_images, start=1):
        results[f"image_ai_{idx}"] = image_path
    for idx, image_path in enumerate(carousel_images, start=1):
        results[f"image_carousel_{idx}"] = image_path

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
