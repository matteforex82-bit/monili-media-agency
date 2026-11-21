"""post_grafica.py - I post Instagram con testo (PRD prompt completi, T5, 20/11/2026).

Tre tipi:
- "etichette": foto VERA del flat-lay; nomi dei pezzi e prezzi li disegna il codice. Nessuna AI, i prodotti non cambiano.
- "titolo" e "look": immagine fatta con GPT Image o Nano Banana dalla foto vera, titolo in serif su fondo caldo
  (look = con la testimonial Aurora). Il modello visivo rilegge il titolo e il codice lo confronta lettera per lettera;
  se non coincide si rigenera una volta, poi il titolo lo scrive il codice. Logo, prezzo e riferimento li mette
  sempre il codice: l'AI inventa loghi e cifre.
- "carosello": 3 slide con la stessa scena e gli stessi caratteri ("3 modi di indossarlo"), didascalia unica.

Ogni immagine realistica fatta con l'AI è marcata aiGenerated: su Instagram va l'etichetta "Info sull'AI".
I file stanno in <missione>/08_POST, l'elenco in 08_POST/posts.json.
"""
from __future__ import annotations

import json
import re
import unicodedata
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

POST_DIR = "08_POST"
POST_SIZE = (1080, 1350)  # post 4:5
STORY_SIZE = (1080, 1920)  # Storie 9:16
FORMATS = {"post": POST_SIZE, "storia": STORY_SIZE}
# Solo questi due per i post con testo (decisione D5): il modello usato si mostra a schermo.
POST_MODELS = {"GPT Image": "openai/gpt-image-2.6-sunburst", "Nano Banana": "google/gemini-nano-banana-2.1"}
DEFAULT_POST_MODEL = "GPT Image"
CLOSING = "Scrivici, ti diciamo se è disponibile"
FORBIDDEN_PHRASES = ("te lo mettiamo da parte", "mettiamo da parte")
SHOP_LINES = {"17": "Via Cavour 17", "21": "Via Cavour 21"}
LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo-monili.png"
PAPER, INK, SOFT, TERRACOTTA = (246, 241, 230), (34, 30, 26), (96, 88, 78), (178, 84, 52)
MAX_TITLE = 70
QUOTES = {chr(0x2019): "'", chr(0x2018): "'", chr(0x201C): '"', chr(0x201D): '"'}


def _font(name: str, size: int):
    import reel_studio

    return reel_studio._font(name, size)


