"""Set 3D stilizzati per il Reel Blender: ogni accessorio ha la sua scena (banco, scrigno, mano, busto, manichino).

Le forme sono blocchi semplici, come in un animatic: servono a guidare inquadratura, scala e gesto di Seedance,
non a riprodurre il pezzo. I colori e i dettagli veri arrivano dalla foto allegata a Seedance.
Gira dentro Blender (bpy), lanciato da build_reel_scene.py.
"""

import math

import bpy

# Scheda del prodotto -> (oggetto, parte del corpo che lo indossa)
STAGES = {
    "Anello": ("ring", "hand"),
    "Orecchini": ("earrings", "bust"),
    "Bracciale": ("bracelet", "wrist"),
    "Collana": ("necklace", "bust"),
    "Cavigliera": ("anklet", "ankle"),
    "Pochette": ("clutch", "hand"),
    "Sciarpa, stola o scialle": ("scarf", "bust"),
    "Foulard o bandana": ("foulard", "bust"),
    "Cappello": ("hat", "bust"),
    "Borsa": ("bag", "mannequin"),
    "Cintura": ("belt", "mannequin"),
    "Giacca o gilet": ("jacket", "mannequin"),
    "Capo singolo": ("garment", "mannequin"),
    "Outfit completo": ("outfit", "mannequin"),
    "Regia libera": ("free", "none"),
}
ACTIONS = ("rest", "reveal", "handle", "worn", "turn")
BOX_PRODUCTS = {"ring", "earrings", "bracelet", "necklace", "anklet"}  # gioielli piccoli: stanno in uno scrigno


def default_actions(kind, body, count):
    """Una sequenza sensata quando il regista non indica l'azione di scena."""
    if body == "mannequin":
        chain = ["rest", "turn", "worn", "turn", "worn", "turn"]
    elif body == "none":
        chain = ["rest", "turn", "rest", "turn", "rest", "turn"]
    elif kind in BOX_PRODUCTS:
        chain = ["reveal", "handle", "turn", "worn", "worn", "rest"]
    else:
        chain = ["rest", "handle", "worn", "turn", "worn", "rest"]
    if count <= 3:
        return [chain[0], chain[1], "worn"][:count]
    return chain[:count - 1] + ["worn"]


# ---------------------------------------------------------------- materiali
def make_materials(mood_color, hero_color):
    def mat(name, color, metal=0.0, rough=0.8):
        material = bpy.data.materials.new(name)
        material.diffuse_color = (*color, 1)
        material.use_nodes = True
        shader = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
        shader.inputs["Base Color"].default_value = (*color, 1)
        shader.inputs["Metallic"].default_value = metal
        shader.inputs["Roughness"].default_value = rough
        return material

    return {
        "wall": mat("Parete", mood_color),
        "wood": mat("Banco", (0.30, 0.17, 0.09), rough=0.55),
        "stone": mat("Pietra chiara", (0.78, 0.74, 0.68)),
        "velvet": mat("Velluto", (0.62, 0.45, 0.42)),
        "skin": mat("Pelle stilizzata", (0.80, 0.62, 0.52)),
        "body": mat("Manichino", (0.76, 0.75, 0.72)),
        "metal": mat("Metallo", (0.85, 0.85, 0.88), metal=0.9, rough=0.22),
        "hero": mat("Pezzo", hero_color, rough=0.45),
        "hero2": mat("Pezzo secondario", (0.18, 0.2, 0.26), rough=0.7),
        "gem": mat("Pietra", (0.45, 0.2, 0.62), rough=0.12),
    }


