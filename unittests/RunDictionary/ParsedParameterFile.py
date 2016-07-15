import unittest

from PyFoam.FoamInformation import oldTutorialStructure,foamTutorials,foamVersionNumber
from os import path,remove
from tempfile import mktemp,mkdtemp
from shutil import copyfile,rmtree,copytree

from PyFoam.RunDictionary.ParsedParameterFile import FoamStringParser,ParsedParameterFile,ParsedBoundaryDict,DictProxy,TupleProxy,PyFoamParserError,WriteParameterFile

from PyFoam.Basics.FoamFileGenerator import Vector,Dimension,Field,Tensor,SymmTensor,Codestream

from PyFoam.FoamInformation import oldAppConvention as oldApp

from .TimeDirectory import damBreakTutorial,gammaName

from PyFoam.Error import error

def simpleBikeTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"incompressible")
    else:
        error("The simpleFoam-motorBike-case does not exist before 1.6")

    return path.join(prefix,"simpleFoam","motorBike")

def simplePitzTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"incompressible")
    return path.join(prefix,"simpleFoam","pitzDaily")

def buoyHotRoomTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"heatTransfer")
    if foamVersionNumber()>=(3,):
        return path.join(prefix,"buoyantSimpleFoam","hotRadiationRoom")
    else:
        return path.join(prefix,"buoyantSimpleFoam","hotRoom")

def XoodlesPitzTutorial():
    prefix=foamTutorials()
    if oldTutorialStructure():
        prefix=path.join(prefix,"Xoodles")
    else:
        prefix=path.join(prefix,"combustion","XiFoam","les")
    return path.join(prefix,"pitzDaily3D")

def XiFoamMoriyoshiTutorial():
    prefix=foamTutorials()
    return path.join(prefix,"combustion","XiFoam","ras","moriyoshiHomogeneous")

def dieselAachenTutorial():
    prefix=foamTutorials()
    if not oldTutorialStructure():
        prefix=path.join(prefix,"combustion")
    return path.join(prefix,"dieselFoam","aachenBomb")

def turbCavityTutorial():
    prefix=foamTutorials()
    if oldTutorialStructure():
        prefix=path.join(prefix,"turbFoam")
    else:
        prefix=path.join(prefix,"incompressible","pisoFoam","ras")
    return path.join(prefix,"cavity")

def potentialCylinderTutorial():
    prefix=foamTutorials()
    if oldTutorialStructure():
        prefix=path.join(prefix,"potentialFoam")
    else:
        prefix=path.join(prefix,"basic","potentialFoam")
    return path.join(prefix,"cylinder")

theSuite=unittest.TestSuite()

