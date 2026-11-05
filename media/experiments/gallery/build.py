#!/usr/bin/env python3
"""Builds a single-file HTML gallery of Claude's night-lab lanes with embedded previews.

Previews are downscaled JPEGs embedded as data URIs so the page needs no server. The game is
linked as a live artifact. Run after the experiments have rendered; re-run to refresh.
"""
import base64
import io
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, "..", "..")
OUTX = os.path.join(MEDIA, "output", "experiments")
OUT = os.path.join(MEDIA, "output")


def data_uri(path, width=960, quality=78):
    if not os.path.exists(path):
        return ""
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def text_of(path, n=None):
    if not os.path.exists(path):
        return ""
    t = open(path, encoding="utf-8").read()
    return t if n is None else "\n".join(t.splitlines()[:n])


LANES = [
    dict(key="nematoda", verb="играть", title="Нематода", kind="браузерная игра",
         img=None, link="../nematoda/nematoda.html",
         text="Вы — червь. Запах гриба тянет курс к ловушкам: бутоны колец безопасны, зрелые срабатывают мгновенно, сети держат, пока не дёрнетесь. Когда еды мало, сети растут быстрее — как в брифе про индукцию ловушек.",
         cmd="открыть experiments/nematoda/index.html"),
    dict(key="cardgame", verb="играть вдвоём", title="Ловчее кольцо", kind="карточная игра, печать",
         img=os.path.join(OUTX, "cardgame", "cards_preview.png"), img2=os.path.join(OUTX, "cardgame", "rules_preview.png"),
         text="Гриб против Червя: 36 карт, одновременный скрытый ход, таблица столкновений. Кольцо зреет ход, запах заставляет повторять карту, дёргаться можно из сети, но не из кольца.",
         cmd="python3 media/experiments/cardgame/build.py → lovchee_kolco_cards_A4.pdf"),
    dict(key="papertheatre", verb="сделать руками", title="Бумажный театр", kind="print-and-play, 4 листа A4",
         img=os.path.join(OUTX, "papertheatre", "sheet3_preview.png"), img2=os.path.join(OUTX, "papertheatre", "sheet2_preview.png"),
         text="Четыре листа: задник с окном сцены, пластина с прорезями, три полумесяца с язычками, лента-червь. Тянешь язычки — клетки сдвигаются внутрь и зажимают бумажного червя. Та же механика, что у настоящего кольца, только пальцами.",
         cmd="python3 media/experiments/papertheatre/build.py → papertheatre_A4.pdf"),
    dict(key="postcards", verb="читать", title="Привет из-под почвы", kind="шесть открыток, дуплекс A6",
         img=os.path.join(OUTX, "postcards", "fronts_sheet.png"), img2=os.path.join(OUTX, "postcards", "card3_back.png"),
         text="Червь путешествует по вехам науки о ловчих грибах: Ашхабад 1958, Ташкент 1975, Баку 1979, Новосибирск 1990, Пасадена 2017, Пекин 2023. Места и даты реальные, переписка вымышленная.",
         cmd="python3 media/experiments/postcards/build.py → postcards_A4_duplex.pdf"),
    dict(key="tamagrib", verb="держать дома", title="Тамагриб", kind="питомец в терминале",
         img=os.path.join(OUTX, "tamagrib", "screen.png"), pre=text_of(os.path.join(OUTX, "tamagrib", "demo_diary.txt"), 8),
         text="Хищный гриб в чашке Петри из символов. Кормите червями (w), мешайте агар (s), ждите (r), читайте дневник (d). Кольца зреют пять часов; за восемь поимок — докторская.",
         cmd="python3 media/experiments/tamagrib/tamagrib.py"),
    dict(key="poemachine", verb="читать вслух вдвоём", title="Почти бесконечная песнь", kind="машина строф",
         img=None, pre=text_of(os.path.join(OUTX, "poemachine", "sample_seed1975.txt"), 12),
         text="18 оригинальных двустиший × 16 третьих строк на -ана. Каждая строфа кончается на «Узбекистана». Есть офлайн-страница с кнопкой «Ещё строфу»; в режиме --endless двое читают по очереди. Ни одной строки сетевой поэмы здесь нет.",
         cmd="открыть experiments/poemachine/poemachine.html · python3 media/experiments/poemachine/poemachine.py --endless"),
    dict(key="ringstl", verb="держать в руке", title="Кольцо для печати", kind="STL, 40 мм",
         img=os.path.join(OUTX, "ringstl", "ringstl_preview.png"),
         text="Три файла: кольцо в покое, клетки раздуты внутрь, подвеска с петлёй. Это прототипы сетки: оболочки клеток перекрываются, не объединены; перед печатью нужен слайсер и проверка. На принтере не проверено.",
         cmd="python3 media/experiments/ringstl/build.py → ring_rest.stl, ring_inflated.stl, ring_pendant.stl"),
    dict(key="soilsim", verb="смотреть", title="Чашка Петри", kind="агентная модель, 40 с",
         img=os.path.join(OUTX, "soilsim", "soilsim_0035s.png"),
         text="Черви оставляют сигнал, гифы растут на него, ловушки появляются там, где сигнал высок, а еды мало. Составная схема двух типов ловушек разных грибов, не калиброванная экосистема.",
         cmd="python3 media/experiments/soilsim/build.py → soilsim.mp4"),
    dict(key="hyphatype", verb="смотреть / печатать", title="Гифальный шрифт", kind="типографика, PNG + SVG",
         img=os.path.join(OUTX, "hyphatype", "hyphatype_preview.png"),
         text="Буквы заглавия выращены алгоритмом колонизации пространства внутри масок глифов. Толщина штриха — по числу ветвей. Чернила на кремовой бумаге.",
         cmd="python3 media/experiments/hyphatype/build.py"),
    dict(key="trap3d", verb="смотреть", title="Кольцо в объёме", kind="POV-Ray, 8 с, MP4 + GIF",
         img=os.path.join(OUT, "trap3d_still_0.60.png"), img2=os.path.join(OUT, "trap3d_still_warm_0.60.png"),
         text="Трассировка лучей: червь продевается сквозь кольцо, три клетки раздуваются внутрь, камера медленно облетает. Две версии: ночная индиго и солнечная (мармелад, нефрит, кобальтовая полоска).",
         cmd="python3 media/build_trap3d.py [--scene media/pov/trap_anim_warm.pov --tag _warm]"),
    dict(key="films", verb="смотреть", title="Два фильма", kind="документальный 20 с · поэтический 57 с",
         img=os.path.join(OUT, "still_015.2s.png"), img2=os.path.join(OUT, "poetry_still_021.5s.png"),
         text="Основные сдачи вечера: документальный компаньон с кодовой схемой кольца и поэтический компаньон, где голоса партитуры стали типографикой.",
         cmd="python3 media/build_companion.py · python3 media/build_poetry.py"),
]


