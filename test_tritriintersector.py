import unittest
import python3d as pd
import math
from TestBase import *

class TriTriIntersectorTest(TestBase):

    def test_apotp(self):
        t1 = self.getmeshtriangle([12.0, -11.0, 20.0], [8.0, 7.0, 20.0], [3.0, 19.0, 20.0])
        t2 = self.getmeshtriangle([9.0, -17.0, 10.0], [81.0, -3.0, 10.0], [3.0, 19.0, 10.0])
        tti = pd.TriTriIntersector(t1, t2)
        erg = tti.apotp()
        self.assertTrue(erg)
        tmp = t1.pts[0]
        t1.pts[0] = t2.pts[0]
        t2.pts[0] = tmp
        tti2 = pd.TriTriIntersector(t1, t2)
        self.assertFalse(tti2.apotp())

    def test_whatever(self):
        #create intersecting triangles
        t1 = self.getmeshtriangle([12.0, -11.0, 10.0], [8.0, 7.0, 20.0], [3.0, 19.0, 20.0])
        t2 = self.getmeshtriangle([9.0, -17.0, 20.0], [81.0, -3.0, 10.0], [3.0, 19.0, 10.0])
        tti = pd.TriTriIntersector(t1, t2)
        erg = tti.getinterpts()

    def getvertices(self, *triangles):
        answ = []
        for tria in triangles:
            answ.append(pd.Vector3(tria[0], tria[1], tria[2]))

        return answ

    def getmeshtriangle(self, *triangles):
        vertices = self.getvertices(*triangles)
        if len(vertices) != 3:
            raise Exception("no triangle in {}".format(vertices))
        n = (vertices[1]-vertices[0]).cross(vertices[2]-vertices[1])
        nnorm = n.norm()
        assert nnorm > 0.0, "triangle norm vector of zero length encountered. This normally means that two of the triangle points are equal"
        return pd.MeshTriangle(vertices, n/nnorm)

if __name__ == "__main__":
    unittest.main()