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