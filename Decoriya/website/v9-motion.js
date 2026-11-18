(()=>{'use strict';
const $=(s,p=document)=>p.querySelector(s),$$=(s,p=document)=>[...p.querySelectorAll(s)],scriptURL=document.currentScript.src;
const reduce=matchMedia('(prefers-reduced-motion: reduce)'),fine=matchMedia('(hover:hover) and (pointer:fine)'),small=matchMedia('(max-width:1199px)');
const active=new Map();let heroFrame=0,heroVisible=true,targetX=0,targetY=0,currentX=0,currentY=0;
function stop(n){active.get(n)?.cancel();active.delete(n)}
function move(n,frames,duration=420,delay=0){if(!n||reduce.matches)return;stop(n);const a=n.animate(frames,{duration,delay,easing:'cubic-bezier(.2,.7,.2,1)'});active.set(n,a);a.finished.catch(()=>{}).finally(()=>{if(active.get(n)===a)active.delete(n)})}
function resetDepth(){cancelAnimationFrame(heroFrame);heroFrame=0;targetX=targetY=currentX=currentY=0;$('#hero')?.style.removeProperty('--hero-x');$('#hero')?.style.removeProperty('--hero-y')}
function refreshMotion(){if(reduce.matches){for(const a of document.getAnimations())a.cancel();active.clear();resetDepth()}}
reduce.addEventListener('change',refreshMotion);
fine.addEventListener('change',()=>{if(!fine.matches)resetDepth()});small.addEventListener('change',()=>{if(small.matches)resetDepth();compact.hidden=heroVisible||small.matches});
// A short entrance. Default CSS is visible, even with JS disabled or failed.
const hero=$('#hero');if(hero&&!reduce.matches){const device=$(small.matches?'.mobile':'.desktop',hero),nav=$('[data-name="00 Navigation / unboxed"]',device),title=$('h1',device),name=$('[data-name="Olesya / name and role"]',device);move(nav,[{opacity:.5,transform:'translateY(-10px)'},{opacity:1,transform:'none'}],440);const lines=title?[...title.children]:[];if(lines.length>1)lines.forEach((n,i)=>move(n,[{opacity:.55,transform:'translateY(22px)'},{opacity:1,transform:'none'}],small.matches?360:560,i*65));else move(title,[{opacity:.55,transform:'translateY(22px)'},{opacity:1,transform:'none'}],560,80);move(name,[{opacity:.5,transform:'translateY(8px)'},{opacity:1,transform:'none'}],460,small.matches?100:260)}
function paintHero(){heroFrame=0;if(reduce.matches||!fine.matches||small.matches||!heroVisible||hero.classList.contains('evening-active')||document.hidden)return;currentX+=(targetX-currentX)*.14;currentY+=(targetY-currentY)*.14;hero.style.setProperty('--hero-x',currentX.toFixed(2)+'px');hero.style.setProperty('--hero-y',currentY.toFixed(2)+'px');if(Math.abs(targetX-currentX)+Math.abs(targetY-currentY)>.05)heroFrame=requestAnimationFrame(paintHero)}
function startHero(){if(!heroFrame)heroFrame=requestAnimationFrame(paintHero)}
hero?.addEventListener('pointermove',e=>{if(e.pointerType!=='mouse'||reduce.matches||!fine.matches||small.matches||hero.classList.contains('evening-active'))return;const r=hero.getBoundingClientRect();targetX=((e.clientX-r.left)/r.width-.5)*-24;targetY=((e.clientY-r.top)/r.height-.5)*-16;startHero()},{passive:true});hero?.addEventListener('pointerleave',()=>{targetX=targetY=0;startHero()});
if(hero)new IntersectionObserver(es=>{heroVisible=es[0].isIntersecting;if(!heroVisible){cancelAnimationFrame(heroFrame);heroFrame=0}},{threshold:0}).observe(hero);document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(heroFrame);heroFrame=0}});
// Mouse drag is an enhancement. Touch keeps native horizontal scrolling.
$$('[data-rail]').forEach(rail=>{let start=null,dragging=false,suppressUntil=0;rail.addEventListener('dragstart',e=>e.preventDefault());rail.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'||e.button!==0)return;start={id:e.pointerId,x:e.clientX,y:e.clientY,left:rail.scrollLeft};dragging=false});rail.addEventListener('pointermove',e=>{if(!start||e.pointerId!==start.id)return;const dx=e.clientX-start.x,dy=e.clientY-start.y;if(!dragging&&Math.abs(dy)>Math.abs(dx)&&Math.abs(dy)>8){start=null;return}if(!dragging&&Math.abs(dx)>8){dragging=true;rail.classList.add('is-dragging');rail.setPointerCapture(e.pointerId)}if(dragging){e.preventDefault();rail.scrollLeft=start.left-dx}});const finish=e=>{if(!start)return;if(dragging)suppressUntil=performance.now()+350;try{if(rail.hasPointerCapture(start.id))rail.releasePointerCapture(start.id)}catch{}rail.classList.remove('is-dragging');start=null;dragging=false};rail.addEventListener('pointerup',finish);rail.addEventListener('pointercancel',finish);rail.addEventListener('lostpointercapture',finish);rail.addEventListener('pointerleave',e=>{if(start&&!dragging)finish(e)});rail.addEventListener('click',e=>{if(performance.now()<suppressUntil&&e.detail!==0){e.preventDefault();e.stopImmediatePropagation()}},true)});
// Decoded image cache and request tokens prevent stale frames on rapid choices.
const imageCache=new Map();function imageReady(url){if(!imageCache.has(url)){const img=new Image();const p=new Promise((resolve,reject)=>{img.onload=()=>resolve(img);img.onerror=()=>{imageCache.delete(url);reject(new Error('image unavailable'))}});img.src=url;imageCache.set(url,p)}return imageCache.get(url)}
function imageController(root){const slot=$('.v9-picture',root),status=$('.v9-image-status',root);let token=0;return async(url,alt)=>{const request=++token;slot.classList.add('is-loading');slot.classList.remove('is-error');slot.setAttribute('aria-busy','true');status.hidden=false;status.textContent='Загружаем фотографию…';try{const source=await imageReady(url);if(request!==token)return;const previous=$('img',slot),img=source.cloneNode();img.alt=alt;img.width=1536;img.height=1024;previous.replaceWith(img);slot.classList.remove('is-loading');status.hidden=true;slot.setAttribute('aria-busy','false');move(img,[{opacity:.5,transform:'scale(1.025)'},{opacity:1,transform:'scale(1)'}],small.matches?240:420)}catch{if(request!==token)return;slot.classList.remove('is-loading');slot.classList.add('is-error');slot.setAttribute('aria-busy','false');status.hidden=false;status.textContent='Фотография пока недоступна. Выберите другой ракурс или повторите нажатие.'}}}
// Local QA server only: reproduce real delayed/error HTTP image responses.
const qa=['127.0.0.1','localhost'].includes(location.hostname)?new URL(location.href).searchParams.get('qa'):null,qaNonce=Date.now();
function asset(path) {
  const url = new URL(path, scriptURL);
  if (qa) {
    const filename = url.pathname.split('/').at(-1);
    url.searchParams.set('__qa_nonce', String(qaNonce));
    if (qa === 'slow') url.searchParams.set('__qa_delay', filename.startsWith('05') ? '1.6' : '.15');
    if (qa === 'error' && filename.startsWith('04')) url.searchParams.set('__qa_error', '1');
  }
  return url.href;
}
const concept=$('#palette');if(concept?.classList.contains('v9-section')){const load=imageController(concept),tabs=$$('[data-v9-view]',concept),variants=[['assets/v9/01-restaurant-front-editorial-768.webp','Хвоя задаёт форму. Бархат держит акцент.','Оформление следует архитектуре входа: хвойный портал, глубокий бордовый текстиль и два латунных фонаря.','Хвоя · бархат · латунь'],['assets/v9/02-restaurant-angle-editorial-768.webp','Вход виден в объёме.','Другой ракурс показывает, как оформление связано с проёмом и боковыми окнами.','Масштаб · глубина · пропорции'],['assets/v9/03-velvet-detail-editorial-768.webp','Материалы вблизи.','Направленный ворс бархата, мелкая хвоя и спокойный металлический блик. Детали работают в одной палитре.','Фактура · складки · отражения']];let chosen=0;function select(i){chosen=i;$('#v9-concept-panel',concept).setAttribute('aria-labelledby','v9-concept-tab-'+i);tabs.forEach((t,j)=>{t.setAttribute('aria-selected',String(i===j));t.tabIndex=i===j?0:-1});const v=variants[i];$('[data-v9-title]',concept).textContent=v[1];$('[data-v9-copy]',concept).textContent=v[2];$('[data-v9-materials]',concept).textContent=v[3];$('[data-action="choose-reference"]',concept).dataset.photo='concept-v9-'+i;load(asset(v[0]),'Пример оформления: '+v[1])}tabs.forEach((t,i)=>{t.addEventListener('click',()=>select(i));t.addEventListener('keydown',e=>{const next=e.key==='Home'?0:e.key==='End'?tabs.length-1:['ArrowRight','ArrowDown'].includes(e.key)?(i+1)%tabs.length:['ArrowLeft','ArrowUp'].includes(e.key)?(i-1+tabs.length)%tabs.length:null;if(next!==null){e.preventDefault();select(next);tabs[next].focus()}})});}
const process = $('#process');
if (process?.classList.contains('v9-section')) {
  const load = imageController(process);
  const tabs = $$('[data-v9-step]', process);
  const steps = [
    {
      image: 'assets/v9/06-survey-1440.webp',
      alt: 'Декоратор измеряет проём у входа без праздничного оформления',
      caption: 'Иллюстрация этапа · обмер проёма',
      title: 'Смотрим на пространство.',
      copy: 'Обсуждаем вход, витрину или интерьер. Уточняем размеры, окружение и желаемую дату.',
      client: 'Показываете зону и рассказываете о задаче.',
      studio: 'Уточняем масштаб, доступ и условия.',
    },
    {
      image: 'assets/v9/07-concept-sketch-1440.webp',
      alt: 'Эскиз оформления входа и образцы бархата и латуни на столе',
      caption: 'Иллюстрация этапа · эскиз и образцы',
      title: 'Собираем характер оформления.',
      copy: 'Сопоставляем цвет, фактуру и свет с архитектурой и стилем вашего бизнеса.',
      client: 'Показываете примеры или готовое ТЗ.',
      studio: 'Готовим направление и обсуждаем материалы.',
    },
    {
      image: 'assets/v9/05-workshop-768.webp',
      alt: 'Декораторы готовят хвою и текстиль за рабочим столом',
      caption: 'Иллюстрация этапа · подготовка в мастерской',
      title: 'Готовим композиции.',
      copy: 'Согласованный образ превращается в элементы, которые можно собрать и установить на объекте.',
      client: 'Подтверждаете состав и условия работ.',
      studio: 'Комплектуем материалы и подготавливаем декор.',
    },
    {
      image: 'assets/v9/04-installation-768.webp',
      alt: 'Два декоратора закрепляют хвою на входе',
      caption: 'Иллюстрация этапа · установка на объекте',
      title: 'Собираем оформление на месте.',
      copy: 'Монтаж связывает отдельные элементы с реальным пространством. Проходы и условия крепления обсуждаем заранее.',
      client: 'Обеспечиваете согласованный доступ.',
      studio: 'Устанавливаем композицию и проверяем детали.',
    },
  ];
  const note = $('.v9-image-note', process);
  function selectStep(i) {
    $('#v9-process-panel', process).setAttribute('aria-labelledby', 'v9-process-tab-' + i);
    tabs.forEach((tab, j) => {
      tab.setAttribute('aria-selected', String(i === j));
      tab.tabIndex = i === j ? 0 : -1;
    });
    const step = steps[i];
    $('[data-v9-title]', process).textContent = step.title;
    $('[data-v9-copy]', process).textContent = step.copy;
    $('[data-v9-client]', process).textContent = step.client;
    $('[data-v9-studio]', process).textContent = step.studio;
    note.textContent = step.caption;
    load(asset(step.image), step.alt);
  }
  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => selectStep(i));
    tab.addEventListener('keydown', event => {
      const key = event.key;
      const last = tabs.length - 1;
      const next = { Home: 0, End: last, ArrowRight: (i + 1) % tabs.length, ArrowDown: (i + 1) % tabs.length,
        ArrowLeft: (i + last) % tabs.length, ArrowUp: (i + last) % tabs.length }[key];
      if (!Number.isInteger(next)) return;
      event.preventDefault();
      selectStep(next);
      tabs[next].focus();
    });
  });
}
// Reveal only once and only after intersection; no content is hidden in CSS.
const seen=new WeakSet();const observer=new IntersectionObserver(es=>{for(const e of es){if(!e.isIntersecting||seen.has(e.target))continue;seen.add(e.target);observer.unobserve(e.target);move(e.target,[{opacity:.55,transform:'translateY(38px)'},{opacity:1,transform:'none'}],small.matches?390:670)}},{threshold:.13});$$('#projects .v9-case,.v9-heading,.v9-three article,.v9-guide').forEach(n=>observer.observe(n));
// Business selection: stable image area, keyboard tabs, context follows the CTA.
const business=$('#business');if(business){const tabs=$$('[data-business-view]',business),values=[['Кафе или ресторан','i-37','Хвойный портал у двери, свет в витрине или композиция в зале. Сначала определим, что гость увидит с улицы.'],['Магазин','i-112','Оформление входа и витрины связывает сезон с продуктом. Оставляем вывеску, товар и проходы в центре внимания.'],['Салон или студия','i-18','Входная группа и зона встречи поддерживают характер салона. Сопоставляем цвет декора с фасадом и интерьером.'],['Офис / другое','i-95','Начать можно с рецепции, входа или одной композиции в общей зоне. Обсудим масштаб, доступ и режим работы.']];let request=0;function select(i){const token=++request;$('#v9-business-panel',business).setAttribute('aria-labelledby','v9-business-tab-'+i);tabs.forEach((t,j)=>{t.setAttribute('aria-selected',String(i===j));t.tabIndex=i===j?0:-1});const v=values[i];$('[data-business-copy]',business).textContent=v[2];$('button[data-business]',business).dataset.business=v[0];imageReady(new URL('assets/v94/portfolio/'+v[1]+'-720.webp',scriptURL).href).then(source=>{if(token!==request)return;const img=$('.v9-business-photo img',business);img.src=source.src;img.alt='Реальное оформление из портфолио: '+tabs[i].textContent.replace(/0[1-4]|↗/g,'').trim();move(img,[{opacity:.55,transform:'scale(1.025)'},{opacity:1,transform:'scale(1)'}],320)}).catch(()=>{})}tabs.forEach((t,i)=>{t.addEventListener('click',()=>select(i));t.addEventListener('keydown',e=>{const next=e.key==='Home'?0:e.key==='End'?3:['ArrowRight','ArrowDown'].includes(e.key)?(i+1)%4:['ArrowLeft','ArrowUp'].includes(e.key)?(i+3)%4:null;if(next!==null){e.preventDefault();select(next);tabs[next].focus()}})})}
// A filter reintroduces only the visible photographs, with a short stagger.
const photoGallery=$('#gallery');
photoGallery?.addEventListener('click', event=>{
 const trigger=event.target.closest('[data-filter]');
 if(!trigger||trigger.getAttribute('aria-pressed')==='true'||reduce.matches)return;
 requestAnimationFrame(()=>$$('[data-gallery-id]:not([hidden])',photoGallery).slice(0,4)
  .forEach((node,i)=>move(node,[{opacity:.45,transform:'translateY(9px)'},{opacity:1,transform:'none'}],310,i*33)));
});
// Native details stay functional without JavaScript. Animate only the visible body.
$$('.v9-faq details,.v9-estimate').forEach(d=>{d.addEventListener('toggle',()=>{if(d.open){const box=$(':scope>div',d);move(box,[{opacity:.4,transform:'translateY(-8px)'},{opacity:1,transform:'none'}],280)}})});
// Compact navigation appears only after the hero; no layout shift.
const compact=document.createElement('nav');compact.className='v9-compact-nav';compact.setAttribute('aria-label','Быстрая навигация');compact.hidden=true;compact.innerHTML='<a href="#hero" aria-label="Декория — к началу"><img src="'+new URL('assets/logo.svg',scriptURL).href+'" alt="Декория" width="120" height="40"></a><a href="#projects">Работы</a><a href="#services">Что оформляем</a><a href="#palette">Стили</a><a href="#olesya">Олеся</a><button class="btn" type="button" data-action="contact">Обсудить объект ↗</button>';document.body.append(compact);if(hero)new IntersectionObserver(es=>{compact.hidden=es[0].isIntersecting||small.matches},{threshold:0}).observe(hero);
// Expert portrait has extra image area; motion stops outside the section.
const expert=$('.v9-expert-image'),pattern=$('#contact');let depthRAF=0;function depth(){depthRAF=0;if(reduce.matches||!fine.matches||small.matches||document.hidden)return;if(expert){const r=expert.getBoundingClientRect();if(r.bottom>0&&r.top<innerHeight){const p=Math.max(0,Math.min(1,(innerHeight-r.top)/(innerHeight+r.height)));expert.style.setProperty('--expert-y',(-1-p*8).toFixed(2)+'%')}}}addEventListener('scroll',()=>{if(!depthRAF)depthRAF=requestAnimationFrame(depth)},{passive:true});if(pattern)new IntersectionObserver(es=>{if(es[0].isIntersecting){if(!reduce.matches)pattern.classList.add('v9-pattern-reveal')}},{threshold:.2}).observe(pattern);

})();

