#  ICE Revision: $Id: EchoLogAnalyzer.py 7581 2007-06-27 15:29:14Z bgschaid $ 
"""Echos a log"""

from FoamLogAnalyzer import FoamLogAnalyzer

from EchoLineAnalyzer import EchoLineAnalyzer

class EchoLogAnalyzer(FoamLogAnalyzer):
    """
    Trivial analyzer. It echos the Log-File
    """
    def __init__(self):
        FoamLogAnalyzer.__init__(self,progress=False)

        self.addAnalyzer("Echo",EchoLineAnalyzer())
        
