from .ElementClasses import *
from .Bodies import *
import sys
import struct
from .Polygons import *

import mapbox_earcut as mbe

from enum import Enum


class Mesh(object):
    """ class to hold Meshes consisting of Polygons stored in the nodes and leaves of a binary tree
        It allpows graphical operations like union, difference and intersection and handles the
        graphic objects accordingly.
    """

    def __init__(self, body=None):
        self.btsource = None
        self.name = "unknkown"
        if not body is None:
            self._addbody(body)

    def clone(self):
        answ = Mesh()
        answ.btsource = self.btsource.clone()

    def get_all_polygons(self) -> list:
        """get all polygons from the bt recursively
        """
        if self.btsource is None:
            return []

        return self.btsource.get_deep_polygons()

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
        elif tele is CylinderElement:
            return self._create_cylindermesh(ele, quality)
        elif tele is SketchedElement:
            return self._create_sketchmesh(ele, quality)
        else:
            raise Exception("Unknonw element type <{}> in _create_mesh".format(tele.__name__))

    def _create_sketchmesh(self, skel : SketchedElement, quality):
        polygons = []
        tr = skel._transf
        botcpt = skel._cent + Vector3.Zdir() * skel._extrdown #botton centre point of the 2d sektch
        topcpt = skel._cent + Vector3.Zdir() * skel._extrup #top centre point of 2d sketch
        #note: extrdown or extrup may also be negative to extrude below or up to a point below the sketch!

        flatpoly2s = self._create_flatsketch_mesh(skel._polygons) #for top and bottom in 2D unscaled

        toppolys = []
        for poly2 in flatpoly2s:
            toppolys.append(self._gettransferred3poly(tr, poly2, topcpt)) #top polys

        botpolys = []
        for poly2 in flatpoly2s:
            botpolys.append(self._gettransferred3poly(tr, poly2, botcpt).turnover()) #bottom polys

        polygons.extend(toppolys)
        polygons.extend(botpolys)

        innerpoly = False
        for poly in skel._polygons:
            voldbot = None
            voldtop = None
            for vert in poly.vertices:
                pt = vert.pos
                currbotpt = tr.transform(Vector3.newFromXYZ(pt.x, pt.y, 0) + botcpt)
                vcurrbot = Vertex3(currbotpt)
                currtoppt = tr.transform(Vector3.newFromXYZ(pt.x, pt.y, 0) + topcpt)
                vcurrtop = Vertex3(currtoppt)
                
                if not voldbot is None:
                    if voldtop == vcurrtop or voldbot == vcurrbot: #eliminate connection points in polygons
                        continue
                    
                    if innerpoly:
                        polygons.append(Polygon3([vcurrtop, vcurrbot, voldbot]))
                        polygons.append(Polygon3([ voldtop, vcurrtop, voldbot]))
                    else:
                        polygons.append(Polygon3([voldbot, vcurrbot, vcurrtop]))
                        polygons.append(Polygon3([voldbot, vcurrtop, voldtop]))

                voldbot = vcurrbot
                voldtop = vcurrtop

            innerpoly = True # any poly but the first on is an outer poly

        answ = Mesh()
        answ.btsource = BTNode(polygons)

        return answ

    def _gettransferred3poly(self, tr, p2, addvect=Vector3.Zero()):
        """Get 3 3d polygon from a2d polygon.

            tr : transformation object used to transform coordinates during the process
            addvect : vector to be added before transformation
        """
        vertices3 = []
        for vert2 in p2.vertices:
            v3 = Vector3.newFromXYZ(vert2.pos.x, vert2.pos.y, 0.0)
            v3t = tr.transform(v3 + addvect)
            vertices3.append(Vertex3.newFromXYZ(v3t.x, v3t.y, v3t.z))

        return Polygon3(vertices3)


    def _create_flatsketch_mesh(self, polygons):
        vertices = []
        rings = []
        pc = 0
        for poly in polygons:
            for vertex in poly.vertices:
                vertices.append([vertex.pos.x, vertex.pos.y])

            pc += len(poly.vertices)
            rings.append(pc)

        vnp = np.array(vertices).reshape(-1, 2)
        ress = mbe.triangulate_float64(vnp, rings)
        answ = []
        for i in range(0,len(ress),3):
            answ.append(Polygon2.newFromList([vnp[ress[i]], vnp[ress[i+1]], vnp[ress[i+2]]]))

        return answ

    def _create_ellipsoidmesh(self, ball : EllipsoidElement, quality):
        polygons = []
        formercirc = None
        currentcirc = None
        stp = 2*ma.pi/quality
        ec = ball._cent
        rxvec = ball._dimensions[0]
        ryvec = ball._dimensions[1]
        rzvec = ball._dimensions[2]
        a = rxvec.magnitude()
        b = ryvec.magnitude()
        c = rzvec.magnitude()
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
                    polygons.append(Polygon3([Vertex3(leftcurrent), Vertex3(leftformer), Vertex3(rightformer)]))
                if rightcurrent != leftcurrent:
                    polygons.append(Polygon3([Vertex3(rightcurrent), Vertex3(leftcurrent),  Vertex3(rightformer)]))

        for i in range(len(formercirc)-1):
            rightcurrent = leftcurrent = toppt
            leftformer = currentcirc[i]
            rightformer = currentcirc[i+1]
            polygons.append(Polygon3([Vertex3(leftcurrent), Vertex3(leftformer), Vertex3(rightformer)]))

        answ = Mesh()
        answ.btsource = BTNode(polygons)

        return answ

    def _create_cylindermesh(self, cyl : CylinderElement, quality):
        """create a mesh for a cylinder element
        """
        rx, ry = self._findperpendicularnormals(cyl._l)
        rx = rx * cyl._r
        ry = ry * cyl._r
        #top
        polygons = self._create_circle_mesh(cyl._cent + (cyl._l * 0.5), rx, ry, quality)

        #rounded shell
        lmag = cyl._l.magnitude()
        lstp = lmag / quality
        formerpts = None
        for cf in np.arange(-0.5, 0.5 + 1/quality, 1/quality):
            cv = (cyl._l - cyl._cent) * cf
            cstp = 2 * ma.pi/quality
            currentpts = []
            for phi in np.arange(0.0, 2* ma.pi + cstp, cstp):
                currentpts.append(cv + rx*ma.cos(phi) + ry*ma.sin(phi))

            if not formerpts is None:
                for i in range(len(currentpts)-1):
                    leftcurrent = Vertex3(currentpts[i])
                    rightcurrent = Vertex3(currentpts[i+1])
                    leftformer = Vertex3(formerpts[i])
                    rightformer = Vertex3(formerpts[i+1])
                    polygons.append(Polygon3([leftformer, rightcurrent, leftcurrent]))
                    polygons.append(Polygon3([leftformer, rightformer, rightcurrent]))

            formerpts = currentpts

        #bottom
        botpolys = self._create_circle_mesh(cyl._cent - (cyl._l * 0.5), rx, ry, quality)
        for botpoly in botpolys:
            botpoly.turnover()
        polygons.extend(botpolys)

        answ = Mesh()
        answ.btsource = BTNode(polygons)

        return answ
        
    def _findperpendicularnormals(self, dirv : Vector3):
        """find two vector which are both perpendicular to the vector dirv and perpendicular to each other
        """
        ndir = dirv.unit()
        basedir = Vector3.Xdir()
        xtst = ndir * basedir
        if xtst > 0.1:
            basedir = Vector3.Ydir()
            
        v1 = basedir.cross(ndir)
        v2 = ndir.cross(v1)

        return v1.unit(), v2.unit()

    def _create_circle_mesh(self, centre : Vector3, rx : Vector3, ry : Vector3, quality : int):
        """create a submesh for  a circle in R3
        """
        polygons = []
        stp = 2 * ma.pi/quality
        oldpt = None
        cvert = Vertex3(centre)
        for phi in np.arange(0.0, 2* ma.pi + stp, stp):
            pt = centre + rx*ma.cos(phi) + ry*ma.sin(phi) 
            if not oldpt is None:
                poly = Polygon3([Vertex3(oldpt), Vertex3(pt), cvert])
                polygons.append(poly)
            oldpt = pt

        return polygons

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
        vertices = list(map(Vertex3, pts))
        return Polygon3(vertices)

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


    def _unionmergemesh(self, other):
        """merge another mesh to self and apply the union operation
        """
        a = self.btsource.clone()
        b = other.btsource.clone()
        a.cutout(b)
        b.cutout(a)
        b.invert()
        b.cutout(a)
        b.invert()
        a.addtree(b)
        self.btsource = a

    def _diffmergemesh(self, other):
        """merge another mesh to self and apply the union operation
        """
        a = self.btsource.clone()
        b = other.btsource.clone()
        a.invert()
        a.cutout(b)
        b.cutout(a)
        b.invert()
        b.cutout(a)
        b.invert()
        a.addtree(b)
        a.invert()
        self.btsource = a

    def _intermergemesh(self, other):
        a = self.btsource.clone()
        b = other.btsource.clone()
        a.invert()
        b.cutout(a)
        b.invert()
        a.cutout(b)
        b.cutout(a)
        a.addtree(b)
        a.invert()
        self.btsource = a

        


