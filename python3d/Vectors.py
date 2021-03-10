import math as ma
import numpy as np

class Vector3(object):
    """a class for storing vectors in 3d space
    """
    def __init__(self, x:float, y:float, z:float):
        self._x = x
        self._y = y
        self._z = z
        self._norm = None

    def __str__(self):
        return "Vector3d: x:{}, y:{}, z:{}, l:{}".format(self.x, self.y, self.z, self.norm())

    def __repr__(self):
        return "Vector3d: x:{}, y:{}, z:{}, l:{}".format(self.x, self.y, self.z, self.norm())

        
    def __getitem__(self, key: int) -> float:
        if key==0: return self._x
        elif key==1: return self._y
        elif key==2: return self._z
        else: raise Exception("Index <{}> is out of range".format(key))

    def __len__(self):
        return 3

    def __iter__(self):
        return iter([self._x, self._y, self._z])

    def __eq__(self, other):
        tother = type(other)
        if tother is Vector3:
            return self._x == other._x and self._y == other._y and self._z == other._z
        elif tother is list and len(other)==3:
            return self._x == other[0] and self.y == other[1] and self.z == other[2]
        else:
            return False

    def __add__(self, other):
        if not type(other) is Vector3: raise Exception("Addition of Vector3 and {} is not declared".format(type(other).__name__))

        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        """scalar product of two vectors or of a vecotr with a number
        """
        tother = type(other)
        if tother is Vector3:
            return self.x * other.x + self.y * other.y + self.z * other.z
        elif tother is float or tother is int or tother is np.float64:
            return Vector3(self.x * other, self.y * other, self.z * other)
        else:
            raise Exception("Multiplikation not declared for types Vector3d and {}".format(tother.__name__))

    def __truediv__(self, other):
        tother = type(other)
        if not (tother is float or tother is int): raise Exception("Division of Vector3 and {} is impossible".format(tother.__name__))

        return Vector3(self.x/other, self.y/other, self.z/other)

    def cross(self, other):
        """vector product self x other
        """
        return Vector3(self.y*other.z - self.z*other.y, self.z*other.x-self.x*other.z, self.x*other.y-self.y*other.x)

    def nparray(self, *addons):
        al = [self._x, self._y, self._z]
        for addon in addons:
            al.append(addon)

        return np.array(al)

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    def norm(self):
        if self._norm is not None:
            return self._norm

        self._norm = ma.sqrt(self._x**2 + self._y**2 + self._z**2)
        return self._norm

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @x.setter
    def x(self, val):
        self._x = val
        self._norm = None

    @y.setter
    def y(self, val):
        self._y = val
        self._norm = None

    @z.setter
    def z(self, val):
        self._z = val
        self._norm = None