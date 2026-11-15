"""Dependency-free shared input contract. Coordinates use the displayed frame."""
from dataclasses import dataclass
from math import hypot

@dataclass(frozen=True)
class HandInput:
    tracked: bool = False
    x: float | None = None
    y: float | None = None
    pinched: bool = False
    pressed: bool = False
    released: bool = False
    points: tuple = ()
    cancelled: bool = False
    ready: bool = False
    source: str = 'hand'

class InputFilter:
    """Open once after startup/loss before a new grab is allowed."""
    def __init__(self, smoothing=.28):
        self.smoothing = smoothing
        self.input = HandInput()
        self.armed = False

    def update(self, x=None, y=None, down=False, *, tracked=True, points=(), source='hand'):
        previous = self.input
        if not tracked:
            self.armed = False
            self.input = HandInput(cancelled=previous.pinched, source=source)
            return self.input
        if x is None or y is None:
            raise ValueError('Tracked input requires x and y')
        x, y = max(0., min(1., x)), max(0., min(1., y))
        if previous.tracked:
            x = previous.x + self.smoothing * (x-previous.x)
            y = previous.y + self.smoothing * (y-previous.y)
        if not down:
            self.armed = True
        held = bool(down and self.armed)
        self.input = HandInput(True, x, y, held, held and not previous.pinched,
                               previous.pinched and not held, points, False,
                               self.armed, source)
        return self.input

class LandmarkInput:
    def __init__(self):
        self.filter = InputFilter()
        self.raw_pinched = False

    def update(self, points, aspect=1.):
        if not points:
            self.raw_pinched = False
            return self.filter.update(tracked=False)
        def distance(a,b):
            return hypot((points[a][0]-points[b][0])*aspect, points[a][1]-points[b][1])
        ratio = distance(4,8)/max(distance(0,9), .001)
        self.raw_pinched = ratio < (.45 if self.raw_pinched else .32)
        x = sum(points[i][0] for i in (0,5,9,17))/4
        y = sum(points[i][1] for i in (0,5,9,17))/4
        return self.filter.update(x,y,self.raw_pinched,points=tuple(points))
