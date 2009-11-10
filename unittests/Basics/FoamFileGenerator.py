
import unittest

from PyFoam.Basics.FoamFileGenerator import FoamFileGenerator,makeString,FoamFileGeneratorError
from PyFoam.Basics.DataStructures import DictProxy,TupleProxy,Unparsed,UnparsedList
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from PyFoam.FoamInformation import oldTutorialStructure,foamTutorials,foamVersionNumber
from os import tmpnam,system,environ,path
from copy import deepcopy
import warnings

warnings.filterwarnings(action='ignore',
                        message="tmpnam is a potential security risk to your program",
                        category=RuntimeWarning)

theSuite=unittest.TestSuite()

def damBreakTutorial():
    prefix=foamTutorials()
    if oldTutorialStructure():
        prefix=path.join(prefix,"interFoam")
    else:
        prefix=path.join(prefix,"multiphase","interFoam","laminar")            
    return path.join(prefix,"damBreak")

def bubbleColumnTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"multiphase")            
    return path.join(prefix,"twoPhaseEulerFoam","bubbleColumn")

def buoyHotRoomTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"heatTransfer")            
    return path.join(prefix,"buoyantSimpleFoam","hotRoom")

def turbCavityTutorial():
    prefix=foamTutorials()
    if oldTutorialStructure():
        prefix=path.join(prefix,"turbFoam")            
    else:
        prefix=path.join(prefix,"incompressible","pisoFoam","ras")            
    return path.join(prefix,"cavity")
        
def simpleBikeTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"incompressible")
    else:
        error("The simpleFoam-motorBike-case does not exist before 1.6")
        
    return path.join(prefix,"simpleFoam","motorBike")

class FoamFileGeneratorTest(unittest.TestCase):
    def testMakePrimitives(self):
        g=FoamFileGenerator(1)
        self.assertEqual(str(g),"1")
        g=FoamFileGenerator("1")
        self.assertEqual(str(g),"1")
        g=FoamFileGenerator(u"1")
        self.assertEqual(str(g),"1")
        g=FoamFileGenerator(1.2)
        self.assertEqual(str(g),"1.2")
        g=FoamFileGenerator(1L)
        self.assertEqual(str(g),"1")
        g=FoamFileGenerator(True)
        self.assertEqual(str(g),"yes")
        g=FoamFileGenerator(False)
        self.assertEqual(str(g),"no")

    def testMakeList(self):
        g=FoamFileGenerator([1,2,3,4])
        self.assertEqual(str(g),"(\n  1\n  2\n  3\n  4\n)\n")
        g=FoamFileGenerator([1,2,3])
        self.assertEqual(str(g),"(1 2 3)")
        g=FoamFileGenerator(range(9))
        self.assertEqual(str(g),"(0 1 2 3 4 5 6 7 8)")
        g=FoamFileGenerator(range(6))
        self.assertEqual(str(g),"(0 1 2 3 4 5)")
        g=FoamFileGenerator([1,2,[3,4],4])
        self.assertEqual(str(g),"(\n  1\n  2\n\n  (\n    3\n    4\n  )\n  4\n)\n")
        g=FoamFileGenerator([1,2,[3,4]])
        self.assertEqual(str(g),"(\n  1\n  2\n\n  (\n    3\n    4\n  )\n)\n")
        g=FoamFileGenerator(["1",u"2"])
        self.assertEqual(str(g),"(\n  1\n  2\n)\n")
        
    def testMakeDictionaryProxy(self):
        d=DictProxy()
        d["b"]=2
        d["a"]=1
        g=FoamFileGenerator(d)
        self.assertEqual(str(g),"b 2;\na 1;\n")
        d=DictProxy()
        d["a"]=1
        d["b"]=2
        g=FoamFileGenerator(d)
        self.assertEqual(str(g),"a 1;\nb 2;\n")
        d=DictProxy()
        d[u"a"]=1
        d["b"]=u"2"
        g=FoamFileGenerator(d)
        self.assertEqual(str(g),"a 1;\nb 2;\n")

    def testMakeDictionaryProxyBool(self):
        d=DictProxy()
        d["b"]=True
        d["a"]=False
        g=FoamFileGenerator(d)
        self.assertEqual(str(g),"b yes;\na no;\n")

    def testMakeDictionary(self):
        g=FoamFileGenerator({'a':1,'b':2})
        self.assertEqual(str(g),"a 1;\nb 2;\n")

    def testMakeEmpty(self):
        g=FoamFileGenerator({'a':None})
        self.assertEqual(str(g),"a /* empty */ ;\n")

    def testMakeNone(self):
        g=FoamFileGenerator(None)
        try:
            self.assertEqual(str(g),"")
            self.fail()
        except FoamFileGeneratorError:
            pass

