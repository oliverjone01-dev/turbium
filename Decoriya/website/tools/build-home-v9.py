"""Build the canonical v10 homepage and preserve the former preview redirect."""
from pathlib import Path
from html import escape as e
import json,re,hashlib,os
from urllib.parse import urlsplit
R=Path(__file__).resolve().parents[1];T=R/'tools/templates';V='10.0.0'
data=json.loads((T/'site-data-v9.json').read_text())
def read(name):return (T/(name+'-v9.html')).read_text()
def btn(text,attrs='data-action="contact"',outline=False):return f'<button type="button" class="btn'+(' outline' if outline else '')+f'" {attrs}>{text}<svg class="btn-arrow" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" stroke="currentColor" stroke-width="1.6"/></svg></button>'
def image(src,alt,cls='',lazy=True):return f'<img src="{src}" alt="{e(alt)}" width="768" height="960" class="{cls}" loading="'+('lazy' if lazy else 'eager')+'" decoding="async">'
def heading(k,h,p=''):return f'<div class="v9-heading"><p class="v9-kicker">{k}</p><div><h2>{h}</h2>'+ (f'<p>{p}</p>' if p else '')+'</div></div>'
def sec(id,content,cls=''):return f'<section id="{id}" class="v9-section {cls}">{content}</section>'
def icon(kind):
 paths={'material':'<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>','mount':'<path d="M4 21V8l8-5 8 5v13M8 21V11h8v10M2 21h20"/><path d="m9 7 3-2 3 2"/>','date':'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 11h18m-14 5 3 3 7-5"/>'}
 return f'<svg class="v9-line-icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">{paths[kind]}</svg>'
hero=read('hero').replace('class="fig-section hero"','class="fig-section hero evening-active"',1)
hero=re.sub(r'<button\b[^>]*>.*?</button>',lambda m:m[0].replace('<button ','<button data-action="contact" ',1) if 'Обсудить объект' in m[0] else m[0],hero,flags=re.S)
# Images in hidden responsive hero variants must not compete with the visible LCP.
# Lazy-load the mobile duplicate. Native browser viewport selection still uses the preserved design.
hero=re.sub(r'<img(?= +src="\./assets/(v81|v82)/[^"]+\.webp")', '<img loading="lazy"', hero)
assert hero.rstrip().endswith('</section>')
hero=re.sub(r'</section>\s*$',lambda _:read('hero-evening').replace('<a href="#olesya">','<a href="#palette">Стили</a><a href="#olesya">')+'</section>',hero)
# Full native responsive page: no desktop/mobile copies below the approved hero.
quiz=read('quiz')
cards=''
for key,c in data['cases'].items():
 thumb='i-55' if key=='myata' else 'i-77'
 cards+=f'<article class="v9-case"><a class="v9-photo-link" href="./projects/{c["id"]}/" aria-label="Смотреть кейс {e(c["short"])}">'+image(f'./assets/v94/portfolio/{thumb}-720.webp',c['short'])+f'<svg class="v9-photo-arrow" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" stroke="currentColor" stroke-width="1.6"/></svg></a><div class="v9-case-caption"><div><p class="v9-kicker">РЕАЛИЗОВАННЫЙ ПРОЕКТ</p><h3><a href="./projects/{c["id"]}/">{c["short"]}</a></h3><p>{c["materials"]}</p></div>'+btn('Обсудить похожее',f'data-case="{c["id"]}"',True)+'</div></article>'
projects=sec('projects',heading('РЕАЛИЗОВАННЫЕ РАБОТЫ','Два новогодних входа','Два проекта из портфолио студии: материалы, общий вид и детали оформления.')+'<div class="v9-case-grid">'+cards+'</div>','v9-paper')
services=''
service_data=[('Входные группы','Входная группа','входа','174-754-b8e81.webp','Дизайнерские фонарики','Хвоя и бархат','Камень и стекло','Хвоя, текстиль и свет обрамляют дверь. Подбираем масштаб композиции к архитектуре фасада.','Обсудить вход'),('Витрины','Витрина','витрины','174-754-bb872.webp','Гирлянды и фонарики','Хвоя, ленты и подарки','Рама и подиумы','Оформление собирается вокруг продукта: фон, подиумы, хвойные акценты и свет у стекла.','Обсудить витрину'),('Интерьеры','Интерьер','интерьера','174-754-f4134.webp','Декоративные подвесы','Хвоя и украшения','Стены и стойка','Композиция для стойки, зала или зоны встречи. Связываем декор с материалами пространства.','Обсудить интерьер')]
# Use the actual third atlas, not a guessed filename.
unique=['174-754-b8e81.webp','174-754-bb872.webp','174-473-9cca5.webp']
for i,(title,zone,obj,atlas,light,decor,surfaces,copy,cta) in enumerate(service_data):
 atlas=unique[i]
 layers=''.join(f'<span class="v9-scene-layer" data-scene-layer="{kind}"><img src="./assets/v81/{atlas}" alt="" width="3072" height="1024" loading="lazy" decoding="async" style="left:-{pos*100}%"></span>' for kind,pos in [('surfaces',2),('decor',1),('light',0)])
 legend=''.join(f'<span><span class="scene-legend-kicker">0{j+1} / {label}</span><span>{text}</span></span>' for j,(label,text) in enumerate([('СВЕТ',light),('ДЕКОР',decor),('ПОВЕРХНОСТИ',surfaces)]))
 services+=f'<article class="v9-service"><button type="button" class="v9-scene" data-action="explode" aria-expanded="false" aria-label="Разобрать оформление {obj}" data-closed-label="Разобрать оформление {obj}"><span class="v9-scene-stage">{layers}</span><span class="scene-legend">{legend}</span><span class="v9-scene-toggle"><span class="scene-toggle-label">Разобрать оформление {obj}</span><span class="scene-toggle-icon" aria-hidden="true">+</span></span></button><h3>{title}</h3><p>{copy}</p>'+btn(cta,f'data-zone="{zone}" data-occasion="Новый год"',True)+'</article>'
