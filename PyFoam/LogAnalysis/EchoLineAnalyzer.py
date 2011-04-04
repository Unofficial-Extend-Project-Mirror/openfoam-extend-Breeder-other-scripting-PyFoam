#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/EchoLineAnalyzer.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Echos a line"""

from LogLineAnalyzer import LogLineAnalyzer

class EchoLineAnalyzer(LogLineAnalyzer):
    """Test implementation. Simply echos every line it gets"""
    
    def __init__(self):
        LogLineAnalyzer.__init__(self)

    def doAnalysis(self,line):
        print "<"+self.parent.getTime()+">"+line+"<"
        
