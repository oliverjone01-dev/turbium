(() => {
const $ = (s, r=document) => r.querySelector(s);
const lead = window.dekoriyaLead;
if (!$("#quiz") || !$("#season") || !lead) return;
const assets = new URL("assets/v10/panel/", document.currentScript.src);
const NS = "http://www.w3.org/2000/svg";
const sysCalm = matchMedia("(prefers-reduced-motion: reduce)");
const calm = () => sysCalm.matches;
const wait = ms => new Promise(r => setTimeout(r, calm() ? 0 : ms));
const el = (tag, attrs={}, parent) => { const n = document.createElementNS(NS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };
const arrow = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" stroke="currentColor" stroke-width="1.6"/></svg>';

/* ---------- data from the Figma mock ---------- */
const STEPS = [
  { q:"Какой у вас объект?", hint:"Выберите один вариант", type:"photo",
    opts:[["Кафе и ресторан","s1-cafe"],["Салон и услуги","s1-salon"],["Бутик и шоурум","s1-boutique",1],["Офис, отель, ТЦ","s1-office",1]],
    extra:"Другое — опишу в конце",
    tip:"В кафе и салоне вход первым встречает гостей. С него удобно начать подбор." },
  { q:"Что хотите оформить?", hint:"Можно выбрать несколько вариантов", type:"photo", multi:true,
    opts:[["Вход","s2-entry"],["Витрина","s2-window"],["Зал","s2-hall"],["Несколько зон","s2-multi"]],
    extra:"Пока не знаю — нужен совет",
    tip:"Если зон несколько, общая палитра свяжет вход, витрину и зал." },
  { q:"Какое настроение ближе?", hint:"Концепты направлений: в эскизе их можно смешать", type:"photo",
    opts:[["Тёплая классика","s3-warm"],["Лёд и серебро","s3-ice"],["Русский орнамент","s3-russian"],["Мягкая пастель","s3-pastel"]],
    extra:"Не знаю — подберите за меня",
    tip:"Если сомневаетесь, выберите «Подберите за меня». Фото поможет учесть цвет фасада и вывеску." },
  { q:"Когда нужен монтаж?", hint:"Выберите один вариант", type:"pills",
    opts:["До 1 декабря","1–15 декабря","16–25 декабря","Пока не знаю"],
    tip:"Назовите желаемую дату сразу: по ней согласуем доступность монтажа." },
  { q:"Покажите ваш объект", hint:"Необязательно, но так эскиз получится точнее", type:"upload", optional:true,
    extra:"Пришлю позже",
    tip:"Фото фасада днём и примерная ширина двери — этого хватит для эскиза." },
  { q:"Как с вами связаться?", hint:"Оставьте телефон, чтобы обсудить ваш объект и эскиз.", type:"contacts",
    tip:"Укажите телефон, по которому удобно обсудить ваш объект." }
];
const PCT = [0,20,40,60,80,90];
const answers = STEPS.map(() => new Set());
let step = 0, busy = false, submitted = false;
let photos = [];
let contactDraft = {name:"", phone:"", context:"", consent:false};

/* ---------- garland (quiz progress) ---------- */
const g = $("#garland");
let G = null;
function buildGarland(){
  const mobile = g.parentElement.clientWidth < 620;
  const cfg = mobile ? {W:310,H:64,d:16,cap:[6,4],th:[12,24,16,28,18]} : {W:792,H:96,d:24,cap:[8,5],th:[20,38,26,44,30]};
  g.innerHTML = ""; g.setAttribute("viewBox", `0 0 ${cfg.W} ${cfg.H}`);
  const defs = el("defs", {}, g); const f = el("filter", {id:"blur", x:"-1", y:"-1", width:"3", height:"3"}, defs); el("feGaussianBlur", {stdDeviation: mobile?4:6}, f);
  el("line", {class:"rail", x1:0, y1:4, x2:cfg.W, y2:4}, g);
  const fill = el("line", {class:"rail-fill", x1:0, y1:4, x2:cfg.W, y2:4}, g);
  const xs = [0,1,2,3,4].map(i => cfg.W/5*i + cfg.W/10);
  const bs = xs.map((x,i) => {
    const b = el("g", {class:"b next"}, g);
    const s = el("g", {class:"swing", style:`transform-origin:${x}px 4px`}, b);
    const th = cfg.th[i], d = cfg.d, cy = 4 + th + cfg.cap[1] + d/2;
    el("line", {class:"thread", x1:x, y1:4, x2:x, y2:4+th}, s);
    el("rect", {class:"cap", x:x-cfg.cap[0]/2, y:4+th, width:cfg.cap[0], height:cfg.cap[1], rx:1.5}, s);
    el("circle", {class:"glow", cx:x, cy, r:d/2+2, filter:"url(#blur)"}, s);
    el("circle", {class:"halo", cx:x, cy, r:d/2+6}, s);
    el("circle", {class:"sphere", cx:x, cy, r:d/2}, s);
    el("ellipse", {class:"hl", cx:x-d*0.18, cy:cy-d*0.2, rx:d*0.16, ry:d*0.11, transform:`rotate(-25 ${x-d*0.18} ${cy-d*0.2})`}, s);
    return b;
  });
  G = {cfg, xs, fill, bs};
  paintGarland(submitted || step === 5 ? 6 : step, false);
}
function paintGarland(k, swing){
  const {xs, fill, bs, cfg} = G; const all = k >= 6;
  fill.style.transform = `scaleX(${all ? 1 : xs[Math.min(k,4)]/cfg.W})`;
  bs.forEach((b,i) => {
    b.classList.remove("done","current","next");
    b.classList.add(all || i < k ? "done" : i === k ? "current" : "next");
    if (swing && i === k && !all){ const s = b.firstChild; s.classList.remove("go"); void s.getBBox(); s.classList.add("go"); }
  });
}
let lastMode = null;
addEventListener("resize", () => { const m = g.parentElement.clientWidth < 620; if (m !== lastMode){ lastMode = m; buildGarland(); } });

/* ---------- percent tween ---------- */
let pctNow = 0, pctAnimation = 0;
function setPct(to){
  cancelAnimationFrame(pctAnimation);
  const from = pctNow; pctNow = to; const t0 = performance.now(), dur = calm() ? 0 : 500;
  const tick = t => { const p = dur ? Math.min(1,(t-t0)/dur) : 1; $("#pct").textContent = `Подбор: ${Math.round(from+(to-from)*p)}%`; if (p<1) pctAnimation = requestAnimationFrame(tick); };
  pctAnimation = requestAnimationFrame(tick);
}

/* ---------- Olesya tip ---------- */
let tipVersion = 0;
async function setTip(text){
  const tip = $("#tip"); const ava = $("#ava");
  const version = ++tipVersion;
  ava.classList.remove("hop"); void ava.offsetWidth; ava.classList.add("hop");
  if (!calm()){ tip.innerHTML = '<span class="typing" aria-hidden="true"><i></i><i></i><i></i></span>'; await wait(500); }
  if (version !== tipVersion) return;
  tip.innerHTML = `<p style="opacity:0">${text}</p>`; requestAnimationFrame(() => { const p = tip.firstChild; if (p) p.style.opacity = 1; });
}

/* ---------- pane renderers ---------- */
function optButton(label, img, pressed, concept){
  return `<button type="button" class="opt" aria-pressed="${pressed}" data-v="${label}"><span class="ph">${concept ? '<span class="concept-tag">концепт</span>' : ""}<img src="${assets}${img}-400.webp" srcset="${assets}${img}-400.webp 400w, ${assets}${img}.webp 800w" sizes="(max-width: 820px) 42vw, (max-width: 1100px) 22vw, 210px" width="400" height="322" loading="lazy" decoding="async" alt=""></span><span class="lb"><span class="radio"></span>${label}</span></button>`;
}
function pill(label, pressed){ return `<button type="button" class="pill" aria-pressed="${pressed}" data-v="${label}"><span class="dot"></span>${label}</button>`; }
function navHTML(k){
  const last = k === 5;
  return `<div class="nav"><button type="button" class="back" ${k===0?"disabled":""}>Назад</button>
    <div class="right"><span class="hint">${last ? "Ответим по телефону" : "Выберите вариант и нажмите «Далее»"}</span>
    <button type="${last?'submit':'button'}" ${last?'form="quiz-contact"':''} class="btn next" aria-disabled="true">${last ? "Получить эскиз бесплатно" : "Далее"} ${arrow}</button></div></div>`;
}
function paneHTML(k){
  const s = STEPS[k], a = answers[k];
  let body = "";
  if (s.type === "photo") body = `<div class="opts" role="group" aria-labelledby="quiz-question">${s.opts.map(([l,i,c]) => optButton(l,i,a.has(l),c)).join("")}</div>`;
  if (s.type === "pills") body = `<div class="pills" role="group" aria-labelledby="quiz-question">${s.opts.map(l => pill(l,a.has(l))).join("")}</div>`;
  if (s.type === "upload") body = `<label class="upload"><input type="file" id="files" accept="image/jpeg,image/png,image/webp" multiple aria-describedby="photo-status"><b>Добавить фото объекта</b><span>До 5 файлов JPEG, PNG или WebP, до 10 МБ каждый. Без людей и документов в кадре.</span></label>
    <p class="step-error" id="photo-status" role="status"></p><div class="files" id="filelist"></div>`;
  if (s.type === "contacts") body = `<form class="form" id="quiz-contact" novalidate data-lead-form="quiz">
      <div class="field"><label for="quiz-name">Ваше имя *</label><input id="quiz-name" name="name" required maxlength="80" autocomplete="name" placeholder="Как к вам обращаться" aria-describedby="quiz-name-error"><small id="quiz-name-error" data-error="name" hidden></small></div>
      <div class="field"><label for="quiz-phone">Телефон *</label><input id="quiz-phone" name="phone" required type="tel" maxlength="26" autocomplete="tel" placeholder="+7 (___) ___-__-__" aria-describedby="quiz-phone-error"><small id="quiz-phone-error" data-error="phone" hidden></small></div>
      <div class="field quiz-context"><label for="quiz-context">Об объекте (по желанию)</label><textarea id="quiz-context" name="context" rows="2" maxlength="1000" placeholder="Адрес, размеры или другие детали"></textarea></div>
      <div class="lead-trap" aria-hidden="true"><label>Оставьте пустым <input name="website" tabindex="-1" autocomplete="off"></label></div>
      ${lead.consentMarkup('quiz')}
      <p class="quiz-status" data-unavailable>Приём заявок через сайт пока закрыт. <a href="tel:+79772666460">Позвонить Олесе</a></p>
      <p class="quiz-status" data-lead-status role="status" aria-live="polite"></p>
    </form>`;
  const extra = s.extra ? `<div class="pills">${pill(s.extra, a.has(s.extra))}</div>` : "";
  return `<div class="pane"><div class="q"><h3 id="quiz-question" tabindex="-1">${s.q}</h3><p>${s.hint}</p></div>${body}${extra}${navHTML(k)}</div>`;
}
function answered(k){ const s = STEPS[k]; if (s.optional) return true; if (s.type === "contacts") return lead.available; return answers[k].size > 0; }
function syncNext(pane, k, shine){
  const btn = pane.querySelector(".next"); const ok = answered(k);
  const was = btn.getAttribute("aria-disabled") === "true";
  btn.setAttribute("aria-disabled", String(!ok));
  if (ok && was && shine && !calm()){ btn.classList.remove("shine"); void btn.offsetWidth; btn.classList.add("shine"); }
}
function bind(pane, k){
  const s = STEPS[k];
  const next = pane.querySelector(".next");
  const back = pane.querySelector(".back");
  const form = pane.querySelector("#quiz-contact");
  function saveContact() {
    if (!form) return;
    contactDraft = Object.fromEntries(["name","phone","context"].map(name => [name,form.elements[name].value]));
    contactDraft.consent = form.elements.consent.checked;
  }
  pane.addEventListener("click", e => {
    if (busy) return;
    const button = e.target.closest(".opt,.pill");
    if (!button) return;
    const value = button.dataset.v, set = answers[k];
    if (s.multi && value !== s.extra) {
      set.delete(s.extra);
      set.has(value) ? set.delete(value) : set.add(value);
    } else {
      const selected = set.has(value);
      set.clear();
      if (!selected) set.add(value);
    }
    if (s.type === "upload" && set.has(s.extra)) {
      photos = [];
      pane.querySelector("#files").value = "";
      pane.querySelector("#photo-status").textContent = "";
      renderFiles(pane);
    }
    pane.querySelectorAll(".opt,.pill").forEach(button => button.setAttribute("aria-pressed", String(set.has(button.dataset.v))));
    syncNext(pane, k, true);
  });
  back.addEventListener("click", () => {
    if (busy || step===0) return;
    saveContact();
    go(step-1, true);
  });
  if (form) {
    lead.wire(form);
    for (const key of ["name","phone","context"]) form.elements[key].value = contactDraft[key];
    form.elements.consent.checked = contactDraft.consent;
    next.disabled = !lead.available;
    form.addEventListener("submit", e => {
      e.preventDefault();
      if (!busy && lead.available) submit(pane, form);
    });
  } else {
    next.addEventListener("click", () => {
      if (next.getAttribute("aria-disabled") === "true" || busy) return;
      go(k+1, false);
    });
  }
  const files = pane.querySelector("#files");
  if (files) {
    renderFiles(pane);
    files.addEventListener("change", () => {
      const nextFiles = [...files.files];
      const top = pane.querySelector("#photo-status");
      if (nextFiles.length > 5 || nextFiles.some(f => f.size <= 0 || f.size > 10*1024*1024 || !["image/jpeg","image/png","image/webp"].includes(f.type))) {
        top.textContent = "Выберите не больше 5 изображений JPEG, PNG или WebP, каждое до 10 МБ.";
        files.value = "";
        return;
      }
      photos = nextFiles;
      answers[k].delete(s.extra);
      pane.querySelector(".pill").setAttribute("aria-pressed","false");
      top.textContent = "";
      renderFiles(pane);
    });
  }
  syncNext(pane, k, false);
}
function renderFiles(pane) {
  const list = pane.querySelector("#filelist");
  list.replaceChildren();
  photos.forEach((photo, index) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.textContent = photo.name + " ×";
    chip.setAttribute("aria-label","Убрать фото " + photo.name);
    chip.addEventListener("click", () => {
      photos.splice(index,1);
      pane.querySelector("#files").value = "";
      renderFiles(pane);
      (list.children[Math.min(index,list.children.length-1)] || pane.querySelector("#files")).focus();
    });
    list.append(chip);
  });
}
/* ---------- step transition ---------- */
const stage = $("#stage");
const quizCard = $("#quiz .card");
const guidance = $("#quiz .aside");
const compactGuidance = matchMedia("(max-width:820px)");
function layoutGuidance() {
  const pane = stage.firstElementChild;
  const nav = pane?.querySelector(".nav");
  if (compactGuidance.matches && nav) pane.insertBefore(guidance, nav);
  else if (guidance.parentElement !== quizCard) quizCard.append(guidance);
}
compactGuidance.addEventListener("change", layoutGuidance);
async function go(k, back){
  if (busy) return; busy = true;
  const old = stage.firstElementChild; const h0 = stage.offsetHeight;
  if (old && !calm()){ old.classList.add("out"); if (back) old.classList.add("back"); await wait(200); }
  stage.innerHTML = paneHTML(k); const pane = stage.firstElementChild; layoutGuidance(); bind(pane, k);
  pane.querySelector("h3").focus({preventScroll:true});
  if (!calm()){ pane.classList.add("in"); if (back) pane.classList.add("back"); }
  const h1 = pane.offsetHeight;
  if (old && !calm()){ stage.style.height = h0+"px"; void stage.offsetHeight; stage.style.height = h1+"px"; setTimeout(() => stage.style.height = "", 320); }
  const prev = step; step = k;
  $("#qnum").textContent = k === 5 ? "Почти готово" : `Вопрос ${k+1} из 5`;
  setPct(PCT[k]);
  const kIdx = k === 5 ? 6 : k;
  if (!back && k > prev){
    // old ball turns gold at once, the rail grows to the next thread, then the next ball becomes current and swings
    if (G.bs[prev]) G.bs[prev].classList.replace("current","done");
    G.fill.style.transform = `scaleX(${kIdx >= 6 ? 1 : G.xs[k]/G.cfg.W})`;
    await wait(550);
  }
  paintGarland(kIdx, !back && !calm());
  setTip(STEPS[k].tip);
  busy = false;
}
async function submit(pane, form){
  if (!lead.validate(form,true)) return;
  busy = true;
  const button = pane.querySelector(".next");
  const back = pane.querySelector(".back");
  const message = form.querySelector("[data-lead-status]");
  button.disabled = true;
  back.disabled = true;
  form.setAttribute("aria-busy","true");
  message.textContent = "Отправляем заявку…";
  const selection = i => [...answers[i]][0];
  try {
    await lead.submit(form, {
      source:"quiz_v10",
      object:selection(0),
      zones:[...answers[1]],
      mood:selection(2),
      install_window:selection(3),
      photos_later:answers[4].has(STEPS[4].extra),
      channel:"call",
      context:{details:form.elements.context.value.trim()}
    }, photos);
    submitted = true;
    setPct(100);
    $("#qnum").textContent = "Подбор завершён";
    paintGarland(6,false);
    if (!calm()){
      G.bs.forEach((ball,i) => setTimeout(() => ball.querySelector(".glow").classList.add("flash-once"),i*80));
      await wait(700);
    }
    stage.innerHTML = `<div class="pane done-pane"><h3 tabindex="-1">Спасибо! Заявка получена.</h3><p>Свяжемся по указанному телефону, чтобы обсудить ваш объект и эскиз.</p><button type="button" class="btn" id="again">Пройти ещё раз ${arrow}</button></div>`;
    layoutGuidance();
    stage.querySelector("h3").focus({preventScroll:true});
    photos = [];
    contactDraft = {name:"",phone:"",context:"",consent:false};
    $("#again").addEventListener("click", () => {
      answers.forEach(set => set.clear());
      submitted = false;
      go(0, true);
    });
  } catch {
    message.textContent = lead.tryAgain;
    button.textContent = "Повторить отправку";
    form.removeAttribute("aria-busy");
    button.disabled = false;
    back.disabled = false;
  } finally {
    busy = false;
  }
}

/* ---------- SEASON timeline ---------- */
const tl = $("#tl"), season = $("#season"), ms = $("#ms");
const TW = 1312, col = TW/5, cx = [0,1,2,3,4].map(i => col*i + col/2), TH = [26,48,34,56,40], D = 30;
const tdefs = el("defs", {}, tl); const tf = el("filter", {id:"tblur", x:"-1", y:"-1", width:"3", height:"3"}, tdefs); el("feGaussianBlur", {stdDeviation:8}, tf);
el("line", {class:"rail", x1:0, y1:8, x2:TW, y2:8}, tl);
el("line", {class:"fill", x1:0, y1:8, x2:cx[3], y2:8}, tl);
const tbs = cx.map((x,i) => {
  const b = el("g", {class:"tb" + (i===4 ? " jan" : "")}, tl);
  const par = el("g", {class:"par"}, b);
  const sw = el("g", {class:"swing", style:`transform-origin:${x}px 8px`}, par);
  el("line", {class:"thread", x1:x, y1:8, x2:x, y2:8+TH[i]}, sw);
  const drop = el("g", {class:"drop"}, sw);
  const cy = 8 + TH[i] + 6 + D/2;
  el("rect", {class:"cap", x:x-5, y:8+TH[i], width:10, height:6, rx:2}, drop);
  el("circle", {class:"glow", cx:x, cy, r:D/2+3, filter:"url(#tblur)"}, drop);
  el("circle", {class:"sphere", cx:x, cy, r:D/2}, drop);
  el("ellipse", {class:"hl", cx:x-D*0.18, cy:cy-D*0.2, rx:D*0.16, ry:D*0.11, transform:`rotate(-25 ${x-D*0.18} ${cy-D*0.2})`}, drop);
  return {b, par, sw, x};
});
const items = [...ms.querySelectorAll(".m")];
function lightAll(){ tbs.slice(0,4).forEach(t => t.b.classList.add("lit")); }
let timers = [];
function playSeason(){
  if (matchMedia("(max-width:820px)").matches) return;
  timers.forEach(clearTimeout); timers = [];
  season.classList.add("pre"); tbs.forEach(t => t.b.classList.remove("lit","flicker"));
  if (calm()){ season.classList.remove("pre"); lightAll(); return; }
  void season.offsetWidth;
  setTimeout(() => {
    season.classList.remove("pre");
    tbs.forEach((t,i) => {
      t.b.querySelector(".thread").style.transitionDelay = `${i*150}ms`;
      t.b.querySelector(".drop").style.transitionDelay = `${i*150+150}ms`;
      timers.push(setTimeout(() => { t.sw.classList.remove("go"); void t.sw.getBBox(); t.sw.classList.add("go"); }, i*150+250));
      if (i < 4) timers.push(setTimeout(() => t.b.classList.add("lit"), 200 + 1200 * (t.x / cx[3])));
    });
    items.forEach((m,i) => { const p = m.querySelector(".photo"); p.style.transitionDelay = `${300 + i*120}ms`; });
    timers.push(setTimeout(() => tbs[4].b.classList.add("flicker"), 200 + 1200 + 400));
  }, 40);
}
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting){ playSeason(); io.disconnect(); } }), {threshold:0.4});
const below = season.getBoundingClientRect().top > innerHeight;
if (below && !calm()){ io.observe(season); } else lightAll();


