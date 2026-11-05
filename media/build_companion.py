#!/usr/bin/env python3
"""
Audiovisual companion builder for «Хищные грибы Узбекистана».

Produces, under media/output (by default):
  companion.mp4   1280x720 H.264 + AAC, ~20 s
  soundtrack.wav  original atmospheric sound design, 48 kHz stereo 16-bit
  still_*.png     a few key frames for review
  trap_schematic.svg  static vector version of the three-cell ring (rest + inflated)

Usage:
  python3 media/build_companion.py artwork/predatory-fungi-uzbekistan.png
  python3 media/build_companion.py artwork/predatory-fungi-uzbekistan.png --preview
  python3 media/build_companion.py --image PATH --out media/output --duration 20 --fps 30

Only numpy, Pillow, the standard library and the ffmpeg binary are used.
If the illustration is missing, a procedural placeholder plate is used so the
pipeline can be developed and tested before the artwork is delivered.

Timeline (for the default 20 s; all times scale with --duration):
   0.0- 3.1  title card on indigo, faint hyphal lattice, three stacked title lines
   3.0-10.6  crossfade to the poster; very slow push-in (the poster's own title stays whole)
  10.6-17.2  poster softens and dims; code-drawn schematic: Drechslerella dactyloides
             three-cell ring, nematode enters, the three cells inflate INWARD
             (time-stylised); separate Arthrobotrys oligospora adhesive-net schematic
  16.8-20.0  closing card: creative line, credit lines, "artistic interpretation" caption
Audio: low drone + mineral overtones + soft capture accent at the inflation moment.
"""
import argparse
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)

# ----------------------------------------------------------------------------
# Palette (from research/brief.json art direction)
# ----------------------------------------------------------------------------
INDIGO = (18, 22, 52)
INDIGO_DEEP = (9, 11, 30)
LAPIS = (38, 60, 140)
TURQUOISE = (72, 178, 170)
CELADON = (168, 222, 200)
GOLD = (222, 178, 92)
HONEY = (236, 196, 110)
IVORY = (236, 230, 214)
TERRACOTTA = (186, 96, 62)

TITLE_LINES = ["ХИЩНЫЕ", "ГРИБЫ", "УЗБЕКИСТАНА"]
CAPTION_ART = "Художественная интерпретация"
CAPTION_SCALE = "Художественная интерпретация. Масштаб условный."
CREATIVE_LINE = "Под почвой начинается охота"
SOURCE_LINE_1 = "Название — Ф. Х. Файзиева, Ташкент, 1975"
SOURCE_LINE_2 = "Биология ловушек — современные исследования"
LABEL_RING_LAT = "Drechslerella dactyloides"
LABEL_RING_RU = "сжимающееся кольцо из трёх клеток"
LABEL_RING_RU2 = "клетки раздуваются внутрь за 0,1–1 с"
LABEL_NET_LAT = "Arthrobotrys oligospora"
LABEL_NET_RU = "клейкая трёхмерная сеть гиф"
LABEL_SCHEMA = "схема · время условно · не запись опыта"