class FoamStringParserTest(unittest.TestCase):

    def testParseInteger(self):
        p1=FoamStringParser("test 1;")
        self.assertEqual(p1["test"],1)

    def testParseBool(self):
        p1=FoamStringParser("test yes;")
        self.assertEqual(p1["test"],True)
        self.assertEqual(p1["test"],"yes")
        p1=FoamStringParser("test on;")
        self.assertEqual(p1["test"],"on")
        self.assertEqual(p1["test"],True)
        p1=FoamStringParser("test off;")
        self.assertEqual(p1["test"],False)
        p1=FoamStringParser("test no;")
        self.assertEqual(p1["test"],False)

    def testParseBoolKey(self):
        p1=FoamStringParser("yes test;")
        self.assertEqual(p1["yes"],"test")

    def testParseWithTab(self):
        p1=FoamStringParser("test\t1;")
        self.assertEqual(p1["test"],1)
        p1=FoamStringParser("\ttest\t 1 \t;")
        self.assertEqual(p1["test"],1)

    def testParseFloat(self):
        p1=FoamStringParser("test 1.23e-4;")
        self.assertAlmostEqual(p1["test"],1.234e-4,6)

    def testParseFloat2(self):
        p1=FoamStringParser("test 1.e-4;")
        self.assertEqual(type(p1["test"]),float)
        self.assertAlmostEqual(p1["test"],1.e-4,6)

    def testParseFloat3(self):
        p1=FoamStringParser("test 1.E-4;")
        self.assertEqual(type(p1["test"]),float)
        self.assertAlmostEqual(p1["test"],1.e-4,6)

    def testParseString(self):
        p1=FoamStringParser('test "der name";')
        self.assertEqual(p1["test"][1:-1],"der name")

    def testParseMultilineString(self):
        p1=FoamStringParser("""test #{
der name
#};""")
        self.assertEqual(p1["test"][1:-1],"der name")
        self.assertEqual(p1["test"].count('\n'),2)

    def testParseWord(self):
        p1=FoamStringParser('test  name;')
        self.assertEqual(p1["test"],"name")

    def testParseWordUniform(self):
        p1=FoamStringParser('test  uniform;')
        self.assertEqual(p1["test"],"uniform")

    def testParseFieldUniform(self):
        p1=FoamStringParser('test  uniform 42;')
        self.assertEqual(type(p1["test"]),Field)
        self.assert_(p1["test"].isUniform())

    def testParseFieldNonniform(self):
        p1=FoamStringParser('test  nonuniform 4(42 66 34 44);')
        self.assertEqual(type(p1["test"]),Field)
        self.assert_(not p1["test"].isUniform())

    def testParseFieldNonniformLengthThree(self):
        p1=FoamStringParser('test  nonuniform 3(42 66 34);')
        self.assertEqual(type(p1["test"]),Field)
        self.assert_(not p1["test"].isUniform())

    def testParseFieldNonniformLengthZero(self):
        p1=FoamStringParser('test  nonuniform 0();')
        self.assertEqual(type(p1["test"]),Field)
        self.assert_(not p1["test"].isUniform())

    def testListPrefixUniform(self):
        p=FoamStringParser("test 10{42.5};")
        self.assertEqual(len(p["test"]),10)
        self.assertEqual(type(p["test"]),Field)
        self.assert_(p["test"].isUniform())

    def testListPrefixUniformVector(self):
        p=FoamStringParser("test 10{(1 2 3)};")
        self.assertEqual(len(p["test"]),10)
        self.assertEqual(type(p["test"]),Field)
        self.assert_(p["test"].isUniform())

    def testListPrefixNested(self):
        p=FoamStringParser("test 3 ( 3{0.} 3 (1 1 1) 3 (2 2 2));")
        self.assertEqual(len(p["test"]),3)

    def testParseWordMinus(self):
        p1=FoamStringParser('test  name-0;')
        self.assertEqual(p1["test"],"name-0")

    def testParseWordWithBrackets(self):
        p1=FoamStringParser('test  div((phi*nix),U);')
        self.assertEqual(p1["test"],"div((phi*nix),U)")

    def testParseWordWithBrackets2(self):
        p1=FoamStringParser('test  div((phi&nix),U);')
        self.assertEqual(p1["test"],"div((phi&nix),U)")

    def testParseStrangeNames(self):
        p1=FoamStringParser('test%1 1;')
        self.assertEqual(p1["test%1"],1)

    def testParseStrangeNames2(self):
        p1=FoamStringParser('test+1 1;')
        self.assertEqual(p1["test+1"],1)

    def testParseStrangeNames3(self):
        p1=FoamStringParser('test:1 1;')
        self.assertEqual(p1["test:1"],1)

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

    def testDataList3(self):
        p1=FoamStringParser("test (5 4 (2 3 4 5));")
        self.assertEqual(type(p1["test"]),list)
        self.assertEqual(len(p1["test"]),2)

    def testDataListFOType(self):
        p1=FoamStringParser("test ( fo1 {a 2;});")
        self.assertEqual(type(p1["test"]),list)
        self.assertEqual(len(p1["test"]),2)

    def testDataListFOTypeExtraSemicolon(self):
        p1=FoamStringParser("test ( fo1 {a 2;};);")
        self.assertEqual(type(p1["test"]),list)
        self.assertEqual(len(p1["test"]),2)

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

    def testDataNoVector(self):
        p1=FoamStringParser("test ( 1 3 4 );",
                            noVectorOrTensor=True)
        self.assertEqual(p1["test"].__class__,list)

    def testDataTensor(self):
        p1=FoamStringParser("test ( 1 2 3 4 5 4 3 2 1 );")
        self.assertEqual(p1["test"].__class__,Tensor)

    def testDataNoTensor(self):
        p1=FoamStringParser("test ( 1 2 3 4 5 4 3 2 1 );",
                            noVectorOrTensor=True)
        self.assertEqual(p1["test"].__class__,list)

    def testDataSymmTensor(self):
        p1=FoamStringParser("test ( 1 2 3 4 5 4 );")
        self.assertEqual(p1["test"].__class__,SymmTensor)

    def testDataNoSymmTensor(self):
        p1=FoamStringParser("test ( 1 2 3 4 5 4 );",
                            noVectorOrTensor=True)
        self.assertEqual(p1["test"].__class__,list)

    def testDataDimension(self):
        p1=FoamStringParser("test [1 2 -3 0 1.4 1 2];")
        self.assertEqual(p1["test"].__class__,Dimension)

        p1=FoamStringParser("test [1 2 -3 0 1.4];")
        self.assertEqual(p1["test"].__class__,Dimension)

    def testDataDimensionSymbolic(self):
        p1=FoamStringParser("test [m s^-1];")
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
        p1=FoamStringParser("test ding; // test dings 2;")
        self.assertEqual(p1["test"],"ding")

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

    def testNestedComment(self):
        p=FoamStringParser("""
        /* this should never be read
        /* that is never there */
        This too */
        test dings 2;""")
        self.assertEqual(str(p),"test dings     2 ;\n")

    def testCommentOutElements(self):
        p1=FoamStringParser("""things (
// test dings 2;
nix // Hepp
);""")
        self.assertEqual(len(p1["things"]),1)
        self.assertEqual(p1["things"][0],"nix")

    def testListInList(self):
        p=FoamStringParser("test (2.3 (3.3 -3 3) 2);")
        self.assertEqual(len(p["test"]),3)
        self.assertEqual(type(p["test"][1]),Vector)
        self.assertEqual(p["test"][1][0],3.3)

    def testListAllPreList(self):
        p=FoamStringParser("test (3(1.1 -1 1) 3(2.2 -2 2) 3(3.3 -3 3));")
        self.assertEqual(len(p["test"]),3)
        self.assertEqual(type(p["test"][1]),list)
        self.assertEqual(p["test"][1][0],2.2)

    def testListAllPreListNoVector(self):
        p=FoamStringParser("test (3(1.1 -1 1) 3(2.2 -2 2) 3(3.3 -3 3));",
                           noVectorOrTensor=True)
        self.assertEqual(len(p["test"]),3)
        self.assertEqual(type(p["test"][1]),list)
        self.assertEqual(p["test"][1][0],2.2)

    def testPreListUniform(self):
        p=FoamStringParser("test 5 {42.1} ;")
        self.assertEqual(len(p["test"]),5)
        self.assertEqual(p["test"][2],42.1)

    def testPreListUniformNested(self):
        p=FoamStringParser("test 2 (5 {42.1} 5 (1 2 3 4 5)) ;")
        #        p=FoamStringParser("test 2 (5 (42.1 42.1 42.1 42.1 42.1) 5 (1 2 3 4 5)) ;")
        self.assertEqual(len(p["test"]),2)
        self.assertEqual(len(p["test"][0]),5)
        self.assertEqual(p["test"][0][2],42.1)
        self.assertEqual(p["test"][1][2],3)

    def testReactionList(self):
        p=FoamStringParser("""test (
someReaction
   0.5 H2 + O2 = H2O
   (1000 0 10)
otherReaction
   C + O2 = CO2
   ((1000 0 10) (3 4 5))
);""")
        self.assertEqual(type(p["test"][0]),str)
        self.assertEqual(type(p["test"][1]),str)
        self.assertEqual(type(p["test"][2]),Vector)
        self.assertEqual(type(p["test"][3]),str)
        self.assertEqual(type(p["test"][4]),str)
        self.assertEqual(type(p["test"][5]),list)

    def testFalseReactionBug(self):
        p1=FoamStringParser("""things (
test // test = dings 2;
nix
);""")
        self.assertEqual(len(p1["things"]),2)
        self.assertEqual(p1["things"][0],"test")

    def testStringWithAssignment(self):
        p1=FoamStringParser('''
nix "a=3+x;b=4;";
''')
        self.assertEqual(p1["nix"],'"a=3+x;b=4;"')

    def testDeletionOfEntry(self):
        p1=FoamStringParser("nix 2; test  3;")
        self.assertEqual(p1["nix"],2)
        del p1["nix"]
        self.assert_("nix" not in p1)

    def testSubstitute1(self):
        p1=FoamStringParser("nix $da;")
        self.assertEqual(p1["nix"],"$da")

    def testSubstitute2(self):
        p1=FoamStringParser("nix 2 $da;")
        self.assertEqual(p1["nix"],[2,"$da"])

    def testInclude(self):
        p1=FoamStringParser('#include "nixda"\n')
        p1=FoamStringParser('#include "nixda" ; \n')

    def testRemove(self):
        p1=FoamStringParser('#remove da\n')
        p1=FoamStringParser('#remove da;\n')
        p1=FoamStringParser('#remove da; ;\n')

    def testRemoveList(self):
        p1=FoamStringParser('#remove (nix da) ;\n')
        p1=FoamStringParser('#remove (nix da)\n')

    def testInputMode(self):
        p1=FoamStringParser('#inputMode merge\n')
        p1=FoamStringParser('#inputMode merge foobar\n')

    def testInputMode2(self):
        p1=FoamStringParser('#inputMode overwrite\n')
        p1=FoamStringParser('#inputMode overwrite;\n')

    def testInputMode3(self):
        p1=FoamStringParser('#inputMode error\n')

    def testInputMode4(self):
        p1=FoamStringParser('#inputMode default\n')

