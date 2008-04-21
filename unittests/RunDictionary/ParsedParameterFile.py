
import unittest

from os import path,environ,system

from PyFoam.RunDictionary.ParsedParameterFile import FoamStringParser,ParsedParameterFile,ParsedBoundaryDict,DictProxy,TupleProxy,PyFoamParserError

from PyFoam.Basics.FoamFileGenerator import Vector,Dimension,Field,Tensor,SymmTensor

theSuite=unittest.TestSuite()
    
class FoamStringParserTest(unittest.TestCase):
    
    def testParseInteger(self):
        p1=FoamStringParser("test 1;")
        self.assertEqual(p1["test"],1)
        
    def testParseFloat(self):
        p1=FoamStringParser("test 1.23e-4;")
        self.assertAlmostEqual(p1["test"],1.234e-4,6)
        
    def testParseFloat2(self):
        p1=FoamStringParser("test 1.e-4;")
        self.assertEqual(type(p1["test"]),float)
        self.assertAlmostEqual(p1["test"],1.e-4,6)
        
    def testParseString(self):
        p1=FoamStringParser('test "der name";')
        self.assertEqual(p1["test"][1:-1],"der name")

    def testParseWord(self):
        p1=FoamStringParser('test  name;')
        self.assertEqual(p1["test"],"name")
    
    def testParseWordMinus(self):
        p1=FoamStringParser('test  name-0;')
        self.assertEqual(p1["test"],"name-0")
    
    def testParseError(self):
        try:
            p1=FoamStringParser('test  name')
            self.fail()
        except PyFoamParserError:
            pass
        
    def testDataList(self):
        p1=FoamStringParser("test (2 3 4 5);")
        self.assertEqual(type(p1["test"]),list)
        self.assertEqual(len(p1["test"]),4)
        
    def testDataList2(self):
        p1=FoamStringParser("test (a b c d);")
        self.assertEqual(type(p1["test"]),list)
        self.assertEqual(len(p1["test"]),4)
        self.assertEqual(p1["test"][-1],"d")
        
    def testDataDictionary(self):
        p1=FoamStringParser("test { dings 2;}")
        self.assertEqual(type(p1["test"]),DictProxy)
        self.assertEqual(len(p1["test"]),1)

    def testEmptyDictionary(self):
        p1=FoamStringParser("test {}")
        self.assertEqual(len(p1["test"]),0)
        self.assertEqual(type(p1["test"]),DictProxy)

    def testDataTuple(self):
        p1=FoamStringParser("test dings 2;")
        self.assertEqual(type(p1["test"]),TupleProxy)
        self.assertEqual(len(p1["test"]),2)

    def testDataNone(self):
        p1=FoamStringParser("test;")
        self.assertEqual(p1["test"],None)

    def testDataVector(self):
        p1=FoamStringParser("test ( 1 3 4 );")
        self.assertEqual(p1["test"].__class__,Vector)
        
    def testDataTensor(self):
        p1=FoamStringParser("test ( 1 2 3 4 5 4 3 2 1 );")
        self.assertEqual(p1["test"].__class__,Tensor)
        
    def testDataSymmTensor(self):
        p1=FoamStringParser("test ( 1 2 3 4 5 4 );")
        self.assertEqual(p1["test"].__class__,SymmTensor)
        
    def testDataDimension(self):
        p1=FoamStringParser("test [1 2 -3 0 1.4 1 2];")
        self.assertEqual(p1["test"].__class__,Dimension)
        
    def testStringConversion(self):
        p1=FoamStringParser("test dings 2;")
        self.assertEqual(str(p1),"test dings     2 ;\n")

    def testOneLineComment(self):
        p1=FoamStringParser("// test dings 2;")
        self.assertEqual(str(p1),"")
        p1=FoamStringParser("""
        // test dings 2;
        test2 dings 3;""")
        self.assertEqual(str(p1),"test2 dings     3 ;\n")

    def testMultiLineComment(self):
        p=FoamStringParser("""
        /* this should never be read
        This too */
        test dings 2;""")
        self.assertEqual(str(p),"test dings     2 ;\n")
        p=FoamStringParser("""
        /* this should never be read
        This too */
        test dings 2;
        /* Here goes the next comment */""")
        self.assertEqual(str(p),"test dings     2 ;\n")
        
theSuite.addTest(unittest.makeSuite(FoamStringParserTest,"test"))

class ParsedBoundaryDictTest(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test.boundaryFile"
        system("cp "+path.join(environ["FOAM_TUTORIALS"],"simpleFoam/pitzDaily/constant/polyMesh/boundary")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    def testReadTutorial(self):
        test=ParsedBoundaryDict(self.theFile)
        self.assertEqual(len(test.content),5)
        self.assert_("inlet" in test)
    
theSuite.addTest(unittest.makeSuite(ParsedBoundaryDict,"test"))
                 
class ParsedParameterFileTest(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test.turbulence"
        system("cp "+path.join(environ["FOAM_TUTORIALS"],"simpleFoam/pitzDaily/constant/turbulenceProperties")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        self.assertEqual(len(test.content),17)
        self.assertEqual(test["turbulenceModel"],"kEpsilon")
    
theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest,"test"))
                 
class ParsedParameterFileTest2(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test.gamma"
        system("cp "+path.join(environ["FOAM_TUTORIALS"],"interFoam/damBreak/0/gamma")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        self.assertEqual(len(test["boundaryField"]),5)
    
theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest2,"test"))
                 
class ParsedParameterFileTest3(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test.Thotroom"
        system("cp "+path.join(environ["FOAM_TUTORIALS"],"buoyantSimpleFoam/hotRoom/0/T.org")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        self.assertEqual(len(test["boundaryField"]),3)
        self.assertEqual(len(test["boundaryField"]["floor"]["value"].val),400)
    
theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest3,"test"))
                 
class ParsedParameterFileTest4(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test.Xoodles.schems"
        system("cp "+path.join(environ["FOAM_TUTORIALS"],"Xoodles/pitzDaily3D/system/fvSchemes")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        self.assertEqual(len(test["gradSchemes"]),2)
        self.assertEqual(len(test["divSchemes"]["div(phi,ft_b_h_hu)"][2]),5)
    
theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest4,"test"))
                 
class ParsedParameterFileTest5(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test.Rfile"
        system("cp "+path.join(environ["FOAM_TUTORIALS"],"turbFoam/cavity/0/R")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        self.assertEqual(test["internalField"].__class__,Field)
        self.assertEqual(test["internalField"].isUniform(),True)
        self.assertEqual(test["internalField"].value().__class__,Tensor)
        
theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest5,"test"))
                 
class ParsedParameterFileTest6(unittest.TestCase):
    def setUp(self):
        self.theFile="/tmp/test.Xoodles.schems"
        system("cp "+path.join(environ["FOAM_TUTORIALS"],"dieselFoam/aachenBomb/0/spray")+" "+self.theFile)
        
    def tearDown(self):
        system("rm "+self.theFile)
        
    def testReadTutorial(self):
        try:
            test=ParsedParameterFile(self.theFile)
        except PyFoamParserError:
            pass
    
theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest6,"test"))
                 