FONT_CANDIDATES_REGULAR = [
    "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Regular.ttf",
    "/usr/share/fonts/truetype/ebgaramond/EBGaramond08-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]
FONT_CANDIDATES_ITALIC = [
    "/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Italic.ttf",
    "/usr/share/fonts/truetype/ebgaramond/EBGaramond08-Italic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
] + FONT_CANDIDATES_REGULAR


def find_font(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


_FONT_CACHE = {}


def font(size, italic=False):
    key = (size, italic)
    if key not in _FONT_CACHE:
        path = find_font(FONT_CANDIDATES_ITALIC if italic else FONT_CANDIDATES_REGULAR)
        if path is None:
            _FONT_CACHE[key] = ImageFont.load_default()
        else:
            _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


# ----------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def seg(t, a, b):
    """0 before a, 1 after b, linear between."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def smoother(x):
    x = clamp(x)
    return x * x * x * (x * (x * 6 - 15) + 10)


def lerp(a, b, k):
    return a + (b - a) * k


def with_alpha(rgb, a):
    return (rgb[0], rgb[1], rgb[2], int(clamp(a, 0, 255)))


def mix_rgb(a, b, k):
    """Opaque blend of two RGB colours (PIL's ImageDraw replaces pixels on RGBA layers,
    so translucent detail on top of a filled shape must be pre-blended)."""
    return tuple(int(round(lerp(a[i], b[i], k))) for i in range(3))


def scale_alpha(layer, k):
    """Multiply the alpha channel of an RGBA image by k in [0,1]."""
    if k >= 0.999:
        return layer
    if k <= 0.001:
        return None
    a = layer.getchannel("A").point(lambda v: int(v * k))
    out = layer.copy()
    out.putalpha(a)
    return out


def composite(base, layer, k=1.0):
    layer = scale_alpha(layer, k)
    if layer is None:
        return base
    return Image.alpha_composite(base, layer)


def text_size(draw, s, fnt):
    l, t, r, b = draw.textbbox((0, 0), s, font=fnt)
    return r - l, b - t


def draw_text(draw, xy, s, fnt, fill, anchor="la", spacing=0.0):
    """Draw text with optional letter-spacing (in px). anchor: 'la' left/top, 'ma' centre/top, 'ra' right."""
    if spacing <= 0:
        draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)
        return
    widths = [draw.textlength(ch, font=fnt) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for ch, w in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="la")
        x += w + spacing


# ----------------------------------------------------------------------------
# Placeholder plate when the illustration is not yet available
# ----------------------------------------------------------------------------
def placeholder_plate(w=1920, h=1080, seed=7):
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), INDIGO_DEEP)
    # vertical gradient: dusk ochre at the top, indigo below
    grad = np.zeros((h, w, 3), dtype=np.float32)
    ys = np.linspace(0, 1, h)[:, None]
    top = np.array([150, 96, 52], dtype=np.float32)
    mid = np.array(INDIGO, dtype=np.float32)
    bot = np.array(INDIGO_DEEP, dtype=np.float32)
    k1 = np.clip(ys / 0.12, 0, 1)
    k2 = np.clip((ys - 0.12) / 0.88, 0, 1)
    col = top * (1 - k1) + mid * k1
    col = col * (1 - k2) + bot * k2
    grad[:] = col[:, None, :]
    img = Image.fromarray(grad.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    # faint hyphal lattice
    for _ in range(140):
        x0, y0 = rng.uniform(0, w), rng.uniform(h * 0.15, h)
        for _ in range(rng.randint(2, 5)):
            ang = rng.uniform(-math.pi, math.pi)
            ln = rng.uniform(40, 220)
            x1, y1 = x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln
            d.line((x0, y0, x1, y1), fill=with_alpha(IVORY, rng.randint(14, 40)), width=rng.randint(1, 2))
            if rng.random() < 0.35:
                r = rng.uniform(8, 26)
                d.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), outline=with_alpha(CELADON, 40), width=1)
            x0, y0 = x1, y1
    # a note in the corner
    f = font(int(h * 0.028))
    d.text((w * 0.03, h * 0.94), "Основная иллюстрация ожидается (artwork/predatory-fungi-uzbekistan.png)",
           font=f, fill=with_alpha(IVORY, 110))
    return img


def load_poster(path, frame_w, frame_h, max_scale):
    """Load the illustration (or placeholder) and pre-size it so the maximum zoom still
    has >= 1 source px per output px. Returns an RGB image with 16:9-cover aspect."""
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGB")
        source = "illustration"
    else:
        print(f"[warn] illustration not found at {path!r}; using procedural placeholder", file=sys.stderr)
        img = placeholder_plate()
        source = "placeholder"
    # cover-fit to the frame aspect
    fa = frame_w / frame_h
    ia = img.width / img.height
    if ia > fa:
        nw = int(round(img.height * fa))
        x0 = (img.width - nw) // 2
        img = img.crop((x0, 0, x0 + nw, img.height))
    elif ia < fa:
        nh = int(round(img.width / fa))
        y0 = (img.height - nh) // 2
        img = img.crop((0, y0, img.width, y0 + nh))
    target_w = int(frame_w * max_scale * 1.15)
    if img.width > target_w:
        img = img.resize((target_w, int(round(target_w / fa))), Image.LANCZOS)
    return img, source


# ----------------------------------------------------------------------------
# Timeline
# ----------------------------------------------------------------------------
class Timeline:
    """All key times in seconds, defined for 20 s and scaled by duration/20."""

    def __init__(self, duration):
        s = duration / 20.0
        self.duration = duration
        self.title_in = (0.0, 1.6 * s)
        self.title_out = (2.3 * s, 3.1 * s)
        self.poster_in = (3.0 * s, 4.8 * s)
        self.schema_dim = (10.6 * s, 11.9 * s)
        self.schema_in = (11.0 * s, 12.2 * s)
        self.worm_start = 11.3 * s
        self.worm_capture = 13.8 * s          # inflation begins (audio accent here)
        self.inflate_dur = 1.0 * s            # stylised; real 0.1-1 s
        self.schema_out = (16.8 * s, 17.8 * s)
        self.closing_in = (17.2 * s, 18.4 * s)
        self.closing_out = (19.2 * s, 20.0 * s)
        self.cam_slow_end = 10.8 * s          # end of the gentle poster-only move
        self.poster_cam_end = 17.8 * s


# ----------------------------------------------------------------------------
# Scene: title / closing cards
# ----------------------------------------------------------------------------
def lattice_background(w, h, seed=3):
    """Dark indigo card with a faint code-drawn hyphal lattice and a touch of lapis glow."""
    rng = random.Random(seed)
    base = Image.new("RGBA", (w, h), with_alpha(INDIGO_DEEP, 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((w * 0.35, h * 0.3, w * 1.25, h * 1.4), fill=with_alpha(LAPIS, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(w * 0.12))
    base = Image.alpha_composite(base, glow)
    ss = 2
    lay = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(90):
        x0, y0 = rng.uniform(w * 0.3, w) * ss, rng.uniform(0, h) * ss
        for _ in range(rng.randint(2, 4)):
            ang = rng.uniform(-math.pi, math.pi)
            ln = rng.uniform(30, 150) * ss
            x1, y1 = x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln
            d.line((x0, y0, x1, y1), fill=with_alpha(IVORY, rng.randint(16, 42)), width=ss)
            if rng.random() < 0.4:
                r = rng.uniform(6, 22) * ss
                d.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), outline=with_alpha(CELADON, 46), width=ss)
            x0, y0 = x1, y1
    lay = lay.reduce(ss)
    return Image.alpha_composite(base, lay)


def title_layer(w, h, t, tl):
    k_in = smoother(seg(t, *tl.title_in))
    k_out = 1 - smooth(seg(t, *tl.title_out))
    k = k_in * k_out
    if k <= 0:
        return None
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    big = font(int(h * 0.135))
    x = w * 0.075
    y = h * 0.16
    for i, line in enumerate(TITLE_LINES):
        kk = smoother(seg(t, tl.title_in[0] + 0.25 * i, tl.title_in[1] + 0.25 * i)) * k_out
        if kk <= 0:
            continue
        col = IVORY if i < 2 else GOLD
        dy = (1 - kk) * h * 0.02
        draw_text(d, (x, y + dy), line, big, with_alpha(col, 255 * kk), spacing=h * 0.012)
        y += h * 0.15
    small = font(int(h * 0.034), italic=True)
    kk = smoother(seg(t, tl.title_in[1] + 0.3, tl.title_in[1] + 1.0)) * k_out
    if kk > 0:
        draw_text(d, (x + 4, y + h * 0.03), CAPTION_ART, small, with_alpha(IVORY, 170 * kk))
    return lay


def closing_layer(w, h, t, tl):
    k = smoother(seg(t, *tl.closing_in)) * (1 - smooth(seg(t, *tl.closing_out)))
    if k <= 0:
        return None, 0.0
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f1 = font(int(h * 0.075))
    f2 = font(int(h * 0.030))
    f3 = font(int(h * 0.028), italic=True)
    draw_text(d, (w / 2, h * 0.40), CREATIVE_LINE, f1, with_alpha(IVORY, 255), anchor="ma", spacing=h * 0.004)
    # thin gold rule
    d.line((w * 0.42, h * 0.52, w * 0.58, h * 0.52), fill=with_alpha(GOLD, 180), width=1)
    kk = smoother(seg(t, tl.closing_in[0] + 0.5, tl.closing_in[1] + 0.6))
    draw_text(d, (w / 2, h * 0.565), SOURCE_LINE_1, f2, with_alpha(IVORY, 190 * kk), anchor="ma")
    draw_text(d, (w / 2, h * 0.615), SOURCE_LINE_2, f2, with_alpha(IVORY, 190 * kk), anchor="ma")
    draw_text(d, (w / 2, h * 0.68), CAPTION_SCALE, f3, with_alpha(GOLD, 200 * kk), anchor="ma")
    return lay, k


# ----------------------------------------------------------------------------
# Scene: poster camera move
# ----------------------------------------------------------------------------
def poster_frame(poster, w, h, t, tl, max_scale):
    """Two-stage push-in. Stage 1 (poster alone) is a barely perceptible drift that keeps the
    poster's own title whole; stage 2 (under the dimmed schematic) pushes toward the ring."""
    u1 = smoother(seg(t, tl.poster_in[0], tl.cam_slow_end))
    u2 = smoother(seg(t, tl.cam_slow_end, tl.poster_cam_end))
    scale = lerp(lerp(1.0, 1.045, u1), max_scale, u2)
    cx = lerp(lerp(0.5, 0.50, u1), 0.56, u2)
    cy = lerp(lerp(0.5, 0.49, u1), 0.46, u2)
    # gentle breathing drift so the move never feels mechanical
    cx += 0.004 * math.sin(t * 0.37)
    cy += 0.003 * math.cos(t * 0.29)
    cw = poster.width / scale
    ch = poster.height / scale
    x0 = clamp(cx * poster.width - cw / 2, 0, poster.width - cw)
    y0 = clamp(cy * poster.height - ch / 2, 0, poster.height - ch)
    box = (x0, y0, x0 + cw, y0 + ch)
    return poster.resize((w, h), Image.LANCZOS, box=box)


def vignette(w, h):
    yy, xx = np.mgrid[0:h, 0:w]
    nx = (xx / w - 0.5) * 2
    ny = (yy / h - 0.5) * 2
    r = np.sqrt(nx * nx * 0.9 + ny * ny)
    v = 1 - 0.42 * np.clip((r - 0.55) / 0.8, 0, 1) ** 1.6
    v = (v * 255).astype(np.uint8)
    return Image.fromarray(v, "L").convert("RGB")


# ----------------------------------------------------------------------------
# Scene: schematic (three-cell constricting ring + adhesive net)
# ----------------------------------------------------------------------------
RING_TILT = 0.62      # minor/major axis ratio of the tilted disc
RING_ROT = math.pi / 2  # major axis vertical: the worm passes through left<->right
RING_IN_REST = 0.52   # inner radius / R at rest (plump cells)
RING_IN_SQUEEZE = 0.38  # how far the mid-cell bulges inward at full inflation (in R)


def ring_cells(cx, cy, R, inflation, tilt=RING_TILT, rot=RING_ROT, n_cells=3, gap_deg=2.5, steps=32):
    """Return polygons (outer/inner edge) for the three cells of a constricting ring.

    Each cell occupies 120 degrees. On inflation its inner edge bulges INWARD toward the
    aperture (strongest at mid-cell), closing the opening; the outer edge swells slightly.
    The ring is drawn as a tilted disc: y is compressed by `tilt`, then rotated by `rot`.
    """
    polys = []
    septa = []
    span = 2 * math.pi / n_cells
    gap = math.radians(gap_deg)

    def to_xy(r, ang):
        x = r * math.cos(ang)
        y = r * math.sin(ang) * tilt
        xr = x * math.cos(rot) - y * math.sin(rot)
        yr = x * math.sin(rot) + y * math.cos(rot)
        return (cx + xr, cy + yr)

    offset = math.radians(90)  # one septum at the top of the disc, stalk between two cells below
    nuclei = []
    for i in range(n_cells):
        a0 = offset + i * span + gap / 2
        a1 = offset + (i + 1) * span - gap / 2
        outer, inner = [], []
        for j in range(steps + 1):
            s = j / steps
            ang = lerp(a0, a1, s)
            bump = math.sin(math.pi * s) ** 0.8
            # a resting cell is already plump (sausage-shaped), inflation swells it inward
            r_out = R * (1.0 + 0.06 * inflation * bump + 0.03 * math.sin(math.pi * s))
            r_in = R * (RING_IN_REST - 0.10 * math.sin(math.pi * s) - RING_IN_SQUEEZE * inflation * bump)
            outer.append(to_xy(r_out, ang))
            inner.append(to_xy(r_in, ang))
        polys.append(outer + inner[::-1])
        # septum seams at the cell boundaries
        septa.append((to_xy(R * RING_IN_REST, a0), to_xy(R * 1.0, a0)))
        septa.append((to_xy(R * RING_IN_REST, a1), to_xy(R * 1.0, a1)))
        am = (a0 + a1) / 2
        nuclei.append(to_xy(R * (0.78 - 0.12 * inflation), am))
    stalk_base = to_xy(R * 1.0, math.radians(270))
    return polys, septa, stalk_base, to_xy, nuclei


def worm_points(head_u, length_u, path, n=70):
    """Sample the worm centreline from the tail to the head along `path(u)`."""
    pts = []
    for j in range(n):
        u = head_u - length_u + length_u * j / (n - 1)
        pts.append(path(u))
    return pts


def draw_worm(d, pts, radius, alpha=215, wobble=0.0, tphase=0.0, ss=1, pinch=None):
    """Smooth tapered legless roundworm: stacked discs with a tapered radius profile.
    `pinch(j)` optionally returns a radius multiplier for point j (constriction at the ring)."""
    n = len(pts)
    pts = list(pts)
    for j, (x, y) in enumerate(pts):
        s = j / (n - 1)                       # 0 tail .. 1 head
        if s < 0.85:
            taper = max(0.0, math.sin(math.pi * (0.08 + 0.92 * s))) ** 0.55
        else:
            taper = max(0.0, 1 - (s - 0.85) / 0.15) ** 0.5 * 0.92 + 0.08
        r = radius * (0.25 + 0.75 * taper)
        if pinch is not None:
            r *= pinch(j)
        if wobble:
            y += wobble * math.sin(tphase + s * 9.0) * (1 - s * 0.5)
            pts[j] = (x, y)
        d.ellipse((x - r, y - r, x + r, y + r), fill=with_alpha(HONEY, alpha))
    # faint gut line and a soft highlight (opaque, pre-blended with the body colour)
    d.line(pts[3:-3], fill=with_alpha(mix_rgb(HONEY, TERRACOTTA, 0.22), alpha), width=max(1, int(radius * 0.30)))
    hl = [(x - radius * 0.15, y - radius * 0.42) for (x, y) in pts[6:-5]]
    d.line(hl, fill=with_alpha(mix_rgb(HONEY, IVORY, 0.45), alpha), width=max(1, int(radius * 0.20)))


def adhesive_net(d, ox, oy, size, ss, seed=11, alpha=1.0):
    """Small separate schematic of an Arthrobotrys-type adhesive 3-D net: branching hyphae with
    anastomosing loops. Purely illustrative."""
    rng = random.Random(seed)
    col = with_alpha(IVORY, int(165 * alpha))
    col2 = with_alpha(CELADON, int(120 * alpha))
    # main hypha
    pts = [(ox, oy + size * 0.95)]
    x, y = pts[0]
    for i in range(6):
        x += size * rng.uniform(0.04, 0.12)
        y -= size * 0.15
        pts.append((x, y))
    d.line(pts, fill=col, width=max(1, int(2.2 * ss)))
    # loops hanging off the hypha, slightly 3-D (varying ellipse aspect)
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        for k in range(rng.randint(1, 2)):
            rx = size * rng.uniform(0.09, 0.16)
            ry = rx * rng.uniform(0.45, 0.95)
            dx = (1 if rng.random() < 0.5 else -1) * rx * 1.0
            dy = size * rng.uniform(-0.06, 0.06)
            box = (px + dx - rx, py + dy - ry, px + dx + rx, py + dy + ry)
            d.ellipse(box, outline=col, width=max(1, int(1.6 * ss)))
            # a second interlocking loop
            if rng.random() < 0.6:
                box2 = (px + dx * 1.3 - rx * 0.7, py + dy - ry * 1.3, px + dx * 1.3 + rx * 0.7, py + dy + ry * 0.4)
                d.ellipse(box2, outline=col2, width=max(1, int(1.4 * ss)))
            # adhesive droplets
            for _ in range(3):
                a = rng.uniform(0, 2 * math.pi)
                qx = px + dx + rx * math.cos(a)
                qy = py + dy + ry * math.sin(a)
                rr = 1.6 * ss
                d.ellipse((qx - rr, qy - rr, qx + rr, qy + rr), fill=with_alpha(TURQUOISE, int(170 * alpha)))


_GLOW_CACHE = {}


def ring_glow(W, H, cx, cy, R, k):
    """Soft turquoise halo behind the ring, computed once per size and alpha-scaled."""
    key = (W, H)
    if key not in _GLOW_CACHE:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.ellipse((cx - R * 1.3, cy - R * 1.5, cx + R * 1.3, cy + R * 1.5), fill=with_alpha(TURQUOISE, 120))
        _GLOW_CACHE[key] = g.filter(ImageFilter.GaussianBlur(R * 0.55))
    return scale_alpha(_GLOW_CACHE[key], k)


def schematic_layer(w, h, t, tl, ss=2):
    """RGBA overlay with the three-cell ring, nematode, hyphae, adhesive net and labels."""
    k_in = smoother(seg(t, *tl.schema_in))
    k_out = 1 - smooth(seg(t, *tl.schema_out))
    k = k_in * k_out
    if k <= 0:
        return None
    W, H = w * ss, h * ss
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    # --- geometry -----------------------------------------------------------
    cx, cy = W * 0.60, H * 0.50
    R = H * 0.20
    infl = smoother(seg(t, tl.worm_capture, tl.worm_capture + tl.inflate_dur))
    # tiny settle after inflation (cells are living, not rigid)
    if infl >= 0.999:
        infl = 1 - 0.02 * abs(math.sin((t - tl.worm_capture) * 5.0)) * math.exp(-(t - tl.worm_capture))

    # worm path: enters from the right, passes through the aperture, continues left in a soft S
    amp = H * 0.085
    L = W * 0.60
    u_ring = 0.46

    def path(u):
        # u in [0,1]: 0 = right edge (entry side), 1 = far left (exit side)
        x = cx + L * (u_ring - u)
        y = cy + amp * math.sin((u - u_ring) * 2 * math.pi * 1.05) + H * 0.05 * (u - u_ring)
        return (x, y)

    # worm progress: eased approach that arrives at exactly u_capture when inflation starts
    # (continuous, no jump), then held with a small creep and a decaying wriggle.
    worm_len = 0.40
    u_start = -0.05
    u_capture = u_ring + 0.17
    if t < tl.worm_capture:
        k = seg(t, tl.worm_start, tl.worm_capture)
        k = 1 - (1 - k) ** 1.6   # ease-out: the worm slows as it threads the ring
        u_head = lerp(u_start, u_capture, k)
    else:
        held = t - tl.worm_capture
        u_head = u_capture + 0.03 * (1 - math.exp(-held * 1.5))
    wobble = 0.0
    tphase = 0.0
    if t > tl.worm_capture + 0.3 * tl.inflate_dur:
        held = t - (tl.worm_capture + 0.3 * tl.inflate_dur)
        wobble = H * 0.010 * math.exp(-held * 0.5)
        tphase = held * 8.0

    worm_r = R * 0.19
    n_pts = 80
    pts = worm_points(u_head, worm_len, path, n=n_pts)

    def pinch(j):
        # constriction where the inflated cells grip the worm
        u = u_head - worm_len + worm_len * j / (n_pts - 1)
        g = math.exp(-((u - u_ring) / 0.045) ** 2)
        return 1 - 0.38 * infl * g

    # --- draw order: glow, hyphae/stalk, far half of ring, worm, near half of ring ---
    polys, septa, stalk_base, to_xy, nuclei = ring_cells(cx, cy, R, infl)
    lay = Image.alpha_composite(lay, ring_glow(W, H, cx, cy, R, 0.55 + 0.45 * infl))

    hy = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hy)
    # short stalk from the ring down to a supporting hypha that runs along the lower area
    sx, sy = stalk_base
    stalk_end = (sx - R * 0.10, sy + R * 0.62)
    hd.line((sx, sy, stalk_end[0], stalk_end[1]), fill=with_alpha(IVORY, 190), width=int(3.4 * ss))
    hcurve = []
    for i in range(-9, 8):
        x = stalk_end[0] + W * 0.05 * i
        y = stalk_end[1] + H * 0.012 * i + H * 0.018 * math.sin(i * 0.9)
        hcurve.append((x, y))
    hd.line(hcurve, fill=with_alpha(IVORY, 150), width=int(3.4 * ss))
    for i in (2, 5, 11, 14):
        x, y = hcurve[i]
        hd.line((x, y, x - W * 0.025, y - H * 0.06 * (1 + 0.3 * (i % 3))), fill=with_alpha(IVORY, 100), width=int(2 * ss))
    lay = Image.alpha_composite(lay, hy)

    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    fill_a = int(165 + 40 * infl)
    for poly in polys:
        rd.polygon(poly, fill=with_alpha(CELADON, fill_a))
    # a paler vacuole-like highlight gives each cell volume
    for (nx_, ny_) in nuclei:
        rr = R * (0.13 + 0.03 * infl)
        rd.ellipse((nx_ - rr * 0.8, ny_ - rr, nx_ + rr * 0.8, ny_ + rr), fill=with_alpha(mix_rgb(CELADON, (236, 250, 242), 0.6), fill_a))
    for poly in polys:
        rd.line(poly + [poly[0]], fill=with_alpha(IVORY, 210), width=max(1, int(1.8 * ss)))
    for (a, b) in septa:
        rd.line((a, b), fill=with_alpha(INDIGO, 190), width=max(1, int(1.8 * ss)))
    # split the ring: the half on the entry side (right) is behind the worm, the exit side in front
    ring_np = np.array(ring)
    xx = np.arange(W)[None, :]
    back_mask = np.broadcast_to(xx > cx, (H, W))
    back = ring_np.copy()
    back[..., 3] = np.where(back_mask, back[..., 3], 0)
    front = ring_np.copy()
    front[..., 3] = np.where(back_mask, 0, front[..., 3])
    lay = Image.alpha_composite(lay, Image.fromarray(back, "RGBA"))

    wl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wl)
    draw_worm(wd, pts, worm_r, wobble=wobble, tphase=tphase, ss=ss, pinch=pinch)
    lay = Image.alpha_composite(lay, wl)
    lay = Image.alpha_composite(lay, Image.fromarray(front, "RGBA"))

    # --- adhesive net schematic on the left, visually separate -----------------
    nl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nl)
    adhesive_net(nd, W * 0.08, H * 0.26, H * 0.46, ss)
    lay = Image.alpha_composite(lay, nl)

    # --- labels ----------------------------------------------------------------
    lay = lay.reduce(ss)
    d = ImageDraw.Draw(lay)
    f_lat = font(int(h * 0.040), italic=True)
    f_ru = font(int(h * 0.030))
    f_sm = font(int(h * 0.024), italic=True)
    gold = with_alpha(GOLD, 235)
    ivory = with_alpha(IVORY, 215)
    # ring label (right of the ring, upper right)
    lx, ly = w * 0.56, h * 0.10
    draw_text(d, (lx, ly), LABEL_RING_LAT, f_lat, gold)
    draw_text(d, (lx, ly + h * 0.055), LABEL_RING_RU, f_ru, ivory)
    k2 = smoother(seg(t, tl.worm_capture + 0.2, tl.worm_capture + 0.9))
    if k2 > 0:
        draw_text(d, (lx, ly + h * 0.095), LABEL_RING_RU2, f_ru, with_alpha(IVORY, 215 * k2))
    d.line((lx, ly + h * 0.052, lx + w * 0.30, ly + h * 0.052), fill=with_alpha(GOLD, 120), width=1)
    # net label (left)
    nx, ny = w * 0.05, h * 0.80
    draw_text(d, (nx, ny), LABEL_NET_LAT, f_lat, gold)
    draw_text(d, (nx, ny + h * 0.055), LABEL_NET_RU, f_ru, ivory)
    # schematic disclaimer
    draw_text(d, (w - w * 0.04, h * 0.93), LABEL_SCHEMA, f_sm, with_alpha(IVORY, 150), anchor="ra")
    return scale_alpha(lay, k)


