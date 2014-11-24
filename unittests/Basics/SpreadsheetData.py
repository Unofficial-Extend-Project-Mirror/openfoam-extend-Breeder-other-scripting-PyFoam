
import unittest
import math
import numpy

from PyFoam.Basics.SpreadsheetData import SpreadsheetData

theSuite=unittest.TestSuite()

names1=['t','p1','p2']
data1=[[(k+1)*i for k in range(len(names1))] for i in range(len(names1)*2)]

names2=['t','p1','p3','p4']
data2=[[(k+1)*i for k in range(len(names2))] for i in range(len(names1)*2)]

class SpreadsheetDataTest(unittest.TestCase):
    def testSpreadsheetDataConstruction(self):
        sp=SpreadsheetData(data=data1,names=names1)
        self.assertEqual(names1,list(sp.names()))
        self.assertEqual(len(sp.data),len(names1)*2)
        self.assertEqual(max(sp.data['t']-range(len(names1)*2)),0)

    def testSpreadsheetDataAddition(self):
        sp1=SpreadsheetData(data=data1,names=names1)
        sp2=SpreadsheetData(data=data2,names=names2,title="nix")
        sp=sp1+sp2
        self.assertEqual(len(names1)+len(names2)-1,len(sp.names()))

    def testSpreadsheetScaleData(self):
        sp1=SpreadsheetData(data=data1,names=names1)
        self.assertAlmostEqual(min(sp1.data["t"]),0)
        self.assertAlmostEqual(max(sp1.data["t"]),5.0)
        self.assertAlmostEqual(min(sp1.data["p1"]),0)
        self.assertAlmostEqual(max(sp1.data["p1"]),10.0)
        self.assertAlmostEqual(min(sp1.data["p2"]),0)
        self.assertAlmostEqual(max(sp1.data["p2"]),15.0)
        sp1.recalcData("t","t/60")
        self.assertAlmostEqual(min(sp1.data["t"]),0)
        self.assertAlmostEqual(max(sp1.data["t"]),5.0/60.)
        sp1.recalcData("p 3","p1+p2",create=True)
        self.assertAlmostEqual(min(sp1.data["p 3"]),0)
        self.assertAlmostEqual(max(sp1.data["p 3"]),25.0)
        sp1.recalcData("p4","data['p1']+data['p2']",create=True)
        self.assertAlmostEqual(min(sp1.data["p4"]),0)
        self.assertAlmostEqual(max(sp1.data["p4"]),25.0)
        sp1.recalcData("p1","this/10+1")
        self.assertAlmostEqual(min(sp1.data["p1"]),1)
        self.assertAlmostEqual(max(sp1.data["p1"]),2)

    def testSpreadsheetDataExtend(self):
        sp1=SpreadsheetData(data=data1,names=names1)
        sp1.append("test",[i*i for i in range(len(data1))])
        self.assertEqual(len(sp1.names()),len(names1)+1)
        self.assert_("test" in sp1.names())

    def testSpreadsheetDataAddTimes(self):
        sp1=SpreadsheetData(data=data1,names=names1)
        self.assertEqual(len(sp1.data),6)
        sp1.addTimes([1.5],interpolate=True)
        self.assertEqual(len(sp1.data),7)
        self.assertAlmostEqual(sp1.data["p1"][2],3)
        sp1.addTimes([2.5],interpolate=False)
        self.assertEqual(len(sp1.data),8)
        self.assert_(numpy.isnan(sp1.data["p1"][4]))
        sp1.addTimes([-1],interpolate=True,invalidExtend=True)
        self.assertEqual(len(sp1.data),9)
        self.assertAlmostEqual(sp1.data["p1"][0],0)
        sp1.addTimes([10],interpolate=True,invalidExtend=False)
        self.assertEqual(len(sp1.data),10)
        self.assert_(numpy.isnan(sp1.data["p1"][-1]))
        sp1.addTimes([0,1,2],interpolate=True)
        self.assertEqual(len(sp1.data),10)
        sp1.addTimes([-2,2.37,20],interpolate=True)
        self.assertEqual(len(sp1.data),13)
        sp1.addTimes([-3,4,19],interpolate=True)
        self.assertEqual(len(sp1.data),15)

