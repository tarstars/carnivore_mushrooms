#!/usr/bin/env python3
"""
3D constricting-ring sequence, ray-traced with POV-Ray from media/pov/trap_anim.pov.

Pipeline:
  1. povray renders N frames at `--render-fps` (default 12) into media/pov/frames/
  2. Pillow overlays the labels and the schematic caption on each frame
  3. ffmpeg motion-interpolates to `--fps` (default 30), encodes H.264 MP4 (silent)
  4. ffmpeg also writes a seamless GIF loop of the inflation beat

Outputs (media/output/):
  trap3d.mp4         1280x720, 30 fps, ~8 s, labelled, silent
  trap3d_clean.mp4   same without labels (for compositing)
  trap3d_loop.gif    ~2.4 s loop around the inflation, 640 px wide
  trap3d_still_*.png review stills

Usage:
  python3 media/build_trap3d.py             # full: 1280x720, 96 povray frames, ~1.5-2.5 h on 20 cores
  python3 media/build_trap3d.py --preview   # 480x270, 24 frames, a few minutes
  python3 media/build_trap3d.py --skip-render   # reuse frames already in media/pov/frames
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_companion import (  # noqa: E402
    HERE, GOLD, IVORY, font, draw_text, with_alpha, seg, smoother,
    LABEL_RING_LAT, LABEL_RING_RU, LABEL_RING_RU2, LABEL_SCHEMA,
)

POV_DIR = os.path.join(HERE, "pov")
SCENE = os.path.join(POV_DIR, "trap_anim.pov")   # overridden by --scene
DURATION = 8.0
INFL_T = (0.46, 0.58)   # clock fraction where the cells inflate (matches the scene)


def render_frames(frames_dir, w, h, n, quality, scene=SCENE):
    os.makedirs(frames_dir, exist_ok=True)
    for f in glob.glob(os.path.join(frames_dir, "f*.png")):
        os.remove(f)
    cmd = ["povray", f"+I{scene}", f"+O{os.path.join(frames_dir, 'f.png')}",
           f"+W{w}", f"+H{h}", "+A0.3" if quality == "full" else "+A0.5", "+R2",
           "+KI0", "+KF1", "+KFI1", f"+KFF{n}", "-D", "-GA", "+Q9", "-V", "+WT12"]
    print("[povray]", " ".join(cmd), flush=True)
    rc = subprocess.call(cmd, cwd=POV_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if rc != 0:
        sys.exit(f"povray exited with {rc}")
    return sorted(glob.glob(os.path.join(frames_dir, "f*.png")))


def label_frame(img, T):
    w, h = img.size
    # ink adapts to the frame: dark brown on bright (warm) renders, gold/ivory on dark ones
    probe = img.convert("L").resize((16, 9)).crop((0, 0, 8, 3))
    bright = sum(probe.getdata()) / (8 * 3) > 128
    GOLD_, IVORY_ = ((120, 70, 30), (58, 44, 32)) if bright else (GOLD, IVORY)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f_lat = font(int(h * 0.046), italic=True)
    f_ru = font(int(h * 0.032))
    f_sm = font(int(h * 0.026), italic=True)
    k = smoother(seg(T, 0.02, 0.12))
    lx, ly = w * 0.05, h * 0.07
    draw_text(d, (lx, ly), LABEL_RING_LAT, f_lat, with_alpha(GOLD_, 235 * k))
    d.line((lx, ly + h * 0.058, lx + w * 0.30, ly + h * 0.058), fill=with_alpha(GOLD_, 120 * k), width=1)
    draw_text(d, (lx, ly + h * 0.065), LABEL_RING_RU, f_ru, with_alpha(IVORY_, 215 * k))
    k2 = smoother(seg(T, INFL_T[0] + 0.02, INFL_T[0] + 0.10))
    if k2 > 0:
        draw_text(d, (lx, ly + h * 0.11), LABEL_RING_RU2, f_ru, with_alpha(IVORY_, 215 * k2))
    draw_text(d, (w * 0.96, h * 0.92), LABEL_SCHEMA + " · 3D-рендер", f_sm, with_alpha(IVORY_, 170 * k), anchor="ra")
    return Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB")


def encode(frames_glob_dir, pattern, render_fps, out_fps, mp4, w):
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-framerate", str(render_fps), "-i", os.path.join(frames_glob_dir, pattern),
           "-vf", f"minterpolate=fps={out_fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=yuv420p",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-movflags", "+faststart", mp4]
    subprocess.check_call(cmd)


def gif_loop(frames_dir, pattern, render_fps, n, gif, width=640):
    # frames around the inflation, played forward then backward -> seamless loop
    i0 = max(1, int(INFL_T[0] * n) - 4)
    i1 = min(n, int(INFL_T[1] * n) + 8)
    seq = list(range(i0, i1 + 1)) + list(range(i1 - 1, i0, -1))
    tmp = os.path.join(frames_dir, "loop")
    os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(os.path.join(tmp, "*.png")):
        os.remove(f)
    for j, i in enumerate(seq):
        shutil.copy(os.path.join(frames_dir, pattern % i), os.path.join(tmp, f"l{j:03d}.png"))
    fps = render_fps * 2
    subprocess.check_call(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                           "-framerate", str(render_fps), "-i", os.path.join(tmp, "l%03d.png"),
                           "-vf", f"minterpolate=fps={fps}:mi_mode=mci,scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=sierra2_4a",
                           "-loop", "0", gif])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(HERE, "output"))
    ap.add_argument("--size", default="1280x720")
    ap.add_argument("--render-fps", type=int, default=12)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--scene", default=SCENE, help="POV scene file (e.g. media/pov/trap_anim_warm.pov)")
    ap.add_argument("--tag", default="", help="suffix for output names and frames dir, e.g. _warm")
    args = ap.parse_args()

    w, h = (480, 270) if args.preview else tuple(int(v) for v in args.size.lower().split("x"))
    render_fps = 3 if args.preview else args.render_fps
    n = int(DURATION * render_fps)
    frames_dir = os.path.join(POV_DIR, ("frames_preview" if args.preview else "frames") + args.tag)
    os.makedirs(args.out, exist_ok=True)

    if args.skip_render:
        frames = sorted(glob.glob(os.path.join(frames_dir, "f*.png")))
        n = len(frames)
    else:
        frames = render_frames(frames_dir, w, h, n, "preview" if args.preview else "full", scene=args.scene)
    if len(frames) != n:
        sys.exit(f"expected {n} frames, found {len(frames)}")
    print(f"[info] {n} povray frames at {w}x{h}", flush=True)

    # labelled copies
    lab_dir = os.path.join(frames_dir, "labelled")
    os.makedirs(lab_dir, exist_ok=True)
    digits = len(os.path.basename(frames[0])) - 5
    pattern_raw = "f%0" + str(digits) + "d.png"
    for i, fp in enumerate(frames, start=1):
        T = (i - 1) / max(1, n - 1)
        label_frame(Image.open(fp), T).save(os.path.join(lab_dir, f"g{i:03d}.png"))

    tag = ("_preview" if args.preview else "") + args.tag
    mp4 = os.path.join(args.out, f"trap3d{tag}.mp4")
    mp4_clean = os.path.join(args.out, f"trap3d_clean{tag}.mp4")
    encode(lab_dir, "g%03d.png", render_fps, args.fps, mp4, w)
    encode(frames_dir, pattern_raw, render_fps, args.fps, mp4_clean, w)
    gif = os.path.join(args.out, f"trap3d_loop{tag}.gif")
    gif_loop(frames_dir, pattern_raw, render_fps, n, gif, width=min(640, w))
    for T in (0.0, 0.3, 0.47, 0.6, 1.0):
        i = 1 + int(round(T * (n - 1)))
        shutil.copy(os.path.join(lab_dir, f"g{i:03d}.png"), os.path.join(args.out, f"trap3d_still{tag}_{T:.2f}.png"))
    print(f"[info] wrote {mp4}, {mp4_clean}, {gif}")


if __name__ == "__main__":
    main()
