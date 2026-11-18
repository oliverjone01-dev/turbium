"""Build the canonical v9 homepage and keep the former preview as a redirect."""
from pathlib import Path
from html import escape as e
import json,re,hashlib,os
from urllib.parse import urlsplit
R=Path(__file__).resolve().parents[1];T=R/'tools/templates';V='9.4.2'
data=json.loads((T/'site-data-v9.json').read_text())
def read(name):return (T/(name+'-v9.html')).read_text()
def btn(text,attrs='data-action="contact"',outline=False):return f'<button type="button" class="btn'+(' outline' if outline else '')+f'" {attrs}>{text}<span aria-hidden="true">↗</span></button>'
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
hero=re.sub(r'</section>\s*$',lambda _:read('hero-evening')+'</section>',hero)
# Full native responsive page: no desktop/mobile copies below the approved hero.
business=sec('business',heading('ВАШ ОБЪЕКТ','Что оформить<br>в вашем пространстве?','Выберите тип объекта. Покажем, с каких зон можно начать.')+'''<div class="v9-editorial v9-business"><div class="v9-business-tabs" role="tablist" aria-label="Тип бизнеса">'''+''.join(f'<button type="button" role="tab" aria-selected="{str(i==0).lower()}" aria-controls="v9-business-panel" tabindex="{0 if i==0 else -1}" data-business-view="{i}"><span>0{i+1}</span>{text}<span aria-hidden="true">↗</span></button>' for i,text in enumerate(['Кафе и рестораны','Магазины','Салоны и студии','Офисы и пространства']))+'''</div><div id="v9-business-panel" role="tabpanel"><div class="v9-business-photo">'''+image('./assets/v94/portfolio/i-37-720.webp','Новогодний вход Surf Coffee','',True)+'''</div><div class="v9-business-copy"><p data-business-copy>Хвойный портал у двери, свет в витрине или композиция в зале. Сначала определим, что гость увидит с улицы.</p>'''+btn('Обсудить оформление','data-business="Кафе или ресторан" data-occasion="Новый год"')+'''</div></div></div>''')
cards=''
for key,c in data['cases'].items():
 thumb='i-55' if key=='myata' else 'i-77'
 cards+=f'<article class="v9-case"><a class="v9-photo-link" href="./projects/{c["id"]}/" aria-label="Смотреть кейс {e(c["short"])}">'+image(f'./assets/v94/portfolio/{thumb}-720.webp',c['short'])+f'<span class="v9-photo-arrow" aria-hidden="true">↗</span></a><div class="v9-case-caption"><div><p class="v9-kicker">РЕАЛИЗОВАННЫЙ ПРОЕКТ</p><h3><a href="./projects/{c["id"]}/">{c["short"]}</a></h3><p>{c["materials"]}</p></div>'+btn('Обсудить похожее',f'data-case="{c["id"]}"',True)+'</div></article>'
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
items=[x for x in data['gallery'] if x.get('category')!='concept']
gallery=sec('gallery',heading('ПОРТФОЛИО','Входы, фасады<br>и детали','Фотографии выполненных работ. Откройте интересующий кадр, чтобы рассмотреть его целиком.')+'<div class="v9-gallery-toolbar"><div class="v9-filters" role="group" aria-label="Фильтр фотографий">'+''.join(f'<button type="button" data-filter="{k}" aria-pressed="{str(i==0).lower()}">{label}</button>' for i,(k,label) in enumerate([('all','Все'),('entrance','Входы'),('facade','Фасады'),('detail','Детали')]))+'</div><p data-gallery-count aria-live="polite">12 фотографий</p></div><div class="v9-gallery-rail" data-rail tabindex="0" aria-label="Фотографии портфолио; листайте горизонтально">'+''.join(f'<button type="button" class="v9-gallery-card" data-gallery-id="{x["id"]}" data-category="{x["category"]}" data-action="gallery-open" data-photo="{x["id"]}"><span class="v9-gallery-image">'+image(f'./assets/v94/portfolio/{x["id"]}-720.webp',x['title'])+f'<span class="v9-photo-arrow" aria-hidden="true">↗</span></span><span class="v9-gallery-caption"><span class="v9-kicker">{i+1:02}</span><span>{x["title"]}</span></span></button>' for i,x in enumerate(items))+'</div><div class="rail-controls"><button type="button" data-rail-dir="-1" aria-label="Предыдущие фотографии">←</button><button type="button" data-rail-dir="1" aria-label="Следующие фотографии">→</button><span>Листайте фотографии</span></div>','v9-paper')
palette=read('palette')
olesya=sec('olesya','<div class="v9-editorial v9-expert"><div class="v9-expert-image">'+image('./assets/v81/174-549-0e4aa.webp','Олеся Овакимян за работой с композицией')+'</div><div class="v9-copy"><p class="v9-kicker">ЧЕЛОВЕК ЗА ПРОЕКТОМ</p><h2>Олеся<br>Овакимян.</h2><p class="v9-expert-role">Декоратор и руководитель студии</p><p>Олеся определяет направление оформления. Дизайнеры готовят эскизы, флористы и декораторы собирают композиции, монтажники устанавливают их на объекте.</p><div class="v9-expert-ways"><div><h3>Концепция с нуля</h3><p>Эскизы, палитра и подбор материалов.</p></div><div><h3>Ваш готовый проект</h3><p>Оформление по техническому заданию.</p></div></div>'+btn('Обсудить задачу')+'</div></div>')
process=read('process')
conditions=sec('conditions',heading('ДО ПЕРВОГО МОНТАЖА','Детали, о которых<br>договариваемся заранее.','Чтобы оформление стало частью пространства, согласуем не только его внешний вид.')+'<div class="v9-three">'+''.join(f'<article>{icon(k)}<h3>{h}</h3><p>{p}</p></article>' for k,h,p in [('material','Состав и материалы','Что входит в оформление, какие материалы используем и как обсуждаем возможные замены.'),('mount','Крепления и доступ','Где можно закрепить декор, как сохранить проходы и в какие часы работать на объекте.'),('date','Дата и завершение','К какой дате готовим оформление, как принимаем работу и что делаем с демонтажем.')])+'</div>'+btn('Обсудить условия'),'v9-dark')
budget=sec('budget',heading('МАСШТАБ ОФОРМЛЕНИЯ','От одного акцента<br>до целого пространства.','Стоимость зависит от размеров зоны, материалов, доставки и монтажа. Начать можно с фотографии объекта.')+'<div class="v9-three v9-scales">'+''.join(f'<article><p class="v9-kicker">0{i+1} / {tag}</p><h3>{h}</h3><p>{p}</p>'+btn(cta,f'data-format="{h}" data-zone="{zone}" data-occasion="Новый год"',True)+'</article>' for i,(tag,h,p,cta,zone) in enumerate([('АКЦЕНТ','Одна зона','Стойка, угол у входа или одна выразительная композиция.','Обсудить акцент','Интерьер'),('ВСТРЕЧА','Входная группа','Хвоя, текстиль и свет вокруг дверного проёма.','Обсудить вход','Входная группа'),('КОНЦЕПЦИЯ','Несколько зон','Вход, витрина и интерьер в одном направлении.','Обсудить проект','Несколько зон')]))+'</div><details class="v9-estimate"><summary>Из чего складывается смета <span aria-hidden="true">+</span></summary><div><p>Материалы и изготовление, подготовка композиций, доставка и монтаж обсуждаются отдельно. Итоговый состав зависит от вашего объекта.</p></div></details>','v9-paper')
partners=sec('partners','<div class="v9-editorial"><div class="v9-material-photo">'+image('./assets/studio/materials-wide-v6.webp','Цветы и бордовый бархат на фоне каменной аркады')+'</div><div class="v9-copy"><p class="v9-kicker">ДИЗАЙНЕРАМ И АВТОРАМ ПРОСТРАНСТВ</p><h2>Декор в логике<br>вашего проекта.</h2><p>Работаем с готовой концепцией и техническим заданием. Обсудим палитру, материалы и взаимодействие на объекте.</p>'+btn('Обсудить готовый проект','data-format="По готовому дизайн-проекту"')+'</div></div>')
guide=sec('guide','<div class="v9-guide"><div><p class="v9-kicker">ПЕРЕД ПЕРВЫМ РАЗГОВОРОМ</p><h2>Покажите пространство.<br>Остальное обсудим.</h2><p>Пара фотографий, примерные размеры и желаемая дата помогут начать. Если чего-то пока нет, это можно уточнить позже.</p></div><div class="v9-guide-actions">'+btn('Открыть памятку','data-action="guide"',True)+btn('Обсудить объект')+'</div></div>','v9-paper')
faq_items=[('Можно заказать декор по своему проекту?','Да. Пришлите эскиз или техническое задание. Команда обсудит с вами материалы, крепления и условия монтажа.'),('Как рассчитывают стоимость оформления?','Расчёт зависит от размеров зоны, материалов, доставки и монтажа. Пришлите фото и примерные размеры. Если бюджет уже определён, укажите его.'),('Когда обсуждать дату монтажа?','Укажите желаемую дату уже в первом сообщении. Возможность монтажа зависит от объёма работ, наличия материалов и доступа на объект. Сам выбор даты её не бронирует.'),('Можно заказать оформление не к Новому году?','Да. Студия также оформляет коммерческие пространства живой и декоративной флористикой. Покажите объект и расскажите, к какому событию готовитесь.')]
faq=sec('questions','<div class="v9-heading"><div><h2>Вопросы<br>о декоре</h2></div><div class="v9-faq">'+''.join(f'<details><summary>{q}<span aria-hidden="true">+</span></summary><div><p>{a}</p></div></details>' for q,a in faq_items)+'</div></div>')
contact=read('contact')
endpoint=os.environ.get('DEKORIYA_LEAD_ENDPOINT','').strip()
if endpoint:
 parsed=urlsplit(endpoint)
 if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
  raise ValueError('Expected public HTTPS lead endpoint')
 contact=contact.replace('data-lead-endpoint=""','data-lead-endpoint="'+e(endpoint,quote=True)+'"')
