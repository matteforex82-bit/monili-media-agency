"""
optimize_image.py - I Monili Ravenna
Ridimensiona e ottimizza la foto originale per le piattaforme:
  - Instagram post: 1080x1350 (ratio 4:5)
  - Stories:        1080x1920 (ratio 9:16)
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

TARGET_JPEG_KB = int(os.environ.get("TARGET_JPEG_KB", "450"))


def polish(img: Image.Image) -> Image.Image:
    """Migliora leggermente contrasto, colore, luminosita e nitidezza."""
    out = img.convert("RGB")
    out = ImageEnhance.Contrast(out).enhance(1.08)
    out = ImageEnhance.Color(out).enhance(1.06)
    out = ImageEnhance.Brightness(out).enhance(1.03)
    out = ImageEnhance.Sharpness(out).enhance(1.08)
    return out


def save_jpeg_budget(img: Image.Image, output_path: Path, target_kb: int = TARGET_JPEG_KB) -> Path:
    """Salva JPG progressivo cercando di restare sotto il budget KB."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for quality in (88, 84, 80, 76, 72):
        img.save(output_path, "JPEG", quality=quality, optimize=True, progressive=True)
        if output_path.stat().st_size <= target_kb * 1024:
            return output_path
    return output_path


def make_feed(img: Image.Image, output_path: Path) -> Path:
    """Crea versione Instagram post 1080x1350 con sfondo neutro."""
    w, h = 1080, 1350
    img_copy = polish(img)
    img_copy.thumbnail((1010, 1240), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), (250, 247, 240))
    offset = ((w - img_copy.width) // 2, (h - img_copy.height) // 2)
    canvas.paste(img_copy, offset)
    return save_jpeg_budget(canvas, output_path)


def make_stories(img: Image.Image, output_path: Path) -> Path:
    """Crea versione 1080x1920 con sfondo blurrato e prodotto centrato."""
    w, h = 1080, 1920
    polished = polish(img)
    bg = ImageOps.fit(polished.copy(), (w, h), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=20))
    bg = bg.point(lambda p: int(p * 0.58))

    fg = polished.copy()
    fg.thumbnail((900, 1400), Image.LANCZOS)
    offset = ((w - fg.width) // 2, (h - fg.height) // 2)
    bg.paste(fg, offset)
    return save_jpeg_budget(bg, output_path)


def optimize(input_path: str, output_dir: str) -> dict:
    """Ottimizza l'immagine per Instagram post + stories."""
    src = Path(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    img = Image.open(src).convert("RGB")

    feed_path = out / "post_1080x1350.jpg"
    stories_path = out / "stories_1080x1920.jpg"

    make_feed(img, feed_path)
    make_stories(img, stories_path)

    print(f"Post 4:5: {feed_path}")
    print(f"Stories:  {stories_path}")

    return {"feed": str(feed_path), "stories": str(stories_path)}


def optimize_from_sources(feed_input_path: str, stories_input_path: str, output_dir: str) -> dict:
    """Crea post e stories partendo da sorgenti diverse."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    feed_img = Image.open(feed_input_path).convert("RGB")
    stories_img = Image.open(stories_input_path).convert("RGB")

    feed_path = out / "post_1080x1350.jpg"
    stories_path = out / "stories_1080x1920.jpg"

    make_feed(feed_img, feed_path)
    make_stories(stories_img, stories_path)

    print(f"Post 4:5: {feed_path}")
    print(f"Stories:  {stories_path}")

    return {"feed": str(feed_path), "stories": str(stories_path)}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python optimize_image.py <input_foto> <output_dir>")
        sys.exit(1)
    optimize(sys.argv[1], sys.argv[2])
