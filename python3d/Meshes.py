import sys
import struct
from .Bodies import *
from .Vectors import *
from .ElementClasses import *
from .TriTriIntersector import *
import numpy as np
import math as ma
from enum import Enum


   

class Mesh(object):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def isempty(self):
        return len(self._vertices) == 0

    def __init__(self, element : BasicElement = None, quality : float = 100):
        self._name = "noname"
        self._vertices = []
        self._triangles = []
        self._smallestpt = Vector3(sys.float_info.max, sys.float_info.max, sys.float_info.max)
        if not element is None:
            self._addelement(element, quality)

    def clone(self):
        answ = Mesh()
        for vertex in self._vertices:
            answ._vertices.append(vertex)
        for triangle in self._triangles:
            answ._triangles.append(triangle)
        
        answ._smallestpt = self._smallestpt
        return answ

    def _appendvertex(self, p : Vector3):
        if not p in self._vertices:
            self._vertices.append(p)
            if p.x < self._smallestpt.x:
                self._smallestpt.x = p.x
            if p.y < self._smallestpt.y:
                self._smallestpt.y = p.y
            if p.z < self._smallestpt.z:
                self._smallestpt.z = p.z

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
        assert nnorm > 0.0, "triangle norm vector of zero length encountered. This normally means that two of the triangle points are equal"
        n = n/nnorm #normalize the triangle norm vector
        self._triangles.append([idx1, idx2, idx3, n])

    def get_resolved_tria(self, idx : int, offset : Vector3 = Vector3(0.0, 0.0, 0.0)) -> MeshTriangle:
        """get a triangle with resolved points an normal vector
        """
        tria = self._triangles[idx]
        n = tria[3]
        pts = []
        for i in range(0,3):
            pts.append(self._vertices[tria[i]] + offset)

        return MeshTriangle(pts, n)

    def _addelement(self, element, quality = 100):
        t = type(element)
        if t is BoxElement:
            self._addbox(element)
        elif t is EllipsoidElement:
            self._addellipsoid(element, quality=quality)

    def addbody(self, body : Body):
        newmesh = self.clone()
        for bdel in body._elements:
            submesh = Mesh(bdel, bdel.quality)
            newmesh._mergemesh(submesh, bdel.operation)

        return newmesh

    def _mergemesh(self, other, operation):
        if operation is BodyOperationEnum.UNION:
            self._mergemesh_union(other)
        elif operation is BodyOperationEnum.INTERSECTION:
            self._mergemesh_intersect(other)
        elif operation is BodyOperationEnum.DIFFERENCE:
            self._mergemesh_difference(other)
        else:
            raise Exception("Unsupported merge operation {}".format(operation))

    def _mergemesh_union(self, other):
        if self.isempty:
            self._vertices = other._vertices
            self._triangles = other._triangles
        elif other.isempty:
            return

        #do something now
        

    def _mergemesh_intersect(self, other):
        if self.isempty:
            return
        elif other.isempty:
            self._vertices = []
            self._triangles = []
            self._smallestpt = Vector3(sys.float_info.max, sys.float_info.max, sys.float_info.max)
        #do something now


    def _mergemesh_difference(self, other):
        if self.isempty or other.isempty:
            return

        #do something now
        
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
        currentcirc = None
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
        for chi in np.arange(-ma.pi/2.0 + stp, ma.pi/2.0, stp):
            formercirc = currentcirc
            currentcirc = []
            for phi in np.arange(0, 2*ma.pi + stp, stp):
                xi = a * ma.cos(chi) * ma.cos(phi)
                yi = b * ma.cos(chi) * ma.sin(phi)
                zi = c * ma.sin(chi)
                dotpos = ec + rxdir*xi + rydir*yi + rzdir*zi #Vector3(xi, yi, zi)
                currentcirc.append(dotpos)

            for i in range(len(currentcirc)-1):
                if formercirc is None:
                    leftformer = rightformer = botpt
                else:
                    leftformer = formercirc[i]
                    rightformer = formercirc[i+1]

                leftcurrent = currentcirc[i]
                rightcurrent = currentcirc[i+1]

                if leftformer != rightformer:
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
        self._offset = self._mesh._smallestpt
        if self._offset.x != 0.0: self._offset.x = -self._offset.x
        if self._offset.y != 0.0: self._offset.y = -self._offset.y
        if self._offset.z != 0.0: self._offset.z = -self._offset.z

    def write(self):
        if self._mode == StlModeEnum.ASCII:
            self._write_ascii()
        elif self._mode == StlModeEnum.BINARY:
            self._write_binary()
        else:
            raise Exception("Unsupported stl-Mode {} in save()".format(self._mode))

    def _write_ascii(self):
        with open(self._fname, "wt", encoding="UTF-8") as f:
            f.write("solid {}\n".format(self._mesh.name))
            for i in range(len(self._mesh._triangles)):
                tria = self._mesh.get_resolved_tria(i, self._offset)
                f.write("\tfacet normal {:e} {:e} {:e}\n".format(tria.n.x, tria.n.y, tria.n.z))
                f.write("\t\touter loop\n")
                for vi in range(3):
                    f.write("\t\t\tvertex {:e} {:e} {:e}\n".format(tria.pts[vi].x, tria.pts[vi].y, tria.pts[vi].z))
                f.write("\t\tendloop\n")
                f.write("\tendfacet\n")        
            f.write("endsolid {}\n".format(self._mesh.name))
            

    def _write_binary(self):
        header = bytes(80)
        filler = bytes(2)
        numtrias = len(self._mesh._triangles)
        with open(self._fname, "wb") as f:
            f.write(header)
            f.write(numtrias.to_bytes(4, sys.byteorder, signed=False))
            for i in range(numtrias):
                tria = self._mesh.get_resolved_tria(i, self._offset)
                self._write_floatvec(f, tria.n)
                
                for vi in range(3):
                    self._write_floatvec(f, tria.pts[vi])

                f.write(filler)                

    def _write_floatvec(self, f, vec : Vector3):
        flts = [vec.x, vec.y, vec.z]
        s = struct.pack('f'*len(flts), *flts)
        f.write(s)
