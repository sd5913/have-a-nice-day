import tempfile
import unittest
from pathlib import Path
import cv2
import numpy as np
from utils.visuals import Visuals

class VisualTests(unittest.TestCase):
    def test_alpha_and_edge_clipping(self):
        with tempfile.TemporaryDirectory() as d:
            p=np.zeros((20,20,4),dtype=np.uint8); p[:]=(0,0,200,128)
            cv2.imwrite(str(Path(d)/'cat.png'),p)
            v=Visuals(d); c=np.zeros((30,30,3),dtype=np.uint8)
            v.draw(c,'cat',(0,0),(20,20))
            self.assertIn(int(c[2,2,2]),(100,))
            self.assertEqual(int(c[20,20,2]),0)
    def test_missing_and_corrupt_use_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'cat.png').write_bytes(b'not a picture')
            v=Visuals(d); c=v.background(960,640)
            v.draw(c,'cat',(500,300),(150,170))
            self.assertEqual(c.shape,(640,960,3))
            self.assertTrue(v.cache[('cat',150,170)][:,:,3].any())
