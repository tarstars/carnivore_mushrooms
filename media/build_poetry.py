#!/usr/bin/env python3
"""
Poetic companion builder for «Хищные грибы Узбекистана» — «Рифма — тоже ловчее кольцо».

A typographic reading of the project's original poem (Codex, 2026-11-04) over the portrait
poster input/poetry-illustration.png. There is NO spoken performance: the "voices" of the
reading score are rendered as typography and as synthesized sound (paper, ink, tone clusters).

Outputs (default media/output/):
  poetry_companion.mp4    1280x720 H.264 + AAC, ~54 s (50 s score + 4 s credits)
  poetry_soundtrack.wav   original synthesized soundtrack, 48 kHz stereo 16-bit
  poetry_still_*.png      review stills

Usage:
  python3 media/build_poetry.py media/input/poetry-illustration.png
  python3 media/build_poetry.py --preview            # 640x360, 15 fps draft

Depends on build_companion.py (same directory) for shared helpers; numpy + Pillow + ffmpeg only.
"""
import argparse
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_companion import (  # noqa: E402
    HERE, PROJECT, clamp, seg, smooth, smoother, lerp, with_alpha, mix_rgb, scale_alpha,
    draw_text, font, write_wav,
)

# ----------------------------------------------------------------------------
# Palette: ink, paper, cinnabar, gold (from the poetic poster)
# ----------------------------------------------------------------------------
INK = (14, 11, 10)
INK_WARM = (28, 20, 16)
PAPER = (226, 208, 176)
PAPER_DIM = (160, 144, 118)
CINNABAR = (196, 58, 38)
GOLD = (214, 170, 84)
ASH = (110, 100, 88)

# ----------------------------------------------------------------------------
# The reading score (copied from input/poetry-direction.json; poem © project, Codex 2026)
# ----------------------------------------------------------------------------
CUES = [
    (0.0, 2.0, "archive", "В каталоге было тихо."),
    (2.0, 4.0, "archive", "Ташкент. Семьдесят пятый."),
    (4.0, 6.0, "archive", "Двадцать семь страниц —"),
    (6.0, 9.0, "archive", "и целая ночь между строк."),
    (9.0, 11.0, "first_voice", "Кто-то прочёл заглавие вслух."),
    (11.0, 13.5, "second_voice", "Другой подставил рифму."),
    (13.5, 16.0, "third_voice", "Третий не успел закрыть окно:"),
    (16.0, 19.0, "voices_growing", "из букв уже тянулись гифы."),
    (19.0, 23.0, "chorus", "Хищные грибы Узбекистана."),
    (23.0, 26.0, "reader", "У каждой строчки появился голос."),
    (26.0, 29.0, "reader_and_echo", "У каждого из голосов — сосед."),
    (29.0, 33.0, "reader", "Мы думали, что сочиняем о грибнице."),
    (33.0, 37.0, "page_chorus", "Она писала нами много лет."),
    (37.0, 41.0, "reader", "Рифма — тоже ловчее кольцо."),
    (41.0, 44.0, "reader_close", "Сначала ищешь слово."),
    (44.0, 46.0, "reader_close", "Потом оно"),
    (46.0, 50.0, "chorus_fading", "не отпускает."),
]
SCORE_END = 50.0
CREDITS = [
    ("«Рифма — тоже ловчее кольцо» — стихотворение проекта, 2026", PAPER),
    ("Отклик на сетевую поэму «Хищные грибы Узбекистана», зафиксированную в 2018 г.", PAPER_DIM),
    ("Поэтическая фантазия, не фольклор. Голоса — типографика и синтез.", GOLD),
]
TITLE = "Хищные грибы Узбекистана."

# stanza grouping: which cue indices are shown together, and when the group dissolves
STANZAS = [
    (list(range(0, 4)), 9.0),
    (list(range(4, 8)), 19.0),
    ([8], 23.0),
    (list(range(9, 13)), 37.0),
    (list(range(13, 17)), SCORE_END + 1.0),
]

MONO_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]
_MONO = {}


def mono(size):
    if size not in _MONO:
        for p in MONO_CANDIDATES:
            if os.path.exists(p):
                _MONO[size] = ImageFont.truetype(p, size)
                break
        else:
            _MONO[size] = font(size)
    return _MONO[size]