// parallax: baubles follow the cursor (±4px), desktop pointer only
const fine = matchMedia("(hover:hover) and (pointer:fine)");
let tx = 0, ty = 0, px = 0, py = 0, raf = 0;
season.addEventListener("pointermove", e => {
  if (!fine.matches || calm()) return;
  const r = season.getBoundingClientRect(); tx = ((e.clientX - r.left)/r.width - .5) * 8; ty = ((e.clientY - r.top)/r.height - .5) * 6;
  if (!raf) raf = requestAnimationFrame(loop);
});
season.addEventListener("pointerleave", () => { tx = 0; ty = 0; });
function loop(){
  px += (tx - px) * .08; py += (ty - py) * .08;
  tbs.forEach((t,i) => t.par.setAttribute("transform", `translate(${(px*(0.6+i*0.1)).toFixed(2)} ${(py*0.5).toFixed(2)})`));
  raf = (Math.abs(tx-px) + Math.abs(ty-py) > .02) ? requestAnimationFrame(loop) : 0;
}
// hover a milestone: its bauble sways
items.forEach((m,i) => m.addEventListener("mouseenter", () => { if (calm() || !fine.matches) return; const s = tbs[i].sw; s.classList.remove("go"); void s.getBBox(); s.classList.add("go"); }));

