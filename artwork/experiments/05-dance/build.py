"""An original cheerful 7/8 miniature, synthesized audio, editable MIDI and graphic score."""
from pathlib import Path
import json, math, struct, wave
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

HERE=Path(__file__).resolve().parent
SR=44100;BPM=152;BARS=32;EIGHTH=60/BPM/2;TICKS=480;BAR=7*TICKS//2
MOTIFS=[
    [62,66,69,67,66,64,62],
    [62,66,69,71,69,67,64],
    [69,72,74,72,69,67,66],
    [67,66,64,62,64,66,62],
]

def arrangement():
    notes=[]
    def add(track,bar,pos,length,note,velocity):
        if bar==BARS-1:length=min(length,7-pos)
        notes.append({'track':track,'bar':bar,'beat':pos,'length':length,'note':note,'velocity':velocity})
    for bar in range(BARS):
        motif=MOTIFS[(bar//2)%4]
        if 24<=bar<28:motif=[66,67,66,67,66,64,62] # a playful caught phrase
        if bar==31:motif=[67,66,64,62,62,62,62]
        for i,n in enumerate(motif):
            length=.92 if i==6 and bar%4==3 else .78
            if bar==31 and i>3:continue
            add('melody',bar,i,length,n+(12 if 12<=bar<24 else 0),84 if i in (0,3,5) else 66)
        bass=38 if (bar//4)%2==0 else 43
        for pos,n in [(0,bass),(3,bass+7),(5,bass+12)]:add('bass',bar,pos,1.5,n,62)
        for pos in range(7):add('drums',bar,pos,.15,36 if pos==0 else 37 if pos in (3,5) else 42,66 if pos in (0,3,5) else 29)
        if 4<=bar<28:
            for i in (1,3,5):add('answer',bar,i,.86,motif[(i+2)%7]+12,51)
        if 12<=bar<24 or bar>=28:
            for pos,n in [(0,74),(3,78),(5,81)]:add('bell',bar,pos,2.2,n,45)
    return notes

def variable(n):
    b=[n&127];n>>=7
    while n:b.insert(0,(n&127)|128);n>>=7
    return bytes(b)

def meta(kind,data):return bytes([255,kind])+variable(len(data))+data

def midi(notes):
    tracks=[]
    conductor=[(0,meta(3,b'Dance of three cells / 3+2+2')),
               (0,meta(0x51,int(60_000_000/BPM).to_bytes(3,'big'))),
               (0,meta(0x58,bytes([7,3,24,8]))),
               (0,meta(1,b'Original invented miniature; not traditional Uzbek music.'))]
    def encode(events):
        events=sorted(enumerate(events),key=lambda p:(p[1][0],p[0]));out=b'';last=0
        for _,(t,data) in events:out+=variable(t-last)+data;last=t
        out+=variable(max(0,BARS*BAR-last))+meta(0x2f,b'')
        return b'MTrk'+struct.pack('>I',len(out))+out
    tracks.append(encode(conductor))
    for name,ch,program in [('melody',0,24),('answer',1,12),('bass',2,32),('bell',3,10),('drums',9,None)]:
        events=[(0,meta(3,name.encode()))]
        if program is not None:events.append((0,bytes([0xc0|ch,program])))
        for n in notes:
            if n['track']!=name:continue
            tick=int(n['bar']*BAR+n['beat']*TICKS/2);end=tick+int(n['length']*TICKS/2)
            events.extend([(tick,bytes([0x90|ch,n['note'],n['velocity']])),(end,bytes([0x80|ch,n['note'],0]))])
        tracks.append(encode(events))
    (HERE/'dance-of-three-cells.mid').write_bytes(b'MThd'+struct.pack('>IHHH',6,1,len(tracks),TICKS)+b''.join(tracks))

def sound(notes):
    duration=BARS*7*EIGHTH+3
    mix=np.zeros((int(duration*SR),2),np.float64)
    rng=np.random.default_rng(2732)
    cache={}
    def sample(kind,note,length):
        key=(kind,note,round(length,3))
        if key in cache:return cache[key]
        f=440*2**((note-69)/12)
        dur=max(.5,length*EIGHTH+(.8 if kind!='bass' else 1.1))
        t=np.arange(int(dur*SR))/SR
        if kind=='drums':
            t=np.arange(int(.3*SR))/SR
            if note==36:
                phase=2*np.pi*(70*t+14*.035*(1-np.exp(-t/.035)))
                s=np.sin(phase)*np.exp(-t/.080)*.8
            elif note==37:s=(np.sin(2*np.pi*1050*t)+.5*np.sin(2*np.pi*1680*t))*np.exp(-t/.018)*.35
            else:s=rng.normal(0,1,len(t))*np.exp(-t/.014)*.11
        else:
            s=np.zeros_like(t)
            if kind=='bell':
                for h,r in enumerate([1,2.37,4.13,5.61]):s+=np.sin(2*np.pi*f*r*t+.3*h)/(h+1)**1.5*np.exp(-t*(2.8+h*2))
                s*=.32
            else:
                for h in range(1,10 if kind!='bass' else 5):
                    s+=np.sin(2*np.pi*f*h*t+.1*h)*np.exp(-t*(2.0+h*1.5))/(h**1.45)
                s*=.53 if kind=='bass' else .42 if kind=='answer' else .60
                s+=rng.normal(0,1,len(t))*np.exp(-t/.008)*.025
            s*=1-np.exp(-t/.0025)
        cache[key]=s;return s
    pans={'melody':-.20,'answer':.48,'bass':-.12,'bell':.23,'drums':0}
    for n in notes:
        start=(n['bar']*7+n['beat'])*EIGHTH
        # consistent tiny timing differences keep the ensemble lively without drifting.
        start+=0 if n['track']=='drums' else .003*math.sin(n['bar']*1.7+n['beat'])
        i=max(0,int(start*SR));s=sample(n['track'],n['note'],n['length'])*(n['velocity']/100)
        m=min(len(s),len(mix)-i);pan=pans[n['track']]
        mix[i:i+m,0]+=s[:m]*math.sqrt((1-pan)/2)
        mix[i:i+m,1]+=s[:m]*math.sqrt((1+pan)/2)
    for seconds,gain in [(.079,.10),(.173,.075),(.301,.045)]:
        delay=int(seconds*SR);mix[delay:,0]+=mix[:-delay,1].copy()*gain;mix[delay:,1]+=mix[:-delay,0].copy()*gain
    t=np.arange(len(mix))/SR
    mix*=np.minimum(1,t/.35)[:,None]*np.minimum(1,(duration-t)/1.8)[:,None]
    mix=np.tanh(mix*1.2);mix*=.5/(np.max(np.abs(mix))+1e-9)
    pcm=(mix*32767).astype('<i2')
    with wave.open(str(HERE/'dance-of-three-cells.wav'),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes())
    return duration

def score(notes):
    W,H=1600,1050
    out=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050">',
         '<rect width="1600" height="1050" fill="#fff9e9"/>',
         '<text x="70" y="65" fill="#417a58" font-family="sans-serif" font-size="14" letter-spacing="3">НОЧНАЯ ЛАБОРАТОРИЯ / 05 / СЛУШАТЬ</text>',
         '<text x="70" y="135" fill="#214b3b" font-family="Georgia,serif" font-size="56">Танец трёх клеток</text>',
         '<text x="74" y="177" fill="#df5237" font-family="sans-serif" font-size="22">7/8  ·  3 + 2 + 2  ·  ♩ = 152  ·  три голоса учатся продолжать друг друга</text>']
    pdfmetrics.registerFont(TTFont('DanceSerif','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
    pdfmetrics.registerFont(TTFont('DanceBody','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    c=canvas.Canvas(str(HERE/'graphic-score.pdf'),pagesize=(800,525));c.setTitle('Танец трёх клеток — графическая партитура')
    c.setFillColor(HexColor('#fff9e9'));c.rect(0,0,800,525,stroke=0,fill=1)
    def txt(x,y,s,size,colour='#214b3b',serif=False):
        c.setFont('DanceSerif' if serif else 'DanceBody',size/2);c.setFillColor(HexColor(colour));c.drawString(x/2,(H-y)/2,s)
    txt(70,65,'НОЧНАЯ ЛАБОРАТОРИЯ / 05 / СЛУШАТЬ',14,'#417a58')
    txt(70,135,'Танец трёх клеток',56,serif=True)
    txt(74,177,'7/8 · 3 + 2 + 2 · четверть = 152',22,'#df5237')
    legend='Красный — мелодия; зелёный — ответ. Семь долей: хлопните 3 + 2 + 2.'
    out.append(f'<text x="74" y="213" fill="#417a58" font-family="sans-serif" font-size="18">{legend}</text>')
    txt(74,213,legend,18,'#417a58')
    for bar in range(BARS):
        row,col=divmod(bar,8);x=70+col*184;y=248+row*181
        for a,b,colour in [(0,3,'#eaf0d3'),(3,5,'#fae7b7'),(5,7,'#f7d8c5')]:
            xx=x+a*23;ww=(b-a)*23
            out.append(f'<rect x="{xx}" y="{y}" width="{ww}" height="116" fill="{colour}"/>')
            c.setFillColor(HexColor(colour));c.rect(xx/2,(H-y-116)/2,ww/2,58,stroke=0,fill=1)
        for n in [n for n in notes if n['bar']==bar and n['track'] in ('melody','answer')]:
            px=x+n['beat']*23+11;py=y+100-(n['note']-62)*3.0
            colour='#df5237' if n['track']=='melody' else '#417a58';r=4.8 if n['track']=='melody' else 3.2
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{colour}"/>')
            c.setFillColor(HexColor(colour));c.circle(px/2,(H-py)/2,r/2,stroke=0,fill=1)
        out.append(f'<text x="{x}" y="{y+140}" font-size="15" fill="#417a58" font-family="sans-serif">{bar+1:02}</text>')
        txt(x,y+140,f'{bar+1:02}',15,'#417a58')
    label='Новая композиция проекта. Воображаемый ансамбль; это не запись грибов и не традиционная узбекская музыка.'
    out.append(f'<text x="70" y="1005" fill="#417a58" font-family="sans-serif" font-size="17">{label}</text></svg>')
    txt(70,1005,label,13,'#417a58')
    channel='Telegram · https://t.me/phys_math_dev'
    out.insert(-1, '<a href="https://t.me/phys_math_dev"><text x="70" y="1033" fill="#417a58" font-family="sans-serif" font-size="14">'+channel+'</text></a>')
    txt(70,1033,channel,14,'#417a58')
    c.linkURL('https://t.me/phys_math_dev',(35,5,250,16),relative=0,thickness=0)
    c.save()
    (HERE/'graphic-score.svg').write_text('\n'.join(out))

def main():
    notes=arrangement();midi(notes);duration=sound(notes);score(notes)
    (HERE/'composition.json').write_text(json.dumps({'title':'Танец трёх клеток','tempo_quarter':BPM,'meter':'7/8','grouping':[3,2,2],'bars':BARS,'music_seconds':BARS*7*EIGHTH,'audio_seconds':duration,'tracks':['plucked melody','answer','bass','bells','percussion'],'authorship':'Original composition and synthesis for the project by Codex, 2026','scope':'An invented lively ensemble, not traditional Uzbek music, recorded fungi or a biological model.','events':notes},ensure_ascii=False,indent=2)+'\n')
    print(f'Wrote WAV, MIDI and graphic score: {duration:.2f} seconds, {len(notes)} note events.')

if __name__=='__main__':main()