# ---------------------------------------------------------------- primitive
def _adopt(obj, col, parent, name, loc, rot, mat, smooth=True):
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    col.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    if mat is not None and hasattr(obj.data, "materials"):
        obj.data.materials.append(mat)
    if smooth and obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def empty(col, name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_size = 0.02
    col.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    return obj


def box(col, name, loc, size, mat, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.scale = size
    return _adopt(obj, col, parent, name, loc, rot, mat, smooth=False)


def cyl(col, name, loc, radius, height, mat, parent=None, rot=(0, 0, 0), top_radius=None):
    if top_radius is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, vertices=28)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=top_radius, depth=height, vertices=28)
    return _adopt(bpy.context.object, col, parent, name, loc, rot, mat)


def ball(col, name, loc, radius, mat, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=28, ring_count=14)
    obj = bpy.context.object
    obj.scale = scale
    return _adopt(obj, col, parent, name, loc, (0, 0, 0), mat)


def ring3d(col, name, loc, major, minor, mat, parent=None, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=48, minor_segments=14)
    obj = bpy.context.object
    obj.scale = scale
    return _adopt(obj, col, parent, name, loc, rot, mat)


def key(obj, frame, **values):
    for prop, value in values.items():
        setattr(obj, prop, value)
        obj.keyframe_insert(prop, frame=frame)


# ---------------------------------------------------------------- corpo
FINGERS = ((-0.027, 0.044, 0.032), (-0.009, 0.050, 0.035), (0.009, 0.047, 0.033), (0.027, 0.038, 0.028))


class Hand:
    """Mano destra vista da dietro: dita verso l'alto, dorso verso la camera. Origine nel centro del palmo."""

    def __init__(self, col, M, parent, name):
        self.root = empty(col, name, parent)
        ball(col, f"{name} palmo", (0, 0, 0.0), 1.0, M["skin"], self.root, (0.047, 0.016, 0.056))
        ball(col, f"{name} palmo b", (0, 0, 0.026), 1.0, M["skin"], self.root, (0.045, 0.014, 0.03))
        cyl(col, f"{name} avambraccio", (0, 0, -0.2), 0.034, 0.30, M["skin"], self.root, top_radius=0.029)
        self.bases, self.joints = [], []
        for i, (x, first, second) in enumerate(FINGERS):
            base = empty(col, f"{name} dito {i + 1}", self.root, (x, 0, 0.045))
            cyl(col, f"{name} falange {i + 1}a", (0, 0, first / 2), 0.0082, first, M["skin"], base)
            joint = empty(col, f"{name} snodo {i + 1}", base, (0, 0, first))
            cyl(col, f"{name} falange {i + 1}b", (0, 0, second / 2), 0.0078, second, M["skin"], joint)
            self.bases.append(base)
            self.joints.append(joint)
        thumb = empty(col, f"{name} pollice", self.root, (-0.034, 0.0, -0.03), (0, -0.75, 0))
        cyl(col, f"{name} pollice a", (0, 0, 0.02), 0.0095, 0.04, M["skin"], thumb)
        joint = empty(col, f"{name} snodo pollice", thumb, (0, 0, 0.04))
        cyl(col, f"{name} pollice b", (0, 0, 0.015), 0.0085, 0.03, M["skin"], joint)
        self.bases.append(thumb)
        self.joints.append(joint)
        self.thumb_rest = thumb.rotation_euler.y

    def pose(self, frame, curl, thumb=0.0):
        """curl 0 = dita distese, 1 = pugno chiuso. Il pollice si chiude verso l'indice."""
        for i, (base, joint) in enumerate(zip(self.bases, self.joints)):
            if i == len(self.bases) - 1:
                key(base, frame, rotation_euler=(0, self.thumb_rest + thumb * 0.6, 0))
                key(joint, frame, rotation_euler=(0, thumb * 0.5, 0))
            else:
                key(base, frame, rotation_euler=(-curl * 1.1, 0, 0))
                key(joint, frame, rotation_euler=(-curl * 1.3, 0, 0))


