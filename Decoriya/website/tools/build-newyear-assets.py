"""Encode the approved raster passes; preserve the generated alpha and source pixels.

Sources: entrance/window/interior-master.png (three square passes in one row),
and room-master.png. This build only resizes and encodes delivery derivatives.
"""
import argparse
import json
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--sources', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
out = root / 'assets/newyear-v66'
out.mkdir(parents=True, exist_ok=True)
report = {}
for scene in ('entrance', 'window', 'interior'):
    image = Image.open(args.sources / f'{scene}-master.png')
    assert image.mode == 'RGBA' and image.width == image.height * 3
    for width, quality in ((1536, 78), (2172, 82)):
        path = out / f'{scene}-atlas-{width}.webp'
        image.resize((width, width // 3), Image.Resampling.LANCZOS).save(
            path, quality=quality, method=6, exact=True
        )
        report[path.name] = {'bytes': path.stat().st_size, 'width': width,
                             'height': width // 3, 'passes': 3}
    poster = args.sources / f'{scene}-closed.png'
    if poster.exists():
        path = out / f'{scene}-closed.webp'
        Image.open(poster).save(path, quality=80, method=6)
        report[path.name] = {'bytes': path.stat().st_size, 'width': 720,
                             'height': 720, 'source': 'browser export of the same CSS passes'}
room = Image.open(args.sources / 'room-master.png')
for width, quality in ((960, 65), (1672, 72)):
    path = out / f'room-{width}.webp'
    room.resize((width, round(room.height * width / room.width)), Image.Resampling.LANCZOS).save(
        path, quality=quality, method=6
    )
    report[path.name] = {'bytes': path.stat().st_size, 'width': width}
(out / 'assets.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
