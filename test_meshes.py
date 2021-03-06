from sys import setrecursionlimit
from TestBaseMeshes import TestBaseMeshes
import numpy
from numpy.core.arrayprint import _leading_trailing
from numpy.lib.polynomial import poly
from TestBase import *
import unittest
import python3d as pd

class ElementTest(TestBaseMeshes):
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
        b1 = pd.BoxElement(xlength=15,ylength=15,zlength=15)
        b2 = pd.BoxElement(xlength=30, ylength=5, zlength=5)
        body = pd.Body().addelement(b1)
        body.addelement(b2) #union is default operation
        m = pd.Mesh(body)
        self.assertIsNotNone(m.btsource)

        m.name = "test_box_union"
        self.write_stl(m)

    def test_box_difference(self):
        b1 = pd.BoxElement(xlength=15,ylength=15,zlength=15)
        b2 = pd.BoxElement(xlength=30, ylength=5, zlength=5)
        body = pd.Body().addelement(b1)
        body.addelement(b2, pd.BodyOperationEnum.DIFFERENCE) 
        m = pd.Mesh(body)
        self.assertIsNotNone(m.btsource)
        m.name = "test_stl_boxdifference"

        self.write_stl(m)

    def test_box_intersect(self):
        b1 = pd.BoxElement(xlength=15,ylength=15,zlength=15)
        b2 = pd.BoxElement(xlength=30, ylength=5, zlength=5)
        body = pd.Body().addelement(b1)
        body.addelement(b2, pd.BodyOperationEnum.INTERSECTION) 
        m = pd.Mesh(body)
        self.assertIsNotNone(m.btsource)

        m.name = "test_box_intersect"
        self.write_stl(m)

    def test_sphere_polygons(self):
        elli = pd.EllipsoidElement(rx=10.0, ry=10.0,rz=10.0)
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
        m.name = "test_two_ball_merge"
        self.write_stl(m)

    

    def test_stl_ascii(self):
        fname = "test_stl_ascii.stl"

        box = pd.BoxElement(0, 0, 0, 100, 100, 100)
        body = pd.Body().addelement(box)
        m = pd.Mesh(body)
        m.name = "test_stl_ascii"
        self.write_stl(m, pd.StlModeEnum.ASCII)

    def test_stl_bin(self):
        fname = "test_stl_bin.stl"

        box = pd.BoxElement(0, 0, 0, 100, 100, 100)
        body = pd.Body()
        body.addelement(box)
        m = pd.Mesh(body)
        m.name = "test_stl_bin"
        self.write_stl(m, pd.StlModeEnum.BINARY)


    def test_stl_ellipsoid_simple(self):
        elli = pd.EllipsoidElement(0, 0, 0, 100, 100, 100)
        body = pd.Body().addelement(elli, quality=20)
        m = pd.Mesh(body)
        m.name = "test_stl_ellipsoid_simple"
        self.write_stl(m)

    def test_stl_ellipsoid_rotated(self):
        elli = pd.EllipsoidElement(0, 0, 0, 100, 70, 50).rotate(pd.AxisEnum.ZAXIS, 45)
        body = pd.Body().addelement(elli, quality=20)
        m = pd.Mesh(body)
        m.name = "test_stl_ellipsoid_rotated"
        self.write_stl(m)

    def test_stl_ellipsoid_pinched(self):
        #view triangles in viewer to see this
        elli = pd.EllipsoidElement(rx=100, ry=70, rz=50)
        body = pd.Body().addelement(elli, quality=30)
        toolelli = pd.EllipsoidElement(rx=10, ry=10, rz=10).translate(100,0,0) #places centre on the outer tip of first ellipsoid
        body.addelement(toolelli, pd.BodyOperationEnum.DIFFERENCE, 30)
        m = pd.Mesh(body)
        m.name = "test_stl_ellipsoid_pinched"
        self.write_stl(m)

   
    def test_cylinder_simple(self):
        cyl = pd.CylinderElement(l=10, rx=5, ry=5)
        body = pd.Body().addelement(cyl, quality=20)
        m = pd.Mesh(body)
        m.name = "test_cylinder_simple"

        self.write_stl(m)

    def test_cylinder_translated(self):
        cyl = pd.CylinderElement(l=10, rx=25, ry=25).translate(20,20,20)
        body = pd.Body().addelement(cyl, quality=20)
        m = pd.Mesh(body)
        m.name = "test_cylinder_translated"

        self.write_stl(m)

    def test_cylinder_rotated(self):
        cyl = pd.CylinderElement(l=20, rx=5, ry=5).rotate(pd.AxisEnum.YAXIS, 45)
        body = pd.Body().addelement(cyl, quality=20)
        m = pd.Mesh(body)
        m.name = "test_cylinder_rotated"

        self.write_stl(m)

    def test_cylinder_pinched(self):
        cyl = pd.CylinderElement(l=10, rx=10, ry=10).rotate(pd.AxisEnum.YAXIS, 45)
        body = pd.Body().addelement(cyl, quality=30)
        cyl2 = pd.CylinderElement(l=20, rx=4, ry=4).rotate(pd.AxisEnum.YAXIS, 45)
        body.addelement(cyl2, pd.BodyOperationEnum.DIFFERENCE, 30)
        m = pd.Mesh(body)
        m.name = "test_cylinder_pinched"
        self.write_stl(m)


    def test_findperpinormals(self):
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


    def test_sketched_element(self):
        extsketch = self._get_box_sketch([-10,-10],[10,-10],[10,10],[-10,10], 3.0)
        body = pd.Body().addelement(extsketch)
        m = pd.Mesh(body)
        m.name = "test_sketched_element"
        self.write_stl(m)


    def test_sketched_element_withholes(self):
        extsketch = self._get_box_sketch([-10,-10],[10,-10],[10,10],[-10,10], 3.0)
        self._addhole_sketch(extsketch, [-10, -10], 1.0)
        self._addhole_sketch(extsketch, [ 10, -10], 1.0)
        self._addhole_sketch(extsketch, [ 10,  10], 1.0)
        self._addhole_sketch(extsketch, [-10,  10], 1.0)

        body = pd.Body().addelement(extsketch)
        m = pd.Mesh(body)
        m.name = "test_sketched_element_withholes"
        self.write_stl(m)

    def test_sketched_star(self):
        spoly = self.create_star_polygon()
        skel = pd.LineExtrudedElement(extrdown=-10, extrup=10)
        skel.add_poly(spoly)
        body = pd.Body().addelement(skel)
        
        m = pd.Mesh(body)
        m.name = "test_sketched_star"
        self.write_stl(m)

    def test_sketched_framestar(self):
        spolyouter = self.create_star_polygon()
        spolyinner = self.create_star_polygon(5, 15, 45)
        skel = pd.LineExtrudedElement(extrdown=-10, extrup=10)
        skel.add_poly(spolyouter)
        skel.add_poly(spolyinner)
        body = pd.Body().addelement(skel)
        
        m = pd.Mesh(body)
        m.name = "test_sketched_framestar"
        self.write_stl(m)

    def test_sketched_drop(self):
        arc = pd.EllipticArc2(pd.Vector2.Zero(), pd.Vector2.newFromXY(10, 10), -(90 + 45), 90 + 45, 30)
        ts = arc.get_tangent(pd.TangentPosEnum.START)
        te = arc.get_tangent(pd.TangentPosEnum.END)

        hole = pd.Ellipse2(arc.get_centre(), pd.Vector2.newFromXY(3,3), 30)

        corne = te.get_projectedpt(-4) #projected outwards of the arc, negative t
        corns = ts.get_projectedpt(-4)

        line = pd.Line2(te.pt, corne, corns, ts.pt)
        skel = pd.LineExtrudedElement(extrup=10)

        skel.add_poly(pd.Polygon2.newFromSketch(arc, line))
        skel.add_poly(pd.Polygon2.newFromSketch(hole))
        body = pd.Body().addelement(skel)
        
        m = pd.Mesh(body)
        m.name = "test_sketched_drop"
        self.write_stl(m)

    def test_zigzag(self):
        lin = pd.Line2(pd.Vector2.Zero(), pd.Vector2.newFromXY(0.0,10.0))

        for i in range(2,5):
            iseven = i % 2 == 0
            if not iseven:
                lin.add_point_byangle(100, 5)
            else:
                lin.add_point_byangle(80, 5)

        lin.add_point_byangle(180, 10.0)

        for i in range(2,5):
            iseven = i % 2 == 0
            if not iseven:
                lastpt = lin.add_point_byangle(280, 5)
            else:
                lastpt = lin.add_point_byangle(260, 5)
        lin.add_point(pd.Vector2.newFromXY(-10.0,0.0))

        lin.close_line()

        bohrung = pd.Ellipse2(pd.Vector2.newFromXY(-5,10), 
            pd.Vector2.newFromXY(2,2), 20)
        skel = pd.LineExtrudedElement(extrup=10)

        skel.add_poly(pd.Polygon2.newFromSketch(lin))
        skel.add_poly(pd.Polygon2.newFromSketch(bohrung))
        body = pd.Body().addelement(skel)
        
        m = pd.Mesh(body)
        m.name = "test_zigzag"
        self.write_stl(m)

    def test_bezier(self):
        ctrlpts = [pd.Vector2.newFromXY(0,0),
            pd.Vector2.newFromXY(0.0, 10.0),
            pd.Vector2.newFromXY(10.0, 10.0),
            pd.Vector2.newFromXY(10.0, 0.0)]

        ctrlpts.reverse()

        bez = pd.Bezier2(ctrlpts, 30)
        clin = pd.Line2(pd.Vector2.Zero(), pd.Vector2.newFromXY(10.0, 0.0))
        poly = pd.Polygon2.newFromSketch(bez, clin)
        skel = pd.LineExtrudedElement(extrup=20)
        skel.add_poly(poly)
        body = pd.Body().addelement(skel)

        m = pd.Mesh(body)
        m.name = "test_bezier"
        self.write_stl(m)

    def test_rotate_extrude_doughnut(self):
        elli = pd.Ellipse2(pd.Vector2.newFromXY(40.0, 0.0), pd.Vector2.newFromXY(10.0, 10.0), quality=30)
        rotex = pd.RotateExtrudedElement().add_poly(pd.Polygon2.newFromSketch(elli))
        rotex = rotex.rotate(pd.AxisEnum.XAXIS, 45)
        body = pd.Body().addelement(rotex, quality=30)
        
        m = pd.Mesh(body)
        m.name = "test_rotate_extrude_doughnut"
        self.write_stl(m)

    def test_rotate_extrude_vase(self):
        vp = self.create_vase_polygon()
        rotex = pd.RotateExtrudedElement()
        rotex.add_poly(vp)
        rotexin = rotex.scale(0.9, 0.9, 0.9).translate(0.0, 2.5, 0.0)
        cyl = pd.CylinderElement(rx=18, ry=18, l=5).rotate(pd.AxisEnum.XAXIS, 90).translate(0,50,0)
        body = pd.Body().addelement(rotex, quality=30)
        body.addelement(rotexin, pd.BodyOperationEnum.DIFFERENCE, quality=30)
        body.addelement(cyl, pd.BodyOperationEnum.DIFFERENCE, quality=30)
        
        m = pd.Mesh(body)
        m.name = "test_rotate_extrude_vase"
        self.write_stl(m)

    def test_rotate_extrude_withholes(self):
        ellout = pd.Ellipse2(pd.Vector2.newFromXY(40.0, 0.0), pd.Vector2.newFromXY(10.0, 10.0), quality=30)
        ellin = pd.Ellipse2(pd.Vector2.newFromXY(40.0, 0.0), pd.Vector2.newFromXY(8.0, 8.0), quality=30)
        rotex = pd.RotateExtrudedElement(stopangle=180).add_poly(pd.Polygon2.newFromSketch(ellout)).add_poly(pd.Polygon2.newFromSketch(ellin))
        body = pd.Body().addelement(rotex, quality=30)
        
        m = pd.Mesh(body)
        m.name = "test_rotate_extrude_withholes"
        self.write_stl(m)


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
        skel = pd.LineExtrudedElement(extrup=10)
        skel.add_poly(pd.Polygon2.newFromSketch(arc1, l12, arc2, l23, arc3, l34, arc4, l41))
        return skel

    def _addhole_sketch(self, sketch, cent, rad):
        arc = pd.Ellipse2(pd.Vector2.newFromList(cent), pd.Vector2.newFromXY(rad, rad))
        sketch.add_poly(pd.Polygon2.newFromSketch(arc))

if __name__ == "__main__":
    setrecursionlimit(5000)
    # tc = ElementTest()
    # tc.test_rotate_extrude_withholes()

    unittest.main()