def build_bust(col, M, parent, name):
    """Busto con testa: origine alla base del collo. Guarda verso -Y."""
    root = empty(col, name, parent)
    cyl(col, f"{name} collo", (0, 0, 0.07), 0.05, 0.14, M["body"], root)
    ball(col, f"{name} testa", (0, 0, 0.255), 1.0, M["body"], root, (0.085, 0.10, 0.115))
    box(col, f"{name} naso", (0, -0.105, 0.24), (0.018, 0.03, 0.04), M["body"], root)
    for side in (-1, 1):
        ball(col, f"{name} orecchio", (side * 0.087, 0.0, 0.245), 1.0, M["body"], root, (0.012, 0.02, 0.03))
    box(col, f"{name} spalle", (0, 0, -0.015), (0.40, 0.15, 0.07), M["body"], root)
    box(col, f"{name} petto", (0, 0, -0.17), (0.32, 0.18, 0.30), M["body"], root)
    return root


def build_mannequin(col, M, parent, name):
    """Manichino a figura intera: origine ai piedi. Il busto (con testa) sta in cima, collo a z=1.42."""
    root = empty(col, name, parent)
    cyl(col, f"{name} base", (0, 0, 0.01), 0.26, 0.02, M["stone"], root)
    for side in (-1, 1):
        cyl(col, f"{name} gamba", (side * 0.085, 0, 0.42), 0.058, 0.80, M["body"], root, top_radius=0.07)
        cyl(col, f"{name} braccio", (side * 0.245, 0, 1.15), 0.04, 0.55, M["body"], root)
    cyl(col, f"{name} bacino", (0, 0, 0.93), 0.145, 0.26, M["body"], root, top_radius=0.13)
    bust = build_bust(col, M, root, f"{name} busto")
    bust.location = (0, 0, 1.42)
    return root, bust