theSuite.addTest(unittest.makeSuite(FoamStringParserTest,"test"))

class ParsedParameterDictionaryMacroExpansion(unittest.TestCase):
    def testSimpleSubst(self):
        p1=FoamStringParser("""
a 10;
b $a;
""",doMacroExpansion=True)
        self.assertEqual(p1["b"],10)

    def testSimpleSubstNoMacro(self):
        p1=FoamStringParser("""
a 10;
b $a;
        """,doMacroExpansion=False)
        self.assertEqual(p1["b"],"$a")

    def testSubdictSubst(self):
        p1=FoamStringParser("""
subdict
{
    a 10;
}
b $subdict.a;
""",doMacroExpansion=True)
        self.assertEqual(p1["b"],10)

    def testParentDict(self):
        p1=FoamStringParser("""
a 10;

subdict
{
    b $..a;  // double-dot takes scope up 1 level, then 'a' is available

    subsubdict
    {
        c $:a; // colon takes scope to top level, then 'a' is available
        d $...a;
    }
}
""",doMacroExpansion=True)
        self.assertEqual(p1["subdict"]["b"],10)
        self.assertEqual(p1["subdict"]["subsubdict"]["c"],10)
        self.assertEqual(p1["subdict"]["subsubdict"]["d"],10)

    def testParentDictNoMacro(self):
        p1=FoamStringParser("""
a 10;

subdict
{
    b $..a;  // double-dot takes scope up 1 level, then 'a' is available

    subsubdict
    {
        c $:a; // colon takes scope to top level, then 'a' is available
        d $...a;
    }
}
        """,doMacroExpansion=False)
        self.assertEqual(p1["subdict"]["b"],"$..a")
        self.assertEqual(p1["subdict"]["subsubdict"]["c"],"$:a")
        self.assertEqual(p1["subdict"]["subsubdict"]["d"],"$...a")

    def testRedirect(self):
        p1=FoamStringParser("""
a 10;
b a;
c ${${b}}; // returns 10, since $b returns 'a', and $a returns 10
        """,doMacroExpansion=True)
        self.assertEqual(p1["b"],"a")
        self.assertEqual(p1["c"],10)

    def testRedirectNoMacro(self):
        p1=FoamStringParser("""
a 10;
b a;
c ${${b}}; // returns 10, since $b returns 'a', and $a returns 10
        """,doMacroExpansion=False)
        self.assertEqual(p1["b"],"a")
        self.assertEqual(p1["c"],"${${b}}")

