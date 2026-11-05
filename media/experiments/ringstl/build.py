#!/usr/bin/env python3
"""3D-printable constricting ring: binary STL from numpy, rest and inflated states, plus a pendant.

Geometry: three cells, each a swept tube along a 116-degree arc with a varying radius; the inflated
version thickens inward (the centreline moves toward the lumen). A short stalk joins the lower
septum gap. The pendant variant adds a small loop for a cord. Units: millimetres; ring diameter
~40 mm, printable without supports lying flat (the ring is slightly flattened on the back).
Outputs: ring_rest.stl, ring_inflated.stl, ring_pendant.stl, and a PNG preview rendered with a
painter's-algorithm projection in Pillow (no external renderer needed).
"""
import math
import os
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from build_companion import find_font, FONT_CANDIDATES_REGULAR  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "output", "experiments", "ringstl")


def tube(path_fn, radius_fn, n_along=90, n_round=28):
    """Sweep a circle along a 3D path. path_fn(s)->(x,y,z), radius_fn(s)->r, s in [0,1]."""
    P = np.array([path_fn(i / (n_along - 1)) for i in range(n_along)], dtype=np.float64)
    R = np.array([radius_fn(i / (n_along - 1)) for i in range(n_along)])
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    up = np.array([0, 0, 1.0])
    verts = []
    for i in range(n_along):
        n1 = np.cross(T[i], up)
        if np.linalg.norm(n1) < 1e-6:
            n1 = np.cross(T[i], [1, 0, 0])
        n1 /= np.linalg.norm(n1)
        n2 = np.cross(T[i], n1)
        ring = []
        for k in range(n_round):
            a = 2 * math.pi * k / n_round
            # slightly flattened on the back (z<0) so it prints lying flat
            rz = R[i] * (0.85 if math.sin(a) < 0 else 1.0)
            ring.append(P[i] + n1 * R[i] * math.cos(a) + n2 * rz * math.sin(a))
        verts.append(ring)
    tris = []
    for i in range(n_along - 1):
        for k in range(n_round):
            a, b = verts[i][k], verts[i][(k + 1) % n_round]
            c, d = verts[i + 1][k], verts[i + 1][(k + 1) % n_round]
            tris.append((a, c, b)); tris.append((b, c, d))
    # caps
    for i, order in ((0, 1), (n_along - 1, -1)):
        c = P[i]
        for k in range(n_round):
            a, b = verts[i][k], verts[i][(k + 1) % n_round]
            tris.append((c, b, a) if order == 1 else (c, a, b))
    return tris


def cell(a0_deg, infl, R=18.0, r0=4.2):
    span = 116.0

    def path(s):
        a = math.radians(a0_deg + s * span)
        bump = math.sin(math.pi * s) ** 0.8
        rc = R - 0.30 * R * 0.6 * infl * bump
        return (rc * math.cos(a), rc * math.sin(a), 0.0)

    def rad(s):
        bump = math.sin(math.pi * s) ** 0.8
        end = min(1.0, min(s, 1 - s) / 0.12) ** 0.5   # rounded ends
        return (r0 * (1 + 0.1 * math.sin(math.pi * s)) + 0.24 * R * 0.6 * infl * bump) * (0.25 + 0.75 * end)
    return tube(path, rad)


def stalk(R=18.0):
    def path(s):
        return (0.0, -R - 2 - s * 12.0, 0.0)

    def rad(s):
        return 1.8
    return tube(path, rad, n_along=12, n_round=16)


def loop(R=18.0):
    def path(s):
        a = 2 * math.pi * s
        return (0.0, R + 4.5 + 2.6 * math.cos(a), 2.6 * math.sin(a))

    def rad(s):
        return 1.1
    return tube(path, rad, n_along=40, n_round=12)


def write_stl(path, tris, name=b"predatory_fungi_ring"):
    with open(path, "wb") as f:
        f.write(name.ljust(80, b"\0"))
        f.write(struct.pack("<I", len(tris)))
        for (a, b, c) in tris:
            n = np.cross(np.subtract(b, a), np.subtract(c, a))
            n = n / (np.linalg.norm(n) + 1e-12)
            f.write(struct.pack("<3f", *n))
            for v in (a, b, c):
                f.write(struct.pack("<3f", *v))
            f.write(b"\0\0")


def preview(models, path, size=(1400, 520)):
    img = Image.new("RGB", size, (238, 228, 204))
    d = ImageDraw.Draw(img)
    light = np.array([0.4, -0.5, 0.75]); light /= np.linalg.norm(light)
    for mi, (title, tris) in enumerate(models):
        cx = size[0] * (mi + 0.5) / len(models); cy = size[1] * 0.5
        sc = 7.0
        rot = math.radians(-58)
        rows = []
        for (a, b, c) in tris:
            pts = []
            z = 0
            for v in (a, b, c):
                x, y, zz = v
                # tilt around x
                y2 = y * math.cos(rot) - zz * math.sin(rot)
                z2 = y * math.sin(rot) + zz * math.cos(rot)
                pts.append((cx + x * sc, cy - y2 * sc)); z += z2
            n = np.cross(np.subtract(b, a), np.subtract(c, a)); nn = np.linalg.norm(n)
            if nn == 0:
                continue
            n = n / nn
            shade = max(0.0, float(np.dot(n, light)))
            rows.append((z / 3, pts, shade))
        rows.sort(key=lambda r: r[0])
        for (_, pts, sh) in rows:
            col = (int(120 + 110 * sh), int(170 + 70 * sh), int(150 + 60 * sh))
            d.polygon(pts, fill=col)
        d.text((cx, size[1] - 40), title, fill=(60, 48, 40), anchor="mm", font=ImageFont.truetype(find_font(FONT_CANDIDATES_REGULAR), 30))
    img.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    rest = cell(-90 + 2, 0.0) + cell(30 + 2, 0.0) + cell(150 + 2, 0.0) + stalk()
    infl = cell(-90 + 2, 1.0) + cell(30 + 2, 1.0) + cell(150 + 2, 1.0) + stalk()
    pend = cell(-90 + 2, 0.6) + cell(30 + 2, 0.6) + cell(150 + 2, 0.6) + loop()
    write_stl(os.path.join(OUT, "ring_rest.stl"), rest)
    write_stl(os.path.join(OUT, "ring_inflated.stl"), infl)
    write_stl(os.path.join(OUT, "ring_pendant.stl"), pend)
    preview([("кольцо в покое, 40 мм", rest), ("клетки раздуты внутрь", infl), ("подвеска с петлёй", pend)],
            os.path.join(OUT, "ringstl_preview.png"))
    for n, t in (("rest", rest), ("inflated", infl), ("pendant", pend)):
        print(f"[info] {n}: {len(t)} triangles")
    print("[info] wrote", OUT)


if __name__ == "__main__":
    main()
