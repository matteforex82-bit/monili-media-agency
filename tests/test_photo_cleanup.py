"""Foto reale ripulita: scontorno simulato, niente modello e niente rete."""
import numpy as np
import pytest
from PIL import Image, ImageDraw

import photo_cleanup


def _photo_with_piece() -> tuple[Image.Image, np.ndarray]:
    """Fondo grigio con dominante blu e un "pezzo" rosso al centro, con la sua maschera."""
    img = Image.new("RGB", (900, 1200), (190, 195, 225))
    ImageDraw.Draw(img).rectangle((300, 400, 600, 800), fill=(180, 40, 40))
    alpha = np.zeros((1200, 900), dtype=np.float32)
    alpha[400:801, 300:601] = 1.0
    return img, alpha


def test_clean_photo_puts_the_real_piece_on_ivory(monkeypatch, tmp_path):
    img, alpha = _photo_with_piece()
    monkeypatch.setattr(photo_cleanup, "ensure_model", lambda path, notify=None: path)
    monkeypatch.setattr(photo_cleanup, "predict_alpha", lambda photo, path: alpha)
    out, issues = photo_cleanup.clean_photo(img, tmp_path / "model.onnx")
    assert issues == []
    assert out.size == photo_cleanup.CANVAS
    corner = out.getpixel((5, 5))
    assert corner[0] > 235 and corner[0] >= corner[1] >= corner[2]  # avorio caldo, niente grigio-blu
    r, g, b = out.getpixel((600, 700))
    assert r > 150 and r > g + 80 and r > b + 80  # il pezzo resta rosso


def test_check_cutout_rejects_bad_cutouts():
    alpha = np.zeros((100, 80), dtype=np.float32)
    assert "non ha trovato" in photo_cleanup.check_cutout(alpha)[0]
    assert "quasi tutta" in photo_cleanup.check_cutout(np.ones((100, 80), dtype=np.float32))[0]
    alpha[30:70, 20:60] = 1.0
    assert photo_cleanup.check_cutout(alpha) == []
    alpha[70:, 40:42] = 1.0  # un manico di scopa attaccato che arriva al bordo
    assert "bordo" in photo_cleanup.check_cutout(alpha)[0]


def test_white_balance_only_from_a_neutral_background():
    img, alpha = _photo_with_piece()
    gains = photo_cleanup.white_balance_gains(img, alpha)
    assert gains[0] > 1 > gains[2]  # toglie la dominante blu
    orange_wall = Image.new("RGB", (900, 1200), (210, 120, 50))
    assert photo_cleanup.white_balance_gains(orange_wall, alpha).tolist() == [1.0, 1.0, 1.0]


def test_model_is_not_downloaded_when_disabled(tmp_path):
    with pytest.raises(photo_cleanup.CleanupError):
        photo_cleanup.ensure_model(tmp_path / "models" / "x.onnx")


def test_corrupted_download_leaves_nothing_behind(monkeypatch, tmp_path):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size):
            yield b"non sono un modello"

    monkeypatch.setenv("CUTOUT_MODEL_AUTO_DOWNLOAD", "1")
    monkeypatch.setattr(photo_cleanup.requests, "get", lambda *a, **k: FakeResponse())
    target = tmp_path / "models" / "x.onnx"
    with pytest.raises(photo_cleanup.CleanupError):
        photo_cleanup.ensure_model(target)
    assert list(target.parent.iterdir()) == []
