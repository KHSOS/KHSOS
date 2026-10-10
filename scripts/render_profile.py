import json, os, subprocess, urllib.request, html
from pathlib import Path
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
def api(query):
    if os.environ.get('GH_TOKEN'):
        req=urllib.request.Request('https://api.github.com/graphql',data=json.dumps({'query':query}).encode(),headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Content-Type':'application/json'})
        return json.load(urllib.request.urlopen(req))
    return json.loads(subprocess.check_output(['/mnt/c/Program Files/GitHub CLI/gh.exe','api','graphql','-f','query='+query]))
def svg(w,h,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" rx="16" fill="#0d1117"/>{body}</svg>'
def text(x,y,s,size=18,color='#c9d1d9'):
    return f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" fill="{color}">{html.escape(str(s))}</text>'
cal=api('query { user(login:"KHSOS") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount color } } } } } }')['data']['user']['contributionsCollection']['contributionCalendar']
body=text(26,34,'KHSOS / contribution activity',18,'#39d353')
for x,week in enumerate(cal['weeks']):
    for day in week['contributionDays']:
        from datetime import date
        y=(date.fromisoformat(day['date']).weekday()+1)%7
        color=day['color'] if day['contributionCount'] else '#161b22'
        body+=f'<rect x="{26+x*15}" y="{56+y*15}" width="11" height="11" rx="2" fill="{color}"><title>{day["date"]}: {day["contributionCount"]} contributions</title><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{x*0.015}s" fill="freeze"/></rect>'
body+=text(26,190,f'{cal["totalContributions"]} contributions in the GitHub calendar',14)
(ROOT/'contrib-heatmap.svg').write_text(svg(860,215,body))
im=ImageOps.autocontrast(Image.open(ROOT/'source-photo.png').convert('L')).resize((90,90))
chars=' .,:;irsXA253hMHGS#9B&@'
body=text(24,32,'$ whoami --ascii',18,'#39d353')
for y in range(90):
    row=''.join(chars[im.getpixel((x,y))* (len(chars)-1)//256] for x in range(90))
    body+=f'<text xml:space="preserve" x="24" y="{60+y*8.5}" font-family="monospace" font-size="8" fill="#c9d1d9">{html.escape(row)}</text>'
(ROOT/'khsos-ascii.svg').write_text(svg(480,850,body))
days=[d for w in cal['weeks'] for d in w['contributionDays']]
active=sum(d['contributionCount']>0 for d in days)
body=text(36,58,'KHSOS',32,'#39d353')+text(36,100,'KimHeeSang',23)+text(36,174,'GITHUB ACTIVITY',16,'#8b949e')+text(36,240,cal['totalContributions'],52,'#39d353')+text(36,278,'Contributions / calendar year',15)+text(36,358,active,42,'#58a6ff')+text(36,395,'Active days',16)+text(36,495,'BUILD / LEARN / SHARE',18)+text(36,540,'OCI Roadmap Labs',21)+text(36,582,'Hands-on learning',17,'#8b949e')+text(36,780,'Source: GitHub GraphQL API',13,'#8b949e')
(ROOT/'stats.svg').write_text(svg(480,850,body))
print('Generated ASCII portrait, contribution heatmap, and stats:',cal['totalContributions'])
