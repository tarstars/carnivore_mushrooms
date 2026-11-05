#!/usr/bin/env python3
"""Hyphal typeface: the title's letters grown as hyphae inside the glyph masks.

Each glyph of «ХИЩНЫЕ / ГРИБЫ / УЗБЕКИСТАНА» is rendered as a mask (EB Garamond), filled with
attractor points, and a space-colonisation tree grows from the glyph's baseline into the mask.
Stroke width follows the pipe model (thicker where more branches join). Ring-shaped trap
ornaments sit on a few terminal tips. Output: a 2400x1350 PNG poster and an SVG of the strokes.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from colonize import Colonizer  # noqa: E402
from build_companion import INDIGO_DEEP, IVORY, GOLD, CELADON, TURQUOISE, find_font, FONT_CANDIDATES_REGULAR  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "output", "experiments", "hyphatype")
LINES = ["ХИЩНЫЕ", "ГРИБЫ", "УЗБЕКИСТАНА"]


def grow_glyph(mask, rng, seed):
    """mask: bool array (h,w). Returns Colonizer with the grown tree in mask coords."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    n_att = max(300, len(xs) // 22)
    pick = rng.choice(len(xs), n_att, replace=False)
    att = np.column_stack([xs[pick], ys[pick]]).astype(np.float32)
    # roots: a few points along the bottom edge of the glyph
    bottom = ys.max()
    base_cols = xs[ys > bottom - 6]
    roots = []
    for c in np.linspace(base_cols.min(), base_cols.max(), 3):
        roots.append((float(c), float(bottom + 4)))
    col = Colonizer(att, roots, influence=80, kill=6, step=4.0, seed=seed, jitter=0.35)
    for _ in range(400):
        if col.grow() == 0:
            break
    return col


def main(lines=None, output=None, language="ru"):
    out = output or OUT
    lines = lines or LINES
    os.makedirs(out, exist_ok=True)
    W, H = 2400, 1350
    PAPER = (238, 228, 204)
    INKC = (48, 42, 36)
    JADE = (40, 120, 100)
    img = Image.new("RGB", (W, H), PAPER)
    # paper grain
    g = np.array(Image.effect_noise((W, H), 14).convert("L"), dtype=np.int16) - 128
    img = Image.fromarray(np.clip(np.array(img, dtype=np.int16) + g[..., None] // 4, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(5)
    fpath = find_font(FONT_CANDIDATES_REGULAR)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<rect width="{W}" height="{H}" fill="rgb(238,228,204)"/>']
    y = 150
    sizes = [300, 300, 300]
    for li, line in enumerate(lines):
        tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
        size = sizes[li]
        # fit the line inside safe margins before growing (the 11-letter line is wider than the canvas at 300 px)
        while True:
            fnt = ImageFont.truetype(fpath, size)
            total = sum(tmp.textlength(ch, font=fnt) for ch in line) + 18 * (len(line) - 1)
            if total <= W - 2 * 120 or size < 120:
                break
            size -= 6
        sizes[li] = size
        x = (W - total) / 2
        for ci, ch in enumerate(line):
            gw = int(tmp.textlength(ch, font=fnt)) + 40
            gh = sizes[li] + 80
            m = Image.new("L", (gw, gh), 0)
            ImageDraw.Draw(m).text((20, 20), ch, font=fnt, fill=255)
            mask = np.array(m) > 128
            col = grow_glyph(mask, rng, seed=li * 100 + ci)
            if col is not None:
                size = col.subtree_sizes()
                segs = col.segments()
                ox, oy = x - 20, y - 20
                for (x0, y0, x1, y1, dep) in segs:
                    # child index lookup: width from subtree size of child
                    pass
                idx = np.nonzero(col.parent >= 0)[0]
                for k, i in enumerate(idx):
                    p = col.parent[i]
                    wdt = 1.8 + 4.0 * math.log1p(size[i]) / math.log1p(size.max())
                    x0, y0 = col.nodes[p]; x1, y1 = col.nodes[i]
                    d.line((ox + x0, oy + y0, ox + x1, oy + y1), fill=INKC + (235,), width=int(round(wdt)))
                    svg.append(f'<line x1="{ox+x0:.1f}" y1="{oy+y0:.1f}" x2="{ox+x1:.1f}" y2="{oy+y1:.1f}" stroke="rgb{INKC}" stroke-width="{wdt:.2f}" stroke-linecap="round"/>')
                # ornaments: small three-cell rings on a few leaf tips
                leaves = [i for i in idx if size[i] == 1]
                for i in rng.choice(leaves, min(3, len(leaves)), replace=False):
                    cx, cy = col.nodes[i]; r = 9
                    for c in range(3):
                        a0 = c * 120 + 4; a1 = (c + 1) * 120 - 4
                        d.arc((ox + cx - r, oy + cy - r, ox + cx + r, oy + cy + r), a0, a1, fill=JADE + (230,), width=4)
                        svg.append(f'<path d="M{ox+cx+r*math.cos(math.radians(a0)):.1f},{oy+cy+r*math.sin(math.radians(a0)):.1f} A{r},{r} 0 0 1 {ox+cx+r*math.cos(math.radians(a1)):.1f},{oy+cy+r*math.sin(math.radians(a1)):.1f}" fill="none" stroke="rgb{JADE}" stroke-width="4" stroke-linecap="round"/>')
                # a couple of adhesive droplets
                for i in rng.choice(leaves, min(4, len(leaves)), replace=False):
                    cx, cy = col.nodes[i]
                    d.ellipse((ox + cx - 3, oy + cy - 3, ox + cx + 3, oy + cy + 3), fill=(196, 92, 44, 220))
                    svg.append(f'<circle cx="{ox+cx:.1f}" cy="{oy+cy:.1f}" r="3" fill="rgb(196,92,44)"/>')
            x += tmp.textlength(ch, font=fnt) + 18
        y += sizes[li] + 60
    # caption
    cap = ImageFont.truetype(fpath, 34)
    d.text((W / 2, H - 70), ("hyphal lettering · grown by a space-colonisation algorithm · @phys_math_dev" if language == "en" else "гифальный шрифт · буквы выращены алгоритмом колонизации пространства · художественная интерпретация"),
           font=cap, fill=(120, 96, 60, 230), anchor="ma")
    svg.append(f'<text x="{W/2}" y="{H-60}" text-anchor="middle" font-family="EB Garamond, serif" font-size="34" fill="rgb(120,96,60)">{"hyphal lettering · artistic interpretation · @phys_math_dev" if language == "en" else "гифальный шрифт · художественная интерпретация"}</text>')
    svg.append("</svg>")
    img.save(os.path.join(out, "hyphatype_poster.png"))
    with open(os.path.join(out, "hyphatype_poster.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    img.resize((1200, 675), Image.LANCZOS).save(os.path.join(out, "hyphatype_preview.png"))
    print("[info] wrote", out)


if __name__ == "__main__":
    main()
