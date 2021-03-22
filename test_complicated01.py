from python3d.Bodies import BodyOperationEnum
import unittest
import python3d as pd
from TestBase import *

class TestBodies(TestBase):
    def test_tortured_cube(self):
        cube = pd.BoxElement(-25, -25, -25, 50, 50, 50)
        body = pd.Body().addelement(cube)
        innerelli = pd.EllipsoidElement(radx=20, rady=20, radz=20)
        body.addelement(innerelli, pd.BodyOperationEnum.DIFFERENCE, 20)
        windowx = pd.BoxElement(-50, -10, -10, 100, 20, 20)
        windowy = windowx.rotate(pd.AxisEnum.ZAXIS, 90)
        windowz = windowx.rotate(pd.AxisEnum.YAXIS, 90)
        body.addelement(windowx, pd.BodyOperationEnum.DIFFERENCE)
        body.addelement(windowy, pd.BodyOperationEnum.DIFFERENCE)
        body.addelement(windowz, pd.BodyOperationEnum.DIFFERENCE)
        m = pd.Mesh(body)
        
        m.name = "Complex01mesh"
        fname = m.name + ".stl"
        sth = pd.StlHelper(m, fname, pd.StlModeEnum.BINARY)
        sth.write()


if __name__ == "__main__":
    unittest.main()