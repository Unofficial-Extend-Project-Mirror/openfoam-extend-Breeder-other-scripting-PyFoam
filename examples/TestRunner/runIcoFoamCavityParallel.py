#! /usr/bin/env python

from runIcoFoamCavity import PlainIcoFoamCavity
from PyFoam.Applications.Decomposer import Decomposer

class ParallelIcoFoamCavity(PlainIcoFoamCavity):
    def init(self):
        self.setParameters(parallel=True,
                           autoDecompose=False,
                           nrCpus=2)
    def decompose(self):
        Decomposer(args=[self.caseDir,
                         str(self["nrCpus"]),
                         "--method=simple",
                         "--n=(2,1,1)",
                         "--delta=1e-5"])

if __name__=='__main__':
    ParallelIcoFoamCavity().run()
