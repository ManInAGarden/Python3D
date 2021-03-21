from python3d.Polygons import Ellipse2, EllipticArc2, Line2, Polygon2, Vector3
from TestBase import *
import unittest
import python3d as pd
import math

class ElementTest(TestBase):

    def test_balls(self):
        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).translate(tx = 10.0)
        self.assertEqual(pd.Vector3.newFromXYZ(10.0, 0.0, 0.0), b._cent)
        self.assertMatrAlmostEqual([[10.0, 0.0, 0.0],[0.0, 20.0, 0.0], [0.0, 0.0, 10.0]], b._dimensions)

        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).translate(tx = 10.0).translate(ty=-100.0)
        self.assertEqual(pd.Vector3.newFromXYZ(10.0, -100.0, 0.0), b._cent)
        self.assertMatrAlmostEqual([[10.0, 0.0, 0.0],[0.0, 20.0, 0.0], [0.0, 0.0, 10.0]], b._dimensions)

        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).scale(sz = 10.0)
        self.assertEqual(pd.Vector3.newFromXYZ(0.0, 0.0, 0.0), b._cent)
        self.assertMatrAlmostEqual([[10.0, 0.0, 0.0],[0.0, 20.0, 0.0], [0.0, 0.0, 100.0]], b._dimensions)

        b = pd.EllipsoidElement(radx = 10, rady=20, radz=10).translate(tx=10.0).scale(sz = 10.0)
        self.assertEqual(pd.Vector3.newFromXYZ(10.0, 0.0, 0.0), b._cent)
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
        self.assertAlmostEqual(50.0, cyl._r)

        cyl = pd.CylinderElement(lx=0, ly=0, lz=10, r=5).scale(10,10,10).rotate(pd.AxisEnum.YAXIS, 45)
        self.assertVectAlmostEqual([0,0,0], cyl._cent)
        fact = math.sin(math.pi/4)
        self.assertVectAlmostEqual([fact*100,0,fact*100], cyl._l)
        self.assertAlmostEqual(50.0, cyl._r)

    def test_sketched(self):
        skel = pd.SketchedElement(extr=10)
        l = Line2(pd.Vector2.newFromXY(0,0),
            pd.Vector2.newFromXY(0,1),
            pd.Vector2.newFromXY(1,1),
            pd.Vector2.newFromXY(0,0))
        skel.add_poly(Polygon2.newFromSketch(l))
        
        skelscal = skel.scale(10,10,5)
        self.assertAlmostEqual(skel._extr*5, skelscal._extr) #just scaled in z times 5 with no rotation and no translation
        self.assertAllPolysAlmostEqual(skel._polygons, skelscal._polygons) #polygons are not touched by tranformations
        self.assertVectAlmostEqual(skel._cent, skelscal._cent)
        
        skelrot = skel.rotate(pd.AxisEnum.ZAXIS, 45)
        self.assertAlmostEqual(skel._extr*5, skelscal._extr) #rotation does not touch extrusion factor
        self.assertAllPolysAlmostEqual(skel._polygons, skelscal._polygons) #polygons are not touched by tranformations
        #check for rotation of dims by 45deg
        xrotfact = math.cos(math.pi/4)
        yrotfact = math.sin(math.pi/4)
        self.assertMatrAlmostEqual([[xrotfact, yrotfact,0],[-xrotfact, yrotfact,0],[0,0,1]], skelrot._dimensions)
        self.assertVectAlmostEqual(skel._cent, skelscal._cent) #rotation of (0,0,0) does nothing
        
        skeltrans = skel.translate(10, 20, 30)
        self.assertVectAlmostEqual(Vector3.newFromXYZ(10,20,30), skeltrans._cent)
        self.assertMatrAlmostEqual(skel._dimensions, skeltrans._dimensions) #translation does nothing to dimensions
        self.assertAlmostEqual(skel._extr, skeltrans._extr)
        self.assertAllPolysAlmostEqual(skel._polygons, skeltrans._polygons) #polygons are not touched by tranformations

    def test_sketched2(self):
        corner1 = pd.Vector2.newFromXY(-10, -10)
        corner2 = pd.Vector2.newFromXY( 10, -10)
        corner3 = pd.Vector2.newFromXY( 10,  10)
        corner4 = pd.Vector2.newFromXY(-10,  10)
        arcr = 3.0
        arcrv = pd.Vector2.newFromXY(arcr, arcr)
        arc1 = EllipticArc2(corner1, arcrv, 180, 270, 20)
        l12 = Line2(corner1 + pd.Vector2.newFromXY(0,-arcr),
            corner2 + pd.Vector2.newFromXY(0, -arcr))
        arc2 = EllipticArc2(corner2, arcrv, 270, 360, 20)
        l23 = Line2(corner2 + pd.Vector2.newFromXY(arcr,0),
            corner3 + pd.Vector2.newFromXY(arcr, 0))
        arc3 = EllipticArc2(corner3, arcrv, 0, 90, 20)
        l34 = Line2(corner3 + pd.Vector2.newFromXY(0,arcr),
            corner4 + pd.Vector2.newFromXY(0,arcr))
        arc4 = EllipticArc2(corner4, arcrv, 90, 180, 20)
        l41 = Line2(corner4 + pd.Vector2.newFromXY(-arcr,0),
            corner1 + pd.Vector2.newFromXY(-arcr,0))
        skel = pd.SketchedElement(extr=10)
        skel.add_poly(Polygon2.newFromSketch(arc1, l12, arc2, l23, arc3, l34, arc4, l41))
        self.assertEqual(len(skel._polygons), 1)
        self.assertEqual(len(skel._polygons[0].vertices), 4*6 + 4*2) #4 arcs in qual 20 (6 vertices) and 4 lines with tow vertices each


if __name__ == "__main__":
    unittest.main()