from python3d.ElementClasses import BasicElement, BoxElement, EllipsoidElement
from python3d.Bodies import Body, BodyOperationEnum
import sys
import struct
from .Polygons import *

from enum import Enum


class Mesh(object):
    """ class to hold Meshes consisting of Polygons stored in the nodes and leaves of a binary tree
        It allpows graphical operations like union, difference and intersection and handles the
        graphic objects accordingly.
    """

    def __init__(self, body=None):
        self.btsource = None
        if not body is None:
            self._addbody(body)

    def clone(self):
        answ = Mesh()
        answ.btsource = self.btsource.clone()

    def _addbody(self, body):
        """add an instance of Body to the mesh by extracting and adding its polygons
        """
        assert type(body) is Body, "make sure to only uses Body instances as arguments to addbodies()"
        self._add_body_polygons(body)


    def _add_body_polygons(self, body):
        for bodyelement in body:
            submesh = self._create_mesh(bodyelement.element, bodyelement.quality)
            self._mergemesh(submesh, bodyelement.operation)

    def _create_mesh(self, ele : BasicElement, quality : int):
        tele = type(ele)
        if tele is BoxElement:
            return self._create_boxmesh(ele)
        elif tele is EllipsoidElement:
            return self._create_ellipsoidmesh(ele, quality)
        else:
            raise Exception("Unknonw element type <{}> in _create_mesh".format(tele.__name__))

    def _create_boxmesh(self, box : BoxElement):
        polygons = []
     
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
        polygons.append(self._get_polygon(p4, p1, p2))
        polygons.append(self._get_polygon(p4, p2, p6))
        #right
        polygons.append(self._get_polygon(p6, p2, p8))
        polygons.append(self._get_polygon(p6, p8, p7))
        #left
        polygons.append(self._get_polygon(p5, p3, p1))
        polygons.append(self._get_polygon(p5, p1, p4))
        #back
        polygons.append(self._get_polygon(p7, p8, p3))
        polygons.append(self._get_polygon(p7, p3, p5))
        #top
        polygons.append(self._get_polygon(p5, p4, p6))
        polygons.append(self._get_polygon(p5, p6, p7))
        #bottom
        polygons.append(self._get_polygon(p2, p1, p3))
        polygons.append(self._get_polygon(p2, p3, p8))
        
        answ = Mesh()
        answ.btsource = BTNode(polygons)

        return answ

    def _get_polygon(self, *pts):
        assert len(pts)>2, "get_polygon needs at least three points to produce a valid polygon"
        n = (pts[1]-pts[0].cross(pts[2]-pts[1])).unit()
        vertices = list(map(Vertex, pts, [n]*len(pts)))
        return Polygon(vertices)

    def _mergemesh(self, mmesh, operation : BodyOperationEnum):
        if self.btsource is None:
            self.btsource = mmesh.btsource.clone()
            return

        if operation == BodyOperationEnum.UNION:
            self._unionmergemesh(mmesh)
        elif operation == BodyOperationEnum.DIFFERENCE:
            self._diffmergemesh(mmesh)
        elif operation == BodyOperationEnum.INTERSECTION:
            self._intermergemesh(mmesh)
        else:
            raise NotImplementedError("Unknown mesh operation <{}> in Mesh._mergemesh()".format(operation))


        


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
