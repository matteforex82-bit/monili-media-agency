"""Importazione dei vecchi reel nella Sala Reel: compressione, testi, niente doppioni. Senza rete."""
import importlib.util
import re
from pathlib import Path

import pytest

import reel_studio

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "importa_reel.py"


@pytest.fixture(scope="module")
def importer():
    spec = importlib.util.spec_from_file_location("importa_reel", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_video(path: Path, seconds: int = 2):
    reel_studio._run_ffmpeg([
        "-f", "lavfi", "-i", f"color=c=0x5a3c82:s=540x960:d={seconds}:r=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
    ])


def test_prova_compresses_without_sending(importer, tmp_path, monkeypatch):
    _fake_video(tmp_path / "anelli-ametista.mp4")
    sent = []
    monkeypatch.setattr(importer.server, "_send_reel_to_showcase", lambda *a: sent.append(a) or {"ok": True})
    done = importer.import_folder(tmp_path, dry_run=True)
    assert len(done["prepared"]) == 1 and not sent and not done["failed"]
    assert (tmp_path / "_web" / "anelli-ametista-reel.mp4").stat().st_size <= 4_000_000
    assert not (tmp_path / "_importati.json").exists()


def test_sends_draft_with_texts_and_skips_on_rerun(importer, tmp_path, monkeypatch):
    video = tmp_path / "Reel_Orecchini-Fiore.mp4"
    _fake_video(video)
    video.with_suffix(".txt").write_text("Orecchini a fiore\nSmaltati a mano, in via Cavour.", encoding="utf-8")
    sent = []
    monkeypatch.setattr(importer.server, "_send_reel_to_showcase", lambda meta, v, p: sent.append((meta, v, p)) or {"ok": True})
    first = importer.import_folder(tmp_path)
    assert len(first["sent"]) == 1
    meta, web_video, poster = sent[0]
    assert meta["title"] == "Orecchini a fiore" and meta["caption"] == "Smaltati a mano, in via Cavour."
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{2,79}", meta["id"]) and 1 <= meta["duration_sec"] <= 3
    assert web_video.suffix == ".mp4" and poster.suffix == ".jpg" and poster.stat().st_size <= 600_000
    assert "aiGenerated" not in meta  # senza il file .ia il reel è reale
    assert importer.REGISTRY_NAME in {p.name for p in tmp_path.iterdir()}
    second = importer.import_folder(tmp_path)
    assert second["skipped"] == [video.name] and not second["sent"] and len(sent) == 1


def test_failed_send_is_not_registered_and_is_retried(importer, tmp_path, monkeypatch):
    _fake_video(tmp_path / "borsa.mp4")
    monkeypatch.setattr(importer.server, "_send_reel_to_showcase", lambda *a: {"ok": False, "error": "sito spento"})
    done = importer.import_folder(tmp_path)
    assert done["failed"] and "sito spento" in done["failed"][0] and not done["sent"]
    assert not (tmp_path / "_importati.json").exists()
    monkeypatch.setattr(importer.server, "_send_reel_to_showcase", lambda *a: {"ok": True})
    assert len(importer.import_folder(tmp_path)["sent"]) == 1


def test_too_long_video_is_reported_and_others_continue(importer, tmp_path, monkeypatch):
    _fake_video(tmp_path / "a-lungo.mp4", seconds=2)
    _fake_video(tmp_path / "b-ok.mp4", seconds=2)
    real = reel_studio.probe_duration
    monkeypatch.setattr(reel_studio, "probe_duration", lambda p: 75.0 if "a-lungo" in str(p) else real(p))
    monkeypatch.setattr(importer.server, "_send_reel_to_showcase", lambda *a: {"ok": True})
    done = importer.import_folder(tmp_path)
    assert len(done["failed"]) == 1 and "troppo lungo" in done["failed"][0]
    assert len(done["sent"]) == 1


def test_title_from_filename_and_stable_unique_ids(importer, tmp_path):
    assert importer.read_texts(tmp_path / "anelli_citrino-estate.mp4") == ("Anelli citrino estate", "")
    assert importer.read_texts(tmp_path / "18012345.mp4")[0] == importer.DEFAULT_TITLE
    a, b = tmp_path / "x1.mp4", tmp_path / "x2.mp4"
    assert importer.reel_id_for(a) == importer.reel_id_for(a) != importer.reel_id_for(b)


def test_ia_marker_file_flags_the_reel_as_ai(importer, tmp_path, monkeypatch):
    video = tmp_path / "bomber-ricamato.mp4"
    _fake_video(video)
    video.with_suffix(".ia").write_text("", encoding="utf-8")
    sent = []
    monkeypatch.setattr(importer.server, "_send_reel_to_showcase", lambda meta, v, p: sent.append(meta) or {"ok": True})
    importer.import_folder(tmp_path)
    assert sent[0]["aiGenerated"] is True
