import unittest
from math import cos,sin,pi
from utils.hand_input import InputFilter,HandInput,LandmarkInput
from utils.game_controls import DragObject,CircleStir,basket_position

class InputTests(unittest.TestCase):
    def test_press_hold_release(self):
        f=InputFilter(); f.update(.5,.5,False)
        self.assertTrue(f.update(.5,.5,True).pressed)
        self.assertFalse(f.update(.5,.5,True).pressed)
        self.assertTrue(f.update(.5,.5,False).released)
        self.assertFalse(f.update(.5,.5,False).released)
    def test_loss_is_cancel_not_drop_and_reacquisition_waits(self):
        f=InputFilter(); f.update(.3,.3,False); f.update(.3,.3,True)
        lost=f.update(tracked=False)
        self.assertTrue(lost.cancelled); self.assertFalse(lost.released)
        self.assertFalse(f.update(tracked=False).cancelled)
        self.assertFalse(f.update(.3,.3,True).pressed)
        f.update(.3,.3,False)
        self.assertTrue(f.update(.3,.3,True).pressed)
    def test_drag_returns_to_pregrab_position_on_loss(self):
        f=InputFilter(1); o=DragObject(.3,.3)
        o.update(f.update(.3,.3,False)); o.update(f.update(.3,.3,True))
        o.update(f.update(.7,.7,True)); o.update(f.update(tracked=False))
        self.assertEqual((o.x,o.y),(.3,.3)); self.assertFalse(o.held)
    def test_stir_requires_circles_not_small_oscillations(self):
        s=CircleStir()
        for i in range(200):
            a=.1 if i%2 else 0
            s.update(HandInput(True,.65+.1*cos(a),.55+.1*sin(a),True))
        self.assertLess(s.progress,.05)
        s=CircleStir()
        for i in range(150):
            a=i*.1
            s.update(HandInput(True,.65+.1*cos(a),.55+.1*sin(a),True))
        self.assertEqual(s.progress,1)
    def test_basket_freezes_without_tracking(self):
        self.assertEqual(basket_position(HandInput(),.4),.4)
    def test_pinch_hysteresis(self):
        p=[(.5,.5)]*21; p[0]=(.5,.8); p[9]=(.5,.4); p[4]=(.3,.3)
        t=LandmarkInput()
        def sample(r):
            p[8]=(.3+.4*r,.3)
            return t.update(p)
        sample(.6)
        self.assertTrue(sample(.2).pressed)
        self.assertTrue(sample(.4).pinched)
        self.assertTrue(sample(.5).released)
if __name__=='__main__': unittest.main()