# ----------------------------------------------------------------------------
# Hyphae growing out of letters
# ----------------------------------------------------------------------------
def make_hyphae(rng, x0, x1, y, n, length, up=True):
    """Deterministic set of branching polylines starting along a baseline [x0,x1] at y."""
    paths = []
    for i in range(n):
        sx = rng.uniform(x0, x1)
        ang = (-math.pi / 2 if up else math.pi / 2) + rng.uniform(-0.9, 0.9)
        pts = [(sx, y)]
        x, yy = sx, y
        total = length * rng.uniform(0.5, 1.3)
        steps = 9
        for s in range(steps):
            ang += rng.uniform(-0.28, 0.28)
            ln = total / steps
            x += math.cos(ang) * ln
            yy += math.sin(ang) * ln
            pts.append((x, yy))
        paths.append(pts)
        if rng.random() < 0.6:
            k = rng.randint(3, 6)
            bx, by = pts[k]
            bang = ang + rng.choice([-1, 1]) * rng.uniform(0.6, 1.3)
            bp = [(bx, by)]
            for s in range(5):
                bang += rng.uniform(-0.4, 0.4)
                bx += math.cos(bang) * total / 12
                by += math.sin(bang) * total / 12
                bp.append((bx, by))
            paths.append(bp)
    return paths


def draw_hyphae(d, paths, grow, color, width, scale=1.0, ox=0.0, oy=0.0):
    """Draw polylines up to fraction `grow` of their length (0..1)."""
    if grow <= 0:
        return
    for pts in paths:
        n = len(pts)
        m = grow * (n - 1)
        k = int(m)
        seq = [(ox + x * scale, oy + y * scale) for (x, y) in pts[: k + 1]]
        if k < n - 1:
            f = m - k
            ax, ay = pts[k]
            bx, by = pts[k + 1]
            seq.append((ox + (ax + (bx - ax) * f) * scale, oy + (ay + (by - ay) * f) * scale))
        if len(seq) >= 2:
            d.line(seq, fill=color, width=width)
            ex, ey = seq[-1]
            d.ellipse((ex - width, ey - width, ex + width, ey + width), fill=color)


