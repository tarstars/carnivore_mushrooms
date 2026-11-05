#!/usr/bin/env python3
"""«Почти бесконечная песнь» — a combinatorial quatrain machine.

Every stanza ends on «Узбекистана». Lines 1–2 rhyme with each other (AA), line 3 rhymes with
the refrain (-ана). All lines below are original, written for this project; the machine only
recombines them. It nods to the collective internet poem around the 1975 dissertation title
without quoting a single line of it.

Usage:
  python3 poemachine.py                # 6 stanzas
  python3 poemachine.py -n 12 --seed 7
  python3 poemachine.py --endless      # one stanza every few seconds until Ctrl-C
  python3 poemachine.py --theme soil   # soil | archive | city | night | science | any
"""
import argparse
import random
import sys
import time

# Rhymed couplets (lines 1–2). Each tuple: (line1, line2, theme)
COUPLETS = [
    ("Под коркой глины, где не слышен ветер,", "где корень дышит и никто не светел,", "soil"),
    ("В пыли архива, в шелесте бумаги,", "в чернильных реках, в выцветшей отваге,", "archive"),
    ("Над Регистаном плавится жара,", "и тень минарета ползёт со двора,", "city"),
    ("Когда к полуночи стихает Ташкент", "и лампа над столом даёт последний свет,", "night"),
    ("Нить тоньше волоса, прозрачнее стекла,", "и терпелива, как сама зола,", "science"),
    ("Червь ищет пищу, слепо и упрямо,", "и ползёт на запах, ползёт прямо,", "science"),
    ("В чайхане старик рассказывал без спешки,", "ломая лепёшку, двигая орешки,", "city"),
    ("Три клетки ждут, не двигаясь ни разу,", "созреют за ночь и сработают сразу,", "science"),
    ("Страница сто сорок девять, список книг,", "и чей-то карандашный тихий штрих,", "archive"),
    ("Между арыком и сухой чинарой,", "где воздух пахнет пылью и отарой,", "soil"),
    ("Вернись домой, не задевай петли,", "не трогай стенок, что внутри росли,", "science"),
    ("Учёный совет собрался в среду,", "налили чай и продолжили беседу,", "archive"),
    ("Сквозь дырочки сетчатой тени тута", "в полдень ложится золотая смута,", "city"),
    ("Не хоронили, не рубили, не сжигали,", "а просто ждали, терпеливо ждали,", "night"),
    ("В одной горсти земли их больше, чем людей", "во всех столицах всех семи морей,", "science"),
    ("Диссертация лежит на правах рукописи,", "и буквы в ней не выцвели, не скисли,", "archive"),
    ("У кольца три щеки, и каждая щека", "ждёт прикосновения червяка,", "science"),
    ("Когда ты думаешь, что всё уже прочёл,", "за строчкой строчка, как за пчёлкой пчёл,", "night"),
]

# Line 3: rhymes with «Узбекистана» (all end on -ана)
THIRD = [
    ("раскрывают рты посреди тумана", "night"),
    ("просыпаются раньше муэдзина и чабана", "city"),
    ("не смотрятся в зеркало старого дивана", "archive"),
    ("тянут нити тоньше паутины и обмана", "science"),
    ("ждут под корнями старого платана", "soil"),
    ("обнимают червя три раза, как три брата из дастана", "science"),
    ("не знают ни границы, ни тарана", "soil"),
    ("растут из буквы, из строки, из плана", "archive"),
    ("молчат, как рыба на столе у Мирзо-Хана", "city"),
    ("делят ночь на до и после капкана", "night"),
    ("пьют росу из глиняного чана", "soil"),
    ("просачиваются в сон сквозь трещины экрана", "night"),
    ("сидят в земле, как косточка в тутовнике — не рано", "soil"),
    ("ждут того, кто проползёт из-за бархана", "soil"),
    ("согласованы учёным советом, без изъяна", "archive"),
    ("ловят то, что ловится, без гнева и без плана", "science"),
]

REFRAIN = "хищные грибы Узбекистана."
REFRAIN_VARIANTS = [
    "хищные грибы Узбекистана.",
    "хищные грибы Узбекистана!",
    "хищные грибы Узбекистана…",
    "— хищные грибы Узбекистана.",
]


_bags = {}


def _draw(rng, pool, key):
    """Draw without replacement until the pool is exhausted, then reshuffle."""
    bag = _bags.get(key)
    if not bag:
        bag = list(pool)
        rng.shuffle(bag)
        _bags[key] = bag
    return bag.pop()


def stanza(rng, theme="any"):
    cpl = [c for c in COUPLETS if theme == "any" or c[2] == theme] or COUPLETS
    thr = [t for t in THIRD if theme == "any" or t[1] == theme] or THIRD
    l1, l2, _ = _draw(rng, cpl, "_c")
    l3, _ = _draw(rng, thr, "_t")
    l4 = rng.choice(REFRAIN_VARIANTS) if rng.random() < 0.3 else REFRAIN
    # the refrain is a sentence subject: capitalise the third line as a clause start
    return f"{l1}\n{l2}\n{l3[0].upper() + l3[1:]}\n{l4[0].upper() + l4[1:]}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", type=int, default=6)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--theme", default="any", choices=["any", "soil", "archive", "city", "night", "science"])
    ap.add_argument("--endless", action="store_true")
    ap.add_argument("--delay", type=float, default=4.0)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    print("ПОЧТИ БЕСКОНЕЧНАЯ ПЕСНЬ · машина строф · все строки оригинальные\n")
    print("Telegram · https://t.me/phys_math_dev\n")
    combos = len(COUPLETS) * len(THIRD) * len(REFRAIN_VARIANTS)
    i = 0
    try:
        while args.endless or i < args.n:
            print(stanza(rng, args.theme))
            print()
            i += 1
            if args.endless:
                sys.stdout.flush()
                time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\n…и так далее.")
    if not args.endless:
        print(f"[{i} строф из {combos} возможных сочетаний]")


if __name__ == "__main__":
    main()
