"""Game-specific helpers; no camera, MediaPipe or drawing dependencies."""
from math import atan2, hypot, pi

class DragObject:
    def __init__(self, x, y, radius=.08):
        self.home=(x,y); self.x=x; self.y=y; self.radius=radius
        self.held=False; self.offset=(0,0); self.start=self.home

    def update(self, hand):
        if hand.cancelled or not hand.tracked:
            if self.held: self.x,self.y=self.start
            self.held=False
            return 'cancel' if hand.cancelled else None
        if hand.pressed and hypot(hand.x-self.x,hand.y-self.y)<=self.radius:
            self.held=True; self.start=(self.x,self.y)
            self.offset=(self.x-hand.x,self.y-hand.y)
        if self.held:
            self.x=max(0,min(1,hand.x+self.offset[0]))
            self.y=max(0,min(1,hand.y+self.offset[1]))
            if hand.released:
                self.held=False
                return 'drop'
        return None

class CircleStir:
    """Accumulate deliberate circles; reset continuity on release/loss/outside bowl."""
    def __init__(self, center=(.65,.55), turns=2):
        self.center=center; self.target=turns*2*pi
        self.total=0.; self.last=None; self.direction=0

    def update(self, hand):
        if not hand.tracked or not hand.pinched or hand.cancelled:
            self.last=None; return self.progress
        dx,dy=hand.x-self.center[0],hand.y-self.center[1]
        if not .04<hypot(dx,dy)<.20:
            self.last=None; return self.progress
        angle=atan2(dy,dx)
        if self.last is not None:
            delta=(angle-self.last+pi)%(2*pi)-pi
            if .004<abs(delta)<.6:
                direction=1 if delta>0 else -1
                if self.direction==0: self.direction=direction
                # Reversing subtracts work, so small back-and-forth cannot finish.
                self.total=max(0,self.total+delta*self.direction)
        self.last=angle
        return self.progress

    @property
    def progress(self): return min(1.,self.total/self.target)

def basket_position(hand, previous=.5):
    return max(.08,min(.92,hand.x)) if hand.tracked else previous