// mobile: scroll-linked vertical rail + lighting at screen center
const vfill = $("#vfill");
function onScroll(){
  if (!matchMedia("(max-width:820px)").matches) return;
  const r = ms.getBoundingClientRect(); const mid = innerHeight/2;
  const p = Math.max(0, Math.min(1, (mid - r.top) / r.height));
  ms.style.setProperty("--p", calm() ? 1 : p.toFixed(3));
  items.forEach((m,i) => { const mr = m.getBoundingClientRect(); m.classList.toggle("lit", i < 4 && (calm() || mr.top < mid)); });
}
let scrollFrame = 0;
function queueScroll(){
  if (!scrollFrame) scrollFrame = requestAnimationFrame(() => { scrollFrame = 0; onScroll(); });
}
addEventListener("scroll", queueScroll, {passive:true});
addEventListener("resize", queueScroll);
sysCalm.addEventListener("change", () => { if (calm()) lightAll(); queueScroll(); });
onScroll();

/* ---------- start ---------- */
lastMode = g.parentElement.clientWidth < 620;
buildGarland();
stage.innerHTML = paneHTML(0); layoutGuidance(); bind(stage.firstElementChild, 0);
$("#tip").innerHTML = `<p>${STEPS[0].tip}</p>`;
paintGarland(0, false);
const styleButtons = [...document.querySelectorAll("[data-style-pick]")];
const styleFeatures = [...document.querySelectorAll("[data-style-feature]")];
styleButtons.forEach(button => button.addEventListener("click", () => {
  const style = button.dataset.stylePick;
  styleButtons.forEach(item => item.setAttribute("aria-pressed", String(item.dataset.stylePick === style)));
  styleFeatures.forEach(panel => { panel.hidden = panel.dataset.styleFeature !== style; });
}));
document.querySelectorAll("[data-quiz-mood]").forEach(link => link.addEventListener("click", () => {
  const mood = link.dataset.quizMood;
  if (!STEPS[2].opts.some(choice => choice[0] === mood) || submitted || busy) return;
  answers[2].clear();
  answers[2].add(mood);
  if (step === 2) {
    stage.querySelectorAll(".opt,.pill").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.v === mood)));
    syncNext(stage.firstElementChild, step, false);
  }
}));
})();
