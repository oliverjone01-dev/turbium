(()=>{'use strict';
const $=(s,p=document)=>p.querySelector(s),$$=(s,p=document)=>[...p.querySelectorAll(s)];
const base=new URL(document.documentElement.dataset.assetBase||'./',document.currentScript.src),home=new URL(document.documentElement.dataset.homeUrl||'./',location.href),reduce=matchMedia('(prefers-reduced-motion:reduce)');
const config=JSON.parse($('#site-data')?.textContent||'{"cases":{},"gallery":[]}'),form=$('#brief-form'),dialog=$('#content-dialog'),content=$('#dialog-content');
let selected=null,returnFocus=null,currentPhotos=[],photoIndex=0,filter='all';
const fields=['business','zone','style','format','occasion','date'],key='dekoriya-brief-context-v1';
function save(){if(!form)return;try{sessionStorage.setItem(key,JSON.stringify({...Object.fromEntries(fields.map(k=>[k,form.elements[k].value])),selected:selected?.id||''}))}catch{}}
function summary(){if(!form)return;const labels={business:'Тип бизнеса',zone:'Зона',style:'Стиль',format:'Формат',occasion:'Повод',date:'Желаемая дата',case:'Выбранный пример'};let any=false;for(const [k,label]of Object.entries(labels)){const value=k==='case'?selected?.short||'':form.elements[k].value,n=$('#chosen-'+k);if(n){n.hidden=!value;n.textContent=label+': '+value}any=any||!!value}if($('.brief-summary'))$('.brief-summary').hidden=!any;$('#clear-context').hidden=!any;if($('#chosen-case'))$('#chosen-case').dataset.caseId=selected?.id||'';save()}
function setField(k,v){if(!form)return;if(k==='zone'&&form.elements.zone.value!==v)form.elements.format.value='';form.elements[k].value=v}
function reference(item){return{id:item.id,short:item.short||item.title,url:item.category?new URL('?reference='+item.id+'#'+(item.category==='concept'?'palette':'gallery'),home).href:(document.documentElement.dataset.homeUrl?new URL('?dk_project='+item.id,home):new URL('projects/'+item.id+'/',home)).href}}
function contact(){const target=$('#contact');if(!target)return;if(form)summary();returnFocus=null;target.querySelector('h2')?.focus({preventScroll:true});target.scrollIntoView({block:'start',behavior:reduce.matches?'instant':'smooth'})}
function choose(item){if(!item)return;selected=reference(item);const u=new URL(location.href);u.searchParams.delete('case');u.searchParams.set('reference',item.id);u.hash='contact';history.replaceState(null,'',u);summary();if(dialog?.open)dialog.close();contact()}
let draft={};try{draft=JSON.parse(sessionStorage.getItem(key)||'{}')}catch{}if(form)for(const k of fields)if(typeof draft[k]==='string')setField(k,draft[k]);
const params=new URL(location.href).searchParams,id=params.get('case')||params.get('reference')||draft.selected;
const chosen=Object.values(config.cases).find(x=>x.id===id)||config.gallery.find(x=>x.id===id);if(chosen)selected=reference(chosen);summary();
$('#clear-context')?.addEventListener('click',()=>{fields.forEach(k=>setField(k,''));selected=null;const u=new URL(location.href);u.searchParams.delete('case');u.searchParams.delete('reference');history.replaceState(null,'',u);summary();form.elements.object.focus({preventScroll:true})});
form?.addEventListener('change',summary);
document.addEventListener('dekoriya:project-received', () => {
  selected=null;
  fields.forEach(k=>setField(k,''));
  const u=new URL(location.href);
  u.searchParams.delete('case');
  u.searchParams.delete('reference');
  history.replaceState(null,'',u);
  summary();
});
function button(text,action,cls='btn outline'){const b=document.createElement('button');b.type='button';b.className=cls;b.dataset.action=action;b.textContent=text;return b}
function open(title,copy=''){if(!dialog)return;returnFocus=document.activeElement;content.replaceChildren();const h=document.createElement('h2');h.className='dialog-title';h.id='dialog-heading';h.textContent=title;h.tabIndex=-1;content.append(h);if(copy){const p=document.createElement('p');p.className='dialog-copy';p.textContent=copy;content.append(p)}dialog.showModal();h.focus({preventScroll:true});dialog.scrollTop=0}
dialog?.querySelector('.close').addEventListener('click',()=>dialog.close());
dialog?.addEventListener('close',()=>{if(returnFocus?.isConnected)returnFocus.focus({preventScroll:true})});
dialog?.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});
function renderPhoto(){const item=currentPhotos[photoIndex],focus=document.activeElement?.dataset.action;content.replaceChildren();const h=document.createElement('h2');h.className='dialog-title';h.id='dialog-heading';h.textContent=item.title;h.tabIndex=-1;const stage=document.createElement('div');stage.className='gallery-stage';stage.dataset.state='loading';stage.setAttribute('aria-busy','true');const img=document.createElement('img');img.className='gallery-large';img.alt=item.title;const status=document.createElement('p');status.className='gallery-load-status';status.setAttribute('role','status');status.textContent='Загружаем фотографию…';img.onload=()=>{if(!img.isConnected)return;stage.dataset.state='ready';stage.setAttribute('aria-busy','false');status.hidden=true};img.onerror=()=>{if(!img.isConnected)return;stage.dataset.state='error';stage.setAttribute('aria-busy','false');status.textContent='Не удалось загрузить фото. Выберите соседнее или откройте исходник.'};stage.append(img,status);img.src=new URL(item.image,base).href;const counter=document.createElement('p');counter.textContent=(photoIndex+1)+' / '+currentPhotos.length;const controls=document.createElement('div');controls.className='gallery-controls';controls.append(button('← Предыдущая','photo-prev'),button('Следующая →','photo-next'));const full=document.createElement('a');full.href=img.src;full.target='_blank';full.rel='noopener';full.className='v9-source';full.textContent='Открыть полный кадр ↗';content.append(h,stage,counter,controls,button('Обсудить этот пример','photo-discuss','btn'),full);if(['photo-prev','photo-next'].includes(focus))$('[data-action="'+focus+'"]',content).focus({preventScroll:true});else h.focus({preventScroll:true});if(img.complete&&img.naturalWidth)img.onload()}
function gallery(id){const item=config.gallery.find(x=>x.id===id);if(!item)return;currentPhotos=config.gallery.filter(x=>item.category==='concept'?x.category==='concept':x.category!=='concept'&&(filter==='all'||x.category===filter));if(!currentPhotos.some(x=>x.id===id))currentPhotos=[item];photoIndex=currentPhotos.findIndex(x=>x.id===id);open(item.title);renderPhoto()}
dialog?.addEventListener('keydown',e=>{if(!$('.gallery-large',dialog))return;if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();photoIndex=(photoIndex+(e.key==='ArrowRight'?1:-1)+currentPhotos.length)%currentPhotos.length;renderPhoto()}});
const guide=['Снимите общий вид и нужную зону.','Запишите примерные ширину, высоту и глубину.','Покажите двери, вывеску и проходы.','Уточните разрешённые крепления.','Скажите, декор будет на улице или внутри.','Покажите доступ к питанию.','Укажите желаемую дату, если она уже известна.','Уточните часы доступа на объект.','Пришлите примеры или готовое ТЗ.','Обсудите бюджет, срок использования и демонтаж.'];
function setScene(scene,on){scene.classList.toggle('service-expanded',on);scene.setAttribute('aria-expanded',String(on));scene.setAttribute('aria-label',on?'Собрать оформление обратно':scene.dataset.closedLabel);$('.scene-toggle-label',scene).textContent=on?'Собрать обратно':scene.dataset.closedLabel;$('.scene-toggle-icon',scene).textContent=on?'×':'+'}
$$('[data-action=explode]').forEach(scene=>{let pinned=false,pointer='';scene.addEventListener('pointerdown',e=>{pointer=e.pointerType});scene.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'&&matchMedia('(hover:hover)').matches&&!pinned)setScene(scene,true)});scene.addEventListener('pointerleave',e=>{if(e.pointerType==='mouse'&&!pinned&&!scene.matches(':focus-visible'))setScene(scene,false)});scene.addEventListener('keydown',e=>{if(e.key==='Escape'){pinned=false;setScene(scene,false)}});scene.addEventListener('click',e=>{if(pointer==='mouse'&&e.detail!==0&&!pinned){pinned=true;setScene(scene,true)}else{const on=scene.getAttribute('aria-expanded')!=='true';pinned=on;setScene(scene,on)}})});
function filterPhotos(value){filter=value;let count=0;$$('[data-gallery-id]').forEach(n=>{n.hidden=value!=='all'&&n.dataset.category!==value;if(!n.hidden)count++});$$('[data-filter]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.filter===value)));$('[data-gallery-count]').textContent='Фотографий: '+count;$$('[data-rail]').forEach(n=>n.scrollLeft=0)}
document.addEventListener('click',e=>{const el=e.target.closest('button,a,[role=button]');if(!el)return;const action=el.dataset.action,text=el.textContent.trim();
if(el.dataset.case){e.preventDefault();choose(Object.values(config.cases).find(x=>x.id===el.dataset.case));return}
if(fields.some(k=>el.dataset[k])){e.preventDefault();for(const k of fields)if(el.dataset[k])setField(k,el.dataset[k]);summary();contact();return}
if(action==='lead-close'){dialog?.close();return}
if(action==='contact'){e.preventDefault();contact();return}
if(action==='gallery-open'){gallery(el.dataset.photo);return}
if(action==='choose-reference'){choose(config.gallery.find(x=>x.id===el.dataset.photo));return}
if(action==='photo-prev'||action==='photo-next'){photoIndex=(photoIndex+(action==='photo-next'?1:-1)+currentPhotos.length)%currentPhotos.length;renderPhoto();return}
if(action==='photo-discuss'){choose(currentPhotos[photoIndex]);return}
if(el.dataset.filter){filterPhotos(el.dataset.filter);return}
if(el.dataset.railDir){const rail=el.closest('section').querySelector('[data-rail]');rail.scrollBy({left:Number(el.dataset.railDir)*rail.clientWidth*.82,behavior:reduce.matches?'instant':'smooth'});return}
if(action==='guide'){open('Что подготовить перед оформлением',guide.map((x,i)=>(i+1)+'. '+x).join('\n'));content.append(button('Обсудить объект','dialog-contact','btn'));return}
if(action==='dialog-contact'){dialog.close();contact();return}
if(text==='Меню'||/menu/i.test(el.dataset.name||'')){open('Декория');for(const[id,label]of [['projects','Работы'],['services','Что оформляем'],['palette','Стили'],['olesya','Олеся'],['quiz','Подобрать оформление'],['contact','Обсудить объект'],['tel:+79772666460','+7 (977) 266-64-60'],['https://t.me/+79772666460','Написать в Telegram']]){const a=document.createElement('a');a.href=id.includes(':')?id:'#'+id;a.className='btn outline';a.textContent=label;a.addEventListener('click',()=>dialog.close());content.append(a)}return}
});
const scale=()=>{const w=document.documentElement.clientWidth;document.documentElement.style.setProperty('--desktop-scale',w/1440);document.documentElement.style.setProperty('--mobile-scale',Math.min(w,640)/390)};scale();addEventListener('resize',scale,{passive:true});
const progress=$('.reading-progress');let scheduled=false;
function scroll(){scheduled=false;const total=document.documentElement.scrollHeight-innerHeight;progress?.style.setProperty('--progress',String(total>0?scrollY/total:0));}
addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(scroll)}},{passive:true});addEventListener('resize',scroll);if(dialog)new MutationObserver(()=>{document.documentElement.classList.toggle('dialog-open',dialog.open);scroll()}).observe(dialog,{attributes:true,attributeFilter:['open']});scroll();
if(params.has('reference')&&location.hash!=='#contact')requestAnimationFrame(()=>gallery(params.get('reference')));
})();
