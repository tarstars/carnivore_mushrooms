#!/usr/bin/env python3
"""«Привет из-под почвы» — six postcards from a nematode on a journey through the research lineage.

Each card: a sunny illustrated front (landscape, code-drawn, warm kitsch) and a written back
(message, stamp, address). The places are the real stations of predatory-fungus research the
research notes found; the letters are humorous fiction by a worm. Output: PDF (A6 cards, 2 per A4
page, fronts and backs on facing pages) and PNG previews.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from build_companion import find_font, FONT_CANDIDATES_REGULAR, FONT_CANDIDATES_ITALIC  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "output", "experiments", "postcards")
DPI = 300
MM = DPI / 25.4
CW, CH = int(148 * MM), int(105 * MM)   # A6 landscape
F = find_font(FONT_CANDIDATES_REGULAR)
FI = find_font(FONT_CANDIDATES_ITALIC)


def fnt(px, italic=False):
    return ImageFont.truetype(FI if italic else F, px)


CARDS = [
    {"place": "АШХАБАД, 1958", "sky": ((252, 214, 150), (236, 150, 90)), "ground": (208, 150, 86),
     "motif": "dunes", "msg": [
        "Дорогая тётя Панагреллус!",
        "Здесь жарко, песок до горизонта, и какой-то",
        "профессор Сопрунов собирает нас в баночки.",
        "Говорит, что из грибов сделает «препарат».",
        "Подумаешь. Я лично ни в какие кольца не лезу.",
        "Целую, твой Червяк."]},
    {"place": "ТАШКЕНТ, 1975", "sky": ((214, 236, 246), (250, 230, 190)), "ground": (196, 166, 110),
     "motif": "domes", "msg": [
        "Привет из столицы!",
        "Тут защитили диссертацию с моим участием",
        "(в самом конце, в списке литературы — нет,",
        "в разделе «материал»). Сто пятьдесят девять",
        "страниц, а обо мне ни слова хорошего.",
        "Зато купола бирюзовые. Твой Ч."]},
    {"place": "БАКУ, 1979", "sky": ((230, 240, 250), (190, 220, 236)), "ground": (120, 150, 170),
     "motif": "sea", "msg": [
        "Море! Ветер! Книга в 244 страницы!",
        "Мехтиева насчитала 87 видов тех, кто нас ест.",
        "Я прочёл список дважды и теперь не сплю.",
        "Говорят, кольца умеют ждать по пять часов,",
        "прежде чем сработать. Я тоже умею ждать.",
        "Напишу ещё. Ч."]},
    {"place": "НОВОСИБИРСК, 1990", "sky": ((236, 242, 250), (200, 214, 230)), "ground": (236, 240, 244),
     "motif": "snow", "msg": [
        "Холодно. Снег. Теплица.",
        "Здесь придумали «Нематофагин» и сыплют его",
        "под огурцы. Огурцы довольны, мы — не очень.",
        "Узнал, что гриб в почве живёт как хламидоспора,",
        "три года ждёт. Три года!",
        "Пора домой. Ч."]},
    {"place": "ПАСАДЕНА, 2017", "sky": ((252, 236, 170), (250, 190, 120)), "ground": (120, 170, 110),
     "motif": "palms", "msg": [
        "Хорошая новость: учёные доказали, что гриб",
        "пахнет едой и партнёром нарочно, чтобы меня",
        "заманить. Плохая новость: пахнет он прекрасно.",
        "Пишу из-за дерева, зажав нос.",
        "Солнце, пальмы, метил-3-метил-2-бутеноат.",
        "Твой Ч."]},
    {"place": "ПЕКИН, 2023", "sky": ((246, 226, 230), (236, 196, 170)), "ground": (190, 160, 130),
     "motif": "lab", "msg": [
        "Последняя открытка. Здесь под микроскопом",
        "сняли, как кольцо раздувается за долю секунды:",
        "три клетки, объём втрое, мембрана из запаса.",
        "Я посмотрел видео четыре раза.",
        "Решил стать вегетарианцем и жить в компосте.",
        "Обнимаю всеми сегментами, которых у меня нет. Ч."]},
]


def gradient(d, box, c0, c1):
    x0, y0, x1, y1 = box
    for i in range(int(y1 - y0)):
        k = i / max(1, (y1 - y0))
        d.line((x0, y0 + i, x1, y0 + i), fill=tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3)))


def front(card, idx):
    img = Image.new("RGB", (CW, CH), (250, 244, 230))
    d = ImageDraw.Draw(img)
    m = int(5 * MM)
    gradient(d, (m, m, CW - m, CH * 0.62), *card["sky"])
    d.rectangle((m, CH * 0.62, CW - m, CH - m), fill=card["ground"])
    rng = random.Random(idx)
    sunx, suny = CW * 0.78, CH * 0.22
    d.ellipse((sunx - 11 * MM, suny - 11 * MM, sunx + 11 * MM, suny + 11 * MM), fill=(252, 236, 160))
    mo = card["motif"]
    if mo == "dunes":
        for k in range(4):
            y = CH * (0.5 + 0.05 * k); col = (int(226 - 14 * k), int(170 - 12 * k), int(100 - 8 * k))
            pts = [(m, CH)] + [(m + (CW - 2 * m) * i / 30, y + 8 * MM * math.sin(i * 0.6 + k)) for i in range(31)] + [(CW - m, CH)]
            d.polygon(pts, fill=col)
    elif mo == "domes":
        for (dx, w, h) in [(0.2, 30, 26), (0.5, 40, 34), (0.75, 24, 20)]:
            cx = CW * dx; base = CH * 0.62
            d.rectangle((cx - w * MM / 2, base - h * MM * 0.55, cx + w * MM / 2, base), fill=(224, 186, 130))
            d.pieslice((cx - w * MM / 2, base - h * MM, cx + w * MM / 2, base - h * MM * 0.1), 180, 360, fill=(70, 170, 170))
            for k in range(3):
                d.arc((cx - w * MM / 2 + k * 2, base - h * MM + k * 2, cx + w * MM / 2 - k * 2, base - h * MM * 0.1 - k * 2), 180, 360, fill=(40, 120, 130), width=2)
        d.rectangle((CW * 0.62 - 2 * MM, CH * 0.25, CW * 0.62 + 2 * MM, CH * 0.62), fill=(224, 186, 130))
    elif mo == "sea":
        d.rectangle((m, CH * 0.45, CW - m, CH * 0.62), fill=(60, 130, 170))
        for i in range(40):
            x = rng.uniform(m, CW - m); y = rng.uniform(CH * 0.46, CH * 0.61)
            d.line((x, y, x + 6 * MM, y), fill=(190, 220, 236), width=3)
        d.polygon([(CW * 0.3, CH * 0.5), (CW * 0.3, CH * 0.25), (CW * 0.42, CH * 0.5)], fill=(250, 250, 240))
        d.rectangle((CW * 0.26, CH * 0.5, CW * 0.45, CH * 0.54), fill=(140, 70, 50))
    elif mo == "snow":
        for i in range(120):
            x = rng.uniform(m, CW - m); y = rng.uniform(m, CH - m)
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 255, 255))
        for (dx, s) in [(0.25, 1.0), (0.55, 1.3), (0.8, 0.9)]:
            cx = CW * dx; base = CH * 0.62
            for k in range(3):
                w = (22 - 5 * k) * MM * s; y = base - (8 + 9 * k) * MM * s
                d.polygon([(cx - w / 2, y), (cx + w / 2, y), (cx, y - 14 * MM * s)], fill=(50, 100, 80))
        d.rectangle((CW * 0.4, CH * 0.5, CW * 0.6, CH * 0.62), fill=(200, 230, 236), outline=(120, 140, 150), width=3)
    elif mo == "palms":
        for (dx, h) in [(0.18, 40), (0.3, 30), (0.85, 36)]:
            cx = CW * dx; base = CH * 0.62
            d.line((cx, base, cx + 5 * MM, base - h * MM), fill=(140, 100, 60), width=10)
            for a in range(0, 360, 45):
                d.line((cx + 5 * MM, base - h * MM, cx + 5 * MM + 14 * MM * math.cos(math.radians(a)), base - h * MM + 7 * MM * math.sin(math.radians(a)) + 4 * MM), fill=(60, 140, 80), width=8)
    elif mo == "lab":
        d.rectangle((CW * 0.2, CH * 0.3, CW * 0.8, CH * 0.62), fill=(246, 246, 250), outline=(180, 180, 190), width=3)
        d.ellipse((CW * 0.35, CH * 0.36, CW * 0.65, CH * 0.58), fill=(236, 222, 186), outline=(190, 176, 140), width=3)
        cx, cy = CW * 0.5, CH * 0.47; r = 7 * MM
        for c in range(3):
            d.arc((cx - r, cy - r, cx + r, cy + r), c * 120 + 5, c * 120 + 115, fill=(60, 160, 140), width=14)
    # the worm, always in the foreground, waving
    wx, wy = CW * 0.3, CH * 0.8
    pts = [(wx + i * 3 * MM, wy + 5 * MM * math.sin(i * 0.5)) for i in range(26)]
    for i, (x, y) in enumerate(pts):
        r = (2.2 + 2.0 * math.sin(math.pi * (0.1 + 0.9 * i / 25))) * MM
        d.ellipse((x - r, y - r, x + r, y + r), fill=(236, 190, 100))
    hx, hy = pts[-1]
    d.ellipse((hx - 1.2 * MM, hy - 1.2 * MM, hx + 1.2 * MM, hy + 1.2 * MM), fill=(60, 48, 40))
    d.line((hx + 2 * MM, hy - 3 * MM, hx + 8 * MM, hy - 10 * MM), fill=(236, 190, 100), width=int(2 * MM))
    # banner text
    banner = fnt(int(9 * MM))
    d.text((CW / 2 + 4, CH * 0.12 + 4), "ПРИВЕТ ИЗ-ПОД ПОЧВЫ!", font=banner, fill=(120, 60, 40), anchor="mm")
    d.text((CW / 2, CH * 0.12), "ПРИВЕТ ИЗ-ПОД ПОЧВЫ!", font=banner, fill=(250, 246, 230), anchor="mm")
    d.text((CW - 8 * MM + 2, CH - 12 * MM + 2), card["place"], font=fnt(int(6.5 * MM)), fill=(100, 60, 40), anchor="ra")
    d.text((CW - 8 * MM, CH - 12 * MM), card["place"], font=fnt(int(6.5 * MM)), fill=(250, 246, 230), anchor="ra")
    d.text((8 * MM, CH - 12 * MM), f"{idx + 1}/6", font=fnt(int(5 * MM)), fill=(250, 246, 230))
    d.text((CW/2, CH-5*MM), "Telegram · https://t.me/phys_math_dev", font=fnt(int(2.5*MM)), fill=(80,70,60), anchor="ma")
    return img


def back(card, idx):
    img = Image.new("RGB", (CW, CH), (248, 242, 226))
    d = ImageDraw.Draw(img)
    d.line((CW * 0.55, 10 * MM, CW * 0.55, CH - 10 * MM), fill=(120, 110, 100), width=2)
    d.text((CW * 0.55, 8 * MM), "ПОЧТОВАЯ КАРТОЧКА · ОТКРЫТОЕ ПИСЬМО", font=fnt(int(4 * MM)), fill=(120, 110, 100), anchor="ma")
    # stamp: a three-cell ring, "почта почвы"
    sx, sy = CW - 32 * MM, 12 * MM
    d.rectangle((sx, sy, sx + 24 * MM, sy + 28 * MM), fill=(236, 226, 196), outline=(150, 120, 80), width=2)
    for i in range(0, int(24 * MM), 12):
        d.ellipse((sx + i - 3, sy - 3, sx + i + 3, sy + 3), fill=(248, 242, 226))
        d.ellipse((sx + i - 3, sy + 28 * MM - 3, sx + i + 3, sy + 28 * MM + 3), fill=(248, 242, 226))
    cx, cy, r = sx + 12 * MM, sy + 12 * MM, 7 * MM
    for c in range(3):
        d.arc((cx - r, cy - r, cx + r, cy + r), c * 120 + 5, c * 120 + 115, fill=(60, 140, 120), width=12)
    d.text((sx + 12 * MM, sy + 24 * MM), "ПОЧТА ПОЧВЫ · 3", font=fnt(int(2.8 * MM)), fill=(100, 80, 50), anchor="mm")
    # postmark
    pm = (CW - 50 * MM, 26 * MM)
    d.ellipse((pm[0] - 12 * MM, pm[1] - 12 * MM, pm[0] + 12 * MM, pm[1] + 12 * MM), outline=(90, 90, 110), width=3)
    d.text(pm, card["place"].split(",")[0], font=fnt(int(3 * MM)), fill=(90, 90, 110), anchor="mm")
    d.text((pm[0], pm[1] + 5 * MM), card["place"].split(", ")[1], font=fnt(int(3 * MM)), fill=(90, 90, 110), anchor="mm")
    # address lines
    for k in range(4):
        y = CH * 0.55 + k * 9 * MM
        d.line((CW * 0.6, y, CW - 10 * MM, y), fill=(160, 150, 140), width=2)
    d.text((CW * 0.6, CH * 0.55 - 7 * MM), "Кому: тёте Панагреллус, компост", font=fnt(int(3.6 * MM), True), fill=(80, 70, 60))
    d.text((CW * 0.6, CH * 0.55 + 2 * MM), "Куда: под яблоней, где никто не ест", font=fnt(int(3.6 * MM), True), fill=(80, 70, 60))
    # message
    # message wrapped to the left column, clear of the divider at CW*0.55
    f = fnt(int(3.5 * MM), True)
    maxw = CW * 0.55 - 14 * MM
    lines = []
    for ln in card["msg"]:
        cur = ""
        for w in ln.split(" "):
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > maxw:
                lines.append(cur); cur = w
            else:
                cur = t
        lines.append(cur)
    y = 16 * MM
    for ln in lines:
        d.text((8 * MM, y), ln, font=f, fill=(60, 48, 40))
        y += 6.6 * MM
    d.text((10 * MM, CH - 14 * MM), "Вымышленная переписка и воображаемый маршрут по мотивам истории изучения ловчих грибов.", font=fnt(int(2.6 * MM)), fill=(120, 110, 100))
    d.text((10 * MM, CH - 10 * MM), "Города и годы — ориентиры, а не места конкретных опытов. Художественная интерпретация.", font=fnt(int(2.6 * MM)), fill=(120, 110, 100))
    d.text((CW/2, CH-5*MM), "Telegram · https://t.me/phys_math_dev", font=fnt(int(2.5*MM)), fill=(80,70,60), anchor="ma")
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    A4 = (int(210 * MM), int(297 * MM))
    pages = []
    fronts = [front(c, i) for i, c in enumerate(CARDS)]
    backs = [back(c, i) for i, c in enumerate(CARDS)]
    for k in range(0, 6, 2):
        for group in (fronts, backs):
            p = Image.new("RGB", A4, (255, 255, 255))
            p.paste(group[k], (int(31 * MM), int(30 * MM)))
            p.paste(group[k + 1], (int(31 * MM), int(30 * MM + 115 * MM)))
            dd = ImageDraw.Draw(p)
            dd.rectangle((int(31 * MM) - 1, int(30 * MM) - 1, int(31 * MM) + CW, int(30 * MM) + CH), outline=(200, 200, 200))
            dd.rectangle((int(31 * MM) - 1, int(145 * MM) - 1, int(31 * MM) + CW, int(145 * MM) + CH), outline=(200, 200, 200))
            pages.append(p)
    pdf = os.path.join(OUT, "postcards_A4_duplex.pdf")
    pages[0].save(pdf, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    for i, (f, b) in enumerate(zip(fronts, backs), 1):
        f.resize((740, 525), Image.LANCZOS).save(os.path.join(OUT, f"card{i}_front.png"))
        b.resize((740, 525), Image.LANCZOS).save(os.path.join(OUT, f"card{i}_back.png"))
    sheet = Image.new("RGB", (740 * 3, 525 * 2), (255, 255, 255))
    for i, f in enumerate(fronts):
        sheet.paste(f.resize((740, 525), Image.LANCZOS), ((i % 3) * 740, (i // 3) * 525))
    sheet.save(os.path.join(OUT, "fronts_sheet.png"))
    print("[info] wrote", pdf)


if __name__ == "__main__":
    main()