# ---------------------------------------------------------------- prodotti
def build_product(col, M, parent, kind, count=1, pose="worn"):
    """Il pezzo: pose "worn" (origine nel punto di attacco) o "rest" (appoggiato/esposto sul banco). Restituisce (root, shape, rest_rot, rest_lift, size)."""
    root = empty(col, f"Pezzo · {kind}", parent)
    shape = empty(col, f"Forma · {kind}", root)
    metal, hero, gem = M["metal"], M["hero"], M["gem"]
    rest_rot, lift, size = (0, 0, 0), 0.0, 0.05
    if kind == "ring":
        R, r = 0.0105, 0.0016
        ring3d(col, "Fascia", (0, 0, 0), R, r, metal, shape, scale=(1, 1, 2.6))
        ball(col, "Pietra", (0, -R - 0.002, 0), 0.0065, gem, shape, (1, 0.8, 1))
        for side in (-1, 1):
            ball(col, "Pietra piccola", (side * 0.0075, -R, 0), 0.0028, metal, shape)
        rest_rot, lift, size = (math.radians(-90), 0, 0), R + r, 0.026
    elif kind == "earrings":
        size = 0.07
        if pose == "rest":
            # espositore a T: palo, barra e orecchini appesi
            cyl(col, "Palo espositore", (0, 0, -0.06), 0.0035, 0.12, M["wood"], shape)
            cyl(col, "Barra espositore", (0, 0, 0.0), 0.0035, 0.14, M["wood"], shape, rot=(0, math.radians(90), 0))
            cyl(col, "Base espositore", (0, 0, -0.121), 0.035, 0.004, M["wood"], shape)
            lift = 0.125
        for index in range(count if pose == "rest" else 1):
            dx = (index - 0.5) * 0.07 if pose == "rest" else 0.0
            earring = empty(col, f"Orecchino {index + 1}", shape, (dx, 0, -0.004 if pose == "rest" else 0))
            ball(col, "Chiusura", (0, 0, 0), 0.0045, metal, earring)
            cyl(col, "Gambo", (0, 0, -0.012), 0.0012, 0.022, metal, earring)
            ball(col, "Goccia", (0, 0, -0.034), 0.009, hero, earring, (0.8, 0.55, 1.8))
            ball(col, "Pietra", (0, -0.002, -0.021), 0.0055, gem, earring)
    elif kind in ("bracelet", "anklet"):
        R = 0.036 if kind == "bracelet" else 0.042
        ring3d(col, "Cerchio", (0, 0, 0), R, 0.0028, metal, shape, scale=(1, 1, 1.5))
        for i in range(9):
            angle = i * math.tau / 9
            ball(col, "Perla", (math.cos(angle) * R, math.sin(angle) * R, 0), 0.0058, hero if i % 2 else gem, shape)
        rest_rot, lift, size = (math.radians(-90), 0, 0), R + 0.004, R * 2.4
    elif kind == "necklace":
        links = 56
        if pose == "worn":  # giro del collo con goccia sul petto
            for i in range(links):
                a = i * math.tau / links
                front = (1 + math.cos(a)) / 2  # 1 davanti, 0 dietro
                ball(col, "Maglia", (math.sin(a) * 0.066, -0.066 - 0.028 * front, -0.125 * front + 0.012), 0.0034, metal, shape)
            ball(col, "Ciondolo", (0, -0.1, -0.128), 0.013, gem, shape, (0.85, 0.45, 1.2))
        else:  # catena arrotolata sul vassoio con il ciondolo davanti
            for i in range(links):
                a = i * math.tau / links
                ball(col, "Maglia", (math.cos(a) * 0.07, math.sin(a) * 0.045, 0.0), 0.0034, metal, shape)
            ball(col, "Ciondolo", (0, -0.075, 0.0), 0.013, gem, shape, (0.85, 0.9, 0.6))
            lift = 0.004
        size = 0.17
    elif kind == "clutch":
        box(col, "Pochette", (0, 0, 0), (0.24, 0.03, 0.14), hero, shape)
        box(col, "Patta", (0, -0.017, 0.035), (0.24, 0.006, 0.07), M["hero2"], shape)
        ball(col, "Chiusura", (0, -0.022, 0.0), 0.009, metal, shape)
        rest_rot, lift, size = (0, 0, 0), 0.07, 0.26
    elif kind in ("scarf", "foulard"):
        tail = 0.30 if kind == "scarf" else 0.17
        size = 0.30 if kind == "scarf" else 0.20
        if pose == "worn":
            ring3d(col, "Giro", (0, 0, 0), 0.062, 0.018, hero, shape, scale=(1, 1.1, 0.9))
            box(col, "Lembo", (0.02, -0.07, -tail / 2), (0.075 if kind == "scarf" else 0.1, 0.012, tail), hero, shape)
            box(col, "Lembo b", (-0.035, -0.066, -tail / 2 - 0.02), (0.07, 0.012, tail * 0.9), M["hero2"], shape, (0, 0, 0.12))
        elif kind == "scarf":  # piegata a strati
            for layer in range(4):
                box(col, "Piega", (0.004 * layer, 0.002 * layer, 0.006 + layer * 0.011), (0.22, 0.14, 0.011), hero if layer % 2 == 0 else M["hero2"], shape, (0, 0, math.radians(2 * layer)))
        else:  # quadrato steso e appena sollevato in un angolo
            box(col, "Telo", (0, 0, 0.004), (0.24, 0.24, 0.004), hero, shape, (0, 0, math.radians(18)))
            box(col, "Bordo", (0, 0, 0.0065), (0.18, 0.18, 0.003), M["hero2"], shape, (0, 0, math.radians(18)))
    elif kind == "hat":
        cyl(col, "Copa", (0, 0, 0.045), 0.085, 0.09, hero, shape)
        cyl(col, "Tesa", (0, 0, 0.003), 0.17, 0.006, hero, shape)
        cyl(col, "Nastro", (0, 0, 0.018), 0.0865, 0.018, M["hero2"], shape)
        rest_rot, lift, size = (0, 0, 0), 0.0, 0.2
    elif kind == "bag":
        box(col, "Corpo borsa", (0, 0, -0.11), (0.30, 0.10, 0.22), hero, shape)
        box(col, "Patta", (0, -0.052, -0.055), (0.30, 0.008, 0.10), M["hero2"], shape)
        ring3d(col, "Manico", (0, 0, 0.0), 0.08, 0.008, M["hero2"], shape, rot=(math.radians(90), 0, 0), scale=(1, 1, 1))
        ball(col, "Chiusura", (0, -0.058, -0.08), 0.012, metal, shape)
        rest_rot, lift, size = (0, 0, 0), 0.22, 0.34
    elif kind == "belt":
        ring3d(col, "Cintura", (0, 0, 0), 0.148, 0.009, hero, shape, scale=(1, 1, 2.6))
        box(col, "Fibbia", (0, -0.152, 0), (0.05, 0.012, 0.045), metal, shape)
        rest_rot, lift, size = (math.radians(90), 0, 0), 0.0, 0.30
    elif kind == "jacket":
        box(col, "Giacca corpo", (0, 0, -0.17), (0.40, 0.24, 0.58), hero, shape)
        for side in (-1, 1):
            cyl(col, "Manica", (side * 0.255, 0, -0.14), 0.062, 0.52, hero, shape)
            box(col, "Risvolto", (side * 0.07, -0.125, -0.02), (0.08, 0.012, 0.30), M["hero2"], shape, (0, 0, side * 0.22))
        size = 0.60
    elif kind == "garment":
        cyl(col, "Abito", (0, 0, -0.52), 0.30, 0.95, hero, shape, top_radius=0.16)
        box(col, "Corpetto", (0, 0, -0.12), (0.34, 0.2, 0.26), hero, shape)
        size = 0.70
    elif kind == "outfit":
        box(col, "Top", (0, 0, -0.14), (0.40, 0.24, 0.50), hero, shape)
        for side in (-1, 1):
            cyl(col, "Manica", (side * 0.25, 0, -0.14), 0.06, 0.50, hero, shape)
            cyl(col, "Pantalone", (side * 0.085, 0, -1.0), 0.10, 0.78, M["hero2"], shape, top_radius=0.085)
        size = 0.90
    else:  # regia libera: blocco astratto
        box(col, "Blocco", (0, 0, 0), (0.12, 0.12, 0.12), hero, shape, (0, 0, math.radians(20)))
        ball(col, "Sfera", (0.0, 0, 0.1), 0.05, gem, shape)
        rest_rot, lift, size = (0, 0, 0), 0.06, 0.2
    if pose == "rest" and kind in ("earrings", "necklace", "scarf", "foulard"):
        rest_rot = (0, 0, 0)
    return root, shape, rest_rot, lift, size


