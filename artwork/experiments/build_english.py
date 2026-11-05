"""Build the complete English static edition and reciprocal language navigation."""
from pathlib import Path
import ast,html,importlib.util,json,re,subprocess,sys,tempfile,copy
from PIL import Image,ImageDraw,ImageFont
from build_readers import STYLE
from site_languages import ROOT,ORIGIN,PAIRS,PAGES,ASSETS,translate,localized,add_language,strip_language,url_to
from locales.english_text import COMMON,GAME,CHORUS,DINNER,DANCE,POETRY,DINNER_REPLIES,PET,POSTCARDS,POEM_DATA
import build_gallery

def write(path,content):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content);return p

def custom(title,body,path,ru,script='',extra=''):
 source='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+STYLE+extra+'</style><main><a class="back" href="../">← Night laboratory</a>'+body+'<p class="small"><a data-project-channel href="https://t.me/phys_math_dev" target="_blank" rel="noopener noreferrer">Telegram · @phys_math_dev ↗</a></p></main><script>'+script+'</script></html>'
 return add_language(source,path,ru,path,'en',title)

def english_code():
 class Words(ast.NodeTransformer):
  def visit_Constant(self,n):
   if isinstance(n.value,str):n.value=translate(n.value,PET)
   return n
 tree=Words().visit(ast.parse((ROOT/'media/experiments/tamagrib/tamagrib.py').read_text()));ast.fix_missing_locations(tree)
 pet=write('en/pet/tamagrib.py','# English edition of Claude’s original terminal pet.\n'+ast.unparse(tree)+'\n')
 diary=subprocess.check_output([sys.executable,str(pet),'--demo'],text=True)
 write('en/pet/diary.txt',diary+'\nTelegram · https://t.me/phys_math_dev\n')
 spec=importlib.util.spec_from_file_location('english_pet_preview',pet);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 f=mod.Fungus();f.rng.seed(1975)
 for hour in range(40):
  if hour%9==0:f.release_worm()
  f.tick()
 lines=[f'TAMAGRYB · {f.title} · hour {f.hour} (day {f.day()}) · {f.mood}',f'food {f.food:.1f}    signal {f.signal:.1f}    caught {f.caught}    traps {len(f.traps)}','']
 grid=[[' ']*f.w for _ in range(f.h)]
 for y in range(f.h):
  for x in range(f.w):
   if f.inside(x,y):grid[y][x]='·' if not(f.inside(x+1,y) and f.inside(x-1,y) and f.inside(x,y+1) and f.inside(x,y-1)) else '~' if(x,y) in f.hyphae else ' '
 for t in f.traps:
  if 0<=t['y']<f.h and 0<=t['x']<f.w:grid[t['y']][t['x']]='@' if t['fired'] else 'O' if t['kind']=='ring' else '#'
 for worm in f.worms:
  if 0<=worm['y']<f.h and 0<=worm['x']<f.w:grid[worm['y']][worm['x']]='S'
 lines+=[''.join(row) for row in grid]+['','w worm   s stir   r hour   d diary   q quit']+f.diary[-3:]
 im=Image.new('RGB',(1440,760),(28,23,18));draw=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',20)
 for i,line in enumerate(lines):draw.text((22,20+i*25),line[:110],font=font,fill=(237,191,104))
 im.save(ROOT/'en/pet/screen.png')
 tree=ast.parse((ROOT/'media/experiments/poemachine/poemachine.py').read_text())
 values={'COUPLETS':[tuple(x) for x in POEM_DATA['couplets']],'THIRD':[tuple(x) for x in POEM_DATA['third']],'REFRAIN':POEM_DATA['refrains'][0],'REFRAIN_VARIANTS':POEM_DATA['refrains']}
 class PoemWords(ast.NodeTransformer):
  def visit_Assign(self,n):
   if len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in values:n.value=ast.parse(repr(values[n.targets[0].id]),mode='eval').body
   return self.generic_visit(n)
  def visit_Constant(self,n):
   if isinstance(n.value,str):
    n.value=n.value.replace('ПОЧТИ БЕСКОНЕЧНАЯ ПЕСНЬ · машина строф · все строки оригинальные','AN ALMOST ENDLESS SONG · new English verse for this edition').replace('…и так далее.','…and so it grows.').replace('строф из','stanzas from').replace('возможных сочетаний','possible combinations')
   return n
 tree=PoemWords().visit(tree)
 tree.body[0].value=ast.Constant('An almost endless song: original English verse for the project.\nAlternate stanzas with another reader. This is not the historical collective poem.\nUse -n 6 --seed 1975, --theme soil/archive/city/night/science, or --endless.\n')
 ast.fix_missing_locations(tree);machine=write('en/poetry/poemachine.py',ast.unparse(tree)+'\n')
 sample=subprocess.check_output([sys.executable,str(machine),'--seed','1975'],text=True);write('en/poetry/sample.txt',sample)
 return diary

