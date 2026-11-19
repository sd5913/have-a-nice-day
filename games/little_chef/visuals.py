"""PNG skins with alpha blending. Missing/invalid files use code-drawn placeholders."""
from pathlib import Path
import warnings
import cv2
import numpy as np

INK=(70,75,85)
class Visuals:
    def __init__(self, root):
        self.root=Path(root); self.images={}; self.cache={}
        for name in ('cat','ingredient','bowl','cover','ball','basket','fish','background','ingredient_fish','ingredient_chicken','ingredient_kibble','ingredient_pumpkin','ingredient_carrot','ingredient_peas','ingredient_rice','ingredient_salmon'):
            path=self.root/(name+'.png')
            if path.is_file():
                pic=cv2.imdecode(np.fromfile(str(path),dtype=np.uint8),cv2.IMREAD_UNCHANGED)
                if pic is not None:
                    if pic.ndim==2: pic=cv2.cvtColor(pic,cv2.COLOR_GRAY2BGRA)
                    if pic.shape[2]==3: pic=cv2.cvtColor(pic,cv2.COLOR_BGR2BGRA)
                    self.images[name]=pic
                else: warnings.warn(f'Cannot read {path}; using placeholder')

        # The generated sheet uses eight equal cells. Treat each cell as a sprite.
        sheet_path=self.root/'ingredients.png'
        if sheet_path.is_file():
            sheet=cv2.imdecode(np.fromfile(str(sheet_path),dtype=np.uint8),cv2.IMREAD_UNCHANGED)
            if sheet is not None and sheet.ndim==3 and sheet.shape[2]==4:
                sh,sw=sheet.shape[:2]
                names=('fish','chicken','kibble','pumpkin','carrot','peas','rice','salmon')
                for i,name in enumerate(names):
                    cell=sheet[(i//4)*sh//2:((i//4)+1)*sh//2,(i%4)*sw//4:((i%4)+1)*sw//4]
                    yy,xx=np.where(cell[:,:,3]>64)
                    if len(xx):
                        self.images['ingredient_'+name]=cell[max(0,yy.min()-4):yy.max()+5,max(0,xx.min()-4):xx.max()+5].copy()

    def background(self,w,h):
        out=np.full((h,w,3),(240,247,250),dtype=np.uint8)
        if 'background' in self.images:
            self.draw(out,'background',(w//2,h//2),(w,h))
        else:
            cv2.rectangle(out,(20,165),(w-20,h-80),(224,236,239),-1)
            cv2.line(out,(20,h-160),(w-20,h-160),(205,218,224),2)
        return out

    def draw(self,canvas,name,center,size):
        w,h=map(int,size); cx,cy=map(int,center)
        if w<=0 or h<=0: return
        key=(name,w,h)
        if key not in self.cache:
            if name in self.images:
                src=self.images[name]; sh,sw=src.shape[:2]
                scale=min(w/sw,h/sh)
                self.cache[key]=cv2.resize(src,(max(1,round(sw*scale)),max(1,round(sh*scale))),interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_LINEAR)
            else: self.cache[key]=self.placeholder(name,w,h)
        sprite=self.cache[key]; h,w=sprite.shape[:2]
        left,top=cx-w//2,cy-h//2
        x0,y0=max(0,left),max(0,top); x1,y1=min(canvas.shape[1],left+w),min(canvas.shape[0],top+h)
        if x1<=x0 or y1<=y0: return
        src=sprite[y0-top:y1-top,x0-left:x1-left]
        alpha=src[:,:,3:4].astype(np.float32)/255
        canvas[y0:y1,x0:x1]=(src[:,:,:3]*alpha+canvas[y0:y1,x0:x1]*(1-alpha)).astype(np.uint8)

    @staticmethod
    def placeholder(name,w,h):
        p=np.zeros((240,240,4),dtype=np.uint8)
        ink=(*INK,255); cream=(195,218,240,255); pink=(150,170,220,255)
        if name=='cat':
            cv2.ellipse(p,(120,179),(60,48),0,0,360,cream,-1)
            cv2.fillPoly(p,[np.array([(58,93),(56,24),(103,66)]),np.array([(139,64),(185,24),(184,100)])],cream)
            cv2.ellipse(p,(120,106),(76,65),0,0,360,cream,-1)
            for x in (87,151): cv2.line(p,(x-9,106),(x+9,106),ink,5)
            cv2.polylines(p,[np.array([(104,132),(112,139),(120,131),(128,139),(136,132)])],False,ink,4)
            cv2.ellipse(p,(80,124),(12,6),0,0,360,pink,-1); cv2.ellipse(p,(160,124),(12,6),0,0,360,pink,-1)
        elif name=='bowl':
            cv2.ellipse(p,(120,85),(100,40),0,0,360,(185,192,157,255),-1)
            cv2.ellipse(p,(120,110),(100,75),0,0,180,(165,182,142,255),-1)
            cv2.ellipse(p,(120,85),(85,26),0,0,360,(225,235,215,255),-1)
        elif name=='cover':
            cv2.rectangle(p,(15,20),(225,220),(151,181,207,255),-1)
            cv2.line(p,(15,80),(225,80),ink,3)
            cv2.rectangle(p,(75,105),(165,142),(205,223,236,255),-1)
        elif name=='basket':
            cv2.ellipse(p,(120,85),(95,54),180,0,180,(105,145,180,255),8)
            cv2.fillPoly(p,[np.array([(15,90),(225,90),(205,215),(35,215)])],(135,173,204,255))
            for x in range(50,210,35): cv2.line(p,(x,100),(x,200),(185,209,226,255),4)
        elif name in ('fish','ingredient','ingredient_fish'):
            cv2.ellipse(p,(105,120),(70,40),0,0,360,(145,183,211,255),-1)
            cv2.fillPoly(p,[np.array([(160,120),(218,75),(218,165)])],(145,183,211,255))
            cv2.circle(p,(65,110),5,ink,-1)
        elif name.startswith('ingredient_'):
            colors={'ingredient_chicken':(169,195,224,255),'ingredient_kibble':(85,126,167,255),'ingredient_pumpkin':(85,163,231,255)}
            color=colors.get(name,cream)
            if name=='ingredient_carrot':
                cv2.fillPoly(p,[np.array([(65,65),(175,65),(120,210)])],(55,145,235,255))
                for x in (95,120,145): cv2.line(p,(120,65),(x,25),(80,150,95,255),10)
            elif name=='ingredient_peas':
                for x,y in [(75,100),(130,75),(165,135),(100,165)]: cv2.circle(p,(x,y),29,(90,170,115,255),-1)
            elif name=='ingredient_rice':
                for x,y in [(80,90),(120,80),(160,105),(90,135),(140,145)]: cv2.ellipse(p,(x,y),(15,30),35,0,360,(220,235,245,255),-1)
            elif name=='ingredient_salmon':
                cv2.ellipse(p,(120,120),(85,60),-15,0,360,(130,165,235,255),-1)
                for x in (75,110,145): cv2.line(p,(x,85),(x+30,150),(220,230,250,255),7)
            elif name=='ingredient_kibble':
                for x,y in [(70,90),(140,80),(100,150),(170,145)]: cv2.circle(p,(x,y),27,color,-1)
            elif name=='ingredient_pumpkin':
                cv2.ellipse(p,(120,125),(75,65),0,0,360,color,-1)
                cv2.line(p,(120,40),(120,65),(90,140,100,255),10)
            else:
                cv2.ellipse(p,(100,115),(65,45),-30,0,360,color,-1)
                cv2.line(p,(145,145),(195,195),cream,20)
        elif name=='ball':
            cv2.circle(p,(120,120),95,(147,169,222,255),-1)
            cv2.ellipse(p,(120,120),(43,95),20,0,360,(192,211,244,255),5)
        else: cv2.rectangle(p,(10,10),(230,230),cream,-1)
        return cv2.resize(p,(w,h),interpolation=cv2.INTER_AREA)
