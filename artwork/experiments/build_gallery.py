"""Build the local, offline exhibition from finished artifacts; no web dependencies."""
from pathlib import Path
import html,json,os

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def esc(s):return html.escape(str(s),quote=True)
def url(path):return esc(os.path.relpath(ROOT/path,HERE))

CSS='''
:root{--paper:#fff9eb;--ink:#183f36;--red:#d9492f;--green:#43835d;--line:#d4d9c6;--gold:#e9b549}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.6 system-ui,sans-serif}a{color:inherit;text-underline-offset:4px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:4px}header{padding:40px 5vw 30px;max-width:1600px;margin:auto}.kicker{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--green)}.top{display:flex;justify-content:space-between;gap:22px}.top a{font-size:12px}h1{font:clamp(42px,7.4vw,112px)/.94 Georgia,serif;letter-spacing:-.055em;font-weight:400;margin:36px 0 24px;max-width:1150px}h1 em{font-weight:400;color:var(--red)}.intro{display:grid;grid-template-columns:1fr 1fr;gap:40px;max-width:1150px}.intro p{max-width:520px;margin:0}.intro .small{font-size:13px;color:#587260}.filters{position:sticky;top:0;z-index:4;background:#fff9ebf2;backdrop-filter:blur(12px);padding:14px 5vw;display:flex;flex-wrap:wrap;gap:8px;border-block:1px solid var(--line)}button{font:600 12px system-ui;border:1px solid var(--line);background:transparent;color:var(--ink);padding:9px 14px;cursor:pointer}button[aria-pressed=true]{background:var(--ink);color:var(--paper);border-color:var(--ink)}main{max-width:1600px;padding:0 5vw;margin:auto}.warmup{margin:35px 0 65px;display:grid;grid-template-columns:1.35fr 1fr;gap:40px;align-items:center}.warmup img{width:100%;display:block}.warmup h2{font:36px/1.1 Georgia,serif;margin:12px 0}.warmup p{max-width:420px}.label{font-size:10px;text-transform:uppercase;letter-spacing:.15em;color:var(--green)}.piece{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(280px,1fr);gap:5vw;align-items:center;border-top:1px solid var(--line);padding:48px 0;scroll-margin-top:90px}.piece[hidden]{display:none}.art{min-width:0;display:block;text-decoration:none}.art img{display:block;width:100%;max-height:650px;object-fit:contain;object-position:center;background:#fffdf6}.piece[data-id="03"] .art img{max-height:760px}.piece h2{font:clamp(30px,3.2vw,48px)/1.08 Georgia,serif;letter-spacing:-.025em;font-weight:400;margin:16px 0}.piece h3{font:italic 20px/1.4 Georgia,serif;color:var(--green);font-weight:400;margin:0 0 18px}.piece p{max-width:490px}.number{display:inline-block;font:18px Georgia,serif;color:var(--red);margin-right:15px}.primary{display:inline-block;background:var(--ink);color:var(--paper);text-decoration:none;padding:12px 18px;margin:12px 0 8px;font-size:13px}.links{display:flex;gap:15px;flex-wrap:wrap;font-size:12px;margin:10px 0}.note{font-size:11px;color:#69806d;max-width:480px}audio{width:100%;max-width:470px;margin:16px 0}.source{display:inline-block;margin-top:14px;color:#7a8e79;font-size:10px;text-decoration:none;letter-spacing:.07em}.source:hover{text-decoration:underline}.section-title{font:40px/1.1 Georgia,serif;font-weight:400;margin:0 0 20px}.curation,.letters,.basis{border-top:1px solid var(--line);padding:40px 0}.curation p,.basis p{max-width:850px}.curation ol{padding-left:23px;max-width:900px}.curation li{margin-bottom:18px}.letters details{margin:12px 0;padding:16px 0;border-bottom:1px solid var(--line)}summary{cursor:pointer;font:20px Georgia,serif}.letters p{max-width:850px}.letters pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.7 system-ui;max-width:950px;color:#456651}.basis p,.credits{font-size:12px;color:#5f7965}.credits{display:flex;justify-content:space-between;padding:20px 0 40px;gap:20px}.empty{font-size:14px;color:var(--green)}@media(min-width:1050px){.piece:nth-of-type(even){grid-template-columns:minmax(280px,1fr) minmax(0,1.3fr)}.piece:nth-of-type(even) .art{order:2}.piece:nth-of-type(even) .copy{order:1}}@media(max-width:800px){header{padding-top:24px}h1{font-size:clamp(40px,11.5vw,72px);margin-top:24px}.intro{grid-template-columns:1fr;gap:15px}.warmup,.piece{grid-template-columns:1fr;gap:22px}.warmup{margin-bottom:45px}.warmup h2{font-size:29px}.piece{padding:32px 0}.piece h2{font-size:34px}.piece h3{font-size:19px}.filters{padding-block:10px}.filters button{padding:8px 10px}.art img{max-height:600px}.top{display:block}.top a{display:inline-block;margin-top:8px}.credits{display:block}.source{font-size:11px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''

CSS+='''.drawer{border-top:1px solid var(--line);padding:40px 0}.bonus-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:32px}.bonus img{width:100%;height:240px;object-fit:contain;background:#fffdf6}.bonus h3{font:28px Georgia,serif;font-weight:400;margin:15px 0}.bonus p{font-size:13px;max-width:580px}.archive-links{display:flex;gap:20px;flex-wrap:wrap;margin-top:24px}.films{display:grid;grid-template-columns:1fr 1fr;gap:25px;margin-top:28px}.films video{width:100%;background:#183f36}.films h3{font:25px Georgia,serif;font-weight:400;margin:12px 0}.films p{font-size:12px}@media(max-width:800px){.bonus-grid,.films{grid-template-columns:1fr}.bonus img{height:auto;max-height:400px}}'''

def main(data=None,output=None):
    data=data or json.loads((HERE/'collection.json').read_text());pieces=data['pieces']
    missing=[]
    for p in pieces:
        for k in ['primary','image','audio','source']:
            if p.get(k) and not (ROOT/p[k]).is_file():missing.append(p[k])
        for link in p.get('links',[]):
            if not (ROOT/link['path']).is_file():missing.append(link['path'])
    for p in data.get('bonus',[]):
        for k in ['image','path']:
            if not (ROOT/p[k]).is_file():missing.append(p[k])
        for link in p.get('links',[]):
            if not (ROOT/link['path']).is_file():missing.append(link['path'])
    if missing:raise SystemExit('Missing gallery assets: '+', '.join(missing))
    chunks=['<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
       '<title>Хищные грибы Узбекистана — ночная лаборатория</title>',f'<style>{CSS}</style>',
       '<header><div class="top"><div class="kicker">Хищные грибы Узбекистана / ночная лаборатория / Codex × Claude</div><div><a href="../../research/dossier.pdf">История и источники ↗</a> · <a data-project-channel href="https://t.me/phys_math_dev" target="_blank" rel="noopener noreferrer" style="color:inherit;text-underline-offset:3px">Telegram · @phys_math_dev ↗</a></div></div>',
       '<h1>Одно название.<br>Десять способов<br><em>разрастись.</em></h1>',
       '<div class="intro"><p>Оно было научным заглавием. Потом стало общей рифмой. Здесь оно продолжает менять форму: приглашает к столу, учится танцевать, выходит из бланка и просит читателя стать следующим голосом.</p>',
       '<p class="small">Десять опытов: смотреть, читать, слушать, играть, делать руками. Ниже — ещё четыре черновых исследования и два фильма. Начните с того, что вам сейчас ближе.</p></div></header>',
       '<nav class="filters" aria-label="Выбрать способ знакомства">']
    for mode in ['Все','Участвовать','Смотреть','Читать','Слушать','Играть','Сделать']:
        chunks.append(f'<button type="button" data-filter="{mode}" aria-pressed="{"true" if mode=="Все" else "false"}">{mode}</button>')
    chunks.append('<button type="button" id="surprise" style="margin-left:auto;border-color:var(--red);color:var(--red)">Доверьте выбор грибнице ↗</button>')
    chunks.append('</nav><main>')
    garden=ROOT/'artwork/povray/rhyme-garden.png'
    if garden.is_file():
        chunks.append('<section class="warmup"><a href="../povray/rhyme-garden.png"><img src="../povray/rhyme-garden.png" alt="Цветной керамический сад на книге, бирюзовая вода и слово внутри трёхчастного кольца"></a><div><div class="label">Пролог / обновлённый POV-Ray</div><h2>Живая рифма</h2><p>Тёплый свет, вода, листья и цветной керамический хор. С этого сада начался поворот от мрачного кабинета к живой, смешной и гостеприимной грибнице.</p><a href="../povray/rhyme-garden.pov">Редактируемая сцена ↗</a></div></section>')
    chunks.append('<div id="pieces">')
    for p in pieces:
        chunks.append(f'<article class="piece" id="piece-{esc(p["id"])}" data-id="{esc(p["id"])}" data-mode="{esc(p["mode"])}"><a class="art" href="{url(p["primary"])}"><img src="{url(p["image"])}" alt="{esc(p["title"])}" loading="lazy"></a><div class="copy">')
        chunks.append(f'<div class="label"><span class="number">{esc(p["id"])}</span>{esc(p["mode"])} / {esc(p["owner"])}</div><h2>{esc(p["title"])}</h2><h3>{esc(p["angle"])}</h3><p>{esc(p["description"])}</p>')
        if p.get('audio'):chunks.append(f'<audio controls preload="none" src="{url(p["audio"])}">Аудио можно открыть по ссылке ниже.</audio>')
        chunks.append(f'<a class="primary" href="{url(p["primary"])}">{esc(p["action"])} ↗</a>')
        chunks.append('<div class="links">'+''.join(f'<a href="{url(l["path"])}">{esc(l["label"])}</a>' for l in p.get('links',[]))+'</div>')
        if p.get('note'):chunks.append(f'<p class="note">{esc(p["note"])}</p>')
        if p.get('source'):chunks.append(f'<a class="source" href="{url(p["source"])}">ИСХОДНИК / КАК ЭТО СДЕЛАНО ↗</a>')
        chunks.append('</div></article>')
    chunks.append('</div><p class="empty" id="empty" hidden>В этом разделе пока нет опыта. Выберите другой способ.</p>')
    if data.get('shortlist'):
        chunks.append('<section class="curation"><h2 class="section-title">Если открыть только три</h2><ol>')
        for s in data['shortlist']:chunks.append(f'<li><a href="#piece-{esc(s["id"])}">{esc(s["title"])}</a> — {esc(s["reason"])}</li>')
        chunks.append('</ol></section>')
    if data.get('bonus'):
        chunks.append('<section class="drawer"><div class="label">За пределами основной десятки / Claude</div><h2 class="section-title">В ящике лаборатории</h2><p>Четыре дополнительных хода. Здесь виден и следующий шаг работы: где нужен реальный стол, где — ножницы, где — принтер.</p><div class="bonus-grid">')
        for p in data['bonus']:
            chunks.append(f'<article class="bonus"><a href="{url(p["path"])}"><img src="{url(p["image"])}" loading="lazy" alt="{esc(p["title"])}"></a><h3><a href="{url(p["path"])}">{esc(p["title"])}</a></h3><p>{esc(p["description"])}</p>')
            chunks.append('<div class="links">'+''.join(f'<a href="{url(l["path"])}">{esc(l["label"])}</a>' for l in p.get('links',[]))+'</div></article>')
        chunks.append('</div></section>')
    chunks.append('<section class="drawer"><div class="label">Первые ветви / Codex × Claude</div><h2 class="section-title">Образы и два фильма</h2><p>Научный образ, поэтическая книга и движение текста. Во втором фильме голоса стихотворения становятся типографикой и синтезированным звуком.</p><div class="archive-links"><a href="../predatory-fungi-uzbekistan.png">Биологический постер ↗</a><a href="../poetic-chorus.png">Книга, которая стала хором ↗</a><a href="../poem.txt">Новое стихотворение ↗</a><a href="../povray/rhyme-trap.png">Ранний тёмный POV-Ray ↗</a></div><div class="films"><article><video controls preload="none" poster="../../media/output/still_007.5s.png" src="../../media/output/companion.mp4"></video><h3>Под почвой начинается охота</h3><p>20 секунд · изображение, схема трёх клеток и оригинальный звук.</p></article><article><video controls preload="none" poster="review/poetry-final-45.png" src="../../media/output/poetry_companion.mp4"></video><h3>Рифма — тоже ловчее кольцо</h3><p>57 секунд · новая поэма проекта, буквенный хор и оригинальный звук. Полный постер сохранён в кадре.</p></article></div></section>')
    letters=data.get('correspondence',[])
    if letters:
        chunks.append('<section class="letters"><h2 class="section-title">Мы спорили по делу</h2><p>Переписка двух авторов: задачи, ограничения, критика и ответы. Общие файлы служили почтовым ящиком; рабочие каталоги были разделены.</p>')
        for l in letters:
            chunks.append(f'<details><summary>{esc(l["title"])}</summary><pre>{esc((ROOT/l["path"]).read_text())}</pre></details>')
        chunks.append('</section>')
    chunks.append('<section class="basis"><h2 class="section-title">Откуда всё выросло</h2><p>В основе — библиографическая запись диссертации Флоры Файзиевой 1975 года, исследования ловчих грибов и документированная коллективная сетевая поэма. Полный текст диссертации нами не изучен. Художественные сюжеты, музыкальные соответствия и правила игр придуманы для этой лаборатории.</p><p><a href="../../research/dossier.pdf">Исследование и ссылки</a> · <a href="../../research/poetry-context.json">История коллективной поэмы</a> · <a href="../poem.txt">Новое стихотворение проекта</a></p></section><footer class="credits"><span>Codex × Claude · 2026 · Хищные грибы Узбекистана</span><a data-project-channel href="https://t.me/phys_math_dev" target="_blank" rel="noopener noreferrer" style="color:inherit;text-underline-offset:3px">Telegram · @phys_math_dev ↗</a><span>Одна тема. Разные способы быть её читателем.</span></footer></main>')
    chunks.append('''<script>(()=>{const buttons=[...document.querySelectorAll('[data-filter]')],pieces=[...document.querySelectorAll('.piece')];function choose(mode){buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===mode)));let count=0;pieces.forEach(p=>{p.hidden=mode!=='Все'&&p.dataset.mode!==mode;if(!p.hidden)count++;});document.getElementById('empty').hidden=count>0;}buttons.forEach(b=>b.addEventListener('click',()=>choose(b.dataset.filter)));document.querySelectorAll('a[href^="#piece-"]').forEach(a=>a.addEventListener('click',()=>choose('Все')));let bag=[];document.getElementById('surprise').addEventListener('click',()=>{choose('Все');if(!bag.length)bag=pieces.map((_,i)=>i).sort(()=>Math.random()-.5);const p=pieces[bag.pop()];location.hash=p.id;p.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'start'});});})();</script></html>''')
    (output or HERE/'index.html').write_text('\n'.join(chunks));print(f'Built offline gallery: {len(pieces)} finished experiments.')

if __name__=='__main__':main()
