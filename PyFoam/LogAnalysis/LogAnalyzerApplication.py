#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/LogAnalyzerApplication.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Wraps an Analyzer"""

import sys

from os import path,mkdir

class LogAnalyzerApplication(object):
    """
    Wrapper for the Analyzer Classes
     - Builds a directory for their output
       - name is derived from the logfile-name
       - anounces the directory to them
     - starts the analyzer
    """
    
    def __init__(self,analyze):
        """ @param analyze: The analyzer"""
        self.analyzer=analyze

    def run(self,pfad=None):
        """ runs the analyzer
        @param pfad: path to the logfile, if no path is given it is
        taken from the command line"""
        if pfad==None:
            fn=sys.argv[1]
        else:
            fn=pfad
            
        pfad=path.abspath(fn)
        dn=path.dirname(pfad)
        oDir=path.join(dn,path.basename(pfad)+"_analyzed")
        if not path.exists(oDir):
            mkdir(oDir)

        self.analyzer.setDirectory(oDir)
        
        fh=open(fn,'r')
        self.analyzer.analyze(fh)
        
