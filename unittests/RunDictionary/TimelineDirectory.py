import unittest

from PyFoam.RunDictionary.TimelineDirectory import TimelineDirectory
from PyFoam.Basics.SpreadsheetData import SpreadsheetData

from os import path,mkdir
from shutil import rmtree
from tempfile import mkdtemp

theSuite=unittest.TestSuite()

def destroyDirectory(theDir):
    if path.exists(theDir):
        rmtree(theDir)

def createDirectory():
    theDir=mkdtemp()

    mkdir(path.join(theDir,"timeline"))
    mkdir(path.join(theDir,"timeline","0"))
    open(path.join(theDir,"timeline","0","p"),"w").write(
"""# time p p2 p3
0 0 0 0
1 0 0 1
3 1 1 1
""")
    open(path.join(theDir,"timeline","0","h"),"w").write(
"""# time p p2 p3
0 0 0 0
1 0 1
3 1 1 1
""")
    mkdir(path.join(theDir,"timeline","5"))
    mkdir(path.join(theDir,"probes"))
    mkdir(path.join(theDir,"probes","0"))
    open(path.join(theDir,"probes","0","p"),"w").write(
"""# x 0 1 2 3
# y 0 0 0 1
# z 1 1 1 1
# Time
0 0 0 0 1
1 0 0 1 1
3 1 1 1 1
""")
    open(path.join(theDir,"probes","0","h"),"w").write(
"""# x 0 1 2 3
# y 0 0 0 1
# z 1 1 1 1
# Time
0 0 0 0 0
1 0 1
3 1 1 1
""")
    open(path.join(theDir,"probes","0","U"),"w").write(
"""# x 0 1 2 3
# y 0 0 0 1
# z 1 1 1 1
# Time
0 (0 0 1) (0 0 0) (0 0 1) (0 0 0)
1 (0 0 1) (0 1 0) (0 0 1) (0 0 0)
3 (0 0 1) (0 0 1) (0 0 1) (0 0 0)
""")
    open(path.join(theDir,"probes","0","UTens"),"w").write(
"""# x 1.5
# y 0
# z 1.5
# Time
0.2 (0 0 0 0 0 0)
0.4 (2.7993e-08 -7.77667e-10 1.05859e-08 2.16042e-11 -2.94084e-10 4.00318e-09)
0.6 (3.17292e-08 -1.45928e-09 1.17226e-08 8.21429e-11 -5.31962e-10 4.33446e-09)
0.8 (2.85533e-08 -1.82099e-09 1.0425e-08 1.72582e-10 -6.48406e-10 3.81149e-09)
1 (2.40662e-08 -1.85896e-09 8.91598e-09 2.70264e-10 -7.08062e-10 3.32037e-09)
1.2 (2.01257e-08 -1.64986e-09 7.54823e-09 3.69006e-10 -7.58858e-10 2.96515e-09)
""")
    open(path.join(theDir,"probes","0","wrong1"),"w").write(
"""# x 0 1 2 3
# z 1 1 1 1
# Time
0 0 0 0 0
1 0 1
3 1 1 1
""")
    open(path.join(theDir,"probes","0","wrong2"),"w").write(
"""# x 0 1 2 3
# y 0 0 0
# z 1 1 1 1
# Time
0 0 0 0 1
1 0 0 1 1
3 1 1 1 1
""")
    return theDir

class TimelineDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.theDir=createDirectory()

    def tearDown(self):
        destroyDirectory(self.theDir)

    def testFindCorrectNames(self):
        sd=TimelineDirectory(self.theDir,writeTime=0.1)
        self.assertEqual(len(sd),3)
        self.assertEqual(sd.timeRange(),(0.,3.))
        self.assertEqual(len(sd.getData([0])),3)
        self.assertEqual(len(sd.getData([0])[0][2]),4)
        self.assertEqual(len(sd.getDataLocation(vectorMode="mag")),12)
        self.assertEqual(sd.positions(),  ['(0 0 1)', '(1 0 1)', '(2 0 1)', '(3 1 1)'])

theSuite.addTest(unittest.makeSuite(TimelineDirectoryTest,"test"))

class TimelineValueTest(unittest.TestCase):
    def setUp(self):
        self.theDir=createDirectory()

    def tearDown(self):
        destroyDirectory(self.theDir)

    def testGetTimes(self):
        sd=TimelineDirectory(self.theDir)
        st=sd["p"]
        self.assertEqual(st.getData([0.5,1,2,4]), [[0.0, 0.0, 0.0, 1.0],
                                                   [0.0, 0.0, 1.0, 1.0],
                                                   [0.0, 0.0, 1.0, 1.0],
                                                   [1.0, 1.0, 1.0, 1.0]] )
        self.assert_(st.isProbe())
        st=sd["h"]
        # this should be checked, but I don't want to
        self.assertEqual(st.getData([0.5,1,2,4]), [[0.0, 0.0, 0.0, 0.0],
                                                   [0.0, 1.0],
                                                   [0.0, 1.0],
                                                   [1.0, 1.0, 1.0]])
        self.assertRaises(KeyError,sd.__getitem__,"ha")

    def testGetTimesTimeline(self):
        sd=TimelineDirectory(self.theDir,dirName="timeline")
        st=sd["p"]
        self.assertEqual(st.getData([0.5,1,2,4]),[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [1.0, 1.0, 1.0]])
        self.assert_(not st.isProbe())
        st=sd["h"]
        self.assertEqual(st.getData([0.5,1,2,4]), [[0.0, 0.0, 0.0], [0.0, 1.0], [0.0, 1.0], [1.0, 1.0, 1.0]])
        self.assertRaises(KeyError,sd.__getitem__,"ha")

    def testGetSpreadsheet(self):
        csvName=path.join(self.theDir,"nix.csv")
        sd=TimelineDirectory(self.theDir)
        st=sd["p"]
        spread=st()
        spread.writeCSV(csvName)
        self.assertEqual(len(st.positions)+1,len(spread.names()))
        rereadSpread=SpreadsheetData(csvName=csvName)
        self.assertEqual(len(spread.names()),len(rereadSpread.names()))
        self.assertEqual(len(spread.data),len(rereadSpread.data))
        sd=TimelineDirectory(self.theDir,"timeline")
        st=sd["p"]
        spread=st()
        spread.writeCSV(path.join(self.theDir,"nix2.csv"))

theSuite.addTest(unittest.makeSuite(TimelineValueTest,"test"))
