import unittest

from PyFoam.RunDictionary.SolutionFile import SolutionFile

from os import path,environ,remove,system
from tempfile import mktemp
from shutil import copyfile

from .TimeDirectory import damBreakTutorial,gammaName
from PyFoam.FoamInformation import foamVersionNumber

theSuite=unittest.TestSuite()

class SolutionFileTest(unittest.TestCase):
    def setUp(self):
        self.theFile=mktemp()
        if foamVersionNumber()>=(2,0):
            extension=".org"
        else:
            extension=""
        copyfile(path.join(damBreakTutorial(),"0",gammaName()+extension),self.theFile)

    def tearDown(self):
        remove(self.theFile)

    def testSolutionFileReadWrite(self):
        test=SolutionFile(path.dirname(self.theFile),path.basename(self.theFile))
        self.assertEqual(test.readInternalUniform(),"0")
        self.assertEqual(test.readBoundary("atmosphere"),"0")
        self.assertEqual(test.readDimension(),"0 0 0 0 0 0 0")
        test.replaceBoundary("atmosphere",2.3)
        self.assertEqual(test.readBoundary("atmosphere"),"2.3")
        test.replaceInternal(3.14)
        self.assertEqual(test.readInternalUniform(),"3.14")

theSuite.addTest(unittest.makeSuite(SolutionFileTest,"test"))

class SolutionFileTestZipped(unittest.TestCase):
    def setUp(self):
        self.theFile=mktemp()
        if foamVersionNumber()>=(2,0):
            extension=".org"
        else:
            extension=""
        copyfile(path.join(damBreakTutorial(),"0",gammaName()+extension),self.theFile)
        system("gzip -f "+self.theFile)

    def tearDown(self):
        remove(self.theFile+".gz")

    def testSolutionFileZippedReadWrite(self):
        test=SolutionFile(path.dirname(self.theFile),path.basename(self.theFile))
        self.assertEqual(test.readInternalUniform(),"0")
        self.assertEqual(test.readBoundary("atmosphere"),"0")
        self.assertEqual(test.readDimension(),"0 0 0 0 0 0 0")
        test.replaceBoundary("atmosphere",2.3)
        self.assertEqual(test.readBoundary("atmosphere"),"2.3")
        test.replaceInternal(3.14)
        self.assertEqual(test.readInternalUniform(),"3.14")

theSuite.addTest(unittest.makeSuite(SolutionFileTestZipped,"test"))

# Should work with Python3 and Python2
