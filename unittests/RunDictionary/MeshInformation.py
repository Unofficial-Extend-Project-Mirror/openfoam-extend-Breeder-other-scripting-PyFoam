import unittest

from PyFoam.RunDictionary.MeshInformation import MeshInformation
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.UtilityRunner import UtilityRunner

from PyFoam.Error import PyFoamException

from PyFoam.FoamInformation import oldAppConvention as oldApp

from os import path,environ
from shutil import rmtree
from tempfile import mktemp

from .TimeDirectory import damBreakTutorial

theSuite=unittest.TestSuite()

class MeshInformationTest(unittest.TestCase):
    def setUp(self):
        self.dest=mktemp()
        SolutionDirectory(damBreakTutorial(),archive=None,paraviewLink=False).cloneCase(self.dest)

        if oldApp():
            pathSpec=[path.dirname(self.dest),path.basename(self.dest)]
        else:
            pathSpec=["-case",self.dest]

        run=UtilityRunner(argv=["blockMesh"]+pathSpec,silent=True,server=False)
        run.start()

    def tearDown(self):
        rmtree(self.dest)

    def testBoundaryRead(self):
        mesh=MeshInformation(self.dest)
        self.assertEqual(mesh.nrOfFaces(),9176)
        self.assertEqual(mesh.nrOfPoints(),4746)
        self.assertEqual(mesh.nrOfCells(),2268)
        try:
            self.assertEqual(mesh.nrOfCells(),2268)
        except:
            if not oldApp():
                self.fail()

theSuite.addTest(unittest.makeSuite(MeshInformationTest,"test"))

# Should work with Python3 and Python2
