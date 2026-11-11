"""DEKORIYA: true geometry, 48 sampled camera views, staged light/decor/surface explosion.
Run with Blender 4.5 LTS --background --python this_file -- --out PATH --mode preview|sequence.
No image warping or AI frame interpolation: every frame is rendered from the same scene.
"""
import bpy, math, random, json, sys, argparse
from mathutils import Vector
from pathlib import Path
from math import sin,cos,pi
args=sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else []
ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--mode',default='preview');ap.add_argument('--category',default='all');ap.add_argument('--engine',default='eevee');ap.add_argument('--samples',type=int,default=32);cfg=ap.parse_args(args);OUT=Path(cfg.out);OUT.mkdir(parents=True,exist_ok=True)
random.seed(1464);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
SC=bpy.context.scene;SC.render.engine='CYCLES'if cfg.engine=='cycles'else'BLENDER_EEVEE_NEXT';
if cfg.engine=='cycles':
 SC.cycles.samples=cfg.samples;SC.cycles.use_denoising=True
 try:
  prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
  for d in prefs.devices:d.use=d.type=='METAL'
  SC.cycles.device='GPU'
 except Exception:SC.cycles.device='CPU'
SC.render.film_transparent=True;SC.render.image_settings.file_format='PNG';SC.render.image_settings.color_mode='RGBA';SC.render.resolution_percentage=100
if hasattr(SC.eevee,'taa_render_samples'):SC.eevee.taa_render_samples=cfg.samples
SC.world.use_nodes=True;SC.world.node_tree.nodes['Background'].inputs[0].default_value=(.73,.69,.61,1);SC.world.node_tree.nodes['Background'].inputs[1].default_value=.45
SC.view_settings.view_transform='AgX'
try:SC.view_settings.look='AgX - Medium High Contrast'
except:pass
PARENT=None

def rgb(h):
 c=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)
