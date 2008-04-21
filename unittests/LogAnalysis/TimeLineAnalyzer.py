
import unittest
from LineFeeder import feedText

from PyFoam.LogAnalysis.TimeLineAnalyzer import TimeLineAnalyzer

theSuite=unittest.TestSuite()

class TimeLineTest(unittest.TestCase):

    def setTime(self,time):
        self.time=time
        
    def testNormal(self):
        self.time=None
        ta=TimeLineAnalyzer()
        ta.addListener(self.setTime)
        
        feedText(ta,
"""Nix
Time = 1.23
nix"""
        )
        self.assertAlmostEqual(self.time,1.23,6)
        
        feedText(ta,
"""Nix
Time = constant
nix"""
        )
        self.assertNotEqual(self.time,"constant")
        
        feedText(ta,
"""Nix
Time = 1.4 23
nix"""
        )
        self.assertNotEqual(self.time,1.4)
        
theSuite.addTest(unittest.makeSuite(TimeLineTest,"test"))