theSuite.addTest(unittest.makeSuite(ParsedParameterDictionaryMacroExpansion,"test"))

class ParsedBoundaryDictTest(unittest.TestCase):
    def setUp(self):
        self.theFile=mktemp()
        copyfile(path.join(foamTutorials(),"incompressible","simpleFoam","airFoil2D","constant","polyMesh","boundary"),self.theFile)

    def tearDown(self):
        remove(self.theFile)

    def testReadTutorial(self):
        test=ParsedBoundaryDict(self.theFile)
        self.assertEqual(len(test.content),4)
        self.assert_("inlet" in test)

theSuite.addTest(unittest.makeSuite(ParsedBoundaryDict,"test"))

class ParsedParameterFileTest(unittest.TestCase):
    def setUp(self):
        self.theFile=mktemp()
        turb=path.join(simplePitzTutorial(),"constant")
        if oldApp():
            turb=path.join(turb,"turbulenceProperties")
        elif foamVersionNumber()>=(3,):
            turb=path.join(turb,"turbulenceProperties")
        else:
            turb=path.join(turb,"RASProperties")

        copyfile(turb,self.theFile)

    def tearDown(self):
        remove(self.theFile)

    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        if foamVersionNumber()<(1,5):
            nrTurbModels=17
            model="turbulenceModel"
        elif foamVersionNumber()>=(3,):
            test=test["RAS"]
            nrTurbModels=3
            model="RASModel"
        else:
            if foamVersionNumber()<(1,6):
                nrTurbModels=19
            else:
                nrTurbModels=3

            model="RASModel"

        # self.assertEqual(len(test.content),nrTurbModels)
        self.assertEqual(len(test),nrTurbModels)
        self.assertEqual(test[model],"kEpsilon")

theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest,"test"))

class ParsedParameterFileTest2(unittest.TestCase):
    def setUp(self):
        self.theFile=mktemp()
        if foamVersionNumber()>=(2,0):
            extension=".org"
        else:
            extension=""
        copyfile(path.join(damBreakTutorial(),"0",gammaName()+extension),self.theFile)

    def tearDown(self):
        remove(self.theFile)

    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        self.assertEqual(len(test["boundaryField"]),5)

theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest2,"test"))

class ParsedParameterFileTest3(unittest.TestCase):
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
        if foamVersionNumber()>=(3,):
            self.assertEqual(len(test["boundaryField"]),4)
        else:
            self.assertEqual(len(test["boundaryField"]),3)
        if foamVersionNumber()<(2,):
            self.assertEqual(len(test["boundaryField"]["floor"]["value"].val),400)

theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest3,"test"))

class ParsedParameterFileTest4(unittest.TestCase):
    def setUp(self):
        self.theFile=mktemp()
        try:
            copyfile(path.join(XoodlesPitzTutorial(),"system","fvSchemes"),self.theFile)
        except IOError:
            copyfile(path.join(XiFoamMoriyoshiTutorial(),"system","fvSchemes"),self.theFile)

    def tearDown(self):
        remove(self.theFile)

    def testReadTutorial(self):
        test=ParsedParameterFile(self.theFile)
        gradSchemes=1
        divSchemes=4
        if foamVersionNumber()<(1,6):
            gradSchemes=2
            divSchemes=5
        self.assertEqual(len(test["gradSchemes"]),gradSchemes)
        if foamVersionNumber()>=(3,):
            self.assertEqual(len(test["divSchemes"]["div(phi,ft_b_ha_hau)"][2]),5)
        else:
            self.assertEqual(len(test["divSchemes"]["div(phi,ft_b_h_hu)"][2]),divSchemes)

theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest4,"test"))

class ParsedParameterFileTest5(unittest.TestCase):
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
        self.assertEqual(test["internalField"].__class__,Field)
        self.assertEqual(test["internalField"].isUniform(),True)
        if foamVersionNumber()<(1,5):
            self.assertEqual(test["internalField"].value().__class__,Tensor)
        else:
            self.assertEqual(test["internalField"].value().__class__,SymmTensor)

theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest5,"test"))

