import unittest

from PyFoam.Basics.TemplateFile import TemplateFile,TemplateFileOldFormat,PyratempPreprocessor
from PyFoam.Error import FatalErrorPyFoamException

from tempfile import mktemp

from PyFoam.ThirdParty.six import PY3

import sys

theSuite=unittest.TestSuite()

template1="""$$ y = 3+x
This should be $x+y$"""

template2="""
$$ xxx=13
$$ xx=34+xxx
$2*x+xx-xxx$
"""

templateFor="""$$ y = 2*x
<!--(for i in range(y))--> @!i!@ <!--(end)-->#!
"""

templateMath="sqrt(x) = $sqrt(x)$"

templateList="""<!--(for e in theList)-->#!
  <!--(if e.lower()=="joe")-->#!
Big @!e!@
  <!--(else)-->#!
Little @!e!@
  <!--(end)-->#!
<!--(end)-->#!
"""

templateMacro="""<!--(macro tabsquare)-->
@!x!@ \t = @!x*x!@

<!--(end)-->
<!--(for i in vals)-->@!tabsquare(x=i)!@<!--(end)-->#!
"""

templateBuiltIn="""
<!--(if True)-->TRUE<!--(end)-->
<!--(if not False)-->FALSE<!--(end)-->
@!min(2,3)!@ @!max(2,3)!@
@!chr(42)!@ @!ord(' ')!@
"""

templateVariablesIn3="""
$$ duesenAus=[0,2,3]
$$ duesenNamen=["B30"]+["B%d_%d" % (29-i,j) for i in range(7) for j in [2,1]]
$$ removeDuesen=[duesenNamen[i] for i in duesenAus]
<!--(for d in removeDuesen)-->
|-d-|
<!--(end)-->
"""

class TemplateFileTest(unittest.TestCase):
    def testTemplateFileString(self):
        t=TemplateFile(content=template1,expressionDelimiter="$")
        self.assertEqual(t.getString({"x":-1}),"This should be 1")
        fName=mktemp()
        t.writeToFile(fName,{"x":1+2.})
        result=open(fName).read()
        self.assertEqual(result,"This should be 9.0")

    def testTemplateFileFile(self):
        fName=mktemp()
        open(fName,"w").write(template1)
        t=TemplateFile(name=fName,expressionDelimiter="$")
        self.assertEqual(t.getString({"x":-1}),"This should be 1")

    def testTemplateFileLongVars(self):
        t=TemplateFile(content=template2,expressionDelimiter="$")
        self.assertEqual(int(t.getString({"x":1})),36)

    def testTemplateFileForLoop(self):
        t=TemplateFile(content=templateFor)
        self.assertEqual(t.getString({"x":2})," 0  1  2  3 ")

    def testTemplateFileMacro(self):
        t=TemplateFile(content=templateMacro)
        if PY3 and sys.version_info.minor>1:
            self.assertEqual(t.getString({"vals":[2,3.3,-1]}),"2 \t = 4\n3.3 \t = 10.889999999999999\n-1 \t = 1\n")
        else:
            self.assertEqual(t.getString({"vals":[2,3.3,-1]}),"2 \t = 4\n3.3 \t = 10.89\n-1 \t = 1\n")

    def testTemplateFileListLoop(self):
        t=TemplateFile(content=templateList)
        self.assertEqual(t.getString({"theList":["Henry","Joe","joe","Tom"]}),"Little Henry\nBig Joe\nBig joe\nLittle Tom\n")

    def testTemplateFileLongMath(self):
        t=TemplateFile(content=templateMath,expressionDelimiter="$")
        self.assertEqual(t.getString({"x":4}),"sqrt(x) = 2.0")

    def testTemplateFileMathRealDelim(self):
        t=TemplateFile(content=templateMath.replace("$","|"))
        self.assertEqual(t.getString({"x":4}),"sqrt(x) = 2.0")

    def testTemplateFilePercentDelimiter(self):
        t=TemplateFile(content="x=$!x!$")
        self.assertEqual(t.getString({"x":4}),"x=4")

    def testTemplateFileBuiltinStuff(self):
        t=TemplateFile(content=templateBuiltIn)
        self.assertEqual(t.getString({}),"\nTRUE\nFALSE\n2 3\n* 32\n")
theSuite.addTest(unittest.makeSuite(TemplateFileTest,"test"))

class TemplateFileAllowExecutionTest(unittest.TestCase):
    def testAssignmentNotWorkingInPython3(self):
        t=TemplateFile(content=templateVariablesIn3,
                       expressionDelimiter="|-",
                       allowExec=True)

        self.assertEqual(t.getString({}),"\nB30\nB29_1\nB28_2\n")

