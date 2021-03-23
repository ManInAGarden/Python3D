from python3d.Polygons import Polygon2
import unittest


class TestBase(unittest.TestCase):

    stlpath = "stlsfromtest\\"
    
    def assertVectAlmostEqual(self, exp, cand, places = 6):
        dimexp = len(exp)
        dimcand = len(cand)
        if dimexp != dimcand:
            raise AssertionError("Dimensions of vectors are not identical {} != {}".format(dimexp, dimcand))

        self.assertVectDimmedAlmostEqual(exp, cand, dimexp, places)

    def assertMatrAlmostEqual(self, exp, cand, places = 6):
        dimexp = len(exp)
        dimcand = len(cand)
        if dimexp != dimcand:
            raise AssertionError("Main dimensions of matrices are not identical {} != {}".format(dimexp, dimcand))

        dimsubexp = len(exp)
        dimsubcand = len(cand)
        if dimsubexp != dimsubcand:
            raise AssertionError("Subdimension dimensions of matrices are not identical {} != {}".format(dimsubexp, dimsubcand))

        self.assertMatrDimmedAlmostEqual(exp, cand, [dimexp, dimsubexp], places)

    def assertVectDimmedAlmostEqual(self, exp, cand, dims, places = 6):
        for i in range(dims):
            with self.subTest(i=i):
                self.assertAlmostEqual(exp[i], cand[i], places)

    def assertMatrDimmedAlmostEqual(self, exp, cand, dims, places = 6):
        for i in range(dims[0]):
            for j in range(dims[1]):
                try:
                    self.assertAlmostEqual(exp[i][j], cand[i][j], places)
                except AssertionError as ae:
                    raise AssertionError()

    def assertPolyAlmostEqual(self, exp, cand, places = 6):
        vexp = exp.vertices
        vcand = cand.vertices
        self.assertEqual(len(vexp), len(vcand), "Number of vertices differs {} != {}".format(len(vexp), len(vcand)))
        for i in range(len(vexp)):
            self.assertVectAlmostEqual(vexp[i].pos, vcand[i].pos)

    def assertAllPolysAlmostEqual(self, exp, cand, places = 6):
        dimexp = len(exp)
        dimcand = len(cand)

        if dimexp != dimcand:
            self.assertEqual(dimexp, dimcand, "Number of polygons differs {} != {}".format(dimexp, dimcand))

        for i in range(dimexp):
            self.assertPolyAlmostEqual(exp[i], cand[i])
