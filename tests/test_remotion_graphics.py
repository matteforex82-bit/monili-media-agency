from pathlib import Path

import pytest

import remotion_graphics as rg


def test_place_label_maps_the_shop_and_has_a_default():
    assert rg.place_label("via-cavour-21") == "Via Cavour 21, Ravenna"
    assert rg.place_label("") == rg.DEFAULT_PLACE
    assert rg.place_label("altro") == rg.DEFAULT_PLACE


def test_render_without_remotion_raises_so_the_caller_falls_back(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(rg, "is_available", lambda: False)
    with pytest.raises(RuntimeError):
        rg.render_graphics(tmp_path / "in.mp4", tmp_path / "out.mp4", 5)
