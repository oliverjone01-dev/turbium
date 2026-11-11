"""Build responsive delivery files; preserve the approved source images.

Optional --camera-render-dir points to the renderer's 48 PNGs per scene.
Dependencies: tools/requirements-assets.txt. This is a build tool, not runtime.
"""
import argparse
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont

parser = argparse.ArgumentParser()
parser.add_argument('--camera-render-dir', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
out = root/'assets/optimized'
out.mkdir(exist_ok=True)
photos = [
    ('room','assets/studio/studio-quiet-v61.webp',[(960,65),(1672,72)]),
    ('portrait','assets/generated/olesya-cutout.webp',[(640,78),(1148,82)]),
    ('desk','assets/studio/continuous-desk-v61.webp',[(960,65),(1920,72)]),
    ('hands','assets/studio/olesya-hands-v61.webp',[(640,78),(1148,82)]),
    ('materials','assets/studio/materials-wide-v6.webp',[(768,72),(1448,76)]),
    ('expert','assets/olesya-expert-v2.webp',[(640,72),(1122,76)]),
]
for name, source, variants in photos:
    image = Image.open(root/source)
    for width, quality in variants:
        image.resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS).save(out/f'{name}-{width}.webp',quality=quality,method=4)
for source in (root/'assets/generated').glob('*-1280.webp'):
    Image.open(source).save(out/source.name,quality=72,method=4)
for weight in ('regular','medium','semibold'):
    font = TTFont(root/f'assets/golos-{weight}.ttf')
    font.flavor = 'woff2'
    font.save(root/f'assets/golos-{weight}.woff2')
camera = root/'assets/camera-v65'
camera.mkdir(exist_ok=True)
for name in ('entrance','window','interior'):
    for state in ('closed','open'):
        Image.open(root/f'assets/camera-v64/{name}-{state}.webp').save(camera/f'{name}-{state}.webp',quality=78,method=4)
    if args.camera_render_dir:
        atlas = Image.new('RGBA',(1536,864))
        for i in range(48):
            frame = Image.open(args.camera_render_dir/name/f'frame-{i:03d}.png').convert('RGBA').resize((192,144),Image.Resampling.LANCZOS)
            atlas.paste(frame,(i%8*192,i//8*144))
        atlas.save(camera/f'{name}-lite.webp',quality=55,method=4)
print('Delivery images and WOFF2 built; source files preserved.')
