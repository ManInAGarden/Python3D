from math import sin
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
        elif tele is EllipsoidElement or tele is SphereElement:
            return self._create_ellipsoidmesh(ele, quality)
        elif tele is CylinderElement:
            return self._create_cylindermesh(ele, quality)
        elif tele is LineExtrudedElement:
            return self._create_linexmesh(ele, quality)
        elif tele is RotateExtrudedElement:
            return self._create_rotexmesh(ele, quality)
        else:
            raise Exception("Unknonw element type <{}> in _create_mesh".format(tele.__name__))

    def _create_rotexmesh(self, rotel : RotateExtrudedElement, quality):
        polygons = []
        tr = rotel._transf
        
        if ma.fabs(rotel._stopangle - rotel._startangle) % 360.0 < 1e-9:
            dofull = True
        else:
            dofull = False

        trb = Transformer().translateinit(rotel._cent.x, rotel._cent.y, rotel._cent.z) + rotel._transf

        c3pols = self._get_contur3d(rotel) #get the contur polygons as 3d for z=0
        stp = (rotel._stopangle - rotel._startangle)/quality
        preconturs = None
        firstconturs = None
        if dofull: 
            max = quality 
        else: 
            max = quality + 1

        for i in range(max):
            phi = i * stp + rotel._startangle
            conturs = self._get_transconturs(trb, c3pols, phi)
            if firstconturs is None:
                firstconturs = conturs
            if not preconturs is None:
                for j in range(len(conturs)):
                    for k in range(len(conturs[j].vertices) - 1):
                        v1 = preconturs[j].vertices[k+1]
                        v2 = preconturs[j].vertices[k]
                        v3 = conturs[j].vertices[k]
                        self._append_if_ok(polygons, v1, v2, v3)
                        v1 = conturs[j].vertices[k]
                        v2 = conturs[j].vertices[k+1]
                        v3 = preconturs[j].vertices[k+1]
                        self._append_if_ok(polygons, v1, v2, v3)

            preconturs = conturs

        #now exactly close the conturs
        if dofull:
            for j in range(len(conturs)):
                for k in range(len(conturs[j].vertices) - 1):
                    v1 = conturs[j].vertices[k+1]
                    v2 = conturs[j].vertices[k]
                    v3 = firstconturs[j].vertices[k]
                    self._append_if_ok(polygons, v1, v2, v3)
                    v1 = firstconturs[j].vertices[k]
                    v2 = firstconturs[j].vertices[k+1]
                    v3 = conturs[j].vertices[k+1]
                    self._append_if_ok(polygons, v1, v2, v3)
        else: #we have to produce a front and a back closing part
            startlid = self._get_rota_lid(trb, rotel._polygons, rotel._startangle)
            endlid = self._get_rota_lid(trb, rotel._polygons, rotel._stopangle)
            polygons.extend(startlid)
            polygons.extend(list(map(lambda p: p.turnover(), endlid)))

        answ = Mesh()
        answ.btsource = BTNode(polygons)
        
        return answ

    def _get_rota_lid(self, trb : Transformer, polygons : list, phi : float) -> list:
        assert len(polygons)>0, "No polygons at all as argument to _get_start_lid is not OK"
        assert type(polygons[0]) is Polygon2, "Polygons for _get_start_lid must be Polygon2!!!. Got {} instead".format(type(polygons[0]).__name__)
        pol2s = self._create_flatsketch_mesh(polygons)
        rotr = Transformer().yrotinit(phi)
        rotr += trb

        return list(map(lambda pol2: rotr.transform(Polygon3.newFromPoly2inZZero(pol2)), pol2s))

    def _append_if_ok(self, polys : list, v1 : Vertex3, v2 : Vertex3, v3 : Vertex3):
        """create a polygon out of the given three vercices if they really describe a triangle
        and append that polygon to the supplied list of polygons
        """
        if v1 != v2 and v2 != v3 and v3 != v1:
            polys.append(Polygon3.newFromVertices([v1, v2, v3]))

    def _get_contur3d(self, rotel : RotateExtrudedElement) -> list:
        answ = []

        first = True
        for p2 in rotel._polygons:
            verts3 = list(map(lambda vert2: Vertex3.newFromXYZ(vert2.pos.x, vert2.pos.y, 0.0), p2.vertices))
            verts3clean = [verts3[0]]
            for i in range(1, len(verts3)):
                if not (verts3[i-1].pos.x==0 and verts3[i].pos.x == 0): #when both x und z of two consecutive positions are zero, we have a connection via the y axis! #remember z is always zero here!
                    verts3clean.append(verts3[i])

            if first:
                first = False
            else:
                verts3clean.reverse()

            answ.append(Polygon3.newFromVertices(verts3clean))
            
            
        return answ

    
    def _get_transconturs(self, trb : Transformer, pols : list, angle : float):
        answ = []
        mytr = Transformer().yrotinit(angle) + trb
        for pol in pols:
            newverts = list(map(lambda vert : Vertex3(mytr.transform(vert.pos)), pol.vertices))
            answ.append(Polygon3.newFromVertices(newverts))

        return answ

    def _create_linexmesh(self, skel : LineExtrudedElement, quality):
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
                        polygons.append(Polygon3.newFromVertices([vcurrtop, vcurrbot, voldbot]))
                        polygons.append(Polygon3.newFromVertices([ voldtop, vcurrtop, voldbot]))
                    else:
                        polygons.append(Polygon3.newFromVertices([voldbot, vcurrbot, vcurrtop]))
                        polygons.append(Polygon3.newFromVertices([voldbot, vcurrtop, voldtop]))

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

        return Polygon3.newFromVertices(vertices3)


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
        tr = ball._transf
        formercirc = None
        currentcirc = None
        stp = 2*ma.pi/quality
        phistp = stp
        ec = ball._cent
        a = ball._rx
        b = ball._ry
        c = ball._rz
        botpt = tr.transform(ec - Vector3.Zdir()*c)
        toppt = tr.transform(ec + Vector3.Zdir()*c)
        for chi in np.arange(-ma.pi/2.0 + phistp, ma.pi/2.0, phistp):
            formercirc = currentcirc
            currentcirc = []
            for i in range(quality):
                phi = i*stp
                xi = a * ma.cos(chi) * ma.cos(phi)
                yi = b * ma.cos(chi) * ma.sin(phi)
                zi = c * ma.sin(chi)
                dotpos = tr.transform(ec + Vector3.newFromXYZ(xi, yi, zi))
                if i == 0:
                    firstdotpos = dotpos

                currentcirc.append(dotpos)

            currentcirc.append(firstdotpos) #close the loop

            for i in range(len(currentcirc)-1):
                if formercirc is None:
                    leftformer = rightformer = botpt
                else:
                    leftformer = formercirc[i]
                    rightformer = formercirc[i+1]

                leftcurrent = currentcirc[i]
                rightcurrent = currentcirc[i+1]

                if leftformer != rightformer:
                    polygons.append(Polygon3.newFromVertices([Vertex3(leftcurrent), Vertex3(leftformer), Vertex3(rightformer)]))
                if rightcurrent != leftcurrent:
                    polygons.append(Polygon3.newFromVertices([Vertex3(rightcurrent), Vertex3(leftcurrent),  Vertex3(rightformer)]))

        for i in range(len(formercirc)-1):
            rightcurrent = leftcurrent = toppt
            leftformer = currentcirc[i]
            rightformer = currentcirc[i+1]
            polygons.append(Polygon3.newFromVertices([Vertex3(leftcurrent), Vertex3(leftformer), Vertex3(rightformer)]))

        answ = Mesh()
        answ.btsource = BTNode(polygons)

        return answ

    def _create_cylindermesh(self, cyl : CylinderElement, quality):
        """create a mesh for a cylinder element
        """
        rx = cyl._rx
        ry = cyl._ry
        l = cyl._l
        tr = cyl._transf
        #top
        toppolygons = self._create_circle_mesh(cyl._cent + (Vector3.Zdir() * cyl._l * 0.5), rx, ry, quality)
        polygons = []
        for poly in toppolygons:
            polygons.append(cyl._transf.transform(poly))

        #rounded shell
        formerpts = None
        zpt = cyl._cent.z - l/2
        pts_lower = []
        pts_upper = []
        for i in range(quality):
            phi = i*2*ma.pi/quality
            xpt = cyl._rx*ma.sin(phi)
            ypt = cyl._ry*ma.cos(phi)
            if i==0:
                firstxpt = xpt
                firstypt = ypt
            pts_lower.append(tr.transform(Vector3.newFromXYZ(xpt, ypt, zpt)))
            pts_upper.append(tr.transform(Vector3.newFromXYZ(xpt, ypt, zpt + l)))

        #exactly close the fullcircle - more accurate than doing the loop to i<(quality+1)
        pts_lower.append(tr.transform(Vector3.newFromXYZ(firstxpt, firstypt, zpt)))
        pts_upper.append(tr.transform(Vector3.newFromXYZ(firstxpt, firstypt, zpt + l)))

        for i in range(len(pts_lower)-1):
                leftlower = Vertex3(pts_lower[i])
                rightlower = Vertex3(pts_lower[i+1])
                leftupper = Vertex3(pts_upper[i])
                rightupper = Vertex3(pts_upper[i+1])
                polygons.append(Polygon3.newFromVertices([leftlower, leftupper, rightupper]))
                polygons.append(Polygon3.newFromVertices([rightupper, rightlower, leftlower]))

        #bottom
        botpolys = self._create_circle_mesh(cyl._cent - (Vector3.Zdir() * cyl._l * 0.5), rx, ry, quality)
        for poly in botpolys:
            polygons.append(cyl._transf.transform(poly.turnover()))

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

    def _create_circle_mesh(self, centre : Vector3, rx : float, ry : float, quality : int):
        """create a submesh for  a circle in R3
        """
        polygons = []
        oldpt = None
        cvert = Vertex3(centre)
        stp = 2*ma.pi/quality
        for i in range(quality):
            phi = i*stp
            pt = centre + Vector3.newFromXYZ(rx*ma.sin(phi), ry*ma.cos(phi), 0.0) 
            if i==0:
                firstpt = pt

            if not oldpt is None:
                poly = Polygon3.newFromVertices([cvert, Vertex3(pt), Vertex3(oldpt)])
                polygons.append(poly)
            oldpt = pt

        polygons.append(Polygon3.newFromVertices([cvert, Vertex3(firstpt), Vertex3(oldpt)])) #close the circle

        return polygons

    def _create_boxmesh(self, box : BoxElement):
        polygons = []
     
        dx = box._dimensions[0]
        dy = box._dimensions[1]
        dz = box._dimensions[2]
        p1 = box._cent - dx/2 - dy/2 - dz/2
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
        return Polygon3.newFromVertices(list(map(Vertex3, pts)))

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
        """merge another mesh to self and apply the diff operation
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
        """merge another mesh to self with the intersect operation
        """
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

    def transform(self, tr : Transformer):
        """apply a transformation to the polygons of this mesh
        """
        answ = self.clone()
        self._transnode(answ.btsource, tr)
        return answ

    def _transnode(self, btn : BTNode, tr : Transformer):
        """recursivly transform the polygons in a node"""
        btn.polygons = list(map(tr.transform, btn.polygons))
        if btn.front is not None:
            self._transnode(btn.front, tr)
        if btn.back is not None:
            self._transnode(btn.back, tr)

    def checkforconsistentrianglemesh(self):
        """check the mesh if it consists only of triangles
        """
        faulties = []
        self._checkforfaulties(self.btsource, faulties)
        return faulties

    def _checkforfaulties(self, bnode : BTNode, faulties : list):
        for pol in bnode.polygons:
            if pol.vertices is None or len(pol.vertices) != 3:
                faulties.append(pol)

        if bnode.front is not None:
            self._checkforfaulties(bnode.front, faulties)

        if bnode.back is not None:
            self._checkforfaulties(bnode.back, faulties)
                
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
