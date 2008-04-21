#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/EchoLogAnalyzer.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
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
        