# ----------------------------------------------------------------------------
# Renderer
# ----------------------------------------------------------------------------
class PoetryRenderer:
    def __init__(self, poster, w, h, duration, seed=11):
        self.w, self.h = w, h
        self.duration = duration
        self.rng = random.Random(seed)
        # layout: sharp portrait poster panel on the left, text field on the right
        self.margin = int(h * 0.035)
        self.panel_h = h - 2 * self.margin
        self.panel_w = int(self.panel_h * poster.width / poster.height)
        self.panel_x = int(w * 0.035)
        self.text_x0 = self.panel_x + self.panel_w + int(w * 0.04)
        self.text_x1 = w - int(w * 0.04)
        self.text_w = self.text_x1 - self.text_x0
        # poster working copy large enough for the slow zoom
        self.poster_panel = poster.resize((self.panel_w, self.panel_h), Image.LANCZOS)
        # blurred, darkened full-frame background from the poster's own ink and paper
        bg = poster.resize((w, int(w * poster.height / poster.width)), Image.LANCZOS)
        top = (bg.height - h) // 2
        bg = bg.crop((0, top, w, top + h)).filter(ImageFilter.GaussianBlur(w * 0.03))
        bg = Image.blend(bg, Image.new("RGB", (w, h), INK), 0.90)
        self.bg = bg.convert("RGBA")
        # paper grain overlay for the text field (static)
        g = np.array(Image.effect_noise((w, h), 18).convert("L"), dtype=np.float32)
        grain = Image.fromarray(((g - g.mean()) * 0.35 + 128).clip(0, 255).astype(np.uint8), "L")
        self.grain = Image.merge("RGBA", (grain, grain, grain, Image.new("L", (w, h), 28)))
        # fonts
        self.f_archive = mono(int(h * 0.037))
        self.f_voice = [font(int(h * 0.054)), font(int(h * 0.056)), font(int(h * 0.058))]
        self.f_reader = font(int(h * 0.056))
        self.f_reader_close = font(int(h * 0.074))
        self.f_chorus = font(int(h * 0.088))
        self.f_credit = font(int(h * 0.030))
        self.f_credit_i = font(int(h * 0.030), italic=True)
        self.f_small = font(int(h * 0.022), italic=True)
        # title echoes: rotated text sprites placed across the frame, appearing over time
        self.echoes = []
        for i in range(20):
            size = int(h * self.rng.uniform(0.03, 0.085))
            fnt = font(size, italic=self.rng.random() < 0.5)
            col = [PAPER_DIM, CINNABAR, GOLD, ASH][self.rng.randrange(4)]
            tmp = Image.new("RGBA", (int(size * 14), int(size * 1.6)), (0, 0, 0, 0))
            ImageDraw.Draw(tmp).text((4, 2), TITLE, font=fnt, fill=with_alpha(col, 255))
            tmp = tmp.crop(tmp.getbbox() or (0, 0, 1, 1))
            ang = self.rng.uniform(-14, 14)
            spr = tmp.rotate(ang, expand=True, resample=Image.BICUBIC)
            x = self.rng.uniform(-0.05, 0.95) * w
            y = self.rng.uniform(-0.03, 0.97) * h
            t0 = 19.0 + 4.0 * (i / 20) ** 1.4 + self.rng.uniform(0, 0.4)
            self.echoes.append((spr, int(x), int(y), t0, self.rng.uniform(0.10, 0.30)))
        # hyphae for the "гифы" line and the finale (in normalized text-field coordinates)
        self.hyphae_line = make_hyphae(self.rng, 0.0, 1.0, 0.0, 16, 0.7, up=True)
        self.hyphae_final = make_hyphae(self.rng, 0.0, 1.0, 0.0, 22, 1.6, up=True) + \
            make_hyphae(self.rng, 0.0, 1.0, 0.0, 12, 1.1, up=False)
        self.black = Image.new("RGBA", (w, h), (0, 0, 0, 255))

    # ---- poster panel -----------------------------------------------------
    def panel(self, t):
        """The complete poster, never cropped; it floats by a few pixels over the score."""
        return self.poster_panel

    def panel_offset(self, t):
        return (int(round(3 * math.sin(t * 0.21))), int(round(self.margin + 4 * math.sin(t * 0.17 + 1.0))))

    # ---- text field -------------------------------------------------------
    def stanza_alpha(self, t, idx):
        cues, dissolve = STANZAS[idx]
        first = CUES[cues[0]][0]
        a_in = 1.0
        a_out = 1 - smooth(seg(t, dissolve, dissolve + 1.2))
        return a_in * a_out

    def line_alpha(self, t, cue):
        t0, t1, voice, _ = cue
        d = min(1.0, (t1 - t0) * 0.55)
        return smoother(seg(t, t0, t0 + d))

    def draw_text_field(self, lay, t):
        d = ImageDraw.Draw(lay)
        w, h = self.w, self.h
        x0, x1, tw = self.text_x0, self.text_x1, self.text_w
        cx = (x0 + x1) / 2

        # stanza 1: catalogue card, typewriter reveal with a thin rule
        sa = self.stanza_alpha(t, 0)
        if sa > 0:
            y = h * 0.20
            d.rectangle((x0, y - h * 0.06, x1, y - h * 0.06 + 1), fill=with_alpha(PAPER_DIM, int(120 * sa)))
            d.text((x0, y - h * 0.055), "Каталог · Ташкент · 1975 · автореферат · 27 с.", font=self.f_small,
                   fill=with_alpha(ASH, int(200 * sa)))
            for ci in STANZAS[0][0]:
                t0, t1, _, text = CUES[ci]
                if t < t0:
                    continue
                k = seg(t, t0, t0 + (t1 - t0) * 0.75)
                n = int(len(text) * k + 0.999)
                shown = text[:n]
                if n < len(text) and int(t * 3) % 2 == 0:
                    shown += "▏"
                d.text((x0, y), shown, font=self.f_archive, fill=with_alpha(PAPER, int(235 * sa)))
                y += h * 0.072

        # stanza 2: three voices answer one another, then hyphae grow out of the last line
        sa = self.stanza_alpha(t, 1)
        if sa > 0:
            y = h * 0.20
            for j, ci in enumerate(STANZAS[1][0]):
                cue = CUES[ci]
                la = self.line_alpha(t, cue) * sa
                if la <= 0:
                    continue
                text = cue[3]
                if j < 3:
                    fnt = self.f_voice[j]
                    col = [PAPER, GOLD, CINNABAR][j]
                    xx = x0 + tw * [0.0, 0.05, 0.10][j]
                    dy = (1 - la) * h * 0.015
                    draw_text(d, (xx, y + dy), text, fnt, with_alpha(col, int(240 * la)))
                    y += h * 0.1
                else:
                    fnt = self.f_voice[2]
                    xx = x0 + tw * 0.10
                    draw_text(d, (xx, y), text, fnt, with_alpha(PAPER, int(240 * la)))
                    grow = smoother(seg(t, cue[0] + 0.6, cue[1] + 0.8))
                    if grow > 0:
                        hl = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
                        hd = ImageDraw.Draw(hl)
                        tl = d.textlength(text, font=fnt)
                        draw_hyphae(hd, self.hyphae_line, grow, with_alpha(PAPER_DIM, int(210 * sa)), 3,
                                    scale=tl * 2, ox=xx * 2, oy=(y + h * 0.07) * 2)
                        draw_hyphae(hd, self.hyphae_line[::3], grow, with_alpha(GOLD, int(160 * sa)), 2,
                                    scale=tl * 2 * 0.7, ox=xx * 2 + tl * 0.3, oy=(y + h * 0.058) * 2)
                        lay.alpha_composite(hl.reduce(2))
                        d = ImageDraw.Draw(lay)

        # stanza 3: the chorus — the title itself, large, cinnabar, breathing
        sa = self.stanza_alpha(t, 2)
        if sa > 0 and t >= 19.0:
            la = smoother(seg(t, 19.0, 20.2)) * sa
            pulse = 1 + 0.012 * math.sin((t - 19.0) * 2.4)
            fnt = font(int(self.h * 0.088 * pulse))
            words = TITLE.split(" ")
            y = h * 0.30
            for wi, word in enumerate(words):
                ka = smoother(seg(t, 19.0 + 0.35 * wi, 19.9 + 0.35 * wi)) * sa
                col = CINNABAR if wi == 1 else PAPER
                draw_text(d, (cx, y), word, fnt, with_alpha(col, int(250 * ka)), anchor="ma", spacing=h * 0.006)
                y += h * 0.12

        # stanza 4: reader + echo + page chorus
        sa = self.stanza_alpha(t, 3)
        if sa > 0:
            y = h * 0.17
            for j, ci in enumerate(STANZAS[3][0]):
                cue = CUES[ci]
                la = self.line_alpha(t, cue) * sa
                if la <= 0:
                    continue
                text, voice = cue[3], cue[2]
                xx = x0 + tw * 0.04
                if voice == "reader_and_echo":
                    # a faint neighbour copy, offset like a second voice following the first
                    ea = smoother(seg(t, cue[0] + 0.9, cue[1] + 0.3)) * sa
                    draw_text(d, (xx + h * 0.012, y + h * 0.014), text, self.f_reader,
                              with_alpha(GOLD, int(130 * ea)))
                col = PAPER if voice != "page_chorus" else CINNABAR
                draw_text(d, (xx, y), text, self.f_reader, with_alpha(col, int(240 * la)))
                y += h * 0.11

        # stanza 5: closing lines, centred, growing; finale hyphae reach out of «не отпускает.»
        sa = self.stanza_alpha(t, 4)
        if sa > 0:
            y = h * 0.22
            for j, ci in enumerate(STANZAS[4][0]):
                cue = CUES[ci]
                la = self.line_alpha(t, cue) * sa
                if la <= 0:
                    continue
                text, voice = cue[3], cue[2]
                fnt = self.f_reader if j == 0 else self.f_reader_close
                col = PAPER if j < 3 else CINNABAR
                if j == 3:
                    y += h * 0.02
                draw_text(d, (cx, y), text, fnt, with_alpha(col, int(245 * la)), anchor="ma")
                if j == 3:
                    grow = smoother(seg(t, cue[0] + 0.5, cue[1] + 1.5))
                    if grow > 0:
                        hl = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
                        hd = ImageDraw.Draw(hl)
                        tl = d.textlength(text, font=fnt)
                        draw_hyphae(hd, self.hyphae_final, grow, with_alpha(PAPER_DIM, 200), 3,
                                    scale=tl * 2 * 1.1, ox=(cx - tl * 0.55) * 2, oy=(y + h * 0.045) * 2)
                        lay.alpha_composite(hl.reduce(2))
                        d = ImageDraw.Draw(lay)
                y += h * 0.12 if j > 0 else h * 0.10

    # ---- echoes of the title across the whole frame -------------------------
    def draw_echoes(self, lay, t):
        if t < 19.0:
            return
        fade = 1.0
        if t > 23.0:
            fade = 1 - 0.45 * smooth(seg(t, 23.0, 24.5))   # step back so the reader's lines stay legible
        if t > 46.0:
            fade = 1 - smooth(seg(t, 46.0, 50.0)) * 0.85   # chorus_fading
        if t > SCORE_END:
            fade *= 1 - smooth(seg(t, SCORE_END, SCORE_END + 1.0))
        for spr, x, y, t0, amax in self.echoes:
            a = smoother(seg(t, t0, t0 + 1.4)) * amax * fade
            if a <= 0.01:
                continue
            lay.alpha_composite(scale_alpha(spr, a), (x, y))

    # ---- credits ---------------------------------------------------------------
    def draw_credits(self, lay, t):
        k = smoother(seg(t, SCORE_END + 0.6, SCORE_END + 1.6)) * (1 - smooth(seg(t, self.duration - 1.6, self.duration - 0.6)))
        if k <= 0:
            return
        d = ImageDraw.Draw(lay)
        y = self.h * 0.40
        for i, (text, col) in enumerate(CREDITS):
            fnt = self.f_credit if i < 2 else self.f_credit_i
            draw_text(d, (self.w / 2, y), text, fnt, with_alpha(col, int(230 * k)), anchor="ma")
            y += self.h * 0.07

    def frame(self, t):
        w, h = self.w, self.h
        base = self.bg.copy()
        # poster panel with a hairline paper frame; slides away under the credits
        k_panel = 1 - smooth(seg(t, SCORE_END + 0.2, SCORE_END + 1.4))
        if k_panel > 0:
            p = self.panel(t).convert("RGBA")
            ox, oy = self.panel_offset(t)
            px = self.panel_x + ox - int((1 - k_panel) * (self.panel_w + self.panel_x + 10))
            base.alpha_composite(p, (px, oy))
            ImageDraw.Draw(base).rectangle((px - 1, oy - 1, px + self.panel_w, oy + self.panel_h), outline=with_alpha(PAPER_DIM, 110))
        base.alpha_composite(self.grain)
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.draw_echoes(lay, t)
        if t < SCORE_END + 1.2:
            self.draw_text_field(lay, t)
        self.draw_credits(lay, t)
        base.alpha_composite(lay)
        k_fade = smooth(seg(t, 0.0, 1.0)) * (1 - smooth(seg(t, self.duration - 0.8, self.duration)))
        if k_fade < 1.0:
            base = Image.blend(self.black, base, k_fade)
        return base.convert("RGB")