def postcards():
 path='en/postcards/index.html'
 body='''<h1>Greetings from<br>underground.</h1><p>Six postcards from a travelling nematode with a growing suspicion that something is wrong.</p><p class="eyebrow">Letters and drawings by Claude / English reading room by Codex</p><h2 id="place"></h2><section id="postcard"><img id="card" alt=""><article id="letter" hidden aria-live="polite"></article></section><div class="tools"><button id="prev" aria-label="Previous postcard">←</button><button id="flip">Read the letter</button><button id="next" aria-label="Next postcard">→</button><span id="counter" aria-live="polite"></span></div><div class="links"><a href="postcards_A4_duplex.pdf">All six English postcards · printable PDF</a></div><p class="small">Fictional correspondence and an imagined itinerary inspired by the history of trapping-fungus research. These letters are not a documentary chronology of particular experiments. English adaptations for this edition.</p>'''
 script='const cards='+json.dumps(POSTCARDS,ensure_ascii=False)+''';let i=0,back=false;function show(){document.querySelector('#place').textContent=cards[i].place.replace(',',', ');const img=document.querySelector('#card');img.src='card'+(i+1)+'-front.png';img.alt='Postcard from '+cards[i].place;img.hidden=back;const letter=document.querySelector('#letter');letter.hidden=!back;letter.replaceChildren();for(const line of cards[i].msg){const p=document.createElement('p');p.textContent=line;letter.append(p)}document.querySelector('#flip').textContent=back?'See the illustration':'Read the letter';document.querySelector('#counter').textContent=(i+1)+' / 6';}function move(n){i=(i+n+6)%6;back=false;show()}document.querySelector('#flip').onclick=()=>{back=!back;show()};document.querySelector('#prev').onclick=()=>move(-1);document.querySelector('#next').onclick=()=>move(1);document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();move(1)}if(e.key==='ArrowLeft'){e.preventDefault();move(-1)}});show();'''
 extra='''#postcard{min-height:360px}#letter{background:#f6edda;border:1px solid #d3c9ad;padding:35px;font:23px/1.6 Georgia,serif;max-width:850px;min-height:420px}#letter p{margin:0 0 20px}#card[hidden],#letter[hidden]{display:none}@media(max-width:600px){#letter{font-size:20px;padding:24px;min-height:420px}}'''
 write(path,custom('Greetings from underground — English postcards',body,path,'artwork/experiments/08-postcards/index.html',script,extra))

def pet_page(diary):
 path='en/pet/index.html'
 body='''<h1>What if a predator<br>needed your care?</h1><p class="eyebrow">Tamagryb / a terminal pet / Claude</p><p>Release worms, stir the agar, and read its diary. This culture builds traps, gets bored, and dreams about a dissertation.</p><img class="screen" src="screen.png" alt="English terminal pet: a Petri dish, rings and a culture diary"><h2>Bring it home</h2><p>Download the English script and run it in a terminal in the download folder. A standard 80 × 24 window works.</p><div class="links"><a class="primary" download="tamagrib.py" href="tamagrib.py">Download the English pet</a></div><pre id="command">python3 tamagrib.py</pre><button id="copy">Copy the command</button><p><code>w</code> release a worm · <code>s</code> stir · <code>r</code> advance an hour · <code>d</code> diary · <code>q</code> quit.</p><details><summary>Read its diary without running the game</summary><pre>'''+html.escape(diary)+'''</pre></details><div class="links"><a href="diary.txt">English diary · TXT</a></div><p class="small">Requires Python 3 and a terminal with curses (Linux/macOS). Add <code>--demo</code> for a text-only version. The pet does not save progress between runs. It is a fictional composite: sticky networks and constricting rings are distinct trapping mechanisms in biology.</p>'''
 script="document.querySelector('#copy').onclick=async()=>{const b=document.querySelector('#copy');try{await navigator.clipboard.writeText(document.querySelector('#command').textContent);b.textContent='Command copied'}catch(e){const r=document.createRange();r.selectNodeContents(document.querySelector('#command'));const s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent='Command selected—copy it to continue';}};"
 write(path,custom('Tamagryb — care for a predator',body,path,'artwork/experiments/10-pet/index.html',script))

