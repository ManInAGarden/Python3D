from python3d.ElementClasses import Transformer
import unittest
import python3d as pd
from TestBase import *

class TestBodies(TestBase):
    def test_body_rotation(self):
        bod = pd.Body()
        cb = pd.SphereElement(r=100)
        bod.addelement(cb)
        numouter = 4
        trs = []
        trs.append(Transformer().scaleinit(1,1,1))
        for i in range(numouter):
            b = pd.SphereElement(r=10.0).translate(tx=100.0).rotate(pd.AxisEnum.ZAXIS, i*360.0/numouter)
            bod.addelement(b)
            trs.append(Transformer().translateinit(100,0,0) + Transformer().zrotinit(i*360.0/numouter))

        prot = bod.rotate(pd.AxisEnum.YAXIS, 90.0)
        prottr = Transformer().yrotinit(90)

        #test unrotated body
        for i in range(0,4):
            self.assertEqual(trs[i], bod[i].element._transf)

        #test effect of body rotation on the elements of the body
        for i in range(0,4):
            self.assertEqual(trs[i] + prottr, prot[i].element._transf)
        

if __name__ == "__main__":
    unittest.main()