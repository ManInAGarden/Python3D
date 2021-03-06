from sys import float_info
import numpy as np
from numpy.lib.polynomial import poly
from numpy.linalg.linalg import norm
import math as ma
from enum import Enum
import mapbox_earcut as mbe


class Vector3(object):

    def __init__(self, dta : np.array):
        self.pos = dta
        t = type(dta)
        assert t is np.ndarray, "Unsupported type <{}> in init of Vector3".format(t.__name__)
        assert self.pos.size == 3, "Unsupported array lenght in init of Vector3"

    @classmethod
    def newFromXYZ(cls, x : float, y : float, z:float):
        return Vector3(np.array([x,y,z]))

    @classmethod
    def newFromList(cls, lst):
        return Vector3(np.array(lst[0:3]))

    @classmethod
    def Xdir(cls):
        return Vector3(np.array([1,0,0]))

    @classmethod
    def Ydir(cls):
        return Vector3(np.array([0,1,0]))

    @classmethod
    def Zdir(cls):
        return Vector3(np.array([0,0,1]))

    @classmethod
    def Zero(cls):
        return Vector3(np.array([0,0,0]))

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

    def __setitem__(self, key : int, value):
        if key>-1 and key <3: 
            self.pos[key] = value
        else: 
            raise Exception("Index <{}> is out of range".format(key))

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
        assert type(other) is Vector3, "Addition of Vector3 and {} is not declared".format(type(other).__name__)
        
        return Vector3(np.add(self.pos, other.pos))

    def __sub__(self, other):
        assert type(other) is Vector3, "Subtraction of Vector3 and {} is not declared".format(type(other).__name__)

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
        if self.pos[0]==0.0 and self.pos[1]==0 and self.pos[2]==0.0:
            raise Exception("Unit vector for zero vector does not exist.")
        else:
            return Vector3((self.pos/np.linalg.norm(self.pos)))

class Vertex3(object):
    """ a class for vertexes of polygons. Quite the same as Vector3 bzt with
    space for some additional methodes only applicable to vertices of polygons
    """
    def __init__(self, pos : Vector3):
        assert type(pos) is Vector3
        self.pos = pos

    @classmethod
    def newFromXYZ(cls, x, y, z):
        return Vertex3(Vector3.newFromXYZ(x,y,z))

    @classmethod
    def newFromList(cls, lst):
        return Vertex3(Vector3.newFromList(lst))

    def clone(self):
        return Vertex3(self.pos.clone())

    def __eq__(self, other):
        return self.pos == other.pos

    def __str__(self):
        return "Vertex3 {}".format(str(self.pos))

    def __repr__(self) -> str:
        return "Vertex3 x {} y {} z {}".format(self.pos.x, self.pos.y, self.pos.z)

    def getbetween(self, other, t):
        """get a position on the connection between self and other (both vertices)
        weighed by t
        """
        return Vertex3(self.pos + ((other.pos - self.pos) * t))



