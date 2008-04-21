
import unittest
import sys

if len(sys.argv)==1:
    doAll=True
else:
    doAll=False
    
from Applications import theSuite as Applications
from Basics import theSuite as Basics
from Execution import theSuite as Execution
from Infrastructure import theSuite as Infrastructure
from LogAnalysis import theSuite as LogAnalysis
from RunDictionary import theSuite as RunDictionary

suite = unittest.TestSuite()

if doAll or "Applications" in sys.argv[1:]:
    suite.addTest(Applications)
if doAll or "Basics" in sys.argv[1:]:
    suite.addTest(Basics)
if doAll or "Execution" in sys.argv[1:]:
    suite.addTest(Execution)
if doAll or "Infrastructure" in sys.argv[1:]:
    suite.addTest(Infrastructure)
if doAll or "LogAnalysis" in sys.argv[1:]:
    suite.addTest(LogAnalysis)
if doAll or "RunDictionary" in sys.argv[1:]:
    suite.addTest(RunDictionary)

unittest.TextTestRunner(verbosity=10).run(suite)
