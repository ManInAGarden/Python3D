import sys

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


class TriTriIntersector(object):
    def __init__(self, t1 : MeshTriangle, t2 : MeshTriangle) -> None:
        self._t1 = t1
        self._t2 = t2
        self._rels12 = None
        self._rels21 = None

    @property
    def t1(self):
        return self._t1

    @property
    def t2(self):
        return self._t2

    def apotp(self) -> bool:
        """check if all vertices of t2 are on one side of t1 OR all vertices of t1 are on one sider of t2
        """

        if self._rels12 is None or self._rels21 is None:
            unders12, overs12, hits12, dists12 = self._getplanerels(self._t1, self._t2)
            unders21, overs21, hits21, dists21 = self._getplanerels(self._t2, self._t1)

            #cache the values for later use
            self._rels12 = (unders12, overs12, hits12, dists12)
            self._rels21 = (unders21, overs21, hits21, dists21)
        else:
            unders12, overs12, hits12 = self._rels12
            unders21, overs21, hits21 = self._rels21

        return (len(hits12)==0 and len(hits21)==0) and (len(unders12)==3 or len(overs12)==3) and (len(unders21)==3 or len(overs21)==3)

    def getinterpts(self):
        """get the vertices of an intersection line of zhe two triangles stored in this class. If no intersection 
        exists None is returned
        """
        #when all vertices of t1 are on one side of t2 and all vertices of t2 are on one side od t1 we
        #have no intersection
        #besides checking for that the method fills in some cache points we may use later on ( see tuples _rels21 and rels12)
        if self.apotp() == True:
            return None

        inter1, inter2 = self._getintervals()
        if not self._dooverlap(inter1, inter2): return None
        #to to CALCUTE THE INTERSECTION POINTS now and return them
        pass

    def _dooverlap(self, i1, i2):
        return (i1[0] <= i2[1] and i1[0] >= i2[0]) or (i1[1] <= i2[1] and i1[1] >= i2[0])
        
    def _getintervals(self):
        if self._rels12 is None or self._rels21 is None:
            self.apotp()
        T1 = self._t1 #triangle1
        T2 = self._t2 #triangle2
        D1 = T1.n.cross(T2.n) #direction of line where the two planes created by the two triangles intersect.
        P1 = []
        for pr in T1.pts:
            P1.append(D1*pr)
        P2 = []
        for pr in T2.pts:
            P2.append(D1*pr)

        dists = self._rels12[3]
        t1inter = self._calcinterval(P1, dists)
        dists = self._rels21[3]
        t2inter = self._calcinterval(P2, dists)
        return t1inter, t2inter

        
    def _calcinterval(self, P, d):
        t = [0,0,0]
        t[0] = P[0] + (P[1] - P[0]) * d[0]/(d[0]-d[1])
        t[1] = P[1] + (P[2] - P[1]) * d[1]/(d[1]-d[2])
        t[2] = P[2] + (P[0] - P[2]) * d[2]/(d[2]-d[0])
        tmin = sys.float_info.max
        tmax = sys.float_info.min
        for i in range(3):
            if t[i] < tmin: tmin = t[i]
            if t[i] > tmax: tmax = t[i]

        return tmin, tmax

    def _getplanerels(self, t1, t2):
        d2 = -t2.n * t2.pts[0]
        unders = []
        overs = []
        hits = []
        dists = []
        for i in range(3):
            dist = t2.n * t1.pts[i] + d2
            dists.append(dist)
            if dist > 0.0:
               overs.append(t1.pts[i])
            elif dist < 0.0:
                unders.append(t1.pts[i])
            else:
                hits.append(t1.pts[i])

        return unders, overs, hits, dists

