from .Bodies import *
from .Vectors import *
from .ElementClasses import *
import numpy as np
import math as ma
from enum import Enum

class MeshTriangle(object):
    def __init__(self, pts, n):
        self._pts = pts
        self._n = n
        self._name = "noname"

    @property
    def pts(self):
        return self._pts

    @property
    def n(self):
        return self._n

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

class Mesh(object):
    def __init__(self):
        self._vertices = []
        self._triangles = []

    def _appendvertex(self, p : Vector3):
        if not p in self._vertices:
            self._vertices.append(p)

        return self._vertices.index(p)

    def _addtria(self, p1 : Vector3, p2 : Vector3, p3 : Vector3):
        """add a triangle to the mesh with the given vertices
        vertices have to be in a clockwise manner, so that a calclualted
        normal vector points to the outside of a body to which the triangle
        adds a part of the surface
        """
        idx1 = self._appendvertex(p1)
        idx2 = self._appendvertex(p2)
        idx3 = self._appendvertex(p3)
        n = (p2-p1).cross(p3-p2)
        nnorm = n.norm()
        if nnorm==0.0:
            raise Exception("Scheiße!")
        n = n/n.norm()
        self._triangles.append([idx1, idx2, idx3, n])

    def get_resolved_tria(self, idx : int) -> MeshTriangle:
        """get a triangle with resolved points an normal vector
        """
        tria = self._triangles[idx]
        n = tria[3]
        pts = []
        for i in range(0,3):
            pts.append(self._vertices[tria[i]])

        return MeshTriangle(pts, n)

    def addelement(self, element, quality = 100):
        t = type(element)
        if t is BoxElement:
            self._addbox(element)
        elif t is EllipsoidElement:
            self._addellipsoid(element, quality=quality)

    def addbody(self, body : Body):
        for bdel in body._elements:
            self.addelement(bdel.element, bdel.quality)
        #    submesh = Mesh()
        #    submesh.addelement(bdel.element, bdel.quality)
        #to be done 
        #merge the meshes accoring to bodyelement operation (ADD, SUBSTRACT) to create a new single mesh
        


    def _addbox(self, box : BoxElement):
        dx = box._dimensions[0]
        dy = box._dimensions[1]
        dz = box._dimensions[2]
        p1 = box._cent
        p2 = p1 + dx
        p3 = p1 + dy
        p4 = p1 + dz
        p5 = p3 + dz
        p6 = p2 + dz
        p7 = p6 + dy
        p8 = p3 + dx
        #front
        self._addtria(p4, p1, p2)
        self._addtria(p4, p2, p6)
        #right
        self._addtria(p6, p2, p8)
        self._addtria(p6, p8, p7)
        #left
        self._addtria(p5, p3, p1)
        self._addtria(p5, p1, p4)
        #back
        self._addtria(p7, p8, p3)
        self._addtria(p7, p3, p5)
        #top
        self._addtria(p5, p4, p6)
        self._addtria(p5, p6, p7)
        #bottom
        self._addtria(p2, p1, p3)
        self._addtria(p2, p3, p8)

    def _length(self, vec):
        return ma.sqrt(vec[0]^2 + vec[1]^2 + vec[2]^2)


    def _addellipsoid(self, ball : EllipsoidElement, quality):
        formercirc = None
        currentcirc = []
        stp = 2*ma.pi/quality
        ec = ball._cent
        rxvec = ball._dimensions[0]
        ryvec = ball._dimensions[1]
        rzvec = ball._dimensions[2]
        a = rxvec.norm()
        b = ryvec.norm()
        c = rzvec.norm()
        rxdir = rxvec/a
        rydir = ryvec/b
        rzdir = rzvec/c
        botpt = ec - rzvec
        toppt = ec + rzvec
        #range = np.arange(-ma.pi/2.0 + stp, ma.pi/2.0, stp)
        for chi in np.arange(-ma.pi/2.0 + stp, ma.pi/2.0, stp):
            formercirc = currentcirc
            currentcirc = []
            for phi in np.arange(0, 2*ma.pi, stp):
                xi = a * ma.cos(chi) * ma.cos(phi)
                yi = b * ma.cos(chi) * ma.sin(phi)
                zi = c * ma.sin(chi)
                dotpos = ec + rxdir*xi + rydir*yi + rzdir*zi #Vector3(xi, yi, zi)
                currentcirc.append(dotpos)

            for i in range(len(formercirc)-1):
                if formercirc is None:
                    leftformer = rightformer = botpt
                else:
                    leftformer = formercirc[i]
                    rightformer = formercirc[i+1]

                leftcurrent = currentcirc[i]
                rightcurrent = currentcirc[i+1]

                self._addtria(leftcurrent, leftformer, rightformer)
                if rightcurrent != leftcurrent:
                    self._addtria(rightcurrent, leftcurrent, rightformer)

        for i in range(len(formercirc)-1):
            rightcurrent = leftcurrent = toppt
            leftformer = currentcirc[i]
            rightformer = currentcirc[i+1]
            self._addtria(leftcurrent, leftformer, rightformer)

class StlModeEnum(Enum):
    ASCII = 1
    BINARY = 2

class StlHelper(object):
    def __init__(self, mesh : Mesh, filename : str, mode : StlModeEnum = StlModeEnum.ASCII):
        self._fname = filename
        self._mesh = mesh
        self._mode = mode

    def write(self):
        if self._mode == StlModeEnum.ASCII:
            self._write_ascii()
        elif self._mode == StlModeEnum.BINARY:
            self._write_binary()
        else:
            raise Exception("Unsupported stl-Mode {} in save()".format(self._mode))

    def _write_ascii(self):
        with open(self._fname, "w", encoding="UTF-8") as f:
            f.write("solid {}\n".format(self._mesh.name))
            for i in range(len(self._mesh._triangles)):
                tria = self._mesh.get_resolved_tria(i)
                f.write("\tfacet normal {:e} {:e} {:e}\n".format(tria.n.x, tria.n.y, tria.n.z))
                f.write("\t\touter loop\n")
                for vi in range(3):
                    f.write("\t\t\tvertex {:e} {:e} {:e}\n".format(tria.pts[vi].x, tria.pts[vi].y, tria.pts[vi].z))
                f.write("\t\tendloop\n")
                f.write("\tendfacet\n")        
            f.write("endsolid {}\n".format(self._mesh.name))
            

    def _write_binary(self):
        raise NotImplementedError()


