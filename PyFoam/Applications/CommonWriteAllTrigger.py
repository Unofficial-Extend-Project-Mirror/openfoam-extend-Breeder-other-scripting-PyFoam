"""Implements a trigger that manipulates the controlDict in
such a way that every time-step is written to disk"""

import re
from os import path
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Error import warning

class CommonWriteAllTrigger(object):
    """ The class that does the actual triggering
    """

    def addOptions(self):
        self.parser.add_option("--write-all-timesteps",
                               action="store_true",
                               dest="writeAll",
                               default=False,
                               help="Write all the timesteps to disk")

    def addWriteAllTrigger(self,run,sol):
        if self.opts.writeAll:
            warning("Adding Trigger and resetting to safer start-settings")
            trig=WriteAllTrigger(sol)
            run.addEndTrigger(trig.resetIt)

        
class WriteAllTrigger:
    def __init__(self,sol):
        self.control=ParsedParameterFile(path.join(sol.systemDir(),"controlDict"),backup=True)

        self.fresh=True
        
        try:
            self.control["writeControl"]="timeStep"
            self.control["writeInterval"]="1"
            
            self.control.writeFile()
        except Exception,e:
            warning("Restoring defaults")
            self.control.restore()
            raise e
        
    def resetIt(self):
        if self.fresh:
            warning("Trigger called: Resetting the controlDict")
            self.control.restore()
            self.fresh=False