class Plane3(object):
    """a plane in R3, defined by a normal vector (n) and the distance (perpendicular to the plane) to the point (0,0,0)
    """
    def __init__(self, n : Vector3, zdist : float) -> None:
        self.n = n
        self.zdist = zdist

    @classmethod
    def newFromPoints(cls, a : Vector3, b : Vector3, c : Vector3):
        try:
            n = (b - a).cross(c - a).unit()
        except:
            raise Exception("Points do not span a valid plane {} {} {}".format(str(a), str(b), str(c)))

        return Plane3(n, n * a)

    def clone(self):
        return Plane3(self.n.clone(), self.zdist)

    def turnover(self):
        self.n = -self.n
        self.zdist = -self.zdist

    def splitPolygon(self, polygon, coplanarFront, coplanarBack, front, back):
        """
        Split `polygon` by this plane if needed, then put the polygon or polygon
        fragments in the appropriate lists. Coplanar polygons go into either
        `coplanarFront` or `coplanarBack` depending on their orientation with
        respect to this plane. Polygons in front or in back of this plane go into
        either `front` or `back`
        "stolen" and adapted from pycsg
        """
        epsi = 1.e-9
        COPLANAR = 0 # all the vertices are within EPSILON distance from plane
        FRONT = 1 # all the vertices are in front of the plane
        BACK = 2 # all the vertices are at the back of the plane
        SPANNING = 3 # some vertices are in front, some in the back

        # Classify each point as well as the entire polygon into one of the above
        # four classes.
        polygonType = 0
        vertexLocs = []
        
        numVertices = len(polygon.vertices)
        for i in range(numVertices):
            t = self.n * polygon.vertices[i].pos - self.zdist
            loc = -1
            if t < -epsi: 
                loc = BACK
            elif t > epsi: 
                loc = FRONT
            else: 
                loc = COPLANAR
            polygonType |= loc
            vertexLocs.append(loc)
    
        # Put the polygon in the correct list, splitting it when necessary.
        if polygonType == COPLANAR:
            normalDotPlaneNormal = self.n * polygon.plane.n
            if normalDotPlaneNormal > 0:
                coplanarFront.append(polygon)
            else:
                coplanarBack.append(polygon)
        elif polygonType == FRONT:
            front.append(polygon)
        elif polygonType == BACK:
            back.append(polygon)
        elif polygonType == SPANNING:
            f = []
            b = []
            for i in range(numVertices):
                j = (i+1) % numVertices
                ti = vertexLocs[i]
                tj = vertexLocs[j]
                vi = polygon.vertices[i]
                vj = polygon.vertices[j]
                if ti != BACK: 
                    f.append(vi)
                if ti != FRONT:
                    if ti != BACK: 
                        b.append(vi.clone())
                    else:
                        b.append(vi)
                if (ti | tj) == SPANNING:
                    # interpolation weight at the intersection point
                    t = (self.zdist - self.n * vi.pos) / (self.n * (vj.pos - vi.pos))
                    # intersection point on the plane
                    v = vi.getbetween(vj, t)
                    f.append(v)
                    b.append(v.clone())
            if len(f) >= 3: 
                front.append(Polygon3.newFromVertices(f))
            if len(b) >= 3: 
                back.append(Polygon3.newFromVertices(b))






class Vector2(object):
    def __init__(self, coord : np.array):
        t = type(coord)
        assert t is np.ndarray, "Unsupported type <{}> in init of Vector2".format(t.__name__)
        assert coord.size == 2
        self.pos = coord

    @classmethod
    def newFromXY(cls, x : float, y : float):
        return Vector2(np.array([x,y]))

    @classmethod
    def newFromList(cls, lst):
        return Vector2(np.array(lst))

    @classmethod
    def Xdir(cls):
        return Vector2(np.array([1,0]))

    @classmethod
    def Ydir(cls):
        return Vector2(np.array([0,1]))

    @classmethod
    def Zero(cls):
        return Vector2(np.array([0,0]))

    @property
    def x(self):
        return self.pos[0]
    @property
    def y(self):
        return self.pos[1]

    @x.setter
    def x(self, val):
        self.pos[0] = val
    @y.setter
    def y(self, val):
        self.pos[1] = val
    
    def __str__(self):
        return "Vector2: x:{}, y:{}".format(self.x, self.y)

    def __repr__(self):
        return "Vector2: x:{}, y:{}".format(self.x, self.y)

    def __getitem__(self, key: int) -> float:
        if key>-1 and key <2: return self.pos[key]
        else: raise Exception("Index <{}> is out of range".format(key))

    def __setitem__(self, key : int, value):
        if key>-1 and key <2: 
            self.pos[key] = value
        else: 
            raise Exception("Index <{}> is out of range".format(key))

    def __len__(self):
        return 2

    def __iter__(self):
        return iter(self.pos)

    def __eq__(self, other):
        tother = type(other)
        if tother is Vector2:
            return self.pos[0] == other.pos[0] and self.pos[1] == other.pos[1]
        elif tother is list and len(other)==2:
            return self.pos[0] == other[0] and self.pos[1] == other[1]
        else:
            return False

    def __add__(self, other):
        assert type(other) is Vector2, "Addition of Vector2 and {} is not declared".format(type(other).__name__)
        
        return Vector2(np.add(self.pos, other.pos))

    def __sub__(self, other):
        assert type(other) is Vector2, "Subtraction of Vector2 and {} is not declared".format(type(other).__name__)

        return Vector2(np.subtract(self.pos, other.pos))

    def __neg__(self):
        return Vector2(np.negative(self.pos))

    def __mul__(self, other):
        """scalar product of two vectors or of a vecotr with a number
        """
        tother = type(other)
        if tother is Vector2:
            return np.dot(self.pos, other.pos)
        elif tother is float or tother is int or tother is np.float64:
            return Vector2(np.dot(self.pos, other))
        else:
            raise Exception("Multiplikation not declared for types Vector2 and {}".format(tother.__name__))

    def __truediv__(self, other):
        return Vector2(np.divide(self.pos, other))

    def cross(self, other):
        """vector product self x other - in R2 this returns a float!
        """
        return np.cross(self.pos, other.pos)

    def nparray(self, *addons):
        """get a new np.array from this vector and add the numbers in addon as
        additional dimensions to the vector
        """
        answ = np.array(list(self.pos) + list(addons))
        return answ

    def clone(self):
        return Vector2(np.copy(self.pos))

    def magnitude(self):
        return np.linalg.norm(self.pos)

    def unit(self):
        return Vector2((self.pos/np.linalg.norm(self.pos)))


