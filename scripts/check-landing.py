#!/usr/bin/env python3
"""Check release references and ensure only public assets are served."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'www/landing'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.refs=[]; self.anchors=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        for key in ('src','href'):
            value=attrs.get(key,'')
            if value.startswith('#'): self.anchors.append(value[1:])
            elif value: self.refs.append(value)
        for item in attrs.get('srcset','').split(','):
            if item.strip(): self.refs.append(item.strip().split()[0])
def check_ref(value, base):
    uri=urlsplit(value)
    if uri.scheme or uri.netloc: return
    target=(base/unquote(uri.path)).resolve()
    assert target.is_relative_to(WEB.resolve()), f'Outside public root: {value}'
    assert target.is_file(), f'Missing file: {target}'
p=Page();p.feed((WEB/'index.html').read_text())
assert len(p.ids)==len(set(p.ids)), 'Duplicate HTML IDs'
assert all(a in p.ids for a in p.anchors), 'Broken section link'
for ref in p.refs: check_ref(ref,WEB)
for css in (WEB/'assets').glob('*.css'):
    for ref in re.findall(r'url\([\"\']?([^\)\"\']+)',css.read_text()): check_ref(ref,css.parent)
for f in WEB.rglob('*'):
    assert not f.is_symlink(), f'Symlink: {f}'
    assert f.name not in ('.env','.git','page.html','turbium-landing.php'), f'Private/build file in webroot: {f}'
assert '{{ASSET}}' not in (WEB/'index.html').read_text()
fragment=(ROOT/'wordpress/page.html').read_text().replace('{{ASSET}}','assets/')
assert fragment in (WEB/'index.html').read_text(), 'Run scripts/build-landing.py to synchronise HTML'
print(f'PASS: {len(p.ids)} unique IDs; {len(p.refs)} HTML references; CSS fonts; public-root boundary; WordPress fragment sync')