def mat(name,h,metal=0,rough=.5,noise=False,sheen=0,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb(h),1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if 'Specular IOR Level'in p.inputs:p.inputs['Specular IOR Level'].default_value=.28
 if 'Sheen Tint'in p.inputs:p.inputs['Sheen Tint'].default_value=(*rgb(h),1)
 if 'Sheen Weight'in p.inputs:p.inputs['Sheen Weight'].default_value=sheen
 if emit:p.inputs['Emission Color'].default_value=(*rgb(h),1);p.inputs['Emission Strength'].default_value=emit
 if noise:
  t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=95 if sheen else 32;t.inputs['Detail'].default_value=3
  bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.06 if sheen else .10;bump.inputs['Distance'].default_value=.001 if sheen else .008;m.node_tree.links.new(t.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
STONE=mat('Ivory limestone','D9CCB8',rough=.63,noise=True);STONE2=mat('Warm travertine','C3AE8E',rough=.6,noise=True);GOLD=mat('Brushed champagne brass','AE8953',.78,.27);DARK=mat('Bronze dark glass','7F7059',.05,.19);
DARK.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.22
if hasattr(DARK,'surface_render_method'):DARK.surface_render_method='DITHERED'
VELVET=mat('Burgundy velvet','57212F',rough=.64,noise=True,sheen=.18);VELVETD=mat('Burgundy shaded velvet','36101D',rough=.52,sheen=.5);IVORY=mat('Ivory ceramic','F1E8D4',rough=.32);PAPER=mat('Warm translucent candle','F3D8A3',rough=.45,emit=.4);FLAME=mat('Candle flame','FFD188',rough=.4,emit=3);GUIDE=mat('Assembly guide','B7A58E',rough=.7)
GREENS=[mat('Leaf sage '+str(i),h,rough=.6)for i,h in enumerate(['536348','66755B','7A896B','40523D'])];PETAL=mat('Ivory petals','EEE2CC',rough=.48,sheen=.15);PINK=mat('Soft blush petals','C9A79D',rough=.5);YELLOW=mat('Flower centre','B6974E',rough=.75)

ROOT=Path(__file__).resolve().parents[1]
def texture_material(m,path,scale=1):
 n=m.node_tree.nodes;p=n.get('Principled BSDF');tex=n.new('ShaderNodeTexImage');tex.projection='BOX';tex.projection_blend=.2;tex.image=bpy.data.images.load(str(ROOT/path),check_existing=True);coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=scale;m.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0]);m.node_tree.links.new(mapping.outputs[0],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
texture_material(STONE,Path('assets/camera-v64/materials/limestone.png'),2.8)
texture_material(STONE2,Path('assets/camera-v64/materials/limestone.png'),3.4)
texture_material(VELVET,Path('assets/camera-v64/materials/velvet.png'),4.0)
BOT=bpy.data.materials.new('Photographic botanical cutout');BOT.use_nodes=True;n=BOT.node_tree.nodes;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets/camera-v64/materials/botanical.png'));BOT.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.65;p.inputs['Specular IOR Level'].default_value=.15
alpha=n.new('ShaderNodeMapRange');alpha.inputs['From Min'].default_value=.10;alpha.inputs['From Max'].default_value=.90;alpha.clamp=True;BOT.node_tree.links.new(t.outputs['Alpha'],alpha.inputs['Value']);BOT.node_tree.links.new(alpha.outputs['Result'],p.inputs['Alpha']);BOT.surface_render_method='DITHERED'
DOOR=bpy.data.materials.new('Photographic bronze and interior');DOOR.use_nodes=True;n=DOOR.node_tree.nodes;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets/exploded-v62/entrance-surfaces.png'));DOOR.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);DOOR.node_tree.links.new(t.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.22;p.inputs['Roughness'].default_value=.38;p.inputs['Specular IOR Level'].default_value=.16

def put(o,name,m=None):
 o.name=name
 if m:o.data.materials.append(m)
 if PARENT:o.parent=PARENT
 return o

def cube(name,loc,dim,m,bev=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=put(bpy.context.object,name,m);o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:b=o.modifiers.new('Soft crafted edges','BEVEL');b.width=bev;b.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def sphere(name,loc,scale,m,seg=24,rings=12):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=1,location=loc);o=put(bpy.context.object,name,m);o.scale=scale
 for f in o.data.polygons:f.use_smooth=True
 return o

def cylinder(name,loc,r,depth,m,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=put(bpy.context.object,name,m);b=o.modifiers.new('Edge glints','BEVEL');b.width=.008;b.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o

def line(name,pts,r,m):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=16;d.bevel_depth=r;d.bevel_resolution=3;sp=d.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,d);SC.collection.objects.link(o);return put(o,name,m)

def mesh(name,verts,faces,m):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);SC.collection.objects.link(o);put(o,name,m)
 for f in d.polygons:f.use_smooth=True
 return o

