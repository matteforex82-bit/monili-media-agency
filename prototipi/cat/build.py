"""Builds categorie.html: the four 'Sfoglia per tipo' variants as one self-contained page."""
import base64
from pathlib import Path

here = Path(__file__).parent
html = (here / "categorie.src.html").read_text(encoding="utf-8")
for key in ("bijoux", "abbigliamento", "accessori", "unici"):
    data = base64.b64encode((here / "img" / f"{key}.jpg").read_bytes()).decode()
    html = html.replace(f"__{key.upper()}__", f"data:image/jpeg;base64,{data}")
(here / "categorie.html").write_text(html, encoding="utf-8")
print("categorie.html", round(len(html) / 1024), "KB")
