from TestBase import *
import unittest
import python3d as pd
import math

class ElementTest(TestBase):

    def test_balls(self):
        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).translate(tx = 10.0)
        self.assertEqual(pd.Vector3([10.0, 0.0, 0.0]), b._cent)
        self.assertMatrAlmostEqual([[10.0, 0.0, 0.0],[0.0, 20.0, 0.0], [0.0, 0.0, 10.0]], b._dimensions)

        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).translate(tx = 10.0).translate(ty=-100.0)
        self.assertEqual(pd.Vector3([10.0, -100.0, 0.0]), b._cent)
        self.assertMatrAlmostEqual([[10.0, 0.0, 0.0],[0.0, 20.0, 0.0], [0.0, 0.0, 10.0]], b._dimensions)

        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).scale(sz = 10.0)
        self.assertEqual(pd.Vector3([0.0, 0.0, 0.0]), b._cent)
        self.assertMatrAlmostEqual([[10.0, 0.0, 0.0],[0.0, 20.0, 0.0], [0.0, 0.0, 100.0]], b._dimensions)

        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).translate(tx=10.0).scale(sz = 10.0)
        self.assertEqual(pd.Vector3([10.0, 0.0, 0.0]), b._cent)
        self.assertMatrAlmostEqual([[10.0, 0.0, 0.0],[0.0, 20.0, 0.0], [0.0, 0.0, 100.0]], b._dimensions)

        b = pd.EllipsoidElement(radx = 10, rady=20, radz=5).rotate(pd.AxisEnum.ZAXIS, 90)
        self.assertVectAlmostEqual([0.0, 0.0, 0.0], b._cent)
        self.assertMatrAlmostEqual([[0.0, 10.0, 0.0],[-20.0, 0.0, 0.0],[0.0, 0.0, 5.0]], b._dimensions)

    def test_boxes(self):
        b = pd.BoxElement(xlength=10, ylength=20, zlength=30).translate(100,100,100)
        self.assertVectAlmostEqual([100, 100, 100], b._cent)
        self.assertMatrAlmostEqual([[10,0,0],[0,20,0],[0,0,30]], b._dimensions)

    def test_cylinders(self):
        cyl = pd.CylinderElement(lx=0, ly=0, lz=10, r=5).scale(10,10,10)
        self.assertVectAlmostEqual([0,0,0], cyl._cent)
        self.assertVectAlmostEqual([0,0,100], cyl._l)
        self.assertVectAlmostEqual(50.0, cyl._r)

        cyl = pd.CylinderElement(lx=0, ly=0, lz=10, r=5).scale(10,10,10).rotate(pd.AxisEnum.YAXIS, 45)
        self.assertVectAlmostEqual([0,0,0], cyl._cent)
        fact = math.sin(math.pi/4)
        self.assertVectAlmostEqual([fact*100,0,fact*100], cyl._l)
        self.assertVectAlmostEqual(50.0, cyl._r)


if __name__ == "__main__":
    unittest.main()