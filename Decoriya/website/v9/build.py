"""Build an isolated v9 motion prototype from the published v8.3 structure."""
from pathlib import Path
import json,re

P=Path(__file__).parent
ROOT=P.parent
html=(ROOT/'index.html').read_text()
def section(id,body):
 global html
 pattern=r'<section\b(?=[^>]*\bid="'+id+r'")[^>]*>.*?</section>'
 html,n=re.subn(pattern,lambda _:body,html,count=1,flags=re.S)
 assert n==1, f'Missing source section: {id}'

palette='''<section id="palette" class="v9-section v9-dark" aria-labelledby="v9-palette-title"><div class="v9-heading"><p class="v9-kicker">ПРИМЕР ОФОРМЛЕНИЯ / НОВЫЙ ГОД</p><div><h2 id="v9-palette-title">Один образ.<br>Все детали.</h2><p>От общего вида до фактуры вблизи. Рассмотрите пример оформления, которое можно обсудить для вашего пространства.</p></div></div><div class="v9-editorial"><div><div class="v9-picture" aria-busy="false"><img src="../assets/v9/01-restaurant-front-768.webp" width="1536" height="1024" alt="Концепт новогоднего ресторанного входа с бордовым бархатом и хвоей" loading="lazy"><p class="v9-image-status" role="status" hidden></p></div><p class="v9-image-note">Вариант оформления / концепция для обсуждения</p></div><div class="v9-copy"><div class="v9-tabs" role="tablist" aria-label="Ракурсы оформления"><button type="button" role="tab" aria-selected="true" aria-controls="v9-concept-panel" data-v9-view="0">Общий вид</button><button type="button" role="tab" aria-selected="false" aria-controls="v9-concept-panel" tabindex="-1" data-v9-view="1">Ракурс</button><button type="button" role="tab" aria-selected="false" aria-controls="v9-concept-panel" tabindex="-1" data-v9-view="2">Детали</button></div><div id="v9-concept-panel" role="tabpanel" tabindex="0"><h3 data-v9-title>Хвоя задаёт форму.<br>Бархат держит акцент.</h3><p data-v9-copy>Оформление следует архитектуре входа: хвойный портал, глубокий бордовый текстиль и два латунных фонаря.</p><p class="v9-materials" data-v9-materials>Хвоя · бархат · латунь</p><button type="button" class="btn" data-action="choose-reference" data-photo="concept-v9-0">Обсудить этот пример <span aria-hidden="true">↗</span></button></div></div></div></section>'''
process='''<section id="process" class="v9-section v9-process" aria-labelledby="v9-process-title"><div class="v9-heading"><p class="v9-kicker">КАК СОБИРАЕТСЯ ОФОРМЛЕНИЕ</p><div><h2 id="v9-process-title">От пространства<br>к его характеру.</h2><p>На каждом этапе понятно, что обсуждаем, что готовим и что потребуется от вас.</p></div></div><div class="v9-process-tabs" role="tablist" aria-label="Этапы работы"><button type="button" role="tab" aria-selected="true" aria-controls="v9-process-panel" data-v9-step="0"><span class="v9-step-number">01</span>Объект</button><button type="button" role="tab" aria-selected="false" aria-controls="v9-process-panel" tabindex="-1" data-v9-step="1"><span class="v9-step-number">02</span>Концепция</button><button type="button" role="tab" aria-selected="false" aria-controls="v9-process-panel" tabindex="-1" data-v9-step="2"><span class="v9-step-number">03</span>Подготовка</button><button type="button" role="tab" aria-selected="false" aria-controls="v9-process-panel" tabindex="-1" data-v9-step="3"><span class="v9-step-number">04</span>Монтаж</button></div><div class="v9-editorial" id="v9-process-panel" role="tabpanel" tabindex="0"><div><div class="v9-picture" aria-busy="false"><img src="../assets/v9/01-restaurant-front-768.webp" width="1536" height="1024" alt="Пример входной группы для обсуждения оформления" loading="lazy"><p class="v9-image-status" role="status" hidden></p></div><p class="v9-image-note">Иллюстрации этапов / пример работы с оформлением</p></div><div class="v9-copy"><h3 data-v9-title>Смотрим на пространство.</h3><p data-v9-copy>Обсуждаем вход, витрину или интерьер. Уточняем размеры, окружение и желаемую дату.</p><dl class="v9-duties"><div><dt>Ваша часть</dt><dd data-v9-client>Показываете зону и рассказываете о задаче.</dd></div><div><dt>Наша часть</dt><dd data-v9-studio>Уточняем масштаб, доступ и условия.</dd></div></dl><button type="button" class="btn" data-action="contact">Обсудить объект <span aria-hidden="true">↗</span></button></div></div></section>'''
section('palette',palette)
section('process',process)
html=html.replace('src="./assets/','src="../assets/').replace('href="./assets/','href="../assets/').replace('srcset="./assets/','srcset="../assets/').replace(', ./assets/',', ../assets/').replace('href="./projects/','href="../projects/')
html=html.replace('href="projects/','href="../projects/').replace('href="sitemap.xml"','href="../sitemap.xml"')
html=html.replace('&quot;./assets/','&quot;../assets/').replace("url('./assets/","url('../assets/").replace('url(./assets/','url(../assets/')
html=re.sub(r'href="\./v81([^\"]+)"',r'href="../v81\1"',html)
html=re.sub(r'src="\./v81\.js[^\"]*"',r'src="./site-core.js?v=9.0.0"',html)
html=html.replace('data-build="8.3.0"','data-build="9.0.0-preview" data-motion="v9"')
html=html.replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,follow">')
html=html.replace('</head>','<link rel="stylesheet" href="./motion.css?v=9.0.0"><script src="./motion.js?v=9.0.0" defer></script></head>')
# The deferred scripts execute in source order. Core is already declared before motion.
config_re=r'(<script type="application/json" id="site-data">)(.*?)(</script>)'
m=re.search(config_re,html,re.S)
config=json.loads(m.group(2))
for i,(filename,title) in enumerate([('01-restaurant-front','Концепт / новогодний вход'),('02-restaurant-angle','Концепт / другой ракурс входа'),('03-velvet-detail','Концепт / бархат и хвоя вблизи')]):
 config['gallery'].append({'id':f'concept-v9-{i}','title':title,'image':f'./assets/v9/{filename}-1536.webp','category':'concept'})
