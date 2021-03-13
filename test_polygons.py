from python3d.Polygons import Vector3, Vertex
from TestBase import *
import unittest
import python3d as pd
import math

class PartsTest(TestBase):

    def get_poly(self):
        n = Vector3([0,0,0])
        v1 = Vertex(Vector3([  0, 0,10]), n)
        v2 = Vertex(Vector3([  0,10,10]), n)
        v3 = Vertex(Vector3([-10,10,10]), n)
        return pd.Polygon([v1,v2,v3])

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
        


if __name__ == "__main__":
    unittest.main()
