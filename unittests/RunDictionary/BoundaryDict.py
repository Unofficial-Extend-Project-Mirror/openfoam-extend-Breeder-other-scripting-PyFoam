import unittest

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.Error import PyFoamException

from shutil import rmtree

from tempfile import mktemp

from .TimeDirectory import damBreakTutorial

theSuite=unittest.TestSuite()

class BoundaryDictTest(unittest.TestCase):
    def setUp(self):
        self.dest=mktemp()
        SolutionDirectory(damBreakTutorial(),archive=None,paraviewLink=False).cloneCase(self.dest)

    def tearDown(self):
        rmtree(self.dest)

    def testBoundaryRead(self):
        bnd=BoundaryDict(self.dest)
        self.assertEqual(bnd["leftWall"]["type"],"wall")
        self.assertEqual(bnd["leftWall"]["nFaces"],50)
        self.assertEqual(len(bnd.patches()),5)
        self.assertEqual(len(bnd.patches(patchType="wall")),3)

    def testBoundaryWrite(self):
        bnd=BoundaryDict(self.dest)
        test1={"type":"wall" , "nFaces":0,"startFace":666}
        bnd["testIt"]=test1
        self.assertEqual(len(bnd.patches()),6)
        bnd["leftWall"]=test1
        self.assertEqual(len(bnd.patches()),6)
        test2={"type":"wall" , "Faces":0,"startFace":666}
        try:
            bnd["nix"]=test2
            self.fail()
        except PyFoamException:
            pass

theSuite.addTest(unittest.makeSuite(BoundaryDictTest,"test"))
