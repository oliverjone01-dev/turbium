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
    if(material){const r=material.getBoundingClientRect();if(r.top<innerHeight&&r.bottom>0){const p=clamp((innerHeight-r.top)/(innerHeight+r.height));material.style.setProperty('--parallax-y',((p-.5)*2*(fine.matches?C.parallax.material:C.parallax.mobile))+'px')}}
    if(steps){const r=steps.getBoundingClientRect(),p=clamp((innerHeight*.75-r.top)/(r.height+innerHeight*.25));steps.style.setProperty('--process-progress',p);steps.querySelectorAll('li').forEach((li,i)=>li.classList.toggle('active',p>i/3));}
  }
  function schedule(){if(!raf&&!document.hidden)raf=requestAnimationFrame(updateScroll)}
  function setupSpatial(){
    const S=C.spatial,controllers=[];
    document.querySelectorAll('[data-spatial]').forEach(button=>{
      const atlases=[...button.querySelectorAll('.sequence-strip')],canvas=button.querySelector('canvas'),ctx=canvas.getContext('2d',{alpha:true});
      const hint=button.querySelector('.teaser-hint-text'),closed=hint.textContent;
      let bitmaps=null,frameWidth=0,frameHeight=0,lastPaint=0;
      const urls=()=>atlases.map(i=>new URL(matchMedia('(max-width:767px)').matches?i.parentElement.querySelector('source').getAttribute('srcset'):i.getAttribute('src'),document.baseURI).href);
      const allReady=()=>bitmaps?.length===S.frames||atlases.every(i=>i.complete&&i.naturalWidth),sourceKey=()=>urls().join('|');
      let pinned=false,wanted=false,progress=0,target=0,raf=0,last=0,loading=null,loadedSrc='',draws=0,maxGap=0;
      const paint=()=>{button.classList.toggle('is-open',wanted);button.setAttribute('aria-expanded',String(wanted));hint.textContent=wanted?'Собрать обратно':closed};
      const stop=()=>{if(raf)cancelAnimationFrame(raf);raf=0;last=0;button.classList.remove('is-playing')};
      const staticView=()=>{progress=target;stop();paint();button.dataset.frame=String(Math.round(progress*(S.frames-1)))};
      const draw=()=>{
        const fw=bitmaps?frameWidth:atlases[0].naturalWidth/S.columns,fh=bitmaps?frameHeight:atlases[0].naturalHeight/S.rows;
        if(!fw||!fh)return;
        if(canvas.width!==fw||canvas.height!==fh){canvas.width=fw;canvas.height=fh}
        const p=progress*(S.frames-1),a=Math.floor(p),b=Math.min(S.frames-1,a+1),mix=p-a;
        ctx.clearRect(0,0,fw,fh);
        // Additive premultiplied blending of neighbouring REAL camera samples avoids
        // 27fps stepping; neither frame is skewed or transformed in the browser.
        ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1-mix;
        if(bitmaps)ctx.drawImage(bitmaps[a],0,0,fw,fh);else{const ia=a%S.stripFrames;ctx.drawImage(atlases[Math.floor(a/S.stripFrames)],ia%S.columns*fw,Math.floor(ia/S.columns)*fh,fw,fh,0,0,fw,fh)}
        if(mix>.001){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=mix;if(bitmaps)ctx.drawImage(bitmaps[b],0,0,fw,fh);else{const ib=b%S.stripFrames;ctx.drawImage(atlases[Math.floor(b/S.stripFrames)],ib%S.columns*fw,Math.floor(ib/S.columns)*fh,fw,fh,0,0,fw,fh)}}
        ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';button.dataset.frame=String(Math.round(p));draws++;
      };
      const tick=now=>{
        raf=0;if(document.hidden){last=0;return}
        const dt=last?Math.min(100,now-last):0;if(last)maxGap=Math.max(maxGap,now-last);last=now;
        const direction=Math.sign(target-progress);progress=clamp(progress+direction*dt/S.duration);
        if(direction>0)progress=Math.min(progress,target);else progress=Math.max(progress,target);
        if(now-lastPaint>=15.5||Math.abs(progress-target)<.00001){draw();lastPaint=now}
        if(Math.abs(progress-target)<.00001){stop();button.dataset.draws=String(draws);button.dataset.maxFrameGap=Math.round(maxGap)+'ms';paint()}
        else raf=requestAnimationFrame(tick);
      };
      const play=()=>{paint();if(reduced.matches){staticView();return}if(progress===target){stop();return}button.classList.add('is-playing');if(!raf){last=0;lastPaint=0;draws=0;maxGap=0;draw();raf=requestAnimationFrame(tick)}};
      const directPrepare=()=>{
        if(allReady()&&loadedSrc===sourceKey())return Promise.resolve(true);
        if(loading)return loading;button.setAttribute('aria-busy','true');
        loading=Promise.all(atlases.map(img=>{img.loading='eager';return new Promise((resolve,reject)=>{
          if(img.complete&&img.naturalWidth){resolve();return}
          const done=()=>{img.removeEventListener('load',ok);img.removeEventListener('error',bad)},ok=()=>{done();resolve()},bad=()=>{done();reject(new Error('Camera strip not loaded'))};img.addEventListener('load',ok,{once:true});img.addEventListener('error',bad,{once:true});
        }).then(()=>img.decode())})).then(async()=>{
          loadedSrc=sourceKey();const fw=atlases[0].naturalWidth/S.columns,fh=atlases[0].naturalHeight/S.rows;canvas.width=fw;canvas.height=fh;
          // Upload small textures across paint opportunities while the poster is visible.
          for(const img of atlases){await new Promise(resolve=>requestAnimationFrame(resolve));ctx.clearRect(0,0,fw,fh);ctx.drawImage(img,0,0,fw,fh,0,0,1,1)}
          await new Promise(resolve=>requestAnimationFrame(resolve));draw();button.dataset.sequenceReady='true';return true;
        }).catch(()=>false).finally(()=>{loading=null;button.removeAttribute('aria-busy')});return loading;
      };
      const prepare=()=>{
        if(allReady()&&loadedSrc===sourceKey())return Promise.resolve(true);
        if(loading)return loading;
        if(!window.Worker||!window.OffscreenCanvas||!window.createImageBitmap)return directPrepare();
        button.setAttribute('aria-busy','true');const key=sourceKey(),list=urls();
        loading=new Promise((resolve,reject)=>{
          const worker=new Worker(new URL('worker.js',list[0]));const timer=setTimeout(()=>{worker.terminate();reject(new Error('Camera decode timeout'))},20000);
          worker.onerror=()=>{clearTimeout(timer);worker.terminate();reject(new Error('Camera worker failed'))};
          worker.onmessage=e=>{clearTimeout(timer);worker.terminate();if(e.data.error){reject(new Error(e.data.error));return}if(bitmaps)for(const f of bitmaps)f.close();bitmaps=e.data.frames;frameWidth=e.data.width;frameHeight=e.data.height;loadedSrc=key;button.dataset.sequenceSource='worker-bitmaps';button.dataset.frameSize=frameWidth+'x'+frameHeight;button.dataset.sequenceReady='true';resolve(true)};
          worker.postMessage({urls:list,columns:S.columns,rows:S.rows});
        }).catch(()=>{loading=null;button.removeAttribute('aria-busy');return directPrepare()}).finally(()=>{loading=null;button.removeAttribute('aria-busy')});return loading;
      };
      const set=open=>{
        wanted=open;target=open?1:0;
        if(reduced.matches){staticView();return}
        if(!open&&progress===0){paint();return}
        if(allReady()&&loadedSrc===sourceKey()){play();return}
        hint.textContent='Готовим анимацию…';
        // A slow first download must not leave the control indefinitely busy.
        // Keep decoding in the background; the next interaction can use it.
        Promise.race([prepare(),new Promise(resolve=>setTimeout(()=>resolve(false),5000))]).then(ok=>{
          target=wanted?1:0;
          if(ok)play();
          else{button.removeAttribute('aria-busy');button.dataset.sequenceReady='fallback';staticView()}
        });
      };
      button.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')set(true)});
      button.addEventListener('pointerleave',()=>{if(!pinned)set(false)});
      button.addEventListener('click',()=>{pinned=!pinned;set(pinned)});
      button.addEventListener('focus',()=>{if(button.matches(':focus-visible'))set(true)});
      button.addEventListener('blur',()=>{if(!pinned)set(false)});
      button.addEventListener('keydown',e=>{if(e.key==='Escape'){pinned=false;set(false)}});
      reduced.addEventListener('change',()=>{target=wanted?1:0;staticView()});
      controllers.push({button,resume:()=>{if(progress!==target&&!reduced.matches)play()},settle:()=>{target=wanted?1:0;staticView()}});
    });
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)controllers.forEach(c=>c.resume())});
    if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(!e.isIntersecting)controllers.find(c=>c.button===e.target)?.settle()}));controllers.forEach(c=>observer.observe(c.button))}
    addEventListener('resize',()=>controllers.forEach(c=>c.settle()),{passive:true});
  }
  function setupMagnetic(){document.querySelectorAll('[data-magnetic]').forEach(el=>{
    el.addEventListener('pointermove',e=>{if(!fine.matches||reduced.matches||e.pointerType!=='mouse')return;const r=el.getBoundingClientRect(),x=(e.clientX-r.left-r.width/2)/r.width*10,y=(e.clientY-r.top-r.height/2)/r.height*10;el.style.transform=`translate3d(${clamp(x,-5,5)}px,${clamp(y,-5,5)}px,0)`});el.addEventListener('pointerleave',()=>el.style.transform='');
  })}
  function boot(){
    setupEditorial();entrance();observeReveals();setupSpatial();setupMagnetic();
    const contact=document.querySelector('#contact');
    if(contact&&'IntersectionObserver'in window)new IntersectionObserver(es=>contact.classList.toggle('pattern-active',es[0].isIntersecting&&es[0].intersectionRatio>=.15),{threshold:.15}).observe(contact);
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
