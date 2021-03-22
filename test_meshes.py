from python3d.ElementClasses import SketchedElement
from python3d.Polygons import Vector2
import numpy
from numpy.core.arrayprint import _leading_trailing
from numpy.lib.polynomial import poly
from TestBase import *
import unittest
import python3d as pd
import math

class ElementTest(TestBase):
    def test_boxmesh(self):
        box = pd.BoxElement(xlength=10, ylength=20, zlength=30).rotate(pd.AxisEnum.XAXIS, 45).rotate(pd.AxisEnum.YAXIS, 45)
        b = pd.Body().addelement(box)
        m = pd.Mesh(b)
        self.assertIsNotNone(m.btsource)


    def test_box_polygons(self):
        box = pd.BoxElement(xlength=10, ylength=20, zlength=30)
        body = pd.Body().addelement(box)
        m = pd.Mesh(body)
        polygons = m.get_all_polygons()

        self.assertEqual(12, len(polygons))
        normsum = pd.Vector3.newFromXYZ(0.0, 0.0, 0.0)
        for poly in polygons:
            normsum += poly.plane.n
            self.assertGreater(len(poly.vertices), 2)

        self.assertAlmostEqual(0.0, normsum.x)
        self.assertAlmostEqual(0.0, normsum.y)
        self.assertAlmostEqual(0.0, normsum.z)

    def test_box_union(self):
        b1 = pd.BoxElement(xlength=15,ylength=15,zlength=15).translate(-7.5, -7.5, -7.5)
        b2 = pd.BoxElement(xlength=30, ylength=5, zlength=5).translate(-15, -2.5, -2.5)
        body = pd.Body().addelement(b1)
        body.addelement(b2) #union is default operation
        m = pd.Mesh(body)
        self.assertIsNotNone(m.btsource)

        fname = "test_stl_boxuinion.stl"
        m.name = "Boxuniontest"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    def test_box_difference(self):
        b1 = pd.BoxElement(xlength=15,ylength=15,zlength=15).translate(-7.5, -7.5, -7.5)
        b2 = pd.BoxElement(xlength=30, ylength=5, zlength=5).translate(-15, -2.5, -2.5)
        body = pd.Body().addelement(b1)
        body.addelement(b2, pd.BodyOperationEnum.DIFFERENCE) 
        m = pd.Mesh(body)
        self.assertIsNotNone(m.btsource)

        fname = "test_stl_boxdifference.stl"
        m.name = "Boxdifferencetest"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    def test_box_intersect(self):
        b1 = pd.BoxElement(xlength=15,ylength=15,zlength=15).translate(-7.5, -7.5, -7.5)
        b2 = pd.BoxElement(xlength=30, ylength=5, zlength=5).translate(-15, -2.5, -2.5)
        body = pd.Body().addelement(b1)
        body.addelement(b2, pd.BodyOperationEnum.INTERSECTION) 
        m = pd.Mesh(body)
        self.assertIsNotNone(m.btsource)

        fname = "test_stl_intersect.stl"
        m.name = "Boxintersecttest"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    def test_sphere_polygons(self):
        elli = pd.EllipsoidElement(radx=10.0, rady=10.0,radz=10.0)
        body = pd.Body().addelement(elli, quality=20)
        m = pd.Mesh(body)
        cent = elli._cent
        normsum = pd.Vector3.Zero()
        srad = 10.0
        for poly in m.get_all_polygons():
            normsum += poly.plane.n
            for vert in poly.vertices:
                rad = (vert.pos-cent).magnitude()
                self.assertAlmostEqual(srad, rad)

        self.assertAlmostEqual(0.0, normsum.x)
        self.assertAlmostEqual(0.0, normsum.y)
        self.assertAlmostEqual(0.0, normsum.z)

    
    def test_two_ball_merge(self):
        ball1 = pd.EllipsoidElement(0.0, 0.0, 0.0, 10.0, 10.0, 10.0) #this is a sphere
        ball2 = pd.EllipsoidElement(0.0, 0.0, 0.0, 10.0, 10.0, 10.0).translate(8.0,0.0, 0.0)
        body = pd.Body().addelement(ball1, quality=20)
        body.addelement(ball2, quality=20)
        m = pd.Mesh(body)
        sth = pd.StlHelper(m, "two_balls_ascii.stl", pd.StlModeEnum.ASCII)
        sth.write()

    # def test_ballmeshoutofcentre(self):
    #     ball = pd.EllipsoidElement(10.0, -90.0, 52.0, 10.0, 10.0, 10.0) #this is a sphere
    #     srad = 10.0
    #     cent = ball._cent
    #     m = pd.Mesh(ball, 10)
    #     self.assertTrue(len(m._vertices) > 0)
    #     self.assertTrue(len(m._triangles) > 0)
    #     #check all the vertices to be on the sphere's surface
    #     for pt in m._vertices:
    #         rad = (pt-cent).norm()
    #         self.assertAlmostEqual(srad, rad)

    # def test_ellipsoidincentre(self):
    #     elli = pd.EllipsoidElement(0.0, 0.0, 0.0, 10.0, 30.0, 20.0) #this is an ellipsoid
    #     cent = elli._cent
    #     m = pd.Mesh(elli, 10)
    #     self.assertTrue(len(m._vertices) > 0)
    #     self.assertTrue(len(m._triangles) > 0)
    #     #check all the vertices to be on the sphere's surface
    #     asq = elli._dimensions[0].magnitude()**2
    #     bsq = elli._dimensions[1].magnitude()**2
    #     csq = elli._dimensions[2].magnitude()**2
    #     for pt in m._vertices:
    #         chkval = pt.x**2/asq + pt.y**2/bsq + pt.z**2/csq
    #         self.assertAlmostEqual(1.0, chkval)

    # def test_ellipsoidoutoffcentre(self):
    #     m = pd.Mesh()
    #     elli = pd.EllipsoidElement(-90.0, 100.0, 12.0, 10.0, 30.0, 20.0) #this is an ellipsoid
    #     cent = elli._cent
    #     m = pd.Mesh(elli, 10)
    #     self.assertTrue(len(m._vertices) > 0)
    #     self.assertTrue(len(m._triangles) > 0)
    #     #check all the vertices to be on the sphere's surface
    #     asq = elli._dimensions[0].magnitude()**2
    #     bsq = elli._dimensions[1].magnitude()**2
    #     csq = elli._dimensions[2].magnitude()**2
    #     for ptr in m._vertices:
    #         pt = ptr - cent
    #         chkval = pt.x**2/asq + pt.y**2/bsq + pt.z**2/csq
    #         self.assertAlmostEqual(1.0, chkval)

    def test_stl_ascii(self):
        fname = "test_stl_ascii.stl"

        box = pd.BoxElement(0, 0, 0, 100, 100, 100)
        body = pd.Body().addelement(box)
        m = pd.Mesh(body)
        m.name = "Boxtestmesh"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    def test_stl_bin(self):
        fname = "test_stl_bin.stl"

        box = pd.BoxElement(0, 0, 0, 100, 100, 100)
        body = pd.Body()
        body.addelement(box)
        m = pd.Mesh(body)
        m.name = "Boxtestmesh"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.BINARY)
        sth.write()

    def test_stl_ascii2(self):
        fname = "test_stl_ascii2.stl"

        elli = pd.EllipsoidElement(0, 0, 0, 100, 70, 50).rotate(pd.AxisEnum.ZAXIS, 45)
        body = pd.Body().addelement(elli, quality=20)
        m = pd.Mesh(body)
        m.name = "Ellipsoidtestmesh"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    # # def test_ellipsoidrotated(self):
    # #     m = pd.Mesh()
    # #     elli = pd.EllipsoidElement(0.0, 0.0, 0.0, 10.0, 30.0, 20.0).rotate(pd.AxisEnum.ZAXIS, 45).rotate(pd.AxisEnum.YAXIS, 45) #this is an ellipsoid
    # #     cent = elli._cent
    # #     m.addelement(elli, quality=10)
    # #     self.assertTrue(len(m._vertices) > 0)
    # #     self.assertTrue(len(m._triangles) > 0)
    # #     #check all the vertices to be on the sphere's surface
    # #     asq = elli._dimensions[0].norm()**2
    # #     bsq = elli._dimensions[1].norm()**2
    # #     csq = elli._dimensions[2].norm()**2
    # #     for ptr in m._vertices:
    # #         pt = ptr - cent
    # #         chkval = pt.x**2/asq + pt.y**2/bsq + pt.z**2/csq
    # #         self.assertAlmostEqual(1.0, chkval)

    def test_cylinder_simple(self):
        cyl = pd.CylinderElement(lz=10, r=5)
        body = pd.Body().addelement(cyl, quality=20)
        m = pd.Mesh(body)
        m.name = "Cylindertestmesh"
        fname = m.name + ".stl"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    def test_cylinder_pinched(self):
        cyl = pd.CylinderElement(lz=10, r=10).rotate(pd.AxisEnum.YAXIS, 45)
        body = pd.Body().addelement(cyl, quality=50)
        cyl2 = pd.CylinderElement(lz=20, r=4).rotate(pd.AxisEnum.YAXIS, 45)
        body.addelement(cyl2, pd.BodyOperationEnum.DIFFERENCE, 50)
        m = pd.Mesh(body)
        m.name = "Cylinderpinchedtestmesh"
        fname = m.name + ".stl"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    def test_findperpinormals(self):
        print("findperpinormals start")
        m = pd.Mesh()
        axis = pd.Vector3.Zdir()
        n1, n2 = m._findperpendicularnormals(axis)
        self.assertAlmostEqual(n1 * n2, 0.0)
        self.assertAlmostEqual(axis * n2, 0.0)
        self.assertAlmostEqual(axis * n1, 0.0)

        axis = pd.Vector3.Xdir()
        n1, n2 = m._findperpendicularnormals(axis)
        self.assertAlmostEqual(n1 * n2, 0.0)
        self.assertAlmostEqual(axis * n2, 0.0)
        self.assertAlmostEqual(axis * n1, 0.0)

        axis = pd.Vector3.Ydir()
        n1, n2 = m._findperpendicularnormals(axis)
        self.assertAlmostEqual(n1 * n2, 0.0)
        self.assertAlmostEqual(axis * n2, 0.0)
        self.assertAlmostEqual(axis * n1, 0.0)

        axis = pd.Vector3.newFromXYZ(0, 7, -12)
        n1, n2 = m._findperpendicularnormals(axis)
        self.assertAlmostEqual(n1 * n2, 0.0)
        self.assertAlmostEqual(axis * n2, 0.0)
        self.assertAlmostEqual(axis * n1, 0.0)
        print("findperpinormals end")


    def test_sketched_element(self):
        print("sketched_element start")
        extsketch = self._get_box_sketch([-10,-10],[10,-10],[10,10],[-10,10], 3.0)
        body = pd.Body().addelement(extsketch)
        m = pd.Mesh(body)
        m.name = "Sketchtestmesh"
        fname = m.name + ".stl"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()
        print("sketched_element end")


    def test_sketched_element_withholes(self):
        extsketch = self._get_box_sketch([-10,-10],[10,-10],[10,10],[-10,10], 3.0)
        self._addhole_sketch(extsketch, [-10, -10], 1.0)
        self._addhole_sketch(extsketch, [ 10, -10], 1.0)
        self._addhole_sketch(extsketch, [ 10,  10], 1.0)
        self._addhole_sketch(extsketch, [-10,  10], 1.0)

        body = pd.Body().addelement(extsketch)
        m = pd.Mesh(body)
        m.name = "Sketchholestestmesh"
        fname = m.name + ".stl"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.BINARY)
        sth.write()

    def test_sketched_star(self):
        spikes = 5
        rout = 50
        rin = 20
        rcur = rout
        lines = []
        oldpt = None
        endpt = None
        for i in range(2*spikes):
            phi = -i * math.pi/spikes
            x = rcur*math.sin(phi)
            y = rcur*math.cos(phi)
            pt = pd.Vector2.newFromXY(x, y)
            if endpt is None: endpt = pt
            if not oldpt is None:
                lines.append(pd.Line2(oldpt, pt))
            
            if rcur==rout:
                rcur = rin
            else:
                rcur = rout

            oldpt = pt

        lines.append(pd.Line2(oldpt, endpt))
        skel = SketchedElement(extrdown=-10, extrup=10)
        skel.add_poly(Polygon2.newFromSketch(*lines))

        body = pd.Body().addelement(skel)
        m = pd.Mesh(body)
        m.name = "Sketchedstarsmesh"
        fname = m.name + ".stl"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.ASCII)
        sth.write()

    def _get_box_sketch(self, c1, c2, c3, c4, arcr):
        corner1 = pd.Vector2.newFromList(c1)
        corner2 = pd.Vector2.newFromList(c2)
        corner3 = pd.Vector2.newFromList(c3)
        corner4 = pd.Vector2.newFromList(c4)
        arcrv = pd.Vector2.newFromXY(arcr, arcr)
        arc1 = pd.EllipticArc2(corner1, arcrv, 180, 270, 20)
        l12 = pd.Line2(corner1 + pd.Vector2.newFromXY(0,-arcr),
            corner2 + pd.Vector2.newFromXY(0, -arcr))
        arc2 = pd.EllipticArc2(corner2, arcrv, 270, 360, 20)
        l23 = pd.Line2(corner2 + pd.Vector2.newFromXY(arcr,0),
            corner3 + pd.Vector2.newFromXY(arcr, 0))
        arc3 = pd.EllipticArc2(corner3, arcrv, 0, 90, 20)
        l34 = pd.Line2(corner3 + pd.Vector2.newFromXY(0,arcr),
            corner4 + pd.Vector2.newFromXY(0,arcr))
        arc4 = pd.EllipticArc2(corner4, arcrv, 90, 180, 20)
        l41 = pd.Line2(corner4 + pd.Vector2.newFromXY(-arcr,0),
            corner1 + pd.Vector2.newFromXY(-arcr,0))
        skel = pd.SketchedElement(extrup=10)
        skel.add_poly(Polygon2.newFromSketch(arc1, l12, arc2, l23, arc3, l34, arc4, l41))
        return skel

    def _addhole_sketch(self, sketch, cent, rad):
        arc = pd.Ellipse2(pd.Vector2.newFromList(cent), pd.Vector2.newFromXY(rad, rad))
        sketch.add_poly(pd.Polygon2.newFromSketch(arc))

if __name__ == "__main__":
    unittest.main()


