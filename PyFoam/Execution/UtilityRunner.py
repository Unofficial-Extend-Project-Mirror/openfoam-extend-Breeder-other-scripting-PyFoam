#  ICE Revision: $Id: UtilityRunner.py 9667 2008-11-12 18:20:16Z bgschaid $ 
"""Run a non-solver utility"""

from AnalyzedRunner import AnalyzedRunner
from PyFoam.LogAnalysis.UtilityAnalyzer import UtilityAnalyzer

class UtilityRunner(AnalyzedRunner):
    """To this runner regular expressions can be added. Each line is
    checked against each regular expression and saved with the
    corresponding time.

    Each RegEx has a name

    For each pattern group in the RegEx one data value is stored"""
    
    def __init__(self,
                 argv=None,
                 silent=False,
                 logname="PyFoamUtility",
                 server=False,
                 restart=False,
                 noLog=False):
        """see BasicRunner"""
        AnalyzedRunner.__init__(self,UtilityAnalyzer(),
                                argv=argv,
                                silent=silent,
                                logname=logname,
                                server=server,
                                restart=restart,
                                noLog=noLog)
        
    def add(self,name,exp,idNr=None):
        """adds a regular expression

        name - name under whcih the RegExp is known
        exp - the regular expression
        idNr - number of the pattern group that is used to make a data
        set unique"""
        self.analyzer.addExpression(name,exp,idNr)
        self.reset()

    def get(self,name,time=None,ID=None):
        """get a data set

        name - name of the RegExp
        time - at which time (if unset the last time is used)
        ID - the unique ID determined by idNr"""
        return self.analyzer.getData(name,time=time,ID=ID)

    def getIDs(self,name):
        """get a list of all the IDs"""
        return self.analyzer.getIDs(name)

    def getTimes(self,name,ID=None):
        """get a list of all the times that are available for ID"""
        return self.analyzer.getTimes(name,ID=ID)
    
