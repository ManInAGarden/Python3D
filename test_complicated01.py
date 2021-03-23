import unittest
import python3d as pd
from TestBase import *
from TestBaseMeshes import *

class TestBodies(TestBaseMeshes):
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
        m.name = "test_tortured_cube"

        self.write_stl(m)

    def test_starpierced_cookie(self):
        cookie = pd.CylinderElement(lz=20, r=70)
        spoly = self.create_star_polygon() #create a star with 5 tips
        skel = pd.SketchedElement(extrdown=-10, extrup=10)
        skel.add_poly(spoly)

        cyls = []
        r = 60
        #now create five cylinders
        for i in range(0, 5):
            phi = i * 2 * math.pi/5
            #cyls.append(pd.CylinderElement(lz=50, r=5).translate(r*math.sin(phi), r*math.cos(phi), 0.0))
            #or even like this
            cyls.append(pd.CylinderElement(lz=50, r=5).translate(0.0, r, 0.0).rotate(pd.AxisEnum.ZAXIS, phi/math.pi * 180.0))

        body = pd.Body().addelement(cookie)
        body.addelement(skel, pd.BodyOperationEnum.DIFFERENCE)
        for cyl in cyls:
            body.addelement(cyl, pd.BodyOperationEnum.DIFFERENCE, 20)

        m = pd.Mesh(body)
        m.name = "test_starpierced_cookie"

        self.write_stl(m)


if __name__ == "__main__":
    unittest.main()