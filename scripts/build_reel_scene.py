"""Script bpy lanciato da AI Studio. Legge dati di regia, senza eseguire codice generato."""

import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_props  # noqa: E402  (set e oggetti 3D per tipo di accessorio)


def track(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def surface(collection, name, vertices, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.update()
    layer = mesh.uv_layers.new()
    for item, uv in zip(layer.data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        item.uv = uv
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)


def material(name, color, image=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = 0.85
    if image:
        texture = mat.node_tree.nodes.new("ShaderNodeTexImage")
        texture.image = image
        mat.node_tree.nodes.active = texture
        mat.node_tree.links.new(texture.outputs["Color"], shader.inputs["Emission Color"])
        shader.inputs["Emission Strength"].default_value = 1
        shader.inputs["Base Color"].default_value = (0, 0, 0, 1)
    return mat


def settings(scene, fps, last_frame):
    scene.frame_start = 1
    scene.frame_end = last_frame
    scene.render.fps = fps
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 50
    output = scene.render.image_settings
    if hasattr(output, "media_type"):
        output.media_type = "VIDEO"
    output.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.audio_codec = "AAC"
    scene.render.filepath = "//anteprima-reel.mp4"
    scene.view_settings.view_transform = "Standard"


def light(collection, name, position, target, power, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.size, data.color = power, size, color
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = position
    track(obj, target)


SET_COLORS = {
    "warm_cream": (0.65, 0.49, 0.34),
    "deep_charcoal": (0.07, 0.065, 0.06),
    "neutral": (0.47, 0.46, 0.44),
}

LIGHTS = {
    "soft": (3.6, 250, 150),
    "texture": (1.6, 330, 95),
    "jewelry": (4.2, 230, 150),
}


def stage_camera(camera, shot, target, frame_height, start, end):
    """Camera su un bersaglio 3D: frame_height è l'altezza (in metri) di ciò che deve entrare nel quadro."""
    lens = shot["lens_mm"]
    camera.data.lens = lens
    camera.data.sensor_fit = "VERTICAL"
    camera.data.sensor_height = 24
    camera.data.clip_start = 0.004
    camera.data.clip_end = 60
    distance = frame_height * lens / 24
    yaw = min(45, max(-45, shot["yaw_deg"]))
    pitch = math.radians(min(25, max(-25, shot["pitch_deg"])))
    motion = shot["motion"]
    camera.data.dof.use_dof = True
    camera.data.dof.focus_distance = distance
    camera.data.dof.aperture_fstop = 2.8 if shot["scale"] in ("macro", "detail") else 8
    for frame, phase in ((start, 0), (end, 1)):
        angle = math.radians(yaw + (phase * 16 if motion == "orbit" else 0))
        radius = distance * (1 - 0.12 * phase) if motion == "push" else distance
        slide = frame_height * 0.12 * phase if motion == "slide" else 0
        horizontal = radius * math.cos(pitch)
        camera.location = (
            target[0] + math.sin(angle) * horizontal + slide,
            target[1] - math.cos(angle) * horizontal,
            target[2] + math.sin(pitch) * radius,
        )
        track(camera, target)
        if motion != "fixed" and end > start:
            camera.keyframe_insert("location", frame=frame)
            camera.keyframe_insert("rotation_euler", frame=frame)


def build(spec, output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    studio = bpy.context.scene
    studio.name = "Set e camere"
    studio.world = bpy.data.worlds.new("Luce ambiente")
    studio.world.color = (0.22, 0.22, 0.22)
    fps = spec["fps"]
    last_frame = round(spec["shots"][-1]["end_ms"] * fps / 1000)
    settings(studio, fps, last_frame)
    studio.render.use_sequencer = False
    if hasattr(studio, "eevee"):
        studio.eevee.taa_render_samples = 8

    collections = {}
    for name in ("Set", "Riferimenti", "Luci", "Camere"):
        collections[name] = bpy.data.collections.new(name)
        studio.collection.children.link(collections[name])
    template = spec.get("template") or "Regia libera"
    kind, body = reel_props.STAGES.get(template, reel_props.STAGES["Regia libera"])
    M = reel_props.make_materials(SET_COLORS[spec["set_mood"]], tuple(spec.get("hero_color") or (0.72, 0.32, 0.22)))
    notes = bpy.data.texts.new("Regia e audio")
    notes.write(spec["notes"])
    defaults = reel_props.default_actions(kind, body, len(spec["shots"]))
    start = 1
    marks = []
    for number, shot in enumerate(spec["shots"], 1):
        end = round(shot["end_ms"] * fps / 1000)
        x = (number - 1) * 18
        name = f"{number:02d} {shot['framing'][:54]}"
        action = shot.get("stage_action")
        if action not in reel_props.ACTIONS:
            action = defaults[number - 1]
        focus = reel_props.build_stage(collections["Set"], M, kind, body, action, x, start, max(end, start + 1))
        target, frame_height = focus[shot["scale"]]
        size, power, fill = LIGHTS[shot["light"]]
        # banco: pezzi piccoli e vicini, serve meno luce; manichino: i bianchi si bruciano facilmente
        scale_light = 0.35 if body not in ("mannequin", "none") else 0.5
        power, fill = power * scale_light, fill * scale_light
        side = {"left": -1, "front": 0, "right": 1}[shot["key_side"]]
        key_x = x + side * (2.3 if shot["light"] == "texture" else 1.9)
        centre = focus["medium"][0]
        light(collections["Luci"], f"Chiave {number} · {shot['light']}", (key_x, -2.2, 3.1), centre, power, size, (1, 0.93, 0.85))
        light(collections["Luci"], f"Riempimento {number}", (x - (side or -1) * 2, -1, 2.6), centre, fill, 3.5, (0.94, 0.96, 1))
        data = bpy.data.cameras.new(name)
        data.show_safe_areas = True
        camera = bpy.data.objects.new(name, data)
        collections["Camere"].objects.link(camera)
        if body not in ("mannequin", "none") and not shot["pitch_deg"]:
            shot = {**shot, "pitch_deg": 12}  # banco: si guarda un po' dall'alto, come il banco di un negozio
        stage_camera(camera, shot, target, frame_height, start, end)
        marker = studio.timeline_markers.new(name, frame=start)
        marker.camera = camera
        marks.append((name, start))
        if number == 1:
            studio.camera = camera
        start = end + 1

    montage = bpy.data.scenes.new("Montaggio e musica")
    settings(montage, fps, last_frame)
    montage.render.use_sequencer = True
    editor = montage.sequence_editor_create()
    strips = editor.strips if hasattr(editor, "strips") else editor.sequences
    strips.new_scene("Riprese Blender", studio, channel=1, frame_start=1)
    audio = strips.new_sound(spec["audio_title"], spec["audio"], channel=2, frame_start=1)
    audio.volume = 0.8
    for name, frame in marks:
        montage.timeline_markers.new(name, frame=frame)
    for time, weight in spec["audio_accents"]:
        marker_name = "Accento principale" if weight == "strong" else "Accento leggero"
        montage.timeline_markers.new(marker_name, frame=round(time * fps / 1000) + 1)
    studio.frame_set(1)
    montage.frame_set(1)
    bpy.ops.file.pack_all()
    # Il formato .blend conserva foto e suono anche dopo la rimozione dei file temporanei.
    if not audio.sound.packed_file:
        raise RuntimeError("La traccia audio non è stata incorporata.")
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D" and area.spaces.active.region_3d:
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.shading.color_type = "MATERIAL"
    bpy.ops.wm.save_as_mainfile(filepath=str(output))


if __name__ == "__main__":
    spec_path, output = map(Path, sys.argv[sys.argv.index("--") + 1:])
    build(json.loads(spec_path.read_text(encoding="utf-8")), output)
