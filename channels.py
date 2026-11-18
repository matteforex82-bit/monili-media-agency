"""Photo formats per channel (knowledge/formati-canali.md): one approved photo, one file for each place it goes."""
from __future__ import annotations

from pathlib import Path

# id: (label, (width, height), mode for main.export_ratio_jpeg, target size in KB)
CHANNELS: dict[str, tuple[str, tuple[int, int], str, int]] = {
    "sito": ("Sito (4:5)", (1080, 1350), "extend", 700),
    "instagram-post": ("Instagram post (4:5)", (1080, 1350), "extend", 700),
    "instagram-storia": ("Instagram Storie (9:16)", (1080, 1920), "contain", 800),
    "google-foto": ("Google Business foto (1:1)", (1200, 1200), "extend", 900),
    "google-post": ("Google Business post (4:3)", (1200, 900), "contain", 800),
    "tripadvisor": ("Tripadvisor (3:2)", (1800, 1200), "contain", 1200),
}


def channel_list() -> list[dict]:
    return [{"id": key, "label": label, "width": size[0], "height": size[1]} for key, (label, size, _m, _k) in CHANNELS.items()]


def export_for_channel(source: Path, channel: str, destination: Path) -> Path:
    import main as studio_main

    label, size, mode, target_kb = CHANNELS[channel]
    return studio_main.export_ratio_jpeg(source, destination, size, mode=mode, target_kb=target_kb)
