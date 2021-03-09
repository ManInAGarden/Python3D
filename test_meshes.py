from TestBase import *
import unittest
import python3d as pd
import math

class ElementTest(TestBase):
    def test_boxmesh(self):
        m = pd.Mesh()
        box = pd.BoxElement(xlength=10, ylength=20, zlength=30).rotate(pd.AxisEnum.XAXIS, 45).rotate(pd.AxisEnum.YAXIS, 45)
        m.addelement(box)
        self.assertEqual(8, len(m._vertices))
        self.assertEqual(12, len(m._triangles))

    def test_ballmesh(self):
        m = pd.Mesh()
        ball = pd.BallElement(10.0, 20.0, 30.0)
        m.addelement(ball)

if __name__ == "__main__":
    unittest.main()


