"""
importa_reel.py - porta nella Sala Reel del sito ("Guarda i Reel") i reel già pubblicati su Instagram.

Ogni video viene reso leggero per il web (720x1280, senza audio, sotto i 4 MB), riceve una copertina
e va al sito come BOZZA: la pubblichi tu, uno per uno, da /admin/reels sul sito.

Uso (dalla cartella del progetto):
    python scripts/importa_reel.py C:/percorso/cartella-reel            # comprime e invia al sito
    python scripts/importa_reel.py C:/percorso/cartella-reel --prova    # solo compressione, niente invio

Nella cartella metti i video (.mp4, .mov, .m4v). Accanto a un video, con lo stesso nome, puoi mettere:
    nome.jpg o nome.png   la copertina (altrimenti si prende un fotogramma del video)
    nome.txt              prima riga = titolo, il resto = didascalia

Si può rilanciare quando vuoi: i reel già inviati (registro `_importati.json` nella cartella) si saltano.
I file leggeri restano in `<cartella>/_web/`. Serve SHOWCASE_INGEST_URL (e il token) come per le schede.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_args = sys.argv[1:]
sys.argv = sys.argv[:1]  # main legge sys.argv all'import
import api.server as server  # noqa: E402
import reel_studio  # noqa: E402

VIDEO_SUFFIXES = {".mp4", ".mov", ".m4v"}
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png")
WEB_DIR_NAME = "_web"
REGISTRY_NAME = "_importati.json"
DEFAULT_TITLE = "Reel I Monili"


def find_videos(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_SUFFIXES)


def read_texts(video: Path) -> tuple[str, str]:
    """Titolo e didascalia: dal file `.txt` accanto al video, altrimenti dal nome del file."""
    sidecar = video.with_suffix(".txt")
    if sidecar.is_file():
        lines = sidecar.read_text(encoding="utf-8-sig").strip().splitlines()
        if lines and lines[0].strip():
            return lines[0].strip()[:120], "\n".join(lines[1:]).strip()[:600]
    words = re.sub(r"[_\-\s]+", " ", video.stem).strip()
    return (words.capitalize() if sum(c.isalpha() for c in words) >= 4 else DEFAULT_TITLE)[:120], ""


def reel_id_for(video: Path) -> str:
    """Id stabile per file: lo stesso video dà sempre lo stesso id (niente doppioni se si rilancia)."""
    digest = hashlib.sha1(video.stem.encode("utf-8")).hexdigest()[:6]
    slug = server._slugify(f"importato-{video.stem}")[:60].strip("-")
    return f"reel-{slug}-{digest}"


def poster_for(video: Path, web_dir: Path) -> Path:
    source = next((video.with_suffix(s) for s in IMAGE_SUFFIXES if video.with_suffix(s).is_file()), None)
    if source is None:
        source = web_dir / f"{video.stem}-frame.jpg"
        second = "1" if reel_studio.probe_duration(video) > 1.5 else "0"
        reel_studio._run_ffmpeg(["-ss", second, "-i", str(video), "-frames:v", "1", str(source)])
    return reel_studio.make_web_poster(source, web_dir / f"{video.stem}-poster.jpg")


def prepare(video: Path, web_dir: Path) -> tuple[dict, Path, Path]:
    web_dir.mkdir(parents=True, exist_ok=True)
    web_video = reel_studio.make_web_video(video, web_dir / f"{video.stem}-reel.mp4")
    poster = poster_for(video, web_dir)
    title, caption = read_texts(video)
    meta = {
        "id": reel_id_for(video),
        "title": title,
        "caption": caption,
        "duration_sec": reel_studio.probe_duration(web_video),
        "run_id": f"importato-{video.stem}"[:120],
    }
    return meta, web_video, poster


def load_registry(folder: Path) -> dict:
    path = folder / REGISTRY_NAME
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            pass
    return {}


def import_folder(folder: Path, dry_run: bool = False) -> dict[str, list[str]]:
    registry = load_registry(folder)
    done: dict[str, list[str]] = {"sent": [], "prepared": [], "skipped": [], "failed": []}
    for video in find_videos(folder):
        reel_id = reel_id_for(video)
        if reel_id in registry:
            done["skipped"].append(video.name)
            continue
        try:
            meta, web_video, poster = prepare(video, folder / WEB_DIR_NAME)
        except (RuntimeError, ValueError, OSError) as exc:
            done["failed"].append(f"{video.name}: {exc}")
            continue
        if dry_run:
            done["prepared"].append(f"{video.name} -> {web_video.stat().st_size / 1_000_000:.1f} MB")
            continue
        result = server._send_reel_to_showcase(meta, web_video, poster)
        if not result.get("ok"):
            done["failed"].append(f"{video.name}: {result.get('error') or 'invio non riuscito'}")
            continue
        registry[reel_id] = {"file": video.name, "sent_at": datetime.now().isoformat(timespec="seconds")}
        (folder / REGISTRY_NAME).write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
        done["sent"].append(f"{video.name} -> {meta['title']}")
    return done


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Porta i reel di Instagram nella Sala Reel del sito.")
    parser.add_argument("cartella", help="cartella con i video dei reel")
    parser.add_argument("--prova", action="store_true", help="comprime soltanto, non invia nulla al sito")
    args = parser.parse_args(argv)
    folder = Path(args.cartella)
    if not folder.is_dir():
        print(f"Cartella non trovata: {folder}")
        return 2
    if not args.prova and not server._reel_ingest_url():
        print("SHOWCASE_INGEST_URL non configurata: nel file .env va l'indirizzo del sito. Usa --prova per provare senza inviare.")
        return 2
    if not find_videos(folder):
        print("Nessun video (.mp4, .mov, .m4v) nella cartella.")
        return 1
    done = import_folder(folder, dry_run=args.prova)
    labels = {"sent": "Inviati come bozza", "prepared": "Pronti (non inviati)", "skipped": "Già inviati, saltati", "failed": "Non riusciti"}
    for key, label in labels.items():
        if done[key]:
            print(f"\n{label} ({len(done[key])}):")
            for line in done[key]:
                print(f"  - {line}")
    if done["sent"]:
        print("\nOra apri /admin/reels sul sito e pubblica quelli che vuoi mostrare.")
    return 1 if done["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main(_args))
