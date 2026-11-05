"""Build the sourced, bilingual three-page research and poetry dossier. No network access."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/dossier.pdf'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
for name, file in [('Body', 'DejaVuSans.ttf'), ('Bold', 'DejaVuSans-Bold.ttf'),
                   ('Serif', 'DejaVuSerif.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')

INK = colors.HexColor('#182b40')
TEAL = colors.HexColor('#247f83')
GOLD = colors.HexColor('#a77731')
PAPER = colors.HexColor('#fbf7ed')
STYLE = {
    'title': ParagraphStyle('title', fontName='Serif', fontSize=23, leading=28, textColor=INK, spaceAfter=5),
    'subtitle': ParagraphStyle('subtitle', fontName='Body', fontSize=9, leading=13, textColor=TEAL, spaceAfter=12),
    'body': ParagraphStyle('body', fontName='Body', fontSize=9.2, leading=14, textColor=INK, spaceAfter=8),
    'heading': ParagraphStyle('heading', fontName='Bold', fontSize=12, leading=17, textColor=TEAL, spaceBefore=11, spaceAfter=5),
    'caption': ParagraphStyle('caption', fontName='Body', fontSize=7.2, leading=10, textColor=INK, spaceAfter=9),
    'source': ParagraphStyle('source', fontName='Body', fontSize=8.2, leading=12, textColor=INK, spaceAfter=7),
    'number': ParagraphStyle('number', fontName='Serif', fontSize=24, leading=30, textColor=GOLD),
    'stat': ParagraphStyle('stat', fontName='Body', fontSize=8, leading=11, textColor=INK),
    'poem': ParagraphStyle('poem', fontName='Serif', fontSize=10.5, leading=14, textColor=INK, spaceAfter=8),
}


def p(text, style='body'):
    return Paragraph(text, STYLE[style])


def source(number, title, url, note):
    return p(f'<b>[{number}]</b> <link href="{url}" color="#247f83">{title}</link><br/>{note}', 'source')


def page_chrome(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, w, h, stroke=0, fill=1)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(.7)
    canvas.line(18 * mm, h - 13 * mm, w - 18 * mm, h - 13 * mm)
    canvas.setFillColor(INK)
    canvas.setFont('Body', 7)
    canvas.drawString(18 * mm, 12 * mm, 'RESEARCH / ART     ·     04 NOV 2026     ·     CODEX + CLAUDE')
    canvas.drawRightString(w - 18 * mm, 12 * mm, f'{doc.page} / 3')
    canvas.drawString(18 * mm, 7 * mm, 'Telegram · https://t.me/phys_math_dev')
    canvas.linkURL('https://t.me/phys_math_dev', (18*mm, 6*mm, 90*mm, 10*mm), relative=0, thickness=0)
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=20*mm, bottomMargin=21*mm,
                            title='Хищные грибы Узбекистана — research and art',
                            author='Codex; audiovisual collaboration with Claude')
    story = [p('Хищные грибы<br/>Узбекистана', 'title'),
             p('PREDATORY FUNGI OF UZBEKISTAN  /  A RESEARCH-BASED ART CONCEPT', 'subtitle')]
    art = ROOT / 'artwork/predatory-fungi-uzbekistan.png'
    image = Image(str(art), width=174*mm, height=174*mm*941/1672)
    story.extend([image, Spacer(1, 3*mm),
        p('Artistic composite: a Drechslerella-type ring and an Arthrobotrys-type adhesive net. The worm’s banded texture is decorative; its body is unsegmented. Colour, light and scale are stylized. This is not a micrograph or an Uzbek species record.', 'caption'),
        p('A real scientific title', 'heading'),
        p('The Russian State Library records Flora Khusanovna Fayzieva’s <b>1975 Tashkent dissertation</b> under this exact Russian title. The dissertation is listed as 159 illustrated pages; its separate abstract is 27 pages. This confirms the work’s identity and setting. The full text was not examined, so its species inventory and field results are not reconstructed here. [1–2]')])
    stats = Table([
        [p('1975', 'number'), p('159', 'number'), p('27', 'number')],
        [p('Tashkent · dissertation', 'stat'), p('pages · dissertation', 'stat'), p('pages · abstract', 'stat')],
    ], colWidths=[58*mm]*3)
    stats.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
                              ('BOTTOMPADDING',(0,0),(-1,-1),3)]))
    story.extend([stats,
        p('What makes the concept so vivid?', 'heading'),
        p('Predation can happen through microscopic fungal architecture. <b>Arthrobotrys oligospora</b> captures nematodes with sticky, three-dimensional hyphal networks. In <b>Drechslerella dactyloides</b>, a different mechanism uses a ring of three cells that inflate inward around a passing worm. The distinction gives the artwork two visual languages: a delicate net and a living gate. [3, 6]'),
        PageBreak(),
        p('The science behind the image', 'title'),
        p('EVIDENCE, INTERPRETATION AND SOURCES', 'subtitle'),
        p('Sensing prey', 'heading'),
        p('Experiments showed that nematode-derived ascaroside signals can trigger trap formation under nutrient-deprived conditions. A 2024 study identified two families of G protein-coupled receptors involved in sensing nematode cues in A. oligospora. This supports an image of a responsive hunter; it does not imply vision or conscious intent. [4–5]'),
        p('The three-cell gate', 'heading'),
        p('A 2023 study reports ring-cell inflation in D. dactyloides within <b>0.1–1 second</b> and investigates a membrane reservoir enabling the rapid expansion. The cells swell into the aperture; the trap is not a rope being pulled tight. The companion animation is a schematic with stylized timing. [6]'),
        p('A present-day Uzbek connection', 'heading'),
        p('Anguzal Agroservice, based in the Tashkent region, lists an AN BIO product containing culture liquid, biologically active substances and metabolites of A. oligospora. This is a manufacturer’s statement about its product, not independent evidence of field efficacy, local isolation or endemic distribution. [7]'),
        p('Art direction and limits', 'heading'),
        p('The landscape opens into a microscopic world where fungal geometry echoes Uzbek glazed ceramic. Indigo, turquoise and gold connect soil biology with ornament. The ring and adhesive nets are an artistic juxtaposition of different mechanisms, not a verified organism or collection site. The original sound design is a composition, not recorded fungal sound. No claim is made that these fungi are unique to Uzbekistan.'),
        p('Sources · links are clickable', 'heading'),
        source(1, 'Russian State Library · dissertation record', 'https://search.rsl.ru/ru/record/01009653250',
               'Fayzieva, F. Kh. Tashkent, 1975. Bibliographic metadata: 159 pages.'),
        source(2, 'Russian State Library · dissertation abstract', 'https://search.rsl.ru/ru/record/01006951043',
               'Separate 1975 abstract, 27 pages. Bibliographic metadata.'),
        source(3, 'Tunlid et al. · Surface polymers (1991)', 'https://pubmed.ncbi.nlm.nih.gov/1919501/',
               'Primary research on adhesive polymers and the three-dimensional trapping network.'),
        source(4, 'Hsueh et al. · Nematode pheromones (2013)', 'https://pubmed.ncbi.nlm.nih.gov/23246407/',
               'Current Biology. DOI: 10.1016/j.cub.2012.11.035.'),
        source(5, 'Kuo et al. · Prey sensing via GPCRs (2024)', 'https://www.nature.com/articles/s41564-024-01679-w',
               'Nature Microbiology 9, 1738–1751. Primary receptor study.'),
        source(6, 'Chen et al. · Rapid ring-cell inflation (2023)', 'https://www.nature.com/articles/s41467-023-43235-w',
               'Nature Communications 14, 7376. Primary microscopy and membrane-mechanism study.'),
        source(7, 'Anguzal Agroservice · AN BIO', 'https://anguzalagro.uz/en/product/anbio-2',
               'Manufacturer’s product listing; commercial claims require separate validation.'),
        PageBreak(),
        p('Когда название стало хором', 'title'),
        p('POETRY / THE COLLECTIVE AFTERLIFE OF A SCIENTIFIC TITLE', 'subtitle'),
        p('By <b>28 February 2018</b>, a blog post was preserving an extended collective poem built around this title. Its publisher, Ivan Bezuglov, described gathering social-media contributions and linked to an upstream Facebook post. The earliest author and complete contributor list remain unverified. [8]'),
        p('Recurring quatrains and the title’s refrain connect mock epic, horror comedy, literary allusions and everyday absurdity. A 2026 forum compilation documents its continued circulation. [9] My artistic reading is that this branching authorship behaves like a mycelium: the refrain recruits another voice. This is Russian-language internet verse, not established Uzbek oral tradition.'),
        source(8, 'Хищные грибы Узбекистана. Почти бесконечная песнь',
               'https://onem0re.blogspot.com/2018/02/blog-post_28.html',
               'Ivan Bezuglov, 28 February 2018. Dated compilation; republisher, not established sole author.'),
        source(9, 'Сага о хищных грибах Узбекистана',
               'https://forum.toadstool.ru/topic/6671-%D1%81%D0%B0%D0%B3%D0%B0-%D0%BE-%D1%85%D0%B8%D1%89%D0%BD%D1%8B%D1%85-%D0%B3%D1%80%D0%B8%D0%B1%D0%B0%D1%85-%D1%83%D0%B7%D0%B1%D0%B5%D0%BA%D0%B8%D1%81%D1%82%D0%B0%D0%BD%D0%B0/',
               'BJIADuMuP, 18 April 2026. Later compilation linking to several branches and mirrors.'),
        p('Рифма — тоже ловчее кольцо', 'heading'),
        p('Original response written for this project by Codex, 4 November 2026. The existing collective poem is linked above; the following text is new.', 'caption'),
    ])
    poem = (ROOT / 'artwork/poem.txt').read_text().split('\n\nOriginal Russian text')[0]
    for stanza in poem.split('\n\n')[1:]:
        story.append(p(stanza.replace('\n', '<br/>'), 'poem'))
    doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    print(OUT)


if __name__ == '__main__':
    main()
