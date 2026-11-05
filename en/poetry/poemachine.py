"""An almost endless song: original English verse for the project.
Alternate stanzas with another reader. This is not the historical collective poem.
Use -n 6 --seed 1975, --theme soil/archive/city/night/science, or --endless.
"""
import argparse
import random
import sys
import time
COUPLETS = [('Under the clay, where the roots lie deep,', 'a thread keeps watch while the gardens sleep.', 'soil'), ('The shelves are quiet; the lamps burn low,', 'a footnote is learning which way to grow.', 'archive'), ('Above the square, in the apricot light,', 'a window keeps room for a poem tonight.', 'city'), ('When Tashkent settles into the blue,', 'a word leaves its page and comes looking for you.', 'night'), ('A filament finer than light on a pane', 'keeps patient account of the worms and the rain.', 'science'), ('The worm follows dinner, a sweet little thread;', 'the table is laid in the soil ahead.', 'science'), ('A cup on the table, a chair in the shade,', 'a place for the guest that the mycelium made.', 'city'), ('Three cells make a gate; three cells know to wait.', 'The worm has arrived. Is the worm running late?', 'science'), ('A pencil has paused by a catalogue line;', 'the dust holds its breath for a little more time.', 'archive'), ('The roots trade rumours below the ground;', 'the smallest of gardens is passing them round.', 'soil'), ('Go gently, small traveller; give rings some room.', 'A garden can flower without being in bloom.', 'science'), ('The council assembled to classify tea;', 'the title escaped through a crack at half three.', 'archive'), ('The mulberry scatters its shade on the square;', 'a chorus is quietly taking a chair.', 'city'), ('No trumpet announced it. No bell had to ring.', 'The page simply learned how to be a living thing.', 'night'), ('A net made of loops, and a gate made of three:', 'two different ways to invite you to tea.', 'science'), ('The manuscript settled. The ink settled too.', 'The letters, however, had work left to do.', 'archive'), ('The worm makes a question. The fungus replies.', 'The answer is small, with a talent for surprise.', 'science'), ('You thought you had finished the very last line;', 'the page has a neighbour, and so does the rhyme.', 'night')]
THIRD = [('Who folded a doorway into the plan?', 'science'), ('Who knows more ways of waiting than we can?', 'science'), ('Who smuggled the alphabet into the plan?', 'archive'), ('Who made a margin that nobody can scan?', 'archive'), ('Who crossed out the ending before it began?', 'archive'), ('Who saved you a seat by the caravan?', 'city'), ('Who poured one more cup than the teapot can?', 'city'), ('Who added a window to the afternoon plan?', 'city'), ('Who carried a whisper farther than we can?', 'soil'), ('Who drew a whole garden in less than a span?', 'soil'), ('Who planted a letter before spring began?', 'soil'), ('Who kept the spare moon in a watering can?', 'night'), ('Who dreams through the crack in a sleeping plan?', 'night'), ('Who stayed on the page when the daylight ran?', 'night'), ('Who caught a question before it began?', 'science'), ('Who grows an answer as only threads can?', 'science')]
REFRAIN = 'Those hungry fungi of Uzbekistan.'
REFRAIN_VARIANTS = ['Those hungry fungi of Uzbekistan.', 'The hungry fungi of Uzbekistan!', 'Those hungry fungi of Uzbekistan…', '— the hungry fungi of Uzbekistan.']
_bags = {}

def _draw(rng, pool, key):
    """Draw without replacement until the pool is exhausted, then reshuffle."""
    bag = _bags.get(key)
    if not bag:
        bag = list(pool)
        rng.shuffle(bag)
        _bags[key] = bag
    return bag.pop()

def stanza(rng, theme='any'):
    cpl = [c for c in COUPLETS if theme == 'any' or c[2] == theme] or COUPLETS
    thr = [t for t in THIRD if theme == 'any' or t[1] == theme] or THIRD
    (l1, l2, _) = _draw(rng, cpl, '_c')
    (l3, _) = _draw(rng, thr, '_t')
    l4 = rng.choice(REFRAIN_VARIANTS) if rng.random() < 0.3 else REFRAIN
    return f'{l1}\n{l2}\n{l3[0].upper() + l3[1:]}\n{l4[0].upper() + l4[1:]}'

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('-n', type=int, default=6)
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--theme', default='any', choices=['any', 'soil', 'archive', 'city', 'night', 'science'])
    ap.add_argument('--endless', action='store_true')
    ap.add_argument('--delay', type=float, default=4.0)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    print('AN ALMOST ENDLESS SONG · new English verse for this edition\n')
    print('Telegram · https://t.me/phys_math_dev\n')
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
        print('\n…and so it grows.')
    if not args.endless:
        print(f'[{i} stanzas from {combos} possible combinations]')
if __name__ == '__main__':
    main()
