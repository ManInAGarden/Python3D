import math as ma
import numpy as np
from enum import Enum

from numpy.compat.py3k import npy_load_module

from .Polygons import *


class Transformer():
    @property
    def transmat(self):
        """property to get the transformation matrix of this transformer
        """
        return self._tmat

    def __init__(self, tmat : np.array=None):
        self._tmat = tmat

    def clone(self):
        answ = Transformer()
        if not self._tmat is None:
            answ._tmat = self._tmat.copy()
        
        return answ

    def addtrans(self, tmat : np.array):
        if self._tmat is None:
            self._tmat = tmat
            return

        self._tmat = np.dot(tmat, self._tmat)

    def transform(self, vec : Vector3):
        ivec = vec.nparray(1.0).T
        answ = np.dot(self._tmat, ivec)
        return Vector3.newFromXYZ(answ[0], answ[1], answ[2]) #we have to do it like this to get rid off the n-dimension

    def scaleinit(self, sx, sy, sz):
        tmat = np.array([
                 [sx, 0, 0, 0],
                 [0, sy, 0, 0],
                 [0, 0, sz, 0],
                 [0, 0,  0, 1]
               ])
        self.addtrans(tmat)
        return self

    def translateinit(self, tx, ty, tz):
        tmat = np.array([
                [1,0,0,tx],
                [0,1,0,ty],
                [0,0,1,tz],
                [0,0,0, 1]
               ])
        self.addtrans(tmat)
        return self

    def zrotinit(self, deg):
        rad = deg/180.0 * ma.pi
        cosi = ma.cos(rad)
        sini = ma.sin(rad)
        tmat = np.array([
                [cosi, -sini, 0, 0],
                [sini, cosi,  0, 0],
                [   0,    0,  1, 0],
                [   0,    0,  0, 1]
               ])
        self.addtrans(tmat)
        return self

    def xrotinit(self, deg):
        rad = deg/180.0 * ma.pi
        cosi = ma.cos(rad)
        sini = ma.sin(rad)
        tmat = np.array([
                [   1,    0,     0, 0],
                [   0, cosi, -sini, 0],
                [   0, sini,  cosi, 0],
                [   0,    0,     0, 1]
               ])
        self.addtrans(tmat)
        return self

    def yrotinit(self, deg):
        rad = deg/180.0 * ma.pi
        cosi = ma.cos(rad)
        sini = ma.sin(rad)
        tmat = np.array([
                [ cosi,    0,  sini, 0],
                [    0,    1,     0, 0],
                [-sini,    0,  cosi, 0],
                [    0,    0,     0, 1]
               ])
        self.addtrans(tmat)
        return self


class AxisEnum(Enum):
    XAXIS = 1
    YAXIS = 2
    ZAXIS = 3

class BasicElement:
    def __init__(self, centx, centy, centz):
        self._cent = Vector3.newFromXYZ(centx, centy, centz)

    def rotate(self, axis : AxisEnum, deg : float):
        raise NotImplementedError("rotate(): Override me!")

    def translate(self, x : float, y : float, z : float):
        raise NotImplementedError("translate(): Override me!")

    def scale(self, x : float, y : float, z : float):
        raise NotImplementedError("scale(): Override me!")

    def get_polygons(self):
        raise NotImplementedError("getpolygons(): Override me!")

    def clone(self):
        return BasicElement(self._cent.x, self._cent.x, self._cent.z)


class DimensionedElement(BasicElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, xdim=1.0, ydim=1.0, zdim=1.0):
        super().__init__(centx, centy, centz)
        self._dimensions = [Vector3.Zero() for i in range(3)]
        self._dimensions[0].x = xdim
        self._dimensions[1].y = ydim
        self._dimensions[2].z = zdim

    def clone(self):
        t = type(self)
        answ = t()
        answ._cent = self._cent.clone() # centre point vector
        answ._dimensions = []
        for dimension in self._dimensions:
            answ._dimensions.append(dimension.clone()) #dimension

        return answ

    def scale(self, sx: float = 1.0, sy: float = 1.0, sz: float = 1.0):
        answ = self.clone()

        if sx==1.0 and sy==1.0 and sz == 1.0: return answ

        tr = Transformer().scaleinit(sx, sy, sz)
        answ._cent = tr.transform(self._cent)
        for i in range(3):
            answ._dimensions[i] = tr.transform(self._dimensions[i])
        return answ

    def translate(self, tx: float = 0.0, ty: float = 0.0, tz: float = 0.0):
        answ = self.clone()

        if tx==0.0 and ty==0.0 and tz == 0.0: return answ

        tr = Transformer().translateinit(tx, ty, tz)
        answ._cent = tr.transform(self._cent)
        return answ

    def rotate(self, axis : AxisEnum, deg : float = 0.0):
        answ = self.clone()

        if deg == 0.0: return answ

        if axis is AxisEnum.XAXIS:
            trans = Transformer().xrotinit(deg)
        elif axis is AxisEnum.YAXIS:
            trans = Transformer().yrotinit(deg)
        elif axis is AxisEnum.ZAXIS:
            trans = Transformer().zrotinit(deg)
        else:
            raise Exception("Unknown axis <{}>".format(axis))

        answ._cent = trans.transform(self._cent)
        for i in range(3):
            answ._dimensions[i] = trans.transform(self._dimensions[i])

        return answ

class BoxElement(DimensionedElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, xlength=1.0, ylength=1.0, zlength=1.0):
        super().__init__(centx, centy, centz, xlength, ylength, zlength)

    def __str__(self):
        return "box centra point {}, dimensions {}".format(self._cent, self._dimensions)