def comic():
 path='en/comic/index.html';captions=['The catalogue was quiet.','Someone read the title out.','Another offered it a rhyme.','A third opened the window.','The word found a loop.','And the page found its next reader.']
 body='''<h1>The dissertation<br>that sprouted.</h1><p>A wordless comic about a title that becomes a shared poem.</p><img src="../../artwork/experiments/03-comic/the-dissertation-that-sprouted.png" alt="Six panels: a fictional archivist opens a book, letters grow, neighbours join, and a garden spreads across the pages"><ol>'''+''.join('<li>'+html.escape(s)+'</li>' for s in captions)+'''</ol><div class="links"><a href="comic-print.pdf">English title and notes · A3 PDF</a><a href="../../artwork/experiments/03-comic/the-dissertation-that-sprouted.png">Full illustration</a></div><p class="small">A fictional archival fable. The archivist is not a portrait of Flora Fayzieva. The microscopic panel is an artistic metaphor. The illustration was generated for the project.</p>'''
 write(path,custom('The dissertation that sprouted — English reading',body,path,'index.html'))

def bureau():
 path='en/bureau/index.html'
 body='''<div class="bureau"><p class="eyebrow">Form HYP-27 / Department of Provisional Definitions</p><h1>The Bureau<br>of Self-Germinating<br><em>Titles.</em></h1><p>If a title outgrows its book, please do not interfere.</p><div class="tools"><button id="example">Completed example</button><button id="blank">Blank form</button><button id="print">Print this form</button></div><label>01 / TITLE<input id="name" maxlength="100"></label><label>02 / CIRCUMSTANCES IN WHICH IT TOOK ROOT<textarea id="circumstances" rows="2" maxlength="300"></textarea></label><label>03 / EXPECTED DAMAGE<textarea id="damage" rows="2" maxlength="300"></textarea></label><label>04 / UNIT OF ACCOUNT<select id="unit"><option>fungus</option><option>stanza</option><option selected>not yet determined</option></select></label><div class="stamp">CLASSIFICATION<br><strong>REFUSED</strong><br>reason: still growing</div><h2>Permission granted</h2><p>to grow beyond the margins of this form.</p><p class="small">Little roots for your neighbours: keep one and pass the rest along.</p><div class="roots"><span>KEEP<br>GROWING</span><span>PASS<br>IT ON</span><span>CROSS<br>THE MARGIN</span><span>LET IT<br>TAKE ROOT</span></div></div><div class="links"><a href="self-germinating-form.pdf">Completed and blank forms · English A4 PDF</a></div><p class="small">A fictional art document. Your entries stay on this page.</p>'''
 script="const fields=['name','circumstances','damage'];document.querySelector('#example').onclick=()=>{['Predatory fungi of Uzbekistan','One reader began. Another offered a rhyme.','The reader started adding lines.'].forEach((s,i)=>document.getElementById(fields[i]).value=s)};document.querySelector('#blank').onclick=()=>fields.forEach(id=>document.getElementById(id).value='');document.querySelector('#print').onclick=()=>window.print();document.querySelector('#example').click();"
 extra='''.bureau{position:relative;max-width:850px}h1 em{font-weight:400;color:#bc4a32}.bureau label{display:block;font-size:11px;letter-spacing:.08em;margin:24px 0}.bureau input,.bureau textarea,.bureau select{display:block;width:100%;border:0;border-bottom:1px solid #b5c4a9;background:transparent;padding:13px 0;color:inherit;font:22px/1.4 Georgia,serif}.bureau select{font-size:16px}.stamp{border:2px solid #bc4a32;border-radius:50%;width:174px;height:174px;text-align:center;padding:40px 12px;margin:30px 0;color:#bc4a32;font-size:11px;transform:rotate(9deg)}.stamp strong{font-size:23px}.roots{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px dashed #758b6f;margin:25px 0}.roots span{text-align:center;padding:25px 5px;border-right:1px dashed #758b6f;font-size:11px}@media print{@page{size:A4;margin:14mm}body{background:white}main{padding:0}.tools,.links,.back{display:none}h1{font-size:34px}.bureau label{margin:12px 0}.bureau input,.bureau textarea{font-size:15px;padding:6px 0}.stamp{float:right;width:140px;height:140px;padding:29px 6px;margin:0;font-size:9px}.stamp strong{font-size:19px}}'''
 write(path,custom('Bureau of Self-Germinating Titles — English form',body,path,'index.html',script,extra))