class ParsedParameterFileTest6(unittest.TestCase):
    def setUp(self):
        try:
            if foamVersionNumber()>=(1,6):
                from nose.plugins.skip import SkipTest
                raise SkipTest()
        except ImportError:
            pass

        self.theFile=mktemp()
        copyfile(path.join(dieselAachenTutorial(),"0","spray"),self.theFile)

    def tearDown(self):
        remove(self.theFile)

    def testReadTutorial(self):
        try:
            test=ParsedParameterFile(self.theFile)
        except PyFoamParserError:
            pass

if foamVersionNumber()<(1,5):
    theSuite.addTest(unittest.makeSuite(ParsedParameterFileTest6,"test"))

class ParsedParameterFileIncludeTest(unittest.TestCase):
    def setUp(self):
        if oldTutorialStructure():
            null="0"
        else:
            null="0.org"
        self.fileName=path.join(simpleBikeTutorial(),null,"U")

    def tearDown(self):
        pass

    def testBasicInclude(self):
        test=ParsedParameterFile(self.fileName,doMacroExpansion=True)
        self.assertEqual(test["pressure"],0)
        self.assertEqual("upperWall" in test["boundaryField"],True)
        self.assertEqual(test["boundaryField"]["upperWall"]["type"],"slip")

if foamVersionNumber()>=(1,6):
    theSuite.addTest(unittest.makeSuite(ParsedParameterFileIncludeTest,"test"))

class ParsedParameterFileCodeStreamTest(unittest.TestCase):
    def setUp(self):
        self.fileName=path.join(potentialCylinderTutorial(),"system","controlDict")

    def tearDown(self):
        pass

    def testBasicInclude(self):
        test=ParsedParameterFile(self.fileName)
        if foamVersionNumber()<(2,):
            return
        self.assertEqual(type(test["functions"]["difference"]["code"]),Codestream)

if foamVersionNumber()>=(2,):
    theSuite.addTest(unittest.makeSuite(ParsedParameterFileCodeStreamTest,"test"))

class ParsedParameterFileRedirectDictionary(unittest.TestCase):
    def setUp(self):
        self.data="""
dictA {
        a 1;
        b 2;
        c 3;
}
dictB {
        $dictA;

        a 4;
        d 5;
}
dictC {
        a 6;
        $dictB;
        d 7;
        e 8;
        c 9;
}
        """

    def tearDown(self):
        pass

    def testExistsRedirect(self):
        data=FoamStringParser(
            self.data,
            doMacroExpansion=True)
        self.assertEqual("a" in data["dictA"],True)
        self.assertEqual("b" in data["dictC"],True)

        data=FoamStringParser(
            self.data,
            doMacroExpansion=False)
        self.assertEqual("a" in data["dictA"],True)
        self.assertEqual("b" in data["dictC"],False)

    def testReadRedirect(self):
        data=FoamStringParser(
            self.data,
            doMacroExpansion=True)
        self.assertEqual(data["dictA"]["a"],1)
        self.assertEqual(data["dictB"]["a"],4)
        self.assertEqual(data["dictC"]["a"],6)

        self.assertEqual(data["dictA"]["b"],2)
        self.assertEqual(data["dictB"]["b"],2)
        self.assertEqual(data["dictC"]["b"],2)

        self.assertEqual(data["dictB"]["d"],5)
        self.assertEqual(data["dictC"]["d"],7)

        self.assertEqual(data["dictA"]["c"],3)
        self.assertEqual(data["dictB"]["c"],3)
        self.assertEqual(data["dictC"]["c"],9)

    def testWriteRedirect(self):
        data=FoamStringParser(
            self.data,
            doMacroExpansion=True)
        self.assertEqual(data["dictA"]["a"],1)
        self.assertEqual(data["dictB"]["a"],4)
        self.assertEqual(data["dictC"]["a"],6)
        data["dictC"]["a"]=16
        self.assertEqual(data["dictA"]["a"],1)
        self.assertEqual(data["dictB"]["a"],4)
        self.assertEqual(data["dictC"]["a"],16)
        data["dictA"]["f"]=17
        self.assertEqual(data["dictA"]["f"],17)
        self.assertEqual(data["dictA"]["f"],17)
        self.assertEqual(data["dictA"]["f"],17)