html=html[:m.start(2)]+json.dumps(config,ensure_ascii=False)+html[m.end(2):]
(P/'index.html').write_text(html)

core=(ROOT/'v81.js').read_text()
def patch(old,new):
 global core
 assert core.count(old)==1, old[:100]
 core=core.replace(old,new,1)
patch("base=new URL('./',document.currentScript.src)","base=new URL('../',document.currentScript.src)")
patch("function animate(n){if(n&&!reduce.matches)n.animate([{opacity:.3,transform:'translateY(14px)'},{opacity:1,transform:'translateY(0)'}],{duration:180,easing:'cubic-bezier(0,0,.2,1)'})}","const transient=new WeakMap();function animate(n){if(!n||reduce.matches)return;transient.get(n)?.cancel();const a=n.animate([{opacity:.55,transform:'translateY(10px)'},{opacity:1,transform:'translateY(0)'}],{duration:220,easing:'cubic-bezier(.2,.7,.2,1)'});transient.set(n,a);a.finished.catch(()=>{});}reduce.addEventListener('change',()=>{if(reduce.matches)document.getAnimations().forEach(a=>a.cancel())});")
patch("if(!reduce.matches){$$('#hero", "if(!reduce.matches&&document.documentElement.dataset.motion!=='v9'){$$('#hero")
patch("currentPhotos=config.gallery.filter(x=>!visible.length||visible.includes(x.id));", "currentPhotos=config.gallery.filter(x=>item.category==='concept'?x.category==='concept':(!visible.length||visible.includes(x.id)));")
old_start=core.index('function renderPhoto()')
old_end=core.index("dialog?.addEventListener('keydown'",old_start)
core=core[:old_start]+'''function chooseReference(item){if(!item)return;selected={id:item.id,short:item.title,url:new URL((item.category==='concept'?'v9/':'')+'?reference='+item.id+'#'+(item.category==='concept'?'palette':'gallery'),base).href};const url=new URL(location.href);url.searchParams.delete('case');url.searchParams.set('reference',item.id);url.hash='contact';history.replaceState(null,'',url);summary();if(dialog.open)dialog.close();contact()}
function renderPhoto(){const focusAction=document.activeElement?.dataset.action,item=currentPhotos[photoIndex];content.replaceChildren();const h=document.createElement('h2');h.className='dialog-title';h.id='dialog-heading';h.textContent=item.title;const stage=document.createElement('div');stage.className='gallery-stage';stage.dataset.state='loading';stage.setAttribute('aria-busy','true');const img=document.createElement('img');img.alt=item.title;img.className='gallery-large';const status=document.createElement('p');status.className='gallery-load-status';status.setAttribute('role','status');status.textContent='Загружаем фотографию…';stage.append(img,status);img.onload=()=>{if(!img.isConnected)return;stage.dataset.state='ready';stage.setAttribute('aria-busy','false');status.hidden=true;animate(img)};img.onerror=()=>{if(!img.isConnected)return;stage.dataset.state='error';stage.setAttribute('aria-busy','false');status.hidden=false;status.textContent='Фотография пока недоступна. Можно выбрать другую или открыть исходник.'};img.src=new URL(item.image,base).href;const counter=document.createElement('p');counter.textContent=(photoIndex+1)+' / '+currentPhotos.length;const controls=document.createElement('div');controls.className='gallery-controls';controls.append(button('← Предыдущая','photo-prev','btn outline'),button('Следующая →','photo-next','btn outline'));const link=document.createElement('a');link.href=img.src;link.target='_blank';link.rel='noopener';link.className='btn outline';link.textContent='Открыть фотографию ↗';content.append(h,stage,counter,controls,button('Обсудить этот пример','photo-discuss'),link);h.tabIndex=-1;const focus=focusAction==='photo-prev'||focusAction==='photo-next'?$('[data-action="'+focusAction+'"]',content):h;focus.focus({preventScroll:true});if(img.complete&&img.naturalWidth)img.onload();}
'''+core[old_end:]
patch("if(action==='photo-discuss'){const item=currentPhotos[photoIndex];selected={id:item.id,short:item.title,url:new URL('?reference='+item.id+'#gallery',base).href};const url=new URL(location.href);url.searchParams.delete('case');url.searchParams.set('reference',item.id);url.hash='contact';history.replaceState(null,'',url);summary();dialog.close();contact();return}","if(action==='photo-discuss'){chooseReference(currentPhotos[photoIndex]);return}if(action==='choose-reference'){chooseReference(config.gallery.find(x=>x.id===el.dataset.photo));return}")
patch("url:new URL('?reference='+p.id+'#gallery',base).href", "url:new URL((p.category==='concept'?'v9/':'')+'?reference='+p.id+'#'+(p.category==='concept'?'palette':'gallery'),base).href")
(P/'site-core.js').write_text(core)
print('Built isolated v9 preview:',len(html),'HTML chars;',len(core),'core JS chars')
