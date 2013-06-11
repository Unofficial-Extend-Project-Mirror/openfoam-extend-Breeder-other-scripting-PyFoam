import unittest

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.TimeDirectory import TimeDirectory

from os import path,environ,system
from tempfile import mkdtemp
from shutil import rmtree,copytree

from .TimeDirectory import damBreakTutorial

theSuite=unittest.TestSuite()

class SolutionDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.theDir=mkdtemp()
        self.theFile=path.join(self.theDir,"damBreak")
        copytree(damBreakTutorial(),self.theFile)

    def tearDown(self):
        rmtree(self.theDir)

    def testSolutionDirectoryBasicContainerStuff(self):
        test=SolutionDirectory(self.theFile)
        self.assertEqual(len(test),1)
        self.assert_("0" in test)
        self.assert_("1e-7" in test)
        self.assert_("1e-4" not in test)
        self.assert_(0. in test)
        td=test["0"]
        self.assertEqual(type(td),TimeDirectory)
        self.assertRaises(KeyError,test.__getitem__,"42")
        td=test[-1]
        self.assertEqual(type(td),TimeDirectory)
        lst=[]
        for t in test:
            lst.append(t.baseName())
        self.assertEqual(len(test),len(lst))
        self.assertEqual(lst,test.getTimes())

    def testTimeCopy(self):
        test=SolutionDirectory(self.theFile)
        self.assertEqual(len(test),1)
        test["42"]=test[0]
        self.assertEqual(len(test),2)
        self.assertEqual(len(test["42"]),len(test[0]))
        del test["42"]
        self.assertEqual(len(test),1)
        del test[-1]
        self.assertEqual(len(test),0)

theSuite.addTest(unittest.makeSuite(SolutionDirectoryTest,"test"))

# Should work with Python3 and Python2
