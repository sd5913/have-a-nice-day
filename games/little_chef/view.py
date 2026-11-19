"""Chef drawing is independent from rules; PNG replacement remains supported."""
from math import sin
from collections import Counter
import cv2

def draw_chef(v,g,status):
    w,h=960,640; c=v.background(w,h)
    def text(t,x,y,s=.6,color=(65,70,80)): cv2.putText(c,t,(x,y),cv2.FONT_HERSHEY_SIMPLEX,s,color,1,cv2.LINE_AA)
    def sprite(n,x,y,ww,hh): v.draw(c,n,(x*w,y*h),(ww,hh))
    text('LITTLE CAT CHEF',28,35,.85)
    text('BOND: '+str(g.affection),640,35,.65)
    text('M mouse / H hand / R reset / Enter action / Q quit',28,67,.5)
    text(status,28,96,.5)
    text('TODAY / ORDER '+str(g.round_index+1)+': '+ ' | '.join(n+' x'+str(q) for n,q in Counter(g.recipe).items()),28,135,.55)
    text('Stage: '+g.stage.upper(),28,163,.5)
    for i,name in enumerate(g.names):
        item=g.items[name]
        cv2.rectangle(c,(int(item.home[0]*w)-65,int(item.home[1]*h)-42),(int(item.home[0]*w)+65,int(item.home[1]*h)+47),(244,248,250),-1)
        sprite('ingredient_'+name.lower(),item.x,item.y,75,52)
        text(name,int(item.home[0]*w)-33,int(item.home[1]*h)+39,.5)
    sprite('bowl',*g.bowl,235,150)
    if g.stage=='stir':
        color=(85,170,85) if g.last_stir else (100,145,220)
        for angle in range(0,360,24):
            cv2.ellipse(c,(int(g.bowl[0]*w),int(g.bowl[1]*h)),(96,64),0,angle,angle+12,color,2)
        text('HAND OK' if g.last_stir else 'FINGERS TOGETHER',340,390,.55,color)

    for i,name in enumerate(g.added):
        sprite('ingredient_'+name.lower(),g.bowl[0]-.06+(i%4)*.04,g.bowl[1]-.035+(i//4)*.025,34,25)
    sprite('cat',g.cat_x,g.cat_y,145,160)
    # Independent motion and expressive overlays also work for replacement static PNGs.
    x,y=int(g.cat_x*w),int(g.cat_y*h)
    if g.stage in ('ingredients','stir'):
        if int(g.elapsed*3)%14==0:
            cv2.line(c,(x-26,y-14),(x-10,y-14),(70,75,85),3)
            cv2.line(c,(x+10,y-14),(x+26,y-14),(70,75,85),3)
        text('sniff...' if g.cat_mood=='sniff' else '?',x-18,y-90,.6)
    if g.stage=='approach': text('Coming!',x-45,y-86,.65)
    if g.stage=='eat': text('nom nom...',x-45,y-84,.6)
    if g.stage=='result':
        text('<3' if g.correct else '...',x-22,y-90,.8)
        text('PURRR! I LOVE IT!' if g.correct else 'A DIFFERENT FLAVOUR...',240,360,.8)
        text(g.reaction[:80],190,397,.55)
    if g.stage in ('stir','ready','approach','eat','result'):
        cv2.rectangle(c,(315,521),(650,535),(205,215,215),-1)
        cv2.rectangle(c,(315,521),(315+int(335*g.stir.progress),535),(140,182,155),-1)
        text('MIX '+str(int(g.stir.progress*100))+'%',690,535,.5)
    labels={'ingredients':'MIX INGREDIENTS','ready':'CALL CAT','result':'NEW ORDER'}
    if g.stage in labels:
        cv2.rectangle(c,(336,563),(653,620),(172,203,184),-1)
        text(labels[g.stage],380,600,.65)
    text(g.message[:115],28,555,.47)
    text('In bowl: '+(' | '.join(n+' x'+str(q) for n,q in Counter(g.added).items()) or 'nothing yet'),28,498,.43)
    if g.stage=='ingredients': text('Pick any tray. Backspace: undo last ingredient',28,178,.43)
    return c
