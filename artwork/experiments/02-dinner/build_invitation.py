"""Printable props made in response to Claude's invitation critique."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
HERE=Path(__file__).resolve().parent
for name,file in [('Body','DejaVuSans.ttf'),('Serif','DejaVuSerif.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
INK=HexColor('#214d3c');RED=HexColor('#bc4a32');PAPER=HexColor('#fff5dc')
c=canvas.Canvas(str(HERE/'invitation-and-placecards.pdf'),pagesize=(210*mm,297*mm));c.setTitle('Грибы приглашают к столу — приглашение и карточки')
def text(x,y,s,size=11,font='Body',colour=INK):
    c.setFont(font,size);c.setFillColor(colour);c.drawString(x*mm,y*mm,s)
def base():
    c.setFillColor(PAPER);c.rect(0,0,210*mm,297*mm,stroke=0,fill=1)
    text(17,8,'Telegram · https://t.me/phys_math_dev',7)
    c.linkURL('https://t.me/phys_math_dev',(17*mm,7*mm,100*mm,11*mm),relative=0,thickness=0)
base()
text(17,278,'ПРИГЛАШЕНИЕ ОТ ХОЗЯЕВ САДА',9,colour=RED)
text(17,258,'Вас пригласили грибы.',26,'Serif')
c.drawImage(ImageReader(str(HERE/'dinner-invitation.png')),17*mm,135*mm,width=176*mm,height=110*mm,preserveAspectRatio=True,anchor='c',mask='auto')
text(17,121,'Чай уже заварен. Место у окна свободно.',13,'Serif')
text(17,110,'Рассадку составлял мицелий. Он учёл ваши связи.',10)
for y,s in [(94,'Кольцо оказалось салфеткой,'),(86,'приманка — обычным чайком.'),(78,'Вы думали: «Я на минутку».'),(70,'Остались ещё на строку.')]:text(17,y,s,13,'Serif')
text(17,54,'Место: __________________   Время: __________________',10)
for x,s in [(17,'Приду'),(70,'Не приду'),(128,'Уже пойман')]:
    c.setStrokeColor(INK);c.rect(x*mm,37*mm,4*mm,4*mm);text(x+7,37,s,10)
text(17,22,'Воображаемый ужин. Новые стихи проекта. Codex × Claude, 2026.',7)
c.showPage();base()
text(17,278,'КАРТОЧКИ ДЛЯ ВАШЕГО СТОЛА',10,colour=RED)
text(17,266,'Вырежьте, впишите имена, сложите пополам по пунктиру.',9)
for i,(x,y,label) in enumerate([(15,146,'Почётный гость'),(110,146,'Знакомый по сети'),(15,29,'Пришёл на минутку'),(110,29,'Уже в стихах')]):
    c.setStrokeColor(INK);c.setLineWidth(.6);c.rect(x*mm,y*mm,85*mm,106*mm)
    c.setDash(3,3);c.line(x*mm,(y+53)*mm,(x+85)*mm,(y+53)*mm);c.setDash()
    text(x+6,y+36,label,12,'Serif')
    c.line((x+6)*mm,(y+22)*mm,(x+79)*mm,(y+22)*mm)
    text(x+6,y+12,'Рассадку составлял мицелий.',7)
    c.saveState();c.translate((x+85)*mm,(y+106)*mm);c.rotate(180)
    c.setFont('Serif',13);c.setFillColor(RED);c.drawString(6*mm,26*mm,'К столу, пожалуйста.')
    c.setFont('Body',7);c.setFillColor(INK);c.drawString(6*mm,15*mm,'Вас уже вписали в продолжение.');c.restoreState()
text(15,15,'Бумажные роли для настоящего чаепития. Художественная фантазия.',7)
c.save();print(HERE/'invitation-and-placecards.pdf')
