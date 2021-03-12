from .Vectors import *
import math as ma
from enum import Enum

class MeshTriangle(object):
    def __init__(self, pts, n):
        self._pts = pts
        self._n = n

    @property
    def pts(self):
        return self._pts

    @property
    def n(self):
        return self._n

class TriTriIsectResultEnum(Enum):
    DONTINTERSECT = 1
    COPLANARINTERSECT = 2
    INTERSECT = 3
    COPLANARDONTINTERSECT = 4

class TriTriIntersectResult(object):
    def __init__(self, status : TriTriIsectResultEnum , p1 : Vector3 = None, p2 : Vector3 = None):
        self._status = status
        self._p1 = p1
        self._p2 = p2

    @property
    def status(self):
        return self._status

    @property
    def p1(self):
        return self._p1

    @property
    def p2(self):
        return self._p2

    
class TriTriIntersector(object):
    def __init__(self, t1 : MeshTriangle, t2 : MeshTriangle, epsi = None) -> None:
        self._v = t1
        self._u = t2
        self._epsi = epsi

    @property
    def v(self):
        return self._v

    @property
    def u(self):
        return self._u

    @property
    def epsi(self):
        return self._epsi

    def getisectline(self) -> TriTriIntersectResult:
        """get intersectionline for the two triangles
           returns an instance of TriTriIntersctResulst which contains a status and if status is DOINTERSECT
           also contains tow points of type Vector3 which denote the start end end point of the intersection line.
        """

        v = self.v
        u = self.u
        #compute plane equation of triangle(V0,V1,V2) //quoted from Moeller//

        d1 = -v.n * v.pts[0]
        # plane equation 1: N1.X+d1=0 
        # put U0,U1,U2 into plane equation 1 to compute signed distances to the plane //quoted from Moeller//
        du0 = v.n * u.pts[0] + d1
        du1 = v.n * u.pts[1] + d1
        du2 = v.n * u.pts[2] + d1

        if not self.epsi is None:
            if ma.fabs(du0) < self.epsi: du0 = 0.0
            if ma.fabs(du1) < self.epsi: du1 = 0.0
            if ma.fabs(du2) < self.epsi: du2 = 0.0

        du0du1=du0*du1
        du0du2=du0*du2

        if du0du1>0.0 and du0du2>0.0: #+ same sign on all of them + not equal 0 ? //quoted from Moeller//
            return TriTriIntersectResult(TriTriIsectResultEnum.DONTINTERSECT)  # no intersection occurs //quoted from Moeller//

        #compute plane of triangle (U0,U1,U2) //quoted from Moeller//
        d2= -u.n * u.pts[0]
        #plane equation 2: N2.X+d2=0 //quoted from Moeller//
        #put V0,V1,V2 into plane equation 2  //quoted from Moeller//
        dv0= u.n * v.pts[0] + d2
        dv1= u.n * v.pts[1] + d2
        dv2= u.n * v.pts[2] + d2

        if not self.epsi is None:
            if ma.fabs(dv0) < self.epsi: dv0 = 0.0
            if ma.fabs(dv1) < self.epsi: dv1 = 0.0
            if ma.fabs(dv2) < self.epsi: dv2 = 0.0
        
        dv0dv1=dv0*dv1
        dv0dv2=dv0*dv2
        
        if dv0dv1>0.0 and dv0dv2>0.0 : # same sign on all of them + not equal 0 ? //quoted from Moeller//
            return  TriTriIntersectResult(TriTriIsectResultEnum.DONTINTERSECT) # no intersection occurs //quoted from Moeller//

        # compute direction of intersection line //quoted from Moeller//
        D = v.n.cross(u.n)

        # compute and index to the largest component of D //quoted from Moeller//
        max=ma.fabs(D.x)
        index=0
        b=ma.fabs(D.y)
        c=ma.fabs(D.z)
        if b>max:
            max=b
            index=1
        if c>max:
            max=c
            index=2

        # this is the simplified projection onto L //quoted from Moeller//
        #pts in v und u is addressable by x, y, z but can also be indexed 0 is x, 1 is y, 2 is z
        #so th efollwing also works
        vp0 = v.pts[0][index]
        vp1 = v.pts[1][index]
        vp2 = v.pts[2][index]
  
        up0 = u.pts[0][index]
        up1 = u.pts[1][index]
        up2 = u.pts[2][index]

        # compute interval for triangle 1 //quoted from Moeller//
        iscoplanar,isect1,isectpointA1,isectpointA2  = self.compute_intervals_isectline(v,
                                                                        vp0,vp1,vp2,
                                                                        dv0,dv1,dv2,
                                                                        dv0dv1,dv0dv2)
        if iscoplanar:
            return self.coplanar_tri_tri(v, u)

        # compute interval for triangle 2 //quoted from Moeller//
        iscoplanar, isect2,isectpointB1,isectpointB2 = self.compute_intervals_isectline(u,
                                                                        up0,up1,up2,
                                                                        du0,du1,du2,
                                                                        du0du1,du0du2)
        #we know iscoplanar must be false here, so we don't ask again
        isect1, smallest1 = self._sort_interval(isect1)
        isect2, smallest2 = self._sort_interval(isect2)

        if isect1[1]<isect2[0] or isect2[1]<isect1[0]:
             return TriTriIntersectResult(TriTriIsectResultEnum.DONTINTERSECT)

        # at this point, we know that the triangles intersect  //quoted from Moeller//

        if isect2[0] < isect1[0]:
            if smallest1==0:
                isectpt1 = isectpointA1
            else:
                isectpt1 = isectpointA2

            if isect2[1]<isect1[1]:
                if smallest2==0:
                    isectpt2 = isectpointB2
                else:
                    isectpt2 = isectpointB1
            else:
                if smallest1==0:
                    isectpt2 = isectpointA2
                else:
                    isectpt2 = isectpointA1
        else:
            if smallest2==0:
                isectpt1 = isectpointB1
            else:
                isectpt1 = isectpointB2

            if isect2[1]>isect1[1]:
                if smallest1==0:
                    isectpt2 = isectpointA2
                else:
                    isectpt2 = isectpointA1
            else:
                if smallest2==0:
                    isectpt2 = isectpointB2
                else:
                    isectpt2 = isectpointB1

        return TriTriIntersectResult(TriTriIsectResultEnum.INTERSECT, isectpt1, isectpt2)



    def _sort_interval(self, iterv):
        answ = [None]*2
        if iterv[0] > iterv[1]:
            answ[1] = iterv[0] 
            answ[0] = iterv[1]
            smallest = 1
        else:
            answ[0] = iterv[0] 
            answ[1] = iterv[1]
            smallest = 0
        
        return answ, smallest


    def compute_intervals_isectline(self, tria : MeshTriangle, vv0 : float, vv1 : float, vv2 : float, d0 : float, d1 : float, d2 : float, d0d1 : float, d0d2 : float):
        vert0 = tria.pts[0]
        vert1 = tria.pts[1]
        vert2 = tria.pts[2]

        if d0d1 > 0.0:                                        
            # here we know that D0D2<=0.0 */                  
            # that is D0, D1 are on the same side, D2 on the other or on the plane //quoted from Moeller//
            isect, isectpoint0, isectpoint1 = self.isect2(vert2, vert0, vert1, vv2,vv0,vv1,d2,d0,d1)
        elif d0d2>0.0:
            # here we know that d0d1<=0.0 */             
            isect, isectpoint0, isectpoint1 = self.isect2(vert1, vert0, vert2,vv1,vv0,vv2,d1,d0,d2)
        elif d1 * d2 > 0.0 or d0 != 0.0:   
            #here we know that d0d1<=0.0 or that D0!=0.0 //quoted from Moeller//
            isect, isectpoint0, isectpoint1 = self.isect2(vert0, vert1, vert2,vv0,vv1,vv2,d0,d1,d2)
        elif d1!=0.0:
            isect, isectpoint0, isectpoint1 = self.isect2(vert1, vert0, vert2,vv1,vv0,vv2,d1,d0,d2)
        elif d2!=0.0:
            isect, isectpoint0, isectpoint1 = self.isect2(vert2,vert0,vert1,vv2,vv0,vv1,d2,d0,d1)
        else:
            # triangles are coplanar //quoted from Moeller//    
            return True, None, None, None

        return False, isect, isectpoint0, isectpoint1


    def isect2(self, vtx0 : Vector3, vtx1 : Vector3, vtx2 : Vector3, vv0 : float, vv1 : float, vv2 : float,
	    d0 : float, d1 : float, d2 : float):

        tmp = d0/(d0-d1)   
        isect0= vv0 + (vv1 - vv0)*tmp
        diff = (vtx1 - vtx0)*tmp
        isectpoint0 = diff + vtx0        

        tmp = d0/(d0-d2)        
        isect1 = vv0 + (vv2 - vv0)*tmp
        diff = (vtx2 - vtx0)*tmp
        isectpoint1 = vtx0 + diff

        return [isect0, isect1], isectpoint0, isectpoint1


    def coplanar_tri_tri(self, v : MeshTriangle, u : MeshTriangle) -> bool:
        # first project onto an axis-aligned plane, that maximizes the area //quoted from Moeller//
        # of the triangles, compute indices: i0,i1. //quoted from Moeller//
        A = Vector3(ma.fabs(v.n.x), ma.fabs(v.n.y), ma.fabs(v.n.z))
        if A[0]>A[1]:
            if A[0]>A[2]:
                i0 = 1      # A[0] is greatest //quoted from Moeller//
                i1 = 2
            else:
                i0 = 0      # A[2] is greatest //quoted from Moeller//
                i1 = 1
        else:   # A[0]<=A[1]  //quoted from Moeller//
            if A[2]>A[1]:
                i0 = 0 # A[2] is greatest //quoted from Moeller//
                i1 = 1                                           
            else:
                i0 = 0 # A[1] is greatest //quoted from Moeller//
                i1 = 2
                        
        # test all edges of triangle 1 against the edges of triangle 2 //quoted from Moeller//
        if self.EDGE_AGAINST_TRI_EDGES(v.pts[0], v.pts[1], u, i0, i1):
            return TriTriIntersectResult(TriTriIsectResultEnum.COPLANARINTERSECT)
            
        if self.EDGE_AGAINST_TRI_EDGES(v.pts[1], v.pts[2], u, i0, i1):
            return TriTriIntersectResult(TriTriIsectResultEnum.COPLANARINTERSECT)
        
        if self.EDGE_AGAINST_TRI_EDGES(v.pts[2], v.pts[0], u, i0, i1):
            return TriTriIntersectResult(TriTriIsectResultEnum.COPLANARINTERSECT)
            
                    
        # finally, test if tri1 is totally contained in tri2 or vice versa //quoted from Moeller//
        if self.POINT_IN_TRI(v.pts[0], u, i0, i1):
            return TriTriIntersectResult(TriTriIsectResultEnum.COPLANARINTERSECT)
        if self.POINT_IN_TRI(u.pts[0], v, i0, i1):
            return TriTriIntersectResult(TriTriIsectResultEnum.COPLANARINTERSECT)

        return TriTriIntersectResult(TriTriIsectResultEnum.COPLANARDONTINTERSECT)


    def EDGE_AGAINST_TRI_EDGES(self, V0 : Vector3, V1 : Vector3, u : MeshTriangle, i0, i1):
        #float Ax,Ay,Bx,By,Cx,Cy,e,d,f
        Ax = V1[i0] - V0[i0]
        Ay = V1[i1] - V0[i1]                            
        # test edge U0,U1 against V0,V1 */          
        if self.EDGE_EDGE_TEST(V0, u.pts[0], u.pts[1], i0, i1, Ax, Ay):
            return True
        # test edge U1,U2 against V0,V1 */         
        if self.EDGE_EDGE_TEST(V0, u.pts[1], u.pts[2], i0, i1, Ax, Ay):               
            return True
        # test edge U2,U1 against V0,V1 */         
        if self.EDGE_EDGE_TEST(V0, u.pts[2], u.pts[0], i0, i1, Ax, Ay):
            return True

    def EDGE_EDGE_TEST(self, V0,U0,U1, i0, i1, Ax, Ay):                 
        Bx=U0[i0]-U1[i0]
        By=U0[i1]-U1[i1]
        Cx=V0[i0]-U0[i0]
        Cy=V0[i1]-U0[i1]
        f=Ay*Bx-Ax*By
        d=By*Cx-Bx*Cy                      
        if (f>0 and d>=0 and d<=f) or (f<0 and d<=0 and d>=f):
            e=Ax*Cy-Ay*Cx
            if f>0:
                if e>=0 and e<=f: return True
            else:                        
                if e<=0 and e>=f: return True

        return False

    def POINT_IN_TRI(self, V0 : Vector3,u : MeshTriangle, i0, i1) -> bool:
        #float a,b,c,d0,d1,d2;                     \
        # is T1 completly inside T2? */          \
        # check if V0 is inside tri(U0,U1,U2) */ \
        a = u.pts[1][i1] - u.pts[0][i1]
        b = -(u.pts[1][i0] - u.pts[0][i0])
        c = -a*u.pts[0][i0] - b*u.pts[0][i1]
        d0 = a*V0[i0]+b*V0[i1]+c
                              
        a = u.pts[2][i1] - u.pts[1][i1]
        b = -(u.pts[2][i0] - u.pts[1][i0])
        c = -a*u.pts[1][i0]-b*u.pts[1][i1]
        d1 = a*V0[i0]+b*V0[i1]+c
               
        a = u.pts[0][i1] - u.pts[2][i1]
        b = -(u.pts[0][i0] - u.pts[2][i0]);                       \
        c = -a*u.pts[2][i0] - b*u.pts[2][i1]
        d2 = a*V0[i0] + b*V0[i1] + c
        if d0*d1>0.0:
            if d0*d2>0.0: return True

        return False

  