class Vertex2(object):
    """ a class for vertexes of polygons in R2. Quite the same as Vector2 but with
    room for some additional methods only applicable to vertices of polygons in R2
    """
    def __init__(self, pos : Vector2):
        self.pos = pos

    @classmethod
    def newFromXY(cls, x : float, y : float):
        return Vertex2(Vector2(np.array([x,y])))

    @classmethod
    def newFromList(cls, lst : list):
        return Vertex2(Vector2(np.array(lst)))

    def clone(self):
        return Vertex2(self.pos.clone())

    def __eq__(self, other):
        return self.pos == other.pos

    def __str__(self):
        return "Vertex2 {}".format(str(self.pos))

    def __repr__(self) -> str:
        return "Vertex2 x {} y {}".format(self.pos.x, self.pos.y)

    def getbetween(self, other, t):
        return Vertex2(self.pos + (other.pos - self.pos)*t)
        
class TangentPosEnum(Enum):
    START = 1
    END = 2
    ANGLED = 3

class Tangent2(object):
    def __init__(self, pt : Vector2, ndir : Vector2, pos : TangentPosEnum):
        self.pt = pt #the point whe the tangent starts
        self.ndir = ndir
        self.pos = pos #the position of the tangent related to the object it has been derived from

    def get_projectedpt(self, t : float) -> Vector2:
        return self.pt + self.ndir * t

class SketchPart2(object):
    def __init__(self):
        self.points = []

    def get_tangent(self, tangpos : TangentPosEnum) -> Tangent2:
        assert len(self.points) > 1, "Irreglular line with less than 2 points found"

        if tangpos is TangentPosEnum.START:
            p1 = self.points[0]
            p2 = self.points[1]
        elif tangpos is TangentPosEnum.END:
            l = len(self.points)
            p1 = self.points[l-1]
            p2 = self.points[l-2]

        return Tangent2(p1, (p2 - p1).unit(), tangpos)

    def getvertices(self):
        vertices = []
        for pt in self.points:
            vertices.append(Vertex2(pt))

        return vertices

    def get_centre(self):
        raise NotImplementedError()

    
class Line2(SketchPart2):
    """a polygon for sketching in 2d
    """
    def __init__(self, *pts):
        super().__init__()
        for pt in pts:
            self.points.append(pt)

    def get_centre(self):
        ptsum = Vector2.Zero()
        for pt in self.points:
            ptsum += pt

        return ptsum/len(self.points)

    def add_point_bydir(self, dir : Vector2, len : float) -> Vector2:
        """add a point to the end of the line in direction

            returns the added point for more convenience in subsequent calculations
        """
        pt = dir*len + self.points[-1]
        self.points.append(pt)
        return pt

    def add_point_byangle(self, angdeg : float, len : float) -> Vector2:
        """add a point to the end of the line in direction given by the supplied angle

           returns the added point for more convenience in subsequent calculations
        """
        angrad = angdeg/180*ma.pi
        pt = Vector2.newFromXY(len*ma.cos(angrad), len*ma.sin(angrad)) + self.points[-1]
        self.points.append(pt)
        return pt

    def add_point(self, pt : Vector2) -> Vector2:
        self.points.append(pt)
        return pt

    def close_line(self):
        self.points.append(self.points[0].clone())
        return self.points[-1]
        
    
