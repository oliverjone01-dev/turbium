"""Check preview URL resolution, especially inline masks and contextual photo data."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json,re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'v9'
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.urls=[];self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for key in ('src','href'):
            if a.get(key):self.urls.append(a[key])
        if a.get('srcset'):
            self.urls.extend(x.strip().split()[0] for x in a['srcset'].split(','))
        self.urls.extend(re.findall(r'url\([\"\']?([^\)\"\']+)',a.get('style','')))
        if tag=='script' and a.get('src'):self.scripts.append(a['src'])
html=(P/'index.html').read_text();p=Parser();p.feed(html)
missing=[]
for u in p.urls:
    if u.startswith(('#','http','data:','mailto:','tel:')):continue
    if not (P/urlsplit(u).path).exists():missing.append(u)
assert not missing, missing
data=json.loads(re.search(r'<script type="application/json" id="site-data">(.*?)</script>',html,re.S).group(1))
for item in data['gallery']:
    assert (ROOT/item['image']).exists(),item['image']
assert p.scripts.index('./site-core.js?v=9.0.0')<p.scripts.index('./motion.js?v=9.0.0')
assert '<meta name="robots" content="noindex,follow">' in html
assert 'data-motion="v9"' in html
assert len([x for x in data['gallery'] if x.get('category')=='concept'])==3
print(f'PASS: {len(p.urls)} resource/link targets, inline masks, {len(data["gallery"])} photo entries, script order and preview indexing')
