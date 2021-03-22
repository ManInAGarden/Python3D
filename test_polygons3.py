from python3d.Polygons import Polygon3, Vector3, Vertex3
from TestBase import *
import unittest
import python3d as pd
import math

class Poly3Test(TestBase):

    def get_poly(self):
        v1 = Vertex3.newFromXYZ(0, 0,10)
        v2 = Vertex3.newFromXYZ(0,10,10)
        v3 = Vertex3.newFromXYZ(-10,10,10)
        return pd.Polygon3([v1,v2,v3])

    def test_polygon_creation(self):
        poly = self.get_poly()
        self.assertEqual(3, len(poly.vertices))
        self.assertIsNotNone(poly.plane)
        self.assertEqual(Vector3.Zdir(), poly.plane.n)
        self.assertEqual(10, poly.plane.zdist)

    def test_polygon_cloning(self):
        poly = self.get_poly()
        polyc = poly.clone()

        for i in range(len(poly.vertices)):
            self.assertEqual(poly.vertices[i], polyc.vertices[i])
        
        #but
        vx = poly.vertices[0]
        vx.pos.x = 1000

        self.assertEqual(1000, poly.vertices[0].pos[0])
        self.assertNotEqual(1000, polyc.vertices[0].pos[0])
        
    def test_triangularization(self):
        vmat = [[0,0,0],[10,0,0],[10,10,0],[12,15,0],[9,7,0]]
        p = self._get_poly(vmat)

        ptrias = p.to_triangles()
        self.assertEqual(len(ptrias), len(vmat)-2)

    def test_vertex(self):
        v1 = Vertex3.newFromXYZ(10,0,0)
        v2 = Vertex3.newFromXYZ(30,0,0)
        v3 = v1.getbetween(v2, 0.5)
        self.assertEqual(Vertex3.newFromXYZ(20,0,0), v3)


    def _get_poly(self, ptmat):
        verts = []        
        for pt in ptmat:
            verts.append(Vertex3.newFromList(pt))

        return Polygon3(verts)




if __name__ == "__main__":
    unittest.main()