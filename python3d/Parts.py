from .Bodies import *

class Part(object):
    """basically a part is a list of bodies which can be treated like
    a single body with 3d graphic operations
    """
    def __init__(self, *bodies):
        self._bodies = []
        for body in bodies:
            self._bodies.append(body)

    def append(self, body : Body):
        self._bodies.append(body)

    def __getitem__(self, idx):
         return self._bodies[idx]

    def __len__(self):
        return len(self._bodies)

    def __iter__(self):
        return iter(self._bodies)