class EllipticArc2(SketchPart2):
    def __init__(self, centrept : Vector2, rv : Vector2, phi1 : float, phi2 : float, quality : int =100):
        super().__init__()
        self.phis = phi1/180*ma.pi
        self.phie = phi2/180*ma.pi
        self.stp = 2*ma.pi/quality
        self.quality = quality
        self.cent = centrept
        self.rv = rv
        self.points = self._create_points()
        
    def _create_points(self):
        pts = []
        for phi in np.arange(self.phis, self.phie + self.stp, self.stp):
            pts.append(self._get_pointonarc(phi))

        return pts

    def _get_pointonarc(self, phi):
        return self.cent + Vector2.newFromXY(self.rv.x*ma.cos(phi), self.rv.y*ma.sin(phi))

    def get_centre(self):
        return self.cent

class Ellipse2(EllipticArc2):
    def __init__(self, centrept : Vector2, rv : Vector2, quality : int =100):
        super().__init__(centrept, rv, 0.0, 360, quality)
        
    def _create_points(self):
        pts = []
        for i in range(self.quality):
            phi = i*self.stp
            pts.append(self._get_pointonarc(phi))

        pts.append(pts[0].clone()) #close the circle

        return pts

    def get_tangent(self, phi : float) -> Tangent2:
        """get a tangent to the ellipse2 at a specified angle
        """
        spt = self._get_pointonarc(phi)
        #we need to find the nearest polygon point now
        dist = float_info.max
        idx = -1
        for i in range(len(self.points)):
            d = (spt - self.points[i]).magnitude()
            if dist > d: 
                dist = d
                foundidx = i

        nidx = foundidx + 1
        if nidx >= len(self.points):
            nidx = 0

        return Tangent2(self.points[idx], (self.points[nidx] - self.points[idx]).unit(), TangentPosEnum.ANGLED)
        
class Bezier2(SketchPart2):
    def __init__(self, ctrlpts, quality : int =100):
        super().__init__()
        self.ctrlpoints = ctrlpts
        self.quality = quality
        self.points = self._create_points()

    def _create_points(self):
        answ = [self.ctrlpoints[0]]
        q = self.quality - 1
        stp = 1/q
        t = stp
        for i in range(1, q):
            t = i*stp
            answ.append(self._casteljau(self.ctrlpoints, t))

        answ.append(self.ctrlpoints[-1])
        return answ

    def _casteljau(self, inp, t):
        i = 0
        s = []
        l = len(inp)
        if l==0: return None
        if l==1: return inp[0]
        assert t>=0.0 and t<=1.0, "t must be in the interval [0,1]"

        while i < l:
            if i+1 < l:
                s.append(inp[i]*(1.0-t) + inp[i+1]*t)

            i += 1

        if l >= 2:
            return self._casteljau(s, t)

    def get_tangent(self, tangpos: TangentPosEnum) -> Tangent2:
        if tangpos is TangentPosEnum.START:
            return Tangent2(self.points[0], (self.ctrlpoints[1]-self.ctrlpoints[0]).unit(), tangpos)
        elif tangpos is TangentPosEnum.END:
            return Tangent2(self.points[-1], (self.ctrlpoints[-2]-self.ctrlpoints[-1]).unit(), tangpos)
        else:
            raise Exception("Unknown tangent position {} in get_tangent of Bezier2".format(tangpos))


class PolygonTwistEnum(Enum):
    CLKWISE=1
    COUNTERCLKWISE=2
    BOTH = 3


