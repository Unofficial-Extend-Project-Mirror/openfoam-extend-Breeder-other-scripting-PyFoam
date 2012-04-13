#! /usr/bin/env python

from runPitzDailyBasic import BasicPitzDailyRun

class ParallelPitzDailyRun(BasicPitzDailyRun):
    def init(self):
        self.setParameters(parallel=True,
                           nrCpus=3,
                           velocityAbsoluteTolerance=3e-2,
                           velocityRelativeTolerance=1e-2)

if __name__=='__main__':
    ParallelPitzDailyRun().run()
