#  ICE Revision: $Id: EchoLineAnalyzer.py 7581 2007-06-27 15:29:14Z bgschaid $ 
"""Echos a line"""

from LogLineAnalyzer import LogLineAnalyzer

class EchoLineAnalyzer(LogLineAnalyzer):
    """Test implementation. Simply echos every line it gets"""
    
    def __init__(self):
        LogLineAnalyzer.__init__(self)

    def doAnalysis(self,line):
        print "<"+self.parent.getTime()+">"+line+"<"
        
