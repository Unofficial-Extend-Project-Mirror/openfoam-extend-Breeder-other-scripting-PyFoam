import unittest

from PyFoam.RunDictionary.MeshInformation import MeshInformation
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Execution.UtilityRunner import UtilityRunner

from os import path,environ,system

theSuite=unittest.TestSuite()

class MeshInformationTest(unittest.TestCase):
    def setUp(self):
        self.dest="/tmp/TestDamBreak"
        SolutionDirectory(path.join(environ["FOAM_TUTORIALS"],"interFoam","damBreak"),archive=None,paraviewLink=False).cloneCase(self.dest)
        run=UtilityRunner(argv=["blockMesh",path.dirname(self.dest),path.basename(self.dest)],silent=True,server=False)
        run.start()
        
    def tearDown(self):
        system("rm -rf "+self.dest)
    
    def testBoundaryRead(self):
        mesh=MeshInformation(self.dest)
        self.assertEqual(mesh.nrOfFaces(),9176)
        self.assertEqual(mesh.nrOfPoints(),4746)
        try:
            self.assertEqual(mesh.nrOfCells(),666)
            self.fail()
        except "NotImplemented":
            pass
        
theSuite.addTest(unittest.makeSuite(MeshInformationTest,"test"))
