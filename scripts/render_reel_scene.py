"""Render della scena generata dallo Studio e mix della timeline audio."""

import json
from pathlib import Path
import sys

import bpy


def report_frame(scene):
    print(f"MONILI_FRAME {scene.frame_current - scene.frame_start + 1}", flush=True)


def render(directory):
    studio = bpy.data.scenes.get("Set e camere")
    montage = bpy.data.scenes.get("Montaggio e musica")
    if studio is None or montage is None:
        raise ValueError("Il file Blender deve contenere il set e la timeline musicale.")
    first, last = studio.frame_start, studio.frame_end
    fps = studio.render.fps / studio.render.fps_base
    markers = sorted((marker for marker in studio.timeline_markers if marker.camera), key=lambda marker: marker.frame)
    cuts = [marker for marker in markers if first <= marker.frame <= last]
    if not cuts or cuts[0].frame != first or len({marker.frame for marker in cuts}) != len(cuts):
        raise ValueError("Verifica i cambi camera sulla timeline Blender.")
    shots = [
        {
            "camera": marker.camera.name,
            "start_frame": marker.frame - first,
            "end_frame": (cuts[index + 1].frame if index + 1 < len(cuts) else last + 1) - first,
        }
        for index, marker in enumerate(cuts)
    ]
    if first > last or (last - first + 1) / fps > 60:
        raise ValueError("La timeline deve durare al massimo 60 secondi.")
    (directory / "timeline.json").write_text(
        json.dumps({"fps": fps, "frames": last - first + 1, "shots": shots}), encoding="utf-8",
    )
    print(f"MONILI_TOTAL {last - first + 1}", flush=True)

    montage.frame_start = first
    montage.frame_end = last
    montage.render.fps = studio.render.fps
    montage.render.fps_base = studio.render.fps_base
    bpy.context.window.scene = montage
    bpy.ops.sound.mixdown(filepath=str(directory / "musica.wav"), container="WAV", codec="PCM")

    bpy.context.window.scene = studio
    studio.frame_step = 1
    studio.render.use_sequencer = False
    studio.render.use_file_extension = True
    output = studio.render.image_settings
    if hasattr(output, "media_type"):
        output.media_type = "VIDEO"
    output.file_format = "FFMPEG"
    studio.render.ffmpeg.format = "MPEG4"
    studio.render.ffmpeg.codec = "H264"
    studio.render.ffmpeg.audio_codec = "NONE"
    studio.render.filepath = str(directory / "video-")
    bpy.app.handlers.render_post.append(report_frame)
    bpy.ops.render.render(animation=True, scene=studio.name)


if __name__ == "__main__":
    render(Path(sys.argv[sys.argv.index("--") + 1]))
