from python3d.Polygons import Polygon2
from TestBase import TestBase
import unittest
import math
import python3d as pd

class TestBaseMeshes(TestBase):
    
    def create_star_polygon(self, spikes=5, rin=20, rout=50):
        rcur = rout
        points = []
        for i in range(2*spikes):
            phi = i * math.pi/spikes
            x = rcur*math.sin(phi)
            y = rcur*math.cos(phi)
            pt = pd.Vector2.newFromXY(x, y)
            points.append(pt)
            
            if rcur==rout:
                rcur = rin
            else:
                rcur = rout

        points.append(points[0].clone())
        line = pd.Line2(*points)

        return pd.Polygon2.newFromSketch(line)

    def create_vase_polygon(self):
        line1 = pd.Line2(pd.Vector2.newFromXY(0.0, 0.0), pd.Vector2.newFromXY(10.0,0.0)) #bot line
        line2 = pd.Line2(pd.Vector2.newFromXY(20.0, 50.0), pd.Vector2.newFromXY(0.0,50.0)) #top line
        line2.add_point(pd.Vector2.Zero()) #closing part
        bez1 = pd.Bezier2([pd.Vector2.newFromXY(10,0),
            pd.Vector2.newFromXY(25,10),
            pd.Vector2.newFromXY(30,30),
            pd.Vector2.newFromXY(20,30)], 
            quality=20)
            
        bez2 = pd.Bezier2([pd.Vector2.newFromXY(20,30),
            pd.Vector2.newFromXY(15,35),
            pd.Vector2.newFromXY(15,45),
            pd.Vector2.newFromXY(20,50)], 
            quality=20)

        return Polygon2.newFromSketch(line1, bez1, bez2, line2)

    def write_stl(self, m : pd.Mesh, mode : pd.StlModeEnum = pd.StlModeEnum.BINARY):
        fname = self.stlpath + m.name + ".stl"
        sth = pd.StlHelper(m, fname, mode)
        sth.write()
