from python3d.Polygons import Plane3, Polygon3, Vector3, Vertex3
from TestBase import *
import unittest
import python3d as pd
import math



class Plane3Test(TestBase):
    def test_polysplit_easy(self):
        poly = self.get_polygon([0,0,0],[1,0,0],[1,1,0])

        #define a plane in z,y to the left of the polygon
        plane = Plane3(Vector3.newFromXYZ(1.0,0.0,0.0), -1)

        cofront = []
        coback = []
        front = []
        back = []
        plane.splitPolygon(poly, cofront, coback, front, back)
        self.assertEqual(len(cofront), 0)
        self.assertEqual(len(coback), 0)
        self.assertEqual(len(back), 0)
        self.assertEqual(len(front), 1)

    def test_polysplit_easy2(self):
        poly = self.get_polygon([0,0,0],[1,0,0],[1,1,0])

        #define a plane in z,y to the right of the polygon
        plane = Plane3(Vector3.newFromXYZ(1.0,0.0,0.0), 2)

        cofront = []
        coback = []
        front = []
        back = []
        plane.splitPolygon(poly, cofront, coback, front, back)
        self.assertEqual(len(cofront), 0)
        self.assertEqual(len(coback), 0)
        self.assertEqual(len(back), 1)
        self.assertEqual(len(front), 0)

    def test_polysplit_easy3(self):
        poly = self.get_polygon([0,0,0],[1,0,0],[1,1,0])

        #define a plane in x,y located over the polygon
        plane = Plane3(Vector3.newFromXYZ(0.0,0.0,1.0), 1)

        cofront = []
        coback = []
        front = []
        back = []
        plane.splitPolygon(poly, cofront, coback, front, back)
        self.assertEqual(len(cofront), 0)
        self.assertEqual(len(coback), 0)
        self.assertEqual(len(back), 1)
        self.assertEqual(len(front), 0)


    def test_polysplit_easy4(self):
        poly = self.get_polygon([0,0,0],[1,0,0],[1,1,0])

        #define a plane in x,y under the polygon
        plane = Plane3(Vector3.newFromXYZ(0.0,0.0,1.0), -1)

        cofront = []
        coback = []
        front = []
        back = []
        plane.splitPolygon(poly, cofront, coback, front, back)
        self.assertEqual(len(cofront), 0)
        self.assertEqual(len(coback), 0)
        self.assertEqual(len(back), 0)
        self.assertEqual(len(front), 1)

    def test_polysplit_coplanar1(self):
        poly = self.get_polygon([0,0,1],[1,0,1],[1,1,1])

        #define a plane in x,y under the polygon
        plane = Plane3(Vector3.newFromXYZ(0.0,0.0,1.0), 1)

        cofront = []
        coback = []
        front = []
        back = []
        plane.splitPolygon(poly, cofront, coback, front, back)
        self.assertEqual(len(cofront), 1)
        self.assertEqual(len(coback), 0)
        self.assertEqual(len(back), 0)
        self.assertEqual(len(front), 0)

    def test_polysplit_coplanar2(self):
        poly = self.get_polygon([0,0,1],[1,0,1],[1,1,1])

        #define a plane in x,y under the polygon
        plane = Plane3(Vector3.newFromXYZ(0.0,0.0,-1.0), -1)

        cofront = []
        coback = []
        front = []
        back = []
        plane.splitPolygon(poly, cofront, coback, front, back)
        self.assertEqual(len(cofront), 0)
        self.assertEqual(len(coback), 1)
        self.assertEqual(len(back), 0)
        self.assertEqual(len(front), 0)

    
    def test_polysplit_spanning2(self):
        poly = self.get_polygon([0,0,1],[1,0,1],[1,1,1])
        #define a plane in xy, cutting the polygon at x=0.5 in y-direction
        plane = Plane3(Vector3.newFromXYZ(1.0,0.0, 0.0), 0.5)

        cofront = []
        coback = []
        front = []
        back = []
        plane.splitPolygon(poly, cofront, coback, front, back)
        self.assertEqual(len(cofront), 0)
        self.assertEqual(len(coback), 0)
        self.assertEqual(len(back), 1)
        self.assertEqual(len(front), 1)
        fropo = front[0]
        backpo = back[0]
        self.assertEqual(len(fropo.vertices), 4)
        self.assertEqual(len(backpo.vertices), 3)
        
    


    def get_polygon(self, *pts) -> pd.Polygon3:
        """create and return a polygon constructed with arguments in points

        usage: poly = get_polygon([0,0,0],[0,1,0],[1,1,0],....)
        Parameters
        ----------

        *pts - unlimited number of points each an list with three elements
        """
        vertices = []
        for pt in pts:
            vertices.append(Vertex3.newFromList(pt))

        return Polygon3(vertices)

if __name__ == "__main__":
    unittest.main()