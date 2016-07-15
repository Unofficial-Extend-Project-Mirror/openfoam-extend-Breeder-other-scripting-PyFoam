#  ICE Revision: $Id$
"""Look for the name of the executable"""

from .LogLineAnalyzer import LogLineAnalyzer

from PyFoam.ThirdParty.six import print_

class ExecNameLineAnalyzer(LogLineAnalyzer):
    """Looks for the name of the executable"""

    def __init__(self):
        LogLineAnalyzer.__init__(self)

        self.execName=None

    def doAnalysis(self,line):
        tmp=line.split()
        if len(tmp)>=3:
            if tmp[0]=="Exec" and tmp[1]==":":
                self.execName=tmp[2]
                self.notify(self.execName)

# Should work with Python3 and Python2
