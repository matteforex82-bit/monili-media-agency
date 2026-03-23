"""
optimize_image.py — I Monili Ravenna
Ridimensiona e ottimizza la foto originale per Instagram:
  - Feed:    1080x1080 (ratio 1:1) con padding bianco
  - Stories: 1080x1920 (ratio 9:16) con sfondo blurrato
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps


def make_feed(img: Image.Image, output_path: Path) -> Path:
    """Crea versione 1080x1080 con padding bianco."""
    size = 1080
    img_copy = img.copy()
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
    bg = img.copy()
    bg = ImageOps.fit(bg, (w, h), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=20))
    bg = bg.point(lambda p: int(p * 0.6))  # scurisci leggermente

    # Prodotto: al centro, max 900x1400
    fg = img.copy()
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


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python optimize_image.py <input_foto> <output_dir>")
        sys.exit(1)
    optimize(sys.argv[1], sys.argv[2])
