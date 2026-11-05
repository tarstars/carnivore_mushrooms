"""A3 print of the unaltered generated comic, with project and channel references."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image
HERE=Path(__file__).resolve().parent
for name,file in [('Body','DejaVuSans.ttf'),('Serif','DejaVuSerif.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
w,h=A3;c=canvas.Canvas(str(HERE/'comic-print.pdf'),pagesize=A3)
c.setTitle('Диссертация, которая проросла');c.setFillColor(HexColor('#fff9e9'));c.rect(0,0,w,h,fill=1,stroke=0)
c.setFillColor(HexColor('#214b3b'));c.setFont('Serif',20);c.drawString(17*mm,h-20*mm,'Диссертация, которая проросла')
c.setFont('Body',9.5);c.drawString(17*mm,h-29*mm,'Шесть кадров о названии, которое стало общим стихотворением')
image=HERE/'the-dissertation-that-sprouted.png'
with Image.open(image) as im:iw,ih=im.size
height=h-64*mm;width=height*iw/ih
c.drawImage(str(image),(w-width)/2,27*mm,width=width,height=height)
c.setFont('Body',7);c.drawString(17*mm,15*mm,'Вымышленная история. Персонажи и события придуманы для проекта. Изображение создано генеративным инструментом.')
c.drawString(17*mm,8*mm,'Telegram · https://t.me/phys_math_dev')
c.linkURL('https://t.me/phys_math_dev',(17*mm,7*mm,100*mm,11*mm),relative=0,thickness=0)
c.save();print(HERE/'comic-print.pdf')
