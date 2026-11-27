"""Prompt e file di produzione per il passaggio da Blender a Seedance."""

import json
from pathlib import Path
import re
import zipfile

import reel_studio
from reel_blender import format_time, product_title

SCALES = {
    "look": "an overall view that clearly shows the full product and its proportions",
    "medium": "a medium view showing how the product sits on the wearer or support",
    "detail": "a close view that shows the product feature and its surrounding construction",
    "macro": "a macro view of the documented detail with sharp, readable texture",
}
MOTIONS = {
    "fixed": "Keep the camera locked off",
    "push": "Use one restrained push-in toward the product",
    "slide": "Use one short, smooth lateral camera move",
    "orbit": "Use one subtle arc around the subject, within the approved angle",
}
LIGHTS = {
    "soft": "a large soft key with gentle fill",
    "texture": "a lateral key that reveals texture, with enough fill to retain the true color",
    "jewelry": "broad diffused light and restrained reflections",
}


def _reference(shot: dict, photo_count: int) -> int | None:
    return min((shot.get("design") or {}).get("reference_photo", 1), photo_count) if photo_count else None


def prompts(shots: list[dict], photo_count: int) -> list[dict]:
    result = []
    for index, shot in enumerate(shots, 1):
        design = shot.get("design") or {}
        frame = SCALES.get(design.get("scale"), "the opening composition of the Blender reference")
        light = LIGHTS.get(design.get("light"), "soft controlled studio lighting")
        motion = MOTIONS.get(design.get("motion"), "Follow the restrained movement of the Blender reference")
        side = {"left": "camera left", "right": "camera right", "front": "camera front"}.get(design.get("key_side"))
        if side:
            light += f", keyed from {side}"
        still = shot.get("photo_prompt_en") or f"Create one vertical 9:16 reference image with {frame}. Use {light}."
        video = shot.get("video_prompt_en") or f"{motion}. Hold the approved pose and preserve the opening and closing framing."
        result.append({
            "shot": index,
            "title": shot["framing"],
            "product_reference": _reference(shot, photo_count),
            "photo_en": (
                f"{still}\nUse the supplied real product photo as the source of truth. Match the opening pose "
                "and crop of the Blender reference. Preserve the exact color, shape, materials, details and scale. No lettering."
            ),
            "video_en": (
                f"{video}\nGenerate a single continuous vertical 9:16 shot. Use the prepared first image "
                "for the opening pose and the real product photos for product identity. Use the Blender video only "
                "for framing, movement and timing. Keep exact proportions, "
                "pattern, hardware and color. No cuts, added props, text, logos or generated music."
            ),
        })
    return result


def _timeline_shots(timeline: dict, count: int) -> list[tuple[int, dict]]:
    """Usa l'indice della camera se è stato riordinato il montaggio in Blender."""
    cuts = timeline["shots"]
    if len(cuts) != count:
        raise ValueError("Il render e il copione hanno un numero diverso di inquadrature. Controlla i marker in Blender.")
    indices = []
    for position, take in enumerate(cuts):
        match = re.match(r"^(\d+)\s", take["camera"])
        indices.append(int(match[1]) - 1 if match else position)
    if sorted(indices) != list(range(count)):
        raise ValueError("I marker di Blender non corrispondono alle camere del copione.")
    return list(zip(indices, cuts))


def assemble(directory: Path, output: Path, draft: dict, photos: list[Path]) -> dict:
    timeline = json.loads((directory / "timeline.json").read_text(encoding="utf-8"))
    shots = draft["package"]["shots"]
    takes = _timeline_shots(timeline, len(shots))
    video = next(directory.glob("video-*.mp4"), None)
    music = directory / "musica.wav"
    if not video or not music.is_file():
        raise ValueError("Blender non ha prodotto il video e la traccia della timeline.")
    master = output / "reel-blender.mp4"
    reel_studio._run_ffmpeg([
        "-i", str(video), "-i", str(music), "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-af", "apad", "-shortest", "-movflags", "+faststart", str(master),
    ])

    fps = timeline["fps"]
    all_prompts = prompts(shots, len(photos))
    entries = []
    with zipfile.ZipFile(output / "kit-seedance.zip", "w") as archive:
        archive.write(master, "reel-blender.mp4")
        archive.write(music, "musica-timeline.wav")
        photo_entries = []
        for photo_index, photo in enumerate(photos, 1):
            path = f"foto-prodotto/foto-{photo_index}{photo.suffix}"
            archive.write(photo, path)
            photo_entries.append(path)
        for shot_number, (script_index, take) in enumerate(takes, 1):
            folder = f"inquadrature/{shot_number:02d}"
            start, end = take["start_frame"], take["end_frame"]
            clip = directory / f"riferimento-{shot_number:02d}.mp4"
            reel_studio._run_ffmpeg([
                "-i", str(video), "-map", "0:v:0", "-an",
                "-vf", f"trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,format=yuv420p",
                *reel_studio.X264_ARGS, str(clip),
            ])
            still = directory / f"composizione-{shot_number:02d}.jpg"
            reel_studio._frame_at(clip, 0, still)
            archive.write(clip, f"{folder}/riferimento-blender.mp4")
            archive.write(still, f"{folder}/composizione.jpg")
            instructions = all_prompts[script_index]
            archive.writestr(f"{folder}/foto-en.txt", instructions["photo_en"])
            archive.writestr(f"{folder}/video-en.txt", instructions["video_en"])
            start_ms, end_ms = (round(frame * 1000 / fps) for frame in (start, end))
            photo = instructions["product_reference"]
            entries.append({
                "id": f"shot-{shot_number:02d}",
                "script_index": script_index,
                "title": instructions["title"],
                "start_frame": start,
                "end_frame_exclusive": end,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "video_reference": f"{folder}/riferimento-blender.mp4",
                "composition_image": f"{folder}/composizione.jpg",
                "product_reference": photo_entries[photo - 1] if photo else None,
                "photo_prompt": f"{folder}/foto-en.txt",
                "video_prompt": f"{folder}/video-en.txt",
                "source_image": None,
            })
        manifest = {
            "version": 1,
            "package_revision": draft.get("package_revision"),
            "workflow": "manual",
            "provider": "higgsfield",
            "model_family": "seedance",
            "fps": fps,
            "master": "reel-blender.mp4",
            "soundtrack": "musica-timeline.wav",
            "product_photos": photo_entries,
            "shots": entries,
        }
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        lines = [
            f"# Kit Seedance · {product_title(draft)}",
            "Il Reel Blender con la musica serve a controllare il montaggio. Le clip per Seedance sono mute.",
            "Per ogni ripresa, usa la foto reale e la composizione Blender con `foto-en.txt` per preparare l’immagine.",
            "In Higgsfield usa l’immagine preparata e, nella modalità che supporta video di riferimento, "
            "la clip Blender allegata con `video-en.txt`. Controlla gli ingressi e la durata minima del modello scelto. "
            "[Guida Seedance su Higgsfield](https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-seedance)",
            "Rifila la clip generata ai tempi sotto. La musica resta nella timeline di montaggio.",
        ]
        for number, shot in enumerate(entries, 1):
            lines.append(f"- {number:02d} · {shot['title']} · {format_time(shot['start_ms'])}–{format_time(shot['end_ms'])}")
        archive.writestr("LEGGIMI.md", "\n\n".join(lines) + "\n")
    return {"shots": len(entries), "duration_ms": round(timeline["frames"] * 1000 / fps),
            "review_available": bool(draft.get("package_revision"))}
