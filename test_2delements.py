from python3d.Polygons import Vector2
import unittest
import python3d as pd
from TestBase import *

class Test2DElements(TestBase):
    def test_bezier4_creation(self):
        ctrlpts = [pd.Vector2.newFromXY(0,0),
            pd.Vector2.newFromXY(0.0,1.0),
            pd.Vector2.newFromXY(1.0, 1.0),
            pd.Vector2.newFromXY(1.0, 0.0)]

        bez = pd.Bezier2(ctrlpts, 30)
        self.assertEqual(len(bez.points), 30)

        tangs = bez.get_tangent(pd.TangentPosEnum.START)
        tange = bez.get_tangent(pd.TangentPosEnum.END)

        self.assertEqual(Vector2.Ydir(), tangs.ndir)
        self.assertEqual(Vector2.Ydir(), tange.ndir) #remember: tangents always point inwards



if __name__ == "__main__":
    unittest.main()