# ----------------------------------------------------------------------------
# Static SVG of the ring (rest and inflated), from the same geometry
# ----------------------------------------------------------------------------
def write_svg(path):
    W, H = 1200, 640
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
             f'<rect width="{W}" height="{H}" fill="rgb{INDIGO_DEEP}"/>']
    for idx, (cx, infl, label) in enumerate([(330, 0.0, "покой"), (870, 1.0, "клетки раздуты внутрь")]):
        polys, septa, stalk_base, to_xy, nuclei = ring_cells(cx, 300, 150, infl)
        sx, sy = stalk_base
        parts.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{sx-20:.1f}" y2="{sy+110:.1f}" stroke="rgb{IVORY}" stroke-width="4" stroke-linecap="round"/>')
        for poly in polys:
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
            parts.append(f'<polygon points="{pts}" fill="rgba(168,222,200,0.75)" stroke="rgb{IVORY}" stroke-width="1.5"/>')
        for (a, b) in septa:
            parts.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="rgb{INDIGO}" stroke-width="1.5"/>')
        parts.append(f'<text x="{cx}" y="540" text-anchor="middle" font-family="EB Garamond, Georgia, serif" font-size="30" fill="rgb{IVORY}">{label}</text>')
    parts.append(f'<text x="{W/2}" y="70" text-anchor="middle" font-family="EB Garamond, Georgia, serif" font-style="italic" font-size="40" fill="rgb{GOLD}">{LABEL_RING_LAT}</text>')
    parts.append(f'<text x="{W/2}" y="108" text-anchor="middle" font-family="EB Garamond, Georgia, serif" font-size="26" fill="rgb{IVORY}">{LABEL_RING_RU} · {LABEL_SCHEMA}</text>')
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


