#!/usr/bin/env python3
"""ТАМАГРИБ — a predatory fungus as a terminal pet.

You keep an Arthrobotrys / Drechslerella culture in a Petri dish drawn in your terminal.
It needs worms (prey), a little patience (rings take hours to mature), and attention.
It builds traps when it is hungry and smells prey, gets bored, keeps a diary, and will
eventually offer you a doctorate.

Keys:  w  release a worm into the dish      s  stir the agar (resets smells)
       r  give it a rest (skip 1 hour)       d  read the diary
       q  quit (the culture survives as chlamydospores)

Runs anywhere with python3 and curses. Pure standard library. Humorous fiction with a
few real facts; not a simulation of a real organism.
"""
import curses
import random
import time

DIARY_LINES = [
    "День {d}. Пахнет червём. Ещё не пахнет, но будет.",
    "День {d}. Построил кольцо. Жду. Умею ждать: пять часов — пустяк.",
    "День {d}. Хозяин мешал агар ложкой. Запахи сбились. Обидно.",
    "День {d}. Поймал. Три клетки раздулись за долю секунды. Красиво сделал.",
    "День {d}. Еды много, ловушки не нужны. Отдыхаю. Расту во все стороны.",
    "День {d}. Еды мало. Чувствую сигналы червей. Плету сеть, клей сохнет.",
    "День {d}. Думаю о диссертации. Сто пятьдесят девять страниц обо мне. Ташкент, 1975.",
    "День {d}. Хозяин ушёл. Превращаюсь в хламидоспоры. Вернётся — прорасту.",
    "День {d}. Червь обошёл кольцо. Умный. Запомню его запах.",
    "День {d}. Выделил метил-3-метил-2-бутеноат. Пахнет, говорят, как партнёр. Не мне судить.",
]

MOODS = ["доволен", "ждёт", "голоден", "занят плетением", "задумчив", "торжествует", "скучает"]


