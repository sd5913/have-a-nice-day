"""Chef rules without graphics dependencies. Recipe quantities are toy-game rules."""
from dataclasses import replace
from math import hypot, sin, cos
from utils.game_controls import DragObject, CircleStir

def stirring_hand(hand):
    """Allow a closed finger bundle OR extended fingers held together.

    Two-dimensional approximation only; thumb placement is deliberately flexible.
    Camera recognition still needs validation against real hands.
    """
    if not hand.tracked: return False
    if hand.source=='mouse': return hand.pinched
    p=hand.points
    if len(p)!=21: return False
    def dist(a,b): return hypot(p[a][0]-p[b][0],p[a][1]-p[b][1])
    scale=max(dist(0,9),.001)
    # Ignore thumb when measuring finger spacing: tucking it across the palm is OK.
    fingers=(8,12,16,20)
    gaps=[dist(a,b)/scale for a,b in zip(fingers,fingers[1:])]
    extended=sum(dist(0,i)>dist(0,j)*1.12 for i,j in ((8,6),(12,10),(16,14),(20,18)))>=3
    together=max(gaps)<.65 and dist(8,20)/scale<1.35
    tips=[p[i] for i in (4,8,12,16,20)]
    cx=sum(x for x,y in tips)/5; cy=sum(y for x,y in tips)/5
    bundled=max(hypot(x-cx,y-cy) for x,y in tips)/scale<.85
    return bundled or (extended and together)

class ChefGame:
    names=('Fish','Chicken','Kibble','Pumpkin','Carrot','Peas','Rice','Salmon')
    recipes=(('Fish','Chicken','Kibble'),('Salmon','Salmon','Pumpkin'),('Chicken','Rice','Carrot','Peas'),('Fish','Kibble','Pumpkin','Pumpkin'))
    def __init__(self,round_index=0,affection=0):
        self.affection=affection
        self.round_index=round_index; self.recipe=self.recipes[round_index%len(self.recipes)]
        self.items={n:DragObject(.10+(i%4)*.205,.33+(i//4)*.18,.065) for i,n in enumerate(self.names)}
        self.bowl=(.55,.72); self.added=[]; self.stage='ingredients'
        self.stir=CircleStir(self.bowl,2); self.held=None
        self.message='Cat wants: '+', '.join(self.recipe)
        self.elapsed=0.; self.stage_time=0.; self.reaction=''; self.correct=False
        self.cat_x=.88; self.cat_y=.67; self.cat_mood='curious'
        self.last_stir=False; self.stir_grace=0.

    def remove_last(self):
        if self.stage=='ingredients' and self.added and not self.held:
            name=self.added.pop()
            self.message='Removed '+name+'. Adjust your meal before mixing.'

    def activate_button(self):
        """UI command independent of camera/mouse motion source."""
        if self.stage=='ingredients':
            if self.held:
                self.message='Drop the ingredient before starting to mix.'
            elif len(self.added)<2:
                self.message='Add at least two ingredients into the bowl first.'
            else:
                self.stage='stir'; self.stage_time=0
                self.message='Fingers together, then follow the dotted oval.'
        elif self.stage=='ready':
            self.stage='approach'; self.stage_time=0
            self.message='Here comes your little taste tester!'
        elif self.stage=='result':
            self.__init__(self.round_index+1,self.affection)

    def update(self,hand,dt):
        # Lost input pauses all animation/timers and cancels a held ingredient.
        if not hand.tracked and self.stage not in ('approach','eat','result'):
            if self.held:
                self.items[self.held].update(hand); self.held=None
            self.stir.last=None; self.last_stir=False; self.stir_grace=0.
            self.message='Paused: show your hand, or press M for mouse.'
            return
        dt=max(0,min(dt,.1)); self.elapsed+=dt; self.stage_time+=dt
        if self.stage=='ingredients':
            self.cat_x=.88-.08*min(1,len(self.added)/3)
            self.cat_y=.67+.008*sin(self.elapsed*2)
            if self.held:
                item=self.items[self.held]; event=item.update(hand)
                if event=='drop':
                    name=self.held
                    if hypot((item.x-self.bowl[0])/1.35,item.y-self.bowl[1])<.115:
                        self.added.append(name); self.message=name+' added! Backspace removes the last ingredient.'
                        self.cat_mood='sniff'
                    else: self.message='Outside the bowl. Try again.'
                    item.x,item.y=item.home; self.held=None
                elif event=='cancel': self.held=None
            elif hand.pressed:
                for name,item in self.items.items():
                    item.update(hand)
                    if item.held: self.held=name; break
                if .35<hand.x<.68 and .88<hand.y<.97:
                    self.activate_button()
            # Feedback is observable without requiring assets: bob, blink, look at hand.
        elif self.stage=='stir':
            detected=stirring_hand(hand)
            self.stir_grace=.18 if detected else max(0.,self.stir_grace-dt)
            active=detected or self.stir_grace>0
            self.last_stir=active
            value=self.stir.update(replace(hand,pinched=active))
            self.cat_x=.80; self.cat_y=.67+.01*sin(self.elapsed*3)
            self.cat_mood='watching'
            near=.04<hypot(hand.x-self.bowl[0],hand.y-self.bowl[1])<.20
            self.message=('STIR GESTURE OK - follow the dotted oval.' if near else 'GESTURE OK - move cursor onto the dotted oval.') if active else 'Keep four fingers straight and together; thumb relaxed. Face camera.'
            if value>=1:
                self.stage='ready'; self.stage_time=0; self.message='Meal ready! Press CALL CAT.'
        elif self.stage=='ready':
            self.cat_mood='waiting'
            if hand.pressed and .35<hand.x<.68 and .88<hand.y<.97:
                self.activate_button()
        elif self.stage=='approach':
            self.cat_x=.80-.12*min(1,self.stage_time/1.4)
            self.cat_y=.67+.012*sin(self.elapsed*12)
            if self.stage_time>=1.4: self.stage='eat'; self.stage_time=0
        elif self.stage=='eat':
            self.cat_mood='eating'; self.cat_y=.68+.012*sin(self.elapsed*9)
            self.message='Nom nom...'
            if self.stage_time>=2:
                self.stage='result'; self.stage_time=0
                self.correct=sorted(self.added)==sorted(self.recipe)
                from collections import Counter
                wanted,actual=Counter(self.recipe),Counter(self.added)
                missing=list((wanted-actual).elements())
                extras=list((actual-wanted).elements())
                if self.correct:
                    self.affection+=1
                    self.reaction='PURRR! Exactly what I wanted! Bond +1'; self.cat_mood='love'
                elif not missing: self.reaction='Tasty, but a little too much!'; self.cat_mood='full'
                else: self.reaction='Hmm... '+('Missing '+', '.join(missing) if missing else 'An unexpected extra ingredient')
        elif self.stage=='result':
            self.message=self.reaction
            self.cat_y=.67+(.015*abs(sin(self.elapsed*5)) if self.correct else .005*sin(self.elapsed*2))
            if hand.pressed and .35<hand.x<.68 and .88<hand.y<.97:
                self.activate_button()
