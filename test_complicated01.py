import unittest
from sys import setrecursionlimit
import python3d as pd
from TestBase import *
from TestBaseMeshes import *

class TestBodies(TestBaseMeshes):
    def test_tortured_cube(self):
        cube = pd.BoxElement(0, 0, 0, 50, 50, 50)
        body = pd.Body().addelement(cube)
        innerelli = pd.EllipsoidElement(rx=20, ry=20, rz=20)
        body.addelement(innerelli, pd.BodyOperationEnum.DIFFERENCE, 20)
        windowx = pd.BoxElement(0, 0, 0, 100, 20, 20)
        windowy = windowx.rotate(pd.AxisEnum.ZAXIS, 90)
        windowz = windowx.rotate(pd.AxisEnum.YAXIS, 90)
        body.addelement(windowx, pd.BodyOperationEnum.DIFFERENCE)
        body.addelement(windowy, pd.BodyOperationEnum.DIFFERENCE)
        body.addelement(windowz, pd.BodyOperationEnum.DIFFERENCE)
        m = pd.Mesh(body)
        m.name = "test_tortured_cube"

        self.write_stl(m)

    def test_starpierced_cookie(self):
        cookie = pd.CylinderElement(l=20, rx=70, ry=70)
        spoly = self.create_star_polygon() #create a star with 5 tips
        skel = pd.LineExtrudedElement(extrdown=-10, extrup=10)
        skel.add_poly(spoly)

        cyls = []
        r = 60
        #now create five cylinders
        for i in range(0, 5):
            phi = i * 2 * math.pi/5
            #cyls.append(pd.CylinderElement(lz=50, r=5).translate(r*math.sin(phi), r*math.cos(phi), 0.0))
            #or even like this
            cyls.append(pd.CylinderElement(l=50, rx=5, ry=5).translate(0.0, r, 0.0).rotate(pd.AxisEnum.ZAXIS, phi/math.pi * 180.0))

        body = pd.Body().addelement(cookie)
        body.addelement(skel, pd.BodyOperationEnum.DIFFERENCE)
        for cyl in cyls:
            body.addelement(cyl, pd.BodyOperationEnum.DIFFERENCE, 20)

        m = pd.Mesh(body)
        m.name = "test_starpierced_cookie"

        self.write_stl(m)

    def test_ball_chain(self):
        ellis = []
        for i in range(5):
            ellis.append(pd.SphereElement(r=10))
        
        body = pd.Body()
        zpos = 0
        dist = 0.0
        first = True
        for elli in ellis:
            if first:
                first = False
                zpos = elli._rz + dist
                body.addelement(elli, quality=20)
            else:
                body.addelement(elli.translate(0.0, 0.0, zpos + elli._rz + dist), quality=20)
                zpos += 2* elli._rz + dist

        cyl = pd.CylinderElement(rx=5, ry=5, l=20*len(ellis) + 20).translate(0,0, (10*len(ellis) + 20)/2)
        body.addelement(cyl, quality=30)
        body.rotate(pd.AxisEnum.YAXIS, 45)

        m = pd.Mesh(body)
        m.name = "test_ball_chain"
        self.write_stl(m)


    


if __name__ == "__main__":
    setrecursionlimit(5000)

    unittest.main()