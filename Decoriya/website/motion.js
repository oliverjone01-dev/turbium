(() => {
  'use strict';
  const C = window.DK_MOTION;
  if (!C) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(min-width:1101px) and (hover:hover) and (pointer:fine)');
  const active = new Set(), observed = new WeakSet(), wordGroups = new WeakMap();
  let raf = 0, observer, hero, material, steps, header, back;
  const room = {x:0,y:0,targetX:0,targetY:0};
  const clamp = (v,a=0,b=1) => Math.min(b,Math.max(a,v));
  function animate(el,keyframes,opts={}) {
    if (!el || reduced.matches || !el.animate) return null;
    const a=el.animate(keyframes,{duration:C.control,easing:C.easing,...opts});
    active.add(a);a.finished.catch(()=>{}).finally(()=>active.delete(a));return a;
  }
  function entrance() {
    hero=document.querySelector('.hero-stage');header=document.querySelector('.header');
    animate(header,[{opacity:0,translate:'0 -12px'},{opacity:1,translate:'0 0'}],{duration:C.hero.header,delay:C.hero.headerDelay,fill:'backwards'});
    animate(document.querySelector('.hero-backdrop img'),[{opacity:.45,transform:'scale(1.035)'},{opacity:1,transform:'scale(1)'}],{duration:C.hero.background});
    document.querySelectorAll('.title-mask>span').forEach((el,i)=>animate(el,[{transform:'translateY(110%) rotate(2deg)'},{transform:'translateY(0) rotate(0)'}],{duration:C.hero.title,delay:C.hero.titleDelay+i*C.stagger,fill:'backwards'}));
    // Portrait, desk and exact hand overlay enter as one rigid composition.
    animate(document.querySelector('.hero-anchor'),[{opacity:0,transform:'translateY(36px)'},{opacity:1,transform:'translateY(0)'}],{duration:C.hero.person,delay:C.hero.personDelay,fill:'backwards'});
    animate(document.querySelector('.hero-byline'),[{opacity:0,transform:'translateY(12px)'},{opacity:1,transform:'translateY(0)'}],{duration:700,delay:850,fill:'backwards'});
  }
  function setupEditorial() {
    document.querySelectorAll('main h2,[data-editorial-reveal]').forEach(el=>{
      if(wordGroups.has(el))return;
      const label=el.innerText.replace(/\s+/g,' ').trim();
      const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
      const textNodes=[];let node;while((node=walker.nextNode()))if(node.textContent.trim()&&!node.parentElement.closest('[aria-hidden=true]'))textNodes.push(node);
      const words=[];
      for(const text of textNodes){const fragment=document.createDocumentFragment();
        text.textContent.split(/(\s+)/).forEach(token=>{
          if(!token.trim()){fragment.append(document.createTextNode(token));return;}
          const mask=document.createElement('span'),word=document.createElement('span');
          mask.className='editorial-word-mask';mask.setAttribute('aria-hidden','true');word.className='editorial-word';word.textContent=token;mask.append(word);fragment.append(mask);words.push(word);
        });text.replaceWith(fragment);
      }
      if(words.length){el.setAttribute('aria-label',label);wordGroups.set(el,words);}
    });
  }
  function revealWords(el) {
    const words=wordGroups.get(el)||[];
    words.forEach((word,i)=>animate(word,[{opacity:0,transform:'translateY(108%) rotate(3deg)'},{opacity:1,transform:'translateY(0) rotate(0)'}],{duration:C.editorial.duration,delay:Math.min(i*C.editorial.stagger,C.editorial.maxDelay),fill:'backwards'}));
  }
  function drawIcon(el) {
    el.querySelectorAll('path').forEach((path,i)=>{
      const length=path.getTotalLength();
      animate(path,[{strokeDasharray:String(length),strokeDashoffset:length},{strokeDasharray:String(length),strokeDashoffset:0}],{duration:C.icons.duration,delay:i*90});
    });
  }
  function observeReveals() {
    if(!('IntersectionObserver'in window))return;
    observer??=new IntersectionObserver(entries=>entries.forEach(e=>{
      if(!e.isIntersecting)return;
      if(wordGroups.has(e.target))revealWords(e.target);
      else if(e.target.matches('[data-icon-motion]'))drawIcon(e.target);
      else animate(e.target,[{opacity:.55,transform:'translateY(26px)'},{opacity:1,transform:'translateY(0)'}],{duration:C.reveal});
      observer.unobserve(e.target);
    }),{threshold:.12});
    document.querySelectorAll('main h2,[data-editorial-reveal],.reveal,.service,[data-icon-motion]').forEach(el=>{if(!observed.has(el)){observed.add(el);observer.observe(el)}});
  }
  function updateScroll() {
    raf=0;const h=document.documentElement;
    h.style.setProperty('--reading',clamp(scrollY/Math.max(1,h.scrollHeight-innerHeight)));
    header?.classList.toggle('compact',scrollY>80);back?.classList.toggle('visible',scrollY>innerHeight*.8);
    if(reduced.matches||!fine.matches){room.x=room.y=room.targetX=room.targetY=0;hero?.style.setProperty('--room-x','0px');hero?.style.setProperty('--room-y','0px');hero?.style.setProperty('--room-rx','0deg');hero?.style.setProperty('--room-ry','0deg');hero?.style.setProperty('--hero-bg-y','0px');}
    else if(hero){const r=hero.getBoundingClientRect();if(r.bottom>0&&r.top<innerHeight){
      room.x+=(room.targetX-room.x)*.095;room.y+=(room.targetY-room.y)*.095;
      hero.style.setProperty('--room-x',(room.x*C.hero.backgroundPointer)+'px');hero.style.setProperty('--room-y',(room.y*C.hero.pointerVertical)+'px');
      hero.style.setProperty('--room-rx',(-room.y*C.hero.tilt)+'deg');hero.style.setProperty('--room-ry',(room.x*C.hero.tilt)+'deg');
      hero.style.setProperty('--hero-bg-y',Math.min(C.hero.backgroundScroll,Math.max(0,-r.top*.1))+'px');
      if(Math.abs(room.targetX-room.x)+Math.abs(room.targetY-room.y)>.002)schedule();
    }}
    if(reduced.matches)return;
    if(material&&fine.matches){const r=material.getBoundingClientRect();if(r.top<innerHeight&&r.bottom>0){const p=clamp((innerHeight-r.top)/(innerHeight+r.height));material.style.setProperty('--parallax-y',((p-.5)*2*C.parallax.material)+'px')}}
    if(steps){const r=steps.getBoundingClientRect(),p=clamp((innerHeight*.75-r.top)/(r.height+innerHeight*.25));steps.style.setProperty('--process-progress',p);steps.querySelectorAll('li').forEach((li,i)=>li.classList.toggle('active',p>i/3));}
  }
  function schedule(){if(!raf&&!document.hidden)raf=requestAnimationFrame(updateScroll)}
  function setupSpatial(){
    document.querySelectorAll('[data-spatial]').forEach(button=>{
      let pinned=false;
      const set=open=>{button.classList.toggle('is-open',open);button.setAttribute('aria-expanded',String(open));button.querySelector('.teaser-hint-text').textContent=open?'Собрать композицию':'Разобрать по слоям'};
      button.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')set(true)});
      button.addEventListener('pointerleave',()=>{if(!pinned)set(false)});
      button.addEventListener('click',()=>{pinned=!pinned;set(pinned)});
      button.addEventListener('focus',()=>{if(button.matches(':focus-visible'))set(true)});
      button.addEventListener('blur',()=>{if(!pinned)set(false)});
      button.addEventListener('keydown',e=>{if(e.key==='Escape'){pinned=false;set(false)}});
    });
  }
  function setupMagnetic(){document.querySelectorAll('[data-magnetic]').forEach(el=>{
    el.addEventListener('pointermove',e=>{if(!fine.matches||reduced.matches||e.pointerType!=='mouse')return;const r=el.getBoundingClientRect(),x=(e.clientX-r.left-r.width/2)/r.width*10,y=(e.clientY-r.top-r.height/2)/r.height*10;el.style.transform=`translate3d(${clamp(x,-5,5)}px,${clamp(y,-5,5)}px,0)`});el.addEventListener('pointerleave',()=>el.style.transform='');
  })}
  function boot(){
    setupEditorial();entrance();observeReveals();setupSpatial();setupMagnetic();
    material=document.querySelector('[data-parallax]');steps=document.querySelector('.steps');back=document.querySelector('.back-top');
    back?.addEventListener('click',()=>scrollTo({top:0,behavior:reduced.matches?'instant':'smooth'}));
    hero?.addEventListener('pointermove',e=>{if(!fine.matches||reduced.matches||e.pointerType!=='mouse')return;const r=hero.getBoundingClientRect();room.targetX=clamp((e.clientX-r.left)/r.width*2-1,-1,1);room.targetY=clamp((e.clientY-r.top)/r.height*2-1,-1,1);schedule()});
    hero?.addEventListener('pointerleave',()=>{room.targetX=room.targetY=0;schedule()});
    addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule,{passive:true});
    document.addEventListener('dk:content',()=>{observeReveals();schedule()});
    reduced.addEventListener('change',()=>{active.forEach(a=>a.cancel());schedule()});fine.addEventListener('change',schedule);
    document.addEventListener('visibilitychange',()=>{if(document.hidden&&raf){cancelAnimationFrame(raf);raf=0}else schedule()});
    schedule();window.DKMotion={animate,refresh:()=>{observeReveals();schedule()},reduced:()=>reduced.matches,config:C};
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
