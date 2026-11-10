from pathlib import Path
import json,re,html
p=Path(__file__).resolve().parents[1];E=html.escape
media=json.loads((p/'media.json').read_text())
arrow='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>'
def btn(t,href):return '<a class="btn primary" href="'+href+'">'+E(t)+arrow+'</a>'
def card(x,i):
 return f'<article class="media-card" data-category="{x["category"]}"><a href="media/{x["id"]}.html" class="media-open" data-media="{x["id"]}"><div class="media-image"><img src="{x["thumb"]}" srcset="{x["thumb"]} 640w, {x["medium"]} 1280w" sizes="(max-width:767px)82vw,40vw" alt="{E(x["alt"])}" loading="lazy" draggable="false"><span class="media-badge">{E(x["kindLabel"])}</span><span class="media-open-icon">{arrow}</span></div><div class="media-card-heading"><span class="media-index">{i:02}</span><h3>{E(x["title"])}</h3></div><p>{E(x["categoryLabel"])}</p></a></article>'
def rail(items,id):return f'<div class="media-rail" id="{id}-rail" data-rail="{id}" tabindex="0" role="region" aria-label="Галерея: '+('портфолио'if id=='works' else'ИИ-направления')+'">'+''.join(card(x,i+1)for i,x in enumerate(items))+'</div>'
page=(p/'index.html').read_text()
for kind,rid in [('retouch','works'),('concept','ideas')]:
 items=[m for m in media if m['kind']==kind]
 pattern=r'<div class="media-rail" id="'+rid+r'-rail".*?(?=<div class="rail-controls wrap">)'
 page,n=re.subn(pattern,rail(items,rid),page,flags=re.S)
 assert n==1,(rid,n)
 data=json.dumps(media,ensure_ascii=False).replace('</','<\\/')
page=re.sub(r'(<script id="gallery-data" type="application/json">).*?(</script>)',lambda m:m[1]+data+m[2],page,flags=re.S)
(p/'index.html').write_text(page)
# One-image fallback routes keep the gallery functional without JavaScript.
(p/'media').mkdir(exist_ok=True)
for x in media:
 text=f'<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{E(x["title"])} / Декория</title><link rel="stylesheet" href="../site.css"><main class="project-fallback wrap section"><a class="under-link" href="../index.html#{"projects"if x["kind"]=="retouch"else"directions"}">← К галерее</a><p class="eyebrow">{x["kindLabel"]}</p><h1>{E(x["title"])}</h1><p>{E(x["description"])}</p><img src="../{x["src"]}" alt="{E(x["alt"])}" width="1280" height="960">'+(f'<details><summary>Посмотреть исходник</summary><img src="../{x["original"]}" alt="Исходная фотография" loading="lazy"></details>'if x.get('original')else'')+btn('Обсудить объект','../index.html#contact')+'</main></html>'
 (p/'media'/f'{x["id"]}.html').write_text(text)

print("Updated",len(media),"gallery items and fallbacks")
