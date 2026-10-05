#!/usr/bin/env python3
"""Synchronise the public HTML body and build the installable WordPress plugin."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'www/landing'
index=WEB/'index.html'
head=index.read_text().split('<body>',1)[0]
fragment=(ROOT/'wordpress/page.html').read_text()
index.write_text(head+'<body>'+fragment.replace('{{ASSET}}','assets/')+'</body></html>')
package=ROOT/'packages/turbium-landing-wordpress.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
    for name in ('page.html','turbium-landing.php'):
        z.write(ROOT/'wordpress'/name,'turbium-landing/'+name)
    for f in sorted((WEB/'assets').iterdir()):
        if f.is_file(): z.write(f,'turbium-landing/assets/'+f.name)
    for name in ('README.txt','image-prompt-v3.txt','image-prompt-final-v3.txt'):
        z.write(ROOT/'docs/landing'/name,'turbium-landing/'+name)
print('Updated public HTML and',package.relative_to(ROOT))
