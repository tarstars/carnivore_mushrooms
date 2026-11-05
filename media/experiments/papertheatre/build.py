#!/usr/bin/env python3
"""Paper theatre: a print-and-play constricting ring with pull tabs. A4 PDF, three sheets.

Sheet 1  BACKDROP   — cut the stage window; a sunburnt horizon above, soil below.
Sheet 2  RING       — a celadon three-cell ring. Each cell is a separate crescent with a tab.
                      Cut the three slots in the ring plate; thread each crescent's tab through its slot
                      from behind. Pull all three tabs outward and the crescents slide INWARD and close
                      the opening: the cells "inflate" into the lumen.
Sheet 3  WORM + KEY — a honey-coloured worm strip to thread through the ring, the field-guide text
                      and the assembly diagram.

Everything is drawn with Pillow at 300 dpi and saved as one multi-page PDF.
Colours: cream paper, terracotta, turquoise, ochre. Nothing black-on-gold.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from build_companion import find_font, FONT_CANDIDATES_REGULAR, FONT_CANDIDATES_ITALIC  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "output", "experiments", "papertheatre")
DPI = 300
A4 = (int(8.27 * DPI), int(11.69 * DPI))   # 2481 x 3507
MM = DPI / 25.4

CREAM = (246, 238, 220)
TERRA = (190, 92, 58)
TURQ = (62, 160, 150)
OCHRE = (214, 164, 72)
INK = (60, 48, 40)
CELADON = (176, 220, 198)
CELADON_D = (96, 160, 140)
HONEY = (236, 190, 100)
SKY = (236, 196, 150)
SOIL = (150, 102, 70)

F = find_font(FONT_CANDIDATES_REGULAR)
FI = find_font(FONT_CANDIDATES_ITALIC)


def fnt(px, italic=False):
    return ImageFont.truetype(FI if italic else F, px)


def page():
    img = Image.new("RGB", A4, CREAM)
    d = ImageDraw.Draw(img)
    d.text((20*MM, 7*MM), "Telegram · https://t.me/phys_math_dev", font=fnt(30), fill=INK)
    return img, d


def cutline(d, xy, dash=12):
    """Dashed cut line (scissors) — a rectangle or polyline given as list of points."""
    pts = xy
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / dash))
        for k in range(0, n, 2):
            a = k / n; b = min(1, (k + 1) / n)
            d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=INK, width=3)


def foldline(d, p0, p1):
    x0, y0 = p0; x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / 40))
    for k in range(n):
        a = k / n; b = a + 0.5 / n
        d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=TURQ, width=3)
        d.ellipse((x0 + (x1 - x0) * (b + 0.2 / n) - 3, y0 + (y1 - y0) * (b + 0.2 / n) - 3, x0 + (x1 - x0) * (b + 0.2 / n) + 3, y0 + (y1 - y0) * (b + 0.2 / n) + 3), fill=TURQ)


def header(d, title, sub, n):
    d.text((20 * MM, 14 * MM), title, font=fnt(72), fill=TERRA)
    d.text((20 * MM, 24 * MM), sub, font=fnt(34, True), fill=INK)
    d.text((A4[0] - 20 * MM, 16 * MM), f"лист {n} / 4", font=fnt(34), fill=INK, anchor="ra")
    d.line((20 * MM, 33 * MM, A4[0] - 20 * MM, 33 * MM), fill=OCHRE, width=4)


def crescent(d, cx, cy, R, a0, a1, thick, fill, outline, bulge=0.0):
    pts = []
    steps = 40
    for i in range(steps + 1):
        s = i / steps; a = math.radians(a0 + (a1 - a0) * s)
        r = R + thick * 0.02 * math.sin(math.pi * s)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(steps, -1, -1):
        s = i / steps; a = math.radians(a0 + (a1 - a0) * s)
        r = R - thick * (1 + bulge * math.sin(math.pi * s) ** 0.8)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=4)
    return pts


def sheet_backdrop():
    img, d = page()
    header(d, "БУМАЖНЫЙ ТЕАТР · ХИЩНЫЕ ГРИБЫ", "Лист 1 из 4 — задник. Вырежьте окно сцены по пунктиру.", 1)
    x0, y0, x1, y1 = 25 * MM, 45 * MM, A4[0] - 25 * MM, A4[1] - 60 * MM
    # sky / horizon / soil
    d.rectangle((x0, y0, x1, y0 + 55 * MM), fill=SKY)
    for i in range(0, int(55 * MM), 6):
        k = i / (55 * MM)
        d.line((x0, y0 + i, x1, y0 + i), fill=(int(236 - 30 * k), int(196 - 40 * k), int(150 - 30 * k)))
    # domes and minaret silhouettes
    for (dx, w, h) in [(0.25, 26, 18), (0.62, 20, 14), (0.80, 16, 12)]:
        cx = x0 + (x1 - x0) * dx; base = y0 + 55 * MM
        d.rectangle((cx - w * MM / 2, base - h * MM * 0.5, cx + w * MM / 2, base), fill=(206, 160, 110))
        d.pieslice((cx - w * MM / 2, base - h * MM, cx + w * MM / 2, base - h * MM * 0.0), 180, 360, fill=TURQ)
    d.rectangle((x0 + (x1 - x0) * 0.47 - 3 * MM, y0 + 20 * MM, x0 + (x1 - x0) * 0.47 + 3 * MM, y0 + 55 * MM), fill=(196, 150, 100))
    # soil band with roots
    d.rectangle((x0, y0 + 55 * MM, x1, y1), fill=SOIL)
    import random
    rng = random.Random(4)
    for _ in range(300):
        px, py = rng.uniform(x0, x1), rng.uniform(y0 + 55 * MM, y1)
        d.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(int(SOIL[0] * rng.uniform(0.7, 1.1)), int(SOIL[1] * rng.uniform(0.7, 1.1)), int(SOIL[2] * rng.uniform(0.7, 1.1))))
    for _ in range(14):
        px = rng.uniform(x0 + 10 * MM, x1 - 10 * MM); py = y0 + 55 * MM
        pts = [(px, py)]
        for k in range(8):
            px += rng.uniform(-6, 6) * MM; py += rng.uniform(6, 12) * MM
            pts.append((px, py))
        d.line(pts, fill=(226, 206, 170), width=5)
    # stage window
    wx0, wy0, wx1, wy1 = x0 + 35 * MM, y0 + 75 * MM, x1 - 35 * MM, y1 - 20 * MM
    d.rectangle((wx0, wy0, wx1, wy1), fill=CREAM)
    cutline(d, [(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1), (wx0, wy0)])
    d.text(((wx0 + wx1) / 2, (wy0 + wy1) / 2 - 10 * MM), "ОКНО СЦЕНЫ", font=fnt(60), fill=OCHRE, anchor="mm")
    d.text(((wx0 + wx1) / 2, (wy0 + wy1) / 2 + 4 * MM), "вырезать · за окном стоит лист 2", font=fnt(34, True), fill=INK, anchor="mm")
    # title ribbon on the backdrop
    d.text(((x0 + x1) / 2, y0 + 64 * MM), "ХИЩНЫЕ ГРИБЫ УЗБЕКИСТАНА", font=fnt(66), fill=CREAM, anchor="mm")
    # footer
    d.text((20 * MM, A4[1] - 48 * MM), "Бумажная модель трёхклеточного сжимающегося кольца. Художественная интерпретация: масштаб и время условны.", font=fnt(30, True), fill=INK)
    d.text((20 * MM, A4[1] - 40 * MM), "Печать A4 на плотной бумаге 160–200 г/м². Пунктир — резать, точки-тире — сгибать.", font=fnt(30), fill=INK)
    return img


def sheet_ring():
    img, d = page()
    header(d, "КОЛЬЦО", "Лист 2 — пластина кольца с отверстием и тремя прорезями.", 2)
    cx, cy = A4[0] / 2, 118 * MM
    R = 48 * MM
    # ring plate: a square plate with a round opening and three slots
    px0, py0, px1, py1 = cx - 75 * MM, cy - 70 * MM, cx + 75 * MM, cy + 70 * MM
    d.rectangle((px0, py0, px1, py1), fill=(238, 226, 200), outline=INK, width=4)
    cutline(d, [(px0, py0), (px1, py0), (px1, py1), (px0, py1), (px0, py0)])
    # the ring (three resting cells drawn on the plate)
    for c in range(3):
        a0 = -90 + c * 120 + 3; a1 = a0 + 114
        crescent(d, cx, cy, R, a0, a1, 12 * MM, CELADON, CELADON_D)
    # inner opening to cut
    d.ellipse((cx - R + 12 * MM, cy - R + 12 * MM, cx + R - 12 * MM, cy + R - 12 * MM), fill=CREAM)
    cutline(d, [(cx + (R - 12 * MM) * math.cos(math.radians(a)), cy + (R - 12 * MM) * math.sin(math.radians(a))) for a in range(0, 361, 6)])
    # three radial slots for the tabs (at the middle of each cell), cut lines
    for c in range(3):
        am = math.radians(-90 + c * 120 + 60)
        s0 = (cx + (R - 2 * MM) * math.cos(am), cy + (R - 2 * MM) * math.sin(am))
        s1 = (cx + (R + 14 * MM) * math.cos(am), cy + (R + 14 * MM) * math.sin(am))
        d.line((s0, s1), fill=INK, width=6)
        d.text((cx + (R + 20 * MM) * math.cos(am), cy + (R + 20 * MM) * math.sin(am)), "прорезь", font=fnt(26), fill=INK, anchor="mm")
    d.text((cx, py1 + 8 * MM), "ПЛАСТИНА: вырежьте по контуру, круглое отверстие и три прорези", font=fnt(32), fill=INK, anchor="ma")
    d.text((20 * MM, A4[1] - 48 * MM), "Пластина: вырежьте по контуру, круглое отверстие и три прорези. Клетки с язычками — на листе 3.", font=fnt(30), fill=INK)
    return img


def sheet_cells():
    img, d = page()
    header(d, "ТРИ КЛЕТКИ", "Лист 3 — три полумесяца с язычками, каждый вырезается отдельно.", 3)
    R = 48 * MM
    for c in range(3):
        ccy = 70 * MM + c * 72 * MM          # rows 72 mm apart: crescent ~84 mm wide, ~26 mm tall, tab 30 mm
        ccx = A4[0] / 2
        a0 = -150; a1 = -30
        pts = crescent(d, ccx, ccy + R, R, a0, a1, 12 * MM, CELADON, CELADON_D, bulge=1.4)
        tx = ccx; ty = ccy + R - R
        d.rectangle((tx - 5 * MM, ty - 30 * MM, tx + 5 * MM, ty + 2 * MM), fill=OCHRE, outline=INK, width=3)
        d.text((tx, ty - 16 * MM), "тянуть", font=fnt(24), fill=INK, anchor="mm")
        cutline(d, [(tx - 5 * MM, ty - 30 * MM), (tx + 5 * MM, ty - 30 * MM), (tx + 5 * MM, ty - 2 * MM)])
        cutline(d, [(tx - 5 * MM, ty - 30 * MM), (tx - 5 * MM, ty - 2 * MM)])
        cutline(d, pts + [pts[0]])
        d.text((ccx - 80 * MM, ccy + 12 * MM), f"клетка {c + 1}", font=fnt(30), fill=INK, anchor="lm")
    d.text((20 * MM, A4[1] - 48 * MM), "Вырежьте три полумесяца вместе с язычками. Протяните язычок каждой клетки сзади через свою прорезь на листе 2 так, чтобы", font=fnt(30), fill=INK)
    d.text((20 * MM, A4[1] - 41 * MM), "полумесяц лежал поверх своей трети кольца. Потяните три язычка наружу — полумесяцы сдвинутся ВНУТРЬ и закроют отверстие.", font=fnt(30), fill=INK)
    d.text((20 * MM, A4[1] - 33 * MM), "Так и у Drechslerella: три клетки раздуваются в просвет кольца за 0,1–1 с. Здесь — за одно движение пальцев.", font=fnt(30, True), fill=TERRA)
    return img


def sheet_worm():
    img, d = page()
    header(d, "ЧЕРВЬ И СБОРКА", "Лист 4 — лента-нематода, указатель и схема сборки.", 4)
    # worm strip: a long tapered band to cut, 260 mm long, folded in two to fit
    y = 60 * MM
    for row in range(2):
        yy = y + row * 34 * MM
        pts_top, pts_bot = [], []
        n = 60
        for i in range(n + 1):
            s = i / n
            x = 20 * MM + s * (A4[0] - 40 * MM)
            ss = s if row == 0 else 1 - s
            if row == 0:
                taper = min(1, ss / 0.12) if ss < 0.12 else 1
            else:
                taper = min(1, (1 - ss) / 0.35) ** 0.7 if ss > 0.65 else 1
            h = 11 * MM * (0.15 + 0.85 * taper)
            pts_top.append((x, yy - h)); pts_bot.append((x, yy + h))
        poly = pts_top + pts_bot[::-1]
        d.polygon(poly, fill=HONEY, outline=INK, width=3)
        d.line([(x, yy - 3 * MM) for (x, _) in pts_top[6:-6]], fill=(250, 232, 180), width=6)
        d.line([(x, yy + 2 * MM) for (x, _) in pts_top[4:-4]], fill=(206, 140, 70), width=3)
        cutline(d, poly + [poly[0]])
    d.text((20 * MM, y + 60 * MM), "Склейте два отрезка концами (голова — тупой конец, хвост — острый). Проденьте ленту сквозь отверстие кольца.", font=fnt(30), fill=INK)
    # assembly diagram
    ax, ay = A4[0] / 2, 150 * MM
    d.text((ax, ay - 16 * MM), "СБОРКА", font=fnt(48), fill=TERRA, anchor="mm")
    # row 1: side view (layers from the viewer): backdrop, plate + cells, tabs
    sx0 = 30 * MM
    for i, (label, col) in enumerate([("лист 1: задник", SOIL), ("листы 2+3: пластина и клетки", CELADON_D), ("язычки торчат за край", OCHRE)]):
        bx = sx0 + i * 55 * MM
        d.rectangle((bx, ay, bx + 4 * MM, ay + 30 * MM), fill=col)
        d.text((bx + 8 * MM, ay + 12 * MM), label, font=fnt(26), fill=INK, anchor="lm")
    d.text((sx0, ay + 36 * MM), "вид сбоку: задник сзади, пластина перед ним, язычки выходят за края пластины — за них тянут", font=fnt(26, True), fill=INK)
    # row 2: two top views, centred, within x = 45..165 mm
    for k, (lbl, bul) in enumerate([("покой: отверстие открыто", 0.0), ("тянем язычки: клетки внутрь", 1.4)]):
        ccx = 75 * MM + k * 60 * MM; ccy = ay + 56 * MM; r = 16 * MM
        for c in range(3):
            a0 = -90 + c * 120 + 3; a1 = a0 + 114
            crescent(d, ccx, ccy, r, a0, a1, 6 * MM, CELADON, CELADON_D, bulge=bul)
            am = math.radians(a0 + 57)
            d.line((ccx + r * math.cos(am), ccy + r * math.sin(am), ccx + (r + 10 * MM) * math.cos(am), ccy + (r + 10 * MM) * math.sin(am)), fill=OCHRE, width=8)
        d.line((ccx - 28 * MM, ccy, ccx + 28 * MM, ccy), fill=HONEY, width=int(6 * MM * (1 - 0.3 * bul)))
        d.text((ccx, ccy + 30 * MM), lbl, font=fnt(26), fill=INK, anchor="ma")
    # field guide
    gy = 248 * MM
    d.text((20 * MM, gy), "Что это", font=fnt(44), fill=TERRA)
    lines = [
        "Drechslerella dactyloides ловит почвенных нематод кольцом из трёх клеток на ножке.",
        "Червь задевает внутреннюю стенку — клетки раздуваются внутрь за 0,1–1 с, объём вырастает втрое.",
        "Arthrobotrys oligospora ловит иначе: клейкой трёхмерной сетью. Это два разных механизма.",
        "Название театра — из диссертации Ф. Х. Файзиевой «Хищные грибы Узбекистана», Ташкент, 1975.",
        "Модель бумажная и весёлая, а не научная реконструкция: масштаб, цвет и скорость условны.",
    ]
    for i, ln in enumerate(lines):
        d.text((20 * MM, gy + 11 * MM + i * 7 * MM), ln, font=fnt(28), fill=INK)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    pages = [sheet_backdrop(), sheet_ring(), sheet_cells(), sheet_worm()]
    pdf = os.path.join(OUT, "papertheatre_A4.pdf")
    pages[0].save(pdf, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    for i, p in enumerate(pages, 1):
        p.resize((827, 1169), Image.LANCZOS).save(os.path.join(OUT, f"sheet{i}_preview.png"))
    print("[info] wrote", pdf)


if __name__ == "__main__":
    main()
