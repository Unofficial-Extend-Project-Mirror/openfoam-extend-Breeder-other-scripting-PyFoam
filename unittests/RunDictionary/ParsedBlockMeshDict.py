import unittest

from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.FoamInformation import oldTutorialStructure,foamTutorials,foamVersionNumber
from os import path,environ
from tempfile import mktemp
from shutil import rmtree

theSuite=unittest.TestSuite()

def plateHoleTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"stressAnalysis")
    return path.join(prefix,"solidDisplacementFoam","plateHole")

class ParsedBlockMeshDictTest(unittest.TestCase):
    def setUp(self):
        self.dest=mktemp()
        SolutionDirectory(plateHoleTutorial(),archive=None,paraviewLink=False).cloneCase(self.dest)

    def tearDown(self):
        rmtree(self.dest)

    def testBoundaryRead(self):
        blk=ParsedBlockMeshDict(SolutionDirectory(self.dest).blockMesh())
        self.assertEqual(blk.convertToMeters(),1.)
        self.assertEqual(len(blk.vertices()),22)
        self.assertEqual(len(blk.blocks()),5)
        self.assertEqual(len(blk.patches()),6)
        self.assertEqual(len(blk.arcs()),8)
        self.assertEqual(blk.typicalLength(),1.25)
        self.assertEqual(str(blk.getBounds()),"([0.0, 0.0, 0.0], [2.0, 2.0, 0.5])")

    def testRoundtripBlockMesh(self):
        blk=ParsedBlockMeshDict(SolutionDirectory(self.dest).blockMesh())
        txt=str(blk)
        try:
            i=int(txt.split("blocks")[1].split("(")[0])
            self.assert_(False)
        except ValueError:
            pass

theSuite.addTest(unittest.makeSuite(ParsedBlockMeshDictTest,"test"))
