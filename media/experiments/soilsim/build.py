#!/usr/bin/env python3
"""Agent-based soil simulation: nematodes, their chemical signals, and a trap-building fungus.

Rules (a schematic of the brief's biology, not a calibrated model):
  * nematodes random-walk, biased toward bacteria (food); each leaves ascaroside signal in a
    diffusing field;
  * hyphal tips random-walk, biased up the signal gradient; a tip forms a trap with probability
    proportional to signal x (1 - local food)  — traps are induced by prey signals under
    nutrient limitation;
  * half the traps are constricting rings (fire instantly when a worm enters), half adhesive
    nets (hold a worm that touches them);
  * a captured worm becomes nutrient: nearby tips branch more for a while.
Output: 40 s MP4 at 1280x720 with a small live HUD. numpy + Pillow + ffmpeg.
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from build_companion import IVORY, GOLD, CELADON, HONEY, TERRACOTTA, TURQUOISE, font, draw_text, with_alpha, mix_rgb  # noqa: E402

# Petri-dish palette: cream agar on a sunlit bench
AGAR = (236, 222, 186)
BENCH = (214, 196, 168)
INK = (58, 46, 36)
HYPHA = (116, 92, 66)
WORM = (196, 92, 44)
RING = (36, 128, 112)
SIGNAL = (240, 170, 60)

OUT = os.path.join(HERE, "..", "..", "output", "experiments", "soilsim")
W, H = 1280, 720
GW, GH = 320, 180          # field resolution
SC = W / GW
DURATION, FPS = 40.0, 30


def blur(f):
    f = f + 0.25 * (np.roll(f, 1, 0) + np.roll(f, -1, 0) + np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4 * f)
    return f


def main(preview=False):
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(3)
    fps = 15 if preview else FPS
    n_frames = int(DURATION * fps)
    signal = np.zeros((GH, GW), np.float32)
    food = np.clip(rng.normal(0.5, 0.25, (GH, GW)), 0, 1).astype(np.float32)
    for _ in range(12):
        food = blur(food)
    DCX, DCY, DR = GW / 2, GH / 2 + 1.5, GH * 0.455

    def inside(x, y):
        return (x - DCX) ** 2 + (y - DCY) ** 2 < (DR - 1.5) ** 2

    def rand_in_dish():
        while True:
            x, y = rng.uniform(0, GW), rng.uniform(0, GH)
            if inside(x, y):
                return x, y
    worms = [{"x": rng.uniform(0, GW), "y": rng.uniform(0, GH), "a": rng.uniform(0, 6.28), "alive": True, "held": 0, "trail": []} for _ in range(70)]
    for wm in worms:
        wm["x"], wm["y"] = rand_in_dish()
    tips = [{"x": rng.uniform(0, GW), "y": rng.uniform(0, GH), "a": rng.uniform(0, 6.28), "boost": 0.0} for _ in range(10)]
    for tp in tips:
        tp["x"], tp["y"] = rand_in_dish()
    segs = []         # (x0,y0,x1,y1) in field coords
    traps = []        # dict: x,y,kind('ring'|'net'),age,fired
    captures = []     # (x,y,t)
    stats = {"captured": 0}

    hud_f = font(int(H * 0.028))
    cap_f = font(int(H * 0.022), italic=True)
    # bench + dish: a round Petri dish, agar inside, soft shadow, sunlight from upper left
    base = Image.new("RGB", (W, H), BENCH)
    bd = ImageDraw.Draw(base)
    for i in range(0, H, 2):
        k = i / H
        bd.line((0, i, W, i), fill=mix_rgb(BENCH, (176, 150, 118), k * 0.6))
    cxd, cyd, rd_ = W / 2, H / 2 + 6, H * 0.47
    bd.ellipse((cxd - rd_ - 10, cyd - rd_ + 14, cxd + rd_ + 10, cyd + rd_ + 22), fill=(170, 146, 112))
    bd.ellipse((cxd - rd_, cyd - rd_, cxd + rd_, cyd + rd_), fill=AGAR, outline=(190, 176, 140), width=3)
    bd.ellipse((cxd - rd_ + 8, cyd - rd_ + 8, cxd + rd_ - 8, cyd + rd_ - 8), outline=(246, 236, 206), width=2)
    bd.ellipse((cxd - rd_ * 0.72, cyd - rd_ * 0.95, cxd - rd_ * 0.25, cyd - rd_ * 0.62), fill=(246, 238, 212))
    dish_mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(dish_mask).ellipse((cxd - rd_ + 4, cyd - rd_ + 4, cxd + rd_ - 4, cyd + rd_ - 4), fill=255)
    dish_mask_np = np.array(dish_mask) > 0

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
           "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", os.path.join(OUT, "soilsim.mp4")]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hy_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # persistent hyphae drawing
    hd = ImageDraw.Draw(hy_layer)

    for fi in range(n_frames):
        t = fi / fps
        dt = 1 / fps
        # --- fields
        signal = blur(signal) * 0.992
        food = np.clip(food + 0.0006, 0, 1)
        # --- worms
        for wm in worms:
            if not wm["alive"]:
                continue
            if wm["held"] > 0:
                wm["held"] -= dt
                wm["a"] += rng.normal(0, 0.8)
                if wm["held"] <= 0:
                    wm["alive"] = False
                continue
            xi, yi = int(wm["x"]) % GW, int(wm["y"]) % GH
            # food gradient
            gx = food[yi, (xi + 2) % GW] - food[yi, (xi - 2) % GW]
            gy = food[(yi + 2) % GH, xi] - food[(yi - 2) % GH, xi]
            want = math.atan2(gy, gx) if abs(gx) + abs(gy) > 1e-3 else wm["a"]
            da = math.atan2(math.sin(want - wm["a"]), math.cos(want - wm["a"]))
            wm["a"] += 0.08 * da + rng.normal(0, 0.35)
            sp = 18 * dt
            nx_, ny_ = wm["x"] + math.cos(wm["a"]) * sp, wm["y"] + math.sin(wm["a"]) * sp
            if not inside(nx_, ny_):
                wm["a"] += math.pi * 0.8 + rng.normal(0, 0.3)
            else:
                wm["x"], wm["y"] = nx_, ny_
            wm["trail"].append((wm["x"], wm["y"]))
            wm["trail"] = wm["trail"][-9:]
            signal[yi, xi] += 2.5
            food[yi, xi] = max(0, food[yi, xi] - 0.02)
            # traps
            for tr in traps:
                if tr["fired"] or tr["age"] < 2.0:
                    continue
                dd = (tr["x"] - wm["x"]) ** 2 + (tr["y"] - wm["y"]) ** 2
                if tr["kind"] == "ring" and dd < 2.2 ** 2:
                    tr["fired"] = True; tr["fire_t"] = t
                    wm["held"] = 2.5; captures.append((wm["x"], wm["y"], t)); stats["captured"] += 1
                    for tp in tips:
                        if (tp["x"] - wm["x"]) ** 2 + (tp["y"] - wm["y"]) ** 2 < 40 ** 2:
                            tp["boost"] = 6.0
                    break
                if tr["kind"] == "net" and dd < 3.5 ** 2:
                    tr["fired"] = True; tr["fire_t"] = t
                    wm["held"] = 4.0; captures.append((wm["x"], wm["y"], t)); stats["captured"] += 1
                    break
        # --- hyphal tips
        new_tips = []
        for tp in tips:
            xi, yi = int(tp["x"]) % GW, int(tp["y"]) % GH
            gx = signal[yi, (xi + 3) % GW] - signal[yi, (xi - 3) % GW]
            gy = signal[(yi + 3) % GH, xi] - signal[(yi - 3) % GH, xi]
            if abs(gx) + abs(gy) > 1e-4:
                want = math.atan2(gy, gx)
                da = math.atan2(math.sin(want - tp["a"]), math.cos(want - tp["a"]))
                tp["a"] += 0.25 * da
            tp["a"] += rng.normal(0, 0.10)
            sp = (9 + 6 * (tp["boost"] > 0)) * dt
            nx = tp["x"] + math.cos(tp["a"]) * sp
            ny = tp["y"] + math.sin(tp["a"]) * sp
            if not inside(nx, ny):
                tp["a"] += math.pi * 0.7
                nx, ny = tp["x"], tp["y"]
            else:
                segs.append((tp["x"], tp["y"], nx, ny))
                hd.line((tp["x"] * SC, tp["y"] * SC, nx * SC, ny * SC), fill=with_alpha(HYPHA, 170), width=2)
            tp["x"], tp["y"] = nx, ny
            tp["boost"] = max(0.0, tp["boost"] - dt)
            # branching
            if rng.random() < dt * (0.15 + 0.9 * (tp["boost"] > 0)) and len(tips) + len(new_tips) < 70:
                new_tips.append({"x": nx, "y": ny, "a": tp["a"] + rng.choice([-1, 1]) * rng.uniform(0.7, 1.4), "boost": 0.0})
            # trap induction: signal high, food low
            s = signal[int(ny) % GH, int(nx) % GW]
            p_trap = dt * 2.5 * min(1.0, s / 1.5) * (1.0 - food[int(ny) % GH, int(nx) % GW])
            if rng.random() < p_trap * 0.5 and len(traps) < 90 and all((tr["x"] - nx) ** 2 + (tr["y"] - ny) ** 2 > 7 ** 2 for tr in traps):
                traps.append({"x": nx, "y": ny, "kind": "ring" if rng.random() < 0.5 else "net", "age": 0.0, "fired": False, "fire_t": 0.0, "rot": rng.uniform(0, 6.28)})
        tips.extend(new_tips)
        for tr in traps:
            tr["age"] += dt
        # replenish worms slowly (immigration)
        if rng.random() < dt * 0.6:
            ex, ey = rand_in_dish()
            worms.append({"x": ex, "y": ey, "a": rng.uniform(0, 6.28), "alive": True, "held": 0, "trail": []})

        # --- render
        img = base.copy()
        fimg = np.array(img, dtype=np.float32)
        # signal: warm amber tint; food: faint olive; both only inside the dish
        sig = np.clip(signal / 4.0, 0, 1)
        sigb = np.array(Image.fromarray((sig * 255).astype(np.uint8), "L").resize((W, H), Image.BILINEAR), dtype=np.float32) / 255
        fdn = np.array(Image.fromarray((food * 255).astype(np.uint8), "L").resize((W, H), Image.BILINEAR), dtype=np.float32) / 255
        m = dish_mask_np
        fimg[m, 0] += 0 * sigb[m]; fimg[m, 1] -= 40 * sigb[m]; fimg[m, 2] -= 110 * sigb[m]
        fimg[m, 0] -= 18 * fdn[m]; fimg[m, 2] -= 40 * fdn[m]
        img = Image.fromarray(np.clip(fimg, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
        img.alpha_composite(hy_layer)
        d = ImageDraw.Draw(img)
        # traps
        for tr in traps:
            x, y = tr["x"] * SC, tr["y"] * SC
            k = min(1.0, tr["age"] / 2.0)
            if tr["kind"] == "ring":
                r = 9 * k
                infl = 0.0 if not tr["fired"] else min(1.0, (t - tr["fire_t"]) / 0.3)
                for c in range(3):
                    a0 = math.degrees(tr["rot"]) + c * 120 + 5; a1 = a0 + 110
                    d.arc((x - r, y - r, x + r, y + r), a0, a1, fill=with_alpha(RING, int(120 + 120 * k)), width=int(2 + 4 * infl))
                if infl > 0:
                    d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=with_alpha(RING, 200))
            else:
                for j in range(3):
                    rx, ry = (7 + 3 * j) * k, (5 + 2 * j) * k
                    d.ellipse((x - rx + j * 4, y - ry - j * 3, x + rx + j * 4, y + ry - j * 3), outline=with_alpha(HYPHA, int(90 + 110 * k)), width=1)
                if tr["fired"]:
                    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=with_alpha(TURQUOISE, 180))
        # worms
        for wm in worms:
            if not wm["alive"]:
                continue
            pts = [(px * SC, py * SC) for (px, py) in wm["trail"]]
            if len(pts) >= 2 and all(abs(pts[i][0] - pts[i - 1][0]) < 60 and abs(pts[i][1] - pts[i - 1][1]) < 60 for i in range(1, len(pts))):
                col = WORM if wm["held"] <= 0 else (120, 40, 20)
                d.line(pts, fill=with_alpha(col, 220), width=4)
                hx, hy = pts[-1]
                d.ellipse((hx - 2.5, hy - 2.5, hx + 2.5, hy + 2.5), fill=with_alpha(col, 240))
        # capture flashes
        for (cx, cy, ct) in captures[-30:]:
            a = max(0.0, 1 - (t - ct) / 1.2)
            if a > 0:
                r = 6 + 18 * (1 - a)
                d.ellipse((cx * SC - r, cy * SC - r, cx * SC + r, cy * SC + r), outline=with_alpha(SIGNAL, int(220 * a)), width=2)
        # HUD
        alive = sum(1 for wm in worms if wm["alive"] and wm["held"] <= 0)
        draw_text(d, (24, 18), f"черви {alive:3d}   кончики гиф {len(tips):3d}   ловушки {len(traps):3d}   поймано {stats['captured']:3d}   t = {t:4.1f} c", hud_f, with_alpha(INK, 230))
        draw_text(d, (W - 24, H - 40), "чашка Петри, агентная модель · составная схема: кольца (Drechslerella-тип) и сети (Arthrobotrys-тип) — разные грибы · сигнал червей (янтарь), еда (олива) · не калиброванная экосистема", cap_f, with_alpha(INK, 200), anchor="ra")
        proc.stdin.write(img.convert("RGB").tobytes())
        if fi % (fps * 5) == 0:
            print(f"\r[soilsim] {fi}/{n_frames}", end="", file=sys.stderr, flush=True)
            img.convert("RGB").save(os.path.join(OUT, f"soilsim_{t:04.0f}s.png"))
    proc.stdin.close(); proc.wait()
    print(f"\n[info] wrote {OUT}/soilsim.mp4; captured {stats['captured']} worms")


if __name__ == "__main__":
    main(preview="--preview" in sys.argv)
