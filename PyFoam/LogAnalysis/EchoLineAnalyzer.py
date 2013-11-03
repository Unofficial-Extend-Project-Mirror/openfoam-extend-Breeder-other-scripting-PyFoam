#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/EchoLineAnalyzer.py 8415 2013-07-26T11:32:37.193675Z bgschaid  $
"""Echos a line"""

from .LogLineAnalyzer import LogLineAnalyzer

from PyFoam.ThirdParty.six import print_

class EchoLineAnalyzer(LogLineAnalyzer):
    """Test implementation. Simply echos every line it gets"""

    def __init__(self):
        LogLineAnalyzer.__init__(self)

    def doAnalysis(self,line):
        print_("<"+self.parent.getTime()+">"+line+"<")

# Should work with Python3 and Python2
