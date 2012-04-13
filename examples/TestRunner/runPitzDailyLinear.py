#! /usr/bin/env python

from os import path

from runPitzDailyBasic import BasicPitzDailyRun
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

class LinearPitzDailyRun(BasicPitzDailyRun):
    def init(self):
        self.setParameters(
            velocityAbsoluteTolerance=0.5,
            velocityRelativeTolerance=0.17
            )
        
    def casePrepare(self):
        BasicPitzDailyRun.casePrepare(self)

        schemes=ParsedParameterFile(path.join(self.solution().systemDir(),"fvSchemes"))
        schemes["divSchemes"]["div(phi,U)"]="Gauss linear";
        schemes.writeFile()

if __name__=='__main__':
    LinearPitzDailyRun().run()
