#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/MeshUtilityRunner.py 2866 2008-03-07T13:42:45.412013Z bgschaid  $ 
"""
Application class that implements pyFoamMeshUtilityRunner
"""

from os import listdir,path,system

from PyFoamApplication import PyFoamApplication

from PyFoam.FoamInformation import changeFoamVersion

from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

class MeshUtilityRunner(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Runs an OpenFoam utility that manipulates meshes.  Needs the usual 3
arguments (<solver> <directory> <case>) and passes them on (plus additional arguments).

Output is sent to stdout and a logfile inside the case directory
(PyFoamMeshUtility.logfile)

Before running it clears all timesteps but the first.

After the utility ran it moves all the data from the polyMesh-directory
of the first time-step to the constant/polyMesh-directory

ATTENTION: This utility erases quite a lot of data without asking and
should therefor be used with care
        """
        
        PyFoamApplication.__init__(self,
                                   exactNr=False,
                                   args=args,
                                   description=description)
        
    def addOptions(self):
        self.parser.add_option("--foamVersion",dest="foamVersion",default=None,help="Change the OpenFOAM-version that is to be used")
        
    def run(self):
        if self.opts.foamVersion!=None:
            changeFoamVersion(self.opts.foamVersion)
            
        cName=self.parser.getArgs()[2]
        sol=SolutionDirectory(cName,archive=None)

        print "Clearing out old timesteps ...."
            
        sol.clearResults()

            
        run=BasicRunner(argv=self.parser.getArgs(),server=False,logname="PyFoamMeshUtility")

        run.start()

        if sol.latestDir()!=sol.initialDir():
            for f in listdir(path.join(sol.latestDir(),"polyMesh")):
                system("mv -f "+path.join(sol.latestDir(),"polyMesh",f)+" "+sol.polyMeshDir())

            print "\nClearing out new timesteps ...."
            
            sol.clearResults()
        else:
            print "\n\n  No new timestep. Utility propably failed"
