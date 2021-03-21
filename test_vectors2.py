from TestBase import *
import unittest
import python3d as pd
import math

class Vectors2Test(TestBase):
    def test_vectoraddition(self):
        v1 = pd.Vector2.Zero()
        v2 = pd.Vector2.newFromList([1.0, 2.0])
        v3 = v2 + v1
        self.assertEqual(v2, v3)
        v4 = v2 + v2
        self.assertEqual(pd.Vector2.newFromXY(2.0, 4.0), v4)


    def test_vectorsubtraction(self):
        v1 = pd.Vector2.newFromXY(3.0, 7.0)
        v2 = pd.Vector2.newFromList([1.0, 2.0])
        v3 = v1 - v2
        self.assertEqual(pd.Vector2.newFromXY(2.0, 5.0), v3)

    def test_cloning(self):
        v1 = pd.Vector2.newFromList([1.0, 2.0])
        v2 = v1.clone()
        self.assertEqual(v1, v2)
        v2.x = 12
        self.assertNotEqual(v1, v2)

    def test_length(self):
        v1 = pd.Vector2.newFromList([1.0, 1.0])
        l = v1.magnitude()
        self.assertAlmostEqual(math.sqrt(2.0), l)
        l2 = v1.magnitude()
        self.assertAlmostEqual(l, l2)
        v1.x = 12
        l3 = v1.magnitude()
        self.assertNotEqual(l, l3)
        self.assertAlmostEqual(math.sqrt(12**2+1), l3)


    def test_dotmult(self):
        v1 = pd.Vector2.newFromList([3.0, 2.0])
        v2 = v1 * 12
        self.assertEqual(pd.Vector2.newFromList([3*12, 2*12]), v2)

        v3 = v1 * v2
        self.assertEqual(v1.x*v2.x + v1.y*v2.y, v3)

        v4 = v1 * 3.0
        self.assertEqual(pd.Vector2.newFromXY(9.0, 6.0), v4)

    def test_scalar_division(self):
        v1 = pd.Vector2.newFromList([8.0, 4.0])
        v2 = v1 / 2.0
        self.assertEqual(pd.Vector2.newFromXY(4.0, 2.0), v2)

    def test_norm(self):
        v1 = pd.Vector2.newFromList([10, 0])
        magn = v1.magnitude()
        self.assertEqual(10, magn)
        u = v1.unit()
        self.assertEqual(pd.Vector2.Xdir(), u)

if __name__ == "__main__":
    unittest.main()
