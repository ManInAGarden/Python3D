from python3d.ElementClasses import Transformer
from python3d.Polygons import Ellipse2, EllipticArc2, Line2, Polygon2, Vector3
from TestBase import *
import unittest
import python3d as pd
import math

class ElementTest(TestBase):

    def test_balls(self):
        b = pd.EllipsoidElement(rx = 10, ry=20, rz=10).translate(tx = 10.0)
        tr = Transformer().translateinit(10,0,0)
        self.assertEqual(b._transf, tr)

        b = pd.EllipsoidElement(rx = 10, ry=20, rz=10).translate(tx = 10.0).translate(ty=-100.0)
        tr = Transformer().translateinit(10,-100,0)
        self.assertEqual(b._transf, tr)

        b = pd.EllipsoidElement(rx = 10, ry=20, rz=10).scale(sz = 10.0)
        tr = Transformer().scaleinit(1,1,10)
        self.assertEqual(b._transf, tr)

        b = pd.EllipsoidElement(rx = 10, ry=20, rz=10).translate(tx=10.0).scale(sz = 10.0)
        tr1 = Transformer().translateinit(10,0,0)
        tr2 = Transformer().scaleinit(1,1,10)
        self.assertEqual(b._transf, tr1 + tr2)

        b = pd.EllipsoidElement(rx = 10, ry=20, rz=5).rotate(pd.AxisEnum.ZAXIS, 90)
        tr = Transformer().zrotinit(90)
        self.assertEqual(b._transf, tr)


    def test_boxes(self):
        b = pd.BoxElement(xlength=10, ylength=20, zlength=30).translate(100,100,100)
        self.assertVectAlmostEqual([100, 100, 100], b._cent)
        self.assertMatrAlmostEqual([[10,0,0],[0,20,0],[0,0,30]], b._dimensions)

    def test_cylinders(self):
        cyl = pd.CylinderElement(rx=5, ry=5, l=10).scale(10,10,10)
        ttr = Transformer().scaleinit(10,10,10)
        self.assertEqual(ttr, cyl._transf)

        cyl = pd.CylinderElement(rx=5, ry=5, l=10).scale(10,10,10).rotate(pd.AxisEnum.YAXIS, 45)
        tts = Transformer().scaleinit(10,10,10)
        ttr = Transformer().yrotinit(45)
        tts.addtrans(ttr._tmat)
        self.assertEqual(tts, cyl._transf)

    def test_sketched(self):
        skel = pd.LineExtrudedElement(extrup=10)
        l = Line2(pd.Vector2.newFromXY(0,0),
            pd.Vector2.newFromXY(0,1),
            pd.Vector2.newFromXY(1,1),
            pd.Vector2.newFromXY(0,0))
        skel.add_poly(Polygon2.newFromSketch(l))
        
        skelscal = skel.scale(10,10,5)
        self.assertAllPolysAlmostEqual(skel._polygons, skelscal._polygons) #polygons are not touched by tranformations
        self.assertVectAlmostEqual(skel._cent, skelscal._cent) #cent is not touched
        
        

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
        skel = pd.LineExtrudedElement(extrup=10)
        skel.add_poly(Polygon2.newFromSketch(arc1, l12, arc2, l23, arc3, l34, arc4, l41))
        self.assertEqual(len(skel._polygons), 1)
        self.assertEqual(len(skel._polygons[0].vertices), 4*6 + 4*2) #4 arcs in qual 20 (6 vertices) and 4 lines with tow vertices each


if __name__ == "__main__":
    unittest.main()