class TemplateFileOldFormatTest(unittest.TestCase):
    def testTemplateFileString(self):
        t=TemplateFileOldFormat(content=template1)
        self.assertEqual(t.getString({"x":-1}),"This should be 1\n")
        fName=mktemp()
        t.writeToFile(fName,{"x":"1+sqrt(4)"})
        result=open(fName).read()
        self.assertEqual(result,"This should be 9.0\n")

    def testTemplateFileFile(self):
        fName=mktemp()
        open(fName,"w").write(template1)
        t=TemplateFileOldFormat(name=fName)
        self.assertEqual(t.getString({"x":-1}),"This should be 1\n")

    def testTemplateFileLongVars(self):
        t=TemplateFileOldFormat(content=template2)
        self.assertEqual(int(t.getString({"x":1})),36)

    def testTemplateFileLongMath(self):
        t=TemplateFileOldFormat(content=templateMath)
        self.assertEqual(t.getString({"x":4}),"sqrt(x) = 2.0\n")

theSuite.addTest(unittest.makeSuite(TemplateFileOldFormatTest,"test"))

class PyratempPreprocessorTest(unittest.TestCase):
    def testFullPreprocessing(self):
        p=PyratempPreprocessor()
        self.assertEqual(p("nix\nda"),"nix\nda")
        self.assertEqual(p("nix\nda\n"),"nix\nda\n")
        self.assertEqual(p(""),"")
        self.assertEqual(p("\n"),"\n")
        self.assertEqual(p("$$ a=2 "),'$!setvar("a", "2")!$#!')
        self.assertEqual(p(" $$ a=2 ")," $$ a=2 ")
        self.assertRaises(FatalErrorPyFoamException,p,"$$ a ")
        # Does not work with old nose
#        with self.assertRaises(FatalErrorPyFoamException):
#            p("$$ a ")
        self.assertEqual(p("$$ a=2\n"),'$!setvar("a", "2")!$#!\n')
        self.assertEqual(p("$$ a=2\n$$ b=3"),'$!setvar("a", "2")!$#!\n$!setvar("b", "3")!$#!')
        self.assertEqual(p(" $foo$  $bar$ ")," $!foo!$  $!bar!$ ")
        self.assertEqual(p("$foo$  $bar$"),"$!foo!$  $!bar!$")
        self.assertEqual(p("$foo$  $bar$\n"),"$!foo!$  $!bar!$\n")

    def testNoVarLinePreprocessing(self):
        p=PyratempPreprocessor(dovarline=False)
        self.assertEqual(p("nix\nda"),"nix\nda")
        self.assertEqual(p("nix\nda\n"),"nix\nda\n")
        self.assertEqual(p(""),"")
        self.assertEqual(p("\n"),"\n")
        self.assertEqual(p("$$ a=2 "),'$$ a=2 ')
        self.assertEqual(p(" $$ a=2 ")," $$ a=2 ")
        self.assertEqual(p("$$ a "),"$$ a ")
        self.assertEqual(p("$$ a=2\n"),'$$ a=2\n')
        self.assertEqual(p("$$ a=2\n$$ b=3"),'$$ a=2\n$$ b=3')
        self.assertEqual(p(" $foo$  $bar$ ")," $!foo!$  $!bar!$ ")
        self.assertEqual(p("$foo$  $bar$"),"$!foo!$  $!bar!$")
        self.assertEqual(p("$foo$  $bar$\n"),"$!foo!$  $!bar!$\n")

    def testNoExprPreprocessing(self):
        p=PyratempPreprocessor(doexpr=False)
        self.assertEqual(p("nix\nda"),"nix\nda")
        self.assertEqual(p("nix\nda\n"),"nix\nda\n")
        self.assertEqual(p(""),"")
        self.assertEqual(p("\n"),"\n")
        self.assertEqual(p("$$ a=2 "),'$!setvar("a", "2")!$#!')
        self.assertEqual(p(" $$ a=2 ")," $$ a=2 ")
        self.assertRaises(FatalErrorPyFoamException,p,"$$ a ")
        # Does not work with old nose
#        with self.assertRaises(FatalErrorPyFoamException):
#            p("$$ a ")
        self.assertEqual(p("$$ a=2\n"),'$!setvar("a", "2")!$#!\n')
        self.assertEqual(p("$$ a=2\n$$ b=3"),'$!setvar("a", "2")!$#!\n$!setvar("b", "3")!$#!')
        self.assertEqual(p(" $foo$  $bar$ ")," $foo$  $bar$ ")
        self.assertEqual(p("$foo$  $bar$"),"$foo$  $bar$")
        self.assertEqual(p("$foo$  $bar$\n"),"$foo$  $bar$\n")

theSuite.addTest(unittest.makeSuite(PyratempPreprocessorTest,"test"))
