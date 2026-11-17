// Deploy on the host that holds the existing bot credentials.
// TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are server-side secrets.
export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin');
    const allowed = env.LEAD_ORIGIN || 'https://oliverjone01-dev.github.io';
    const headers = {'Content-Type':'application/json','Cache-Control':'no-store','Vary':'Origin'};
    if(origin===allowed) Object.assign(headers, {'Access-Control-Allow-Origin':allowed,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'});
    const reply=(status,ok)=>new Response(JSON.stringify({ok}),{status,headers});
    if(origin!==allowed)return reply(403,false);
    if(request.method==='OPTIONS')return new Response(null,{status:204,headers});
    if(request.method!=='POST')return reply(405,false);
    if(!env.TELEGRAM_BOT_TOKEN||!env.TELEGRAM_CHAT_ID)return reply(503,false);
    if(!request.headers.get('Content-Type')?.toLowerCase().startsWith('application/json'))return reply(415,false);
    let lead;
    try{const raw=await request.text();if(raw.length>7000)return reply(413,false);lead=JSON.parse(raw);}catch{return reply(400,false);}
    if(!lead||typeof lead!=='object'||lead.website||lead.consent!=='on')return reply(400,false);
    const clean=(key,length)=> typeof lead[key]==='string'?lead[key].trim().slice(0,length):'';
    const name=clean('name',80), contact=clean('contact',150);
    if(!name||(!/^@[a-z0-9_]{5,32}$/i.test(contact)&&!/[0-9]{10,}/.test(contact.replace(/[^0-9]/g,''))))return reply(422,false);
    const pairs=[['Имя',name],['Телефон / Telegram',contact],['Что оформить',clean('object',1000)],['Выбранный пример',clean('example',170)],['Тип объекта',clean('business',170)],['Зона',clean('zone',170)]];
    const text=['ДЕКОРИЯ · новая заявка',...pairs.filter(([,value])=>value).map(([label,value])=>label+': '+value)].join('\n');
    try {
      const telegram=await fetch('https://api.telegram.org/bot'+env.TELEGRAM_BOT_TOKEN+'/sendMessage',{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_id:env.TELEGRAM_CHAT_ID,text}),
        signal:AbortSignal.timeout(8500)
      });
      const result=await telegram.json();
      return result.ok===true&&telegram.ok?reply(200,true):reply(502,false);
    } catch {return reply(502,false);}
  }
};
