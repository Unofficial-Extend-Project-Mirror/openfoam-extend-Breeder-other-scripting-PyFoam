
import unittest

from PyFoam.Basics.CustomPlotInfo import CustomPlotInfo,readCustomPlotInfo,resetCustomCounter
from PyFoam.RunDictionary.ParsedParameterFile import FoamStringParser

theSuite=unittest.TestSuite()

pureRegexp="Time = (%d%)"
pureRegexp2="""Time = (%d%)
Integral of CO2 = (%f%)"""
pyDictRegexp='{"expr":"Integral of CO2 = (%f%)","name":"Total CO2"}'
pyDictRegexp2='''{"expr":"Integral of CO2 = (%f%)","name":"Total CO2"}
{"expr":"Time = (%d%"}'''
newStyle='''
testit {
   expr "Integral of CO2 = (%f%)";
   name "Total CO2";
}
'''
newStyle2='''
testit {
   expr "Integral of CO2 = (%f%)";
   name "Total CO2";
}

time {
   expr "Time = (%d%)";
}
'''

class CustomPlotInfoTest(unittest.TestCase):
    def setUp(self):
        resetCustomCounter()

    def testPureRegex(self):
        ci=CustomPlotInfo(pureRegexp)
        self.assertEqual(ci.expr,pureRegexp)
        self.assertEqual(ci.nr,1)
        self.assertEqual(ci.accumulation,"first")

    def testPyDictRegexp(self):
        ci=CustomPlotInfo(pyDictRegexp)
        self.assertEqual(ci.expr,"Integral of CO2 = (%f%)")
        self.assertEqual(ci.nr,1)
        self.assertEqual(ci.accumulation,"first")

    def testNewStyle(self):
        data=FoamStringParser(newStyle)
        ci=CustomPlotInfo(data["testit"])
        self.assertEqual(ci.expr,"Integral of CO2 = (%f%)")
        self.assertEqual(ci.nr,1)
        self.assertEqual(ci.accumulation,"first")

    def testCustomCounter(self):
        data=FoamStringParser(newStyle2)
        ci=CustomPlotInfo(data["testit"])
        self.assertEqual(ci.nr,1)
        ci=CustomPlotInfo(data["time"])
        self.assertEqual(ci.nr,2)

theSuite.addTest(unittest.makeSuite(CustomPlotInfoTest,"test"))

class readCustomPlotInfoTest(unittest.TestCase):
    def setUp(self):
        resetCustomCounter()

    def testPureRegex(self):
        ci=readCustomPlotInfo(pureRegexp)
        self.assertEqual(len(ci),1)
        ci=readCustomPlotInfo(pureRegexp2)
        self.assertEqual(len(ci),2)

    def testPyDictRegexp(self):
        ci=readCustomPlotInfo(pyDictRegexp)
        self.assertEqual(len(ci),1)
        ci=readCustomPlotInfo(pyDictRegexp2)
        self.assertEqual(len(ci),2)

    def testNewStyle(self):
        ci=readCustomPlotInfo(newStyle)
        self.assertEqual(len(ci),1)
        ci=readCustomPlotInfo(newStyle2)
        self.assertEqual(len(ci),2)

theSuite.addTest(unittest.makeSuite(readCustomPlotInfoTest,"test"))
