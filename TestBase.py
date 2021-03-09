import unittest


class TestBase(unittest.TestCase):
    def assertVectAlmostEqual(self, exp, cand, places = 6):
        for i in range(3):
            with self.subTest(i=i):
                self.assertAlmostEqual(exp[i], cand[i], places)

    def assertMatrAlmostEqual(self, exp, cand, places = 6):
        for i in range(3):
            for j in range(3):
                try:
                    self.assertAlmostEqual(exp[i][j], cand[i][j], places)
                except AssertionError as ae:
                    raise AssertionError()