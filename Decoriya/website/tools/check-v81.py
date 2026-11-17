from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.meta={};self.h1=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='h1':self.h1+=1
  if t=='meta':self.meta[a.get('name')]=a.get('content')
  if t in ('link','script','img','a'):
   if v:=a.get('src',a.get('href')):self.links.append(v)
for rel in ['index.html','projects/myata-lounge/index.html','projects/britva/index.html']:
 p=root/rel;x=Page();x.feed(p.read_text())
 assert x.h1==(3 if rel=='index.html' else 1),(rel,'two responsive studio versions and one alternative; one visible per viewport')
 assert 'noindex' not in x.meta.get('robots','')
 for v in x.links:
  u=urlsplit(v)
  if u.scheme or not u.path:continue
  f=(p.parent/unquote(u.path)).resolve()
  assert f.exists(),(rel,v)
 text=p.read_text();assert 'www.figma.com/api/mcp/asset' not in text
 assert 'rel="canonical"' in text and 'application/ld+json' in text
cases=json.loads((root/'cases.json').read_text())
assert len({v['id'] for v in cases.values()})==2
for c in cases.values():assert (root/c['image'].removeprefix('./')).exists()
ET.parse(root/'sitemap.xml')
assert 'id="direct-contact"' in (root/'index.html').read_text()
assert 'Скопировать сообщение' in (root/'index.html').read_text()
print('v8.1: pages, canonical, local assets, independent cases, sitemap and pending submission checked')
