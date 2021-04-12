from TestBase import TestBase
from sys import setrecursionlimit
import unittest
import python3d as pd


class TestMeshUtils(TestBase):
    def test_consistency(self):
        body = pd.Body().addelement(pd.SphereElement(r=10), quality=30)
        m = pd.Mesh(body)
        faults = m.checkforconsistentrianglemesh()
        self.assertEqual(0, len(faults))
        notriapoly = pd.Polygon3.newFromVertices([pd.Vertex3.newFromXYZ(10,0,0),
            pd.Vertex3.newFromXYZ(0,20,0),
            pd.Vertex3.newFromXYZ(0,20,70),
            pd.Vertex3.newFromXYZ(40,40,40)
            ])
        m.btsource.buildfrompolygons([notriapoly]) #add the faulty "triangle-poly" in a not supported way
        faults = m.checkforconsistentrianglemesh()
        self.assertGreater(len(faults), 0)

        
if __name__ == "__main__":
    setrecursionlimit(5000)
    unittest.main()