services=sec('services',heading('ЗОНЫ ОФОРМЛЕНИЯ','Вход, витрина<br>или интерьер?','Наведите на сцену или нажмите: свет, декор и поверхности разойдутся по слоям.')+'<div class="v9-services">'+services+'</div>')
# These are the nine editorial originals from the reviewed Figma rail.
portfolio = [
    ('i-37', 720, 454, None),
    ('i-18', 720, 813, 'Салон / новогоднее оформление входа'),
    ('i-160', 720, 960, None),
    ('i-55', 720, 908, None),
    ('i-77', 720, 960, None),
    ('i-152', 720, 960, 'Входная группа с хвойным обрамлением'),
    ('i-86', 720, 960, None),
    ('i-64', 720, 960, 'Световая сетка на фасаде'),
    ('i-27', 720, 960, None),
]
source = {item['id']:item for item in data['gallery']}
items = [{**source[id], 'title':title or source[id]['title'], 'w':w, 'h':h} for id,w,h,title in portfolio]
data['gallery'] = items
photos = ''.join(
    f'<button type="button" class="v9-gallery-card" data-gallery-id="{x["id"]}" data-category="{x["category"]}" '
    f'data-action="gallery-open" data-photo="{x["id"]}" style="--photo-ratio:{x["w"]/x["h"]:.6f}">'
    f'<span class="v9-gallery-image"><img src="{x["thumbnail"]}" alt="" width="{x["w"]}" height="{x["h"]}" loading="lazy" decoding="async">'
    f'<svg class="v9-photo-arrow" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" stroke="currentColor" stroke-width="1.6"/></svg></span><span class="v9-gallery-caption">{e(x["title"])}</span></button>'
    for x in items)
gallery = sec('gallery', heading('ПОРТФОЛИО','Входы, фасады<br>и детали','9 фотографий выполненных работ. Листайте, чтобы открыть всю серию.')+
    '<div class="v9-gallery-rail" data-rail tabindex="0" aria-label="Фотографии портфолио. Листайте горизонтально">'+photos+'</div>'+
    '<div class="rail-controls"><button type="button" data-rail-dir="-1" aria-label="Предыдущие фотографии"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m15 18-6-6 6-6" stroke="currentColor" stroke-width="1.6"/></svg></button><button type="button" data-rail-dir="1" aria-label="Следующие фотографии"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m9 18 6-6-6-6" stroke="currentColor" stroke-width="1.6"/></svg></button><span>Листайте фотографии</span></div>','v9-paper')
styles_data = [
    ('s3-warm','Тёплая классика','Кафе и рестораны','Густая хвоя, глубокий бордовый и тёплые отражения в окнах. Для входа, который должен притягивать взгляд в сумерках.'),
    ('s3-ice','Лёд и серебро','Витрины и бутики','Прозрачные подвесы и холодные блики обрамляют витрину и оставляют коллекцию на виду.'),
    ('s3-russian','Русский орнамент','Рестораны и тематические зоны','Роспись, золото и красный текстиль подчёркивают вход. Орнамент подбираем под архитектуру объекта.'),
    ('s3-pastel','Мягкая пастель','Кондитерские и интерьеры','Жемчужные, розовые и мятные оттенки подходят для светлого интерьера.'),
]
GENITIVE={'КАФЕ И РЕСТОРАНЫ':'КАФЕ И РЕСТОРАНОВ','ВИТРИНЫ И БУТИКИ':'ВИТРИН И БУТИКОВ','РЕСТОРАНЫ И ТЕМАТИЧЕСКИЕ ЗОНЫ':'РЕСТОРАНОВ И ТЕМАТИЧЕСКИХ ЗОН','КОНДИТЕРСКИЕ И ИНТЕРЬЕРЫ':'КОНДИТЕРСКИХ И ИНТЕРЬЕРОВ'}
def style_image(asset,sizes):
    return (f'<img src="./assets/v10/panel/{asset}-400.webp" srcset="./assets/v10/panel/{asset}-400.webp 400w, ./assets/v10/panel/{asset}.webp 800w" sizes="{sizes}" alt="" width="800" height="600" loading="lazy" decoding="async">')

