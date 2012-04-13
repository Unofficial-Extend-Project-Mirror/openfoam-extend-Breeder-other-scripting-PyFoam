#! /usr/bin/env python

from runPitzDailyBasic import BasicPitzDailyRun

class ExptInletPitzDailyRun(BasicPitzDailyRun):
    def init(self):
        self.setParameters(originalCase="$FOAM_TUTORIALS/incompressible/simpleFoam/pitzDailyExptInlet",
                           velocityAbsoluteTolerance=3.5,
                           velocityRelativeTolerance=0.37)

if __name__=='__main__':
    ExptInletPitzDailyRun().run()
