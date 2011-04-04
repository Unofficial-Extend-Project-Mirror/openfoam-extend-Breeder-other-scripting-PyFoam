import unittest

from PyFoam.RunDictionary.SampleDirectory import SampleDirectory,SampleTime,SampleData

from os import path,environ,system,mkdir
from shutil import rmtree

theSuite=unittest.TestSuite()

theDir="/tmp/sampleDirectoryTest"

def destroyDirectory():
    if path.exists(theDir):
        rmtree(theDir)

def createDirectory():
    destroyDirectory()

    mkdir(theDir)
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

class SampleDirectoryTest(unittest.TestCase):
    def setUp(self):
        createDirectory()

    def tearDown(self):
        destroyDirectory()

    def testFindCorrectNames(self):
        sd=SampleDirectory(theDir)
        self.assertEqual(len(sd),2)
        self.assertEqual(len(sd.lines()),2)
        self.assertEqual(len(sd.values()),5)
        self.assertEqual(len(sd.getData()),9)

theSuite.addTest(unittest.makeSuite(SampleDirectoryTest,"test"))

class SampleTimeTest(unittest.TestCase):
    def setUp(self):
        createDirectory()

    def tearDown(self):
        destroyDirectory()

    def testGetTimes(self):
        sd=SampleDirectory(theDir)
        st=sd["0"]
        self.assertRaises(KeyError,sd.__getitem__,"3")
        
theSuite.addTest(unittest.makeSuite(SampleTimeTest,"test"))

class SampleDataTest(unittest.TestCase):
    def setUp(self):
        createDirectory()

    def tearDown(self):
        destroyDirectory()

    def testFindCorrectRanges(self):
        sd=SampleDirectory(theDir)
        st=sd["0"]
        U=st[("line1","U")]
        self.assert_(U.isVector())
        p=st[("line1","p")]
        self.assert_(not p.isVector())
        self.assertEqual(p.domain(),(0.,3.))
        self.assertEqual(p.range(),(0.,1.))

    def testFailOnWrongData(self):
        sd=SampleDirectory(theDir)
        st=sd["0"]
        self.assertRaises(KeyError,st.__getitem__,("line2","p3"))

    def testFindCorrectRanges(self):
        sd=SampleDirectory(theDir)
        st=sd["0"]
        U=st[("line1","U")]
        p=st[("line1","p")]
        spread=U()+p()
        spread2=p()
        spread2.title="duplicate"
        spread+=spread2
        spread.writeCSV("/tmp/sample.csv")
        
theSuite.addTest(unittest.makeSuite(SampleTimeTest,"test"))