# anello e attacco del pezzo sul corpo (coordinate del corpo), con la rotazione della forma
def worn_anchor(kind, body):
    table = {
        ("ring", "hand"): ((0.010, 0.0, 0.0695), (0, 0, 0)),
        ("clutch", "hand"): ((0.0, -0.045, 0.02), (0, 0, 0)),
        ("bracelet", "wrist"): ((0.0, 0.0, -0.105), (0, 0, 0)),
        ("anklet", "ankle"): ((0.0, 0.0, 0.0), (0, 0, 0)),
        ("earrings", "bust"): ((0.0935, 0.0, 0.215), (0, 0, 0)),
        ("necklace", "bust"): ((0.0, 0.0, -0.005), (0, 0, 0)),
        ("scarf", "bust"): ((0.0, 0.0, 0.015), (0, 0, 0)),
        ("foulard", "bust"): ((0.0, 0.0, 0.015), (0, 0, 0)),
        ("hat", "bust"): ((0.0, 0.0, 0.335), (0, 0, 0)),
        ("bag", "mannequin"): ((0.26, -0.03, 1.32), (0, 0, 0)),
        ("belt", "mannequin"): ((0.0, 0.0, 0.97), (0, 0, 0)),
        ("jacket", "mannequin"): ((0.0, 0.0, 1.41), (0, 0, 0)),
        ("garment", "mannequin"): ((0.0, 0.0, 1.41), (0, 0, 0)),
        ("outfit", "mannequin"): ((0.0, 0.0, 1.41), (0, 0, 0)),
    }
    return table.get((kind, body), ((0, 0, 0), (0, 0, 0)))


