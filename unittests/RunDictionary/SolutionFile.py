import unittest

from PyFoam.RunDictionary.SolutionFile import SolutionFile

from os import path,environ,system

from TimeDirectory import damBreakTutorial,gammaName

theSuite=unittest.TestSuite()

class SolutionFileTest(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test."+gammaName()
        system("cp "+path.join(damBreakTutorial(),"0",gammaName())+" "+self.theFile)
        
    def tearDown(self):
        system("rm "+self.theFile)
    
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
        self.theFile="/tmp/test."+gammaName()
        system("cp "+path.join(damBreakTutorial(),"0",gammaName())+" "+self.theFile)
        system("gzip -f "+self.theFile)
        
    def tearDown(self):
        system("rm "+self.theFile+".gz")
 
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
