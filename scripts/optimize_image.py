"""
optimize_image.py — I Monili Ravenna
Ridimensiona e ottimizza la foto originale per Instagram:
  - Feed:    1080x1080 (ratio 1:1) con padding bianco
  - Stories: 1080x1920 (ratio 9:16) con sfondo blurrato
"""
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def polish(img: Image.Image) -> Image.Image:
    """
    Migliora lo scatto in modo leggero ma visibile:
    contrasto, colore, luminosita e nitidezza.
    """
    out = img.convert("RGB")
    out = ImageEnhance.Contrast(out).enhance(1.08)
    out = ImageEnhance.Color(out).enhance(1.06)
    out = ImageEnhance.Brightness(out).enhance(1.03)
    out = ImageEnhance.Sharpness(out).enhance(1.08)
    return out


def make_feed(img: Image.Image, output_path: Path) -> Path:
    """Crea versione 1080x1080 con padding bianco."""
    size = 1080
    img_copy = polish(img)
    img_copy.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    offset = ((size - img_copy.width) // 2, (size - img_copy.height) // 2)
    canvas.paste(img_copy, offset)
    canvas.save(output_path, "JPEG", quality=95, optimize=True)
    return output_path


def make_stories(img: Image.Image, output_path: Path) -> Path:
    """Crea versione 1080x1920 con sfondo blurrato e prodotto centrato."""
    w, h = 1080, 1920
    # Sfondo: immagine allargata e blurrata
    polished = polish(img)
    bg = polished.copy()
    bg = ImageOps.fit(bg, (w, h), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=20))
    bg = bg.point(lambda p: int(p * 0.58))  # scurisci leggermente

    # Prodotto: al centro, max 900x1400
    fg = polished.copy()
    fg.thumbnail((900, 1400), Image.LANCZOS)
    offset = ((w - fg.width) // 2, (h - fg.height) // 2)
    bg.paste(fg, offset)
    bg.save(output_path, "JPEG", quality=95, optimize=True)
    return output_path


def optimize(input_path: str, output_dir: str) -> dict:
    """
    Ottimizza l'immagine per Instagram.
    Ritorna dict con path feed e stories.
    """
    src = Path(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    img = Image.open(src).convert("RGB")

    feed_path = out / "feed_1080x1080.jpg"
    stories_path = out / "stories_1080x1920.jpg"

    make_feed(img, feed_path)
    make_stories(img, stories_path)

    print(f"✅ Feed:    {feed_path}")
    print(f"✅ Stories: {stories_path}")

    return {"feed": str(feed_path), "stories": str(stories_path)}


def optimize_from_sources(feed_input_path: str, stories_input_path: str, output_dir: str) -> dict:
    """
    Crea feed e stories partendo da sorgenti diverse.
    Utile quando l'AI genera una immagine specifica per il feed e una verticale per stories.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    feed_img = Image.open(feed_input_path).convert("RGB")
    stories_img = Image.open(stories_input_path).convert("RGB")

    feed_path = out / "feed_1080x1080.jpg"
    stories_path = out / "stories_1080x1920.jpg"

    make_feed(feed_img, feed_path)
    make_stories(stories_img, stories_path)

    print(f"Feed:    {feed_path}")
    print(f"Stories: {stories_path}")

    return {"feed": str(feed_path), "stories": str(stories_path)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python optimize_image.py <input_foto> <output_dir>")
        sys.exit(1)
    optimize(sys.argv[1], sys.argv[2])