theSuite.addTest(unittest.makeSuite(ParsedParameterFileRedirectDictionary,"test"))

class ParsedParameterFileDictionaryNested(unittest.TestCase):
    def setUp(self):
        self.data="""
f 9;

dictA {
        a 1;
        b 2;
        c 3;
        dictB {
               a 4;
               d $c;
               dictC {
                     d 7;
                     dictD {
                           e $d;
                           c $a;
                           g $f;
        }}}
}
        """

    def tearDown(self):
        pass

    def testNestedValues(self):
        data=FoamStringParser(
            self.data,
            doMacroExpansion=True)
        self.assertEqual(
            data["dictA"]["dictB"]["d"],
            data["dictA"]["c"])
        self.assertEqual(
            data["dictA"]["dictB"]["dictC"]["dictD"]["g"],
            data["f"])
        self.assertEqual(
            data["dictA"]["dictB"]["dictC"]["dictD"]["c"],
            data["dictA"]["dictB"]["a"])
        self.assertEqual(
            data["dictA"]["dictB"]["dictC"]["dictD"]["e"],
            data["dictA"]["dictB"]["dictC"]["d"])

theSuite.addTest(unittest.makeSuite(ParsedParameterFileDictionaryNested,"test"))

class ParsedParameterFileDictionaryNestedCopy(unittest.TestCase):
    def setUp(self):
        self.data="""

dictA {
        a 1;
        b 2;
        c 3;
}

dictB {
        a 4;
        d $dictA;
}
        """

    def tearDown(self):
        pass

    def testNestedValues(self):
        data=FoamStringParser(
            self.data,
            doMacroExpansion=True)
        self.assertEqual(data["dictA"]["a"],data["dictB"]["d"]["a"])
        data["dictB"]["d"]["a"]=42
        self.assertEqual(data["dictA"]["a"],1)
        self.assertEqual(42,data["dictB"]["d"]["a"])

theSuite.addTest(unittest.makeSuite(ParsedParameterFileDictionaryNestedCopy,"test"))

class WriteParameterFileTest(unittest.TestCase):
    def setUp(self):
        self.testDir=mkdtemp()
        self.dest=path.join(self.testDir,"testDictionary")

    def tearDown(self):
        rmtree(self.testDir)

    def testOrderOfAdditionsPreserved(self):
        orig=WriteParameterFile(self.dest)
        orig["a"]=1;
        orig["b"]=2;
        orig["d"]=3;
        orig["c"]=4;
        self.assertEqual(str(orig),"""// -*- C++ -*-
// File generated by PyFoam - sorry for the ugliness

FoamFile
{
 class dictionary;
 format ascii;
 object testDictionary;
 version 2.0;
}

a 1;

b 2;

d 3;

c 4;

""")

theSuite.addTest(unittest.makeSuite(WriteParameterFileTest,"test"))

class ReadIncludeAndMacroExpansionTest(unittest.TestCase):
    def setUp(self):
        self.testDir=mkdtemp()
        self.dest=path.join(self.testDir,"0.org")
        copytree(path.join(foamTutorials(),"incompressible","simpleFoam","motorBike","0.org"),
                 self.dest)

    def tearDown(self):
        rmtree(self.testDir)

    def testReadNoMacroExpansion(self):
        kFile=ParsedParameterFile(path.join(self.dest,"k"))
        self.assertEqual(str(kFile["internalField"]),"uniform $turbulentKE")
        self.assertEqual(kFile["boundaryField"]["lowerWall"]["value"],"$internalField")
        self.assertEqual(kFile["boundaryField"]["motorBikeGroup"]["value"],"$internalField")

    def testReadMacroExpansion(self):
        kFile=ParsedParameterFile(path.join(self.dest,"k"),
                                  doMacroExpansion=True)
        self.assertEqual(str(kFile["internalField"]),"uniform 0.24")
        self.assertEqual(str(kFile["boundaryField"]["lowerWall"]["value"]),"uniform 0.24")
        self.assertEqual(str(kFile["boundaryField"]["motorBikeGroup"]["value"]),"uniform 0.24")


theSuite.addTest(unittest.makeSuite(WriteParameterFileTest,"test"))
