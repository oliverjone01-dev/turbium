"""Compose 18 full-photo ad cards. Source photos are never painted over or altered.
Run from any folder. Pillow and bundled Manrope fonts are required for authoring only.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/slides'
PNG=ROOT/'output/new-presentation'
PNG.mkdir(parents=True,exist_ok=True)
F=ROOT/'assets'
W,H=1600,1200
WHITE='#fffdf6';FOREST='#183b32';GOLD='#e6c998';BURGUNDY='#57212f'
configs=[
 dict(key='commercial',tag='КАФЕ · РЕСТОРАНЫ · МАГАЗИНЫ',cover=['Вход, у которого','хочется остановиться'],sub='Новогоднее оформление входной группы',whole=['Оформим вход','в характере заведения'],detail=['Бархат, хвоя','и мягкое золото'],object=['В пропорциях','вашего фасада'],cta=['Покажите вход.','Обсудим оформление.'],items=[('Хвоя','Обрамление по форме входа'),('Цвет','Ленты и украшения под заведение'),('Свет','Декоративные огни по составу')],pointers=[('Хвоя и ленты',(1300,440)),('Цвет и фактура',(1380,780)),('Проход для гостей',(1040,1010))]),
 dict(key='home',tag='ЧАСТНЫЕ ДОМА · ДВЕРЬ И КРЫЛЬЦО',cover=['Новый год','начинается у двери'],sub='Новогоднее оформление входа в дом',whole=['Вечером домой.','И сразу праздник.'],detail=['Хвоя, бархат','и тепло огней'],object=['Под архитектуру','вашего дома'],cta=['Пришлите фото.','Начнём с вашего дома.'],items=[('Вход','Хвойное обрамление и венок'),('Палитра','Ленты и украшения под фасад'),('Продолжение','Холл и ёлка по согласованию')],pointers=[('Хвойная арка',(1290,425)),('Венок и бархат',(1130,625)),('Свободный проход',(1020,1030))]),
 dict(key='window',tag='МАГАЗИНЫ · БУТИКИ · ВИТРИНЫ',cover=['Новогодняя витрина.','Ваша коллекция в центре.'],sub='Новогоднее оформление витрины',whole=['Декор по краям.','Коллекция в центре.'],detail=['Фактура, которую','хочется рассмотреть'],object=['Под ваш бренд','и вашу витрину'],cta=['Покажите витрину.','Подберём композицию.'],items=[('Обрамление','Хвоя и подвесы по краям'),('Акценты','Украшения в палитре бренда'),('Обзор','Расположение с учётом товара')],pointers=[('Декор по краям',(1250,460)),('Товар в центре',(1030,700)),('Вход в той же палитре',(1480,970))])
]
font_cache={}
def font(size,weight=600):
 k=(size,weight)
 if k not in font_cache: font_cache[k]=ImageFont.truetype(str(F/f'manrope-{weight}.ttf'),size)
 return font_cache[k]
def text(im,xy,s,size=32,fill=WHITE,weight=600):
 f=font(size,weight);box=ImageDraw.Draw(im).textbbox(xy,s,font=f,anchor='lt')
 assert box[0]>=0 and box[2]<=W-24 and box[3]<=H-20,(s,box)
 ImageDraw.Draw(im).text(xy,s,font=f,fill=fill,anchor='lt',stroke_width=0)
def width(s,size=32,weight=600):return font(size,weight).getlength(s)
def grad(im,top=0,bottom=0,left=0):
 layer=Image.new('RGBA',(W,H));pix=layer.load()
 # One line per row/column keeps the compositing deterministic.
 d=ImageDraw.Draw(layer)
 for y in range(H):
  a=max(int(top*max(0,1-y/600)),int(bottom*max(0,(y-560)/640)))
  if a:d.line((0,y,W,y),fill=(8,22,18,a))
 if left:
  for x in range(1000):
   a=int(left*max(0,1-x/1000));d.line((x,0,x,H),fill=(8,22,18,a))
 return Image.alpha_composite(im.convert('RGBA'),layer)
def photo(key,view='full'):
 return ImageOps.fit(Image.open(F/f'photos/new/{key}-{view}.webp').convert('RGB'),(W,H),method=Image.Resampling.LANCZOS).convert('RGBA')
def rr(im,box,fill,r=18,outline=None,width=1):ImageDraw.Draw(im).rounded_rectangle(box,r,fill=fill,outline=outline,width=width)
def badge(im,txt,x=64,y=58,size=23):
 w=width(txt,size)+38;rr(im,(x,y,x+w,y+52),(17,36,30,230),r=26);text(im,(x+19,y+14),txt,size)
def brand(im):
 logo=Image.open(F/'logo-white.png').convert('RGBA');logo.thumbnail((240,62));im.alpha_composite(logo,(1296,58))
def header(im,c,n):
 badge(im,c['tag']);brand(im)
 text(im,(64,1139),'ДЕКОРИЯ  /  НОВЫЙ ГОД 2027',19,weight=600)
 text(im,(1440,1139),f'{n:02d} / 06',19)
def title(im,lines,y=154,size=100,x=64,accent=True):
 size=min(size,int(size*1472/max(width(t,size,800) for t in lines)))
 for i,s in enumerate(lines):
  assert x+width(s,size,800)<1540,(s,width(s,size,800))
  text(im,(x,y+i*(size+10)),s,size,GOLD if accent and i==1 else WHITE,weight=800)
def bottom_pills(im,labels,y=1008):
 x=64
 for s in labels:
  w=width(s,31)+40
  rr(im,(x,y,x+w,y+60),(255,253,246,245),r=10);text(im,(x+20,y+15),s,31,FOREST);x+=w+14
 assert x<1536

def callout(im,txt,xy,target,idx):
 x,y=xy;w=width(txt,34)+82
 d=ImageDraw.Draw(im);d.line((x+w,y+32,*target),fill=WHITE,width=2);d.ellipse((target[0]-7,target[1]-7,target[0]+7,target[1]+7),fill=GOLD)
 rr(im,(x,y,x+w,y+65),(255,253,246,246),r=12)
 d.ellipse((x+14,y+14,x+50,y+50),fill=BURGUNDY)
 text(im,(x+25,y+21),str(idx),20);text(im,(x+64,y+17),txt,34,FOREST)

def save(im,key,n):
 im=im.convert('RGB');im.save(PNG/f'{key}-new-{n}.png',optimize=True);im.save(OUT/f'{key}-new-{n}.webp',quality=95,method=6)

for c in configs:
 k=c['key']
 im=grad(photo(k),top=185,bottom=160);header(im,c,1);title(im,c['cover']);text(im,(68,402),c['sub'],35)
 bottom_pills(im,['3D-визуализация бесплатно','Декор и монтаж']);save(im,k,1)
 im=grad(photo(k,'angle'),top=185,bottom=95);header(im,c,2);title(im,c['whole'],size=91)
 for i,(label,target) in enumerate(c['pointers']):callout(im,label,(64,620+i*132),target,i+1)
 save(im,k,2)
 im=grad(photo(k,'detail'),top=190,bottom=160);header(im,c,3);title(im,c['detail'],size=100)
 bottom_pills(im,['Договор и смета','Безнал и документы','Монтаж по графику'],y=1008)
 save(im,k,3)
 im=grad(photo(k),top=190,bottom=180);header(im,c,4)
 title(im,['Три комплектации','под ваш бюджет'],size=101)
 if k=='commercial':
  packs=[('Точечно',['Оформление двери','и входного портала']),('Шире',['Вход и соседние окна','в одной палитре']),('Комплексно',['Вход, витрина','и выбранные зоны внутри'])]
 elif k=='home':
  packs=[('Дверь',['Венок, хвоя','и декоративные акценты']),('Крыльцо',['Вход и композиции','по краям крыльца']),('Вход и дом',['Добавим холл','или оформление ёлки'])]
 else:
  packs=[('Обрамление',['Хвойная композиция','по краям витрины']),('Больше деталей',['Ленты, подвесы','и декоративный свет']),('Витрина и вход',['Две зоны','в единой палитре'])]
 for i,(name,lines) in enumerate(packs):
  x=64+i*498;bg=[(255,253,246,248),(24,59,50,246),(87,33,47,246)][i];fg=FOREST if i==0 else WHITE
  rr(im,(x,760,x+476,1043),bg,r=18)
  text(im,(x+26,786),f'0{i+1}',29,BURGUNDY if i==0 else GOLD)
  text(im,(x+26,839),name,35,fg,800)
  for n,line in enumerate(lines):text(im,(x+26,906+n*43),line,29,fg,400)
 text(im,(68,1080),'Точный состав и стоимость определим по вашему объекту.',29)
 save(im,k,4)
 im=grad(photo(k),top=200,bottom=220);header(im,c,5)
 title(im,['Сначала покажем','ваше оформление'],size=101)
 text(im,(68,393),'Бесплатная 3D-визуализация до заказа',38)
 for x,view,label in [(64,'before','Исходный вид'),(832,'full','Вариант оформления')]:
  pic=ImageOps.fit(Image.open(F/f'photos/new/{k}-{view}.webp').convert('RGB'),(704,528),method=Image.Resampling.LANCZOS).convert('RGBA')
  im.alpha_composite(pic,(x,485))
  rr(im,(x+18,939,x+686,991),(17,36,30,235),r=10)
  text(im,(x+40,954),label,29)
 d=ImageDraw.Draw(im);d.ellipse((759,707,841,789),fill=BURGUNDY,outline=GOLD,width=2)
 d.line((781,748,820,748),fill=WHITE,width=3);d.line((809,736,821,748,809,760),fill=WHITE,width=3)
 text(im,(68,1047),'Выезд и замер бесплатно после подписания договора.',29)
 text(im,(68,1094),'Пример концепции оформления.',24)
 save(im,k,5)
 im=grad(photo(k),top=185,bottom=170);header(im,c,6)
 cta_title=['Пришлите фото','вашего входа'] if k!='window' else ['Пришлите фото','вашей витрины']
 title(im,cta_title,size=106)
 rr(im,(880,490,1536,946),(255,253,246,246),r=22)
 text(im,(916,528),'Для расчёта',39,FOREST,800)
 for i,label in enumerate(['Фото объекта целиком','Примерные размеры','Адрес или населённый пункт','Желаемая дата']):
  y=614+i*72
  ImageDraw.Draw(im).ellipse((916,y,952,y+36),fill=BURGUNDY)
  text(im,(928,y+7),str(i+1),20)
  text(im,(972,y+4),label,30,FOREST)
 for i,line in enumerate(['Олеся уточнит задачу,','предложит состав','и рассчитает стоимость.']):
  text(im,(68,740+i*56),line,36)
 rr(im,(64,1000,1536,1096),BURGUNDY,r=14,outline=GOLD,width=2)
 text(im,(105,1029),'Напишите в чат Авито',40)
 ImageDraw.Draw(im).line((1430,1048,1484,1048),fill=WHITE,width=4)
 ImageDraw.Draw(im).line((1469,1032,1485,1048,1469,1064),fill=WHITE,width=4)
 save(im,k,6)

# View all 18 in their actual gallery order.
sheet=Image.new('RGB',(1800,760),'#e7e9e6')
for row,c in enumerate(configs):
 for col in range(6):
  im=Image.open(PNG/f"{c['key']}-new-{col+1}.png")
  im.thumbnail((290,218));sheet.paste(im,(col*300+5,row*250+28))
  ImageDraw.Draw(sheet).text((col*300+8,row*250+7),f"{c['key']} {col+1}",font=font(15),fill=FOREST)
sheet.save(PNG/'contact-sheet.jpg',quality=94)
print('Created 18 PNG and 18 WebP cards')