theSuite.addTest(unittest.makeSuite(SpreadsheetDataTest,"test"))

names3 = ['t','val']
data3=[[k,k*k]for k in range(10)]

class SpreadsheetInterpolationTest(unittest.TestCase):
    def testSpreadsheetDataInterpolation(self):
        sp=SpreadsheetData(data=data3,names=names3)
        self.assertAlmostEqual(sp(-1,"val",invalidExtend=True),0)
        self.assert_(numpy.isnan(sp(-1,"val")))
        self.assertAlmostEqual(sp(10,"val",invalidExtend=True),81)
        self.assert_(numpy.isnan(sp(10,"val")))
        self.assertAlmostEqual(sp(1,"val"),1)
        self.assertAlmostEqual(sp(1.5,"val"),2.5)
        self.assertAlmostEqual(sp(5,"val"),25)
        self.assertAlmostEqual(sp(5.1,"val"),26.1)
        self.assertAlmostEqual(sp(8.9,"val"),79.3)
        self.assertAlmostEqual(sp(8.9,"t"),8.9)

        self.assertAlmostEqual(sp(1,"val",noInterpolation=True),1)
        self.assert_(numpy.isnan(sp(1.5,"val",noInterpolation=True)))

    def testSpreadsheetDataOuterLimitNoInterpolate(self):
        sp=SpreadsheetData(data=data3,names=names3)
        self.assertAlmostEqual(sp(0,"val",noInterpolation=True),0)
        self.assertAlmostEqual(sp(9,"val",noInterpolation=True),81)
        self.assertAlmostEqual(sp(0,"val"),0)
        self.assertAlmostEqual(sp(9,"val"),81)

theSuite.addTest(unittest.makeSuite(SpreadsheetInterpolationTest,"test"))

names4 = ['t','val']
data4=[[k,k*k+1] for k in range(10)]
data5=[[k-0.5,(k-0.5)*(k-0.5)] for k in range(11)]
data6=[[k,k] for k in range(10)]
data7=[[k-0.5,k-0.5] for k in range(11)]