class Polygon2(object):
    """class for polygons on surfaces (R2)
    """
    def __init__(self, vertices):
        self.vertices = vertices # vertices are expected as Vertex2
        self._cc = None #parameters to project the 2d polygon back into 3d space in case it was constructed from a 3d polygon
        self._plz = None
        self._plx = None
        self._ply = None

    @classmethod
    def newFromSketch(self, *parts):
        """get a polygon by constructing ist points from sketch parts like lines, circles, ...
        """
        vertices = []
        for part in parts:
            subvertices = part.getvertices()
            if len(vertices)>0 and vertices[-1]==subvertices[0]: subvertices = subvertices[1:]

            vertices.extend(subvertices)


        return Polygon2(vertices)

    @classmethod
    def newFromList(self, l):
        """Create a polygon from a list of values, each representing a list of two values (coordinates)
            use like : polys = Polygon2.newFromList([[0,0],[0,10],[12,9]])
            to create a polygon with three vertices
        """
        vertices = []
        for pt in l:
            vertices.append(Vertex2.newFromXY(pt[0], pt[1]))

        return Polygon2(vertices)


    def clone(self):
        answ = Polygon2(list(map(lambda vert: vert.clone(), self.vertices)))
        if not self._cc is None:
            answ._cc = self.cc 
            answ._plz = self.plz
            answ._plx = self.plx
            answ._ply = self.ply
        return answ

    def gettwist(self) -> PolygonTwistEnum :
        """get the overall twist of a polygon
            note that it can be both twist in a polygon, so hat BOTH maybe returned
            when no decision can be made.
        """
        sar = 0.0
        for i in range(0, len(self.vertices) - 1):
            x1 = self.vertices[i].pos.x
            y1 = self.vertices[i].pos.y
            x2 = self.vertices[i+1].pos.x
            y2 = self.vertices[i+1].pos.y
            sar += x1*y2 - x2*y1
        
        if sar > 0.0:
            return PolygonTwistEnum.COUNTERCLKWISE
        elif sar < 0.0:
            return PolygonTwistEnum.CLKWISE
        else:
            return PolygonTwistEnum.BOTH

    def turnover(self):
        self.vertices.reverse()
        return self


class Polygon3(object):
    """class for polygons 3d-space (R3)
    """

    @classmethod
    def newFromPoly2(cls, poly2 : Polygon2):
        assert not poly2._cc is None, "Polygon3 not reconstrucatble from this polygon2"
        cc = poly2._cc
        plx = poly2._plx
        ply = poly2._ply
        return Polygon3.newFromVertices(list(map(lambda v2 : Vertex3(cc + plx*v2.pos.x + ply*v2.pos.y), poly2.vertices)))

    @classmethod
    def newFromPoly2inZZero(cls, poly2 : Polygon2):
        verts3 = list(map(lambda v2 : Vertex3.newFromXYZ(v2.pos.x,v2.pos.y, 0.0), poly2.vertices))
        return Polygon3.newFromVertices(verts3)

    @classmethod
    def newFromPoly2Paras(cls, poly2: Polygon2, parapoly2 : Polygon2):
        assert not parapoly2._cc is None, "Polygon3 not reconstrucatble from the given parameter polygon2"
        cc = parapoly2._cc
        plx = parapoly2._plx
        ply = parapoly2._ply
        return Polygon3.newFromVertices(list(map(lambda v2 : Vertex3(cc + plx*v2.pos.x + ply*v2.pos.y), poly2.vertices)))

    @classmethod
    def newFromVertices(cls, vertices : list):
        answ = Polygon3()
        answ.vertices = vertices
        answ.plane = Plane3.newFromPoints(vertices[0].pos, vertices[1].pos, vertices[2].pos)
        return answ

    def clone(self):
        answ = Polygon3()
        answ.vertices = list(map(lambda vert: vert.clone(), self.vertices))
        answ.plane = self.plane
        return answ

    def turnover(self):
        self.vertices.reverse()
        self.plane.turnover()
        return self

    def to_triangles(self):
        """return a list of polygons (3D) describing only triangles in space
        """
        assert len(self.vertices) > 2, "Polygon with less than three vertices found"

        if len(self.vertices)==3:
            return [self] #we always return a list even though it only return the polygon itself 

        p2 = self.get_polyinplane()

        locvertices = list(map(lambda vert: [vert.pos.x, vert.pos.y], p2.vertices))
        rings = [len(p2.vertices)]
        vnp = np.array(locvertices).reshape(-1, 2)
        ress = mbe.triangulate_float64(vnp, rings)
        answ = []
        for i in range(0,len(ress),3):
            p3 = Polygon3.newFromPoly2Paras(Polygon2.newFromList([vnp[ress[i]], vnp[ress[i+1]], vnp[ress[i+2]]]),
                p2) #create a poly3 from a pol2 using the projection paramaters of another poly2
            answ.append(p3)

        return answ

    
    def get_polyinplane(self) -> Polygon2:
        """project the polygon in 2 dimensions to its own plane
        and return the resluting 2d polygon
        """
        assert len(self.vertices) > 2, "Polygon with less than two vertices found"

        cc = self.vertices[0].pos #centre of the considered system
        plz = self.plane.n #z axis
        plx = (self.vertices[1].pos - self.vertices[0].pos).unit() #x axis
        #plz = plx.cross(self.vertices[2].pos-cc).unit()
        ply = plz.cross(plx).unit() #y axis

        vert2s = []
        for v3 in self.vertices:
            v3cc = v3.pos - cc
            vert2s.append(Vertex2.newFromXY(v3cc*plx, v3cc*ply))
            assert ma.fabs(v3cc*plz)<1e-9, "Polygon is non planar!"

        answ = Polygon2(vert2s)
        answ._cc = cc #store parameters to be able to construct the original 3d polygon out og the resulting 2 polygon
        answ._plz = plz
        answ._plx = plx
        answ._ply = ply

        return answ


