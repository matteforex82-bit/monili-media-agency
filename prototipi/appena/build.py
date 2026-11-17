"""Builds appena.html: the seven ideas for Appena arrivati as one self-contained page."""
import base64
from pathlib import Path

here = Path(__file__).parent
html = (here / "appena.src.html").read_text(encoding="utf-8")
for key in ("ricamo", "camicia", "giacca", "camoscio", "spilla"):
    data = base64.b64encode((here / "img" / f"{key}.jpg").read_bytes()).decode()
    html = html.replace(f"__{key.upper()}__", f"data:image/jpeg;base64,{data}")
(here / "appena.html").write_text(html, encoding="utf-8")
print("appena.html", round(len(html) / 1024), "KB")