footer='''<footer id="footer" class="v9-section v9-footer"><a href="#hero" aria-label="Декория — к началу"><img src="./assets/logo.svg" alt="Декория" width="180" height="60" loading="lazy"></a><p>Новогоднее оформление для бизнеса<br>Москва и Московская область</p><a href="#hero">К началу ↑</a><p class="v9-copyright">© Декория, 2026</p></footer>'''
head=(R/'index.html').read_text().split('</head>')[0]
head=re.sub(r'<script[^>]+src=[^>]+></script>','',head)
head=re.sub(r'<link rel="stylesheet"[^>]+>','',head)
head=re.sub(r'\sdata-motion="[^"]+"','',head)
head=re.sub(r'data-version="[^"]+"','data-version="9.0"',head)
head=re.sub(r'data-build="[^"]+"','data-build="9.4.2" data-motion="v9"',head)
styles=['v81.css','v81-site.css','motion.css','v9.css'];scripts=['site-core.js','v9-motion.js']
def stamp(name):return hashlib.sha256((R/name).read_bytes()).hexdigest()[:10]
head+=''.join(f'<link rel="stylesheet" href="./{n}?v={V}-{stamp(n)}">' for n in styles)
head+=''.join(f'<script src="./{n}?v={V}-{stamp(n)}" defer></script>' for n in scripts)
html=head+'</head><body><a class="skip-link" href="#business">Перейти к содержанию</a><main>'+''.join([hero,business,projects,services,gallery,palette,olesya,process,conditions,budget,partners,guide,faq,contact])+'</main>'+footer+'<dialog id="content-dialog" aria-labelledby="dialog-heading"><button type="button" class="close" aria-label="Закрыть окно">Закрыть ×</button><div id="dialog-content"></div></dialog><script type="application/json" id="site-data">'+json.dumps(data,ensure_ascii=False)+'</script><div class="reading-progress" aria-hidden="true"></div></body></html>'
for group,panel,attribute in [('business','v9-business-panel','data-business-view'),('concept','v9-concept-panel','data-v9-view'),('process','v9-process-panel','data-v9-step')]:
 for i in range(4 if group!='concept' else 3):
  html=html.replace(f'{attribute}="{i}"',f'id="v9-{group}-tab-{i}" {attribute}="{i}"')
 html=html.replace(f'id="{panel}" role="tabpanel"',f'id="{panel}" aria-labelledby="v9-{group}-tab-0" role="tabpanel"')
(R/'index.html').write_text(html)
# Preserve deep links from the retired prototype; only one public homepage remains.
(R/'v9/index.html').write_text('''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="robots" content="noindex,follow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Декория</title><link rel="canonical" href="https://oliverjone01-dev.github.io/turbium/Decoriya/website/"><script>location.replace('../'+location.search+location.hash)</script></head><body><a href="../">Перейти на главную Декории</a></body></html>''')
print('Built canonical v9:',len(html.encode()),'bytes; 14 sections; preview redirects')