def main():
    cards = []
    for L in LANES:
        imgs = ""
        for k in ("img", "img2"):
            p = L.get(k)
            if p:
                u = data_uri(p)
                if u:
                    imgs += f'<img src="{u}" alt="{L["title"]}" loading="lazy">'
        pre = f'<pre>{L["pre"]}</pre>' if L.get("pre") else ""
        link = f'<a class="go" href="{L["link"]}" target="_blank" rel="noopener">Открыть игру ↗</a>' if L.get("link") else ""
        cards.append(f'''
<article class="lane" id="{L["key"]}">
  <div class="meta"><span class="verb">{L["verb"]}</span><span class="kind">{L["kind"]}</span></div>
  <h2>{L["title"]}</h2>
  <div class="media">{imgs}{pre}</div>
  <p>{L["text"]}</p>
  <div class="foot"><code>{L["cmd"]}</code>{link}</div>
</article>''')
    html = f'''<title>Ночная лаборатория</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: warm paper, one column of lanes, each lane = verb + title + media + one paragraph + build line */
:root{{
  --paper:#f3ead8; --paper-2:#e9dec6; --ink:#3a2f26; --ink-2:#6b5a4a; --terra:#b85a3a; --jade:#2f8a74; --marigold:#d9a23c; --rule:#d8c9a8;
  --display:"EB Garamond", Georgia, "Times New Roman", serif; --body:"IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{ --paper:#1f1a16; --paper-2:#2a241e; --ink:#eadfca; --ink-2:#b3a48d; --terra:#e07a55; --jade:#5fc1a6; --marigold:#e8b65a; --rule:#3d342b; color-scheme:dark }} }}
:root[data-theme="dark"]{{ --paper:#1f1a16; --paper-2:#2a241e; --ink:#eadfca; --ink-2:#b3a48d; --terra:#e07a55; --jade:#5fc1a6; --marigold:#e8b65a; --rule:#3d342b; color-scheme:dark }}
body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0}}
.wrap{{max-width:980px;margin:0 auto;padding-block:36px 60px}}
header h1{{font:400 clamp(40px,7vw,72px)/1 var(--display);letter-spacing:.04em;margin:0 0 10px;text-wrap:balance}}
header h1 em{{font-style:italic;color:var(--terra)}}
header p{{max-width:62ch;color:var(--ink-2);margin:6px 0}}
.toc{{display:flex;flex-wrap:wrap;gap:8px 18px;margin:18px 0 34px;padding:14px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}}
.toc a{{color:var(--jade);text-decoration:none;font-size:14px}} .toc a:hover{{text-decoration:underline}}
.lane{{display:grid;grid-template-columns:150px 1fr;gap:10px 26px;padding:28px 0;border-bottom:1px solid var(--rule)}}
@media (max-width:640px){{.lane{{grid-template-columns:1fr}}}}
.meta{{display:flex;flex-direction:column;gap:4px}}
.verb{{font:500 11px var(--body);letter-spacing:.14em;text-transform:uppercase;color:var(--terra)}}
.kind{{font-size:13px;color:var(--ink-2)}}
h2{{font:400 34px/1.1 var(--display);margin:0;grid-column:2}}
.media{{grid-column:2;display:flex;flex-wrap:wrap;gap:10px;align-items:flex-start}}
.media img{{max-width:100%;width:calc(50% - 5px);min-width:260px;flex:1 1 260px;border:1px solid var(--rule);background:#fff}}
.media img:only-child{{width:100%}}
pre{{grid-column:2;margin:0;padding:14px 16px;background:var(--paper-2);border:1px solid var(--rule);font:13px/1.45 "DejaVu Sans Mono",Menlo,monospace;white-space:pre-wrap;color:var(--ink);width:100%;box-sizing:border-box}}
.lane p{{grid-column:2;margin:0;max-width:66ch}}
.foot{{grid-column:2;display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center}}
code{{font:13px "DejaVu Sans Mono",Menlo,monospace;color:var(--ink-2)}}
.go{{font:500 13px var(--body);letter-spacing:.08em;text-transform:uppercase;color:#2a1d08;background:var(--marigold);padding:8px 14px;text-decoration:none}}
.go:focus-visible{{outline:2px solid var(--ink);outline-offset:2px}}
footer{{margin-top:30px;color:var(--ink-2);font-size:13px;max-width:70ch}}
</style>
<div class="wrap">
<header>
  <h1>Ночная <em>лаборатория</em></h1>
  <p><a data-project-channel href="https://t.me/phys_math_dev" target="_blank" rel="noopener noreferrer" style="color:inherit;text-underline-offset:3px">Telegram · @phys_math_dev ↗</a></p>
  <p>Одиннадцать способов подойти к фразе «Хищные грибы Узбекистана» за одну ночь: поиграть, напечатать, вырезать, подержать, прочитать вслух, посмотреть. Половина сделана из бумаги и дневного света, не из индиго.</p>
  <p>Всё собирается из python3, numpy, Pillow, ffmpeg и POV-Ray; код в <code>media/experiments/</code>, результаты в <code>media/output/experiments/</code>. Вторая половина коллекции (участие, чай, комикс, бюро, танец) — у Codex.</p>
</header>
<nav class="toc">{" ".join(f'<a href="#{L["key"]}">{L["title"]}</a>' for L in LANES)}</nav>
{"".join(cards)}
<footer>Художественная интерпретация. Название — из диссертации Ф. Х. Файзиевой, Ташкент, 1975 (библиография проверена, полный текст не изучен). Биология ловушек — современные исследования: кольцо из трёх клеток раздувается внутрь за 0,1–1 с; клейкие сети — другой гриб. Ни один из объектов не описывает узбекские виды.</footer>
</div>
'''
    out = os.path.join(HERE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("[info] wrote", out, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
