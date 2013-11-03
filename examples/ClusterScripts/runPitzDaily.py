#!/usr/bin/python
#
#$ -cwd
#$ -j y
#$ -S /opt/rocks/bin/python
#$ -m be
#

import sys,os
from os import path

os.environ["WM_64"]="1"

from PyFoam.Infrastructure.ClusterJob import SolverJob
from PyFoam.Error import error
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

velIn=sys.argv[1]

name="pitzDaily"

class Pitz(SolverJob):
    def __init__(self):
        SolverJob.__init__(self,
                           name+".run."+velIn,
                           "simpleFoam",
                           template=name,
                           steady=True,
                           foamVersion="1.5")

    def setup(self,parameters):
        self.foamRun("blockMesh")
        vel=ParsedParameterFile(path.join(self.casedir(),"0","U"))
        vel["boundaryField"]["inlet"]["value"] = "uniform (%s 0 0)" % velIn
        vel.writeFile()
        
Pitz().doIt()

