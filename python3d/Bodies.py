from .ElementClasses import *

class BodyOperationEnum(Enum):
    ADD = 1
    SUBTRACT = 2

class BodyElement(object):
    def __init__(self, element : BasicElement, operation : BodyOperationEnum = BodyOperationEnum.ADD, quality : int = 100):
        self._element = element
        self._operation = operation
        self._quality = quality

    def clone(self):
        return BodyElement(self._element.clone(), self._operation)

    @property
    def element(self):
        return self._element

    @property
    def quality(self):
        return self._quality

    def rotate(self, axis : AxisEnum, deg : float):
        self._element = self._element.rotate(axis, deg)

    def translate(self, tx : float, ty : float, tz : float):
        self._element = self._element.translate(tx, ty, tz)

    def scale(self, sx : float, sy : float, sz : float):
        self._element = self._element.scale(sx, sy, sz)


class Body(object):
    """a body basically is a list of graphical elements which can be translated, scaled, rotated like
    a single element. 
    """
    def __init__(self):
        self._elements = []

    def clone(self):
        answ = type(self)()
        for const in self._elements:
            answ._elements.append(const.clone())

        return answ

    def __getitem__(self, idx):
         return self._elements[idx]

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    def append(self, bel : BasicElement, operation : BodyOperationEnum = BodyOperationEnum.ADD, quality=100):
        pelement = BodyElement(bel, operation, quality=quality)
        self._elements.append(pelement)

    def rotate(self, axis : AxisEnum, deg : float):
        """rotate the body with all it's elements arount a giben axis by a given angle (0-360 deg)
        """
        answ = self.clone()
        for i in range(len(self._elements)):
            answ._elements[i]._element = self._elements[i].element.rotate(axis, deg)

        return answ

    def scale(self, sx : float, sy : float, sz : float):
        """ scale the body with all its elements to another size in R3
        """
        answ = self.clone()
        for i in range(len(self._elements)):
            answ._elements[i]._element = self._elements[i].element.scale(sx, sy, sz)

        return answ

    def translate(self, tx : float, ty : float, tz : float):
        """ translate the body with all its elements to another location in R3
        """
        answ = self.clone()
        for i in range(len(self._elements)):
            answ._elements[i]._element = self._elements[i].element.translate(tx, ty, tz)

        return answ