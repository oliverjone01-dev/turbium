"""Pack the real camera render series into small desktop/mobile WebP strips."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('--render', type=Path, required=True)
parser.add_argument('--qa', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / 'assets/camera-v64'
args.qa.mkdir(parents=True, exist_ok=True)
report = {}
for key in ('entrance', 'window', 'interior'):
    files = [args.render/key/f'frame-{i:03d}.png' for i in range(48)]
    frames = [Image.open(f).convert('RGBA') for f in files]
    edges = []
    for i, frame in enumerate(frames):
        assert frame.size == (512, 384)
        bounds = frame.getchannel('A').point(lambda a: 255 if a > 16 else 0).getbbox()
        if not bounds or bounds[0] == 0 or bounds[1] == 0 or bounds[2] == 512 or bounds[3] == 384:
            edges.append(i)
    for mobile, fw, fh, quality in ((False, 512, 384, 86), (True, 384, 288, 82)):
        sized = [f.resize((fw, fh), Image.Resampling.LANCZOS) if mobile else f for f in frames]
        for block in range(6):
            strip = Image.new('RGBA', (fw*4, fh*2))
            for j in range(8):
                strip.paste(sized[block*8+j], (j%4*fw, j//4*fh))
            strip.save(root/f'{key}-{"mobile-" if mobile else ""}strip-{block}.webp', quality=quality, method=4)
        # Keep legacy cached pages clean as well.
        atlas = Image.new('RGBA', (fw*8, fh*6))
        for i, f in enumerate(sized):
            atlas.paste(f, (i%8*fw, i//8*fh))
        atlas.save(root/f'{key}-{"mobile" if mobile else "atlas"}.webp', quality=quality, method=4)
    for state in ('closed', 'open'):
        Image.open(args.render/key/f'{state}.png').save(root/f'{key}-{state}.webp', quality=94, method=4)
    sheet = Image.new('RGB', (1920, 320), (246, 240, 229))
    d = ImageDraw.Draw(sheet)
    for col, i in enumerate((0, 12, 24, 36, 47)):
        f = frames[i].resize((384, 288), Image.Resampling.LANCZOS)
        sheet.paste(f, (col*384, 0), f)
        d.text((col*384+8, 292), f'{key} / frame {i:02d}', fill=(87, 33, 47))
    sheet.save(args.qa/f'{key}-camera-v642.jpg', quality=93)
    report[key] = {'frames': len(frames), 'distinctHashes': len({hashlib.sha256(f.read_bytes()).hexdigest() for f in files}), 'edgeTouchFrames': edges}
    assert not edges, (key, edges)
manifest = json.loads((args.render/'camera-manifest.json').read_text())
manifest['version'] = '6.4.2'
manifest['assemblyGuides'] = False
manifest['runtimeEncoding'] = {'strips': 6, 'framesPerStrip': 8, 'columns': 4, 'rows': 2, 'desktopFrame': [512, 384], 'mobileFrame': [384, 288], 'decoder': 'worker-bitmaps', 'fallback': 'direct-strips-or-static'}
(root/'camera-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
(args.qa/'render-check-v642.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
