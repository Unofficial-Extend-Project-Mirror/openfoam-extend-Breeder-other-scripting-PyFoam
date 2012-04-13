#! /usr/bin/env python

from PyFoam.Infrastructure.CTestRun import CTestRun

class PlainIcoFoamCavity(CTestRun):
    def init(self):
        self.setParameters(solver="icoFoam",
                           originalCase="$FOAM_TUTORIALS/incompressible/icoFoam/cavity",
                           sizeClass="tiny")

if __name__=='__main__':
    PlainIcoFoamCavity().run()
