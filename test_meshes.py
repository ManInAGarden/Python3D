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
        ball = pd.EllipsoidElement(0.0, 0.0, 0.0, 10.0, 10.0, 10.0) #this is a sphere
        srad = 10.0
        cent = ball._cent
        m.addelement(ball, quality=10)
        self.assertTrue(len(m._vertices) > 0)
        self.assertTrue(len(m._triangles) > 0)
        #check all the vertices to be on the sphere's surface
        for pt in m._vertices:
            rad = (pt-cent).norm()
            self.assertAlmostEqual(srad, rad)

    def test_ballmeshoutofcentre(self):
        m = pd.Mesh()
        ball = pd.EllipsoidElement(10.0, -90.0, 52.0, 10.0, 10.0, 10.0) #this is a sphere
        srad = 10.0
        cent = ball._cent
        m.addelement(ball, quality=10)
        self.assertTrue(len(m._vertices) > 0)
        self.assertTrue(len(m._triangles) > 0)
        #check all the vertices to be on the sphere's surface
        for pt in m._vertices:
            rad = (pt-cent).norm()
            self.assertAlmostEqual(srad, rad)

    def test_ellipsoidincentre(self):
        m = pd.Mesh()
        elli = pd.EllipsoidElement(0.0, 0.0, 0.0, 10.0, 30.0, 20.0) #this is an ellipsoid
        cent = elli._cent
        m.addelement(elli, quality=10)
        self.assertTrue(len(m._vertices) > 0)
        self.assertTrue(len(m._triangles) > 0)
        #check all the vertices to be on the sphere's surface
        asq = elli._dimensions[0].norm()**2
        bsq = elli._dimensions[1].norm()**2
        csq = elli._dimensions[2].norm()**2
        for pt in m._vertices:
            chkval = pt.x**2/asq + pt.y**2/bsq + pt.z**2/csq
            self.assertAlmostEqual(1.0, chkval)

    def test_ellipsoidoutoffcentre(self):
        m = pd.Mesh()
        elli = pd.EllipsoidElement(-90.0, 100.0, 12.0, 10.0, 30.0, 20.0) #this is an ellipsoid
        cent = elli._cent
        m.addelement(elli, quality=10)
        self.assertTrue(len(m._vertices) > 0)
        self.assertTrue(len(m._triangles) > 0)
        #check all the vertices to be on the sphere's surface
        asq = elli._dimensions[0].norm()**2
        bsq = elli._dimensions[1].norm()**2
        csq = elli._dimensions[2].norm()**2
        for ptr in m._vertices:
            pt = ptr - cent
            chkval = pt.x**2/asq + pt.y**2/bsq + pt.z**2/csq
            self.assertAlmostEqual(1.0, chkval)


    def test_ellipsoidrotated(self):
        m = pd.Mesh()
        elli = pd.EllipsoidElement(0.0, 0.0, 0.0, 10.0, 30.0, 20.0).rotate(pd.AxisEnum.ZAXIS, 45).rotate(pd.AxisEnum.YAXIS, 45) #this is an ellipsoid
        cent = elli._cent
        m.addelement(elli, quality=10)
        self.assertTrue(len(m._vertices) > 0)
        self.assertTrue(len(m._triangles) > 0)
        #check all the vertices to be on the sphere's surface
        asq = elli._dimensions[0].norm()**2
        bsq = elli._dimensions[1].norm()**2
        csq = elli._dimensions[2].norm()**2
        for ptr in m._vertices:
            pt = ptr - cent
            chkval = pt.x**2/asq + pt.y**2/bsq + pt.z**2/csq
            self.assertAlmostEqual(1.0, chkval)


if __name__ == "__main__":
    unittest.main()