def research():
 path='en/research/index.html';poem=(ROOT/'artwork/experiments/locales/poem.en.txt').read_text();write('en/research/poem.txt',poem)
 sources=[('Dissertation record · Russian State Library','https://search.rsl.ru/ru/record/01009653250'),('Separate abstract · Russian State Library','https://search.rsl.ru/ru/record/01006951043'),('Adhesive networks · Tunlid et al., 1991','https://pubmed.ncbi.nlm.nih.gov/1919501/'),('Nematode pheromones and trap formation · 2013','https://pubmed.ncbi.nlm.nih.gov/23246407/'),('Prey-sensing GPCRs · Nature Microbiology, 2024','https://www.nature.com/articles/s41564-024-01679-w'),('Rapid ring-cell inflation · Nature Communications, 2023','https://www.nature.com/articles/s41467-023-43235-w'),('Olfactory mimicry · eLife, 2017','https://elifesciences.org/articles/20023'),('AN BIO · manufacturer’s composition statement','https://anguzalagro.uz/en/product/anbio-2'),('Dated collective-poem compilation · 28 February 2018','https://onem0re.blogspot.com/2018/02/blog-post_28.html')]
 body='''<h1>A title with<br>roots and a refrain.</h1><p class="eyebrow">Research, literary context and an English rendering of the project poem</p><h2>A real scientific title</h2><p>The Russian State Library records Flora Khusanovna Fayzieva’s <em>Predatory fungi of Uzbekistan</em>, a1975 Tashkent dissertation of159 illustrated pages, with a separate27-page abstract. We verified its bibliography, not its full text. This project does not establish a species inventory for Uzbekistan.</p><h2>Two different traps</h2><p><em>Arthrobotrys oligospora</em> forms sticky three-dimensional hyphal networks. <em>Drechslerella dactyloides</em> uses rings of three cells that inflate inwards around a passing nematode; research reports rapid inflation in about0.1–1second. A living ring is not a rope pulled tight.</p><p>The artworks and games juxtapose these mechanisms as a composite fantasy. They are not micrographs, verified Uzbek collection records, or claims of endemic distribution. Studies of prey sensing and olfactory mimicry inform the games without making them calibrated biological models.</p><p>A Tashkent-region manufacturer also lists an AN BIO product containing culture liquid and metabolites of <em>A.oligospora</em>. That is a commercial composition statement, not independent evidence of efficacy or local isolation.</p><h2>When the title became a chorus</h2><p>A collective Russian-language internet poem built around this title is documented in a compilation dated28February2018. Its first author and complete list of contributors remain unverified. The compiler is not established as the sole author. This is internet verse, not ancient Uzbek folklore.</p><p>The new poems and adaptations in this laboratory respond to that collective tradition. They do not reproduce the historical poem.</p><h2>Rhyme, too, is a hunting ring</h2><p class="small">English rendering of the original2026 project poem by Codex.</p><pre class="poem">'''+html.escape(poem.split('\n\n',1)[1].split('\nEnglish rendering')[0])+'''</pre><div class="links"><a href="poem.txt">English poem · TXT</a><a href="../../research/dossier.pdf">Original dossier · English notes and Russian poem · PDF</a><a href="../../artwork/poem.txt" lang="ru">Russian project poem</a></div><h2>Sources</h2><ol>'''+''.join('<li><a href="'+u+'" target="_blank" rel="noopener noreferrer">'+html.escape(t)+'</a></li>' for t,u in sources)+'''</ol><p class="small">Musical correspondences, fictional journeys, hosts and game rules were invented for the project. The comic’s archivist is not a portrait of Fayzieva. Original generated artwork keeps its original lettering; English reading and print editions provide translated context.</p>'''

 for a,b in {'a1975':'a 1975','of159':'of 159','separate27':'separate 27','about0.1–1second':'about 0.1–1 second','dated28February2018':'dated 28 February 2018','original2026':'original 2026','A.oligospora':'A. oligospora'}.items():body=body.replace(a,b)
 write(path,custom('Research and poetry — Predatory fungi of Uzbekistan',body,path,'index.html',extra='.poem{font:21px/1.7 Georgia,serif;background:transparent;padding:0}li{margin-bottom:12px}h2{margin-top:36px}p{max-width:900px}@media print{.links,.back{display:none}main{padding:0}.poem{font-size:14px}}'))

