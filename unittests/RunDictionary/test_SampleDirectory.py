import unittest

from PyFoam.RunDictionary.SampleDirectory import SampleDirectory

from os import path,mkdir
from shutil import rmtree
from tempfile import mkdtemp

theSuite=unittest.TestSuite()

def destroyDirectory(theDir):
    if path.exists(theDir):
        rmtree(theDir)

def createDirectory():
    theDir=mkdtemp()

    mkdir(path.join(theDir,"samples"))
    mkdir(path.join(theDir,"samples","0"))
    open(path.join(theDir,"samples","0","line1_U_U2.xy"),"w").write(
"""0 0 0 0 0 0 0
1 0 0 1 0 0 0
3 1 1 1 1 1 1
""")
    open(path.join(theDir,"samples","0","line1_p_p2_p3.xy"),"w").write(
"""0 0 0 0
1 0 0 1
3 1 1 1
""")
    open(path.join(theDir,"samples","0","line2_U_U2.xy"),"w").write(
"""0 0 0 0 0 0 0
1 0 0 1 0 0 0
3 1 1 1 1 1 1
""")
    open(path.join(theDir,"samples","0","line2_p_p2_p3.xy"),"w").write(
"""0 0 0 0
1 0 1
3 1 1 1
""")
    mkdir(path.join(theDir,"samples","5"))

    return theDir

def createDirectory2():
    theDir=createDirectory()

    open(path.join(theDir,"samples","0","line1_p_post_preset_pre_p.xy"),"w").write(
"""0 0 0 0
1 0 0 1
3 1 1 1
""")
    open(path.join(theDir,"samples","0","line2_p_post_preset_pre_p.xy"),"w").write(
        open(path.join(theDir,"samples","0","line1_p_post_preset_pre_p.xy")).read()
        )

    return theDir

def createDirectory3():
    theDir=mkdtemp()

    mkdir(path.join(theDir,"samples"))
    mkdir(path.join(theDir,"samples","0"))
    open(path.join(theDir,"samples","0","forgetIt_prefix_line1"),"w").write(
"""# time p p2 p3
0 0 0 0
1 0 0 1
3 1 1 1
""")
    open(path.join(theDir,"samples","0","prefix_line2.xy"),"w").write(
"""0 0 0 0
1 0 1 2
3 1 1 1
""")
    mkdir(path.join(theDir,"samples","5"))

    return theDir

class SampleDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.theDir=createDirectory()

    def tearDown(self):
        destroyDirectory(self.theDir)

    def testFindCorrectNames(self):
        sd=SampleDirectory(self.theDir)
        self.assertEqual(len(sd),2)
        self.assertEqual(len(sd.lines()),2)
        self.assertEqual(len(sd.values()),5)
        self.assertEqual(len(sd.getData()),9)

theSuite.addTest(unittest.makeSuite(SampleDirectoryTest,"test"))

class SampleDirectoryTestPrenamed(unittest.TestCase):
    def setUp(self):
        self.theDir=createDirectory3()

    def tearDown(self):
        destroyDirectory(self.theDir)

    def testFindCorrectNames(self):
        sd=SampleDirectory(self.theDir,
                           valueNames=["p","p2","p3"],
                           linePattern=".*prefix_([^.]+).*",
                           needsExtension=False)
        self.assertEqual(len(sd),2)
        self.assertEqual(len(sd.lines()),2)
        self.assertEqual(len(sd.values()),3)
        self.assertEqual(len(sd.getData()),6)

theSuite.addTest(unittest.makeSuite(SampleDirectoryTestPrenamed,"test"))

class SampleTimeTest(unittest.TestCase):
    def setUp(self):
        self.theDir=createDirectory()

    def tearDown(self):
        destroyDirectory(self.theDir)

    def testGetTimes(self):
        sd=SampleDirectory(self.theDir)
        st=sd["0"]
        self.assertRaises(KeyError,sd.__getitem__,"3")

theSuite.addTest(unittest.makeSuite(SampleTimeTest,"test"))

class SampleDataTest(unittest.TestCase):
    def setUp(self):
        self.theDir=createDirectory()

    def tearDown(self):
        destroyDirectory(self.theDir)

    def testFindCorrectRanges(self):
        sd=SampleDirectory(self.theDir)
        st=sd["0"]
        U=st[("line1","U")]
        self.assert_(U.isVector())
        p=st[("line1","p")]
        self.assert_(not p.isVector())
        self.assertEqual(p.domain(),(0.,3.))
        self.assertEqual(p.range(),(0.,1.))

    def testFailOnWrongData(self):
        sd=SampleDirectory(self.theDir)
        st=sd["0"]
        self.assertRaises(KeyError,st.__getitem__,("line2","p3"))

    def testFindCorrectRanges(self):
        sd=SampleDirectory(self.theDir)
        st=sd["0"]
        U=st[("line1","U")]
        p=st[("line1","p")]
        spread=U()+p()
        spread2=p()
        spread2.title="duplicate"
        spread+=spread2
        spread.writeCSV(path.join(self.theDir,"sample.csv"))

theSuite.addTest(unittest.makeSuite(SampleDataTest,"test"))

class SampleDataTestPrefix(unittest.TestCase):
    def setUp(self):
        self.theDir=createDirectory2()

    def tearDown(self):
        destroyDirectory(self.theDir)

    def testUsePrePostfix(self):
        sd=SampleDirectory(self.theDir,prefixes=["pre"],postfixes=["post"])
        self.assertEqual(len(sd),2)
        self.assertEqual(len(sd.lines()),2)
        self.assertEqual(len(sd.values()),8)
        self.assertEqual(len(sd.getData()),15)
        st=sd["0"]
        p=st[("line2","p_post")]
        p2=st[("line2","pre_p")]

theSuite.addTest(unittest.makeSuite(SampleTimeTest,"test"))
