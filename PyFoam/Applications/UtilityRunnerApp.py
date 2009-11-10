#  ICE Revision: $Id: UtilityRunnerApp.py 10473 2009-05-25 08:00:21Z bgschaid $ 
"""
Application class that implements pyFoamUtilityRunner
"""

from PyFoamApplication import PyFoamApplication

from PyFoam.Execution.UtilityRunner import UtilityRunner

import sys
from os import path

class UtilityRunnerApp(PyFoamApplication):
    def __init__(self,args=None):
        description="""
        Runs a OpenFoam Utility and analyzes the output.  Needs a regular
        expression to look for.  The next 3 arguments are the usual OpenFoam
        argumens (<solver> <directory> <case>) and passes them on (plus
        additional arguments).  Output is sent to stdout and a logfile inside
        the case directory (PyFoamUtility.logfile).  The Directory
        PyFoamUtility.analyzed contains a file test with the information of
        the regexp (the pattern groups).
        """

        PyFoamApplication.__init__(self,
                                   exactNr=False,
                                   args=args,
                                   description=description)

    def addOptions(self):
        self.parser.add_option("-r",
                               "--regexp",
                               type="string",
                               dest="regexp",
                               help="The regular expression to look for")
        
        self.parser.add_option("-n",
                               "--name",
                               type="string",
                               dest="name",
                               default="test",
                               help="The name for the resulting file")
        
        self.parser.add_option("--echo",
                               action="store_true",
                               dest="echo",
                               default=False,
                               help="Echo the result file after the run")
        
        self.parser.add_option("--silent",
                               action="store_true",
                               dest="silent",
                               default=False,
                               help="Don't print the output of the utility to the console")
        
    def run(self):
        if self.opts.regexp==None:
            self.parser.error("Regular expression needed")
    
        cName=self.parser.casePath()

        run=UtilityRunner(argv=self.parser.getArgs(),
                          silent=self.opts.silent,
                          server=True)

        run.add(self.opts.name,self.opts.regexp)

        self.addToCaseLog(cName,"Starting")
        
        run.start()

        self.addToCaseLog(cName,"Ending")

        fn=path.join(run.getDirname(),self.opts.name)

        data=run.analyzer.getData(self.opts.name)

        if data==None:
            print sys.argv[0]+": No data found"
        else:
            if self.opts.echo:
                fh=open(fn)
                print fh.read()
                fh.close()
            else:
                print sys.argv[0]+": Output written to file "+fn
