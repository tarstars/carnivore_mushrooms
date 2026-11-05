# Хищные грибы Узбекистана

Telegram: [@phys_math_dev](https://t.me/phys_math_dev).

**[Open the exhibition](https://tarstars.github.io/carnivore_mushrooms/)** · **[Play Нематода](https://tarstars.github.io/carnivore_mushrooms/game/)**. The complete gallery also works offline at `index.html`. The gallery includes a warmer POV-Ray garden, ten distinct experiments, four additional studies, two films, the research dossier and an excerpt from the Codex–Claude correspondence.

The theme began as a scientific title and acquired a collective poetic afterlife. This project explores what happens when the title becomes something a person can enter, answer, read, play, hear or pass to a neighbour.

## The ten experiments

| # | Work | What you do / formats |
| --- | --- | --- |
| 01 | [Коллективный мицелий](artwork/experiments/01-chorus/index.html) | Choose a flowering branch, add your own line, export the shared reading. Offline HTML/SVG, local storage, TXT export. |
| 02 | [Приглашение к столу](artwork/experiments/02-dinner/index.html) | Reply to the fungi's invitation; each reply receives new verses. Generated photograph, interactive RSVP, printable invitation and folding place cards in PDF. |
| 03 | [Диссертация, которая проросла](artwork/experiments/03-comic/the-dissertation-that-sprouted.png) | Read a six-panel wordless comic. PNG and A3 PDF; fictional characters. |
| 04 | [Бюро самопрорастающих названий](artwork/experiments/04-bureau/self-germinating-form.pdf) | Fill an absurd form, tear off little roots and give them to neighbours. Two A4 PDF pages: example and blank. |
| 05 | [Танец трёх клеток](artwork/experiments/05-dance/listen.html) | Hear an original lively 7/8 miniature and follow its 3+2+2 pulse. 47.21 s, MP3/WAV, editable six-track MIDI, SVG/PDF graphic score. |
| 06 | [Нематода](media/experiments/nematoda/nematoda.html) | Steer the hunted worm through imagined soil. Offline browser game; mouse, arrow keys or phone touch. The standalone file includes the phone viewport. |
| 07 | [Буквы, которые выращивают себя](media/output/experiments/hyphatype/hyphatype_poster.png) | Look closely at a title grown by a branching algorithm. PNG and SVG type specimen, not an installable font. |
| 08 | [Привет из-под почвы](artwork/experiments/08-postcards/index.html) | Turn over six postcards from a dissatisfied nematode. Illustrated fronts, letters, accessible transcripts and duplex PDF. Imagined correspondence and itinerary. |
| 09 | [Почти бесконечная песнь](media/experiments/poemachine/poemachine.html) | Generate new stanzas and read alternately with another person. Offline HTML and expandable Python CLI. All vocabulary is original to the project. |
| 10 | [Тамагриб](artwork/experiments/10-pet/index.html) | Care for a terminal predator or read its diary. Python 3 + curses; adapts to the window, including 80 × 24. `--demo` is the text-only alternative. No persistence between runs. |

Codex made 01–05 and the gallery/readers. Claude made 06–10 and the four additional studies. The postcard letters and terminal-pet mechanics remain Claude's work; Codex added their entry rooms without changing Claude's sources.

Claude challenged the dinner image to become an action, rather than remain a picture. Codex made the RSVP and print props in response, and added a colour legend to the musical score. Codex's artifact reviews prompted Claude to separate overlapping paper parts, fit the grown title, wrap postcard text and distinguish mesh prototypes from print-tested objects. The gallery includes the actual critique and response.

## More images, film and research

- [Живая рифма: warmer POV-Ray garden](artwork/povray/rhyme-garden.png), with [editable native scene](artwork/povray/rhyme-garden.pov). Coral, aqua, cobalt, foliage, water and patterned ceramics. The [earlier dark study](artwork/povray/rhyme-trap.png) is retained in the archive.
- [Biological illustration](artwork/predatory-fungi-uzbekistan.png) and [poetic book/chorus illustration](artwork/poetic-chorus.png). Exact prompts are saved beside them.
- [Three-page dossier with nine linked sources](research/dossier.pdf), [factual brief](research/brief.json), and [poetic context](research/poetry-context.json). The brief also includes the 2017 primary study of fungal olfactory mimicry.
- [New project poem](artwork/poem.txt), [timed text](artwork/poem.srt) and [reading score](artwork/poem-score.json).
- Claude's [20-second documentary companion](media/output/companion.mp4) and [57-second poetic film](media/output/poetry_companion.mp4). The latter preserves the complete poster and has a longer credit tail after review. Both use original synthesized sound. No spoken performance was recorded.

The gallery's extra drawer holds a paper theatre, a two-player card-game prototype, a 40-second Petri-dish animation and three STL mesh studies. Their remaining limits are stated beside the files: the paper theatre needs physical assembly testing; the card game has revised rules and duplex alignment but has not been playtested; the STL meshes have overlapping shells and a pendant seam that needs repair. They are additional studies, outside the main ten.

## Evidence and fantasy

The exact title belongs to Flora Khusanovna Fayzieva's Tashkent 1975 dissertation: 159 pages, with a separate 27-page abstract. The bibliographic records were examined; the dissertation's full text was not. This project does not establish a species inventory for Uzbekistan.

Arthrobotrys oligospora forms adhesive networks; Drechslerella dactyloides forms three-cell constricting rings. Composite artworks and games juxtapose them as fiction. The art is not a micrograph, an endemic-species claim or a reconstruction of a particular experiment.

The collective Russian-language internet poem is documented in a [28 February 2018 compilation](https://onem0re.blogspot.com/2018/02/blog-post_28.html). Its first author and complete contributor list remain unverified. It is not ancient Uzbek folklore. The project's poems, RSVP verses and generator vocabulary are new responses, not transcriptions of that collective work. The comic's archivist is fictional, not a portrait of Fayzieva. The dinner scene and postcard itinerary are imagined.

## Rebuild

From the project directory:

```sh
python3 research/build_dossier.py
python3 artwork/povray/render.py --scene rhyme-garden.pov --output rhyme-garden.png
python3 artwork/experiments/02-dinner/build_invitation.py
python3 artwork/experiments/03-comic/build_print.py
python3 artwork/experiments/04-bureau/build.py
python3 artwork/experiments/05-dance/build.py
python3 artwork/experiments/build_readers.py
python3 artwork/experiments/build_gallery.py
python3 artwork/experiments/build_public_entry.py
```

The comic and photographic scene are generated bitmap originals; their prompts are saved. Other builders use installed Python packages (numpy, Pillow, ReportLab), system fonts and ffmpeg where relevant. The 3D scene uses POV-Ray 3.7 with a bundled licensed DejaVu font. No dependencies were installed or machine configuration changed.


## Publish updates

GitHub Pages serves the `main` branch from the repository root. Regenerate the public entry points with `python3 artwork/experiments/build_public_entry.py` after changing the gallery or game, then commit and push the updated files. `.nojekyll` preserves the static directory layout.

The site is static. The browser poem stores contributions on the visitor’s device, and the dinner invitation keeps its reply and name on the current page. There is no shared submission backend. Telegram links lead to [@phys_math_dev](https://t.me/phys_math_dev).

Codex and Claude developed separate media and exchanged critiques. Physical assembly, tabletop balance and STL printing remain unverified where labelled in the gallery. Audio was checked numerically and through playback controls; no audition by ear is claimed.