theSuite.addTest(unittest.makeSuite(FoamFileGeneratorTest,"test"))

class FoamFileGeneratorUnparsed(unittest.TestCase):
    def testUnparsed(self):
        text="Das ist nicht geparst"
        g=FoamFileGenerator(Unparsed(text))
        self.assertEqual(str(g),text)
        
    def testUnparsedList(self):
        text="Das ist nicht geparst"
        g=FoamFileGenerator([Unparsed(text),"nix"])
        self.assertEqual(str(g),"(\n  "+text+"\n  nix\n)\n")
        
    def testUnparsedDict(self):
        text="Das ist nicht geparst"
        g=FoamFileGenerator({"a":Unparsed(text),"b":"nix"})
        self.assertEqual(str(g),"a "+text+";\nb nix;\n")
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorUnparsed,"test"))

class FoamFileGeneratorUnparsedList(unittest.TestCase):
    def testUnparsedList(self):
        content="1\n2\n3\n4\n5\n6"
        g=FoamFileGenerator(UnparsedList(6,content))
        self.assertEqual(str(g),"6 ("+content+"\n)\n")
    def testUnparsedListList(self):
        content="1\n2\n3\n4\n5\n6"
        g=FoamFileGenerator([UnparsedList(6,content),"nix"])
        self.assertEqual(str(g),"(\n\n  6 ("+content+"\n  )\n  nix\n)\n")
    def testUnparsedListDict(self):
        content="1\n2\n3\n4\n5\n6"
        g=FoamFileGenerator({"a":UnparsedList(6,content),"b":"nix"})
        self.assertEqual(str(g),"a\n  6 ("+content+"\n  );\nb nix;\n")
                
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorUnparsedList,"test"))

class FoamFileGeneratorRoundtrip(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(damBreakTutorial(),"system","fvSolution")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
    
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtrip,"test"))

class FoamFileGeneratorRoundtrip2(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(damBreakTutorial(),"system","fvSchemes")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
    
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtrip2,"test"))

class FoamFileGeneratorRoundtripZipped(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(damBreakTutorial(),"system","fvSolution")+" "+self.theFile)
        system("gzip -f "+self.theFile)
        
    def tearDown(self):
        system("rm "+self.theFile+".gz")
    
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)
        test3=ParsedParameterFile(self.theFile+".gz")
        self.assertEqual(data1,test3.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtripZipped,"test"))

class FoamFileGeneratorRoundtrip2(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(buoyHotRoomTutorial(),"0","T.org")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtrip2,"test"))

class FoamFileGeneratorRoundtrip3(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        if foamVersionNumber()<(1,6):
            envProp="environmentalProperties"
        else:
            envProp="g"
        system("cp "+path.join(damBreakTutorial(),"constant",envProp)+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtrip3,"test"))

class FoamFileGeneratorRoundtrip4(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(buoyHotRoomTutorial(),"0","U")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtrip4,"test"))

class FoamFileGeneratorRoundtrip5(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(turbCavityTutorial(),"0","R")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
        
    
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtrip5,"test"))

class FoamFileGeneratorRoundtripLongList(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(bubbleColumnTutorial(),"0","alpha")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
            
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtripLongList,"test"))

class FoamFileGeneratorRoundtripLongList2(unittest.TestCase):
    def setUp(self):
        self.theFile=tmpnam()
        system("cp "+path.join(bubbleColumnTutorial(),"0","Ua")+" "+self.theFile)

    def tearDown(self):
        system("rm "+self.theFile)
            
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        self.assertEqual(data1,test2.content)
        
theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtripLongList2,"test"))

class MakeStringFunction(unittest.TestCase):
    def testSingleTuple(self):
        self.assertEqual(makeString( (2,3) ),"  2   3 ")
    def testSingleTupleProxy(self):
        self.assertEqual(makeString( TupleProxy((2,3)) ),"  2   3 ")
        
    def testSingleList(self):
        self.assertEqual(makeString( [2,3] ),"(\n  2\n  3\n)\n")
    def testSinglePrimitive(self):
        self.assertEqual(makeString( 2 ),"2")
        
theSuite.addTest(unittest.makeSuite(MakeStringFunction,"test"))

class IncludeFilesRoundTrip(unittest.TestCase):
    def setUp(self):
        self.theDir=tmpnam()
        system("cp -r "+path.join(simpleBikeTutorial(),"0")+" "+self.theDir)
        self.theFile=path.join(self.theDir,"U")
        
    def tearDown(self):
        system("rm -r "+self.theDir)
            
    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        self.assertEqual(data1,test2.content)

if foamVersionNumber()>=(1,6):
    theSuite.addTest(unittest.makeSuite(IncludeFilesRoundTrip,"test"))
