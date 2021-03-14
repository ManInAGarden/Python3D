import math as ma
import numpy as np
from enum import Enum

from numpy.compat.py3k import npy_load_module

from .Polygons import *


class Transformer():
    def __init__(self, tmat : np.array=None):
        self._tmat = tmat

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


class DimensionedElement(BasicElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, xdim=1.0, ydim=1.0, zdim=1.0):
        super().__init__(centx, centy, centz)
        self._dimensions = [Vector3([0.0, 0.0, 0.0]) for i in range(3)]
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
        return "box main point{}, dimensions{}".format(self._cent, self._dimensions)

class EllipsoidElement(DimensionedElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, radx=1.0, rady=1.0, radz=1.0):
        super().__init__(centx, centy, centz, radx, rady, radz)

    
    def __str__(self):
        return "ball centre{}, dimensions{}".format(self._cent, self._dimensions)

if __name__ == "__main__":
    b = EllipsoidElement(10, 0, 0, 10, 10, 10)
    print("initial at 10,0,0 rad 10,10,10", b)
    b = b.translate(10, 10, 10)
    print("translated by 10,10,10", b)
    b = b.scale(0.5,0.5,0.5)
    print("scaled by 0.5,0.5,0.5", b)