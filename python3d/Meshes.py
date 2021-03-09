from python3d.Vectors import Vector3
from .ElementClasses import EllipsoidElement, BoxElement
import numpy as np
import math as ma

class Mesh(object):
    def __init__(self):
        self._vertices = []
        self._triangles = []

    def _appendvertex(self, p : Vector3):
        if not p in self._vertices:
            self._vertices.append(p)

        return self._vertices.index(p)

    def _addtria(self, p1 : Vector3, p2 : Vector3, p3 : Vector3):
        idx1 = self._appendvertex(p1)
        idx2 = self._appendvertex(p2)
        idx3 = self._appendvertex(p3)
        self._triangles.append([idx1, idx2, idx3])

    def addelement(self, element, quality = 100):
        t = type(element)
        if t is BoxElement:
            self._addbox(element)
        elif t is EllipsoidElement:
            self._addellipsoid(element, quality=quality)

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
        for chi in np.arange(-ma.pi/2.0, ma.pi/2, stp/2.0):
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





