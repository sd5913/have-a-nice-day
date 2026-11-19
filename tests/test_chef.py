import unittest
from math import sin,cos
from utils.hand_input import InputFilter,HandInput
from games.little_chef.game import ChefGame,stirring_hand

class ChefTests(unittest.TestCase):
    def add(self,g,f,name):
        o=g.items[name]
        g.update(f.update(o.x,o.y,False,source='mouse'),.02)
        g.update(f.update(o.x,o.y,True,source='mouse'),.02)
        g.update(f.update(*g.bowl,True,source='mouse'),.02)
        g.update(f.update(*g.bowl,False,source='mouse'),.02)
    def click(self,g,f,x=.5,y=.92):
        g.update(f.update(x,y,False,source='mouse'),.02)
        g.update(f.update(x,y,True,source='mouse'),.02)
    def test_complete_recipe_to_reaction_and_replay(self):
        g=ChefGame(); f=InputFilter(1)
        for name in g.recipe: self.add(g,f,name)
        self.click(g,f); self.assertEqual(g.stage,'stir')
        for i in range(160):
            a=i*.1; g.update(f.update(g.bowl[0]+.1*cos(a),g.bowl[1]+.1*sin(a),True,source='mouse'),.02)
        self.assertEqual(g.stage,'ready')
        self.click(g,f); self.assertEqual(g.stage,'approach')
        for i in range(50): g.update(f.update(.4,.5,False,source='mouse'),.1)
        self.assertEqual(g.stage,'result'); self.assertTrue(g.correct)
        self.click(g,f); self.assertEqual(g.stage,'ingredients'); self.assertEqual(g.added,[])
    def test_loss_returns_food_and_pauses(self):
        g=ChefGame(); f=InputFilter(1); o=g.items['Fish']
        g.update(f.update(o.x,o.y,False),.1); g.update(f.update(o.x,o.y,True),.1)
        elapsed=g.elapsed
        g.update(f.update(tracked=False),.1)
        self.assertIsNone(g.held); self.assertEqual(g.elapsed,elapsed); self.assertEqual(g.added,[])
        self.assertEqual((o.x,o.y),o.home)
    def test_empty_bowl_cannot_advance(self):
        g=ChefGame(); self.click(g,InputFilter(1)); self.assertEqual(g.stage,'ingredients')
    def test_mismatched_recipe_gives_different_result(self):
        g=ChefGame(); g.added=['Pumpkin','Pumpkin']; g.stage='eat'; g.stage_time=2
        g.update(HandInput(True,.5,.5),.1)
        self.assertFalse(g.correct); self.assertIn('Missing',g.reaction)
    def test_grouped_fingers_and_mouse_override(self):
        self.assertTrue(stirring_hand(HandInput(True,.5,.5,True,source='mouse')))
        self.assertFalse(stirring_hand(HandInput(True,.5,.5,True)))
        p=[(.5,.5)]*21; p[0]=(.5,.9);p[9]=(.5,.6);p[5]=(.3,.6);p[17]=(.7,.6)
        for i in (4,8,12,16,20):p[i]=(.5,.4)
        self.assertTrue(stirring_hand(HandInput(True,.5,.5,points=tuple(p))))
        p[20]=(.9,.1)
        self.assertFalse(stirring_hand(HandInput(True,.5,.5,points=tuple(p))))

class StraightFingerTests(unittest.TestCase):
    def test_straight_together_with_thumb_tucked(self):
        p=[(.5,.6)]*21
        p[0]=(.5,.9); p[9]=(.5,.65)
        for tip,pip,x in ((8,6,.43),(12,10,.48),(16,14,.53),(20,18,.58)):
            p[tip]=(x,.30);p[pip]=(x,.47)
        p[4]=(.38,.65)
        self.assertTrue(stirring_hand(HandInput(True,.5,.5,points=tuple(p))))
        for tip,x in ((8,.12),(12,.37),(16,.65),(20,.95)):p[tip]=(x,.3)
        self.assertFalse(stirring_hand(HandInput(True,.5,.5,points=tuple(p))))

class ButtonTests(unittest.TestCase):
    def test_direct_button_without_hand(self):
        g=ChefGame(); g.activate_button()
        self.assertEqual(g.stage,'ingredients')
        g.added=['Fish','Chicken'];g.activate_button()
        self.assertEqual(g.stage,'stir')
        g.stage='ready';g.activate_button()
        self.assertEqual(g.stage,'approach')
        g.stage='result';g.activate_button()
        self.assertEqual(g.stage,'ingredients')

class IndependentReactionTests(unittest.TestCase):
    def test_cat_finishes_without_player_hand(self):
        g=ChefGame();g.added=list(g.recipe);g.stage='ready'
        g.activate_button()
        for i in range(50):g.update(HandInput(),.1)
        self.assertEqual(g.stage,'result')
        self.assertTrue(g.correct)
        self.assertIn('PURRR',g.message)
        self.assertAlmostEqual(g.cat_x,.68)

class OrderQuantityTests(unittest.TestCase):
    def test_duplicate_portion_missing_is_reported(self):
        g=ChefGame(1)
        g.added=['Salmon','Pumpkin']; g.stage='eat'; g.stage_time=2
        g.update(HandInput(),.1)
        self.assertFalse(g.correct)
        self.assertIn('Missing Salmon',g.reaction)
    def test_undo_only_before_mixing(self):
        g=ChefGame(); g.added=['Fish','Chicken']; g.remove_last()
        self.assertEqual(g.added,['Fish'])
        g.stage='stir'; g.remove_last()
        self.assertEqual(g.added,['Fish'])


class AffectionTests(unittest.TestCase):
    def test_correct_meal_awards_once_and_replay_keeps_bond(self):
        g=ChefGame(affection=3); g.added=list(g.recipe); g.stage='eat'; g.stage_time=2
        g.update(HandInput(),.1)
        self.assertEqual(g.affection,4)
        for _ in range(20): g.update(HandInput(),.1)
        self.assertEqual(g.affection,4)
        g.activate_button()
        self.assertEqual(g.affection,4)
    def test_incorrect_meal_does_not_reduce_bond(self):
        g=ChefGame(affection=3); g.added=['Pumpkin']; g.stage='eat'; g.stage_time=2
        g.update(HandInput(),.1)
        self.assertEqual(g.affection,3)
