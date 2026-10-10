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
from render_whoami import render
render(cal)
