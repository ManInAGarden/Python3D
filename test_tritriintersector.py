# I got most of this from a program written in C which i translated to python
# 
# See here:
#
# Triangle/triangle intersection test routine,
# * by Tomas Moller, 1997.
# * See article "A Fast Triangle-Triangle Intersection Test",
# * Journal of Graphics Tools, 2(2), 1997
# * updated: 2001-06-20 (added line of intersection)


import unittest
import python3d as pd
import math
from TestBase import *

class TriTriIntersectorTest(TestBase):

    def test_parallel_trias(self):
        t1 = self.getmeshtriangle([12.0, -11.0, 20.0], [8.0, 7.0, 20.0], [3.0, 19.0, 20.0])
        t2 = self.getmeshtriangle([9.0, -17.0, 10.0], [81.0, -3.0, 10.0], [3.0, 19.0, 10.0])
        tti = pd.TriTriIntersector(t1, t2)
        erg = tti.getisectline()
        self.assertIsNotNone(erg)
        self.assertEqual(pd.TriTriIsectResultEnum.DONTINTERSECT, erg.status)

    def test_coplanaer_separate(self):
        t1 = self.getmeshtriangle([-12.0, -11.0, 20.0], [-8.0, -7.0, 20.0], [-3.0, 19.0, 20.0])
        t2 = self.getmeshtriangle([9.0, -17.0, 20.0], [81.0, -3.0, 20.0], [3.0, 19.0, 20.0])
        tti = pd.TriTriIntersector(t1, t2)
        erg = tti.getisectline()
        self.assertIsNotNone(erg)
        self.assertEqual(pd.TriTriIsectResultEnum.COPLANARDONTINTERSECT, erg.status)

    def test_vertical_intersect(self):
        t1 = self.getmeshtriangle([0.0, 0.0, 0.0], [10.0, 10.0, 0.0], [20.0, 0.0, 0.0])
        t2 = self.getmeshtriangle([0.0, 5.0, -5.0], [10.0, 5.0, 20.0], [20.0, 5.0, -5.0])
        tti = pd.TriTriIntersector(t1, t2)
        erg = tti.getisectline()
        self.assertIsNotNone(erg)
        self.assertEqual(pd.TriTriIsectResultEnum.INTERSECT, erg.status)
        #triangles are flat in x/y and x/z so that intersection line only differs in x
        self.assertEqual(erg.p1.y, erg.p2.y)
        self.assertEqual(erg.p1.z, erg.p2.z)


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