# ---------------------------------------------------------------- set e scena
def build_set(col, M, x, small):
    """Banco del negozio con parete e qualche oggetto sfocato dietro, oppure pavimento per le figure intere."""
    if small:
        box(col, "Banco", (x, 0.05, -0.03), (1.6, 0.9, 0.06), M["wood"])
        box(col, "Parete", (x, 0.72, 0.5), (3.2, 0.04, 1.6), M["wall"])
        for i, (dx, h) in enumerate(((-0.45, 0.22), (-0.2, 0.34), (0.28, 0.27), (0.52, 0.19))):
            box(col, "Mensola oggetti", (x + dx, 0.62, h / 2), (0.09, 0.09, h), M["stone"] if i % 2 else M["hero2"])
    else:
        box(col, "Pavimento", (x, 0.3, -0.03), (4.0, 3.4, 0.06), M["wood"])
        box(col, "Parete", (x, 1.7, 1.4), (6.0, 0.04, 3.0), M["wall"])
        box(col, "Pannello", (x - 1.4, 1.66, 1.1), (0.7, 0.03, 2.0), M["stone"])


def build_stage(col, M, kind, body, action, x, start, end, hero_color_unused=None):
    """Costruisce la scena di una inquadratura. Restituisce {scale: (target, altezza di quadro)}."""
    small = body not in ("mannequin", "none")
    build_set(col, M, x, small)
    anchor = empty(col, f"Scena {x}", None, (x, 0, 0))
    product, shape, rest_rot, lift, size = build_product(
        col, M, anchor, kind, 2, "worn" if (action == "worn" or body == "mannequin") else "rest",
    )
    frames = max(1, end - start)

    def at(t):
        return start + round(frames * t)

    if body == "mannequin":
        figure, bust = build_mannequin(col, M, anchor, "Manichino")
        ax, rot = worn_anchor(kind, body)
        product.parent = figure
        product.location = ax
        shape.rotation_euler = rot
        if kind == "garment":
            product.location = (0, 0, 1.41)
        # il manichino ruota piano: mostra il pezzo da più lati
        spin = 0.9 if action in ("turn", "handle", "reveal") else 0.25
        key(figure, start, rotation_euler=(0, 0, math.radians(-spin * 35)))
        key(figure, end, rotation_euler=(0, 0, math.radians(spin * 35)))
        focus = {"look": ((x, 0, 0.9), 2.1), "medium": ((x + ax[0] * 0.5, 0, 1.2), 1.1),
                 "detail": ((x + ax[0], ax[1], ax[2]), max(0.45, size * 1.1)), "macro": ((x + ax[0], ax[1], ax[2]), max(0.24, size * 0.55))}
        return focus
    if body == "none":
        cyl(col, "Piedistallo", (x, 0, 0.06), 0.12, 0.12, M["stone"])
        product.parent = anchor
        product.location = (0, 0, 0.12 + lift)
        shape.rotation_euler = rest_rot
        key(product, start, rotation_euler=(0, 0, 0))
        key(product, end, rotation_euler=(0, 0, math.radians(90)))
        centre = (x, 0, 0.12 + lift)
        return {"look": ((x, 0, 0.22), 0.5), "medium": (centre, 0.32), "detail": (centre, 0.2), "macro": (centre, 0.12)}

    # ---- gioielli e accessori piccoli, sul banco
    wall_hand = Hand(col, M, anchor, "Mano")
    wall_hand.root.rotation_euler = (0, 0, 0)
    ground_z = 0.0
    held = action == "handle"
    worn = action == "worn"
    on_pedestal = action in ("turn", "rest") and kind not in ("clutch",)
    pad_z = 0.0
    if action == "reveal" and kind in BOX_PRODUCTS:
        box(col, "Scrigno", (x, 0, 0.022), (0.13, 0.095, 0.044), M["wood"])
        box(col, "Cuscino", (x, 0, 0.047), (0.11, 0.075, 0.016), M["velvet"])
        hinge = empty(col, "Cerniera scrigno", anchor, (0, 0.0475, 0.044))
        box(col, "Coperchio", (0, -0.0475, 0.008), (0.13, 0.095, 0.016), M["wood"], hinge)
        key(hinge, start, rotation_euler=(0, 0, 0))
        key(hinge, at(0.45), rotation_euler=(math.radians(-105), 0, 0))
        pad_z = 0.055
    elif on_pedestal or held:
        cyl(col, "Piedistallo", (x, 0, 0.035), 0.07, 0.07, M["stone"])
        box(col, "Cuscino", (x, 0, 0.0765), (0.09, 0.07, 0.013), M["velvet"])
        pad_z = 0.083
    else:
        box(col, "Vassoio", (x, 0, 0.007), (0.20, 0.15, 0.014), M["velvet"])
        pad_z = 0.014

    # posizione di riposo del pezzo (sul cuscino) e posizione indossata sul corpo
    rest_loc = (0, 0, pad_z + lift)
    ax, _rot = worn_anchor(kind, body)
    body_root = None
    body_focus = ((x, 0, 0.2), 0.5)
    if body == "hand":
        body_root = wall_hand.root
        body_root.location = (0.0, 0.0, 0.24)
    elif body == "wrist":
        body_root = wall_hand.root
        body_root.location = (0.0, 0.0, 0.24)
        body_root.rotation_euler = (0, 0, 0)
    elif body == "ankle":
        for part in list(wall_hand.root.children):
            bpy.data.objects.remove(part, do_unlink=True)
        bpy.data.objects.remove(wall_hand.root, do_unlink=True)
        wall_hand = None
        body_root = empty(col, "Caviglia", anchor, (0, 0, 0.2))
        cyl(col, "Gamba", (0, 0, 0.0), 0.036, 0.4, M["skin"], body_root, top_radius=0.03)
        box(col, "Piede", (0, -0.06, -0.19), (0.09, 0.22, 0.06), M["skin"], body_root)
    elif body == "bust":
        for part in list(wall_hand.root.children):
            bpy.data.objects.remove(part, do_unlink=True)
        bpy.data.objects.remove(wall_hand.root, do_unlink=True)
        wall_hand = None
        body_root = build_bust(col, M, anchor, "Busto")
        body_root.location = (0, 0.1, 0.335)
        if kind == "earrings":
            body_root.rotation_euler = (0, 0, math.radians(-68))
    if body in ("wrist", "hand", "ankle", "bust") and body_root is not None:
        world = (x + body_root.location[0], body_root.location[1], body_root.location[2])

    def body_point(local):
        """Punto del corpo in coordinate scena (senza ruotare la mano: usiamo la rotazione del busto)."""
        from mathutils import Vector
        return body_root.matrix_basis @ Vector(local)

    product.parent = anchor
    if held and wall_hand is not None:
        # la mano arriva dall'alto a destra, le dita scendono sul pezzo, lo prendono e lo sollevano verso la camera
        hand = wall_hand.root
        hold_z = pad_z + lift + 0.118
        hand.rotation_euler = (math.radians(180), 0, math.radians(-14))
        lift_move = (-0.025, -0.07, 0.15)
        key(hand, start, location=(0.26, -0.02, hold_z + 0.20))
        key(hand, at(0.40), location=(0.0, -0.012, hold_z + 0.06))
        key(hand, at(0.55), location=(0.0, -0.012, hold_z))
        key(hand, end, location=(lift_move[0], -0.012 + lift_move[1], hold_z + lift_move[2]))
        wall_hand.pose(start, 0.05)
        wall_hand.pose(at(0.40), 0.12)
        wall_hand.pose(at(0.55), 0.55, 0.8)
        wall_hand.pose(end, 0.55, 0.8)
        shape.rotation_euler = rest_rot
        product.location = rest_loc
        key(product, start, location=rest_loc)
        key(product, at(0.55), location=rest_loc)
        key(product, end, location=(rest_loc[0] + lift_move[0], rest_loc[1] + lift_move[1], rest_loc[2] + lift_move[2]))
        centre = (x, -0.04, pad_z + lift + 0.08)
        scale_h = {"look": 0.55, "medium": 0.36, "detail": 0.26, "macro": max(0.16, size * 5)}
        return {s: (centre, scale_h[s]) for s in scale_h}
    if wall_hand is not None and body in ("hand", "wrist"):
        wall_hand.pose(start, 0.12)
        wall_hand.pose(end, 0.12)
    if worn and body_root is not None:
        product.parent = body_root
        product.location = ax
        shape.rotation_euler = (0, 0, 0)
        if body == "hand":
            # la mano si muove appena: il pezzo brilla e cambia angolo
            key(body_root, start, rotation_euler=(0, 0, math.radians(-12)))
            key(body_root, end, rotation_euler=(0, 0, math.radians(14)))
        elif body == "wrist":
            key(body_root, start, rotation_euler=(0, math.radians(-8), math.radians(-10)))
            key(body_root, end, rotation_euler=(0, math.radians(8), math.radians(10)))
        elif body == "bust":
            if kind == "earrings":
                key(body_root, start, rotation_euler=(0, 0, math.radians(-78)))
                key(body_root, end, rotation_euler=(0, 0, math.radians(-58)))
            else:
                key(body_root, start, rotation_euler=(0, 0, math.radians(-14)))
                key(body_root, end, rotation_euler=(0, 0, math.radians(14)))
        point = body_point(ax)
        centre = (x + point[0], point[1], point[2] + body_root.location[2] if False else point[2])
        centre = (x + point[0], body_root.location[1] + point[1], point[2])
        if body in ("hand", "wrist"):
            centre = (x + ax[0] * 0.9, ax[1], body_root.location[2] + ax[2])
        extent = {"ring": 0.16, "clutch": 0.45, "bracelet": 0.3, "anklet": 0.4}.get(kind, 0.4)
        body_h = {"hand": 0.42, "wrist": 0.5, "ankle": 0.6, "bust": 0.75}[body]
        return {
            "look": ((x, body_root.location[1], body_root.location[2] + (0.0 if body in ("hand", "wrist", "ankle") else 0.12)), body_h),
            "medium": (centre, max(size * 3.2, body_h * 0.5)),
            "detail": (centre, max(size * 2.4, 0.07)),
            "macro": (centre, max(size * 1.35, 0.045)),
        }
    # rest / turn / reveal: il pezzo sta sul banco
    product.parent = anchor
    product.location = rest_loc
    shape.rotation_euler = rest_rot
    if action == "turn" or action == "rest":
        key(product, start, rotation_euler=(0, 0, 0))
        key(product, end, rotation_euler=(0, 0, math.radians(75 if action == "turn" else 18)))
    if body_root is not None:
        # il corpo è fuori campo (o sul fondo, sfocato) mentre il pezzo è in primo piano
        body_root.location = (0.34, 0.32, body_root.location[2])
        if wall_hand is not None:
            wall_hand.pose(start, 0.1)
    centre = (x, 0, rest_loc[2] + size * 0.15)
    return {
        "look": ((x, 0.1, 0.16), 0.55),
        "medium": (centre, max(size * 4.4, 0.18)),
        "detail": (centre, max(size * 2.8, 0.09)),
        "macro": (centre, max(size * 1.5, 0.05)),
    }
