from TestBase import *
import unittest
import python3d as pd
import math

class PartsTest(TestBase):
    def test_partcreation(self):
        body = pd.Body()
        part = pd.Part(body)
        box = pd.BoxElement(xlength=100, ylength=100, zlength=100).rotate(pd.AxisEnum.ZAXIS, 45).rotate(pd.AxisEnum.YAXIS, 45)
        body.append(box)
        self.assertEqual(1, len(part._bodies))
        self.assertEqual(1, len(part._bodies[0]._consts))


if __name__ == "__main__":
    unittest.main()