# ----------------------------------------------------------------------------
# Sound design (numpy only)
# ----------------------------------------------------------------------------
def make_soundtrack(duration, sr, t_capture, seed=5):
    rng = np.random.default_rng(seed)
    n = int(duration * sr)
    t = np.arange(n) / sr
    L = np.zeros(n)
    Rr = np.zeros(n)

    def add(sig_l, sig_r=None):
        nonlocal L, Rr
        L += sig_l
        Rr += sig_l if sig_r is None else sig_r

    # 1. slow low drone: A1 + E2, two slightly detuned oscillators each, few harmonics
    def drone(f0, amp, detune, harm_n=6, lfo_rate=0.07, lfo_phase=0.0, pan=0.0):
        s = np.zeros(n)
        for h in range(1, harm_n + 1):
            a = amp / (h ** 1.6)
            s += a * np.sin(2 * np.pi * f0 * h * t)
            s += a * np.sin(2 * np.pi * (f0 + detune) * h * t + 0.7 * h)
        lfo = 0.78 + 0.22 * np.sin(2 * np.pi * lfo_rate * t + lfo_phase)
        s *= lfo
        add(s * (1 - 0.5 * pan), s * (1 + 0.5 * pan))

    drone(55.0, 0.16, 0.25, pan=-0.3)
    drone(82.41, 0.075, -0.18, harm_n=5, lfo_rate=0.05, lfo_phase=1.9, pan=0.3)
    drone(27.5, 0.07, 0.1, harm_n=2, lfo_rate=0.04)
    # after the capture a minor third (C2) fades in: the tension quietly resolves
    c2 = np.sin(2 * np.pi * 65.41 * t) * 0.05 + np.sin(2 * np.pi * 130.81 * t) * 0.02
    env_c2 = np.clip((t - t_capture) / 2.5, 0, 1) ** 1.5
    add(c2 * env_c2)

    # 2. mineral overtones: sparse struck inharmonic partials (bell / ceramic), high and quiet
    ratios = [1.0, 2.76, 5.40, 8.93]
    bases = [392.0, 523.25, 587.33, 783.99, 880.0, 1174.66]
    n_hits = 16
    hit_times = np.sort(rng.uniform(1.2, duration - 2.5, n_hits))
    for ht in hit_times:
        f0 = bases[rng.integers(len(bases))] * (1 + rng.normal(0, 0.004))
        dec = rng.uniform(1.4, 3.8)
        amp = rng.uniform(0.012, 0.03)
        pan = rng.uniform(-0.8, 0.8)
        i0 = int(ht * sr)
        seg_len = min(n - i0, int(dec * 3 * sr))
        tt = np.arange(seg_len) / sr
        env = np.exp(-tt / dec) * (1 - np.exp(-tt / 0.012))
        s = np.zeros(seg_len)
        for k, r in enumerate(ratios):
            s += (amp / (k + 1) ** 1.2) * np.sin(2 * np.pi * f0 * r * tt + rng.uniform(0, 6.28)) * np.exp(-tt * k * 0.5)
        s *= env
        L[i0:i0 + seg_len] += s * (1 - 0.5 * pan)
        Rr[i0:i0 + seg_len] += s * (1 + 0.5 * pan)

    # 3. subterranean breath: band-passed noise (FFT), slow amplitude swell, decorrelated L/R
    def band_noise(lo, hi, amp, lfo_rate, lfo_phase):
        x = rng.normal(0, 1, n)
        X = np.fft.rfft(x)
        f = np.fft.rfftfreq(n, 1 / sr)
        win = np.exp(-0.5 * ((np.log(np.maximum(f, 1)) - np.log(math.sqrt(lo * hi))) / (0.5 * math.log(hi / lo))) ** 2)
        y = np.fft.irfft(X * win, n)
        y /= (np.max(np.abs(y)) + 1e-9)
        lfo = 0.55 + 0.45 * np.sin(2 * np.pi * lfo_rate * t + lfo_phase)
        return amp * y * lfo

    L += band_noise(140, 700, 0.045, 0.06, 0.0)
    Rr += band_noise(140, 700, 0.045, 0.06, 2.1)

    # 4. capture accent: soft low thump with a pitch drop + brief rising shimmer, not startling
    i0 = int(t_capture * sr)
    seg_len = min(n - i0, int(2.2 * sr))
    tt = np.arange(seg_len) / sr
    fdrop = 110 * np.exp(-tt / 0.18) + 48
    phase = 2 * np.pi * np.cumsum(fdrop) / sr
    thump = np.sin(phase) * np.exp(-tt / 0.55) * 0.22 * (1 - np.exp(-tt / 0.006))
    shimmer = np.zeros(seg_len)
    for k, (fa, fb) in enumerate([(820, 1640), (1230, 2460), (1640, 3280)]):
        fg = fa + (fb - fa) * np.clip(tt / 0.45, 0, 1) ** 0.6
        ph = 2 * np.pi * np.cumsum(fg) / sr
        shimmer += np.sin(ph) * np.exp(-tt / (0.9 - 0.2 * k)) * (0.03 / (k + 1)) * (1 - np.exp(-tt / 0.02))
    acc = thump + shimmer
    L[i0:i0 + seg_len] += acc
    Rr[i0:i0 + seg_len] += acc * 0.92

    # 5. master: gentle soft clip, fades, normalise to -3 dBFS peak
    mix = np.stack([L, Rr], axis=1)
    mix = np.tanh(mix * 1.6) / 1.6
    fade_in = np.clip(t / 1.8, 0, 1) ** 2
    fade_out = np.clip((duration - t) / 2.6, 0, 1) ** 1.5
    mix *= (fade_in * fade_out)[:, None]
    peak = np.max(np.abs(mix)) + 1e-9
    mix *= 0.50 / peak   # -6 dBFS peak: comfortable listening level
    return (mix * 32767).astype(np.int16)


