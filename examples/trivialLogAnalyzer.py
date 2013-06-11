""" Just a demonstration of a VERY simple log analyzer"""

from PyFoam.LogAnalysis.EchoLogAnalyzer import EchoLogAnalyzer
from PyFoam.LogAnalysis.LogAnalyzerApplication import LogAnalyzerApplication

analyze=LogAnalyzerApplication(EchoLogAnalyzer())

analyze.run()