def main():
 from build_english_prints import main as prints,module
 prints()
 m=module('english_hyphal_type','media/experiments/hyphatype/build.py');m.main(['PREDATORY','FUNGI','OF UZBEKISTAN'],str(ROOT/'en/type'),'en')
 diary=english_code();postcards();pet_page(diary);comic();bureau();research()
 data=json.loads((ROOT/'artwork/experiments/locales/collection.en.json').read_text())
 with tempfile.TemporaryDirectory(prefix='fungi-en-') as tmp:
  p=Path(tmp)/'gallery.html';build_gallery.main(data,p);gallery=p.read_text()
 write('en/index.html',localized(gallery,'artwork/experiments/index.html','en/index.html',COMMON,'index.html','en/index.html',title='Predatory fungi of Uzbekistan — night laboratory',description='One title. Ten ways to grow: poetry, games, music, a comic and sunny fantasies. Codex × Claude · @phys_math_dev.'))
 for source,dest,words in [
 ('media/experiments/nematoda/nematoda.html','en/game/index.html',GAME),
 ('artwork/experiments/01-chorus/index.html','en/chorus/index.html',CHORUS),
 ('artwork/experiments/02-dinner/index.html','en/dinner/index.html',DINNER),
 ('artwork/experiments/05-dance/listen.html','en/dance/index.html',DANCE),
 ('media/experiments/poemachine/poemachine.html','en/poetry/index.html',POETRY)]:
  content=strip_language((ROOT/source).read_text())
  if dest=='en/chorus/index.html':content=content.replace('fungi-chorus-v1','fungi-chorus-en-v1').replace('collective-mycelium.txt','collective-mycelium-en.txt')
  if dest=='en/dinner/index.html':content=re.sub(r'const replies=.*?;\ndocument',lambda _: 'const replies='+json.dumps(DINNER_REPLIES,ensure_ascii=False)+';\ndocument',content,flags=re.S)
  if dest=='en/poetry/index.html':
   content=re.sub(r'const D=.*?;\s*const bags=',lambda _: 'const D='+json.dumps(POEM_DATA,ensure_ascii=False)+';\nconst bags=',content,flags=re.S)
   content=content.replace('<code>poemachine.py</code>','<a href="poemachine.py"><code>poemachine.py</code></a>')
  table=dict(COMMON);table.update(words)
  ru='game/index.html' if dest=='en/game/index.html' else source
  result=localized(content,source,dest,table,ru,dest)
  if dest=='en/game/index.html':result=result.replace('<aside class="guide">','<aside class="guide"><p class="cap"><a href="../" style="color:inherit">← Night laboratory</a></p>',1)
  write(dest,result)
 # Add reciprocal switches to every Russian entry point, without changing its content or game rules.
 for ru,en in {**PAIRS,'artwork/experiments/index.html':'en/index.html','media/experiments/nematoda/nematoda.html':'en/game/index.html','media/experiments/nematoda/index.html':'en/game/index.html','media/experiments/gallery/index.html':'en/index.html'}.items():
  canonical='game/index.html' if 'nematoda' in ru else 'index.html' if ru in ('artwork/experiments/index.html','media/experiments/gallery/index.html') else ru
  p=ROOT/ru;p.write_text(add_language(p.read_text(),ru,canonical,en,'ru'))
 print('Built English gallery, ten experiences, research reading and reciprocal RU/EN navigation.')
if __name__=='__main__':main()
