"""Download completed photographic cards and export web/placement assets.

Raster work is limited to proportional export and contact sheets; source
photographs and their typography are generated together, without repainting.
"""
from pathlib import Path
import json,urllib.request,concurrent.futures,sys
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[1])
ids=['commercial','interior','window','rus','ice','pastel','home']
rows=json.loads((SOURCE/'results.json').read_text())
assert len(rows)==70 and all(x['status']=='completed' for x in rows)
def export(row):
    index=row['index'];name=ids[index//100-1];n=index%100
    folder=SOURCE/name;original=folder/'originals'/f'{n:02}.png';png=folder/'PNG_1600x1200'/f'{n:02}.png'
    original.parent.mkdir(parents=True,exist_ok=True);png.parent.mkdir(parents=True,exist_ok=True)
    if not original.exists():
        with urllib.request.urlopen(row['result_url'],timeout=90) as r:original.write_bytes(r.read())
    with Image.open(original) as im:
        assert im.width>=1600 and im.height>=1200
        out=ImageOps.fit(im.convert('RGB'),(1600,1200),method=Image.Resampling.LANCZOS)
        out.save(png,optimize=True)
        web=ROOT/'assets/slides'/f'{name}-fairytale-{n}.webp';out.save(web,'WEBP',quality=94,method=6)
        if n==1:
            photo=ROOT/'assets/photos/fairytale'/f'{name}.webp';photo.parent.mkdir(parents=True,exist_ok=True);out.save(photo,'WEBP',quality=90,method=6)
    return name,n
selected=set(map(int,sys.argv[2].split(','))) if len(sys.argv)>2 else None
if selected:
    for row in rows:
        if row['index'] in selected:
            original=SOURCE/ids[row['index']//100-1]/'originals'/f"{row['index']%100:02}.png"
            if original.exists():original.rename(original.with_suffix('.previous.png'))
    rows=[row for row in rows if row['index'] in selected]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for i,result in enumerate(pool.map(export,rows),1):
        if i%10==0:print(f'Exported {i}/70',flush=True)
font=ImageFont.truetype(str(ROOT/'assets/manrope-600.ttf'),22)
for name in ids:
    sheet=Image.new('RGB',(1640,1350),'#f4f0e8');draw=ImageDraw.Draw(sheet)
    draw.text((20,12),name+' | 10 карточек',font=font,fill='#57212f')
    for n in range(1,11):
        with Image.open(SOURCE/name/'PNG_1600x1200'/f'{n:02}.png') as im:
            im.thumbnail((520,390));x=20+(n-1)%3*540;y=60+(n-1)//3*320
            im=ImageOps.fit(im,(400,300),method=Image.Resampling.LANCZOS)
            # Four rows, three columns; actual captions remain in original.
            sheet.paste(im,(x,y));draw.text((x+408,y+8),str(n),font=font,fill='#57212f')
    sheet.save(SOURCE/name/'Обзор.jpg',quality=92)
print('PASS: 70 PNG + 70 WebP + 7 covers + 7 contact sheets')
