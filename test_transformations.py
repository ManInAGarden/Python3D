import unittest
import python3d as pd
import math
from TestBase import *

class TransformTest(TestBase):

    def test_translate(self):
        tr = pd.Transformer().translateinit(10,0,0)
        tred = tr.transform(pd.Vector3(0,0,0))
        self.assertEqual(tred, pd.Vector3(10,0,0))
        tred = tr.transform(tred)
        self.assertEqual(tred, pd.Vector3(20,0,0))
        tr = pd.Transformer().translateinit(10,20,30)
        tred = tr.transform(pd.Vector3(1,2,3))
        self.assertEqual(tred, pd.Vector3(11,22,33))
        tred = tr.transform(pd.Vector3(-1,-2,-3))
        self.assertEqual(tred, pd.Vector3(9,18,27))

    

    def test_translate_series(self):
        tr = pd.Transformer().translateinit(10,10,10)
        tred = tr.transform(pd.Vector3(-10,-10,-10))
        self.assertEqual(pd.Vector3(0,0,0), tred)
        tr = tr.translateinit(1,1,1)
        tred = tr.transform(pd.Vector3(-10,-10,-10))
        self.assertEqual(pd.Vector3(1,1,1), tred)
        tr = pd.Transformer().translateinit(10,10,10).translateinit(-1,1,-5)
        tred = tr.transform(pd.Vector3(0,0,0))
        self.assertEqual(pd.Vector3(9,11,5), tred)

    def test_scale(self):
        tr = pd.Transformer().scaleinit(1,1,1)
        tred = tr.transform([12, -10, 9])
        self.assertEqual([12, -10, 9], tred)
        tr = pd.Transformer().scaleinit(10,10,10)
        tred = tr.transform([12, -10, 9])
        self.assertEqual([120, -100, 90], tred)
        tr = pd.Transformer().scaleinit(0.5,0.1,-0.1)
        tred = tr.transform([12, -10, 9])
        self.assertEqual([6, -1, -0.9], tred)


    def test_rotatex(self):
        tr = pd.Transformer().xrotinit(90)
        tred = tr.transform([0,1,0])
        exp = [0, 0, 1.0]
        for i in range(3):
            self.assertAlmostEqual(exp[i], tred[i], 10)

        tr = pd.Transformer().xrotinit(-90)
        tred = tr.transform([0,1,0])
        exp = [0, 0, -1.0]
        for i in range(3):
            self.assertAlmostEqual(exp[i], tred[i], 10)

        
    def test_rotatey(self):
        tr = pd.Transformer().yrotinit(90)
        tred = tr.transform([1,0,0])
        exp = [0, 0, -1.0]
        for i in range(3):
            self.assertAlmostEqual(exp[i], tred[i], 10)


    def test_rotatez(self):
        tr = pd.Transformer().zrotinit(90)
        tred = tr.transform([1,0,0])
        exp = [0, 1.0, 0]
        for i in range(3):
            self.assertAlmostEqual(exp[i], tred[i], 10)

    def test_mixed_series(self):
        tr = pd.Transformer().translateinit(1,0,0).scaleinit(10,10,10).zrotinit(45)
        tred = tr.transform([0, 0, 0])
        exp = [10*math.sin(math.pi/4), 10*math.sin(math.pi/4), 0]
        for i in range(3):
            self.assertAlmostEqual(exp[i], tred[i], 10)



if __name__ == "__main__":
    unittest.main()