"""Test senza rete e senza chiavi: storage temporaneo e AI simulata."""
import os
import sys
import tempfile
from pathlib import Path

# Lo storage va impostato prima di importare i moduli dell'app (i percorsi si calcolano all'import).
_STORAGE = Path(tempfile.mkdtemp(prefix="monili-test-"))
os.environ["MONILI_STORAGE_DIR"] = str(_STORAGE)
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
for key in ("HF_API_KEY_ID", "HF_API_KEY_SECRET", "HIGGSFIELD_API_KEY", "OPENAI_API_KEY", "CUTOUT_MODEL_PATH"):
    os.environ.pop(key, None)
# Niente download del modello di scontorno (~1 GB) durante i test.
os.environ["CUTOUT_MODEL_AUTO_DOWNLOAD"] = "0"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.argv = sys.argv[:1]

import pytest  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402


@pytest.fixture(scope="session")
def storage_root() -> Path:
    return _STORAGE


@pytest.fixture()
def product_photo(tmp_path) -> Path:
    """Finto orecchino: cerchio argento con goccia blu su fondo verde."""
    path = tmp_path / "prodotto.jpg"
    img = Image.new("RGB", (900, 1200), (40, 110, 60))
    draw = ImageDraw.Draw(img)
    draw.ellipse((250, 350, 650, 750), outline=(220, 220, 225), width=30)
    draw.polygon([(450, 450), (520, 600), (450, 680), (380, 600)], fill=(20, 60, 200))
    img.save(path, "JPEG", quality=90)
    return path
