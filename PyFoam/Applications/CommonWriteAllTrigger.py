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
        self.ensureGeneralOptions()
        self.generalOpts.add_option("--write-all-timesteps",
                                    action="store_true",
                                    dest="writeAll",
                                    default=False,
                                    help="Write all the timesteps to disk")
        self.generalOpts.add_option("--purge-write",
                                    action="store",
                                    type="int",
                                    dest="purgeWrite",
                                    default=None,
                                    help="Together with write-all-timesteps determines the number of time-steps that is kept on disc. All will be kept if unset")

    def addWriteAllTrigger(self,run,sol):
        if self.opts.writeAll:
            warning("Adding Trigger and resetting to safer start-settings")
            trig=WriteAllTrigger(sol,self.opts.purgeWrite)
            run.addEndTrigger(trig.resetIt)
        elif self.opts.purgeWrite!=None:
            warning("purgeWrite of",self.opts.purgeWrite,"ignored because write-all-timesteps unused")
        
class WriteAllTrigger:
    def __init__(self,sol,purge):
        self.control=ParsedParameterFile(path.join(sol.systemDir(),"controlDict"),backup=True)

        self.fresh=True
        
        try:
            self.control["writeControl"]="timeStep"
            self.control["writeInterval"]="1"
            if purge!=None:
                self.control["purgeWrite"]=purge
                
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