style_choices=''.join(f'<button type="button" data-style-pick="{i}" aria-pressed="{str(i==0).lower()}" aria-controls="style-feature">{name}</button>' for i,(_,name,_,_) in enumerate(styles_data))
style_features=''.join(
    f'<article class="v10-style-feature" data-style-feature="{i}" {"hidden" if i else ""}>'+style_image(asset,'(max-width:820px) 90vw, 58vw')+
    f'<div><p class="v9-kicker">КОНЦЕПТ ДЛЯ {GENITIVE.get(tag, tag)}</p><h3>{name}</h3><p>{copy}</p><a class="btn" href="#quiz" data-quiz-mood="{e(name)}">Подобрать оформление <svg class="btn-arrow" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" stroke="currentColor" stroke-width="1.6"/></svg></a></div></article>'
    for i,(asset,name,tag,copy) in enumerate(styles_data))
thumbs=''.join(
    f'<button type="button" data-style-pick="{i}" aria-pressed="false" aria-controls="style-feature">'+style_image(asset,'(max-width:820px) 28vw, 30vw')+f'<span>{name}</span></button>'
    for i,(asset,name,_,_) in enumerate(styles_data) if i)
palette = sec('palette',heading('КОНЦЕПТЫ ОФОРМЛЕНИЯ','Выберите настроение','Четыре направления для Нового года. Выберите то, которое подходит вашему пространству.')+
    '<div class="v10-style-pills" role="group" aria-label="Направления оформления">'+style_choices+'</div>'+
    '<div id="style-feature" aria-live="polite">'+style_features+'</div><div class="v10-style-thumbs">'+thumbs+'</div>','v9-dark')
olesya=sec('olesya','<div class="v9-editorial v9-expert"><div class="v9-expert-image">'+image('./assets/v81/174-549-0e4aa.webp','Олеся Овакимян за работой с композицией')+'</div><div class="v9-copy"><p class="v9-kicker">ЧЕЛОВЕК ЗА ПРОЕКТОМ</p><h2>Олеся<br>Овакимян.</h2><p class="v9-expert-role">Декоратор и руководитель студии</p><p>Олеся определяет направление оформления. Дизайнеры готовят эскизы, флористы и декораторы собирают композиции, монтажники устанавливают их на объекте.</p><div class="v9-expert-ways"><div><h3>Концепция с нуля</h3><p>Эскизы, палитра и подбор материалов.</p></div><div><h3>Ваш готовый проект</h3><p>Оформление по техническому заданию.</p></div></div>'+'<a class="btn outline" href="tel:+79772666460">Позвонить Олесе <svg class="btn-arrow" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" stroke="currentColor" stroke-width="1.6"/></svg></a>'+'</div></div>')
season=read('season')
partners=sec('partners','<div class="v9-editorial"><div class="v9-material-photo">'+image('./assets/v10/panel/partnership.webp','Хвойная гирлянда с бордовым бархатом и тёплым светом')+'</div><div class="v9-copy"><p class="v9-kicker">ДИЗАЙНЕРАМ И АРХИТЕКТОРАМ</p><h2>Новогодний декор<br>по вашему проекту</h2><p>Подключимся к новогоднему оформлению ресторана, витрины или входной группы. Согласуем палитру, материалы и монтаж по вашему эскизу или ТЗ.</p>'+btn('Обсудить готовый проект','data-format="По готовому дизайн-проекту"')+'</div></div>')
faq_items=[('Можно заказать декор по своему проекту?','Да. Пришлите эскиз или техническое задание. Команда обсудит с вами материалы, крепления и условия монтажа.'),('Как рассчитывают стоимость оформления?','Расчёт зависит от размеров зоны, материалов, доставки и монтажа. Пришлите фото и примерные размеры. Если бюджет уже определён, укажите его.'),('Когда обсуждать дату монтажа?','Укажите желаемую дату уже в первом сообщении. Возможность монтажа зависит от объёма работ, наличия материалов и доступа на объект. Сам выбор даты её не бронирует.'),('Можно заказать оформление не к Новому году?','Да. Студия также оформляет коммерческие пространства живой и декоративной флористикой. Покажите объект и расскажите, к какому событию готовитесь.')]
faq=sec('questions','<div class="v9-heading"><div><h2>Вопросы<br>о декоре</h2></div><div class="v9-faq">'+''.join(f'<details><summary>{q}<span aria-hidden="true">+</span></summary><div><p>{a}</p></div></details>' for q,a in faq_items)+'</div></div>')
def public_https(value):
    url = urlsplit(value)
    return url.scheme == 'https' and bool(url.hostname) and not (url.username or url.password or url.fragment)

