(() => {
  'use strict';

  const config = document.querySelector('#lead-settings');
  if (!config) return;
  const endpoint = config.dataset.endpoint;
  const policy = new URL(config.dataset.policy, location.href);
  const consent = new URL(config.dataset.consent, location.href);
  const unavailable = 'Приём заявок через сайт пока закрыт.';
  const tryAgain = 'Не удалось подтвердить отправку. Поля сохранены. Попробуйте ещё раз.';

  function phoneNumber(input) {
    const digits = input.trim().replace(/[^\d]/g, '');
    if (digits.length === 10) return '+7' + digits;
    if (/^[78]\d{10}$/.test(digits)) return '+7' + digits.slice(1);
    return '';
  }

  function consentMarkup(prefix) {
    return `<div class="lead-agreement"><label class="lead-consent"><input type="checkbox" name="consent" required aria-describedby="${prefix}-consent-error"><span>Я даю согласие на обработку персональных данных</span></label>
      <div class="lead-doc-links"><a data-lead-doc="consent" target="_blank" rel="noopener">Текст согласия</a><a data-lead-doc="policy" target="_blank" rel="noopener">Политика обработки данных</a></div>
      <p id="${prefix}-consent-error" data-error="consent" hidden></p></div>`;
  }

  function setError(form, field, message) {
    const input = form.elements[field];
    input.setAttribute('aria-invalid', String(Boolean(message)));
    const description = form.querySelector('[data-error="' + field + '"]');
    if (!description) return;
    description.textContent = message;
    description.hidden = !message;
  }

  function validate(form, nameRequired) {
    const { name, phone, consent: agreement } = form.elements;
    const errors = {
      name: nameRequired && !name.value.trim() ? 'Как к вам обращаться? Напишите имя.' : '',
      phone: !phone.value.trim() ? 'Укажите номер телефона.' : !phoneNumber(phone.value) ? 'Нужен номер из 10 цифр после +7.' : '',
      consent: agreement.checked ? '' : 'Отметьте согласие, чтобы отправить заявку.'
    };
    Object.entries(errors).forEach(([key, message]) => setError(form, key, message));
    const first = Object.keys(errors).find(key => errors[key]);
    if (first) form.elements[first].focus();
    return !first;
  }

  function wire(form) {
    form.querySelectorAll('[data-lead-doc]').forEach(a => {
      a.href = a.dataset.leadDoc === 'policy' ? policy : consent;
    });
    form.querySelectorAll('[data-unavailable]').forEach(p => {
      p.hidden = Boolean(endpoint);
    });
    for (const name of ['name', 'phone', 'consent']) {
      const input = form.elements[name];
      if (!input) continue;
      input.addEventListener('input', () => setError(form, name, ''));
    }
    form.elements.phone?.addEventListener('blur', event => {
      const input = event.currentTarget;
      const normalized = phoneNumber(input.value);
      if (normalized) {
        input.value = normalized.replace(/^(\+7)(\d{3})(\d{3})(\d{2})(\d{2})$/, '$1 ($2) $3-$4-$5');
        setError(form, 'phone', '');
      } else if (input.value.trim()) setError(form, 'phone', 'Нужен номер из 10 цифр после +7.');
    });
    if (form.dataset.leadForm === 'project') form.querySelector('[type=submit]').disabled = !endpoint;
  }

  const submissions = new Map();
  async function submit(form, details, files = []) {
    if (!endpoint) throw new Error(unavailable);
    const { name, phone, website } = form.elements;
    const payload = {
      ...details,
      name: name.value.trim(),
      phone: phoneNumber(phone.value),
      consent: { given:true, version:config.dataset.consentVersion },
      honeypot:website.value,
      tracking:Object.fromEntries(['utm_source','utm_medium','utm_campaign','utm_content','utm_term']
        .map(key => [key,new URLSearchParams(location.search).get(key)])
        .filter(([,value]) => value && value.length <= 120))
    };
    const fingerprint = JSON.stringify([payload, files.map(f => [f.name, f.size, f.lastModified])]);
    const previous = submissions.get(details.source);
    const id = previous?.fingerprint === fingerprint ? previous.id : crypto.randomUUID();
    submissions.set(details.source, {fingerprint, id});
    const body = new FormData();
    body.set('lead', JSON.stringify({...payload, id}));
    files.forEach(file => body.append('photos', file, file.name));
    const res = await fetch(endpoint, {method:'POST', body, credentials:'omit', signal:AbortSignal.timeout(30000)});
    const receipt = await res.json();
    if (!res.ok || receipt.ok !== true || receipt.id !== id) throw new Error(tryAgain);
    submissions.delete(details.source);
    return receipt;
  }

  const project = document.querySelector('#brief-form');
  if (project) {
    const button = project.querySelector('button[type=submit]');
    const label = button.innerHTML;
    const message = project.querySelector('[data-lead-status]');
    wire(project);
    project.addEventListener('submit', async event => {
      event.preventDefault();
      if (!endpoint || button.disabled || !validate(project,false)) return;
      button.disabled = true;
      project.setAttribute('aria-busy','true');
      message.textContent = 'Отправляем заявку…';
      try {
        const data = new FormData(project);
        const context = Object.fromEntries(['business','zone','occasion','style','format','date'].map(key => [key,data.get(key)]));
        context.example = document.querySelector('#chosen-case')?.dataset.caseId || '';
        await submit(project, {source:'project_v10', object:data.get('object').trim(), context, channel:'call'});
        project.reset();
        project.dispatchEvent(new CustomEvent('dekoriya:project-received',{bubbles:true}));
        message.textContent = 'Спасибо! Заявка получена. Свяжемся с вами по указанному телефону.';
        button.innerHTML = label;
      } catch {
        message.textContent = tryAgain;
        button.textContent = 'Повторить отправку';
      } finally {
        button.disabled = false;
        project.removeAttribute('aria-busy');
      }
    });
  }

  window.dekoriyaLead = {available:Boolean(endpoint), unavailable, tryAgain, consentMarkup, wire, validate, submit};
})();