class EllipsoidElement(DimensionedElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, radx=1.0, rady=1.0, radz=1.0):
        super().__init__(centx, centy, centz, radx, rady, radz)
    
    def __str__(self):
        return "ball centre {}, dimensions {}".format(self._cent, self._dimensions)

class CylinderElement(BasicElement):
    def __init__(self, cx=0.0, cy=0.0, cz=0.0, lx=0.0, ly=0.0, lz=1.0, r=1.0):
        super().__init__(cx, cy, cz)
        self._l = Vector3.newFromXYZ(lx, ly, lz)
        self._r = r

    def __str__(self):
        return "cylinder centre {}, lenvector {}, radius {}".format(self._cent, self._l, self._r)

    def clone(self):
        return CylinderElement(self._cent.x, self._cent.y, self._cent.z, self._l.x, self._l.y, self._l.z, self._r)
        
    def scale(self, sx: float = 1.0, sy: float = 1.0, sz: float = 1.0):
        answ = self.clone()

        if sx==1.0 and sy==1.0 and sz == 1.0: return answ

        tr = Transformer().scaleinit(sx, sy, sz)
        answ._cent = tr.transform(self._cent)
        answ._l = tr.transform(self._l)
        rv = Vector3.newFromXYZ(1, 1, (answ._l.x + answ._l.y)/answ._l.z).unit()*self._r
        rv = tr.transform(rv)
        answ._r = rv.magnitude()

        return answ

    def translate(self, tx: float = 0.0, ty: float = 0.0, tz: float = 0.0):
        answ = self.clone()

        if tx==0.0 and ty==0.0 and tz == 0.0: return answ

        tr = Transformer().translateinit(tx, ty, tz)
        answ._cent = tr.transform(self._cent)
        return answ

    def rotate(self, axis : AxisEnum, deg : float = 0.0):
        answ = self.clone()

        if deg == 0.0: return answ

        if axis is AxisEnum.XAXIS:
            trans = Transformer().xrotinit(deg)
        elif axis is AxisEnum.YAXIS:
            trans = Transformer().yrotinit(deg)
        elif axis is AxisEnum.ZAXIS:
            trans = Transformer().zrotinit(deg)
        else:
            raise Exception("Unknown axis <{}>".format(axis))

        answ._cent = trans.transform(self._cent)
        answ._l = trans.transform(self._l)

        return answ

class LateTransformElement(BasicElement):
    """abstract class. Derive from this when late transformation shall be used.
    Then a transformation ist oly applyed when a mesh is created from the simple geometry
    """
    def __init__(self, centx, centy, centz):
        super().__init__(centx, centy, centz)
        self._transf = Transformer().scaleinit(1,1,1) #neutral transformation

    def clone(self):
        answ = super().clone()
        answ._transf = self._transf.clone()
        return answ

class SketchedElement(LateTransformElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, extrup : float = 1.0, extrdown=0.0):
        super().__init__(centx, centy, centz)
        assert extrup > extrdown, "combination of extrude down and up makes no sense for up {} down {}".format(extrup, extrdown)
        self._extrup = extrup #up extrusion in z direction
        self._extrdown = extrdown #down extrusion in -z direction
        self._polygons = []

    def clone(self):
        answ = super().clone()
        answ._extrup = self._extrup
        answ._exrrdown = self._extrdown
        answ._polygons = list(map(lambda poly: poly.clone(), self._polygons))
        return answ

    def add_poly(self, poly : Polygon2):
        l = len(poly.vertices)
        assert l>2, "degenrate polygon2 encountered in add_poly"
        assert poly.vertices[0] == poly.vertices[l-1], "Polygon has to be closed"
        self._polygons.append(poly)

    def scale(self, sx: float = 1.0, sy: float = 1.0, sz: float = 1.0):
        answ = self.clone()

        tr = Transformer().scaleinit(sx, sy, sz)
        #answ._cent = tr.transform(self._cent)
        #answ._dimensions = list(map(tr.transform, self._dimensions))

        #extrvec = tr.transform(self._dimensions[2].unit() * self._extr) #we use dim_z as a plane-direction
        #answ._extr = extrvec.magnitude()
        self._transf.addtrans(tr.transmat)
        return answ

    def translate(self, tx: float = 0.0, ty: float = 0.0, tz: float = 0.0):
        answ = self.clone()

        if tx==0.0 and ty==0.0 and tz == 0.0: return answ

        tr = Transformer().translateinit(tx, ty, tz)
        #answ._cent = tr.transform(self._cent)
        self._transf.addtrans(tr.transmat)
        return answ

    def rotate(self, axis : AxisEnum, deg : float = 0.0):
        answ = self.clone()

        if deg == 0.0: return answ

        if axis is AxisEnum.XAXIS:
            trans = Transformer().xrotinit(deg)
        elif axis is AxisEnum.YAXIS:
            trans = Transformer().yrotinit(deg)
        elif axis is AxisEnum.ZAXIS:
            trans = Transformer().zrotinit(deg)
        else:
            raise Exception("Unknown axis <{}>".format(axis))

        #answ._cent = trans.transform(self._cent)
        #answ._dimensions = list(map(trans.transform, self._dimensions))
        self._transf.addtrans(trans.transmat)
        return answ


if __name__ == "__main__":
    b = EllipsoidElement(10, 0, 0, 10, 10, 10)
    print("initial at 10,0,0 rad 10,10,10", b)
    b = b.translate(10, 10, 10)
    print("translated by 10,10,10", b)
    b = b.scale(0.5,0.5,0.5)
    print("scaled by 0.5,0.5,0.5", b)