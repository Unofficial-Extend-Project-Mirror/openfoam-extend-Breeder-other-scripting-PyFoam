import unittest

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.TimeDirectory import TimeDirectory
from PyFoam.RunDictionary.SolutionFile import SolutionFile
from PyFoam.RunDictionary.FileBasis import FileBasis

from PyFoam.FoamInformation import oldTutorialStructure,foamTutorials,foamVersionNumber
from os import path,environ,remove,system
from shutil import copytree,rmtree,copyfile
from tempfile import mktemp,mkdtemp

theSuite=unittest.TestSuite()

def damBreakTutorial():
    prefix=foamTutorials()
    if oldTutorialStructure():
        prefix=path.join(prefix,"interFoam")
    else:
        prefix=path.join(prefix,"multiphase","interFoam","laminar")
    return path.join(prefix,"damBreak")

def gammaName():
    if foamVersionNumber()<(1,6):
        return "gamma"
    elif foamVersionNumber()<(2,3):
        return "alpha1"
    else:
        return "alpha.water"

class TimeDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.theDir=mkdtemp()
        self.theFile=path.join(self.theDir,"damBreak")
        copytree(damBreakTutorial(),self.theFile)
        if foamVersionNumber()>=(2,):
            copyfile(path.join(self.theFile,"0",gammaName()+".org"),
                     path.join(self.theFile,"0",gammaName()))

    def tearDown(self):
        rmtree(self.theDir)

    def testTimeDirectoryBasicContainerStuff(self):
        test=SolutionDirectory(self.theFile)["0"]
        self.assertEqual(len(test),4)
        self.assert_(gammaName() in test)
        self.assert_("nix" not in test)
        tf=test["U"]
        self.assertEqual(type(tf),SolutionFile)
        self.assert_(FileBasis in tf.__class__.__mro__)
        self.assertRaises(KeyError,test.__getitem__,"nix")
        self.assertRaises(TypeError,test.__getitem__,42)
        lst=[]
        for v in test:
            lst.append(v.baseName())
        self.assert_(gammaName() in lst)
        self.assertEqual(len(lst),len(test))

    def testTimeDirectoryAdding(self):
        test=SolutionDirectory(self.theFile)["0"]
        self.assertEqual(len(test),4)
        test["U2"]=test["U"]
        self.assertEqual(len(test),5)
        test["nix"]=23
        self.assertEqual(len(test),6)
        del test["nix"]
        self.assertEqual(len(test),5)
        del test["U2"]
        self.assertEqual(len(test),4)

    def testTimeDirectoryCreating(self):
        self.assertEqual(len(SolutionDirectory(self.theFile)),1)
        test=TimeDirectory(self.theFile,"42",create=True)
        self.assertEqual(len(test),0)
        self.assertEqual(len(SolutionDirectory(self.theFile)),2)

theSuite.addTest(unittest.makeSuite(TimeDirectoryTest,"test"))

class TimeDirectoryTestZipped(unittest.TestCase):
    def setUp(self):
        self.theDir=mkdtemp()
        self.theFile=path.join(self.theDir,"damBreak")
        copytree(damBreakTutorial(),self.theFile)
        if foamVersionNumber()>=(2,):
            copyfile(path.join(self.theFile,"0",gammaName()+".org"),
                     path.join(self.theFile,"0",gammaName()))
        system("gzip "+path.join(self.theFile,"0",gammaName()))

    def tearDown(self):
        rmtree(self.theDir)

    def testTimeReplacingZippedFile(self):
        test=SolutionDirectory(self.theFile)["0"]
        self.assertEqual(len(test),4)
        test[gammaName()]=test[gammaName()+".org"]
        self.assertEqual(len(test),4)

theSuite.addTest(unittest.makeSuite(TimeDirectoryTestZipped,"test"))

class TimeDirectoryTestCopy(unittest.TestCase):
    def setUp(self):
        self.theDir=mkdtemp()
        self.theFile=path.join(self.theDir,"damBreak")
        copytree(damBreakTutorial(),self.theFile)
        if foamVersionNumber()>=(2,):
            copyfile(path.join(self.theFile,"0",gammaName()+".org"),
                     path.join(self.theFile,"0",gammaName()))

    def tearDown(self):
        rmtree(self.theDir)

    def testTimeCopy(self):
        sol=SolutionDirectory(self.theFile)
        self.assertEqual(len(sol),1)
        sol["42"]=sol["0"]
        sol["13"]=sol["0"]
        self.assertEqual(len(sol),3)
        test1=sol["0"]
        test2=sol["13"]
        test3=sol["42"]
        self.assertEqual(len(test3),4)
        del test3[gammaName()]
        self.assertEqual(len(test3),3)
        res=test1.copy(test3)
        self.assertEqual(len(test1),4)
        self.assertEqual(len(res),3)
        res=test1.copy(test3,purge=True)
        self.assertEqual(len(test1),3)
        self.assertEqual(len(res),3)
        res=test1.copy(test2,overwrite=False)
        self.assertEqual(len(test1),4)
        self.assertEqual(len(res),1)
        test1.clear()
        self.assertEqual(len(test1),0)
        res=test1.copy(test2,overwrite=False)
        self.assertEqual(len(test1),4)
        self.assertEqual(len(res),4)
        res=test1.copy(test2,overwrite=False)
        self.assertEqual(len(test1),4)
        self.assertEqual(len(res),0)
        self.assertEqual(len(test3),3)
        res=test3.copy(test1,mustExist=True)
        self.assertEqual(len(test3),3)
        self.assertEqual(len(res),3)
        test1.clear()
        res=test1.copy(test2,include=[gammaName()+"*"])
        self.assertEqual(len(test1),2)
        self.assertEqual(len(res),2)
        res=test1.copy(test2,exclude=["U"],overwrite=False)
        self.assertEqual(len(test1),3)
        self.assertEqual(len(res),1)

theSuite.addTest(unittest.makeSuite(TimeDirectoryTestCopy,"test"))
