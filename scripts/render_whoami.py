import html
from datetime import date, timedelta
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
ROOT=Path(__file__).resolve().parents[1]
def txt(x,y,s,size=20,color='#c9d1d9',extra=''):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{html.escape(str(s))}</text>'
def frame(command):
 s='<svg xmlns="http://www.w3.org/2000/svg" width="840" height="880" viewBox="0 0 840 880" font-family="Consolas,Menlo,monospace"><defs><linearGradient id="bg" x2="0" y2="1"><stop stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs><rect width="840" height="880" rx="12" fill="url(#bg)"/><rect x=".5" y=".5" width="839" height="879" rx="12" fill="none" stroke="#30363d"/><path d="M0 30H840" stroke="#30363d"/>'
 for i,c in enumerate(['#ff5f56','#ffbd2e','#27c93f']): s+=f'<circle cx="{20+16*i}" cy="15" r="5" fill="{c}"/>'
 return s+txt(420,19,'khsos@github: ~$ '+command,12,'#7d8590','text-anchor="middle"')
def render(cal):
 im=Image.open(ROOT/'source-photo.png').convert('L')
 # Preserve the supplied image's proportions on a bright canvas.
 im=ImageOps.pad(im,(800,800),method=Image.Resampling.LANCZOS,color=255)
 im=ImageEnhance.Contrast(ImageOps.autocontrast(im)).enhance(1.05).resize((180,96),Image.Resampling.LANCZOS)
 ramp=' .`:-=+*cs#%@'; s=frame('./portrait.sh')
 for y in range(96):
  row=''.join(' ' if (v:= (im.getpixel((x,y))/255)**1.18)>=.8 else ramp[min(len(ramp)-1,round((1-v)*(len(ramp)-1)))] for x in range(180))
  top=37+y*800/96; begin=y*5.8/96; dur=5.8/96
  s+=f'<defs><clipPath id="line{y}"><rect x="20" y="{top}" width="0" height="8.34"><animate attributeName="width" from="0" to="800" begin="{begin:.4f}s" dur="{dur:.4f}s" fill="freeze"/></rect></clipPath></defs>'
  s+=f'<g clip-path="url(#line{y})">'+txt(20,top+6.2,row,7.2,extra='xml:space="preserve" textLength="800" lengthAdjust="spacing"')+'</g>'
  s+=f'<rect x="20" y="{top}" width="4.44" height="7" fill="#c9d1d9" opacity="0"><set attributeName="opacity" to="1" begin="{begin:.4f}s"/><animate attributeName="x" from="20" to="820" begin="{begin:.4f}s" dur="{dur:.4f}s" fill="freeze"/><set attributeName="opacity" to="0" begin="{begin+dur:.4f}s"/></rect>'
 s+='<path d="M0 837H840" stroke="#30363d"/>'+txt(20,860,'khsos@github:~$ whoami KimHeeSang',13,'#7d8590')+'<rect x="290" y="848" width="8" height="14" fill="#c9d1d9"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect></svg>'
 (ROOT/'khsos-ascii.svg').write_text(s)
 today=date.today(); days=sorted([d for w in cal['weeks'] for d in w['contributionDays'] if date.fromisoformat(d['date'])<=today],key=lambda d:d['date'])
 active=[d for d in days if d['contributionCount']]; longest=run=0; prev=None
 for d in active:
  dt=date.fromisoformat(d['date']); run=run+1 if prev and dt-prev==timedelta(days=1) else 1; longest=max(longest,run); prev=dt
 lookup={date.fromisoformat(d['date']):d['contributionCount'] for d in days}; cursor=today if lookup.get(today) else today-timedelta(days=1); current=0
 while lookup.get(cursor): current+=1; cursor-=timedelta(days=1)
 best=max(days,key=lambda d:d['contributionCount']); total=sum(d['contributionCount'] for d in days)
 tiles=[('current streak',current,'days'),('longest streak',longest,'days'),('contributions',total,'in the last year'),('active days',len(active),f'of {len(days)} calendar days'),('best day',best['contributionCount'],best['date']),('avg / active day',round(total/len(active),1) if active else 0,'contributions')]
 s=frame('./stats.sh')
 for i,(label,value,caption) in enumerate(tiles):
  x=20+(i%2)*408; y=54+(i//2)*166; start=i*.15
  s+=f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{start}s" dur=".45s" fill="freeze"/><animateTransform attributeName="transform" type="translate" from="0 14" to="0 0" begin="{start}s" dur=".45s" fill="freeze"/><rect x="{x}" y="{y}" width="392" height="150" rx="10" fill="#161b22" stroke="#30363d"/>'+txt(x+24,y+40,'$ '+label,22,'#7d8590')
  for k in range(16):
   val=value*(1-(1-(k+1)/16)**3); labelnum=f'{val:.1f}' if isinstance(value,float) else str(round(val)); on=start+.27+k*1.2/16
   anim=f'<set attributeName="opacity" to="1" begin="{on:.4f}s"/>'
   if k<15: anim+=f'<set attributeName="opacity" to="0" begin="{on+1.2/16:.4f}s"/>'
   s+=f'<g opacity="0">'+txt(x+24,y+100,labelnum,54,'#39d353' if i==0 else '#e6edf3')+anim+'</g>'
  s+=txt(x+24,y+132,caption,18,'#7d8590')+'</g>'
 monthly=defaultdict(int)
 for d in days: monthly[d['date'][:7]]+=d['contributionCount']
 s+='<rect x="20" y="552" width="800" height="308" rx="10" fill="#161b22" stroke="#30363d"/>'+txt(44,592,'$ contributions / month',22,'#7d8590')
 peak=max(monthly.values()) or 1; slot=752/len(monthly)
 for i,(month,n) in enumerate(sorted(monthly.items())):
  x=44+i*slot+slot*.19; h=max(2,n/peak*190); begin=1.3+i*.06
  s+=f'<rect x="{x}" y="{820-h}" width="{slot*.62}" height="{h}" rx="3" fill="#39d353"><animate attributeName="height" from="0" to="{h}" begin="{begin}s" dur=".6s" fill="freeze"/><animate attributeName="y" from="820" to="{820-h}" begin="{begin}s" dur=".6s" fill="freeze"/></rect>'+txt(x+slot*.31,845,date.fromisoformat(month+'-01').strftime('%b')[0],18,'#7d8590','text-anchor="middle"')
 (ROOT/'stats.svg').write_text(s+'</svg>')
 print('whoami: 840x880 panels; 96 animated portrait rows; 6 animated stat tiles; monthly bars')