def write_wav(path, data, sr):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(data.shape[1])
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data.tobytes())


# ----------------------------------------------------------------------------
# Frame assembly
# ----------------------------------------------------------------------------
class Renderer:
    def __init__(self, poster, w, h, tl, max_scale):
        self.poster = poster
        self.w, self.h = w, h
        self.tl = tl
        self.max_scale = max_scale
        self.card = lattice_background(w, h)
        self.vig = vignette(w, h)
        self.indigo = Image.new("RGB", (w, h), INDIGO_DEEP)
        self.black = Image.new("RGBA", (w, h), (0, 0, 0, 255))

    def frame(self, t):
        tl = self.tl
        w, h = self.w, self.h
        k_poster = smooth(seg(t, *tl.poster_in))
        k_close = smoother(seg(t, *tl.closing_in))

        # base: title card -> poster
        if k_poster < 1.0:
            base = self.card.copy()
        else:
            base = None
        if k_poster > 0.0:
            p = poster_frame(self.poster, w, h, t, tl, self.max_scale)
            p = ImageChops.multiply(p, self.vig)
            dim = smooth(seg(t, *tl.schema_dim))
            if dim > 0:
                p = p.filter(ImageFilter.GaussianBlur(radius=w * 0.006 * dim))
                p = Image.blend(p, self.indigo, 0.85 * dim)
            p = p.convert("RGBA")
            base = p if base is None else Image.blend(base, p, k_poster)

        lay = title_layer(w, h, t, tl)
        if lay is not None:
            base = Image.alpha_composite(base, lay)
        lay = schematic_layer(w, h, t, tl)
        if lay is not None:
            base = Image.alpha_composite(base, lay)

        if k_close > 0:
            base = Image.blend(base, self.card, k_close)
            lay, _ = closing_layer(w, h, t, tl)
            if lay is not None:
                base = Image.alpha_composite(base, lay)
        # global fade in/out to black
        k_fade = smooth(seg(t, 0.0, 0.9)) * (1 - smooth(seg(t, *tl.closing_out)))
        if k_fade < 1.0:
            base = Image.blend(self.black, base, k_fade)
        return base.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", nargs="?", default=None,
                    help="path to the main illustration (PNG/JPG). Default: media/input/illustration.png, "
                         "then artwork/predatory-fungi-uzbekistan.png. Missing file -> placeholder plate")
    ap.add_argument("--image", dest="image_opt", default=None, help="same as the positional argument")
    ap.add_argument("--out", default=os.path.join(HERE, "output"), help="output directory")
    ap.add_argument("--duration", type=float, default=20.0, help="seconds (timeline scales)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--size", default="1280x720", help="WxH")
    ap.add_argument("--preview", action="store_true", help="fast draft: 640x360, 15 fps, faster x264 preset")
    ap.add_argument("--stills-only", action="store_true", help="only write the review stills, SVG and WAV")
    ap.add_argument("--no-audio", action="store_true", help="skip soundtrack synthesis (silent video)")
    ap.add_argument("--max-scale", type=float, default=1.28, help="final push-in zoom factor on the poster")
    ap.add_argument("--seed", type=int, default=5)
    args = ap.parse_args()

    image = args.image_opt or args.image
    if image is None:
        for cand in (os.path.join(HERE, "input", "illustration.png"),
                     os.path.join(PROJECT, "artwork", "predatory-fungi-uzbekistan.png")):
            image = cand
            if os.path.exists(cand):
                break
    w, h = (640, 360) if args.preview else tuple(int(v) for v in args.size.lower().split("x"))
    fps = 15 if args.preview else args.fps
    os.makedirs(args.out, exist_ok=True)
    sr = 48000
    tl = Timeline(args.duration)

    poster, source = load_poster(image, w, h, args.max_scale)
    print(f"[info] poster source: {source} ({poster.width}x{poster.height} working copy)")

    svg_path = os.path.join(args.out, "trap_schematic.svg")
    write_svg(svg_path)
    print(f"[info] wrote {svg_path}")

    wav_path = os.path.join(args.out, "soundtrack.wav")
    if not args.no_audio:
        audio = make_soundtrack(args.duration, sr, tl.worm_capture, seed=args.seed)
        write_wav(wav_path, audio, sr)
        print(f"[info] wrote {wav_path} ({args.duration:.1f}s, {sr} Hz stereo)")

    rend = Renderer(poster, w, h, tl, args.max_scale)
    still_times = [1.9, 7.5, 12.6, 13.8, 15.2, 18.6]
    for st in still_times:
        st = st * args.duration / 20.0
        p = os.path.join(args.out, f"still_{st:05.1f}s.png")
        rend.frame(st).save(p)
    print(f"[info] wrote {len(still_times)} review stills to {args.out}")
    if args.stills_only:
        return

    mp4_path = os.path.join(args.out, "companion.mp4")
    n_frames = int(round(args.duration * fps))
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
    if not args.no_audio:
        cmd += ["-i", wav_path]
    cmd += ["-c:v", "libx264", "-preset", "veryfast" if args.preview else "medium",
            "-crf", "23" if args.preview else "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-movflags", "+faststart"]
    if not args.no_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += [mp4_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(n_frames):
            t = i / fps
            proc.stdin.write(rend.frame(t).tobytes())
            if i % (fps * 2) == 0:
                print(f"\r[render] {i}/{n_frames} frames", end="", file=sys.stderr, flush=True)
    finally:
        proc.stdin.close()
        rc = proc.wait()
    print(file=sys.stderr)
    if rc != 0:
        print(f"[error] ffmpeg exited with {rc}", file=sys.stderr)
        sys.exit(rc)
    print(f"[info] wrote {mp4_path} ({n_frames} frames @ {fps} fps, {w}x{h})")


if __name__ == "__main__":
    main()
