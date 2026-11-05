/* Self-contained partner demo. No requests are sent by the contact form. */
const app = document.querySelector('#app');
const lightbox = document.querySelector('#lightbox');
const contact = document.querySelector('#contact');
const ads = DEKORIYA.ads;
const slideLabels = ad => ad.slideLabels || DEKORIYA.slideLabels;
const offerLabel = ad => ad.phase==='fairytale'?'Сказочная подача':ad.phase==='creative'?'Новая подача':ad.phase==='test'?'Тематический тест':'Основное предложение';
const state = {category:'Все предложения', phase:'all', query:'', sort:'recommended', onlySaved:false, current:null, slide:0, catalogScroll:0, returnTo:'#showroom', drafts:new Map(), saved:new Set()};
try { state.saved = new Set(JSON.parse(localStorage.getItem('decoriya-favorites') || '[]')); } catch { /* Private browsing may restrict storage. */ }
const esc = value => String(value).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icon = (name,size=20) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${{
  arrow:'<path d="M4 12h15m-6-6 6 6-6 6"/>', back:'<path d="m14 5-7 7 7 7"/>', next:'<path d="m10 5 7 7-7 7"/>', close:'<path d="m6 6 12 12M6 18 18 6"/>', heart:'<path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/>', location:'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>', expand:'<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>', check:'<path d="m5 12 4 4L20 5"/>', chat:'<path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H3l1.8-5A8.5 8.5 0 1 1 21 11.5Z"/>', share:'<path d="M12 16V3m-5 5 5-5 5 5M5 13v8h14v-8"/>', download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>', leaf:'<path d="M20 3c1 11-3 18-10 16C3 17 3 8 20 3ZM4 21 15 9"/>'
}[name] || ''}</svg>`;
const logo = (white=false) => `<img src="assets/logo.svg" width="182" height="40" alt="ДЕКОРИЯ"${white?' style="filter:brightness(0) invert(1)"':''}>`;
const demoBar = () => `<div class="demo-bar"><div class="demo-inner"><span class="demo-label">Демонстрация для партнёров · ${DEKORIYA.season}</span><a href="#home">Главная ДЕКОРИИ</a></div></div>`;
const footer = () => `<footer class="footer"><div class="container footer-inner"><div>${logo()}<p>Варианты новогоднего оформления. Состав, стоимость и доступные даты подтверждаем по объекту. Изображения показывают концепции оформления.</p></div><div class="footer-links"><a href="#home">Лендинг</a><a href="#showroom">Витрина</a></div></div></footer>`;
const avitoMark = () => '<a href="#showroom" class="avito-mark" aria-label="Демонстрационная витрина Авито"><span class="avito-dots"><i></i><i></i><i></i><i></i></span>Авито<em>демо</em></a>';
const marketHeader = () => `${demoBar()}<div class="market-top"><div class="container"><span>Макет витрины и объявлений ДЕКОРИИ</span><a href="#home">Вернуться на лендинг</a></div></div><div class="container market-nav">${avitoMark()}<form id="search-form" class="search-form" role="search"><input name="q" type="search" value="${esc(state.query)}" placeholder="Найти оформление" aria-label="Поиск по предложениям ДЕКОРИИ"><button type="submit">Найти</button></form><div class="market-location">${icon('location',16)}Москва и область</div><button class="icon-btn" data-action="favorites" aria-label="Показать избранное">${icon('heart')}</button></div>`;

function listing(ad){
  return `<article class="listing-card"><a class="listing-image" href="#ad/${ad.id}" aria-label="Открыть: ${esc(ad.title)}"><img src="${ad.slides[0]}" alt="${esc(ad.short)}" width="1600" height="1200" loading="lazy"></a><button class="save-button" data-save="${ad.id}" aria-pressed="${state.saved.has(ad.id)}" aria-label="${state.saved.has(ad.id)?'Убрать из избранного':'Сохранить'}: ${esc(ad.title)}">${icon('heart',19)}</button><a class="listing-title" href="#ad/${ad.id}">${esc(ad.title)}</a><p class="listing-price">Стоимость по расчёту</p><p class="listing-summary">${esc(ad.summary)}</p><p class="listing-meta">${offerLabel(ad)} · Москва и область</p></article>`;
}

function renderHome(){
  document.title='ДЕКОРИЯ | Новогоднее оформление 2026/27';
  document.body.classList.remove('has-mobile-cta');
  app.innerHTML=`${demoBar()}<header class="container site-header"><a class="brand" href="#home">${logo()}<span class="brand-caption">Сезонный и событийный декор</span></a><nav class="site-nav" aria-label="Основная навигация"><a href="#home" data-scroll="directions">Направления</a><a href="#showroom?phase=fairytale">Сказочная подача</a><a class="btn btn-dark" href="#showroom">Витрина ${icon('arrow',18)}</a></nav></header>
  <main id="main"><section class="container hero"><div class="hero-copy"><p class="eyebrow">Москва и Подмосковье · Новый год 2027</p><h1>Праздник начинается<br>с вашего пространства.</h1><p class="hero-description">Оформим вход, витрину или интерьер. Хвоя, бархатные ленты и свет складываются в композицию под ваш объект.</p><a class="btn btn-light" href="#showroom">Посмотреть предложения ${icon('arrow')}</a><p class="hero-note">Выберите оформление и откройте полную галерею</p></div><div class="hero-photo"><img src="assets/photos/commercial.webp" alt="Вход с хвойным обрамлением, бордовым бархатом и тёплым светом" width="1600" height="1194" fetchpriority="high"><div class="photo-caption"><b>Хвоя. Бархат. Тёплый свет.</b><span>Вариант оформления входа</span></div></div></section>
  <section class="container section fairytale-showcase"><div class="section-head"><div><p class="eyebrow">Семь направлений · по десять карточек</p><h2>Сказочная подача</h2><p class="fairytale-intro">Хвоя, свет и детали. Полные серии оформления для входов, витрин и интерьеров.</p></div><a class="link-arrow" href="#showroom?phase=fairytale">Открыть все серии ${icon('arrow')}</a></div><div class="listing-grid">${ads.filter(a=>a.phase==='fairytale').slice(0,3).map(listing).join('')}</div></section><section class="container section new-showcase"><div class="section-head"><div><p class="eyebrow">Семь полных серий по десять карточек</p><h2>Свет, фактура и цвет</h2></div><a class="link-arrow" href="#showroom?phase=creative">Новая подача ${icon('arrow')}</a></div><div class="listing-grid">${ads.filter(a=>a.phase==='creative').slice(0,3).map(listing).join('')}</div></section><div class="container"><section class="intro-line"><h2>Под архитектуру.<br>Под интерьер.<br>Под ваш праздник.</h2><p>Начинаем с фотографии и размеров. Выбираем зоны, палитру и состав декора. Согласуем расчёт, материалы и дату монтажа, чтобы оформление вписалось в пространство.</p></section>
  <section class="section" id="directions"><div class="section-head"><div><p class="eyebrow">Основные предложения</p><h2>С чего начнём оформление</h2></div><a class="link-arrow" href="#showroom">Вся витрина ${icon('arrow')}</a></div><div class="direction-grid">${ads.filter(a=>a.phase==='start').map(ad=>`<a class="direction-card" href="#ad/${ad.id}"><div class="direction-photo"><img src="${ad.photo}" alt="${esc(ad.short)}" width="1600" height="1194" loading="lazy"></div><div class="direction-title"><div><h3>${esc(ad.short)}</h3><p>${esc(ad.summary)}</p></div><span class="icon-btn">${icon('arrow')}</span></div></a>`).join('')}</div></section></div>
  <section class="section trend-section" id="trends"><div class="container"><div class="section-head"><div><p class="eyebrow">Новые варианты оформления</p><h2>Три характера праздника</h2></div><p>Тематические предложения для обсуждения. Комплектацию и дату определяем по объекту.</p></div><div class="trend-grid">${ads.filter(a=>a.phase==='test').map(ad=>`<article class="trend-card"><a href="#ad/${ad.id}"><img src="${ad.photo}" alt="${esc(ad.short)}" width="1600" height="1194" loading="lazy"></a><div><h3><a href="#ad/${ad.id}">${esc(ad.short)}</a></h3><p>${esc(ad.palette)}</p><a class="trend-link" href="#ad/${ad.id}">Смотреть оформление</a></div></article>`).join('')}</div></div></section>
  <section class="container section journey"><div><p class="eyebrow">От идеи до оформления</p><h2>Понятный следующий шаг</h2><p>В витрине собраны предложения и галереи. В каждом объявлении можно рассмотреть общий вид, состав и детали, затем подготовить запрос по своему объекту.</p></div><ol class="journey-list"><li><span>01</span><div><strong>Выберите направление</strong><p>Вход, ёлка, интерьер или витрина. Откройте подходящее объявление.</p></div></li><li><span>02</span><div><strong>Рассмотрите оформление</strong><p>Общий вид, детали, состав оформления и следующий шаг для расчёта.</p></div></li><li><span>03</span><div><strong>Соберите запрос для Олеси</strong><p>Фото, размеры, адрес и желаемая дата. Олеся уточнит задачу и подготовит предложение.</p></div></li></ol></section>
  <section class="container landing-cta"><div><h2>Посмотрите, как клиент увидит наше предложение.</h2><p>Откройте витрину, выберите объявление, пролистайте галерею и подготовьте пример обращения.</p></div><a class="btn btn-light" href="#showroom">Открыть витрину ${icon('arrow')}</a></section></main>${footer()}`;
}

function filteredAds(){
  const q=state.query.toLocaleLowerCase('ru').trim();
  const result=ads.filter(ad=>(state.category==='Все предложения'||ad.category===state.category)&&(state.phase==='all'||ad.phase===state.phase)&&(!state.onlySaved||state.saved.has(ad.id))&&(!q||[ad.title,ad.summary,ad.palette,ad.category].join(' ').toLocaleLowerCase('ru').includes(q)));
  if(state.sort==='title')result.sort((a,b)=>a.title.localeCompare(b.title,'ru'));
  return result;
}
function syncCatalogURL(){
  const p=new URLSearchParams();if(state.query)p.set('q',state.query);if(state.category!=='Все предложения')p.set('category',state.category);if(state.phase!=='all')p.set('phase',state.phase);if(state.onlySaved)p.set('saved','1');if(state.sort!=='recommended')p.set('sort',state.sort);
  const route='#showroom'+(p.size?'?'+p:'');history.replaceState(null,'',route);state.returnTo=route;
}
function updateResults(){
  const result=filteredAds();
  document.querySelector('#results-count').textContent=`Предложения · ${result.length}`;
  document.querySelector('#results-grid').innerHTML=result.length?result.map(listing).join(''):`<div class="empty"><h3>${state.onlySaved?'В избранном пока пусто':'Подходящих предложений пока нет'}</h3><p>${state.onlySaved?'Нажмите на сердечко у понравившегося оформления. Оно появится здесь.':'Попробуйте другое слово или сбросьте фильтры, чтобы увидеть все варианты оформления.'}</p><button class="btn btn-outline" data-action="reset">Показать все предложения</button></div>`;
  document.querySelectorAll('[data-category]').forEach(b=>{const pool=ads.filter(a=>state.phase==='all'||a.phase===state.phase);b.querySelector('span').textContent=b.dataset.category==='Все предложения'?pool.length:pool.filter(a=>a.category===b.dataset.category).length;b.classList.toggle('active',b.dataset.category===state.category);b.setAttribute('aria-pressed',String(b.dataset.category===state.category));});
  document.querySelectorAll('[data-phase]').forEach(b=>{b.classList.toggle('active',b.dataset.phase===state.phase);b.setAttribute('aria-pressed',String(b.dataset.phase===state.phase));});
  const saved=document.querySelector('[data-action="saved-filter"]');saved.classList.toggle('active',state.onlySaved);saved.setAttribute('aria-pressed',String(state.onlySaved));
  syncCatalogURL();
}
function renderShowroom(){
  document.title='Витрина ДЕКОРИИ | Демонстрация Авито';document.body.classList.remove('has-mobile-cta');
  const p=new URLSearchParams(location.hash.split('?')[1]||'');
  state.query=p.get('q')||'';state.category=DEKORIYA.categories.includes(p.get('category'))?p.get('category'):'Все предложения';state.phase=['start','test','creative','fairytale'].includes(p.get('phase'))?p.get('phase'):'all';state.onlySaved=p.get('saved')==='1';state.sort=p.get('sort')==='title'?'title':'recommended';state.returnTo=location.hash;
  app.innerHTML=`${marketHeader()}<main id="main" class="container"><section class="market-brand"><div class="market-brand-copy"><div class="market-avatar">${logo()}</div><div><h1>ДЕКОРИЯ</h1><p>Новогоднее оформление входов, витрин и интерьеров. Подбираем палитру и состав под ваш объект.</p><div class="market-brand-line">${icon('location',14)}Москва и согласованные маршруты Подмосковья</div></div></div><div class="market-brand-photo" role="img" aria-label="Новогодний вход с хвойным обрамлением"></div></section><div class="market-layout"><aside class="market-sidebar" aria-label="Категории предложений"><h2>Наши предложения</h2><div class="cat-list">${DEKORIYA.categories.map(c=>`<button class="cat-btn" data-category="${c}" aria-pressed="false">${c}<span>${c==='Все предложения'?ads.length:ads.filter(a=>a.category===c).length}</span></button>`).join('')}</div><div class="sidebar-about"><h3>О студии</h3><p>Сезонный и событийный декор. Состав и стоимость определяем по фотографии объекта, размерам и задаче.</p></div><div class="sidebar-about"><h3>Для расчёта</h3><p>Фото пространства, размеры, адрес и желаемая дата оформления.</p></div></aside><section aria-label="Объявления"><div class="results-head"><h2 id="results-count" aria-live="polite">Предложения</h2><label><span class="sr-only">Сортировка</span><select id="sort"><option value="recommended"${state.sort==='recommended'?' selected':''}>По порядку запуска</option><option value="title"${state.sort==='title'?' selected':''}>По названию</option></select></label></div><div class="result-tabs"><button class="chip" data-phase="all">Все</button><button class="chip chip-fairytale" data-phase="fairytale">Сказочная подача · 7</button><button class="chip chip-new" data-phase="creative">Новая подача · 7</button><button class="chip" data-phase="start">Основной запуск · 4</button><button class="chip" data-phase="test">Тематические тесты · 3</button><button class="chip chip-favorite" data-action="saved-filter" aria-pressed="false">${icon('heart',15)}Избранное</button></div><div id="results-grid" class="listing-grid"></div></section></div><p class="market-bottom">Это демонстрационная витрина для обсуждения с партнёрами. В «Новой подаче» и «Сказочной подаче» по семь серий из десяти карточек. Базовые версии доступны в соседних вкладках. Состав оформления и даты подтверждает Олеся.</p></main>${footer()}`;
  updateResults();
}

function renderAd(ad){
  state.current=ad;state.slide=0;document.title=`${ad.title} | ДЕКОРИЯ`;document.body.classList.add('has-mobile-cta');
  app.innerHTML=`${marketHeader()}<main id="main" class="container"><nav class="breadcrumb" aria-label="Навигационная цепочка"><a href="#home">ДЕКОРИЯ</a><span>›</span><a href="${esc(state.returnTo)}" data-return>Витрина</a><span>›</span><span>${esc(ad.category)}</span></nav><div class="ad-layout"><article><h1 class="ad-title">${esc(ad.title)}</h1><div class="ad-subline"><span>${offerLabel(ad)}</span><button data-save="${ad.id}" aria-pressed="${state.saved.has(ad.id)}">${icon('heart',16)}${state.saved.has(ad.id)?'Сохранено':'В избранное'}</button><button data-action="share">${icon('share',16)}Ссылка</button></div><div class="gallery-stage" aria-label="Галерея объявления"><button class="gallery-open" data-action="lightbox" aria-label="Открыть слайд на весь экран"><img id="gallery-image" src="${ad.slides[0]}" alt="${esc(ad.title)}: ${slideLabels(ad)[0]}" width="1600" height="1200" fetchpriority="high"></button><button class="gallery-arrow gallery-prev" data-slide-step="-1" aria-label="Предыдущий слайд">${icon('back',18)}</button><button class="gallery-arrow gallery-next" data-slide-step="1" aria-label="Следующий слайд">${icon('next',18)}</button><span class="gallery-counter" id="gallery-counter" aria-live="polite">1 / ${ad.slides.length}</span><span class="gallery-expand">${icon('expand',15)}</span></div><div class="thumbs" style="--slide-count:${Math.min(ad.slides.length,5)}" aria-label="Выбрать слайд">${ad.slides.map((src,i)=>`<button class="thumb" data-slide="${i}" aria-current="${i===0}" aria-label="Слайд ${i+1}: ${slideLabels(ad)[i]}"><img src="${src}" alt="" width="1600" height="1200" loading="lazy"><span>${i+1}. ${slideLabels(ad)[i]}</span></button>`).join('')}</div><section class="ad-section"><h2>Описание</h2><div class="ad-body">${ad.body.map(p=>`<p>${esc(p)}</p>`).join('')}</div></section><section class="ad-section"><h2>Что можно включить</h2><ul class="includes">${ad.includes.map(p=>`<li>${icon('check',18)}<span>${esc(p)}</span></li>`).join('')}</ul></section>${ad.terms?`<section class="ad-section"><h2>Условия работы</h2><ul class="includes">${ad.terms.map(p=>`<li>${icon('check',18)}<span>${esc(p)}</span></li>`).join('')}</ul><p class="measure-condition">Выезд и замер бесплатно после подписания договора.</p></section>`:''}<section class="ad-section"><h2>Детали предложения</h2><dl class="ad-facts"><div><dt>Палитра и материалы</dt><dd>${esc(ad.palette)}</dd></div><div><dt>География</dt><dd>Москва, Подмосковье по согласованному маршруту</dd></div><div><dt>Стоимость</dt><dd>По размерам, составу декора и условиям монтажа</dd></div><div><dt>Демонтаж</dt><dd>Обсуждаем до заказа и указываем в расчёте</dd></div></dl><div class="concept-note">Галерея показывает варианты оформления, а не выполненные клиентские объекты. Масштаб, реквизит, материалы и доступную дату согласуем по вашему пространству.</div></section></article><aside class="seller-box" aria-label="Обращение в ДЕКОРИЮ"><p class="seller-price">Стоимость<br>по расчёту</p><p class="seller-price-note">Фото, размеры и задача помогут определить состав оформления.</p>${ad.visualization?`<p class="visualization-offer">${icon('check',18)}<span>${esc(ad.visualization)}</span></p>`:''}<button class="btn btn-blue" data-action="contact">${icon('chat',18)}Написать</button><button class="btn btn-soft" data-action="contact">Подготовить запрос</button><div class="seller-row"><div class="seller-avatar">${logo()}</div><div><b>ДЕКОРИЯ</b><p>Сезонный и событийный декор</p></div></div><p class="seller-details">Олеся уточняет задачу, готовит предложение и организует продакшен у клиента.</p><a class="seller-link" href="${esc(state.returnTo)}" data-return>Все предложения студии ${icon('next',15)}</a>${ad.phase==='fairytale'?'<p class="seller-tag">Сказочная подача · 10 карточек</p>':ad.phase==='creative'?'<p class="seller-tag">Новая подача · 10 карточек</p>':ad.phase==='test'?'<p class="seller-tag">Тематический вариант для обсуждения</p>':''}</aside></div><section class="related"><h2>Ещё варианты оформления</h2><div class="listing-grid">${ads.filter(a=>a.id!==ad.id && a.phase===ad.phase).slice(0,4).map(listing).join('')}</div></section></main>${footer()}<div class="mobile-ad-cta"><div>Стоимость по расчёту<small>Состав под ваш объект</small></div><button class="btn btn-blue" data-action="contact">Написать</button></div>`;
}

function setSlide(index){
  if(!state.current)return;const ad=state.current;state.slide=(index+ad.slides.length)%ad.slides.length;
  const image=document.querySelector('#gallery-image');if(image){image.src=ad.slides[state.slide];image.alt=`${ad.title}: ${slideLabels(ad)[state.slide]}`;document.querySelector('#gallery-counter').textContent=`${state.slide+1} / ${ad.slides.length}`;document.querySelectorAll('[data-slide]').forEach(b=>b.setAttribute('aria-current',String(Number(b.dataset.slide)===state.slide)));}
  if(lightbox.open){const label=document.activeElement?.getAttribute('aria-label');renderLightbox();if(label)Array.from(lightbox.querySelectorAll('[aria-label]')).find(n=>n.getAttribute('aria-label')===label)?.focus();}
}
function renderLightbox(){
  const ad=state.current;
  lightbox.innerHTML=`<div class="lightbox-header"><div><h2 id="lightbox-title">${esc(ad.title)}</h2><p>${slideLabels(ad)[state.slide]} · ${state.slide+1} из ${ad.slides.length}</p></div><button class="icon-btn" data-close="lightbox" aria-label="Закрыть просмотр">${icon('close')}</button></div><div class="lightbox-main"><button class="icon-btn" data-slide-step="-1" aria-label="Предыдущий слайд">${icon('back')}</button><img src="${ad.slides[state.slide]}" alt="${esc(slideLabels(ad)[state.slide])}" width="1600" height="1200"><button class="icon-btn" data-slide-step="1" aria-label="Следующий слайд">${icon('next')}</button></div><div class="lightbox-controls"><span>← → Листать · Esc Закрыть</span><button class="download-link" data-action="download-slide">Скачать PNG</button></div>`;
}
function openLightbox(){renderLightbox();lightbox.showModal();document.body.classList.add('modal-open');}
async function downloadSlide(){
  const ad=state.current,index=state.slide;
  try{
    const image=new Image();image.src=ad.slides[index];await image.decode();
    const canvas=document.createElement('canvas');canvas.width=1600;canvas.height=1200;canvas.getContext('2d').drawImage(image,0,0,1600,1200);
    const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
    if(!blob)throw new Error('Empty image');
    const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`DEKORIYA-${ad.id}-${index+1}.png`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);notify('Слайд подготовлен в PNG, 1600 × 1200');
  }catch{notify('Не удалось скачать слайд. Попробуйте после загрузки изображения.');}
}
let lastContactId=null;
function openContact(){
  const ad=state.current;if(!ad)return;lastContactId=ad.id;const d=state.drafts.get(ad.id)||{};
  contact.innerHTML=`<div class="dialog-head"><div><h2 id="contact-title">Обсудить оформление</h2><p>Демонстрация обращения к Олесе</p></div><button class="icon-btn" data-close="contact" aria-label="Закрыть обращение">${icon('close')}</button></div><div class="dialog-body"><div class="chat-context"><img src="${ad.photo}" alt="" width="70" height="54"><div><strong>${esc(ad.title)}</strong><span>Стоимость по расчёту</span></div></div><form id="contact-form" novalidate><label class="field"><span>Как к вам обращаться</span><input name="name" autocomplete="given-name" maxlength="80" value="${esc(d.name||'')}" placeholder="Ваше имя" required></label><div class="form-grid"><label class="field"><span>Где нужно оформление</span><input name="place" maxlength="160" value="${esc(d.place||'')}" placeholder="Город, район или адрес" required></label><label class="field"><span>Желаемая дата</span><input name="date" type="date" value="${esc(d.date||'')}" required></label></div><label class="field"><span>Что хотите оформить</span><textarea name="task" maxlength="1800" placeholder="Нужные зоны, размеры, пожелания и бюджетный ориентир" required>${esc(d.task||'')}</textarea></label><label class="field"><span>Фото пространства <small style="display:inline;font-weight:400">по желанию</small></span><input name="photo" type="file" accept="image/*"><small>Фото останется на вашем устройстве. В демоверсии файл не отправляется.</small><span id="photo-file" class="photo-file"></span></label><p class="form-error" id="form-error" role="alert" hidden></p><button class="btn btn-blue" type="submit">Подготовить сообщение ${icon('arrow',18)}</button><p class="form-note">Это локальная демонстрация. Сообщение не отправляется, контактные данные не сохраняются после перезагрузки страницы.</p></form></div>`;
  contact.showModal();document.body.classList.add('modal-open');
}
function draftResult(data){
  const ad=ads.find(a=>a.id===lastContactId);const date=data.date.split('-').reverse().join('.');
  const message=`Здравствуйте! Меня зовут ${data.name}.\n\nИнтересует: ${ad.title.toLocaleLowerCase('ru')}.\nОбъект: ${data.place}.\nЖелаемая дата: ${date}.\n\nЗадача: ${data.task}${data.photo?'\n\nФото пространства выбрано на устройстве.':''}\n\nПодскажите подходящий состав и стоимость оформления.`;
  state.lastMessage=message;
  contact.querySelector('.dialog-body').innerHTML=`<h3 class="success-title">Обращение подготовлено</h3><p class="success-sub">Так будет выглядеть запрос по выбранному объявлению. В демонстрации он не отправлен.</p><div class="chat-message">${esc(message)}</div><div class="dialog-actions"><button class="btn btn-blue" data-action="copy-message">Скопировать текст</button><button class="btn btn-outline" data-action="edit-message">Изменить запрос</button></div>`;
  contact.querySelector('[data-action="copy-message"]').focus();
}
function notify(message){const node=document.querySelector('#toast');node.textContent=message;node.classList.add('visible');clearTimeout(state.toastTimer);state.toastTimer=setTimeout(()=>node.classList.remove('visible'),2800);}
async function copy(value){
  try{await navigator.clipboard.writeText(value);notify('Скопировано');}
  catch{const area=document.createElement('textarea');area.value=value;area.style.cssText='position:fixed;left:0;top:0;opacity:0';(contact.open?contact:document.body).append(area);area.select();const ok=document.execCommand('copy');area.remove();notify(ok?'Скопировано':'Выделите и скопируйте текст вручную');}
}
function save(id){
  if(state.saved.has(id))state.saved.delete(id);else state.saved.add(id);
  try{localStorage.setItem('decoriya-favorites',JSON.stringify([...state.saved]));}catch{}
  document.querySelectorAll(`[data-save="${id}"]`).forEach(b=>{b.setAttribute('aria-pressed',String(state.saved.has(id)));if(!b.classList.contains('save-button'))b.innerHTML=icon('heart',16)+(state.saved.has(id)?'Сохранено':'В избранное');});
  if(location.hash.startsWith('#showroom')&&state.onlySaved)updateResults();
}
function reset(){Object.assign(state,{category:'Все предложения',phase:'all',query:'',onlySaved:false});const search=document.querySelector('.search-form input');if(search)search.value='';updateResults();}
document.addEventListener('click',event=>{
  const button=event.target.closest('button,a');if(!button)return;
  if(button.matches('a[href="#main"]')){event.preventDefault();const main=document.querySelector('#main');main.setAttribute('tabindex','-1');main.focus();return;}
  if(button.matches('[data-save]')){save(button.dataset.save);return;}
  if(button.matches('[data-category]')){state.category=button.dataset.category;updateResults();return;}
  if(button.matches('[data-phase]')){state.phase=button.dataset.phase;updateResults();return;}
  if(button.matches('[data-slide]')){setSlide(Number(button.dataset.slide));return;}
  if(button.matches('[data-slide-step]')){setSlide(state.slide+Number(button.dataset.slideStep));return;}
  if(button.matches('[data-close]')){document.getElementById(button.dataset.close).close();return;}
  if(button.matches('[data-scroll]')){event.preventDefault();document.getElementById(button.dataset.scroll)?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});return;}
  if(button.matches('a[href^="#ad/"]')&&location.hash.startsWith('#showroom')){state.catalogScroll=scrollY;state.returnTo=location.hash;}
  const action=button.dataset.action;
  if(action==='reset')reset();
  if(action==='saved-filter'){state.onlySaved=!state.onlySaved;updateResults();}
  if(action==='favorites'){if(location.hash.startsWith('#showroom')){state.onlySaved=!state.onlySaved;updateResults();}else location.hash='#showroom?saved=1';}
  if(action==='lightbox')openLightbox();
  if(action==='download-slide')downloadSlide();
  if(action==='contact')openContact();
  if(action==='share')copy(location.href);
  if(action==='copy-message')copy(state.lastMessage);
  if(action==='edit-message'){contact.close();openContact();}
});
document.addEventListener('submit',event=>{
  if(event.target.id==='search-form'){event.preventDefault();state.query=new FormData(event.target).get('q').toString().trim();if(location.hash.startsWith('#showroom'))updateResults();else location.hash='#showroom?q='+encodeURIComponent(state.query);}
  if(event.target.id==='contact-form'){
    event.preventDefault();const form=event.target;const values=Object.fromEntries(new FormData(form));const fields=['name','place','date','task'];let first=null;
    for(const key of fields){const field=form.elements[key];const valid=field.value.trim().length>0&&(key!=='date'||field.validity.valid);field.setAttribute('aria-invalid',String(!valid));if(!valid&&!first)first=field;values[key]=field.value.trim();}
    if(first){const error=document.querySelector('#form-error');error.textContent='Заполните имя, место, дату и описание задачи.';error.hidden=false;first.focus();return;}
    values.photo=values.photo?.size?values.photo.name:'';state.drafts.set(state.current.id,values);draftResult(values);
  }
});
document.addEventListener('input',event=>{
  if(event.target.closest('#search-form')&&location.hash.startsWith('#showroom')){state.query=event.target.value;updateResults();}
  if(event.target.closest('#contact-form')){
    const form=document.querySelector('#contact-form');const data={};for(const key of ['name','place','date','task'])data[key]=form.elements[key].value;state.drafts.set(state.current.id,data);
    if(event.target.value.trim())event.target.removeAttribute('aria-invalid');
  }
});
document.addEventListener('change',event=>{
  if(event.target.id==='sort'){state.sort=event.target.value;updateResults();}
  if(event.target.name==='photo'){const file=event.target.files[0];document.querySelector('#photo-file').textContent=file?`Выбрано: ${file.name}`:'';}
});
for(const dialog of [lightbox,contact]){
  dialog.addEventListener('close',()=>{if(!lightbox.open&&!contact.open)document.body.classList.remove('modal-open');});
  dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
}
document.addEventListener('keydown',event=>{
  if(!state.current||contact.open||event.altKey||event.ctrlKey||event.metaKey||event.target.matches('input,textarea,select'))return;
  if((lightbox.open||event.target.closest('.gallery-stage,.thumbs'))&&['ArrowLeft','ArrowRight'].includes(event.key)){event.preventDefault();setSlide(state.slide+(event.key==='ArrowRight'?1:-1));}
});
function route(){
  if(lightbox.open)lightbox.close();if(contact.open)contact.close();
  const hash=location.hash||'#home';
  if(hash==='#home'||hash==='#')renderHome();
  else if(hash.startsWith('#showroom'))renderShowroom();
  else if(hash.startsWith('#ad/')){const ad=ads.find(a=>a.id===hash.slice(4));if(ad)renderAd(ad);else notFound();}
  else notFound();
  window.scrollTo({left:0,top:hash.startsWith('#showroom')?state.catalogScroll:0,behavior:'instant'});
}
function notFound(){document.body.classList.remove('has-mobile-cta');document.title='Предложение не найдено | ДЕКОРИЯ';app.innerHTML=`${demoBar()}<main class="container not-found" id="main"><h1>Такого предложения пока нет</h1><p>Вернитесь в витрину, чтобы выбрать доступное оформление.</p><a class="btn btn-green" href="#showroom">Открыть витрину ${icon('arrow')}</a></main>${footer()}`;}
window.addEventListener('hashchange',route);
document.addEventListener('error',event=>{if(event.target.tagName==='IMG'){event.target.alt='Изображение не загрузилось. Обновите страницу.';}},true);
route();
