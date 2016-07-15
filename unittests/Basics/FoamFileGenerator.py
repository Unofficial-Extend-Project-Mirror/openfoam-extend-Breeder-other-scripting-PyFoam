import unittest

from PyFoam.Basics.FoamFileGenerator import FoamFileGenerator,makeString,FoamFileGeneratorError
from PyFoam.Basics.DataStructures import DictProxy,TupleProxy,Unparsed,UnparsedList,BoolProxy
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile,FoamStringParser

from PyFoam.FoamInformation import oldTutorialStructure,foamTutorials,foamVersionNumber
from os import system,path,remove
from copy import deepcopy
import warnings

from tempfile import mktemp,mkdtemp
from shutil import rmtree,copytree,copyfile

from PyFoam.ThirdParty.six import PY3,u

from PyFoam.Error import error

if PY3:
    long=int

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
    if foamVersionNumber()>=(3,):
        return path.join(prefix,"twoPhaseEulerFoam","laminar","bubbleColumn")
    else:
        return path.join(prefix,"twoPhaseEulerFoam","bubbleColumn")

def buoyHotRoomTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"heatTransfer")
    if foamVersionNumber()>=(3,):
        return path.join(prefix,"buoyantSimpleFoam","hotRadiationRoom")
    else:
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

def potentialCylinderTutorial():
    prefix=foamTutorials()
    if oldTutorialStructure():
        prefix=path.join(prefix,"potentialFoam")
    else:
        prefix=path.join(prefix,"basic","potentialFoam")
    return path.join(prefix,"cylinder")


class FoamFileGeneratorTest(unittest.TestCase):
    def testMakePrimitives(self):
        g=FoamFileGenerator(1)
        self.assertEqual(str(g),"1")
        g=FoamFileGenerator("1")
        self.assertEqual(str(g),"1")
        g=FoamFileGenerator(u("1"))
        self.assertEqual(str(g),"1")
        g=FoamFileGenerator(1.2)
        self.assertEqual(str(g),"1.2")
        g=FoamFileGenerator(long(1))
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
        g=FoamFileGenerator(list(range(9)))
        self.assertEqual(str(g),"(0 1 2 3 4 5 6 7 8)")
        g=FoamFileGenerator(list(range(6)))
        self.assertEqual(str(g),"(0 1 2 3 4 5)")
        g=FoamFileGenerator([1,2,[3,4],4])
        self.assertEqual(str(g),"(\n  1\n  2\n\n  (\n    3\n    4\n  )\n  4\n)\n")
        g=FoamFileGenerator([1,2,[3,4]])
        self.assertEqual(str(g),"(\n  1\n  2\n\n  (\n    3\n    4\n  )\n)\n")
        g=FoamFileGenerator(["1",u("2")])
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
        d[u("a")]=1
        d["b"]=u("2")
        g=FoamFileGenerator(d)
        self.assertEqual(str(g),"a 1;\nb 2;\n")

    def testMakeDictionaryProxyBool(self):
        d=DictProxy()
        d["b"]=True
        d["a"]=False
        g=FoamFileGenerator(d)
        self.assertEqual(str(g),"b yes;\na no;\n")

    def testMakeDictionaryRedirect(self):
        val="""
a {
   b 2;
}
c {
   $a;
   d 3;
}
"""
        d=FoamStringParser(
            val,
            doMacroExpansion=True
        )
        self.assertEqual(str(d),"a\n{\n  b 2;\n}\nc\n{\n  $a;\n  d 3;\n}\n")
        d=FoamStringParser(
            val,
            doMacroExpansion=False
        )
        self.assertEqual(str(d),"a\n{\n  b 2;\n}\nc\n{\n  $a ;\n  d 3;\n}\n")

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

    def testMakeLongList(self):
        g=FoamFileGenerator([i for i in range(20)])
        testString="(\n  0"
        self.assertEqual(str(g)[0:len(testString)],testString)
        g=FoamFileGenerator([i for i in range(21)])
        testString="21\n(\n  0"
        self.assertEqual(str(g)[0:len(testString)],testString)
        g=FoamFileGenerator([i for i in range(20)],longListThreshold=10)
        testString="20\n(\n  0"
        self.assertEqual(str(g)[0:len(testString)],testString)
        g=FoamFileGenerator([i for i in range(21)],longListThreshold=None)
        testString="(\n  0"
        self.assertEqual(str(g)[0:len(testString)],testString)

    def testBool(self):
        g=FoamFileGenerator({'a':True})
        self.assertEqual(str(g),"a yes;\n")
        g=FoamFileGenerator({'a':False})
        self.assertEqual(str(g),"a no;\n")
        g=FoamFileGenerator({'a':BoolProxy(True)})
        self.assertEqual(str(g),"a yes;\n")
        g=FoamFileGenerator({'a':BoolProxy(True,textual="on")})
        self.assertEqual(str(g),"a yes;\n")

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
        self.theFile=mktemp()
        #        print self.theFile,damBreakTutorial()
        copyfile(path.join(damBreakTutorial(),"system","fvSolution"),self.theFile)

    def tearDown(self):
        remove(self.theFile)

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
        self.theFile=mktemp()
        copyfile(path.join(damBreakTutorial(),"system","fvSchemes"),self.theFile)

    def tearDown(self):
        remove(self.theFile)

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
        self.theFile=mktemp()
        copyfile(path.join(damBreakTutorial(),"system","fvSolution"),self.theFile)
        system("gzip -f "+self.theFile)

    def tearDown(self):
        remove(self.theFile+".gz")

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
        self.theFile=mktemp()
        try:
            copyfile(path.join(buoyHotRoomTutorial(),"0","T.org"),self.theFile)
        except IOError:
            copyfile(path.join(buoyHotRoomTutorial(),"0","T"),self.theFile)

    def tearDown(self):
        remove(self.theFile)

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
        self.theFile=mktemp()
        if foamVersionNumber()<(1,6):
            envProp="environmentalProperties"
        else:
            envProp="g"
        copyfile(path.join(damBreakTutorial(),"constant",envProp),self.theFile)

    def tearDown(self):
        remove(self.theFile)

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
        self.theFile=mktemp()
        copyfile(path.join(buoyHotRoomTutorial(),"0","U"),self.theFile)

    def tearDown(self):
        remove(self.theFile)

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
        self.theFile=mktemp()
        if foamVersionNumber()<(2,):
            # there is no appropriate volSymmTensorField-file in 2.x
            copyfile(path.join(turbCavityTutorial(),"0","R"),self.theFile)

    def tearDown(self):
        if foamVersionNumber()<(2,):
            # there is no appropriate volSymmTensorField-file in 2.x
            remove(self.theFile)

    def testReadTutorial(self):
        if foamVersionNumber()>=(2,):
            # there is no appropriate volSymmTensorField-file in 2.x
            return

        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)

