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

    def __eq__(self, other):
        """two transformation objects are equal when the tow matrices are equal
        """
        return (self._tmat == other._tmat).all()

    def __add__(self, other):
        """adding transformations is interpreted as applying the tow transformations left to right resulting
        in a new transformation
        """
        return self.clone().addtrans(other._tmat)

    def clone(self):
        answ = Transformer()
        if not self._tmat is None:
            answ._tmat = self._tmat.copy()
        
        return answ

    def addtrans(self, tmat : np.array):
        """add a transformation to the transformer and s modifying the transformer to apply the former transformation
        and after that the added transformation
        """
        if self._tmat is None:
            self._tmat = tmat
            return

        self._tmat = np.dot(tmat, self._tmat)
        return self

    def transform(self, obj):
        tobj = type(obj)
        if tobj is Vector3:
            return self._transform_vect3(obj)
        elif tobj is Polygon3:
            return self._transform_poly3(obj)
        else:
            raise Exception("Unknown type {} cannot be transformed".format(tobj.__name__))

    def _transform_vect3(self, vec : Vector3):
        ivec = vec.nparray(1.0).T
        answ = np.dot(self._tmat, ivec)
        return Vector3.newFromXYZ(answ[0], answ[1], answ[2]) #we have to do it like this to get rid off the n-dimension

    def _transform_poly3(self, poly : Polygon3):
        avertices = []
        for vert in poly.vertices:
            ivec = vert.pos.nparray(1.0).T
            answ = np.dot(self._tmat, ivec)
            avertices.append(Vertex3.newFromXYZ(answ[0], answ[1], answ[2]))

        return Polygon3(avertices)

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


class _DimensionedElement(BasicElement):
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

class BoxElement(_DimensionedElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, xlength=1.0, ylength=1.0, zlength=1.0):
        super().__init__(centx, centy, centz, xlength, ylength, zlength)

    def __str__(self):
        return "box centra point {}, dimensions {}".format(self._cent, self._dimensions)


class _LateTransformElement(BasicElement):
    """abstract class. Derive from this when late transformation shall be used.
    Then a transformation ist oly applyed when a mesh is created from the simple geometry
    """
    def __init__(self, centx, centy, centz):
        super().__init__(centx, centy, centz)
        self._transf = Transformer().scaleinit(1,1,1) #neutral transformation

    def scale(self, sx: float = 1.0, sy: float = 1.0, sz: float = 1.0):
        answ = self.clone()

        tr = Transformer().scaleinit(sx, sy, sz)
        answ._transf.addtrans(tr.transmat)
        return answ

    def translate(self, tx: float = 0.0, ty: float = 0.0, tz: float = 0.0):
        answ = self.clone()

        if tx==0.0 and ty==0.0 and tz == 0.0: return answ

        tr = Transformer().translateinit(tx, ty, tz)
        answ._transf.addtrans(tr.transmat)
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

        answ._transf.addtrans(trans.transmat)
        return answ

class CylinderElement(_LateTransformElement):
    def __init__(self, cx=0.0, cy=0.0, cz=0.0, rx=1.0, ry=1.0, l=1.0):
        super().__init__(cx, cy, cz)
        self._l = l
        self._rx = rx
        self._ry = ry

    def __str__(self):
        return "cylinder centre {}, radiusx {}, radiusy {}, length {}".format(self._cent, self._rx. self._ry, self._l)

    def clone(self):
        answ = CylinderElement(self._cent.x, self._cent.y, self._cent.z, self._rx, self._ry, self._l)
        answ._transf = self._transf.clone()
        return answ
        
class EllipsoidElement(_LateTransformElement):
    def __init__(self, cx=0.0, cy=0.0, cz=0.0, rx=1.0, ry=1.0, rz=1.0):
        super().__init__(cx, cy, cz)
        self._rx = rx
        self._ry = ry
        self._rz = rz
    
    def __str__(self):
        return "ellipsoid centre {}, rx {} ry {} rz {}".format(self._cent, self._rx, self._ry, self._rz)

    def clone(self):
        answ = EllipsoidElement(self._cent.x, self._cent.y, self._cent.z, self._rx, self._ry, self._rz)
        answ._transf = self._transf.clone()
        return answ
    
class SphereElement(EllipsoidElement):
    def __init__(self, cx=0.0, cy=0.0, cz=0.0, r=1):
        super().__init__(cx, cy, cz, r, r, r)

    def __str__(self):
        return "sphere centre {}, r {} ".format(self._cent, self._rx)

    def clone(self):
        answ = SphereElement(self._cent.x, self._cent.y, self._cent.z, self._rx)
        answ._transf = self._transf.clone()
        return answ


class _SketchedElement(_LateTransformElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0):
        super().__init__(centx, centy, centz)
        self._polygons = []

    def add_poly(self, poly : Polygon2):
        l = len(poly.vertices)
        assert l>2, "degenrate polygon2 encountered in add_poly"
        assert poly.vertices[0] == poly.vertices[l-1], "Polygon has to be closed"
        #make sure polygon ist clockwise!
        twist = poly.gettwist()
        if twist is PolygonTwistEnum.CLKWISE:
            poly.turnover()
        self._polygons.append(poly)

    def _clone_polygons(self):
        return list(map(lambda poly : poly.clone(), self._polygons))


class LineExtrudedElement(_SketchedElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, extrup : float = 1.0, extrdown=0.0):
        super().__init__(centx, centy, centz)
        assert extrup > extrdown, "combination of extrude down and up makes no sense for up {} down {}".format(extrup, extrdown)
        self._extrup = extrup #up extrusion in z direction
        self._extrdown = extrdown #down extrusion in -z direction
        self._polygons = []

    def clone(self):
        answ = LineExtrudedElement(self._cent.x, self._cent.y, self._cent.z)
        answ._polygons = self._clone_polygons()
        answ._transf = self._transf.clone()
        answ._extrdown = self._extrdown
        answ._extrup = self._extrup
        return answ


class RotateExtrudedElement(_SketchedElement):
    def __init__(self, centx=0.0, centy=0.0, centz=0.0, startangle : float = 0.0, stopangle=360.0):
        super().__init__(centx, centy, centz)
        self._startangle = startangle
        self._stopangle = stopangle

    def clone(self):
        answ = RotateExtrudedElement(self._cent.x, self._cent.y, self._cent.z, self._startangle, self._stopangle)
        answ._polygons = self._clone_polygons()
        answ._transf = self._transf.clone()
        return answ
    
if __name__ == "__main__":
    b = EllipsoidElement(10, 0, 0, 10, 10, 10)
    print("initial at 10,0,0 rad 10,10,10", b)
    b = b.translate(10, 10, 10)
    print("translated by 10,10,10", b)
    b = b.scale(0.5,0.5,0.5)
    print("scaled by 0.5,0.5,0.5", b)