/* Switching keeps both layouts native. Evening is available without a script. */
(()=>{
 const root=document.querySelector('#hero'),stage=root?.querySelector('#hero-evening'),control=root?.querySelector('.hero-views');
 if(!root||!stage||!control)return;
 const buttons=[...control.querySelectorAll('[data-hero-view]')];
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const fine=matchMedia('(hover:hover) and (pointer:fine)');
 let cover='evening',frame=0,animations=[];
 const reset=()=>{if(frame)cancelAnimationFrame(frame);frame=0;['stage-x','stage-y','portrait-x','portrait-y'].forEach(k=>stage.style.removeProperty('--'+k));};
 const cancel=()=>{animations.forEach(a=>a.cancel());animations=[];reset();};
 function show(choice,url=true){
  cancel();cover=choice;const evening=choice==='evening';
  stage.hidden=!evening;root.classList.toggle('evening-active',evening);
  buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.heroView===choice)));
  control.querySelector('[role=status]').textContent=evening?'Вечерний монтаж.':'Студия.';
  if(url){const next=new URL(location.href);if(evening)next.searchParams.delete('hero');else next.searchParams.set('hero','studio');history.replaceState(history.state,'',next);}
  if(!reduced.matches&&url){
   const scene=evening?stage:[...root.children].find(n=>(n.classList.contains('mobile')||n.classList.contains('desktop'))&&n.getClientRects().length);
   if(scene)animations.push(scene.animate([{opacity:.35,translate:'0 8px'},{opacity:1,translate:'0 0'}],{duration:460,easing:'cubic-bezier(.2,.74,.26,1)'}));
  }
 }
 control.hidden=false;buttons.forEach(b=>b.addEventListener('click',()=>show(b.dataset.heroView)));
 if(new URLSearchParams(location.search).get('hero')==='studio')show('studio',false);
 let x=0,y=0;
 stage.addEventListener('pointermove',e=>{
  if(cover!=='evening'||reduced.matches||!fine.matches||e.pointerType!=='mouse')return;
  const r=stage.getBoundingClientRect();x=(e.clientX-r.left)/r.width-.5;y=(e.clientY-r.top)/r.height-.5;
  if(frame)return;
  frame=requestAnimationFrame(()=>{frame=0;stage.style.setProperty('--stage-x',(-x*32).toFixed(1)+'px');stage.style.setProperty('--stage-y',(-y*19).toFixed(1)+'px');stage.style.setProperty('--portrait-x',(x*22).toFixed(1)+'px');stage.style.setProperty('--portrait-y',(y*14).toFixed(1)+'px');});
 },{passive:true});
 stage.addEventListener('pointerleave',reset);
 reduced.addEventListener('change',()=>{if(reduced.matches)cancel();});
})();
