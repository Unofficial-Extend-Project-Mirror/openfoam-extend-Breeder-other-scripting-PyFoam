
import unittest

from PyFoam.Basics.TemplateFile import TemplateFile

theSuite=unittest.TestSuite()

template1="""This should be $x+y$
$$ y = 3+x"""

template2="""
$$ xx=34+xxx
$$ xxx=13
$2*x+xx-xxx$
"""

class TemplateFileTest(unittest.TestCase):
    def testTemplateFileString(self):
        t=TemplateFile(content=template1)
        self.assertEqual(t.getString({"x":-1}),"This should be 1\n")
        t.writeToFile("/tmp/testTemplate",{"x":"1+sqrt(4)"})
        result=open("/tmp/testTemplate").read()
        self.assertEqual(result,"This should be 9.0\n")
        
    def testTemplateFileFile(self):
        open("/tmp/writenTemplate","w").write(template1)
        t=TemplateFile(name="/tmp/writenTemplate")
        self.assertEqual(t.getString({"x":-1}),"This should be 1\n")

    def testTemplateFileLongVars(self):
        t=TemplateFile(content=template2)
        self.assertEqual(int(t.getString({"x":1})),36)
                         
theSuite.addTest(unittest.makeSuite(TemplateFileTest,"test"))

