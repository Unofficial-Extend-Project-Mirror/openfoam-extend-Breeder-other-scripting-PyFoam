import unittest

from pandas import DataFrame,TimeSeries
from PyFoam.Wrappers.Pandas import PyFoamDataFrame,PandasWrapperPyFoamException

from math import isnan

theSuite=unittest.TestSuite()

class PyFoamDataFrameTest(unittest.TestCase):
    def setUp(self):
        self.data1={"a":[1.,1,1],
                    "b":[0.,1,3]}
        self.index1=[0.,1,2]
        self.data2={"c":[1.,1,1],
                    "d":[0.,1,2]}
        self.index2=[0.,1,4]
        self.index2a=[0.1,0.2,0.4]

        self.data3={"c":[1,1.,1,1],
                    "d":[0.,1,1,2]}
        self.index3=[0.,1,2,4]

    def tearDown(self):
        pass

    def testAddSame(self):
         dMaster=PyFoamDataFrame(data=self.data1,index=self.index1)
         self.assertEqual(len(dMaster.keys()),2)
         dSlave=PyFoamDataFrame(data=self.data2,index=self.index1)
         dMaster=dMaster.addData(dSlave)
         self.assertEqual(len(dMaster.keys()),4)
         for i,v in enumerate(self.index1):
             self.assertEqual(self.data2["c"][i],dMaster["c"][v])
             self.assertEqual(self.data2["d"][i],dMaster["d"][v])
         try:
             dMaster=dMaster.addData(dSlave)
             self.fail()
         except PandasWrapperPyFoamException:
              pass
         dMaster=dMaster.addData(dSlave,prefix="pre_")
         self.assertEqual(len(dMaster.keys()),6)
         dMaster=dMaster.addData(dSlave,suffix="_post")
         self.assertEqual(len(dMaster.keys()),8)

    def testAddWrong(self):
         dMaster=PyFoamDataFrame(data=self.data1,index=self.index1)
         self.assertEqual(len(dMaster.keys()),2)
         try:
              dMaster=dMaster.addData(self.data2)
              self.fail()
         except PandasWrapperPyFoamException:
              pass

         try:
              dMaster=dMaster.addData(PyFoamDataFrame(self.data3,self.index3))
              self.fail()
         except PandasWrapperPyFoamException:
              pass

    def testAddDifferent(self):
         dMaster=PyFoamDataFrame(data=self.data1,index=self.index1)
         self.assertEqual(len(dMaster.keys()),2)
         dSlave=PyFoamDataFrame(data=self.data2,index=self.index2)
         try:
              dMaster=dMaster.addData(dSlave)
              self.fail()
         except PandasWrapperPyFoamException:
              pass
         dMaster=dMaster.addData(dSlave,sameIndex=False)
         self.assertEqual(len(dMaster.keys()),4)
         self.assertEqual(len(dMaster.index),len(self.index1))
         self.assertEqual(min(dMaster.index),min(self.index1))
         self.assertEqual(max(dMaster.index),max(self.index1))
         for i,v in enumerate(self.index1):
              self.assertEqual(self.data1["a"][i],dMaster["a"][v])
              self.assertEqual(self.data1["b"][i],dMaster["b"][v])
              self.assertEqual(self.index1[i],dMaster.index[i])

    def testAddMerge(self):
         dMaster=PyFoamDataFrame(data=self.data1,index=self.index1)
         self.assertEqual(len(dMaster.keys()),2)
         dSlave=PyFoamDataFrame(data=self.data2,index=self.index2)
         try:
              dMaster=dMaster.addData(dSlave)
              self.fail()
         except PandasWrapperPyFoamException:
              pass
         dMaster=dMaster.addData(dSlave,mergeIndex=True)
         self.assertEqual(len(dMaster.keys()),4)
         self.assert_(len(dMaster.index)>len(self.index1))
         self.assertEqual(min(dMaster.index),min(min(self.index1),min(self.index2)))
         self.assertEqual(max(dMaster.index),max(max(self.index1),max(self.index2)))
         for i,v in enumerate(self.index1):
              self.assertEqual(self.data1["a"][i],dMaster["a"][v])
              self.assertEqual(self.data1["b"][i],dMaster["b"][v])
              self.assertEqual(self.index1[i],dMaster.index[i])
         self.assert_(dMaster["a"].map(isnan).any())
         dMaster=PyFoamDataFrame(data=self.data1,index=self.index1)
         dMaster=dMaster.addData(dSlave,mergeIndex=True,allowExtrapolate=True)
         self.assert_(not dMaster["a"].map(isnan).any())
         dMaster=PyFoamDataFrame(data=self.data1,index=self.index1)
         dSlave=PyFoamDataFrame(data=self.data2,index=self.index2a)
         dMaster=dMaster.addData(dSlave,mergeIndex=True)
         self.assert_(dMaster["c"].map(isnan).any())

    def testIntegrate(self):
        d=PyFoamDataFrame(data=self.data1,index=self.index1)
        i=d.integrate()
        self.assertAlmostEqual(i["a"],2)
        self.assertAlmostEqual(i["b"],2.5)
        l=d.validLength()
        self.assertAlmostEqual(l["a"],2)
        self.assertAlmostEqual(l["b"],2)
        w=d.weightedAverage()
        self.assertAlmostEqual(w["a"],1)
        self.assertAlmostEqual(w["b"],1.25)
        descr=d.describe()
        self.assertAlmostEqual(descr["b"]["integral"],2.5)
        self.assertAlmostEqual(descr["b"]["valid length"],2)
        self.assertAlmostEqual(descr["b"]["weighted average"],1.25)
        d["b"].values[1]=float("NaN")
        descr=d.describe()
        self.assertAlmostEqual(descr["b"]["integral"],1.5)
        self.assertAlmostEqual(descr["b"]["valid length"],1)
        self.assertAlmostEqual(descr["b"]["weighted average"],1.5)
        d["b"].values[:]=float("NaN")
        descr=d.describe()
        self.assert_(isnan(descr["b"]["integral"]))
        self.assertEqual(descr["b"]["valid length"],0)
        self.assert_(isnan(descr["b"]["weighted average"]))

theSuite.addTest(unittest.makeSuite(PyFoamDataFrameTest,"test"))