def _fit(photo: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(ImageOps.exif_transpose(photo).convert("RGB"), size, Image.LANCZOS, centering=(0.5, 0.45))


def format_price(value: object) -> str:
    """'29' -> '29 €', '29,5' -> '29,50 €'. Empty or not a number: '' (decision D1: no price, nothing is written)."""
    text = str(value if value is not None else "").replace("€", "").replace("euro", "").strip().replace(",", ".")
    try:
        number = float(text)
    except ValueError:
        return ""
    if number <= 0:
        return ""
    return (f"{number:.0f}" if number == int(number) else f"{number:.2f}".replace(".", ",")) + " €"


def clean_text(value: object, limit: int = MAX_TITLE) -> str:
    text = " ".join(str(value or "").split())[:limit]
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text.lower():
            raise ValueError(f'"{phrase}" non si scrive mai: la riserva nasce solo dopo la verifica in negozio.')
    return text


# -- logo e testi disegnati dal codice ---------------------------------------------------------------------------
def add_logo(image: Image.Image, width_share: float = 0.22, bottom_margin: int = 46) -> Image.Image:
    """The real logo (assets/logo-monili.png) on a soft cream plate at the bottom centre."""
    if not LOGO_PATH.exists():
        return image
    out = image.convert("RGB").copy()
    with Image.open(LOGO_PATH) as logo:
        logo = logo.convert("RGBA")
        width = int(out.width * width_share)
        logo = logo.resize((width, round(logo.height * width / logo.width)), Image.LANCZOS)
    pad = 18
    box = (
        (out.width - width) // 2 - pad,
        out.height - bottom_margin - logo.height - pad,
        (out.width + width) // 2 + pad,
        out.height - bottom_margin + pad,
    )
    plate = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(plate).rounded_rectangle(box, radius=22, fill=(*PAPER, 215))
    out = Image.alpha_composite(out.convert("RGBA"), plate)
    out.paste(logo, (box[0] + pad, box[1] + pad), logo)
    return out.convert("RGB")


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    lines: list[str] = []
    for word in text.split():
        trial = f"{lines[-1]} {word}" if lines else word
        if lines and draw.textlength(trial, font=font) <= max_width:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


def draw_title(image: Image.Image, title: str, subtitle: str = "") -> Image.Image:
    """The editorial title written by the code (used when the AI got a letter wrong): cream band at the top,
    elegant serif, dark ink; the subtitle in italic terracotta."""
    out = image.convert("RGB").copy()
    draw = ImageDraw.Draw(out)
    width = out.width
    font = _font("GARA.TTF", int(width * 0.075))
    italic = _font("GARAIT.TTF", int(width * 0.04))
    lines = _wrap(draw, title, font, int(width * 0.84))
    line_h = int(font.size * 1.15)
    band_h = int(width * 0.09) + line_h * len(lines) + (int(italic.size * 1.6) if subtitle else 0)
    band = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle((0, 0, width, band_h), fill=(*PAPER, 236))
    out = Image.alpha_composite(out.convert("RGBA"), band).convert("RGB")
    draw = ImageDraw.Draw(out)
    y = int(width * 0.05)
    for line in lines:
        draw.text(((width - draw.textlength(line, font=font)) / 2, y), line, font=font, fill=INK)
        y += line_h
    if subtitle:
        draw.text(((width - draw.textlength(subtitle, font=italic)) / 2, y + 6), subtitle, font=italic, fill=TERRACOTTA)
    return out


def _tag(image: Image.Image, box: tuple[int, int, int, int], rows: list[tuple[str, object, tuple]]) -> Image.Image:
    shadow = Image.new("L", image.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle((box[0] + 4, box[1] + 8, box[2] + 4, box[3] + 8), radius=18, fill=90)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    out = Image.composite(Image.new("RGB", image.size, (60, 45, 30)), image.convert("RGB"), shadow)
    draw = ImageDraw.Draw(out)
    draw.rounded_rectangle(box, radius=18, fill=PAPER)
    y = box[1] + 14
    for text, font, colour in rows:
        if not text:
            continue
        draw.text((box[0] + 24, y), text, font=font, fill=colour)
        y += int(font.size * 1.3)
    return out


def draw_price_tag(image: Image.Image, price: str, reference: str = "", corner: str = "basso-destra") -> Image.Image:
    """Price (and piece reference) drawn by the code, never by the AI."""
    if not price and not reference:
        return image
    out = image.convert("RGB").copy()
    draw = ImageDraw.Draw(out)
    big = _font("GARA.TTF", int(out.width * 0.05))
    small = _font("GARA.TTF", int(out.width * 0.024))
    w = int(max(draw.textlength(price, font=big) if price else 0, draw.textlength(reference, font=small) if reference else 0)) + 48
    h = (int(big.size * 1.3) if price else 0) + (int(small.size * 1.3) if reference else 0) + 28
    margin = int(out.width * 0.05)
    x = out.width - w - margin if "destra" in corner else margin
    y = out.height - h - int(out.height * 0.2) if "basso" in corner else int(out.height * 0.06)
    return _tag(out, (x, y, x + w, y + h), [(price, big, TERRACOTTA), (reference, small, SOFT)])


# -- T5a: foto vera + etichette -----------------------------------------------------------------------------------
def _with_rif(reference: str) -> str:
    return f"Rif. {reference}" if reference and not reference.lower().startswith("rif") else reference


def normalize_items(items: object) -> list[dict]:
    """Each piece of the flat-lay: name, price, reference, shop (17 or 21: chosen by who publishes), position x/y in 0..1."""
    out: list[dict] = []
    for raw in items if isinstance(items, list) else []:
        if not isinstance(raw, dict):
            continue
        name = clean_text(raw.get("name"), 40)
        if not name:
            continue
        shop = str(raw.get("shop") or "").strip()
        item = {
            "name": name,
            "price": format_price(raw.get("price")),
            "reference": _with_rif(clean_text(raw.get("reference"), 20)),
            "shop": shop if shop in SHOP_LINES else "",
        }
        for key in ("x", "y"):
            try:
                item[key] = min(0.95, max(0.0, float(raw.get(key))))
            except (TypeError, ValueError):
                pass
        out.append(item)
    return out[:8]


def label_post(photo: Image.Image, items: list[dict], fmt: str = "post") -> Image.Image:
    """The real flat-lay photo with a tag for each piece (serif italic name, price in terracotta, reference and shop)
    and the real logo. Pieces without a position are stacked along the right edge."""
    size = FORMATS.get(fmt, POST_SIZE)
    out = _fit(photo, size)
    draw = ImageDraw.Draw(out)
    name_font = _font("GARAIT.TTF", int(size[0] * 0.04))
    price_font = _font("GARABD.TTF", int(size[0] * 0.036))
    small = _font("GARA.TTF", int(size[0] * 0.022))
    auto_y = int(size[1] * 0.06)
    for item in items:
        rows = [
            (item["name"], name_font, INK),
            (item.get("price", ""), price_font, TERRACOTTA),
            (" · ".join(filter(None, (item.get("reference"), SHOP_LINES.get(item.get("shop", ""), "")))), small, SOFT),
        ]
        w = int(max(draw.textlength(text, font=font) for text, font, _ in rows if text)) + 48
        h = sum(int(font.size * 1.3) for text, font, _ in rows if text) + 28
        if "x" in item and "y" in item:
            x, y = int(item["x"] * size[0]), int(item["y"] * size[1])
        else:
            x, y = size[0] - w - int(size[0] * 0.04), auto_y
            auto_y += h + 22
        x, y = max(10, min(x, size[0] - w - 10)), max(10, min(y, size[1] - h - 10))
        out = _tag(out, (x, y, x + w, y + h), rows)
        draw = ImageDraw.Draw(out)
    return add_logo(out)


# -- T5b: titolo editoriale e look con la modella ----------------------------------------------------------------
def _refs_line(woman_photos: int) -> str:
    if not woman_photos:
        return "Image 1: the real product, source-of-truth for shape, colours, stones, metal and stitching.\n"
    import casting

    faces = "Image 1" if woman_photos == 1 else f"Images 1-{woman_photos}"
    return (
        f"{faces}: the shop's testimonial Aurora. Take ONLY her face, skin and hair; ignore her clothes and jewellery. "
        f"{casting.OUTFIT_RULE} "
        f"Image {woman_photos + 1}: the real product, source-of-truth. Zero colour or texture blending between the images.\n"
    )


def post_prompt(kind: str, title: str, subtitle: str, subtype: str = "", cut: str = "", model: str = DEFAULT_POST_MODEL,
                woman_photos: int = 0, fmt: str = "post") -> str:
    """The image prompt for a post with an Italian title (GPT Image or Nano Banana), with the model's knowledge,
    the framing of the type, the shop's visual identity and its "never" list. Logo and price are NOT asked."""
    import casting
    import prompt_lab

    ratio = "vertical 9:16 Instagram story" if fmt == "storia" else "vertical 4:5 Instagram post (1080x1350)"
    scene = (
        "The product worn by the woman, framed as described in the framing notes; real photograph, authentic skin texture, "
        "warm natural light, a real place that suits a colourful artisan boutique in Ravenna."
        if kind == "look"
        else "The product as the hero on a warm cream background (light stone, linen or silk), soft natural window light, "
        "gentle shadow, generous negative space around it."
    )
    subtitle_line = f'Under it, smaller, in elegant italic serif, exactly once: "{subtitle}"\n' if subtitle else ""
    knowledge = "\n\n".join(filter(None, (
        prompt_lab.model_knowledge(model),
        prompt_lab.type_guide(subtype, cut) if kind == "look" else "",
    )))
    return f"""USE: {ratio} for I Monili Ravenna, an artisan jewellery and accessories boutique.
{_refs_line(woman_photos if kind == "look" else 0)}SCENE: {scene}
Preserve the exact product: same shape, proportions, colours, stones, metal finish and details as the reference. Do not add other jewellery.
TYPOGRAPHY: editorial, elegant high-contrast serif (Didot / Cormorant style) in dark espresso on a warm cream area at the top.
Headline, EXACT, verbatim, with its accents and punctuation, rendered exactly once: "{title}"
{subtitle_line}LAYOUT: headline in the top quarter; leave the bottom 18% calm and free of text (the shop adds its logo there).
No other text: no logo, no wordmark, no prices, no numbers, no hashtags, no watermark. Never comic, neon or sticker lettering.
{casting.never_line()}

KNOWLEDGE ON THE MODEL AND THE PIECE (follow it):
{knowledge}""".strip()


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFC", str(text or ""))
    for fancy, plain in QUOTES.items():
        text = text.replace(fancy, plain)
    return " ".join(text.split()).strip(" .\"'").casefold()


def text_matches(expected: str, read: str) -> bool:
    """Letter by letter (accents included: è is not e), ignoring only case, spaces and the final full stop."""
    return _norm(expected) == _norm(read)


READ_PROMPT = """Leggi il testo scritto in questa immagine, lettera per lettera, con accenti e punteggiatura come sono.
Non correggere niente: se una lettera è sbagliata, trascrivila sbagliata.
Rispondi SOLO con un JSON: {"titolo": "la scritta più grande", "sottotitolo": "la scritta sotto, o vuoto", "altro": ["ogni altra scritta, anche loghi o cifre"]}"""


def read_text(api_key: str, text_model: str, image_path: Path) -> dict:
    from main import extract_json_object, generate_text_with_openrouter

    parsed = extract_json_object(generate_text_with_openrouter(api_key, text_model, READ_PROMPT, image_path=image_path, max_tokens=400))
    others = parsed.get("altro") if isinstance(parsed.get("altro"), list) else []
    return {
        "titolo": str(parsed.get("titolo", "")).strip(),
        "sottotitolo": str(parsed.get("sottotitolo", "")).strip(),
        "altro": [str(x) for x in others if str(x).strip()],
    }


def check_text(read: dict, title: str, subtitle: str = "") -> dict:
    problems: list[str] = []
    if not text_matches(title, read.get("titolo", "")):
        problems.append(f'Titolo letto "{read.get("titolo", "")}" invece di "{title}"')
    if subtitle and not text_matches(subtitle, read.get("sottotitolo", "")):
        problems.append(f'Sottotitolo letto "{read.get("sottotitolo", "")}" invece di "{subtitle}"')
    invented = [t for t in read.get("altro", []) if re.search(r"\d|€", t)]
    if invented:
        problems.append("Cifre o prezzi inventati dall'AI: " + "; ".join(invented))
    return {"ok": not problems, "problems": problems, "read": read}


def make_ai_post(api_key: str, text_model: str, kind: str, title: str, subtitle: str, product: Path, destination: Path,
                 model: str = DEFAULT_POST_MODEL, subtype: str = "", cut: str = "", price: str = "", reference: str = "",
                 fmt: str = "post", woman_refs: list[Path] | None = None, attempts: int = 2) -> dict:
    """Generates, reads back the text, retries once; if the text is still wrong, the code writes the title on a version
    generated without text. Then the real logo and the price (if any) go on in code."""
    import reel_kit

    model = model if model in POST_MODELS else DEFAULT_POST_MODEL
    title, subtitle = clean_text(title), clean_text(subtitle, 90)
    if not title:
        raise ValueError("Scrivi il titolo del post.")
    refs = list(woman_refs or []) if kind == "look" else []
    prompt = post_prompt(kind, title, subtitle, subtype, cut, model, len(refs), fmt)
    size = FORMATS.get(fmt, POST_SIZE)
    ratio = "9:16" if fmt == "storia" else "4:5"
    destination.parent.mkdir(parents=True, exist_ok=True)
    raw = destination.with_name(destination.stem + "_raw.png")
    check_path = destination.with_name(destination.stem + "_check.jpg")
    checks: list[dict] = []
    image: Image.Image | None = None
    for _ in range(max(1, attempts)):
        reel_kit.generate_image_multi(api_key, POST_MODELS[model], prompt, refs + [product], raw, aspect_ratio=ratio)
        with Image.open(raw) as generated:
            image = _fit(generated, size)
        image.save(check_path, "JPEG", quality=90)
        check = check_text(read_text(api_key, text_model, check_path), title, subtitle)
        checks.append(check)
        if check["ok"]:
            break
    written_by = "ai"
    if not checks[-1]["ok"]:
        # the AI keeps getting a letter wrong: same scene without text, the title written by the code
        no_text = prompt.split("TYPOGRAPHY:")[0] + "No text of any kind in the image; keep the top quarter calm for a title.\n"
        reel_kit.generate_image_multi(api_key, POST_MODELS[model], no_text, refs + [product], raw, aspect_ratio=ratio)
        with Image.open(raw) as generated:
            image = draw_title(_fit(generated, size), title, subtitle)
        written_by = "codice"
    assert image is not None
    image = add_logo(draw_price_tag(image, format_price(price), reference))
    image.save(destination, "JPEG", quality=90, optimize=True)
    for leftover in (raw, check_path):
        leftover.unlink(missing_ok=True)
    return {"model": model, "model_id": POST_MODELS[model], "text_written_by": written_by, "checks": checks, "prompt": prompt}


# -- T5c: carosello ----------------------------------------------------------------------------------------------
CAROUSEL_THEMES = {
    "tre-modi": "3 modi di indossarlo: lo stesso pezzo in tre look diversi (giorno, sera, weekend)",
    "insieme": "Perché stanno bene insieme: il pezzo con altri pezzi del negozio che lo completano",
}


def carousel_plan_prompt(theme: str, analisi: str, styling: str, subtype: str) -> str:
    from main import BRAND, platform_rules

    return f"""Sei la social media manager di I Monili Ravenna. Prepara un carosello Instagram di 3 slide.
{BRAND}
TEMA: {CAROUSEL_THEMES.get(theme, CAROUSEL_THEMES["tre-modi"])}
ANALISI DEL PEZZO: {analisi[:1200]}
STYLING GIA PROPOSTO: {styling or "nessuno"}
TIPO DI PEZZO: {subtype or "da capire dall'analisi"}

REGOLE DI SCRITTURA:
{platform_rules(["stile-umano", "instagram"])}

Le 3 slide hanno la stessa luce, lo stesso fondo e la stessa donna: cambiano solo abbinamento e posa.
Rispondi SOLO con JSON:
{{"slides": [{{"titolo": "max 4 parole in italiano, es. Look da giorno", "prompt_en": "in inglese: abbinamento, posa e inquadratura della slide"}}],
 "scena_en": "in inglese, UNA scena comune alle 3 slide: luogo, fondo, luce, palette",
 "caption": "didascalia unica in italiano, tono da amica, max 2 emoji, chiude con: {CLOSING}"}}
Le slide sono esattamente 3."""


def carousel_slide_prompt(scene: str, slide_prompt: str, index: int, subtype: str, cut: str, model: str, woman_photos: int) -> str:
    import casting
    import prompt_lab

    return f"""USE: slide {index} of a 3-slide Instagram carousel (4:5) for I Monili Ravenna. Every slide shares the same scene.
{_refs_line(woman_photos)}SHARED SCENE (identical in all slides): {scene}
THIS SLIDE: {slide_prompt}
Preserve the exact product from the reference. Real photograph, authentic skin texture, warm natural light.
No text, no logos, no prices, no watermark (the shop adds them).
{casting.never_line()}

{prompt_lab.type_guide(subtype, cut)}
{prompt_lab.model_knowledge(model)}""".strip()


def slide_caption(image: Image.Image, index: int, total: int, title: str) -> Image.Image:
    """Same small serif caption and logo on every slide (consistency between slides is the code's job)."""
    out = image.convert("RGB").copy()
    draw = ImageDraw.Draw(out)
    italic = _font("GARAIT.TTF", int(out.width * 0.05))
    small = _font("GARA.TTF", int(out.width * 0.026))
    label = f"{index}/{total}"
    w = int(max(draw.textlength(title, font=italic), draw.textlength(label, font=small))) + 56
    h = int(italic.size * 1.3) + int(small.size * 1.3) + 30
    x = y = int(out.width * 0.05)
    return add_logo(_tag(out, (x, y, x + w, y + h), [(label, small, SOFT), (title, italic, INK)]))


# -- elenco dei post del pezzo -----------------------------------------------------------------------------------
def post_dir(output_dir: Path) -> Path:
    path = output_dir / POST_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_posts(output_dir: Path) -> list[dict]:
    try:
        data = json.loads((output_dir / POST_DIR / "posts.json").read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def add_post(output_dir: Path, entry: dict) -> dict:
    posts = list_posts(output_dir)
    entry = {"id": uuid.uuid4().hex[:8], "created_at": datetime.now().isoformat(timespec="seconds"), **entry}
    posts.insert(0, entry)
    path = post_dir(output_dir) / "posts.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
    return entry


def new_name(output_dir: Path, kind: str, index: int = 0) -> Path:
    stamp = datetime.now().strftime("%H%M%S")
    suffix = f"_{index}" if index else ""
    return post_dir(output_dir) / f"post_{kind}_{stamp}_{uuid.uuid4().hex[:4]}{suffix}.jpg"