"""Script bpy lanciato da AI Studio. Legge dati di regia, senza eseguire codice generato."""

import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


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


def camera_motion(camera, shot, center_x, width, height, has_photo, start, end):
    lens = shot["lens_mm"]
    camera.data.lens = lens
    camera.data.sensor_fit = "VERTICAL"
    camera.data.sensor_height = 24
    frame_height = {
        "look": max(height, width * 16 / 9) * 1.13,
        "medium": max(height * 0.78, width * 16 / 9 * 0.78),
        "detail": height * 0.51,
        "macro": height * 0.30,
    }[shot["scale"]]
    margin_x = max(0.0, (width - frame_height * 9 / 16) / 2)
    margin_z = max(0.0, (height - frame_height) / 2)
    focus_x = min(margin_x, max(-margin_x, (shot["focus_x"] - 0.5) * width))
    focus_z = min(margin_z, max(-margin_z, (0.5 - shot["focus_y"]) * height))
    target = (center_x + focus_x, 0, 1.04 + focus_z)
    distance = frame_height * lens / 24
    yaw_limit, pitch_limit = (8, 6) if has_photo else (45, 25)
    yaw = min(yaw_limit, max(-yaw_limit, shot["yaw_deg"]))
    pitch = math.radians(min(pitch_limit, max(-pitch_limit, shot["pitch_deg"])))

    motion = shot["motion"]
    for frame, phase in ((start, 0), (end, 1)):
        angle = math.radians(yaw + (phase * (3 if has_photo else 10) if motion == "orbit" else 0))
        radius = distance * (1 - 0.08 * phase) if motion == "push" else distance
        slide = frame_height * 0.12 * phase if motion == "slide" else 0
        horizontal = radius * math.cos(pitch)
        camera.location = (
            target[0] + math.sin(angle) * horizontal + slide,
            -math.cos(angle) * horizontal,
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
    images = [bpy.data.images.load(name, check_existing=True) for name in spec["photos"]]
    backdrop = material("Palette del set", SET_COLORS[spec["set_mood"]])
    proxy = material("Segnaposto", (0.10, 0.24, 0.30))
    photo_materials = [material(f"Foto {i + 1}", (1, 1, 1), image) for i, image in enumerate(images)]
    notes = bpy.data.texts.new("Regia e audio")
    notes.write(spec["notes"])
    start = 1
    marks = []
    for number, shot in enumerate(spec["shots"], 1):
        end = round(shot["end_ms"] * fps / 1000)
        x = (number - 1) * 18
        name = f"{number:02d} {shot['framing'][:54]}"
        surface(collections["Set"], f"Fondale {number}", [
            (x - 5, 1, -1), (x + 5, 1, -1), (x + 5, 1, 6), (x - 5, 1, 6),
        ], backdrop)
        surface(collections["Set"], f"Piano {number}", [
            (x - 5, -6, 0), (x + 5, -6, 0), (x + 5, 1, 0), (x - 5, 1, 0),
        ], backdrop)
        if images:
            index = min(shot["reference_photo"] - 1, len(images) - 1)
            image_width, image_height = images[index].size
            height = 1.56
            width = height * image_width / image_height
            half_width = width / 2
            surface(collections["Riferimenti"], f"Foto {index + 1} · shot {number}", [
                (x - half_width, 0, 0.26), (x + half_width, 0, 0.26),
                (x + half_width, 0, 1.82), (x - half_width, 0, 1.82),
            ], photo_materials[index])
        else:
            width, height = 0.68, 1.26
            bpy.ops.mesh.primitive_uv_sphere_add(location=(x, 0, 1.04))
            obj = bpy.context.object
            obj.name = f"Volume segnaposto {number}"
            obj.scale = (0.34, 0.23, 0.63)
            obj.data.materials.append(proxy)
            collections["Riferimenti"].objects.link(obj)
            for original in list(obj.users_collection):
                if original != collections["Riferimenti"]:
                    original.objects.unlink(obj)
        size, power, fill = LIGHTS[shot["light"]]
        side = {"left": -1, "front": 0, "right": 1}[shot["key_side"]]
        key_x = x + side * (2.3 if shot["light"] == "texture" else 1.9)
        light(collections["Luci"], f"Chiave {number} · {shot['light']}", (key_x, -2.2, 3.1),
              (x, 0, 1.04), power, size, (1, 0.93, 0.85))
        light(collections["Luci"], f"Riempimento {number}", (x - (side or -1) * 2, -1, 2.6),
              (x, 0, 1.04), fill, 3.5, (0.94, 0.96, 1))
        data = bpy.data.cameras.new(name)
        data.show_safe_areas = True
        camera = bpy.data.objects.new(name, data)
        collections["Camere"].objects.link(camera)
        camera_motion(camera, shot, x, width, height, bool(images), start, end)
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
                area.spaces.active.shading.color_type = "TEXTURE"
    bpy.ops.wm.save_as_mainfile(filepath=str(output))


if __name__ == "__main__":
    spec_path, output = map(Path, sys.argv[sys.argv.index("--") + 1:])
    build(json.loads(spec_path.read_text(encoding="utf-8")), output)
