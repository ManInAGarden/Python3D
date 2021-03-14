import numpy as np
from numpy.lib.polynomial import poly

class Vector3(object):

    def __init__(self, dta : np.array):
        self.pos = dta

    @classmethod
    def newFromXYZ(cls, x : float, y : float, z:float):
        return Vector3(np.array([x,y,z]))

    @classmethod
    def newFromList(cls, lst):
        return Vector3(np.array(lst))

    @classmethod
    def Xdir(cls):
        return Vector3([1,0,0])

    @classmethod
    def Ydir(cls):
        return Vector3([0,1,0])

    @classmethod
    def Zdir(cls):
        return Vector3([0,0,1])

    @classmethod
    def Zero(cls):
        return Vector3([0,0,0])

    @property
    def x(self):
        return self.pos[0]
    @property
    def y(self):
        return self.pos[1]
    @property
    def z(self):
        return self.pos[2]

    @x.setter
    def x(self, val):
        self.pos[0] = val
    @y.setter
    def y(self, val):
        self.pos[1] = val
    @z.setter
    def z(self, val):
        self.pos[2] = val

    
    def __str__(self):
        return "Vector3d: x:{}, y:{}, z:{}".format(self.x, self.y, self.z)

    def __repr__(self):
        return "Vector3d: x:{}, y:{}, z:{}".format(self.x, self.y, self.z)

        
    def __getitem__(self, key: int) -> float:
        if key>-1 and key <3: return self.pos[key]
        else: raise Exception("Index <{}> is out of range".format(key))

    def __len__(self):
        return 3

    def __iter__(self):
        return iter(self.pos)

    def __eq__(self, other):
        tother = type(other)
        if tother is Vector3:
            return self.pos[0] == other.pos[0] and self.pos[1] == other.pos[1] and self.pos[2] == other.pos[2]
        elif tother is list and len(other)==3:
            return self.pos[0] == other[0] and self.pos[1] == other[1] and self.pos[2] == other[2]
        else:
            return False

    def __add__(self, other):
        assert(type(other) is Vector3, "Addition of Vector3 and {} is not declared".format(type(other).__name__))
        
        return Vector3(np.add(self.pos, other.pos))

    def __sub__(self, other):
        assert(type(other) is Vector3, "Subtraction of Vector3 and {} is not declared".format(type(other).__name__))

        return Vector3(np.subtract(self.pos, other.pos))

    def __neg__(self):
        return Vector3(np.negative(self.pos))

    def __mul__(self, other):
        """scalar product of two vectors or of a vecotr with a number
        """
        tother = type(other)
        if tother is Vector3:
            return np.dot(self.pos, other.pos)
        elif tother is float or tother is int or tother is np.float64:
            return Vector3(np.dot(self.pos, other))
        else:
            raise Exception("Multiplikation not declared for types Vector3d and {}".format(tother.__name__))

    def __truediv__(self, other):
        assert(type(other) is int or type(other) is float)
        return Vector3(np.divide(self.pos, other))

    def cross(self, other):
        """vector product self x other
        """
        return Vector3(np.cross(self.pos, other.pos))

    def nparray(self, *addons):
        """get a new np.array from this vector and add the numbers in addon as
        additional dimensions to the vector
        """
        answ = np.array(list(self.pos) + list(addons))
        return answ

    def clone(self):
        return Vector3(np.copy(self.pos))

    def magnitude(self):
        return np.linalg.norm(self.pos)

    def unit(self):
        return Vector3((self.pos/np.linalg.norm(self.pos)))

class Vertex(object):
    def __init__(self, pos : Vector3, n : Vector3):
        self.pos = pos
        self.n = n

    def clone(self):
        return Vertex(self.pos.clone(), self.n.clone())

    def __eq__(self, other):
        return self.pos == other.pos and self.n == other.n



class Plane3(object):
    """a plane in R3, defined by a normal vector (n) and the distance (perpendicular to the plane) to the point (0,0,0)
    """
    def __init__(self, n : Vector3, zdist : float) -> None:
        self.n = n
        self.zdist = zdist

    @classmethod
    def newFromPoints(cls, a : Vector3, b : Vector3, c : Vector3):
        n = (b - a).cross(c - a).unit()
        return Plane3(n, n * a)

    def clone(self):
        return Plane3(self.n.clone(), self.zdist)

class Polygon(object):
    def __init__(self, vertices):
        self.vertices = vertices
        self.plane = Plane3.newFromPoints(vertices[0].pos, vertices[1].pos, vertices[2].pos)

    def clone(self):
        return Polygon(list(map(lambda vert: vert.clone(), self.vertices)))



class BTNode(object):
    def __init__(self, polygons=None):
        self.polygons = []
        self.back = None
        self.front = None
        self.plane = None

        if polygons:
            self.initpolygons(polygons)

    def initpolygons(self, pols):
        pass
    

