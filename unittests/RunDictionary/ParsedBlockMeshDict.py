import unittest

from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from os import path,environ,system

theSuite=unittest.TestSuite()

class ParsedBlockMeshDictTest(unittest.TestCase):
    def setUp(self):
        self.dest="/tmp/TestPlateHole"
        SolutionDirectory(path.join(environ["FOAM_TUTORIALS"],"solidDisplacementFoam","plateHole"),archive=None,paraviewLink=False).cloneCase(self.dest)

    def tearDown(self):
        system("rm -rf "+self.dest)

    def testBoundaryRead(self):
        blk=ParsedBlockMeshDict(SolutionDirectory(self.dest).blockMesh())
        self.assertEqual(blk.convertToMeters(),1.)
        self.assertEqual(len(blk.vertices()),22)
        self.assertEqual(len(blk.blocks()),5)
        self.assertEqual(len(blk.patches()),6)
        self.assertEqual(len(blk.arcs()),8)
        self.assertEqual(blk.typicalLength(),1.25)
        self.assertEqual(str(blk.getBounds()),"([0.0, 0.0, 0.0], [2.0, 2.0, 0.5])")

theSuite.addTest(unittest.makeSuite(ParsedBlockMeshDictTest,"test"))
