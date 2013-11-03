#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/EchoLogAnalyzer.py 8415 2013-07-26T11:32:37.193675Z bgschaid  $
"""Echos a log"""

from .FoamLogAnalyzer import FoamLogAnalyzer

from .EchoLineAnalyzer import EchoLineAnalyzer

class EchoLogAnalyzer(FoamLogAnalyzer):
    """
    Trivial analyzer. It echos the Log-File
    """
    def __init__(self):
        FoamLogAnalyzer.__init__(self,progress=False)

        self.addAnalyzer("Echo",EchoLineAnalyzer())

# Should work with Python3 and Python2