class SpreadsheetDifferenceTest(unittest.TestCase):
    def testSpreadsheetDataCompare1(self):
        sp=SpreadsheetData(data=data3,names=names3)
        sp2=SpreadsheetData(data=data4,names=names4)
        diff1=sp.compare(sp2,"val")
        self.assertAlmostEqual(diff1["max"],1)
        self.assertAlmostEqual(diff1["average"],1)
        self.assertAlmostEqual(diff1["wAverage"],1)
        diff2=sp2.compare(sp,"val")
        self.assertEqual(diff1["max"],diff2["max"])
        self.assertEqual(diff1["average"],diff2["average"])
        self.assertEqual(diff1["wAverage"],diff2["wAverage"])
        diff3=sp.compare(sp,"val")
        self.assertAlmostEqual(diff3["max"],0)
        self.assertAlmostEqual(diff3["average"],0)
        self.assertAlmostEqual(diff3["wAverage"],0)

    def testSpreadsheetDataCompare2(self):
        sp=SpreadsheetData(data=data3,names=names3)
        sp2=SpreadsheetData(data=data5,names=names4)
        diff1=sp.compare(sp2,"val")
        self.assertAlmostEqual(diff1["max"],0.25)
        self.assertAlmostEqual(diff1["average"],0.25)
        self.assertAlmostEqual(diff1["wAverage"],0.25)
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff2["max"],9.25)
        self.assertAlmostEqual(diff2["average"],1.0681818181)
        self.assertAlmostEqual(diff2["wAverage"],0.7)

    def testSpreadsheetDataCompare3(self):
        sp=SpreadsheetData(data=data6,names=names3)
        sp2=SpreadsheetData(data=data7,names=names4)
        diff1=sp.compare(sp2,"val")
        self.assertAlmostEqual(diff1["max"],0)
        self.assertAlmostEqual(diff1["average"],0)
        self.assertAlmostEqual(diff1["wAverage"],0)
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff2["max"],0.5)
        self.assertAlmostEqual(diff2["average"],0.09090909)
        self.assertAlmostEqual(diff2["wAverage"],0.05)

    def testSpreadsheetDataCompare4(self):
        sp=SpreadsheetData(data=[[i*0.5,1] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5,2] for i in range(10)],names=['t','val'])
        diff1=sp.compare(sp2,"val")
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff1["max"],diff2["max"])
        self.assertAlmostEqual(diff1["average"],diff2["average"])
        self.assertAlmostEqual(diff1["wAverage"],diff2["wAverage"])
        self.assertAlmostEqual(diff1["average"],diff1["wAverage"])

    def testSpreadsheetDataCompare4a(self):
        sp=SpreadsheetData(data=[[i*0.5,1] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5-0.5,2] for i in range(11)],names=['t','val'])
        diff1=sp.compare(sp2,"val")
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff1["max"],diff2["max"])
        self.assertAlmostEqual(diff1["average"],diff2["average"])
        self.assertAlmostEqual(diff1["wAverage"],diff2["wAverage"])
        self.assertAlmostEqual(diff1["average"],diff1["wAverage"])

    def testSpreadsheetDataCompare4b(self):
        sp=SpreadsheetData(data=[[i*0.5,1+i*i] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5,2+i*i] for i in range(10)],names=['t','val'])
        diff1=sp.compare(sp2,"val")
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff1["max"],diff2["max"])
        self.assertAlmostEqual(diff1["average"],diff2["average"])
        self.assertAlmostEqual(diff1["wAverage"],diff2["wAverage"])
        self.assertAlmostEqual(diff1["average"],diff1["wAverage"])

    def testSpreadsheetDataCompare4c(self):
        sp=SpreadsheetData(data=[[i*0.5,math.sin(i)] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5,math.sin(i)+0.5] for i in range(10)],names=['t','val'])
        diff1=sp.compare(sp2,"val")
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff1["max"],diff2["max"])
        self.assertAlmostEqual(diff1["average"],diff2["average"])
        self.assertAlmostEqual(diff1["wAverage"],diff2["wAverage"])
        self.assertAlmostEqual(diff1["average"],diff1["wAverage"])

    def testSpreadsheetDataCompare4d(self):
        sp=SpreadsheetData(data=[[i*0.5,math.sin(i)] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5-0.5,math.sin(i-1)+0.5] for i in range(11)],names=['t','val'])
        diff1=sp.compare(sp2,"val")
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff1["max"],diff2["max"])
        #        self.assertAlmostEqual(diff1["average"],diff2["average"])
        #        self.assertAlmostEqual(diff1["wAverage"],diff2["wAverage"])
        self.assertAlmostEqual(diff1["average"],diff1["wAverage"])
        #        self.assertAlmostEqual(diff2["average"],diff2["wAverage"])
        diff3=sp.compare(sp2,"val",common=True)
        diff4=sp2.compare(sp,"val",common=True)
        self.assertAlmostEqual(diff3["max"],diff4["max"])
        self.assertAlmostEqual(diff3["average"],diff4["average"])
        self.assertAlmostEqual(diff3["wAverage"],diff4["wAverage"])
        self.assertAlmostEqual(diff3["average"],diff3["wAverage"])
        self.assertAlmostEqual(diff4["average"],diff4["wAverage"])

    def testSpreadsheetDataCompare4e(self):
        sp=SpreadsheetData(data=[[i*0.5,math.sin(i)] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5-0.5,math.sin(i-1)+0.5] for i in range(10)],names=['t','val'])
        diff3=sp.compare(sp2,"val",common=True)
        diff4=sp2.compare(sp,"val",common=True)
        self.assertAlmostEqual(diff3["max"],diff4["max"])
        self.assertAlmostEqual(diff3["average"],diff4["average"])
        self.assertAlmostEqual(diff3["wAverage"],diff4["wAverage"])
        self.assertAlmostEqual(diff3["average"],diff3["wAverage"])
        self.assertAlmostEqual(diff4["average"],diff4["wAverage"])

    def testSpreadsheetDataCompare4f(self):
        sp=SpreadsheetData(data=[[i*0.5,i*0.5] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5-0.25,i*0.5-0.25] for i in range(10)],names=['t','val'])
        diff3=sp.compare(sp2,"val",common=True)
        diff4=sp2.compare(sp,"val",common=True)
        self.assertAlmostEqual(diff3["max"],diff4["max"])
        self.assertAlmostEqual(diff3["average"],diff4["average"])
        self.assertAlmostEqual(diff3["wAverage"],diff4["wAverage"])
        self.assertAlmostEqual(diff3["average"],diff3["wAverage"])
        self.assertAlmostEqual(diff4["average"],diff4["wAverage"])

    def testSpreadsheetDataCompare5(self):
        sp=SpreadsheetData(data=[[i*0.5,1] for i in range(10)],names=['t','val'])
        diff=sp.compare(sp,"val")
        self.assertAlmostEqual(diff["max"],0)
        self.assertAlmostEqual(diff["average"],0)
        self.assertAlmostEqual(diff["wAverage"],0)

    def testSpreadsheetDataCompare6(self):
        sp=SpreadsheetData(data=[[i*0.5,1] for i in range(10)],names=['t','val'])
        sp2=SpreadsheetData(data=[[i*0.5+10,2] for i in range(10)],names=['t','val'])
        diff1=sp.compare(sp2,"val")
        diff2=sp2.compare(sp,"val")
        self.assertAlmostEqual(diff1["max"],1)
        self.assertAlmostEqual(diff1["average"],1)
        self.assertAlmostEqual(diff1["wAverage"],1)
        self.assertAlmostEqual(diff2["max"],1)
        self.assertAlmostEqual(diff2["average"],1)
        self.assertAlmostEqual(diff2["wAverage"],1)
        diff1=sp.compare(sp2,"val",common=True)
        diff2=sp2.compare(sp,"val",common=True)
        self.assertEqual(diff1["max"],None)
        self.assertEqual(diff1["average"],None)
        self.assertEqual(diff1["wAverage"],None)
        self.assertEqual(diff2["max"],None)
        self.assertEqual(diff2["average"],None)
        self.assertEqual(diff2["wAverage"],None)

