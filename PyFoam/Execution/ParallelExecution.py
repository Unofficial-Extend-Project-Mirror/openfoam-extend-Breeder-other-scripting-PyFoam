#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/ParallelExecution.py 2789 2008-02-15T15:35:58.159689Z bgschaid  $ 
"""Things that are needed for convenient parallel Execution"""

from PyFoam.Basics.Utilities import Utilities
from PyFoam.FoamInformation import foamMPI
from PyFoam.Error import error,warning,debug
from PyFoam import configuration as config

from os import path
from string import strip

class LAMMachine(Utilities):
    """Wrapper class for starting an stopping a LAM-Machine"""
    def __init__(self,machines=None,nr=None):
        """@param machines: Name of the file with the machine information
        @param nr: Number of processes"""

        Utilities.__init__(self)

        self.stop()

        if machines=="":
            machines=None
            
        if machines==None and foamMPI()=="LAM":
            error("Machinefile must be specified for LAM")

        if machines==None and nr==None:
            error("Either machinefile or Nr of CPUs must be specified for MPI type",foamMPI())
            
        self.mFile=machines
        self.procNr=nr
        
        self.boot()
        if not self.machineOK():
            error("Error: LAM was not started")
            
    def machineOK(self):
        """Check whether the LAM machine was properly booted"""
        if self.running:
            if(foamMPI()=="LAM"):
                if self.cpuNr()<=0:
                    self.running=False

        return self.running

    def stop(self):
        """Stops a LAM-machine (if one is running)"""
        self.running=False
        if(foamMPI()=="LAM"):
            self.execute("lamhalt -v")
        
    def boot(self):
        """Boots a LAM-machine using the machine-file"""
        if(foamMPI()=="LAM"):
            warning("LAM is untested. Any Feedback most welcome")
            self.execute("lamboot -s -v "+self.mFile)
            self.running=True
        elif(foamMPI()=="OPENMPI"):
            self.running=True
        else:
            error(" Unknown or missing MPI-Implementation: "+foamMPI())
            
    def cpuNr(self):
        if(foamMPI()=="LAM"):
            if self.running:
                lines=self.execute("lamnodes")
                nr=0
                for l in lines:
                    tmp=l.split(':')
                    if len(tmp)>1:
                        nr+=int(tmp[1])
                return nr
            else:
                return -1
        elif(foamMPI()=="OPENMPI"):
            if self.mFile:
                f=open(self.mFile)
                l=map(strip,f.readlines())
                f.close()
                nr=0
                for m in l:
                    tmp=m.split()
                    if len(tmp)==1:
                        nr+=1
                    elif len(tmp)==0:
                        pass
                    else:
                        error("Machinefile not valid (I think): more than one element in one line:"+str(tmp))

                if self.procNr==None:
                    return nr
                else:
                    return min(nr,self.procNr)
                
            elif self.procNr:
                return self.procNr
            else:
                error("Can't determine Nr of CPUs without machinefile")
                
    def buildMPIrun(self,argv):
        """Builds a list with a working mpirun command (for that MPI-Implementation)
        @param argv: the original arguments that are to be wrapped
        @return: list with the correct mpirun-command"""

        nr=str(self.cpuNr())
        mpirun=[config().get("MPI","run_"+foamMPI(),default="mpirun")]

        mpirun+=eval(config().get("MPI","options_"+foamMPI()+"_pre",default="[]"))
        
        if(foamMPI()=="LAM"):
            mpirun+=["-np",nr]
        elif(foamMPI()=="OPENMPI"):
            nr=[]
            if self.procNr!=None:
                nr=["-np",str(self.procNr)]
            machine=[]
            if self.mFile!=None:
                machine=["-machinefile",self.mFile]
            mpirun+=nr+machine
        else:
            error(" Unknown or missing MPI-Implementation for mpirun: "+foamMPI())

        mpirun+=eval(config().get("MPI","options_"+foamMPI()+"_post",default="[]"))

        mpirun+=argv[0:3]+["-parallel"]+argv[3:]

        if config().getdebug("ParallelExecution"):
            debug("Arguments:",mpirun)

        return mpirun
    
    def writeMetis(self,sDir):
        """Write the parameter-File for a metis decomposition
        @param sDir: Solution directory
        @type sDir: PyFoam.RunDictionary.SolutionDirectory"""

        params="method metis;\n"

        self.writeDecomposition(sDir,params)

    def writeSimple(self,sDir,direction):
        """Write the parameter-File for a metis decomposition
        @param sDir: Solution directory
        @type sDir: PyFoam.RunDictionary.SolutionDirectory
        @param direction: direction in which to decompose (0=x, 1=y, 2=z)"""

        params ="method simple;\n"
        params+="\nsimpleCoeffs\n{\n\t n \t ("
        if direction==0:
            params+=str(self.cpuNr())+" "
        else:
            params+="1 "
        if direction==1:
            params+=str(self.cpuNr())+" "
        else:
            params+="1 "
        if direction==2:
            params+=str(self.cpuNr())
        else:
            params+="1"
        params+=");\n\t delta \t 0.001;\n}\n"
        
        self.writeDecomposition(sDir,params)

    def writeDecomposition(self,sDir,par):
        """Write parameter file for a decomposition
        @param par:Parameters specific for that kind of decomposition
        @type par:str
        @param sDir: Solution directory
        @type sDir: PyFoam.RunDictionary.SolutionDirectory"""

        f=open(path.join(sDir.systemDir(),"decomposeParDict"),"w")
        self.writeDictionaryHeader(f)
        f.write("// * * * * * * * * * //\n\n")
        f.write("numberOfSubdomains "+str(self.cpuNr())+";\n\n")
        f.write(par)
        f.write("\n\n// * * * * * * * * * //")
        f.close()