theSuite.addTest(unittest.makeSuite(FoamFileGeneratorRoundtrip5,"test"))

class FoamFileGeneratorRoundtripLongList(unittest.TestCase):
    def setUp(self):
        self.theFile=mktemp()
        alphaName="alpha"
        if foamVersionNumber()>=(3,):
            alphaName="alpha.air"
        elif foamVersionNumber()>=(2,):
            alphaName="alpha1"
        copyfile(path.join(bubbleColumnTutorial(),"0",alphaName),self.theFile)

    def tearDown(self):
        remove(self.theFile)

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
        self.theFile=mktemp()
        UName="Ua"
        if foamVersionNumber()>=(3,):
            UName="U.air"
        elif foamVersionNumber()>=(2,):
            UName="U1"

        copyfile(path.join(bubbleColumnTutorial(),"0",UName),self.theFile)

    def tearDown(self):
        remove(self.theFile)

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

    def testNonunifomLength(self):
        p1=FoamStringParser('test  nonuniform 2(1 2);')
        self.assertEqual(str(p1),"test nonuniform 2\n(\n  1\n  2\n)\n;\n")

    def testNonunifomLengthThree(self):
        p1=FoamStringParser('test  nonuniform 2(1 2 3);')
        self.assertEqual(str(p1),"test nonuniform 3\n(\n  1\n  2\n  3\n)\n;\n")

    def testNonunifomLengthZero(self):
        p1=FoamStringParser('test  nonuniform 0();')
        self.assertEqual(str(p1),"test nonuniform 0\n(\n)\n;\n")

theSuite.addTest(unittest.makeSuite(MakeStringFunction,"test"))

class IncludeFilesRoundTrip(unittest.TestCase):
    def setUp(self):
        self.theDir=mkdtemp()
        if oldTutorialStructure():
            null="0"
        else:
            null="0.org"

        usedDir=path.join(self.theDir,"data")
        copytree(path.join(simpleBikeTutorial(),null),usedDir)
        self.theFile=path.join(usedDir,"U")

    def tearDown(self):
        rmtree(self.theDir)

    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile,listLengthUnparsed=100)
        self.assertEqual(data1,test2.content)

    def testReadTutorialWithMacros(self):
        test=ParsedParameterFile(self.theFile,
                                 listLengthUnparsed=100,
                                 doMacroExpansion=True)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile,listLengthUnparsed=100,doMacroExpansion=True)
        self.compareData(data1,test2.content)

    def compareData(self,d1,d2):
        for k in d1:
            if type(k) not in [int]:
                if type(d1[k])!=DictProxy:
                    self.assertEqual(str(d1[k]),str(d2[k]))
                else:
                    self.compareData(d1[k],d2[k])

if foamVersionNumber()>=(1,6):
    theSuite.addTest(unittest.makeSuite(IncludeFilesRoundTrip,"test"))

class CodeStreamRoundTrip(unittest.TestCase):
    def setUp(self):
        self.theDir=mkdtemp()
        usedDir=path.join(self.theDir,"data")
        copytree(potentialCylinderTutorial(),usedDir)
        self.theFile=path.join(usedDir,"system","controlDict")

    def tearDown(self):
        rmtree(self.theDir)

    def testBasicInclude(self):
        if foamVersionNumber()<(2,):
            return
        test=ParsedParameterFile(self.theFile)
        data1=deepcopy(test.content)
        open(self.theFile,"w").write(str(FoamFileGenerator(data1,header=test.header)))
        del test
        test2=ParsedParameterFile(self.theFile)
        self.assertEqual(data1,test2.content)

if foamVersionNumber()>=(2,):
    theSuite.addTest(unittest.makeSuite(CodeStreamRoundTrip,"test"))
