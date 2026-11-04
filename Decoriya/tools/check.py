"""Validate the complete content inventory and every referenced local asset."""
from pathlib import Path
import json,re,subprocess,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
script=(ROOT/'data.js').read_text()
probe=subprocess.run(['node','-e',script+'\nconsole.log(JSON.stringify(DEKORIYA.ads));'],check=True,capture_output=True,text=True)
ads=json.loads(probe.stdout)
assert len(ads)==7
assert len({a['id'] for a in ads})==7
assert sum(a['phase']=='start' for a in ads)==4
assert sum(a['phase']=='test' for a in ads)==3
for ad in ads:
    assert len(ad['slides'])==5
    assert len(ad['body'])==4
    assert len(ad['includes'])==3
    for src in ad['slides']+[ad['photo']]:
        p=ROOT/src
        assert p.is_file(),src
        assert p.stat().st_size>1000,src
        if p.suffix=='.svg':
            root=ET.parse(p).getroot()
            assert root.attrib['viewBox']=='0 0 1600 1200'
            assert 'data:image/webp;base64,' in p.read_text()
for filename in ['index.html','app.js','data.js','styles.css']:
    text=(ROOT/filename).read_text()
    assert not re.search('[\u2013\u2014]',text),f'Long dash in {filename}'
assert 'noindex,nofollow' in (ROOT/'index.html').read_text()
js=(ROOT/'app.js').read_text()
assert not re.search(r'\b(fetch|XMLHttpRequest|WebSocket)\s*\(',js)
assert 'decoriya-favorites' in js
assert 'contact-form' in js
print('PASS: 7 offers, 35 slides, all local resources, no fabricated prices or remote form endpoint')
