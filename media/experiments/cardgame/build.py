#!/usr/bin/env python3
"""«ЛОВЧЕЕ КОЛЬЦО» — a print-and-play card game for two: the Fungus and the Worm.

36 cards (9 per A4 sheet, 4 sheets) + one rules sheet. Warm paper, terracotta/jade/marigold.
Rules in short (full rules on sheet 5):
  * The Worm wants to cross the dish: 6 bacteria eaten wins. The Fungus wants 3 captures.
  * Each round both play one card face down, then reveal. A table on the rules sheet resolves them.
  * Rings need a turn to mature («Кольцо зреет» → «Кольцо готово»); scent («Запах») forces the Worm
    to re-play its last card; «Дёрнуться» escapes a net but not a ring; «Хламидоспора» lets the
    Fungus skip a round and keep its traps; «Перемешать агар» clears all scent.
Everything is fiction built on real trap biology; no claim about Uzbek species.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from build_companion import find_font, FONT_CANDIDATES_REGULAR, FONT_CANDIDATES_ITALIC  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "output", "experiments", "cardgame")
DPI = 300
MM = DPI / 25.4
CW, CH = int(63 * MM), int(88 * MM)   # poker size
F = find_font(FONT_CANDIDATES_REGULAR)
FI = find_font(FONT_CANDIDATES_ITALIC)
CREAM = (246, 238, 220)
INK = (60, 48, 40)
TERRA = (190, 92, 58)
JADE = (46, 140, 118)
MARIGOLD = (232, 170, 60)
COBALT = (62, 92, 160)


def fnt(px, italic=False):
    return ImageFont.truetype(FI if italic else F, px)


# (side, title, count, rule text, icon)
CARDS = [
    ("ГРИБ", "Кольцо зреет", 4, "Положите перед собой. В следующем раунде переверните: «Кольцо готово». Пока зреет — безопасно.", "ring0"),
    ("ГРИБ", "Сеть", 3, "Если Червь сыграл «Ползти» или «Съесть бактерию» — он прилип. Червь может «Дёрнуться» в следующем раунде.", "net"),
    ("ГРИБ", "Запах", 3, "В следующем раунде Червь обязан сыграть карту с тем же названием, что сейчас, если она есть в руке. Метил-3-метил-2-бутеноат.", "scent"),
    ("ГРИБ", "Хламидоспора", 2, "Пропустите раунд. Все ваши ловушки остаются. Вы умеете ждать три года.", "spore"),
    ("ГРИБ", "Гифа растёт", 4, "Ничего не происходит, но у вас на одну ловушку больше места. Возьмите карту.", "hypha"),
    ("ГРИБ", "Кольцо готово", 2, "Если Червь сыграл «Ползти» или «Обойти» — поймали! Три клетки раздулись внутрь за 0,1–1 с.", "ring1"),
    ("ЧЕРВЬ", "Ползти", 4, "Вы продвигаетесь. Если у Гриба лежит «Кольцо готово» или он сыграл «Сеть» — беда.", "crawl"),
    ("ЧЕРВЬ", "Съесть бактерию", 4, "+1 бактерия. Если Гриб сыграл «Сеть» в этот раунд — вы прилипли, бактерия не считается.", "eat"),
    ("ЧЕРВЬ", "Дёрнуться", 3, "Освобождает от «Сети». Против «Кольца готово» не помогает. Если вы не прилипли — потеря хода.", "wiggle"),
    ("ЧЕРВЬ", "Обойти", 3, "Сбросьте ОДНУ лежащую ловушку Гриба до всех проверок. Ловушка, сыгранная в этот же раунд, ложится после. Нельзя под «Запахом».", "around"),
    ("ЧЕРВЬ", "Перемешать агар", 2, "Все «Запахи» отменяются. Гриб обижен, но жив.", "stir"),
    ("ЧЕРВЬ", "Партнёр!", 2, "Вы учуяли партнёра (а это был гриб). В следующем раунде вы обязаны сыграть «Ползти». +2 бактерии, если выживете.", "mate"),
]


def icon(d, kind, cx, cy, r):
    if kind in ("ring0", "ring1"):
        bul = 0 if kind == "ring0" else 1
        for c in range(3):
            a0 = -90 + c * 120 + 5; a1 = a0 + 110
            w = int(r * (0.32 + 0.3 * bul))
            d.arc((cx - r, cy - r, cx + r, cy + r), a0, a1, fill=JADE if bul else (150, 200, 180), width=w)
        d.line((cx, cy + r, cx, cy + r * 1.5), fill=INK, width=4)
    elif kind == "net":
        for (dx, dy, rx, ry) in [(-0.4, -0.2, 0.5, 0.35), (0.35, -0.3, 0.45, 0.5), (0.0, 0.35, 0.55, 0.3), (-0.2, 0.1, 0.3, 0.25)]:
            d.ellipse((cx + dx * r - rx * r, cy + dy * r - ry * r, cx + dx * r + rx * r, cy + dy * r + ry * r), outline=JADE, width=5)
        for (dx, dy) in [(-0.8, -0.5), (0.7, 0.2), (0.3, 0.6)]:
            d.ellipse((cx + dx * r - 6, cy + dy * r - 6, cx + dx * r + 6, cy + dy * r + 6), fill=COBALT)
    elif kind == "scent":
        for k in range(3):
            d.arc((cx - r * (0.4 + 0.3 * k), cy - r * (0.4 + 0.3 * k), cx + r * (0.4 + 0.3 * k), cy + r * (0.4 + 0.3 * k)), 200, 340, fill=MARIGOLD, width=6)
        d.ellipse((cx - 8, cy + r * 0.3 - 8, cx + 8, cy + r * 0.3 + 8), fill=MARIGOLD)
    elif kind == "spore":
        d.ellipse((cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6), fill=(226, 206, 170), outline=INK, width=6)
        d.ellipse((cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3), outline=INK, width=4)
    elif kind == "hypha":
        d.line((cx - r, cy + r * 0.6, cx - r * 0.3, cy, cx + r * 0.2, cy + r * 0.2, cx + r, cy - r * 0.6), fill=INK, width=6)
        d.line((cx - r * 0.3, cy, cx - r * 0.1, cy - r * 0.7), fill=INK, width=5)
    elif kind in ("crawl", "eat", "wiggle", "around", "mate"):
        import math
        amp = r * (0.45 if kind == "wiggle" else 0.25)
        pts = [(cx - r + i * (2 * r / 24), cy + amp * math.sin(i * (0.7 if kind == "wiggle" else 0.5))) for i in range(25)]
        if kind == "wiggle":
            for k in range(1, 4):
                d.line((cx - r * 0.9, cy - r * 0.9 - k * 6, cx - r * 0.6, cy - r * 0.9 - k * 6), fill=TERRA, width=4)
                d.line((cx + r * 0.6, cy + r * 0.9 + k * 6, cx + r * 0.9, cy + r * 0.9 + k * 6), fill=TERRA, width=4)
        for i, (x, y) in enumerate(pts):
            rr = 4 + 10 * math.sin(math.pi * (0.1 + 0.9 * i / 24))
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=MARIGOLD)
        if kind == "eat":
            for (dx, dy) in [(0.6, -0.6), (0.8, -0.3), (0.4, -0.8)]:
                d.ellipse((cx + dx * r - 7, cy + dy * r - 5, cx + dx * r + 7, cy + dy * r + 5), fill=JADE)
        if kind == "around":
            d.arc((cx - r * 0.3, cy - r * 1.1, cx + r * 0.3, cy - r * 0.5), 0, 360, fill=(150, 200, 180), width=6)
        if kind == "mate":
            d.text((cx + r * 0.7, cy - r * 0.8), "♥", font=fnt(int(r * 0.7)), fill=TERRA, anchor="mm")
    elif kind == "stir":
        d.ellipse((cx - r, cy - r * 0.5, cx + r, cy + r * 0.5), outline=INK, width=5)
        d.line((cx - r * 0.2, cy + r * 0.1, cx + r * 0.6, cy - r * 1.1), fill=INK, width=7)


def card(side, title, text, kind):
    img = Image.new("RGB", (CW, CH), CREAM)
    d = ImageDraw.Draw(img)
    col = JADE if side == "ГРИБ" else TERRA
    d.rectangle((2 * MM, 2 * MM, CW - 2 * MM, CH - 2 * MM), outline=col, width=5)
    d.rectangle((2 * MM, 2 * MM, CW - 2 * MM, 9 * MM), fill=col)
    d.text((CW / 2, 5.5 * MM), side, font=fnt(int(4.2 * MM)), fill=CREAM, anchor="mm")
    d.text((CW / 2, 15 * MM), title, font=fnt(int(5.2 * MM)), fill=INK, anchor="mm")
    icon(d, kind, CW / 2, 36 * MM, 12 * MM)
    # wrapped rule text
    words = text.split(" ")
    lines, cur = [], ""
    f = fnt(int(3.2 * MM), True)
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > CW - 10 * MM:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    y = 54 * MM
    for ln in lines:
        d.text((CW / 2, y), ln, font=f, fill=INK, anchor="ma")
        y += 4.6 * MM
    d.text((CW / 2, CH - 5 * MM), "ЛОВЧЕЕ КОЛЬЦО · художественная игра", font=fnt(int(2.4 * MM)), fill=(140, 120, 100), anchor="mm")
    return img


def back():
    img = Image.new("RGB", (CW, CH), (224, 206, 170))
    d = ImageDraw.Draw(img)
    for y in range(0, CH, int(6 * MM)):
        d.line((0, y, CW, y), fill=(214, 194, 156), width=2)
    cx, cy, r = CW / 2, CH / 2, 14 * MM
    for c in range(3):
        d.arc((cx - r, cy - r, cx + r, cy + r), -90 + c * 120 + 5, -90 + c * 120 + 115, fill=JADE, width=int(5 * MM))
    d.text((cx, CH - 12 * MM), "ЛОВЧЕЕ КОЛЬЦО", font=fnt(int(4.5 * MM)), fill=INK, anchor="mm")
    return img


def rules():
    A4 = (int(210 * MM), int(297 * MM))
    img = Image.new("RGB", A4, CREAM)
    d = ImageDraw.Draw(img)
    d.text((20 * MM, 16 * MM), "ЛОВЧЕЕ КОЛЬЦО", font=fnt(int(12 * MM)), fill=TERRA)
    d.text((20 * MM, 30 * MM), "карточная игра для двоих: Гриб против Червя · 36 карт · 10 минут · прототип, не отыгран за столом", font=fnt(int(4.5 * MM), True), fill=INK)
    lines = [
        ("ЦЕЛЬ", True), ("Червь выигрывает, съев 6 бактерий. Гриб выигрывает, поймав Червя 3 раза (после поимки Червь возрождается, но теряет все бактерии).", False),
        ("", False),
        ("ПОДГОТОВКА", True), ("Каждый берёт свою колоду (18 карт), тасует, держит 5 карт в руке. Ловушки Гриба выкладываются на стол перед ним.", False),
        ("", False),
        ("РАУНД", True), ("1. Оба кладут по карте рубашкой вверх. 2. Открывают одновременно. 3. Разрешают в порядке: сначала «Обойти» (сброс одной лежащей ловушки), затем новые карты Гриба ложатся на стол, затем проверки поимки, затем «Запах». 4. Сыгранные карты в сброс; добирают до 5. Когда колода кончилась, перетасуйте сброс.", False),
        ("", False),
        ("ТАБЛИЦА СТОЛКНОВЕНИЙ", True),
        ("Ползти против Кольца готово (на столе или сыграно) → поймали.", False),
        ("Ползти или Съесть бактерию против Сети (сыграна в этот раунд) → прилип; в следующем раунде только «Дёрнуться» освобождает.", False),
        ("Обойти → сбросьте одну лежащую ловушку Гриба. Не действует под «Запахом».", False),
        ("Запах → в следующем раунде Червь обязан сыграть карту с тем же названием, что сыграл сейчас, если такая есть в руке (иначе любую). «Перемешать агар» снимает все Запахи.", False),
        ("Приоритет: если в один раунд сыграны «Обойти» и «Кольцо готово», Червь сначала сбрасывает одну ЛЕЖАЩУЮ ловушку, а новое кольцо ложится после — поимки нет.", False),
        ("", False),
        ("ПРИМЕР РАУНДА", True),
        ("На столе у Гриба лежит «Кольцо зреет». Гриб играет «Запах», Червь играет «Съесть бактерию». Сети нет — Червь получает +1 (итого 1). Запах действует: в следующем раунде Червь должен снова сыграть «Съесть бактерию», если она в руке. Кольцо переворачивается в «Кольцо готово». Следующий раунд: Гриб играет «Сеть», Червь вынужденно «Съесть бактерию» — прилип, бактерия не считается; дальше его спасёт только «Дёрнуться».", False),
        ("Кольцо зреет → лежит один раунд, потом переворачивается в «Кольцо готово». Пока зреет — безопасно (у настоящего кольца на это уходят часы).", False),
        ("Хламидоспора → Гриб пропускает раунд, ловушки остаются. Гифа растёт → ничего, но Гриб берёт карту.", False),
        ("Партнёр! → Червь обязан сыграть «Ползти» в следующем раунде; если выжил — +2 бактерии. Гриб пахнет партнёром нарочно.", False),
        ("", False),
        ("ПОЧЕМУ ТАК", True),
        ("Кольцо Drechslerella dactyloides зреет часами, а срабатывает за долю секунды: три клетки раздуваются внутрь. Сеть Arthrobotrys oligospora клейкая, из неё можно дёргаться, но редко успешно.", False),
        ("Гриб выделяет летучие вещества, похожие на запах еды и партнёра, и черви ползут на них. В почве гриб переживает голод хламидоспорами. Всё это — общая биология ловчих грибов, а не узбекские виды.", False),
        ("", False),
        ("Название игры и проекта — из диссертации Ф. Х. Файзиевой «Хищные грибы Узбекистана», Ташкент, 1975. Художественная интерпретация.", False),
    ]
    y = 42 * MM
    for text, head in lines:
        if head:
            d.text((20 * MM, y), text, font=fnt(int(5 * MM)), fill=JADE); y += 8 * MM; continue
        if not text:
            y += 3 * MM; continue
        f = fnt(int(3.6 * MM)); words = text.split(" "); cur = ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) > A4[0] - 40 * MM:
                d.text((20 * MM, y), cur, font=f, fill=INK); y += 5.4 * MM; cur = w
            else:
                cur = t
        d.text((20 * MM, y), cur, font=f, fill=INK); y += 6.5 * MM
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    A4 = (int(210 * MM), int(297 * MM))
    deck = []
    for side, title, n, text, kind in CARDS:
        for _ in range(n):
            deck.append(card(side, title, text, kind))
    assert len(deck) == 36, len(deck)
    pages = []
    bk = back()
    for p in range(4):
        sheet = Image.new("RGB", A4, (255, 255, 255))
        sheetb = Image.new("RGB", A4, (255, 255, 255))
        for k in range(9):
            i = p * 9 + k
            x = int(10 * MM + (k % 3) * (CW + 2 * MM)); y = int(12 * MM + (k // 3) * (CH + 2 * MM))
            sheet.paste(deck[i], (x, y))
            # mirrored column order for duplex backs
            xb = A4[0] - x - CW   # mirror around the page centre so duplex backs line up
            sheetb.paste(bk, (xb, y))
        pages += [sheet, sheetb]
    pages.append(rules())
    for page in pages:
        ImageDraw.Draw(page).text((20*MM, A4[1]-9*MM), "Telegram · https://t.me/phys_math_dev", font=fnt(30), fill=INK)
    pdf = os.path.join(OUT, "lovchee_kolco_cards_A4.pdf")
    pages[0].save(pdf, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    strip = Image.new("RGB", (CW // 3 * 6, CH // 3), (255, 255, 255))
    for i, idx in enumerate([0, 4, 7, 15, 18, 26]):
        strip.paste(deck[idx].resize((CW // 3, CH // 3), Image.LANCZOS), (i * (CW // 3), 0))
    strip.save(os.path.join(OUT, "cards_preview.png"))
    pages[-1].resize((827, 1169), Image.LANCZOS).save(os.path.join(OUT, "rules_preview.png"))
    print("[info] wrote", pdf)


if __name__ == "__main__":
    main()