class Fungus:
    def __init__(self):
        self.hour = 0
        self.food = 4.0          # nutrient reserve
        self.traps = []          # dict(kind, x, y, born, fired)
        self.worms = []          # dict(x, y, dx, dy, born)
        self.hyphae = set()      # cells occupied
        self.caught = 0
        self.diary = ["День 0. Меня посеяли. Чашка Петри, агар, тишина."]
        self.mood = "задумчив"
        self.title = "культура"
        self.signal = 0.0
        self.rng = random.Random()
        self.w, self.h = 60, 18
        self.fit(60, 18)

    def fit(self, w, h):
        """Shrink the dish to the terminal (called with the real window size); hyphae outside are dropped."""
        self.w, self.h = max(30, min(60, w)), max(9, min(18, h))
        self.hyphae = {p for p in self.hyphae if self.inside(*p)} or {(self.w // 2, self.h // 2)}
        self.traps = [t for t in self.traps if self.inside(t["x"], t["y"])]
        self.worms = [wm for wm in self.worms if self.inside(wm["x"], wm["y"])]
        cx, cy = self.w // 2, self.h // 2
        for i in range(-2, 3):
            self.hyphae.add((cx + i, cy))

    def day(self):
        return self.hour // 24

    def log(self, s):
        self.diary.append(s.format(d=self.day()))
        self.diary = self.diary[-40:]

    def inside(self, x, y):
        rx, ry = self.w / 2 - 1, self.h / 2 - 1
        return ((x - self.w / 2) / rx) ** 2 + ((y - self.h / 2) / ry) ** 2 < 1

    def tick(self):
        self.hour += 1
        self.food = max(0.0, self.food - 0.08)
        # grow hyphae: more when fed
        growth = 1 + int(self.food > 2) + int(self.food > 5)
        for _ in range(growth):
            if not self.hyphae:
                break
            x, y = self.rng.choice(tuple(self.hyphae))
            dx, dy = self.rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0)])
            nx, ny = x + dx, y + dy
            if self.inside(nx, ny):
                self.hyphae.add((nx, ny))
        # signal from worms
        self.signal = min(5.0, self.signal * 0.85 + 0.6 * len(self.worms))
        # trap induction: hungry + signal
        if self.signal > 0.8 and self.food < 3.5 and self.rng.random() < 0.35 and len(self.traps) < 14:
            x, y = self.rng.choice(tuple(self.hyphae))
            kind = "ring" if self.rng.random() < 0.5 else "net"
            self.traps.append({"kind": kind, "x": x, "y": y, "born": self.hour, "fired": False})
            self.log("День {d}. Построил " + ("кольцо. Созреет часов через пять." if kind == "ring" else "клейкую сеть. Пусть сохнет."))
        # worms move
        for wm in self.worms:
            if self.rng.random() < 0.4:
                wm["dx"], wm["dy"] = self.rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            nx, ny = wm["x"] + wm["dx"], wm["y"] + wm["dy"]
            if self.inside(nx, ny):
                wm["x"], wm["y"] = nx, ny
            else:
                wm["dx"], wm["dy"] = -wm["dx"], -wm["dy"]
        # captures
        for tr in self.traps:
            if tr["fired"]:
                continue
            mature = (self.hour - tr["born"]) >= (5 if tr["kind"] == "ring" else 3)
            if not mature:
                continue
            for wm in list(self.worms):
                if abs(wm["x"] - tr["x"]) <= 1 and abs(wm["y"] - tr["y"]) <= 1:
                    tr["fired"] = True
                    self.worms.remove(wm)
                    self.caught += 1
                    self.food += 3.0
                    if tr["kind"] == "ring":
                        self.log("День {d}. Кольцо сработало: три клетки внутрь, 0,1–1 с. Поймал.")
                    else:
                        self.log("День {d}. Сеть схватила. Прорастаю внутрь, переварю за сутки.")
                    break
        # worms starve the dish a little, then leave
        self.worms = [wm for wm in self.worms if self.hour - wm["born"] < 30]
        # mood
        if self.food > 5:
            self.mood = "доволен"
        elif self.signal > 1.5 and self.food < 3:
            self.mood = "занят плетением" if self.rng.random() < 0.5 else "голоден"
        elif self.traps and not self.worms:
            self.mood = "ждёт"
        else:
            self.mood = self.rng.choice(["задумчив", "скучает", "ждёт"])
        if self.hour % 24 == 0:
            self.log(self.rng.choice(DIARY_LINES))
        # titles
        if self.caught >= 3:
            self.title = "кандидат"
        if self.caught >= 8:
            self.title = "доктор биологических наук"
        if self.caught >= 15:
            self.title = "академик АН УзССР (почётно)"

    def release_worm(self):
        for _ in range(50):
            x, y = self.rng.randint(1, self.w - 2), self.rng.randint(1, self.h - 2)
            if self.inside(x, y) and (x, y) not in self.hyphae:
                self.worms.append({"x": x, "y": y, "dx": 1, "dy": 0, "born": self.hour})
                return
        self.worms.append({"x": self.w // 2, "y": 1, "dx": 1, "dy": 0, "born": self.hour})

    def stir(self):
        self.signal = 0.0
        self.log("День {d}. Агар перемешали. Все запахи — в кашу.")
        self.mood = "скучает"


def put(stdscr, y, x, text, attr=0):
    """addstr that never throws: clips to the window and ignores the bottom-right cell."""
    H, W = stdscr.getmaxyx()
    if y < 0 or y >= H or x >= W:
        return
    text = text[: max(0, W - x - 1)]
    if text:
        try:
            stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass


def draw(stdscr, f, msg):
    stdscr.erase()
    H, W = stdscr.getmaxyx()
    ox, oy = 2, 2
    if W < 44 or H < 14:
        put(stdscr, 0, 1, "ТАМАГРИБ: окно слишком маленькое.")
        put(stdscr, 1, 1, f"Нужно хотя бы 44x14, сейчас {W}x{H}.")
        put(stdscr, 2, 1, "Растяните терминал или нажмите q.")
        stdscr.refresh()
        return
    put(stdscr, 0, 2, f"ТАМАГРИБ · {f.title} · час {f.hour} (день {f.day()}) · {f.mood}")
    put(stdscr, 1, 2, f"еда {'█' * int(min(10, f.food))}{'·' * (10 - int(min(10, f.food)))} сигнал {'~' * int(f.signal)} поймано {f.caught} ловушек {sum(1 for t in f.traps if not t['fired'])}")
    # dish
    for y in range(f.h):
        for x in range(f.w):
            inside = f.inside(x, y)
            edge = inside and not (f.inside(x + 1, y) and f.inside(x - 1, y) and f.inside(x, y + 1) and f.inside(x, y - 1))
            ch = " "
            if edge:
                ch = "·"
            elif (x, y) in f.hyphae:
                ch = "-" if (x + y) % 3 else "~"
            put(stdscr, oy + y, ox + x, ch)
    for tr in f.traps:
        mature = (f.hour - tr["born"]) >= (5 if tr["kind"] == "ring" else 3)
        ch = ("O" if mature else "o") if tr["kind"] == "ring" else ("#" if mature else "+")
        if tr["fired"]:
            ch = "@" if tr["kind"] == "ring" else "%"
        put(stdscr, oy + tr["y"], ox + tr["x"], ch, curses.A_BOLD)
    for wm in f.worms:
        put(stdscr, oy + wm["y"], ox + wm["x"], "S", curses.A_BOLD)
    y0 = oy + f.h + 1
    put(stdscr, y0, 2, "o зреет O готово + сеть сохнет # сеть готова @/% сработало S червь - гифы")
    put(stdscr, y0 + 1, 2, "w червь  s мешать  r час  d дневник  q выйти")
    put(stdscr, y0 + 2, 2, msg)
    for i, line in enumerate(f.diary[-3:]):
        put(stdscr, y0 + 3 + i, 2, line)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    f = Fungus()
    H, W = stdscr.getmaxyx()
    f.fit(W - 6, H - 9)
    msg = "Культура посеяна. w — выпустить червя. Кольца зреют пять часов."
    last = time.time()
    show_diary = False
    while True:
        try:
            k = stdscr.getkey()
        except curses.error:
            k = None
        if k == "q":
            f.log("День {d}. Хозяин ушёл. Хламидоспоры. До встречи.")
            break
        elif k == "w":
            f.release_worm(); msg = "Червь выпущен. Гриб принюхивается."
        elif k == "s":
            f.stir(); msg = "Агар перемешан. Запахи сброшены."
        elif k == "r":
            f.tick(); msg = "Час прошёл."
        elif k == "d":
            show_diary = not show_diary
        elif k == "KEY_RESIZE":
            H, W = stdscr.getmaxyx()
            f.fit(W - 6, H - 9)
        if time.time() - last > 1.2:
            f.tick(); last = time.time()
        if show_diary:
            stdscr.erase()
            put(stdscr, 0, 2, "ДНЕВНИК КУЛЬТУРЫ (d — назад)")
            H, W = stdscr.getmaxyx()
            for i, line in enumerate(f.diary[-(H - 3):]):
                put(stdscr, 2 + i, 2, line)
            stdscr.refresh()
        else:
            draw(stdscr, f, msg)
        time.sleep(0.05)
    return f


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        # headless demo: 60 hours with worms released periodically; print the diary
        f = Fungus()
        for h in range(72):
            if h % 9 == 0:
                f.release_worm()
            f.tick()
        print("\n".join(f.diary))
        print(f"\n[поймано {f.caught}, звание: {f.title}]")
    else:
        fungus = curses.wrapper(main)
        print("\n".join(fungus.diary[-6:]))
        print(f"\nПоймано червей: {fungus.caught}. Звание: {fungus.title}.")
