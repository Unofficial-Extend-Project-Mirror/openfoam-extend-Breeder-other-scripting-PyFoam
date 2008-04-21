""" Analyzes the output of a interFoam-Run and writes the results to files
in a directory
"""
import sys,re

if len(sys.argv)<2:
    print "To few arguments: name of logfile needed"
    sys.exit(-1)

from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.LogAnalysis.LogAnalyzerApplication import LogAnalyzerApplication
from PyFoam.LogAnalysis.SimpleLineAnalyzer import SimpleLineAnalyzer


class InterFoamLogAnalyzer(BoundingLogAnalyzer):
    def __init__(self):
        BoundingLogAnalyzer.__init__(self)
        self.addAnalyzer("deltaT",SimpleLineAnalyzer("deltaT","^deltaT = (.+)$"))
        self.addAnalyzer("LiquidPhase",SimpleLineAnalyzer("liquid","^Liquid phase volume fraction = (.+) Min\((.+)\) = (.+) Max\(.+\) = (.+)$",idNr=2))
        
analyze=LogAnalyzerApplication(InterFoamLogAnalyzer())

analyze.run()
