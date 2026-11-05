"""Generate GitHub Pages entry points from the reviewed local gallery and game."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from urllib.parse import urlsplit,urlunsplit
import posixpath
ROOT=Path(__file__).resolve().parents[2]
ORIGIN='https://tarstars.github.io/carnivore_mushrooms/'
class Relocate(HTMLParser):
    def __init__(self,base):
        super().__init__(convert_charrefs=False);self.base=base;self.parts=[]
    def attr(self,key,value):
        if value is None:return key
        if key in ('href','src','poster'):
            u=urlsplit(value)
            if u.path and not u.scheme and not u.netloc and not u.path.startswith('/'):
                path=posixpath.normpath(posixpath.join(self.base,u.path))
                if path.startswith('../'):raise ValueError(value)
                if path=='media/experiments/nematoda/nematoda.html':path='game/'
                value=urlunsplit(('', '', path,u.query,u.fragment))
        return key+'="'+escape(value,quote=True)+'"'
    def tag(self,tag,attrs,closed=False):
        self.parts.append('<'+tag+''.join(' '+self.attr(k,v) for k,v in attrs)+('/>' if closed else '>'))
    def handle_starttag(self,t,a):self.tag(t,a)
    def handle_startendtag(self,t,a):self.tag(t,a,True)
    def handle_endtag(self,t):self.parts.append('</'+t+'>')
    def handle_data(self,d):self.parts.append(d)
    def handle_entityref(self,n):self.parts.append('&'+n+';')
    def handle_charref(self,n):self.parts.append('&#'+n+';')
    def handle_decl(self,d):self.parts.append('<!'+d+'>')
    def handle_comment(self,d):self.parts.append('<!--'+d+'-->')
def metadata(title,description,url,image):
    return ''.join([
        '<meta name="description" content="'+escape(description,quote=True)+'">',
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="'+escape(title,quote=True)+'">',
        '<meta property="og:description" content="'+escape(description,quote=True)+'">',
        '<meta property="og:url" content="'+url+'">',
        '<meta property="og:image" content="'+image+'">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="canonical" href="'+url+'">'])
def main():
    r=Relocate('artwork/experiments');r.feed((ROOT/'artwork/experiments/index.html').read_text());r.close()
    gallery=''.join(r.parts)
    gallery=gallery.replace('</title>','</title>'+metadata('Хищные грибы Узбекистана — ночная лаборатория','Десять способов разрастись: поэзия, игра, музыка, комикс и солнечные фантазии. Codex × Claude · @phys_math_dev.',ORIGIN,ORIGIN+'artwork/experiments/02-dinner/dinner-invitation.png'),1)
    (ROOT/'index.html').write_text(gallery)
    game=(ROOT/'media/experiments/nematoda/nematoda.html').read_text()
    game=game.replace('</title>','</title>'+metadata('Нематода — Хищные грибы Узбекистана','Вы — маленький круглый червь. Ешьте бактерии, избегайте ловушек. Мышь, стрелки или касание. @phys_math_dev.',ORIGIN+'game/',ORIGIN+'artwork/experiments/review/nematoda-desktop-fixed.png'),1)
    game=game.replace('<aside class="guide">','<aside class="guide"><p class="cap"><a href="../" style="color:inherit">← Вся ночная лаборатория</a></p>',1)
    (ROOT/'game').mkdir(exist_ok=True);(ROOT/'game/index.html').write_text(game)
    (ROOT/'.nojekyll').touch()
    print('Built public root gallery and /game/.')
if __name__=='__main__':main()
