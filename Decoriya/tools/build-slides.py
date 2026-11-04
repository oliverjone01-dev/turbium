"""Compose editable 1600x1200 SVG layouts from the project's photograph assets."""
from pathlib import Path
from html import escape
import base64
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
GREEN, INK, PAPER, BURGUNDY = '#183b32', '#181b1e', '#f5f5f2', '#57212f'
FONT = ImageFont.truetype(str(ASSETS / 'manrope-600.ttf'), 64)

def uri(path, kind):
    return f'data:{kind};base64,' + base64.b64encode(path.read_bytes()).decode()

FONTS = ''.join(f"@font-face{{font-family:Manrope;font-weight:{w};src:url({uri(ASSETS / f'manrope-{w}.ttf', 'font/ttf')})}}" for w in [400,600])
LOGO = uri(ASSETS / 'logo.svg', 'image/svg+xml')

def text(x, y, value, size=48, width=1400, fill=INK, weight=600, leading=None):
    font = ImageFont.truetype(str(ASSETS / f'manrope-{weight}.ttf'), size)
    lines=[]
    for para in value.split('\n'):
        line=''
        for word in para.split():
            test=(line+' '+word).strip()
            if font.getlength(test)>width and line:
                lines.append(line);line=word
            else:line=test
        lines.append(line)
    lh=leading or round(size*1.24)
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="Manrope, sans-serif" font-size="{size}" font-weight="{weight}">' + ''.join(f'<tspan x="{x}" dy="{0 if i==0 else lh}">{escape(line)}</tspan>' for i,line in enumerate(lines)) + '</text>'

def rect(x,y,w,h,fill):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'
def photo(name,x,y,w,h):return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="{uri(ASSETS / "photos" / (name+".webp"),"image/webp")}"/>'
def header(title,dark=False):
    return rect(0,0,1600,236,GREEN if dark else '#fff')+text(56,94,title,72,1190,'#fff' if dark else INK)+f'<image x="1320" y="46" width="224" height="52" href="{LOGO}"'+(' style="filter:brightness(0) invert(1)"' if dark else '')+'/>'
def frame(body):return '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200"><defs><style>'+FONTS+'</style></defs>'+rect(0,0,1600,1200,'#fff')+body+'<rect x="1" y="1" width="1598" height="1198" fill="none" stroke="#d6d9d5" stroke-width="2"/></svg>'

SERIES={
 'rus':{'title':'Новый год\nв русском стиле','caption':'Роспись, хвоя и бархат\nв характере вашего пространства', 'features':[('Орнамент','Под архитектуру'),('Палитра','Красный и золотой'),('Состав','По вашему объекту')], 'parts':[('Хвойное обрамление','Вход или выбранная зона'),('Русские мотивы','Роспись, фигуры, орнамент'),('Свет и текстиль','Согласованная палитра')], 'details':['Роспись и орнамент','Глубокий цвет бархата','Тёплые огни'], 'cta':'Пришлите фото объекта,\nадрес и желаемую дату', 'sub':'Обсудим русские мотивы и состав оформления'},
 'ice':{'title':'Витрина\nв ледяном серебре','caption':'Прозрачные акценты,\nсиний и серебро', 'features':[('Товар','Остаётся виден'),('Палитра','Синий и серебро'),('Свет','Под вашу витрину')], 'parts':[('Обрамление','Хвоя по краям витрины'),('Прозрачные акценты','Подвесы и гранёные детали'),('Цвет и свет','Под коллекцию магазина')], 'details':['Прозрачные подвесы','Серебряные украшения','Открытый обзор товара'], 'cta':'Пришлите фото витрины,\nразмеры и адрес', 'sub':'Состав и дату согласуем по вашему объекту'},
 'pastel':{'title':'Ёлка и интерьер\nв пастельной палитре','caption':'Розовый, мятный и жемчужный\nс мягким тёплым светом', 'features':[('Ёлка','Под пространство'),('Палитра','Нежные оттенки'),('Детали','Ленты и украшения')], 'parts':[('Ёлка','Высота по вашему интерьеру'),('Украшения','Розовый, мятный, жемчужный'),('Дополнения','Подарки и фигуры по смете')], 'details':['Мягкий цвет лент','Матовые украшения','Тёплые огни'], 'cta':'Пришлите фото комнаты,\nвысоту ёлки и дату', 'sub':'Фигуры и дополнительные зоны обсудим отдельно'}
}

for name,d in SERIES.items():
    hero=name+'-hero';technical=name+'-technical'
    # 01: Complete photograph, labels never cover the decoration.
    b=header(d['title'])+photo(hero,504,236,1096,818)
    for i,(a,c) in enumerate(d['features']):
        y=280+i*288;bg=GREEN if i==1 else '#fff';col='#fff' if i==1 else INK
        b+=rect(56,y,400,256,bg)+text(84,y+78,a,54,344,col)+text(84,y+148,c,44,344,col,400)
    b+=rect(504,1054,1096,146,GREEN)+text(536,1106,d['caption'],36,1032,'#fff',400,44)
    (ASSETS/'slides'/f'{name}-1.svg').write_text(frame(b))
    # 02: Removable decoration components; building remains assembled.
    b=header('Из чего складывается\nоформление')+photo(technical,24,280,1050,786)
    for i,(a,c) in enumerate(d['parts']):
        y=350+i*240;b+=text(1120,y-40,f'0{i+1}',28,400,GREEN,400)+text(1120,y,a,42,410)+text(1120,y+116,c,34,410,'#505651',400)
    b+=text(56,1154,'Цвет, материалы и состав согласуем по вашему объекту.',30,1488,'#505651',400)
    (ASSETS/'slides'/f'{name}-2.svg').write_text(frame(b))
    # 03: Photograph with colour and material key, no destructive photo crop.
    b=header('Цвет и детали\nсобирают весь образ')+photo(hero,456,236,1144,854)
    for i,a in enumerate(d['details']):
        y=366+i*260;b+=text(56,y-44,f'0{i+1}',30,344,GREEN,400)+text(56,y+20,a,44,344)
    b+=rect(456,1090,1144,110,PAPER)+text(488,1155,'Палитру подбираем под фасад или интерьер',31,1080,GREEN,400)
    (ASSETS/'slides'/f'{name}-3.svg').write_text(frame(b))
    # 04: A readable request-to-installation sequence.
    b=header('Начнём с фото\nвашего пространства')
    for i,(a,c) in enumerate([('Фото и размеры','Адрес и желаемая дата'),('Состав и расчёт','Обсудим зоны, материалы и крепления'),('Монтаж по адресу','Дату и условия согласуем заранее')]):
        y=376+i*234;b+=text(56,y,f'0{i+1}',40,100,GREEN)+text(184,y,a,46,800)+text(184,y+70,c,34,770,'#505651',400)
    b+=photo(technical,1000,300,560,730)+text(56,1154,'Выезд, монтаж и демонтаж указываем в расчёте.',30,1488,'#505651',400)
    (ASSETS/'slides'/f'{name}-4.svg').write_text(frame(b))
    # 05: Clear next action alongside the entire installed scene.
    b=rect(0,0,1600,1200,GREEN)+header('Подберём оформление\nпод ваш объект',True)+photo(hero,600,290,1000,910)
    b+=text(56,440,d['cta'],48,480,'#fff',600,62)+text(56,810,d['sub'],32,480,'#fff',400,43)
    (ASSETS/'slides'/f'{name}-5.svg').write_text(frame(b))
print('Built 15 self-contained editable SVG slides')
