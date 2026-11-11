"""Validate deliverable assets, content contracts, links and portable WP output."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import collections,json,re,sys
root=Path(__file__).resolve().parents[1];errors=[];documents=[root/'index.html',root/'design-system.html',root/'motion-map.html',*sorted((root/'media').glob('*.html'))]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.h1=0;self.media=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if 'data-media'in a:self.media.append(a['data-media'])
  for k in ('src','href','poster','data-lazy-src','data-compact','data-open-src','data-layer-src'):
   if a.get(k):self.refs.append(a[k])
  for key in ('srcset','data-lazy-srcset','data-layer-srcset'):
   if a.get(key):self.refs.extend(x.strip().split()[0]for x in a[key].split(','))
main=None
for file in documents:
 s=Page();s.feed(file.read_text());duplicates=[k for k,v in collections.Counter(s.ids).items()if v>1]
 if duplicates:errors.append(f'{file.name}: duplicate ids {duplicates}')
 for link in s.refs:
  url=urlsplit(link)
  if url.scheme or url.netloc:continue
  if not url.path:
   if url.fragment and url.fragment not in s.ids:errors.append(f'{file.name}: missing #{url.fragment}')
  elif not(file.parent/unquote(url.path)).is_file():errors.append(f'{file.name}: missing {url.path}')
 if file.name=='index.html':main=s
media=json.loads((root/'media.json').read_text());by_id={m['id']:m for m in media}
if len(by_id)!=len(media):errors.append('Duplicate media ids')
if main.h1!=1:errors.append('Homepage must have one H1')
if set(main.media)!=set(by_id):errors.append('Gallery HTML differs from media.json')
inline=json.loads(re.search(r'<script id="gallery-data" type="application/json">(.*?)</script>',(root/'index.html').read_text(),re.S)[1])
if inline!=media:errors.append('Embedded gallery data differs from media.json; run tools/update-media.py')
for m in media:
 for key in ('src','thumb','medium','original'):
  if m.get(key)and not(root/m[key]).is_file():errors.append(m['id']+': missing '+m[key])
 if m['kind']=='concept' and ('Идея'not in m['kindLabel'] or m.get('original')):errors.append(m['id']+': misleading concept type')
 if m['kind']=='retouch' and not m.get('original'):errors.append(m['id']+': retouch needs source')
for name in ('app.js','motion.js','motion-config.js','site.css','wow.css','spatial.css'):
 if not(root/name).is_file():errors.append('Missing runtime '+name)
for p in root.rglob('*.html'):
 if 'wordpress'in p.parts:continue
 if re.search(r'(?:src|href)=["\'](?:/Users/|file:)',p.read_text()):errors.append('Nonportable path: '+str(p))
result={'documents':len(documents),'gallery':len(media),'retouches':sum(m['kind']=='retouch'for m in media),'concepts':sum(m['kind']=='concept'for m in media),'errors':errors}
print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(errors))
