"""Interactive fridge and low-table scene with independent food/cat sprites."""
from collections import Counter
from math import sin,cos
import cv2
import numpy as np
from .kitchen import rounded,CREAM,PAPER,INK,SAGE,OLIVE,WOOD


def draw_chef(v,g,status):
    c=np.full((640,960,3),PAPER,np.uint8)
    if 'background' in v.images:
        c[40:580]=cv2.resize(v.images['background'][:,:,:3],(960,540))
    def text(t,x,y,s=.4,color=INK,th=1):cv2.putText(c,t,(int(x),int(y)),cv2.FONT_HERSHEY_SIMPLEX,s,color,th,cv2.LINE_AA)
    def centered(t,x,y,s=.4,color=INK):
        width=cv2.getTextSize(t,cv2.FONT_HERSHEY_SIMPLEX,s,1)[0][0];text(t,x-width/2,y,s,color)
    def sprite(n,x,y,ww,hh):v.draw(c,n,(x*960,y*640),(ww,hh))
    text('little cat chef',20,28,.7,INK,2)
    text('BOND '+str(g.affection),480,26,.48,OLIVE)
    text('H hand / M mouse / R retry / Q exit',640,25,.37)
    # Order pinned to wall between fridge and window.
    rounded(c,(330,67),(686,144),PAPER,12)
    text("TODAY'S ORDER  #"+str(g.round_index+1).zfill(2),345,89,.39,OLIVE)
    order=list(Counter(g.recipe).items())
    for i,(n,q) in enumerate(order):text(n+' x'+str(q),345+(i%2)*170,111+(i//2)*22,.43)
    # Seven sources sit in the pictured dishes; salmon gets an extra tabletop plate.
    cv2.ellipse(c,(792,370),(39,9),0,0,360,CREAM,-1,cv2.LINE_AA)
    for name,item in g.items.items():
        x,y=item.home
        if name!=g.held:sprite('ingredient_'+name.lower(),x,y,79 if name in ('Fish','Chicken') else 56,48 if name in ('Fish','Chicken') else 38)
        centered(name,x*960,y*640+28,.31)
    # Contents in the existing illustrated bowl, with no second bowl layered over it.
    for i,name in enumerate(g.added):
        sprite('ingredient_'+name.lower(),g.bowl[0]-.05+(i%4)*.034,g.bowl[1]-.005+(i//4)*.018,31,22)
    if g.stage=='stir':
        color=OLIVE if g.last_stir else WOOD
        for a in range(0,360,24):cv2.ellipse(c,(int(g.bowl[0]*960),int(g.bowl[1]*640)),(84,48),0,a,a+12,color,2,cv2.LINE_AA)
    # Pace below the table; reverse the sprite when changing direction.
    if g.stage in ('ingredients','stir','ready'):
        cat_x=.59+.13*sin(g.elapsed*.7);cat_y=.785+.006*sin(g.elapsed*7)
        facing_right=cos(g.elapsed*.7)>=0
    else:
        cat_x=.59;cat_y=.785+.008*sin(g.elapsed*(10 if g.stage=='eat' else 4));facing_right=True
    img=v.images.get('cat')
    if img is not None:
        # Cache both orientations without touching the source asset.
        if 'cat_left' not in v.images:v.images['cat_left']=cv2.flip(img,1)
        sprite('cat' if facing_right else 'cat_left',cat_x,cat_y,193,140)
    else:sprite('cat',cat_x,cat_y,170,130)
    mood={'ingredients':'What is cooking?','stir':'Smells good!','ready':'Call me when ready!','approach':'Coming!','eat':'nom nom...','result':'PURRR! Bond +1' if g.correct else 'Thanks for cooking!'}[g.stage]
    rounded(c,(int(cat_x*960)-91,415),(int(cat_x*960)+91,443),PAPER,12)
    centered(mood,cat_x*960,434,.35)
    # Serve a sample at floor height so the cat can taste without teleporting onto table.
    if g.stage in ('approach','eat','result'):
        sprite('bowl',.73,.83,87,49)
        if g.stage!='result':
            sprite('ingredient_'+g.added[0].lower(),.73,.815,26,18)
    if g.held:
        item=g.items[g.held];sprite('ingredient_'+g.held.lower(),item.x,item.y,79,52)
    # Left bottom instruction card and stage feedback.
    rounded(c,(18,449),(265,550),PAPER,12)
    stage={'ingredients':'01 / CHOOSE INGREDIENTS','stir':'02 / MIX THE BOWL','ready':'03 / READY TO SERVE','approach':'03 / CAT IS COMING','eat':'03 / TASTE TEST','result':'04 / LITTLE MOMENT'}[g.stage]
    text(stage,30,471,.37,OLIVE)
    if g.stage=='ingredients':
        text('Drag food from fridge or table.',30,492,.33)
        text('Backspace: undo last portion.',30,510,.33)
    elif g.stage=='stir':
        text('Fingers together, circle the bowl.',30,492,.32)
        rounded(c,(30,505),(249,516),CREAM,5)
        if g.stir.progress>0:rounded(c,(30,505),(30+max(10,int(219*g.stir.progress)),516),SAGE,5)
    elif g.stage=='result':text('Just right! +1 bond' if g.correct else 'No bond lost. Try a new order!',30,493,.33)
    else:text('A meal made with care.',30,493,.35)
    text('IN BOWL: '+str(len(g.added))+' portions',30,535,.34)
    labels={'ingredients':'MIX INGREDIENTS','ready':'CALL CAT','result':'NEW ORDER'}
    if g.stage in labels:
        rounded(c,(336,567),(653,620),OLIVE,23);centered(labels[g.stage],494,600,.55,PAPER)
    else:centered('KEEP STIRRING' if g.stage=='stir' else 'A LITTLE TASTE TEST...',494,600,.43,OLIVE)
    text('BACKSPACE undo',19,604,.31)
    text(status[:92],19,635,.29)
    if g.stage=='ingredients' and ('first' in g.message or 'Drop the' in g.message):
        centered(g.message,492,559,.34)
    return c
