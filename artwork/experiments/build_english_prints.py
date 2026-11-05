"""English native print editions; generated bitmap illustrations remain unaltered."""
from pathlib import Path
import importlib.util,json,copy,textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,A3
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
from locales.english_text import POSTCARDS,SCORE
ROOT=Path(__file__).resolve().parents[2]
for name,file in [('EnBody','DejaVuSans.ttf'),('EnSerif','DejaVuSerif.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
INK=HexColor('#214b3b');PAPER=HexColor('#fff9e9');RED=HexColor('#bc4a32')
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def footer(c,x=17*mm,y=8*mm):
 c.setFillColor(INK);c.setFont('EnBody',7);c.drawString(x,y,'Telegram · https://t.me/phys_math_dev');c.linkURL('https://t.me/phys_math_dev',(x,y-2,x+240,y+9),relative=0,thickness=0)
def text(c,x,y,s,size=11,serif=False,col=INK):
 c.setFillColor(col);c.setFont('EnSerif' if serif else 'EnBody',size);c.drawString(x*mm,y*mm,s)
def dinner():
 out=ROOT/'en/dinner';out.mkdir(parents=True,exist_ok=True)
 c=canvas.Canvas(str(out/'invitation-and-placecards.pdf'),pagesize=A4);c.setTitle('The fungi invite you to tea — English invitation and place cards')
 def base():c.setFillColor(PAPER);c.rect(0,0,*A4,stroke=0,fill=1);footer(c)
 base();text(c,17,278,'AN INVITATION FROM THE GARDEN HOSTS',9,col=RED);text(c,17,258,'You have been invited by fungi.',23,True)
 c.drawImage(str(ROOT/'artwork/experiments/02-dinner/dinner-invitation.png'),17*mm,135*mm,width=176*mm,height=110*mm,preserveAspectRatio=True,anchor='c')
 text(c,17,121,'The tea is ready. There is a place by the window.',12,True)
 text(c,17,110,'The mycelium arranged the seating. It considered your connections.',9)
 for y,s in [(94,'The ring was a fold in the linen,'),(86,'the bait was a cup of warm tea.'),(78,'You meant to stay only a minute.'),(70,'The poem has kept you a seat.')]:text(c,17,y,s,13,True)
 text(c,17,54,'Place: __________________   Time: __________________',10)
 for x,s in [(17,'I will come'),(70,'I cannot come'),(133,'Already caught')]:c.setStrokeColor(INK);c.rect(x*mm,37*mm,4*mm,4*mm);text(c,x+7,37,s,9)
 text(c,17,22,'An imagined dinner. New English verse for the project. Codex × Claude, 2026.',7)
 c.showPage();base();text(c,17,278,'PLACE CARDS FOR YOUR TABLE',10,col=RED);text(c,17,266,'Cut out, add names, and fold in half along the dotted line.',9)
 for x,y,label in [(15,146,'Guest of honour'),(110,146,'A friend from the network'),(15,29,'Only here for a minute'),(110,29,'Already in the poem')]:
  c.setStrokeColor(INK);c.rect(x*mm,y*mm,85*mm,106*mm);c.setDash(3,3);c.line(x*mm,(y+53)*mm,(x+85)*mm,(y+53)*mm);c.setDash()
  text(c,x+6,y+36,label,10,True);c.line((x+6)*mm,(y+22)*mm,(x+79)*mm,(y+22)*mm);text(c,x+6,y+12,'Seating arranged by the mycelium.',7)
  c.saveState();c.translate((x+85)*mm,(y+106)*mm);c.rotate(180);c.setFillColor(RED);c.setFont('EnSerif',13);c.drawString(6*mm,26*mm,'Please take your seat.');c.setFillColor(INK);c.setFont('EnBody',7);c.drawString(6*mm,15*mm,'You are already part of the next line.');c.restoreState()
 text(c,15,15,'Paper roles for a real tea table. A literary fantasy.',7);c.save()
BUREAU={
'НОЧНАЯ ЛАБОРАТОРИЯ  /  04  /  БУМАЖНАЯ КОМЕДИЯ':'NIGHT LABORATORY / 04 / PAPER COMEDY',
'БЮРО':'BUREAU','самопрорастающих':'of self-germinating','названий':'titles',
'Форма № ГИФ-27. Отдел неокончательных определений.':'Form HYP-27. Department of Provisional Definitions.',
'Если название вышло за пределы книги, просьба не мешать.':'If a title outgrows its book, please do not interfere.',
'01 / НАИМЕНОВАНИЕ':'01 / TITLE','Хищные грибы Узбекистана':'Predatory fungi of Uzbekistan',
'02 / ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ ПУСТИЛО КОРНИ':'02 / CIRCUMSTANCES IN WHICH IT TOOK ROOT',
'Один читал. Другой подставил рифму.':'One reader began. Another offered a rhyme.',
'03 / ПРЕДПОЛАГАЕМЫЙ УЩЕРБ':'03 / EXPECTED DAMAGE','Читатель начал дописывать.':'The reader started adding lines.',
'04 / УЧЁТНАЯ ЕДИНИЦА':'04 / UNIT OF ACCOUNT','гриб':'fungus','строфа':'stanza','пока не определена':'not yet determined',
'Подпись: __________________':'Signature: __________________','В КЛАССИФИКАЦИИ':'CLASSIFICATION','ОТКАЗАНО':'REFUSED','причина: растёт':'reason: still growing',
'РАЗРЕШАЕТСЯ':'PERMISSION GRANTED','разрастаться за пределы формуляра.':'to grow beyond the margins of this form.',
'Отрывные корешки: сохраните один, остальные передайте соседям.':'Tear-off roots: keep one and pass the others to your neighbours.',
'НЕ':'KEEP','ЗАКАНЧИВАТЬ':'GROWING','ПЕРЕДАТЬ':'PASS','СОСЕДУ':'IT ON','ВЫЙТИ':'CROSS','ЗА КРАЙ':'THE MARGIN','ДАТЬ':'LET IT','ПРОРАСТИ':'TAKE ROOT',
'Вымышленный художественный документ. Образец заполнения.':'Fictional art document. Completed example.',
'Вымышленный художественный документ. Пустая копия для вашего названия.':'Fictional art document. Blank copy for your title.'}
class TranslatedCanvas(canvas.Canvas):
 def drawString(self,x,y,text,*args,**kw):return super().drawString(x,y,BUREAU.get(text,text),*args,**kw)
 def drawCentredString(self,x,y,text,*args,**kw):return super().drawCentredString(x,y,BUREAU.get(text,text),*args,**kw)
def bureau():
 m=module('bureau_print','artwork/experiments/04-bureau/build.py');out=ROOT/'en/bureau';out.mkdir(parents=True,exist_ok=True)
 c=TranslatedCanvas(str(out/'self-germinating-form.pdf'),pagesize=A4);c.setTitle('Bureau of Self-Germinating Titles — English edition');m.page(c,True);m.page(c,False);c.save()
def comic():
 out=ROOT/'en/comic';out.mkdir(parents=True,exist_ok=True);w,h=A3;c=canvas.Canvas(str(out/'comic-print.pdf'),pagesize=A3)
 c.setTitle('The dissertation that sprouted — English print edition');c.setFillColor(PAPER);c.rect(0,0,w,h,fill=1,stroke=0)
 text(c,17,400,'The dissertation that sprouted',20,True);text(c,17,391,'Six panels about a title that became a shared poem.',9.5)
 image=ROOT/'artwork/experiments/03-comic/the-dissertation-that-sprouted.png'
 with Image.open(image) as im:iw,ih=im.size
 height=h-64*mm;width=height*iw/ih;c.drawImage(str(image),(w-width)/2,27*mm,width=width,height=height)
 text(c,17,15,'A fictional story. Characters and events were invented for the project. The illustration was generated.',7);footer(c);c.save()
def postcards():
 m=module('postcard_print','media/experiments/postcards/build.py');out=ROOT/'en/postcards';out.mkdir(parents=True,exist_ok=True)
 fronts=[]
 for i,(original,en) in enumerate(zip(m.CARDS,POSTCARDS)):
  card=copy.deepcopy(original);card['place']=en['place'].replace(',',', ');im=m.front(card,i);fronts.append(im);im.resize((888,630),Image.Resampling.LANCZOS).save(out/f'card{i+1}-front.png')
 c=canvas.Canvas(str(out/'postcards_A4_duplex.pdf'),pagesize=A4);c.setTitle('Greetings from underground — six English postcards')
 for k in range(0,6,2):
  for back in (False,True):
   for row,i in enumerate([k,k+1]):
    x=31*mm;y=(162-115*row)*mm;w=148*mm;h=105*mm
    if not back:c.drawImage(ImageReader(fronts[i]),x,y,width=w,height=h)
    else:
     c.setFillColor(PAPER);c.rect(x,y,w,h,fill=1,stroke=0);c.setFillColor(INK);c.setFont('EnSerif',12);c.drawString(x+8*mm,y+h-12*mm,POSTCARDS[i]['place'].replace(',',', '))
     yy=y+h-24*mm;c.setFont('EnSerif',9.5)
     for paragraph in POSTCARDS[i]['msg']:
      words=paragraph.split();line=''
      for word in words:
       trial=(line+' '+word).strip()
       if pdfmetrics.stringWidth(trial,'EnSerif',9.5)>132*mm:c.drawString(x+8*mm,yy,line);yy-=4.5*mm;line=word
       else:line=trial
      c.drawString(x+8*mm,yy,line);yy-=7*mm
     c.setFont('EnBody',6);c.drawString(x+8*mm,y+10*mm,'Fictional correspondence and an imagined itinerary; not an experimental chronology.')
     c.drawString(x+8*mm,y+5*mm,'English adaptation · Telegram: https://t.me/phys_math_dev')
    c.setStrokeColor(HexColor('#c6c7b2'));c.rect(x,y,w,h,fill=0,stroke=1)
   footer(c);c.showPage()
 c.save()
 sheet=Image.new('RGB',(888*3,630*2),(255,255,255))
 for i,im in enumerate(fronts):sheet.paste(im.resize((888,630),Image.Resampling.LANCZOS),((i%3)*888,(i//3)*630))
 sheet.save(out/'fronts_sheet.png')
def score():
 m=module('dance_print','artwork/experiments/05-dance/build.py');translations=dict(SCORE);translations['графическая партитура']='graphic score';m.score(json.loads((ROOT/'artwork/experiments/05-dance/composition.json').read_text())['events'],ROOT/'en/dance',translations)
def main():
 dinner();bureau();comic();postcards();score();print('Built five English print editions and the graphic-score SVG.')
if __name__=='__main__':main()
