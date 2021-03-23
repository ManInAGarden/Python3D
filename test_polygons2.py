from TestBase import *
import unittest
import python3d as pd
import math

class Poly2Test(TestBase):

    def get_poly(self):
        v1 = pd.Vertex2.newFromXY(0,0)
        v2 = pd.Vertex2.newFromXY(0,10)
        v3 = pd.Vertex2.newFromXY(-10,10)
        return pd.Polygon2([v1,v2,v3])

    def test_polygon_creation(self):
        poly = self.get_poly()
        self.assertEqual(3, len(poly.vertices))

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
        
    def test_vertex_getbetween(self):
        v1 = pd.Vertex2.newFromXY(10,0)
        v2 = pd.Vertex2.newFromXY(30,0)
        v3 = v1.getbetween(v2, 0.5)
        self.assertEqual(pd.Vertex2.newFromXY(20,0), v3)

    def test_polygontwist(self):
        #create a polygon with counterclockwise twist
        v1 = pd.Vertex2.newFromXY(10,0)
        v2 = pd.Vertex2.newFromXY(15,5)
        v3 = pd.Vertex2.newFromXY(10, 10)
        p = pd.Polygon2([v1, v2, v3])
        ptwist = p.gettwist()
        self.assertEqual(ptwist, pd.PolygonTwistEnum.COUNTERCLKWISE)
        p.turnover()
        self.assertEqual(p.gettwist(), pd.PolygonTwistEnum.CLKWISE)
        v4 = pd.Vertex2.newFromXY(0,5)
        p2 = pd.Polygon2([v1,v2,v3,v4])
        self.assertEqual(p2.gettwist(), pd.PolygonTwistEnum.COUNTERCLKWISE)
        v5 = pd.Vertex2.newFromXY(10, 5)
        v6 = pd.Vertex2.newFromXY(0, 0)
        p3 = pd.Polygon2([v1, v2, v3, v4, v5, v6])
        self.assertEqual(p3.gettwist(), pd.PolygonTwistEnum.COUNTERCLKWISE)
        self.assertEqual(p3.turnover().gettwist(), pd.PolygonTwistEnum.CLKWISE)


if __name__ == "__main__":
    unittest.main()
