"""Renders the nine material swatches of the home strip as small PNGs with a transparent background.

Not photographs: lit domes with a procedural texture (veins, banding, grain), made with numpy and PIL only.
Usage: python scripts/render_stones.py [output_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

OUT_SIZE = 128
SS = 3  # supersampling for a clean edge
N = OUT_SIZE * SS
RNG = np.random.default_rng(7)


def rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)


def noise(scale: int, seed: int) -> np.ndarray:
    """Smooth value noise in [0, 1], `scale` cells across."""
    r = np.random.default_rng(seed)
    base = (r.random((scale + 3, scale + 3)) * 255).astype(np.uint8)
    img = Image.fromarray(base).resize((N, N), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255


def fbm(seed: int, base: int = 4, octaves: int = 5) -> np.ndarray:
    total = np.zeros((N, N), dtype=np.float32)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        total += amp * noise(base * 2**o, seed + o * 17)
        norm += amp
        amp *= 0.5
    return total / norm


yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
X = (xx / (N - 1)) * 2 - 1
Y = (yy / (N - 1)) * 2 - 1
ANG = np.arctan2(Y, X)
R2 = R = INSIDE = H = HZ = NX = NY = NZ = None  # set by set_shape()

# the stones are rough hard stones, not discs: each one gets its own lumpy outline with a few flat chipped
# sides, and a bumpy surface. Materials that are not stones (silver, enamel, embroidery, leather) stay round.
ROUGH = {"ametista": 3, "quarzo": 8, "citrino": 5, "turchese": 12, "opale": 21}


def outline(seed: int) -> np.ndarray:
    """Radius of the silhouette (1 = the full frame) for every pixel angle."""
    r = np.random.default_rng(seed)
    harm = np.ones_like(ANG) * 0.90
    for k, amp in zip((2, 3, 4, 5, 7), (0.075, 0.06, 0.045, 0.03, 0.02)):
        harm += amp * np.cos(k * ANG + r.uniform(0, 2 * np.pi)) * r.uniform(0.6, 1.0)
    rho = harm
    for _ in range(int(r.integers(3, 6))):  # flat chipped faces
        phi = r.uniform(0, 2 * np.pi)
        d = r.uniform(0.70, 0.84)
        c = np.cos(ANG - phi)
        rho = np.minimum(rho, np.where(c > 0.05, d / np.maximum(c, 0.05), 9.0))
    return np.clip(rho, 0.55, 0.96)


def set_shape(seed=None):
    """(Re)compute the globals that describe the dome: silhouette mask, height and surface normals."""
    global R2, R, INSIDE, H, HZ, NX, NY, NZ
    if seed is None:
        rho = np.ones_like(ANG)
        bump = 0.0
    else:
        rho = outline(seed)
        bump = 0.5
    xs, ys = X / rho, Y / rho
    R2 = np.clip(xs * xs + ys * ys, 0, 4)
    R = np.sqrt(R2)
    INSIDE = np.clip((1.0 - R) * (N / 2) * rho / 1.2, 0, 1)  # soft anti-aliased edge
    H = np.sqrt(np.clip(1 - R2, 0, 1))  # dome height
    HZ = np.clip(H * 1.15, 0, 1) ** 0.85
    nx, ny, nz = xs, ys, np.maximum(H, 1e-3)
    if seed is not None:  # rough, lumpy surface
        step = 2 / (N - 1)
        lump = 0.75 * fbm(seed + 400, 3, 4) + 0.25 * fbm(seed + 500, 9, 3)
        gy, gx = np.gradient(lump, step)
        nx = nx - bump * 0.09 * gx
        ny = ny - bump * 0.09 * gy
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    NX, NY, NZ = nx / ln, ny / ln, nz / ln


set_shape(None)
L = np.array([-0.42, -0.58, 0.70], dtype=np.float32)
L /= np.linalg.norm(L)
V = np.array([0, 0, 1], dtype=np.float32)
Hh = (L + V) / np.linalg.norm(L + V)
NDL = NDH = FRES = BOUNCE = None


def update_lighting():
    global NDL, NDH, FRES, BOUNCE
    NDL = np.clip(NX * L[0] + NY * L[1] + NZ * L[2], 0, 1)
    NDH = np.clip(NX * Hh[0] + NY * Hh[1] + NZ * Hh[2], 0, 1)
    FRES = (1 - NZ) ** 2.2
    BOUNCE = np.clip(-(NX * -0.5 + NY * -0.7) * (1 - NZ), 0, 1)  # light from lower right


update_lighting()


def light(base, spec=0.7, shin=60, wrap=0.35, glow=None, glow_amt=0.0, rim=None, rim_amt=0.25, bounce=None, ambient=0.34):
    base = base.astype(np.float32)
    diff = np.clip((NDL + wrap) / (1 + wrap), 0, 1)
    col = base * (ambient + (1 - ambient) * diff[..., None])
    if glow is not None:
        depth = (HZ ** 1.6)[..., None]
        col = col * (1 - glow_amt * depth) + glow * (glow_amt * depth) * (0.55 + 0.45 * diff[..., None])
    if bounce is not None:
        col = col + bounce * (0.35 * BOUNCE)[..., None]
    if rim is not None:
        col = col + rim * (rim_amt * FRES)[..., None]
    s = (NDH**shin) * spec
    s2 = (NDH ** (shin * 0.18)) * spec * 0.12
    col = col + (s + s2)[..., None]
    # small secondary window reflection, lower right
    d = np.sqrt((X - 0.38) ** 2 + (Y - 0.42) ** 2)
    col = col + (np.clip(1 - d / 0.22, 0, 1) ** 2 * 0.18 * spec)[..., None]
    return np.clip(col, 0, 1)


def tone(c1, c2, t):
    return c1[None, None, :] * (1 - t[..., None]) + c2[None, None, :] * t[..., None]


def ridged(seed, base=3, octaves=4):
    n = fbm(seed, base, octaves)
    return 1 - np.abs(2 * n - 1)


# --- the long list of hard stones: each is a recipe (kind + colours), lit like the others ---------------
# kinds: clear (translucent gem), bands (agate-like banding), veined (mottled with veins/flecks), chat (cat's eye stripes)
NEW = {
    # translucent gems
    "quarzo-ialino": dict(kind="clear", dark="#aebcc6", lite="#f6fafc", glow="#ffffff", spec=0.95, haze=0.25),
    "quarzo-fume": dict(kind="clear", dark="#2c231c", lite="#9a8672", glow="#c9b49c", spec=0.9),
    "topazio": dict(kind="clear", dark="#2a7fb4", lite="#bfe8f8", glow="#e4f7ff", spec=0.95),
    "zaffiro": dict(kind="clear", dark="#0f2468", lite="#4f78e6", glow="#9db8ff", spec=1.0),
    "rubino": dict(kind="clear", dark="#6b0716", lite="#e8394f", glow="#ff9aa5", spec=1.0),
    "smeraldo": dict(kind="clear", dark="#07503a", lite="#3fc48c", glow="#a8f2cf", spec=0.9, haze=0.1),
    "peridoto": dict(kind="clear", dark="#6f8c0e", lite="#d6ee62", glow="#f2ffa8", spec=0.9),
    "acquamarina": dict(kind="clear", dark="#4aa9c0", lite="#d2f4f2", glow="#f0ffff", spec=0.9),
    "morganite": dict(kind="clear", dark="#e08c98", lite="#fcdcd2", glow="#fff1ec", spec=0.85),
    "granato": dict(kind="clear", dark="#4e0612", lite="#b8283a", glow="#e97585", spec=1.0),
    "tormalina": dict(kind="clear", dark="#1c5c4c", lite="#e0689a", glow="#ffb4d0", spec=0.9, twotone=True),
    "crisoberillo": dict(kind="clear", dark="#a9a52a", lite="#f2ee94", glow="#fffbc0", spec=0.9, haze=0.1),
    "corniola": dict(kind="clear", dark="#a8400c", lite="#f39a46", glow="#ffd09a", spec=0.85, band=0.22),
    "pietra-di-sole": dict(kind="clear", dark="#b9560f", lite="#f2a64c", glow="#ffd88a", spec=0.8, fleck="#fff0b8", fleck_thr=0.70),
    # banded stones
    "agata": dict(kind="bands", c1="#56688a", c2="#e6e8ee", c3="#b98a68", freq=11, warp=5, spec=0.55, shin=40),
    "onice": dict(kind="bands", c1="#100d0c", c2="#efe9de", c3="#3b332c", freq=8, warp=3, spec=0.8, shin=70, sharp=True),
    "rodocrosite": dict(kind="bands", c1="#c94a68", c2="#fbe4e6", c3="#e88aa0", freq=9, warp=7, spec=0.5, shin=36),
    "fluorite": dict(kind="bands", c1="#5a3a96", c2="#8fe0b8", c3="#b4a0e8", freq=8, warp=6, spec=0.85, shin=70),
    "malachite": dict(kind="bands", c1="#0b4a2c", c2="#5fd08a", c3="#1a7a48", freq=13, warp=4, spec=0.6, shin=44, concentric=True),
    # veined / mottled
    "diaspro": dict(kind="veined", c1="#8a2412", c2="#d28a3e", vein="#3a1a10", seed=104, spec=0.35, shin=24, vein_amt=0.35, mottle=True),
    "lapislazzuli": dict(kind="veined", c1="#10287a", c2="#2f55c8", vein="#e9e4d4", seed=111, spec=0.55, shin=40, vein_amt=0.4, fleck="#e8c25a", fleck_thr=0.74),
    "sodalite": dict(kind="veined", c1="#1b3a96", c2="#4d74d4", vein="#f0f0f4", seed=112, spec=0.5, shin=36, vein_amt=0.65),
    "giada": dict(kind="veined", c1="#3a8456", c2="#a6d6b0", vein="#e0f0e2", seed=113, spec=0.55, shin=36, vein_amt=0.15, cloud=True),
    "aventurina": dict(kind="veined", c1="#2f7c4c", c2="#86c898", vein="#2f7c4c", seed=114, spec=0.6, shin=42, vein_amt=0.0, fleck="#f2ffe8", fleck_thr=0.70),
    "crisoprasio": dict(kind="veined", c1="#4cbc72", c2="#bdf2c0", vein="#e8fbe8", seed=115, spec=0.6, shin=44, vein_amt=0.2, cloud=True),
    "calcedonio": dict(kind="veined", c1="#8fa8c2", c2="#e8f0f6", vein="#ffffff", seed=116, spec=0.6, shin=40, vein_amt=0.2, cloud=True),
    "rodonite": dict(kind="veined", c1="#cf6482", c2="#f0aebe", vein="#2a1a1e", seed=117, spec=0.4, shin=30, vein_amt=0.8),
    "ematite": dict(kind="metal", c1="#202228", c2="#a2a8b4"),
    "ossidiana": dict(kind="glass", c1="#050507", c2="#2c2c34"),
    "labradorite": dict(kind="labrador", c1="#272c38", c2="#586072"),
    "pietra-di-luna": dict(kind="moon", c1="#d6dde6", c2="#f6f8fb"),
    # cat's eyes
    "occhio-di-tigre": dict(kind="chat", c1="#4a2a0c", c2="#e0a23a", freq=16),
    "occhio-di-falco": dict(kind="chat", c1="#1f2638", c2="#7686a6", freq=16),
    "occhio-di-bue": dict(kind="chat", c1="#4a160c", c2="#b4502c", freq=16),
}
for _i, _n in enumerate(NEW):
    ROUGH[_n] = 30 + _i * 7


def paint_new(name: str):
    sp = NEW[name]
    kind, sd = sp["kind"], ROUGH[name]
    if kind == "clear":
        dark, lite, glow = rgb(sp["dark"]), rgb(sp["lite"]), rgb(sp["glow"])
        t = np.clip(HZ**1.4 + (fbm(sd, 3, 4) - 0.5) * 0.35, 0, 1)
        if sp.get("twotone"):
            t = np.clip(0.5 + 0.5 * np.tanh((X * 0.9 - Y * 0.4) * 3.0 + (fbm(sd + 1, 3, 3) - 0.5) * 1.2), 0, 1)
        base = tone(dark, lite, t)
        if sp.get("band"):
            base = base + (np.sin((X * 0.6 + Y * 0.8) * 14 + fbm(sd + 2, 3, 3) * 6) * 0.5 * sp["band"])[..., None] * 0.35
        if sp.get("haze"):
            base = base * (1 - sp["haze"]) + (fbm(sd + 3, 3, 4) ** 2)[..., None] * sp["haze"] * 1.4
        facet = (np.abs(np.sin((X * 0.9 - Y * 0.5) * 6 + fbm(sd + 4, 2, 3) * 2)) > 0.97).astype(np.float32) * 0.12
        base = base + facet[..., None]
        if sp.get("fleck"):
            fl = (fbm(sd + 5, 26, 1) > sp["fleck_thr"]).astype(np.float32)[..., None]
            base = base * (1 - fl * 0.8) + rgb(sp["fleck"])[None, None, :] * fl * 0.8
        return light(base, spec=sp["spec"], shin=90, glow=glow, glow_amt=0.5, rim=glow, rim_amt=0.3, bounce=dark, ambient=0.4)
    if kind == "bands":
        c1, c2, c3 = rgb(sp["c1"]), rgb(sp["c2"]), rgb(sp["c3"])
        w = fbm(sd, 3, 4)
        coord = (np.sqrt(X * X + Y * Y) if sp.get("concentric") else (X * 0.8 + Y * 0.6)) * sp["freq"] + w * sp["warp"]
        b = np.sin(coord) * 0.5 + 0.5
        if sp.get("sharp"):
            b = np.clip((b - 0.5) * 3.2 + 0.5, 0, 1)
        t = np.clip(b * 0.8 + fbm(sd + 2, 6, 3) * 0.2, 0, 1)
        base = tone(c1, c2, t)
        m3 = (0.35 * (np.sin(coord * 0.5 + 1.3) * 0.5 + 0.5))[..., None]
        base = base * (1 - m3) + c3[None, None, :] * m3
        return light(base, spec=sp["spec"], shin=sp["shin"], wrap=0.4, rim=c2, rim_amt=0.18, bounce=c1)
    if kind == "veined":
        c1, c2, vein = rgb(sp["c1"]), rgb(sp["c2"]), rgb(sp["vein"])
        sd = sp["seed"]
        t = fbm(sd, 4, 5)
        if sp.get("cloud"):
            t = np.clip(t * 0.7 + fbm(sd + 9, 2, 3) * 0.5, 0, 1)
        base = tone(c1, c2, t)
        if sp.get("mottle"):
            patch = (fbm(sd + 7, 5, 4) > 0.55).astype(np.float32)[..., None]
            base = base * (1 - patch * 0.45) + rgb("#3a1a10")[None, None, :] * patch * 0.45
        if sp["vein_amt"] > 0:
            veins = ridged(sd + 2, 3, 5)
            m = np.clip((veins - 0.86) / 0.10, 0, 1)[..., None] ** 1.3
            base = base * (1 - m * sp["vein_amt"]) + vein[None, None, :] * (m * sp["vein_amt"])
        if sp.get("fleck"):
            fl = (fbm(sd + 5, 26, 1) > sp["fleck_thr"]).astype(np.float32)[..., None]
            base = base * (1 - fl * 0.85) + rgb(sp["fleck"])[None, None, :] * fl * 0.85
        return light(base, spec=sp["spec"], shin=sp["shin"], wrap=0.4, rim=c2, rim_amt=0.18, bounce=c1)
    if kind == "metal":
        c1, c2 = rgb(sp["c1"]), rgb(sp["c2"])
        rx, ry = 2 * NZ * NX, 2 * NZ * NY
        env = 0.5 + 0.5 * np.sin(ry * 4.6 + 0.9) * np.cos(rx * 2.2)
        env = env * 0.6 + 0.4 * np.clip(1 - np.abs(ry + 0.4) * 2.0, 0, 1)
        v = np.clip((env - 0.5) * 1.6 + 0.5 + (HZ - 0.5) * 0.12, 0, 1)
        base = tone(c1, c2, v)
        return light(base, spec=0.95, shin=120, wrap=1.0, ambient=0.8, rim=c2, rim_amt=0.2)
    if kind == "glass":
        c1, c2 = rgb(sp["c1"]), rgb(sp["c2"])
        t = np.clip(HZ**1.3 * 0.7 + fbm(sd, 3, 4) * 0.3, 0, 1)
        base = tone(c1, c2, t)
        return light(base, spec=1.0, shin=130, wrap=0.3, glow=rgb("#4a4a58"), glow_amt=0.3, rim=rgb("#8a8aa0"), rim_amt=0.3, ambient=0.5)
    if kind == "labrador":
        c1, c2 = rgb(sp["c1"]), rgb(sp["c2"])
        base = tone(c1, c2, fbm(sd, 4, 5))
        patch = np.clip((fbm(sd + 1, 3, 4) - 0.42) * 3.0, 0, 1)
        hue = np.clip(fbm(sd + 2, 3, 3) * 1.6 - 0.2, 0, 1)
        flash = tone(rgb("#2f7ae8"), rgb("#f0c040"), hue)
        base = base * (1 - 0.7 * patch[..., None]) + flash * (0.9 * patch[..., None])
        return light(base, spec=0.8, shin=70, wrap=0.5, rim=rgb("#8fb0ff"), rim_amt=0.2, ambient=0.6)
    if kind == "moon":
        c1, c2 = rgb(sp["c1"]), rgb(sp["c2"])
        base = tone(c1, c2, fbm(sd, 3, 4))
        sheen = np.exp(-(((X + 0.25) ** 2 + (Y + 0.25) ** 2) / 0.12))
        base = base * (1 - 0.5 * sheen[..., None]) + rgb("#8fb4ff")[None, None, :] * (0.5 * sheen[..., None])
        return light(base, spec=0.8, shin=60, wrap=0.5, glow=rgb("#ffffff"), glow_amt=0.3, rim=rgb("#cfdcff"), rim_amt=0.3, ambient=0.6)
    if kind == "chat":
        c1, c2 = rgb(sp["c1"]), rgb(sp["c2"])
        warp = fbm(sd, 3, 4)
        st = np.sin((Y * 0.97 + X * 0.25) * sp["freq"] + warp * 5) * 0.5 + 0.5
        t = np.clip(st * 0.75 + fbm(sd + 2, 6, 3) * 0.25, 0, 1)
        base = tone(c1, c2, t)
        eye = np.exp(-(((X * 0.25 - Y * 0.97 + 0.1) / 0.14) ** 2)) * (0.4 + 0.6 * HZ)
        base = base + eye[..., None] * (c2[None, None, :] * 0.55 + 0.1)
        return light(base, spec=0.7, shin=50, wrap=0.45, rim=c2, rim_amt=0.2, bounce=c1)
    raise ValueError(name)


def render(name: str):
    set_shape(ROUGH.get(name))
    update_lighting()
    if name in NEW:
        rgba = np.dstack([paint_new(name), INSIDE])
        img = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8))
        return img.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    if name == "ametista":
        band = np.sin((X * 0.8 + Y * 0.6) * 9 + fbm(11, 3, 4) * 7)
        t = np.clip(0.5 + 0.5 * band, 0, 1) * 0.55 + fbm(12, 5, 4) * 0.45
        base = tone(rgb("#5a3478"), rgb("#a67fd0"), t)
        base = base * (0.78 + 0.22 * (HZ ** 1.2))[..., None]
        cloud = (fbm(13, 6, 4) > 0.64).astype(np.float32) * 0.22
        base = base + cloud[..., None] * 0.6
        col = light(base, spec=0.85, shin=70, glow=rgb("#c9a6ea"), glow_amt=0.4, rim=rgb("#d8c0f0"), rim_amt=0.35, bounce=rgb("#7e4aa0"))
    elif name == "quarzo":
        t = fbm(21, 4, 5)
        base = tone(rgb("#e8b3b0"), rgb("#f8dcd8"), np.clip(t * 1.2, 0, 1))
        milk = (fbm(22, 3, 4) ** 2)[..., None] * 0.22
        base = base + milk
        col = light(base, spec=0.6, shin=45, wrap=0.5, glow=rgb("#fbe6e2"), glow_amt=0.35, rim=rgb("#ffffff"), rim_amt=0.3, bounce=rgb("#f0a8a0"), ambient=0.5)
    elif name == "citrino":
        t = np.clip(HZ**1.4 + (fbm(31, 3, 4) - 0.5) * 0.35, 0, 1)
        base = tone(rgb("#b8780c"), rgb("#f6c93a"), t)
        facet = (np.abs(np.sin((X * 0.9 - Y * 0.5) * 6 + fbm(32, 2, 3) * 2)) > 0.97).astype(np.float32) * 0.12
        base = base + facet[..., None]
        col = light(base, spec=0.95, shin=90, glow=rgb("#ffe58a"), glow_amt=0.5, rim=rgb("#ffd966"), rim_amt=0.3, bounce=rgb("#e09a18"), ambient=0.4)
    elif name == "turchese":
        t = fbm(41, 4, 5)
        base = tone(rgb("#2c8f8b"), rgb("#58c3bb"), t)
        veins = ridged(42, 3, 5)
        mat = np.clip((veins - 0.86) / 0.10, 0, 1) ** 1.4
        base = base * (1 - mat[..., None] * 0.75) + rgb("#5a4632")[None, None, :] * (mat[..., None] * 0.75)
        fleck = (fbm(43, 14, 2) > 0.74).astype(np.float32) * 0.10
        base = base + fleck[..., None]
        col = light(base, spec=0.4, shin=30, wrap=0.4, rim=rgb("#9fe3dc"), rim_amt=0.18, bounce=rgb("#1d6f6c"))
    elif name == "opale":
        n1, n2 = fbm(51, 3, 4), fbm(52, 6, 3)
        hue = (n1 * 1.7 + n2 * 0.6 + X * 0.15) % 1.0
        # smooth rainbow without a colour library
        irid = np.stack([0.5 + 0.5 * np.cos(2 * np.pi * (hue + k)) for k in (0.0, 0.33, 0.66)], axis=-1).astype(np.float32)
        patch = np.clip((fbm(53, 4, 4) - 0.38) * 2.2, 0, 1)[..., None]
        milk = rgb("#eef1f0")[None, None, :]
        base = milk * (1 - 0.55 * patch) + (milk * 0.35 + irid * 0.65) * (0.55 * patch)
        col = light(base, spec=0.8, shin=70, wrap=0.5, glow=rgb("#ffffff"), glow_amt=0.25, rim=rgb("#cdd8ff"), rim_amt=0.3, bounce=rgb("#f3d4e8"), ambient=0.58)
    elif name == "argento":
        # brushed metal: reflect a simple studio environment
        rx, ry = 2 * NZ * NX, 2 * NZ * NY - 0 * NZ
        env = 0.5 + 0.5 * np.sin(ry * 5.2 + 0.8) * np.cos(rx * 2.4)
        env = env * 0.55 + 0.45 * np.clip(1 - np.abs(ry + 0.45) * 2.1, 0, 1)
        brushed = (noise(2, 61)[:, :] * 0.5 + fbm(62, 40, 1) * 0.5)
        brush = np.asarray(Image.fromarray((fbm(62, 60, 1) * 255).astype(np.uint8)).resize((N, 14), Image.BICUBIC).resize((N, N), Image.BICUBIC), dtype=np.float32) / 255
        v = np.clip((env - 0.5) * 1.7 + 0.5 + (brush - 0.5) * 0.14 + (HZ - 0.5) * 0.10, 0, 1)
        base = tone(rgb("#5d636b"), rgb("#fbfcfd"), v)
        col = light(base, spec=0.9, shin=110, wrap=1.0, ambient=0.85, rim=rgb("#ffffff"), rim_amt=0.25)
    elif name == "smalti":
        warp = fbm(71, 3, 4)
        sw = np.sin((X * 1.0 + Y * 0.4) * 6 + warp * 9) * 0.5 + 0.5
        t = np.clip(sw * 0.65 + fbm(72, 5, 3) * 0.35, 0, 1)
        base = tone(rgb("#8a3219"), rgb("#e0714f"), t)
        base = base * (0.82 + 0.18 * HZ)[..., None]
        col = light(base, spec=1.0, shin=140, glow=rgb("#f08a68"), glow_amt=0.25, rim=rgb("#ffb090"), rim_amt=0.22, bounce=rgb("#b84a2a"))
    elif name == "ricami":
        ang = np.arctan2(Y, X)
        rad = R
        # satin stitches: radial strokes in rings of varying direction
        ring = np.floor(rad * 5.5)
        local = ang * (8 + ring * 3) + fbm(81, 6, 2) * 2.2
        stitch = np.sin(local * 1.0) * 0.5 + 0.5
        thread = np.sin(((X * 0.6 + Y * 0.8) * 90) + fbm(82, 18, 2) * 5) * 0.5 + 0.5
        t = np.clip(stitch * 0.55 + thread * 0.25 + fbm(83, 5, 3) * 0.2, 0, 1)
        base = tone(rgb("#9b6420"), rgb("#efcb7e"), t)
        pad = (HZ ** 0.7)[..., None]
        base = base * (0.7 + 0.3 * pad)
        col = light(base, spec=0.55, shin=36, wrap=0.45, rim=rgb("#ffe6a8"), rim_amt=0.2, bounce=rgb("#b07a2e"))
    elif name == "cuoio":
        grain = fbm(91, 22, 2)
        pores = (fbm(92, 40, 1) > 0.66).astype(np.float32) * 0.10
        t = np.clip(0.45 + (fbm(93, 4, 4) - 0.5) * 0.8 + (grain - 0.5) * 0.25, 0, 1)
        base = tone(rgb("#8c5a30"), rgb("#c99560"), t) - pores[..., None]
        # stitched ring near the edge
        dash = (np.sin(np.arctan2(Y, X) * 38) > 0).astype(np.float32)
        ring = (np.abs(R - 0.80) < 0.022).astype(np.float32) * dash
        groove = (np.abs(R - 0.86) < 0.014).astype(np.float32) * 0.18
        base = base * (1 - ring[..., None] * 0.65) + rgb("#f1dcae")[None, None, :] * (ring[..., None] * 0.65)
        base = base - groove[..., None]
        col = light(base, spec=0.35, shin=22, wrap=0.45, rim=rgb("#e8c08a"), rim_amt=0.12, bounce=rgb("#7a4a24"))
    else:
        raise ValueError(name)
    rgba = np.dstack([col, INSIDE])
    img = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8))
    return img.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)


NAMES = ["argento", "ametista", "quarzo", "citrino", "turchese", "opale"] + list(NEW)
# smalti, ricami and cuoio are no longer in the strip: their recipes stay in render() but are not rendered

if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "stones_out"
    out.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        render(name).save(out / f"{name}.png", optimize=True)
        print(name, (out / f"{name}.png").stat().st_size // 1024, "KB")
    # contact sheet for a quick look
    cols = 10
    rows = -(-len(NAMES) // cols)
    sheet = Image.new("RGBA", (cols * (OUT_SIZE + 16) + 16, rows * (OUT_SIZE + 16) + 16), (246, 241, 230, 255))
    for i, name in enumerate(NAMES):
        im = Image.open(out / f"{name}.png")
        sheet.alpha_composite(im, (16 + (i % cols) * (OUT_SIZE + 16), 16 + (i // cols) * (OUT_SIZE + 16)))
    sheet.save(out / "_sheet.png")
