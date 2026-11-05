"""Static bilingual routing; no browser translation service or runtime dependency."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from urllib.parse import urlsplit,urlunsplit,unquote
import posixpath,re
ROOT=Path(__file__).resolve().parents[2]
ORIGIN='https://tarstars.github.io/carnivore_mushrooms/'
PAIRS={
'index.html':'en/index.html',
'game/index.html':'en/game/index.html',
'artwork/experiments/01-chorus/index.html':'en/chorus/index.html',
'artwork/experiments/02-dinner/index.html':'en/dinner/index.html',
'artwork/experiments/05-dance/listen.html':'en/dance/index.html',
'artwork/experiments/08-postcards/index.html':'en/postcards/index.html',
'media/experiments/poemachine/poemachine.html':'en/poetry/index.html',
'artwork/experiments/10-pet/index.html':'en/pet/index.html'}
PAGES=dict(PAIRS)
PAGES.update({
'artwork/experiments/index.html':'en/index.html',
'media/experiments/nematoda/nematoda.html':'en/game/index.html',
'media/experiments/nematoda/index.html':'en/game/index.html',
'artwork/experiments/03-comic/the-dissertation-that-sprouted.png':'en/comic/index.html',
'artwork/experiments/04-bureau/self-germinating-form.pdf':'en/bureau/index.html',
'research/dossier.pdf':'en/research/index.html',
'research/poetry-context.json':'en/research/index.html',
'media/experiments/gallery/index.html':'en/index.html'})
ASSETS={
'artwork/experiments/02-dinner/invitation-and-placecards.pdf':'en/dinner/invitation-and-placecards.pdf',
'artwork/experiments/03-comic/comic-print.pdf':'en/comic/comic-print.pdf',
'artwork/experiments/05-dance/graphic-score.pdf':'en/dance/graphic-score.pdf',
'artwork/experiments/05-dance/graphic-score.svg':'en/dance/graphic-score.svg',
'artwork/experiments/05-dance/cover.png':'en/dance/graphic-score.svg',
'media/output/experiments/postcards/postcards_A4_duplex.pdf':'en/postcards/postcards_A4_duplex.pdf',
'media/output/experiments/hyphatype/hyphatype_poster.png':'en/type/hyphatype_poster.png',
'media/output/experiments/hyphatype/hyphatype_preview.png':'en/type/hyphatype_preview.png',
'media/output/experiments/hyphatype/hyphatype_poster.svg':'en/type/hyphatype_poster.svg',
'media/output/experiments/poemachine/sample_seed1975.txt':'en/poetry/sample.txt',
'media/output/experiments/tamagrib/demo_diary.txt':'en/pet/diary.txt',
'artwork/poem.txt':'en/research/poem.txt',
'artwork/experiments/review/nematoda-desktop-fixed.png':'en/game/preview.png',
'media/experiments/poemachine/poemachine.py':'en/poetry/poemachine.py',
'media/experiments/tamagrib/tamagrib.py':'en/pet/tamagrib.py',
'media/output/experiments/tamagrib/screen.png':'en/pet/screen.png',
'media/output/experiments/postcards/fronts_sheet.png':'en/postcards/fronts_sheet.png'}
def translate(text,table):
 for a,b in sorted(table.items(),key=lambda x:len(x[0]),reverse=True):text=text.replace(a,b)
 return text

def url_to(path,from_file):
 value=posixpath.relpath(path,posixpath.dirname(from_file) or '.')
 if value.endswith('index.html'):value=value[:-10] or './'
 return value
class Rewrite(HTMLParser):
 def __init__(self,source,dest):
  super().__init__(convert_charrefs=False);self.source=source;self.dest=dest;self.parts=[]
 def attribute(self,k,v):
  if v is None:return k
  if k=='lang' and v=='ru':v='en'
  if k in ('href','src','poster'):
   u=urlsplit(v)
   if u.path and not u.scheme and not u.netloc and not u.path.startswith('/'):
    p=posixpath.normpath(posixpath.join(posixpath.dirname(self.source),unquote(u.path)))
    if (ROOT/p).is_dir():p=posixpath.normpath(posixpath.join(p,'index.html'))
    target=(PAGES.get(p) if k=='href' else None) or ASSETS.get(p) or p
    v=urlunsplit(('','',url_to(target,self.dest),u.query,u.fragment))
  return k+'="'+escape(v,quote=True)+'"'
 def tag(self,t,a,closed=False):self.parts.append('<'+t+''.join(' '+self.attribute(k,v) for k,v in a)+('/>' if closed else '>'))
 def handle_starttag(self,t,a):self.tag(t,a)
 def handle_startendtag(self,t,a):self.tag(t,a,True)
 def handle_endtag(self,t):self.parts.append('</'+t+'>')
 def handle_data(self,d):self.parts.append(d)
 def handle_entityref(self,n):self.parts.append('&'+n+';')
 def handle_charref(self,n):self.parts.append('&#'+n+';')
 def handle_decl(self,d):self.parts.append('<!'+d+'>')
 def handle_comment(self,d):self.parts.append('<!--'+d+'-->')
def strip_language(text):
 return re.sub(r'<!-- language switch -->.*?<!-- /language switch -->','',text,flags=re.S)
def strip_metadata(text):
 text=re.sub(r'<meta\b[^>]*(?:name="description"|property="og:[^"]+"|name="twitter:card")[^>]*>','',text,flags=re.I)
 return re.sub(r'<link\b[^>]*rel="(?:canonical|alternate)"[^>]*>','',text,flags=re.I)
def metadata(title,description,path,ru,en):
 page=lambda p:ORIGIN+(p[:-10] if p.endswith('index.html') else p)
 image='en/game/preview.png' if path.startswith('en/game/') else 'artwork/experiments/review/nematoda-desktop-fixed.png' if ('game/' in path or 'nematoda' in path) else 'artwork/experiments/02-dinner/dinner-invitation.png'
 return ''.join(['<meta name="description" content="'+escape(description,quote=True)+'">',
 '<meta property="og:type" content="website">','<meta property="og:title" content="'+escape(title,quote=True)+'">',
 '<meta property="og:description" content="'+escape(description,quote=True)+'">','<meta property="og:url" content="'+page(path)+'">',
 '<meta property="og:image" content="'+ORIGIN+'artwork/experiments/02-dinner/dinner-invitation.png">',
 '<meta name="twitter:card" content="summary_large_image">','<link rel="canonical" href="'+page(path)+'">',
 '<link rel="alternate" hreflang="ru" href="'+page(ru)+'">','<link rel="alternate" hreflang="en" href="'+page(en)+'">',
 '<link rel="alternate" hreflang="x-default" href="'+page(ru)+'">'])
LANG_CSS='''.language-nav{display:flex;justify-content:flex-end;gap:16px;align-items:center;font:600 12px/1.5 system-ui,sans-serif;letter-spacing:.08em;margin:8px 0 14px;max-width:100%;flex-wrap:wrap}.language-nav a{color:inherit;text-decoration:none;padding:5px 2px;opacity:.65}.language-nav a[aria-current=page]{opacity:1;border-bottom:2px solid currentColor}.language-nav a:hover{opacity:1}.language-nav a:focus-visible{outline:2px solid currentColor;outline-offset:4px}@media print{.language-nav{display:none}}'''
def add_language(text,path,ru,en,lang,title=None,description=None):
 text=strip_language(text)
 nav='<!-- language switch --><style>'+LANG_CSS+'</style><nav class="language-nav" aria-label="'+('Language' if lang=='en' else 'Язык')+'">'
 for code,target in [('ru',ru),('en',en)]:
  nav+='<a data-language="'+code+'" lang="'+code+'" hreflang="'+code+'" href="'+url_to(target,path)+'"'+(' aria-current="page"' if code==lang else '')+'>'+code.upper()+'</a>'
 nav+='</nav><!-- /language switch -->'
 if '<aside class="guide">' in text:text=text.replace('<aside class="guide">','<aside class="guide">'+nav,1)
 elif any(x in path for x in ('01-chorus','02-dinner','en/chorus','en/dinner')) and '</header>' in text:text=text.replace('</header>','</header><div style="padding:0 5vw">'+nav+'</div>',1)
 elif '<header>' in text:text=text.replace('<header>','<header>'+nav,1)
 elif '<main>' in text:text=text.replace('<main>','<main>'+nav,1)
 elif '<body>' in text:text=text.replace('<body>','<body>'+nav,1)
 else:text=text.replace('</style>','</style>'+nav,1)
 text=strip_metadata(text)
 if title is None:
  m=re.search(r'<title>(.*?)</title>',text,re.S);title=m.group(1) if m else 'Predatory fungi of Uzbekistan'
 text=text.replace('</title>','</title>'+metadata(title,description or title,path,ru,en),1)
 return text

def localized(source,source_path,dest,table,ru,en,title=None,description=None):
 source=strip_language(source)
 originals=[]
 def save(match):
  originals.append(match.group(0));return '@@ORIGINAL_EXCERPT_'+str(len(originals)-1)+'@@'
 source=re.sub(r'<pre\b[^>]*>.*?</pre>',save,source,flags=re.S)
 source=translate(source,table)
 r=Rewrite(source_path,dest);r.feed(source);r.close()
 rendered=''.join(r.parts)
 for i,original in enumerate(originals):rendered=rendered.replace('@@ORIGINAL_EXCERPT_'+str(i)+'@@',original)
 return add_language(rendered,dest,ru,en,'en',title,description)