class BTNode(object):
    def __init__(self, polygons=None):
        self.polygons = []
        self.back = None
        self.front = None
        self.plane = None

        if polygons:
            self.buildfrompolygons(polygons)

    def clone(self):
        answ = BTNode()
        answ.polygons = list(map(lambda poly: poly.clone(), self.polygons))
        if not self.front is None:
            answ.front = self.front.clone()
        if not self.back is None:
            answ.back = self.back.clone()

        if not self.plane is None:
            answ.plane = self.plane.clone()

        return answ

    def cutout(self, other):
        """ 
        cut away from "self" everything that is inside "other"
        """
        self.polygons = other.cutout_polygons(self.polygons)
        if self.front: 
            self.front.cutout(other)
        if self.back: 
            self.back.cutout(other)

    def cutout_polygons(self, polygons):
        """ 
        Recursively remove all polygons in `polygons` that are inside this tree
        """
        if not self.plane:
            return polygons[:]

        front = []
        back = []
        for poly in polygons:
            self.plane.splitPolygon(poly, front, back, front, back)

        if self.front: 
            front = self.front.cutout_polygons(front)

        if self.back: 
            back = self.back.cutout_polygons(back)
        else:
            back = []

        front.extend(back)
        return front

    def invert(self):
        """ 
        turn over this node, so that everything inside is outside afterwards and
        everything outside is inside
        """
        for poly in self.polygons:
            poly.turnover()
        self.plane.turnover()
        if self.front: 
            self.front.invert()
        if self.back: 
            self.back.invert()
        temp = self.front
        self.front = self.back
        self.back = temp

    def addtree(self, other):
        otherpolys = other.get_deep_polygons()
        self.buildfrompolygons(otherpolys)


    def buildfrompolygons(self, polygons):
        if len(polygons) == 0:
            return
        if not self.plane: 
            self.plane = polygons[0].plane.clone()
        
        front = []
        back = []
        start = 0
        # add polygon to this node
        if len(self.polygons)==0:
            self.polygons.append(polygons[0])
            start = 1
            
        # split all other polygons using the first polygon's plane
        for poly in polygons[start:]:
            # coplanar front and back polygons go into self.polygons
            self.plane.splitPolygon(poly, self.polygons, self.polygons,
                                    front, back)
        # recursively build the tree
        if len(front) > 0:
            if not self.front:
                self.front = BTNode()
            self.front.buildfrompolygons(front)
        if len(back) > 0:
            if not self.back:
                self.back = BTNode()
            self.back.buildfrompolygons(back)

    def get_deep_polygons(self):
        """get all polygons from all nodes recursively
        """
        answ = self.polygons
        if self.front is not None:
            answ.extend(self.front.get_deep_polygons())
        if self.back is not None:
            answ.extend(self.back.get_deep_polygons())

        return answ



