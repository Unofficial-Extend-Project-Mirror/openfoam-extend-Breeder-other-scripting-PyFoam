import unittest

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.Error import PyFoamException
from PyFoam.FoamInformation import foamTutorials

from shutil import rmtree
from os import path
from tempfile import mktemp

theSuite=unittest.TestSuite()

class BoundaryDictTest(unittest.TestCase):
    def setUp(self):
        self.dest=mktemp()
        wholePath=path.join(foamTutorials(),"incompressible","simpleFoam","airFoil2D")
        SolutionDirectory(wholePath,archive=None,paraviewLink=False).cloneCase(self.dest)

    def tearDown(self):
        rmtree(self.dest)

    def testBoundaryRead(self):
        bnd=BoundaryDict(self.dest)
        self.assertEqual(bnd["walls"]["type"],"wall")
        self.assertEqual(bnd["walls"]["nFaces"],78)
        self.assertEqual(len(bnd.patches()),4)
        self.assertEqual(len(bnd.patches(patchType="patch")),2)

    def testBoundaryWrite(self):
        bnd=BoundaryDict(self.dest)
        test1={"type":"wall" , "nFaces":0,"startFace":666}
        bnd["testIt"]=test1
        self.assertEqual(len(bnd.patches()),5)
        bnd["walls"]=test1
        self.assertEqual(len(bnd.patches()),5)
        test2={"type":"wall" , "Faces":0,"startFace":666}
        try:
            bnd["nix"]=test2
            self.fail()
        except PyFoamException:
            pass

theSuite.addTest(unittest.makeSuite(BoundaryDictTest,"test"))