class StlModeEnum(Enum):
    ASCII = 1
    BINARY = 2

class StlHelper(object):
    def __init__(self, mesh : Mesh, filename : str, mode : StlModeEnum = StlModeEnum.ASCII):
        self._fname = filename
        self._mesh = mesh
        self._mode = mode
        self.polygons = self._mesh.get_all_polygons()
        self._offset = self._get_offset()
        

    def _get_offset(self):
        smallest = Vector3.newFromList([sys.float_info.max]*3)
        for poly in self.polygons:
            for vert in poly.vertices:
                for i in range(3):
                    if vert.pos[i] < smallest[i]: smallest[i] = vert.pos[i]

        return smallest

    def write(self):
        self.triangularize()

        if self._mode == StlModeEnum.ASCII:
            self._write_ascii()
        elif self._mode == StlModeEnum.BINARY:
            self._write_binary()
        else:
            raise Exception("Unsupported stl-Mode {} in save()".format(self._mode))

    def triangularize(self):
        """polygons may have more then 3 vertices
            stl only allows triangles ...
        """
        newpolygons = []
        for poly in self.polygons:
            newpolygons.extend(poly.to_triangles())

        self.polygons = newpolygons

    def _write_ascii(self):
        with open(self._fname, "wt", encoding="UTF-8") as f:
            f.write("solid {}\n".format(self._mesh.name))
            for poly in self.polygons:
                f.write("\tfacet normal {:e} {:e} {:e}\n".format(poly.plane.n.x, poly.plane.n.y, poly.plane.n.z))
                f.write("\t\touter loop\n")
                i = 0
                for vert in poly.vertices:
                    i += 1
                    if i > 3: raise Exception("polygon with more than 3 vertices encountered!!!")
                    myv = vert.pos - self._offset
                    f.write("\t\t\tvertex {:e} {:e} {:e}\n".format(myv.x,myv.y,myv.z))
                f.write("\t\tendloop\n")
                f.write("\tendfacet\n")        
            f.write("endsolid {}\n".format(self._mesh.name))
            

    def _write_binary(self):
        header = bytes(80)
        filler = bytes(2)
        numtrias = len(self.polygons)
        with open(self._fname, "wb") as f:
            f.write(header)
            f.write(numtrias.to_bytes(4, sys.byteorder, signed=False))
            for poly in self.polygons:
                self._write_floatvec(f, poly.plane.n)
                
                ct = 0
                for vert in poly.vertices:
                    ct += 1
                    if ct > 3: raise Exception("Polygon with more then 3 vertices encountered in _write_binary()")
                    self._write_floatvec(f, vert.pos)

                f.write(filler)                

    def _write_floatvec(self, f, vec : Vector3):
        flts = [vec.x, vec.y, vec.z]
        s = struct.pack('f'*len(flts), *flts)
        f.write(s)
