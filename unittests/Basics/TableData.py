
import unittest

from PyFoam.Basics.TableData import TableData

theSuite=unittest.TestSuite()

class CustomPlotInfoTest(unittest.TestCase):
    def testCreateTable(self):
        tb=TableData(["a","b","c"],["d","e","f"])
        self.assertEqual(tb[("a","d")],None)
        tb[("a","d")]=42
        self.assertEqual(tb[("a","d")],42)
        self.assertEqual(tb[("b","d")],None)
        self.assertRaises(IndexError,
                          (lambda:tb[("d","a")]))

theSuite.addTest(unittest.makeSuite(CustomPlotInfoTest,"test"))