theSuite.addTest(unittest.makeSuite(SpreadsheetDifferenceTest,"test"))

from PyFoam.ThirdParty.six import BytesIO,b

filecontent=b("""# time  Initial         Final   Iterations
0.005   1       2.96338e-06     8
0.01    0.148584        7.15711e-06     6
0.015   0.0448669       2.39894e-06     6
0.02    0.0235438       1.57074e-06     6
0.025   0.0148809       5.14401e-06     5
""")

from PyFoam.ThirdParty.six import BytesIO

from tempfile import mktemp

class SpreadsheetReadFileTest(unittest.TestCase):
    def testSpreadsheetReadFileTest(self):
        fName=mktemp()
        open(fName,"wb").write(filecontent)
        sp=SpreadsheetData(txtName=fName)
        self.assertEqual(len(sp.names()),4)
        self.assertEqual(sp.size(),5)
        self.assertEqual(sp.tRange(),(0.005,0.025))
        self.assertEqual(sp.names()[1],"Initial")

    def testSpreadsheetReadFileHandleTest(self):
        fName=mktemp()
        open(fName,"w").write(filecontent)
        sp=SpreadsheetData(txtName=open(fName))
        self.assertEqual(len(sp.names()),4)

    def testSpreadsheetReadFileHandleTest(self):
        sp=SpreadsheetData(txtName=BytesIO(filecontent))
        self.assertEqual(len(sp.names()),4)

theSuite.addTest(unittest.makeSuite(SpreadsheetReadFileTest,"test"))
