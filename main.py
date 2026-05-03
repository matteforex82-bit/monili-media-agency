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


def agent_visual_prompts(text_model: str, api_key: str, foto: Path, analisi: str, strategy: str, shooting: str) -> str:
    log("VISUAL AI", "Brief fotorealistici per indossato, sfondo e contesto...")
    prompt = f"""Sei un art director specializzato in visual AI fotorealistici per piccoli negozi locali.
{BRAND}
Analisi prodotto: {analisi[:900]}
Strategia: {strategy[:900]}
Guida foto reale: {shooting[:700]}

Genera 4 prompt in inglese per immagini statiche AI usando la foto caricata come riferimento.
Ogni prompt deve iniziare con "Prompt EN:".

Obiettivo: far vedere il prodotto in contesto reale senza farlo sembrare finto.

Prompt richiesti:
1. Hero su sfondo pulito e migliore
2. Indossato realistico (mano/orecchio/collo/modella/manichino in base al prodotto)
3. Lifestyle quasi Ravenna: luce naturale, centro storico italiano, boutique locale, niente landmark inventati troppo evidenti
4. Visual per cover carousel

Regole obbligatorie in ogni prompt:
- preserve the exact product shape, color, material, proportions, texture and distinctive details from the reference photo
- photorealistic, natural daylight, authentic small Italian boutique style
- no plastic skin, no luxury stock-photo look, no unrealistic body, no fantasy jewelry
- do not change the product into a different item
- no text, no logos, no watermark
- if worn by a model, use a realistic adult model, natural pose, product visible but not exaggerated

Rispondi solo con i 4 prompt, uno per blocco, senza spiegazioni."""
    result = generate_text_with_openrouter(api_key, text_model, prompt, image_path=foto, max_tokens=1600)
    log("VISUAL AI", "Prompt visual controllati pronti", "success")
    return result


def agent_visual_gen(output_dir: Path, visual_prompts: str, selected_model: str, api_key: str, foto: Path) -> list[str]:
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

    max_visuals = int(os.environ.get("MAX_AI_VISUALS", "3"))
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
Preserve the exact product. Create a realistic static commercial photo, not a video frame."""
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


def agent_distribution(text_model: str, api_key: str, analisi: str, strategy: str, carousel: str) -> str:
    log("DISTRIBUZIONE", "Caption, WhatsApp e piano 7 giorni...")
    prompt = f"""Sei una social media manager per piccoli negozi.
{BRAND}
Strategia scelta: {strategy[:900]}
Analisi prodotto: {analisi[:700]}
Carousel generato: {carousel[:900]}

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
- Quando pubblicare il carousel
- Quando fare story di richiamo
- Quando pubblicare Google Business
- Come riutilizzare il contenuto senza sembrare ripetitivo"""
    result = generate_text_with_openrouter(api_key, text_model, prompt, max_tokens=2200)
    log("DISTRIBUZIONE", "Caption, hashtag, WhatsApp e piano 7 giorni pronti", "success")
    return result


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
    data = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(f"output/{data}_{nome}")
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
    shooting = ""
    visual_prompts = ""
    ai_images: list[str] = []
    carousel = ""
    local_visibility = ""
    distribution = ""
    copy = ""
    hashtag = ""
    image_feed = ""
    image_stories = ""

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
        shooting = agent_shooting(selected_text_model, api_key, foto, analisi)
        safe_write(output_dir / "03_ASSET_STATICI" / "guida_foto_reale.md", f"# Guida Foto Reale\n\n{shooting}")
    except Exception as e:
        log("FOTO DIR.", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        visual_prompts = agent_visual_prompts(selected_text_model, api_key, foto, analisi, strategy, shooting)
        safe_write(output_dir / "03_ASSET_STATICI" / "visual_ai_prompts.md", f"# Prompt Visual AI Fotorealistici\n\n{visual_prompts}")
        ai_images = agent_visual_gen(output_dir, visual_prompts, selected_image_model, api_key, foto)
    except Exception as e:
        log("VISUAL GEN", f"ERRORE: {e}", "warn")

    try:
        carousel = agent_carousel(selected_text_model, api_key, analisi, strategy, trend)
        safe_write(output_dir / "04_CAROUSEL" / "carousel_statici.md", f"# Carousel Statici\n\n{carousel}")
    except Exception as e:
        log("CAROUSEL", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        local_visibility = agent_local_visibility(selected_text_model, api_key, analisi, strategy, brief)
        safe_write(output_dir / "05_LOCAL_VISIBILITY" / "local_visibility.md", f"# Local Visibility\n\n{local_visibility}")
    except Exception as e:
        log("LOCAL SEO", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    try:
        distribution = agent_distribution(selected_text_model, api_key, analisi, strategy, carousel)
        safe_write(output_dir / "06_DISTRIBUZIONE" / "caption_whatsapp_piano.md", f"# Distribuzione\n\n{distribution}")
    except Exception as e:
        log("DISTRIBUZIONE", f"ERRORE: {e}\n{traceback.format_exc()}", "warn")

    # Backward-compatible legacy outputs while the 2.0 UI migrates.
    copy = distribution
    hashtag = distribution

    log("FOTO OTT.", "Ottimizzazione foto per Instagram (feed 1:1 + Stories 9:16)...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))
        from optimize_image import optimize

        optimize(str(foto), str(output_dir / "05_FOTO_OTTIMIZZATE"))
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
        "strategy": f"# Strategia 2.0\n\n{strategy}",
        "analisi": f"# Scheda Prodotto\n\n{analisi}",
        "shooting": f"# Guida Foto Reale\n\n{shooting}",
        "visual_prompts": f"# Prompt Visual AI Fotorealistici\n\n{visual_prompts}",
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