# ----------------------------------------------------------------------------
# Sound: paper, ink and tone clusters — no voice
# ----------------------------------------------------------------------------
VOICE_PITCH = {  # Hz, a D-minor-ish cluster; each voice has its own register
    "archive": 146.83, "first_voice": 220.0, "second_voice": 261.63, "third_voice": 329.63,
    "voices_growing": 392.0, "chorus": 73.42, "reader": 196.0, "reader_and_echo": 233.08,
    "page_chorus": 293.66, "reader_close": 174.61, "chorus_fading": 73.42,
}


def band_noise(rng, n, sr, lo, hi):
    x = rng.normal(0, 1, n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / sr)
    win = np.exp(-0.5 * ((np.log(np.maximum(f, 1)) - math.log(math.sqrt(lo * hi))) / (0.5 * math.log(hi / lo))) ** 2)
    y = np.fft.irfft(X * win, n)
    return y / (np.max(np.abs(y)) + 1e-9)


def make_poetry_soundtrack(duration, sr, seed=23):
    rng = np.random.default_rng(seed)
    n = int(duration * sr)
    t = np.arange(n) / sr
    L = np.zeros(n)
    R = np.zeros(n)

    # 1. ink drone: D1/A1 with slow breathing, very low
    for f0, amp, det, ph in [(36.71, 0.10, 0.12, 0.0), (55.0, 0.06, -0.09, 1.3), (73.42, 0.04, 0.07, 2.2)]:
        s = np.zeros(n)
        for hh in range(1, 5):
            a = amp / hh ** 1.7
            s += a * np.sin(2 * np.pi * f0 * hh * t) + a * np.sin(2 * np.pi * (f0 + det) * hh * t + ph)
        s *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.05 * t + ph)
        L += s
        R += s * 0.95

    # 2. paper room tone, decorrelated
    L += 0.03 * band_noise(rng, n, sr, 120, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    R += 0.03 * band_noise(rng, n, sr, 120, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + 2.0))

    def add_at(t0, sig, pan=0.0):
        i0 = max(0, int(t0 * sr))
        m = min(len(sig), n - i0)
        if m <= 0:
            return
        L[i0:i0 + m] += sig[:m] * (1 - 0.5 * pan)
        R[i0:i0 + m] += sig[:m] * (1 + 0.5 * pan)

    def page_turn(dur=0.45, amp=0.08):
        m = int(dur * sr)
        tt = np.arange(m) / sr
        env = np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 1.5
        return amp * band_noise(rng, m, sr, 900, 5000) * env

    def tone(f, dur, amp, attack=0.08, partials=(1.0, 2.0, 3.0), decay=None):
        m = int(dur * sr)
        tt = np.arange(m) / sr
        env = (1 - np.exp(-tt / attack)) * np.exp(-tt / (decay or dur * 0.6))
        s = np.zeros(m)
        for k, p in enumerate(partials):
            s += (amp / (k + 1) ** 1.3) * np.sin(2 * np.pi * f * p * tt + rng.uniform(0, 6.28))
        return s * env

    def typewriter_clicks(t0, t1, n_chars):
        for i in range(n_chars):
            tc = t0 + (t1 - t0) * 0.75 * i / max(1, n_chars - 1) + rng.uniform(-0.01, 0.01)
            m = int(0.018 * sr)
            tt = np.arange(m) / sr
            click = 0.05 * band_noise(rng, m, sr, 1500, 6000) * np.exp(-tt / 0.004)
            add_at(tc, click, pan=-0.4)

    # 3. cues
    chorus_started = False
    for (t0, t1, voice, text) in CUES:
        f = VOICE_PITCH[voice]
        if voice == "archive":
            typewriter_clicks(t0, t1, len(text))
            add_at(t0, tone(f, 2.5, 0.05, attack=0.3, partials=(1, 2)), pan=-0.3)
        elif voice in ("first_voice", "second_voice", "third_voice"):
            pan = {"first_voice": -0.5, "second_voice": 0.0, "third_voice": 0.5}[voice]
            add_at(t0, page_turn(0.5, 0.05), pan)
            add_at(t0, tone(f, 3.0, 0.07, attack=0.15), pan)
        elif voice == "voices_growing":
            for k in range(7):
                add_at(t0 + 0.3 * k, tone(f * (1 + 0.004 * k) * [1, 1.25, 1.5][k % 3], 2.5, 0.03, attack=0.25),
                       pan=rng.uniform(-0.8, 0.8))
        elif voice in ("chorus", "page_chorus", "chorus_fading"):
            # swelling cluster of detuned partials: many voices saying the title together
            m = int((t1 - t0 + 2.5) * sr)
            tt = np.arange(m) / sr
            swell = np.clip(tt / 1.8, 0, 1) ** 1.6 * np.exp(-np.maximum(0, tt - (t1 - t0)) / 1.2)
            if voice == "chorus_fading":
                swell = np.clip(tt / 1.2, 0, 1) * np.exp(-tt / 2.2)
            base_f = 146.83
            cl = np.zeros(m)
            cr = np.zeros(m)
            for k in range(14):
                fk = base_f * [1, 1.5, 2, 2.4, 3, 4][k % 6] * (1 + rng.normal(0, 0.006))
                ph = rng.uniform(0, 6.28)
                sig = np.sin(2 * np.pi * fk * tt + ph) * (0.028 / (1 + k * 0.12))
                pan = rng.uniform(-0.9, 0.9)
                cl += sig * (1 - 0.5 * pan)
                cr += sig * (1 + 0.5 * pan)
            i0 = int(t0 * sr)
            mm = min(m, n - i0)
            L[i0:i0 + mm] += (cl * swell)[:mm]
            R[i0:i0 + mm] += (cr * swell)[:mm]
            add_at(t0, tone(f, 4.0, 0.12, attack=0.6, partials=(1, 2, 3, 4)))
        elif voice in ("reader", "reader_and_echo", "reader_close"):
            add_at(t0, page_turn(0.4, 0.04), 0.2)
            add_at(t0, tone(f, 3.2, 0.06, attack=0.2), 0.2)
            if voice == "reader_and_echo":
                add_at(t0 + 0.9, tone(f * 1.5, 2.5, 0.04, attack=0.2), -0.5)

    # 4. credits: quiet
    # 5. master
    mix = np.stack([L, R], axis=1)
    mix = np.tanh(mix * 1.5) / 1.5
    fade_in = np.clip(t / 1.5, 0, 1) ** 2
    fade_out = np.clip((duration - t) / 2.5, 0, 1) ** 1.5
    mix *= (fade_in * fade_out)[:, None]
    mix *= 0.50 / (np.max(np.abs(mix)) + 1e-9)
    return (mix * 32767).astype(np.int16)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image", nargs="?", default=None, help="portrait poetry poster (default: media/input/poetry-illustration.png)")
    ap.add_argument("--out", default=os.path.join(HERE, "output"))
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--tail", type=float, default=7.0, help="credits seconds after the 50 s score")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--stills-only", action="store_true")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()

    image = args.image or os.path.join(HERE, "input", "poetry-illustration.png")
    w, h = (640, 360) if args.preview else tuple(int(v) for v in args.size.lower().split("x"))
    fps = 15 if args.preview else args.fps
    duration = SCORE_END + args.tail
    os.makedirs(args.out, exist_ok=True)
    sr = 48000

    if os.path.exists(image):
        poster = Image.open(image).convert("RGB")
        print(f"[info] poster: {image} {poster.size}")
    else:
        print(f"[warn] poster not found at {image!r}; using plain ink placeholder", file=sys.stderr)
        poster = Image.new("RGB", (1086, 1448), INK_WARM)
        ImageDraw.Draw(poster).text((60, 60), "poetry-illustration.png ожидается", font=font(40), fill=PAPER)

    wav_path = os.path.join(args.out, "poetry_soundtrack.wav")
    if not args.no_audio:
        write_wav(wav_path, make_poetry_soundtrack(duration, sr, seed=args.seed), sr)
        print(f"[info] wrote {wav_path}")

    rend = PoetryRenderer(poster, w, h, duration, seed=args.seed)
    for st in (5.0, 15.5, 21.5, 30.0, 41.0, 48.5, 54.0):
        rend.frame(st).save(os.path.join(args.out, f"poetry_still_{st:05.1f}s.png"))
    print(f"[info] wrote 7 review stills to {args.out}")
    if args.stills_only:
        return

    mp4 = os.path.join(args.out, "poetry_companion.mp4")
    n_frames = int(round(duration * fps))
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-"]
    if not args.no_audio:
        cmd += ["-i", wav_path]
    cmd += ["-c:v", "libx264", "-preset", "veryfast" if args.preview else "medium",
            "-crf", "23" if args.preview else "18", "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart"]
    if not args.no_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += [mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(n_frames):
            proc.stdin.write(rend.frame(i / fps).tobytes())
            if i % (fps * 5) == 0:
                print(f"\r[render] {i}/{n_frames}", end="", file=sys.stderr, flush=True)
    finally:
        proc.stdin.close()
        rc = proc.wait()
    print(file=sys.stderr)
    if rc != 0:
        sys.exit(rc)
    print(f"[info] wrote {mp4} ({n_frames} frames @ {fps} fps, {w}x{h}, {duration:.0f}s)")


if __name__ == "__main__":
    main()