def lathe(name,pos,profile,m):
 verts=[];faces=[];n=48
 for r,z in profile:
  verts.extend([(pos[0]+r*cos(2*pi*j/n),pos[1]+r*sin(2*pi*j/n),pos[2]+z)for j in range(n)])
 for i in range(len(profile)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
 o=mesh(name,verts,faces,m);sub=o.modifiers.new('Ceramic profile smoothing','SUBSURF');sub.levels=2;return o

# Consolidated botanical meshes avoid thousands of scene objects.
class Bouquet:
 def __init__(self):self.parts={}
 def add(self,m,vs,fs):
  v,f=self.parts.setdefault(m.name,([],[]));n=len(v);v.extend(vs);f.extend(tuple(n+x for x in q)for q in fs)
 def leaf(self,pos,angle,size,m):
  v=[]
  for i in range(9):
   t=i/8;half=sin(pi*t)*size*.53
   for side in [-1,1]:x=t*size;y=side*half;v.append((pos[0]+x*cos(angle)-y*sin(angle),pos[1]+x*sin(angle)+y*cos(angle),pos[2]+sin(pi*t)*size*.16))
  self.add(m,v,[(2*i,2*i+1,2*i+3,2*i+2)for i in range(8)])
 def blossom(self,pos,size,m=PETAL):
  # Layered curved petals have real volume and retain shape during camera orbit.
  for ring,count in [(0,7),(1,9)]:
   for j in range(count):
    a=2*pi*j/count+ring*.35;v=[]
    for i in range(6):
     t=i/5;r=size*(.12+t*(.85-ring*.12));half=sin(pi*t)*size*.38
     for side in [-1,1]:x=r*cos(a)-side*half*sin(a);z=r*sin(a)+side*half*cos(a);v.append((pos[0]+x,pos[1]-.02-ring*.016-sin(pi*t)*size*.25,pos[2]+z))
    self.add(m,v,[(2*i,2*i+1,2*i+3,2*i+2)for i in range(5)])
  # centre is an eight-sided low poly dome, tiny at thumbnail scale
  v=[(pos[0],pos[1]-.04,pos[2])]+[(pos[0]+size*.15*cos(j*pi/4),pos[1]-.025,pos[2]+size*.15*sin(j*pi/4))for j in range(8)]
  self.add(YELLOW,v,[(0,1+j,1+(j+1)%8)for j in range(8)])
 def finish(self,name):
  for mn,(v,f)in self.parts.items():mesh(name+' '+mn,v,f,bpy.data.materials[mn])

def image_card(name,pos,width,height,material,angle=0,uv=None):
 vs=[(-width/2,0,0),(width/2,0,0),(width/2,0,height),(-width/2,0,height)];o=mesh(name,vs,[(0,1,2,3)],material);o.location=pos;o.rotation_euler.z=angle;layer=o.data.uv_layers.new(name='Photo UV');coords=uv or [(0,0),(1,0),(1,1),(0,1)]
 for i,co in enumerate(coords):layer.data[i].uv=co
 return o

def garland(name,x,y,z0,z1):
 height=z1-z0
 for i in range(3):
  image_card(name+' botanical '+str(i),(x+.045*sin(i*3),y-.06*i,z0+height*i*.25),.64,height*.60,BOT,angle=(i-1)*.12)

def floral(name,pos,size=.7):
 for i in range(3):
  image_card(name+' botanical '+str(i),(pos[0]+(i-1)*.14*size,pos[1]+(i-1)*.07,pos[2]-.12),size*.67,size*1.2,BOT,angle=(i-1)*.28)

def drape(name,z=3.35,width=2.7,drop=2.95,y=-.45):
 # Left hanging velvet panel, built as a folded solid cloth surface.
 v=[];f=[];nu,nv=28,64
 for j in range(nv+1):
  t=j/nv
  for i in range(nu+1):
   u=i/nu;x=-width/2+.53*u+.07*sin(t*pi)*sin(u*2*pi);yy=y+.055*(.2+.8*sin(pi*t))*sin(u*8*pi+t*1.2);zz=z-drop*t+.04*sin(u*pi*3)*t;v.append((x,yy,zz))
 for j in range(nv):
  for i in range(nu):a=j*(nu+1)+i;f.append((a,a+1,a+nu+2,a+nu+1))
 o=mesh(name+' vertical fold',v,f,VELVET);sol=o.modifiers.new('Velvet hem thickness','SOLIDIFY');sol.thickness=.012
 v=[];f=[];nu,nv=64,22
 for i in range(nu+1):
  u=i/nu
  for j in range(nv+1):
   t=j/nv;v.append((-width/2+width*u,y-.04+.045*sin(t*8*pi+u*pi),z-.45*sin(pi*u)-.42*t*sin(pi*u)**.4))
 for i in range(nu):
  for j in range(nv):a=i*(nv+1)+j;f.append((a,a+nv+1,a+nv+2,a+1))
 o=mesh(name+' catenary swag',v,f,VELVET);sol=o.modifiers.new('Velvet thickness','SOLIDIFY');sol.thickness=.012

def decorative_lantern(name,x,y,h):
 # Freestanding sculptural candle lantern: brass cage, pleated ivory insert, portable handle.
 n=8;r=h*.25;cylinder(name+' base',(x,y,.18),r+.025,.04,GOLD)
 for j in range(n):
  a=j*2*pi/n;line(name+' fine cage '+str(j),[(x+r*cos(a),y+r*sin(a),.2),(x+r*.86*cos(a),y+r*.86*sin(a),h+.17)],.007,GOLD)
 cylinder(name+' crown',(x,y,h+.18),r*.90,.025,GOLD);cylinder(name+' ivory candle',(x,y,.2+h*.32),r*.56,h*.6,PAPER)
 sphere(name+' flame',(x,y,.2+h*.66),(.018,.018,.055),FLAME,12,8)
 pts=[(x+r*.63*cos(t*pi),y,h+.19+r*.78*sin(t*pi))for t in [i/24 for i in range(25)]];line(name+' arched carry handle',pts,.009,GOLD)

def make_entrance(roots):
 global PARENT
 PARENT=roots['surfaces'];cube('Entry limestone plinth',(0,0,.08),(3.55,1.45,.16),STONE)
 for x in [-1.28,1.28]:cube('Entry solid pier',(x,.12,1.75),(.48,.55,3.35),STONE)
 cube('Entry deep lintel',(0,.12,3.33),(3.04,.55,.4),STONE);cube('Entry crown lower',(0,.1,3.53),(3.24,.66,.13),STONE);cube('Entry crown cap',(0,.1,3.65),(3.43,.78,.1),STONE)
 cube('Entry bronze reveal',(0,.08,1.72),(2.12,.2,2.98),GOLD);image_card('Entry photographic glass',(0,-.065,.3),1.99,2.84,DOOR,uv=[(.323,.095),(.644,.085),(.644,.751),(.323,.763)])
 for x in [-1.0,0,1.0]:cube('Entry bronze stile',(x,-.09,1.72),(.035,.055,2.85),GOLD,.006)
 for z in [.3,3.14]:cube('Entry bronze cross rail',(0,-.09,z),(2.02,.055,.035),GOLD,.005)
 for x in [-.11,.11]:line('Entry long brass door pull',[(x,-.18,1.25),(x,-.18,1.9)],.018,GOLD)
 # Volumetric warm showroom behind transparent glass.
 cube('Entry interior warm back wall',(0,.74,1.65),(2.0,.08,2.8),STONE2)
 cube('Entry interior stone floor',(0,.28,.25),(2.0,1.0,.08),STONE2)
 cylinder('Entry inside round table',(.12,.42,.95),.37,.065,STONE)
 cylinder('Entry inside table brass stem',(.12,.42,.6),.035,.7,GOLD)
 lathe('Entry inside vase',(.12,.42,1.0),[(0,0),(.07,.01),(.09,.12),(.045,.19)],IVORY)
 PARENT=roots['decor'];drape('Entry velvet');garland('Entry eucalyptus and ivory florals',1.18,-.47,.6,3.47)
 PARENT=roots['light'];decorative_lantern('Entry designer lantern tall',-1.0,-.77,1.0);decorative_lantern('Entry designer lantern small',-.54,-.75,.55);decorative_lantern('Entry designer lantern medium',-1.41,-.54,.72)

def make_window(roots):
 global PARENT
 PARENT=roots['surfaces'];cube('Window stone plinth',(0,0,.09),(3.5,1.15,.18),STONE)
 cube('Window back panel',(0,.3,1.65),(3.18,.15,2.95),STONE2)
 for x in [-1.55,1.55]:cube('Window stone jamb',(x,0,1.65),(.24,.7,3.1),STONE)
 for z in [.25,3.12]:cube('Window stone sill and lintel',(0,0,z),(3.3,.7,.22),STONE)
 for x in [-1.41,1.41]:cube('Window bronze trim',(x,-.365,1.67),(.025,.03,2.74),GOLD,.004)
 for z in [.32,3.02]:cube('Window bronze trim horizontal',(0,-.365,z),(2.85,.03,.025),GOLD,.004)
 specs=[(-.89,.65),(-.02,1.03),(.86,.5)]
 for x,h in specs:cube('Window travertine podium',(x,-.07,.2+h/2),(.64,.62,h),STONE)
 PARENT=roots['decor'];drape('Window velvet',z=2.97,width=2.75,drop=2.45,y=-.31)
 lathe('Window round ceramic vase',(-.89,-.07,.85),[(0,0),(.15,.015),(.22,.15),(.20,.28),(.08,.38),(.075,.4)],IVORY)
 lathe('Window ceramic bowl',(-.02,-.07,1.23),[(0,0),(.12,.04),(.20,.12),(.29,.28),(.30,.30)],IVORY)
 lathe('Window floral brass bowl',(.86,-.07,.7),[(0,0),(.17,.015),(.28,.13),(.29,.16)],GOLD);floral('Window delicate flowers',(.86,-.07,.83),.65)
 PARENT=roots['light'];cube('Window brass light rail',(0,.01,2.94),(2.6,.1,.07),GOLD,.01)
 for x in [-.85,0,.85]:cylinder('Window accent spotlight',(x,-.02,2.83),.075,.15,GOLD)

def make_chair():
 x,y=-1.05,-.65
 for dx in [-.24,.24]:
  for dy in [-.23,.23]:line('Chair brass leg',[(x+dx,y+dy,.16),(x+dx*.95,y+dy*.95,.56)],.018,GOLD)
 sphere('Chair seat cushion',(x,y,.59),(.39,.39,.12),VELVET)
 v=[];f=[];n,m=40,12
 for i in range(n+1):
  a=pi*.03+pi*.94*i/n
  for j in range(m):
   b=2*pi*j/m;r=.38+.09*cos(b);v.append((x+r*cos(a),y+r*sin(a),.86+.35*sin(b)))
 for i in range(n):
  for j in range(m):a=i*m+j;b=i*m+(j+1)%m;f.append((a,b,b+m,a+m))
 mesh('Chair upholstered curved back',v,f,VELVET)

def make_interior(roots):
 global PARENT
 PARENT=roots['surfaces'];cube('Interior travertine floor',(0,0,.08),(3.65,2.1,.16),STONE)
 cube('Interior back solid wall',(0,.78,1.75),(3.4,.16,3.35),STONE)
 # Open left window wall, actual thickness and bronze mullions.
 
 for y in [-.72,.72]:cube('Interior left window pier',(-1.61,y,1.75),(.18,.12,3.35),STONE)
 for z in [.2,3.34]:cube('Interior window frame stone',(-1.61,0,z),(.18,1.55,.18),STONE)
 for y in [-.7,.63]:cube('Interior left window bronze jamb',(-1.51,y,1.75),(.08,.035,3.0),GOLD,.006)
 for z in [.3,1.25,2.15,3.2]:cube('Interior window bronze transom',(-1.51,-.03,z),(.08,1.38,.035),GOLD,.005)
 cube('Reception solid travertine desk',(.23,-.35,.73),(1.96,.72,1.1),STONE)
 cube('Reception top slab',(.23,-.35,1.31),(2.1,.82,.12),STONE)
 cube('Reception small brass sign',(.4,-.3,1.48),(.36,.045,.18),GOLD,.01)
 PARENT=roots['decor'];cube('Reception burgundy decorative front',(.23,-.73,.75),(1.66,.06,.78),VELVETD,.012)
 for j in range(23):cylinder('Reception velvet rib',(-.55+j*.071,-.775,.75),.028,.74,VELVET,16)
 make_chair();lathe('Interior ceramic floral vase',(-.18,-.32,1.38),[(0,0),(.13,.01),(.20,.16),(.17,.32),(.08,.38)],IVORY);floral('Interior editorial floral',(-.18,-.32,1.7),.76)
 PARENT=roots['light']
 for x,h in [(-.4,2.45),(.5,2.65)]:
  cylinder('Interior pendant ceiling rose',(x,-.28,3.25),.11,.035,GOLD);line('Interior pendant fine cord',[(x,-.28,3.24),(x,-.28,h+.19)],.008,GOLD)
  lathe('Interior sculptural opal pendant',(x,-.28,h),[(.02,-.16),(.15,-.12),(.22,0),(.17,.15),(.07,.19)],IVORY);cylinder('Interior pendant brass cap',(x,-.28,h+.19),.075,.055,GOLD)

MODELS={}
for key,fn in [('entrance',make_entrance),('window',make_window),('interior',make_interior)]:
 roots={}
 for layer in ['surfaces','decor','light']:
  o=bpy.data.objects.new(key+'__'+layer,None);SC.collection.objects.link(o);roots[layer]=o
 MODELS[key]=roots;fn(roots)
PARENT=None
# Studio light rig only, no textured image planes or perspective deformation.
for name,loc,power,size,col in [('Key',(-4,-6,8),850,5,(1,.9,.75)),('Fill',(5,-2,6),650,5,(.88,.94,1)),('Rim',(0,5,7),1100,4,(1,.87,.72))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(name,d);SC.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('Delivery Camera');cam=bpy.data.objects.new('Delivery Camera',camd);SC.collection.objects.link(cam);SC.camera=cam;camd.type='ORTHO';camd.lens=50

# Assembly guide lines are deliberately omitted from the delivery scene.
# They crossed the photographic door and read as render/decoding artifacts.

def ease(t):t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def phase(t,a,b):return ease((t-a)/(b-a))

def pose(key,t):
 e=ease(t);az=math.radians(-78+30*e);el=math.radians(20+12*e)
 # Fixed world-space explosion vectors chosen for screen-left at final camera azimuth.
 a=math.radians(-48);right=Vector((-sin(a),cos(a),0));up=Vector((-cos(a)*sin(math.radians(32)),-sin(a)*sin(math.radians(32)),cos(math.radians(32))))
 target=Vector((0,0,1.75))+right*(-.85*e)
 cam.location=target+Vector((cos(az)*cos(el),sin(az)*cos(el),sin(el)))*13;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=5.9+2.6*e
 offsets={'light':(-2.9,.28,phase(t,.06,.46)),'decor':(-1.55,.03,phase(t,.27,.76)),'surfaces':(.8,-.12,phase(t,.53,.96))}
 for k,roots in MODELS.items():
  for layer,root in roots.items():
   for o in root.children:o.hide_render=k!=key;o.hide_set(k!=key)
   dx,dy,p=offsets[layer];root.location=(right*dx+up*dy)*p

 # Fit EVERY sampled pose, not just the endpoints: early flying lanterns must not clip.
 bpy.context.view_layer.update();q=cam.rotation_euler.to_quaternion();cr=q@Vector((1,0,0));cu=q@Vector((0,1,0));xs=[];ys=[]
 for root in MODELS[key].values():
  for o in root.children:
   if o.type not in {'MESH','CURVE'}:continue
   for corner in o.bound_box:
    world=o.matrix_world@Vector(corner);xs.append(world.dot(cr));ys.append(world.dot(cu))
 cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
 shift=cr*(cx-target.dot(cr))+cu*(cy-target.dot(cu));cam.location+=shift
 camd.ortho_scale=max((max(xs)-min(xs))*1.20,(max(ys)-min(ys))*4/3*1.20)
 return {'t':t,'azimuthDegrees':-78+30*e,'elevationDegrees':20+12*e,'cameraLocation':list(cam.location),'cameraEuler':list(cam.rotation_euler),'orthoScale':camd.ortho_scale,'layers':{k:list(v.location)for k,v in MODELS[key].items()}}

pose('entrance',0);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'dekoriya-camera-v64.blend'),compress=True)
keys=list(MODELS) if cfg.category=='all'else[cfg.category]
manifest={'frames':48,'columns':8,'rows':6,'frameWidth':512,'frameHeight':384,'durationMs':1800,'order':['light','decor','surfaces'],'cameraOrbitDegrees':30,'cameraElevationDegrees':12,'scenes':{}}
for key in keys:
 target=OUT/key;target.mkdir(exist_ok=True);states=[]
 steps=[0,24,47]if cfg.mode=='preview'else list(range(48))
 for frame in steps:
  state=pose(key,frame/47);state['frame']=frame;states.append(state)
  SC.render.resolution_x=768 if cfg.mode=='preview'else 512;SC.render.resolution_y=576 if cfg.mode=='preview'else 384;SC.render.filepath=str(target/f'frame-{frame:03d}.png');bpy.ops.render.render(write_still=True)
 if cfg.mode=='sequence':
  SC.render.resolution_x=1024;SC.render.resolution_y=768
  for state_name,t in [('closed',0),('open',1)]:pose(key,t);SC.render.filepath=str(target/(state_name+'.png'));bpy.ops.render.render(write_still=True)
 manifest['scenes'][key]={'samples':states}
(OUT/('preview-manifest.json'if cfg.mode=='preview'else'camera-manifest.json')).write_text(json.dumps(manifest,indent=2))
pose('entrance',0);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'dekoriya-camera-v64.blend'),compress=True)
print('DEKORIYA_RENDER_DONE',cfg.mode,keys,flush=True)
