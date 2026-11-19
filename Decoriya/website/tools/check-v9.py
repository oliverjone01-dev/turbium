"""Canonical v10 links, semantics, runtime parity and publication contract."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json,re,hashlib,zipfile
R=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.urls=[];self.ids=[];self.buttons=[];self.scripts=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if t=='button':self.buttons.append(a)
  for k in ['src','href','data-src']:
   if a.get(k):self.urls.append(a[k])
  for k in ['srcset','data-srcset']:
   if a.get(k):self.urls.extend(x.strip().split()[0] for x in a[k].split(','))
  self.urls.extend(re.findall(r'url\([\"\']?([^\)\"\']+)',a.get('style','')))
  if t=='script' and a.get('src'):self.scripts.append(a['src'])
html=(R/'index.html').read_text();p=Page();p.feed(html)
assert len(set(p.ids))==len(p.ids),'duplicate ids'
for url in p.urls:
 u=urlsplit(url)
 if u.scheme or u.netloc:continue
 if not u.path:
  if u.fragment:assert u.fragment in p.ids,url
 else:assert (R/u.path).exists(),url
assert 'data-build="10.0.0"' in html and 'data-motion="v9"' in html
assert 'noindex' not in html and 'rel="canonical"' in html
assert len(re.findall(r'<section\b',html))==11
assert 'data-action="contact"' in re.search(r'<section[^>]+id="hero".*?</section>',html,re.S)[0]
assert p.scripts[0].startswith('./site-core.js') and p.scripts[1].startswith('./v9-motion.js')
assert [urlsplit(s).path for s in p.scripts]==['./site-core.js','./v9-motion.js','./v10-lead.js','./v10.js']
assert any(x.get('type')=='submit' for x in p.buttons) and 'data-endpoint=' in html
assert not re.search(r'<template\b',html)
data=json.loads(re.search(r'<script type="application/json" id="site-data">(.*?)</script>',html,re.S)[1])
assert [x['id'] for x in data['gallery']]==['i-37','i-18','i-160','i-55','i-77','i-152','i-86','i-64','i-27']
assert len(re.findall(r'data-gallery-id=',html))==9
assert 'id="quiz"' in html and 'id="season"' in html and all('id="'+name+'"' not in html for name in ['business','process','conditions','budget','guide'])
assert 'type="checkbox" name="consent" required' in html and 'name="consent" checked' not in html
assert all((R/doc/'index.html').is_file() for doc in ['privacy','consent'])
assert all((R/'assets/v10/panel'/name).is_file() for name in ['s1-boutique.webp','s1-office.webp','p-last.webp'])
for x in data['gallery']:
 assert (R/x['image']).is_file(), x
 assert x['image'].endswith('-editorial.webp') and (R/x['thumbnail']).is_file(),x
assert html.count('data-hero-view=')==2 and 'id="hero-evening"' in html
assert 'assets/v9/portfolio/' not in html and 'assets/v9/portfolio/' not in (R/'v9-motion.js').read_text()
for page in (R/'projects').glob('*/index.html'):
 assert 'assets/v94/portfolio/' in page.read_text(),page
preview=(R/'v9/index.html').read_text();assert 'location.replace' in preview and 'noindex' in preview
for f in ['v81.css','v81-site.css','motion.css','v9.css','site-core.js','v9-motion.js','v10.css','v12.css','v10-lead.js','v10.js','privacy/index.html','consent/index.html']:
 assert (R/f).read_bytes()==(R/'wordpress/dekoriya-atelier'/f).read_bytes(),f+' theme drift'
manifest=json.loads((R/'wordpress/dekoriya-atelier/asset-manifest.json').read_text())
for f,h in manifest.items():assert hashlib.sha256((R/'wordpress/dekoriya-atelier'/f).read_bytes()).hexdigest()==h,f
with zipfile.ZipFile(R/'wordpress/dekoriya-atelier-v9.zip') as z:
 assert z.read('dekoriya-atelier/site-core.js')==(R/'site-core.js').read_bytes()
 assert 'Version: 10.0.0' in z.read('dekoriya-atelier/style.css').decode()
print(f'PASS canonical v10: 11 sections, {len(p.urls)} URLs, {len(p.buttons)} buttons, nine editorial photos, two lead paths, theme and ZIP parity')
