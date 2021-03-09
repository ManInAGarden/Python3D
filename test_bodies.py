import unittest
import python3d as pd
from TestBase import *

class TestBodies(TestBase):
    def test_simple_creation(self):
        bod = pd.Body()
        cb = pd.EllipsoidElement(radx=100, rady=100, radz=100.0)
        bod.append(cb)
        numouter = 4
        for i in range(numouter):
            b = pd.EllipsoidElement(radx=10.0, rady=10, radz=10).translate(tx=100.0).rotate(pd.AxisEnum.ZAXIS, i*360.0/numouter)
            bod.append(b)

        prot = bod.rotate(pd.AxisEnum.YAXIS, 90.0)
        centreball = bod[0].element
        firstball = bod[1].element
        secondball = bod[2].element
        thirdball = bod[3].element
        fourthball = bod[4].element
        self.assertVectAlmostEqual([0,0,0], centreball._cent)
        self.assertVectAlmostEqual([100.0, 0.0, 0.0], firstball._cent)
        self.assertVectAlmostEqual([0.0, 100.0, 0.0], secondball._cent)
        self.assertVectAlmostEqual([-100.0, 0.0, 0.0], thirdball._cent)
        self.assertVectAlmostEqual([0.0, -100.0, 0.0], fourthball._cent)

        centreball = prot[0].element
        firstball = prot[1].element
        secondball = prot[2].element
        thirdball = prot[3].element
        fourthball = prot[4].element
        self.assertVectAlmostEqual([0,0,0], centreball._cent)
        self.assertVectAlmostEqual([0.0, 0.0, -100.0], firstball._cent)
        self.assertVectAlmostEqual([0.0, 100.0, 0.0], secondball._cent)
        self.assertVectAlmostEqual([0.0, 0.0, 100.0], thirdball._cent)
        self.assertVectAlmostEqual([0.0, -100.0, 0.0], fourthball._cent)
        

if __name__ == "__main__":
    unittest.main()