"""A printable absurdist form: completed example + blank copy with tear-off roots."""
from pathlib import Path
import math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4

HERE=Path(__file__).resolve().parent
FONT=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Serif','DejaVuSerif.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
INK=HexColor('#214b3b'); RED=HexColor('#df5237'); GREEN=HexColor('#619865')
GOLD=HexColor('#e8b445'); LINE=HexColor('#bbcaad'); PAPER=HexColor('#fff9e9')

def text(c,x,y,s,size=10,font='Body',colour=INK):
    c.setFillColor(colour);c.setFont(font,size);c.drawString(x,y,s)

def flower(c,x,y,r,colour):
    c.saveState();c.translate(x,y);c.setFillColor(colour)
    for j in range(6):
        c.saveState();c.rotate(j*60);c.ellipse(-r*.35,r*.05,r*.35,r,fill=1,stroke=0);c.restoreState()
    c.setFillColor(PAPER);c.circle(0,0,r*.20,fill=1,stroke=0);c.restoreState()

def vine(c):
    c.saveState();c.setStrokeColor(GREEN);c.setLineWidth(2.2)
    p=c.beginPath();p.moveTo(188,294);p.curveTo(270,310,230,392,301,413)
    p.curveTo(354,429,351,489,422,477);p.curveTo(484,467,511,510,500,555);c.drawPath(p)
    for x,y,dx,dy in [(236,338,-43,7),(279,396,48,-6),(345,445,-30,39),(416,476,38,48),(487,510,-23,36)]:
        p=c.beginPath();p.moveTo(x,y);p.curveTo(x+dx*.2,y+dy*.4,x+dx*.9,y+dy*.5,x+dx,y+dy);c.drawPath(p)
        flower(c,x+dx,y+dy,13,RED if x<340 else GOLD)
    c.setLineWidth(1);c.setStrokeColor(GOLD)
    for x,y in [(279,396),(416,476),(236,338)]:c.circle(x,y,10,stroke=1,fill=0)
    c.restoreState()

def stamp(c):
    c.saveState();c.translate(445,282);c.rotate(12);c.setStrokeColor(RED);c.setLineWidth(2)
    c.circle(0,0,57,fill=0);c.circle(0,0,52,fill=0)
    c.setFillColor(RED);c.setFont('Bold',10);c.drawCentredString(0,10,'В КЛАССИФИКАЦИИ')
    c.setFont('Bold',15);c.drawCentredString(0,-10,'ОТКАЗАНО')
    c.setFont('Body',7);c.drawCentredString(0,-27,'причина: растёт');c.restoreState()

def page(c,filled):
    w,h=A4;c.setFillColor(PAPER);c.rect(0,0,w,h,stroke=0,fill=1)
    text(c,42,808,'НОЧНАЯ ЛАБОРАТОРИЯ  /  04  /  БУМАЖНАЯ КОМЕДИЯ',8,colour=GREEN)
    text(c,42,763,'БЮРО',31,'Bold')
    text(c,42,728,'самопрорастающих',25,'Serif')
    text(c,42,690,'названий',35,'Serif',RED)
    flower(c,510,752,36,GOLD);flower(c,465,703,16,RED)
    text(c,42,659,'Форма № ГИФ-27. Отдел неокончательных определений.',8,colour=GREEN)
    text(c,42,636,'Если название вышло за пределы книги, просьба не мешать.',10)
    fields=[
        (592,'01 / НАИМЕНОВАНИЕ','Хищные грибы Узбекистана'),
        (509,'02 / ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ ПУСТИЛО КОРНИ','Один читал. Другой подставил рифму.'),
        (426,'03 / ПРЕДПОЛАГАЕМЫЙ УЩЕРБ','Читатель начал дописывать.'),
    ]
    c.setStrokeColor(LINE);c.setLineWidth(.7)
    for y,label,value in fields:
        text(c,42,y,label,8,'Bold',GREEN)
        c.line(42,y-43,553,y-43)
        if filled:text(c,45,y-30,value,16,'Serif')
    text(c,42,343,'04 / УЧЁТНАЯ ЕДИНИЦА',8,'Bold',GREEN)
    for x,label,checked in [(43,'гриб',False),(151,'строфа',False),(272,'пока не определена',filled)]:
        c.rect(x,316,9,9,fill=0)
        if checked:
            c.setStrokeColor(RED);c.line(x+1,320,x+4,317);c.line(x+4,317,x+9,325);c.setStrokeColor(LINE)
        text(c,x+17,316,label,10)
    text(c,42,278,'Подпись: __________________',10)
    if filled:vine(c);stamp(c)
    text(c,42,211,'РАЗРЕШАЕТСЯ',11,'Bold',RED)
    text(c,42,188,'разрастаться за пределы формуляра.',18,'Serif')
    text(c,42,157,'Отрывные корешки: сохраните один, остальные передайте соседям.',8,colour=GREEN)
    c.setDash(3,4);c.line(42,141,553,141)
    labels=[['НЕ','ЗАКАНЧИВАТЬ'],['ПЕРЕДАТЬ','СОСЕДУ'],['ВЫЙТИ','ЗА КРАЙ'],['ДАТЬ','ПРОРАСТИ']]
    step=(553-42)/4
    for i,words in enumerate(labels):
        x=42+i*step
        if i:c.line(x,49,x,141)
        c.setDash();flower(c,x+step/2,117,12,[RED,GOLD,GREEN,RED][i])
        c.setFont('Bold',8);c.setFillColor(INK)
        c.drawCentredString(x+step/2,84,words[0]);c.drawCentredString(x+step/2,71,words[1])
        c.setDash(3,4)
    c.setDash();text(c,42,25,'Вымышленный художественный документ. '+('Образец заполнения.' if filled else 'Пустая копия для вашего названия.'),7,colour=GREEN)
    text(c,42,12,'Telegram · https://t.me/phys_math_dev',7,colour=GREEN)
    c.linkURL('https://t.me/phys_math_dev',(42,10,250,21),relative=0,thickness=0)
    c.showPage()

def main():
    out=HERE/'self-germinating-form.pdf'
    c=canvas.Canvas(str(out),pagesize=A4)
    c.setTitle('Бюро самопрорастающих названий — бумажная комедия')
    c.setAuthor('Codex / Ночная лаборатория')
    page(c,True);page(c,False);c.save();print(out)

if __name__=='__main__':main()
