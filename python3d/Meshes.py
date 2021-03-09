from .ElementClasses import BallElement, BoxElement
import numpy as np
import math as ma

class Mesh(object):
    def __init__(self):
        self._vertices = []
        self._triangles = []

    def _appendvertex(self, p):
        pel = list(p)
        if not pel in self._vertices:
            self._vertices.append(pel)

        return self._vertices.index(pel)

    def _addtria(self, p1, p2, p3):
        idx1 = self._appendvertex(p1)
        idx2 = self._appendvertex(p2)
        idx3 = self._appendvertex(p3)
        self._triangles.append([idx1, idx2, idx3])

    def addelement(self, element):
        t = type(element)
        if t is BoxElement:
            self._addbox(element)
        elif t is BallElement:
            self._addball(element)

    def _addbox(self, box : BoxElement):
        dx = box._dimensions[0].nparray()
        dy = box._dimensions[1].nparray()
        dz = box._dimensions[2].nparray()
        p1 = box._cent.nparray()
        p2 = p1 + dx
        p3 = p1 + dy
        p4 = p1 + dz
        p5 = p3 + dz
        p6 = p2 + dz
        p7 = p6 + dy
        p8 = p3 + dx
        self._addtria(p1, p2, p6)
        self._addtria(p1, p4, p6)
        self._addtria(p1, p3, p5)
        self._addtria(p1, p4, p6)
        self._addtria(p1, p2, p8)
        self._addtria(p1, p3, p8)
        self._addtria(p3, p8, p7)
        self._addtria(p3, p5, p7)
        self._addtria(p4, p5, p6)
        self._addtria(p4, p5, p7)
        self._addtria(p2, p6, p7)
        self._addtria(p8, p6, p7)

    def _length(self, vec):
        return ma.sqrt(vec[0]^2 + vec[1]^2 + vec[2]^2)


    def _addball(self, ball : BallElement):
        stp = 2*ma.pi/100
        c = ball._cent
        rxvec = ball._dimensions[0]
        ryvec = ball._dimensions[1]
        rzvec = ball._dimensions[2]
        for alphaz in np.arange(-ma.pi/2.0, ma.pi/2, stp/2.0):
            zd = rzvec * ma.sin(alphaz)
            circent = c + zd
            for alph in np.arange(0, 2*ma.pi, stp):
                dotpos = circent + rxvec * ma.sin(alph) + ryvec * ma.cos(alph)
                print(dotpos)