endpoint=os.environ.get('DEKORIYA_LEAD_ENDPOINT','').strip()
policy=os.environ.get('DEKORIYA_POLICY_URL','').strip()
consent=os.environ.get('DEKORIYA_CONSENT_URL','').strip()
version=os.environ.get('DEKORIYA_CONSENT_VERSION','').strip()
if any((endpoint,policy,consent,version)) and not all((endpoint,policy,consent,version)):
    raise ValueError('Lead activation needs the receiver, published policy and consent URLs, and a consent version')
if endpoint and not (all(map(public_https,(endpoint,policy,consent))) and re.fullmatch(r'[a-zA-Z0-9._-]{1,40}',version) and policy != consent):
    raise ValueError('Expected HTTPS endpoint, two distinct HTTPS document URLs, and a consent version')
policy=policy or './privacy/'
consent=consent or './consent/'
agreement=f'''<div class="lead-agreement"><label class="lead-consent"><input type="checkbox" name="consent" required aria-describedby="brief-consent-error"><span>Я даю согласие на обработку персональных данных</span></label><div class="lead-doc-links"><a href="{e(consent,quote=True)}" data-lead-doc="consent" target="_blank" rel="noopener">Текст согласия</a><a href="{e(policy,quote=True)}" data-lead-doc="policy" target="_blank" rel="noopener">Политика обработки данных</a></div><p id="brief-consent-error" data-error="consent" hidden></p></div>'''
fallback='<p data-unavailable>Приём заявок через сайт пока закрыт. <a href="tel:+79772666460">Позвонить Олесе</a></p>'
trap='<div class="lead-trap" aria-hidden="true"><label>Оставьте поле пустым <input name="website" tabindex="-1" autocomplete="off"></label></div>'
contact=read('contact').replace('{{CONSENT_PROJECT}}',trap+agreement).replace('{{LEAD_AVAILABILITY}}',fallback)
settings=f'<div id="lead-settings" hidden data-endpoint="{e(endpoint,quote=True)}" data-policy="{e(policy,quote=True)}" data-consent="{e(consent,quote=True)}" data-consent-version="{e(version,quote=True)}"></div>'
footer=read('footer').replace('{{POLICY}}',e(policy,quote=True)).replace('{{CONSENT}}',e(consent,quote=True))
head=(R/'index.html').read_text().split('</head>')[0]
head=re.sub(r'<script[^>]+src=[^>]+></script>','',head)
head=re.sub(r'<link rel="stylesheet"[^>]+>','',head)
head=re.sub(r'\sdata-motion="[^"]+"','',head)
head=re.sub(r'data-version="[^"]+"','data-version="10.0"',head)
head=re.sub(r'data-build="[^"]+"','data-build="10.0.0" data-motion="v9"',head)
styles=['v81.css','v81-site.css','motion.css','v9.css','v10.css','v12.css'];scripts=['site-core.js','v9-motion.js','v10-lead.js','v10.js']
def stamp(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()[:10]
head+=''.join(f'<link rel="stylesheet" href="./{n}?v={V}-{stamp(n)}">' for n in styles)
head+=''.join(f'<script src="./{n}?v={V}-{stamp(n)}" defer></script>' for n in scripts)
html=head+'</head><body><a class="skip-link" href="#quiz">Перейти к содержанию</a><main>'+''.join([hero,quiz,projects,services,gallery,palette,olesya,season,partners,faq,contact])+'</main>'+footer+settings+'<dialog id="content-dialog" aria-labelledby="dialog-heading"><button type="button" class="close" aria-label="Закрыть окно">Закрыть ×</button><div id="dialog-content"></div></dialog><script type="application/json" id="site-data">'+json.dumps(data,ensure_ascii=False)+'</script><div class="reading-progress" aria-hidden="true"></div></body></html>'
(R/'index.html').write_text(html)
# Preserve deep links from the retired prototype; only one public homepage remains.
(R/'v9/index.html').write_text('''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Декория</title><link rel="canonical" href="https://oliverjone01-dev.github.io/turbium/Decoriya/website/"><script>location.replace('../'+location.search+location.hash)</script></head><body><a href="../">Перейти на главную Декории</a></body></html>''')
print('Built canonical v10:',len(html.encode()),'bytes; 11 sections; two lead paths')
