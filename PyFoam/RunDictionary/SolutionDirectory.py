#  ICE Revision: $Id: SolutionDirectory.py 9241 2008-08-18 10:44:52Z bgschaid $ 
"""Working with a solution directory"""

from PyFoam.Basics.Utilities import Utilities
from PyFoam.Basics.BasicFile import BasicFile
from TimeDirectory import TimeDirectory

from os import listdir,path,mkdir,symlink,stat
from stat import ST_CTIME
import tarfile,fnmatch
import re

class SolutionDirectory(Utilities):
    """Represents a solution directory

    In the solution directory subdirectories whose names are numbers
    are assumed to be solutions for a specific time-step

    A sub-directory (called the Archive) is created to which solution
    data is copied"""
    
    def __init__(self,name,archive="ArchiveDir",paraviewLink=True,region=None):
        """@param name: Name of the solution directory
        @param archive: name of the directory where the lastToArchive-method
        should copy files, if None no archive is created
        @param paraviewLink: Create a symbolic link controlDict.foam for paraview
        @param region: Mesh region for multi-region cases"""

        self.name=name
        self.archive=None
        if archive!=None:
            self.archive=path.join(name,archive)
            if not path.exists(self.archive):
                mkdir(self.archive)

        self.region=region
        self.backups=[]

        self.lastReread=0L
        self.reread()

        self.essential=[self.systemDir(),self.constantDir(),self.initialDir()]

        if paraviewLink and not path.exists(self.controlDict()+".foam"):
            symlink(path.basename(self.controlDict()),self.controlDict()+".foam")

    def __len__(self):
        self.reread()
        return len(self.times)

    def __contains__(self,item):
        self.reread()
        
        if self.timeName(item)!=None:
            return True
        else:
            return False

    def __getitem__(self,key):
        self.reread()

        ind=self.timeName(key)
        if ind==None:
            raise KeyError(key)
        else:
            return TimeDirectory(self.name,ind,region=self.region)

    def __setitem__(self,key,value):
        self.reread()
        if type(key)!=str:
            raise TypeError(type(key),"of",key,"is not 'str'")

        if type(value)!=TimeDirectory:
            raise TypeError(type(value),"is not TimeDirectory")

        dest=TimeDirectory(self.name,key,create=True,region=self.region)
        dest.copy(value)

        self.reread(force=True)

    def __delitem__(self,key):
        self.reread()
        nm=self.timeName(key)
        if nm==None:
            raise KeyError(key)

        self.execute("rm -rf "+path.join(self.name,nm))
        
        self.reread(force=True)
        
    def __iter__(self):
        self.reread()
        for key in self.times:
            yield TimeDirectory(self.name,key,region=self.region)
            
    def timeName(self,item):
        """Finds the name of a directory that corresponds with the given parameter
        @param item: the time that should be found"""

        if type(item)==int:
            return self.times[item]
        else:
            ind=self.timeIndex(item)
            if ind==None:
                return None
            else:
                return self.times[ind]

    def timeIndex(self,item,minTime=False):
        """Finds the index of a directory that corresponds with the given parameter
        @param item: the time that should be found
        @param minTime: search for the time with the minimal difference.
        Otherwise an exact match will be searched"""
        self.reread()

        time=float(item)
        result=None

        if minTime:
            result=0
            for i in range(1,len(self.times)):
                if abs(float(self.times[result])-time)>abs(float(self.times[i])-time):
                    result=i
        else:
            for i in range(len(self.times)):
                t=self.times[i]
                if abs(float(t)-time)<1e-6:
                    if result==None:
                        result=i
                    elif abs(float(t)-time)<abs(float(self.times[result])-time):
                        result=i
                    
        return result
        
    def isValid(self):
        """Checks whether this is a valid case directory by looking for
        the system- and constant-directories and the controlDict-file"""
        if not path.exists(self.systemDir()):
            return False
        elif not path.isdir(self.systemDir()):
            return False
        elif not path.exists(self.constantDir()):
            return False
        elif not path.isdir(self.constantDir()):
            return False
        elif not path.exists(self.controlDict()):
            return False
        else:
            return True
        
    def addToClone(self,name):
        """add directory to the list that is needed to clone this case
        @param name: name of the subdirectory (the case directory is prepended)"""
        self.essential.append(path.join(self.name,name))

    def cloneCase(self,name,svnRemove=True):
        """create a clone of this case directory. Remove the target directory, if it already exists

        @param name: Name of the new case directory
        @param svnRemove: Look for .svn-directories and remove them
        @rtype: L{SolutionDirectory} or correct subclass
        @return: The target directory"""

        if path.exists(name):
            self.execute("rm -r "+name)
        mkdir(name)
        for d in self.essential:
            self.execute("cp -r "+d+" "+name)

        if svnRemove:
            self.execute("find "+name+" -name .svn -exec rm -rf {} \\; -prune")

        return self.__class__(name,archive=self.archive)

    def packCase(self,tarname,last=False,exclude=[],additional=[]):
        """Packs all the important files into a compressed tarfile.
        Uses the essential-list and excludes the .svn-directories.
        Also excludes files ending with ~
        @param tarname: the name of the tar-file
        @param last: add the last directory to the list of directories to be added
        @param exclude: List with additional glob filename-patterns to be excluded
        @param additional: List with additional glob filename-patterns
        that are to be added"""

        ex=["*~",".svn"]+exclude
        members=self.essential[:]
        if last:
            if self.getLast()!=self.first:
                members.append(self.latestDir())
        for p in additional:
            for f in listdir(self.name):
                if (f not in members) and fnmatch.fnmatch(f,p):
                    members.append(path.join(self.name,f))

        tar=tarfile.open(tarname,"w:gz")

        for m in members:
            self.addToTar(tar,m,exclude=ex)
            
        tar.close()

    def addToTar(self,tar,name,exclude=[]):
        """The workhorse for the packCase-method"""

        for e in exclude:
            if fnmatch.fnmatch(path.basename(name),e):
                return
            
        if path.isdir(name):
            for m in listdir(name):
                self.addToTar(tar,path.join(name,m),exclude=exclude)
        else:
            tar.add(name)
            
    def reread(self,force=False):
        """Rescan the directory for the time directories"""

        if not force and stat(self.name)[ST_CTIME]<=self.lastReread:
            return
        
        self.times=[]
        self.first=None
        self.last=None
        self.procDirs=0
        
        for f in listdir(self.name):
            try:
                val=float(f)
                self.times.append(f)
                if self.first==None:
                    self.first=f
                else:
                    if float(f)<float(self.first):
                        self.first=f
                if self.last==None:
                    self.last=f
                else:
                    if float(f)>float(self.last):
                        self.last=f
                        
            except ValueError:
                if re.compile("processor[0-9]+").match(f):
                    self.procDirs+=1

        self.lastReread=stat(self.name)[ST_CTIME]
        
        self.times.sort(self.sorttimes)

    def processorDirs(self):
        """List with the processor directories"""
        dirs=[]
        for f in listdir(self.name):
            if re.compile("processor[0-9]+").match(f):
                dirs.append(f)
                
        return dirs
            
    def nrProcs(self):
        """The number of directories with processor-data"""
        self.reread()
        return self.procDirs
    
    def sorttimes(self,x,y):
        """Sort function for the solution files"""
        if(float(x)==float(y)):
            return 0
        elif float(x)<float(y):
            return -1
        else:
            return 1

    def getTimes(self):
        """ @return: List of all the available times"""
        self.reread()
        return self.times
        
    def addBackup(self,pth):
        """add file to list of files that are to be copied to the
        archive"""
        self.backups.append(path.join(self.name,pth))

    def getLast(self):
        """@return: the last time for which a solution exists
        @rtype: str"""
        self.reread()
        return self.last
    
    def lastToArchive(self,name):
        """copy the last solution (plus the backup-files to the
        archive)

        @param name: name of the sub-directory in the archive"""
        if self.archive==None:
            print "Warning: nor Archive-directory"
            return
        
        self.reread()
        fname=path.join(self.archive,name)
        if path.exists(fname):
            self.execute("rm -r "+fname)
        mkdir(fname)
        self.execute("cp -r "+path.join(self.name,self.last)+" "+fname)
        for f in self.backups:
            self.execute("cp -r "+f+" "+fname)
            
    def clearResults(self,after=None,removeProcs=False,keepLast=False,vtk=True):
        """remove all time-directories after a certain time. If not time ist
        set the initial time is used
        @param after: time after which directories ar to be removed
        @param removeProcs: if True the processorX-directories are removed.
        Otherwise the timesteps after last are removed from the
        processor-directories
        @param keepLast: Keep the data from the last timestep
        @param vtk: Remove the VTK-directory if it exists"""

        self.reread()

        last=self.getLast()
        
        if after==None:
            time=float(self.first)
        else:
            time=float(after)
            
        for f in self.times:
            if float(f)>time and not (keepLast and f==last):
                self.execute("rm -r "+path.join(self.name,f))

        if path.exists(path.join(self.name,"VTK")) and vtk:
            self.execute("rm -r "+path.join(self.name,"VTK"))
            
        if self.nrProcs():
            for f in listdir(self.name):
                if re.compile("processor[0-9]+").match(f):
                    if removeProcs:
                        self.execute("rm -r "+path.join(self.name,f))
                    else:
                        pDir=path.join(self.name,f)
                        for t in listdir(pDir):
                            try:
                                val=float(t)
                                if val>time:
                                    self.execute("rm -r "+path.join(pDir,t))
                            except ValueError:
                                pass
                            
    def clearPattern(self,glob):
        """Clear all files that fit a certain shell (glob) pattern
        @param glob: the pattern which the files are going to fit"""

        self.execute("rm -rf "+path.join(self.name,glob))
        
    def clearOther(self,pyfoam=True):
        """Remove additional directories
        @param pyfoam: rremove all directories typically created by PyFoam"""

        if pyfoam:
            self.clearPattern("PyFoam.?*")
            self.clearPattern("*?.analyzed")
            
    def clear(self,after=None,processor=True,pyfoam=True,keepLast=False):
        """One-stop-shop to remove data
        @param after: time after which directories ar to be removed
        @param processor: remove the processorXX directories
        @param pyfoam: rremove all directories typically created by PyFoam
        @param keepLast: Keep the last time-step"""
        self.clearResults(after=after,removeProcs=processor,keepLast=keepLast)
        self.clearOther(pyfoam=pyfoam)
        
    def initialDir(self):
        """@return: the name of the first time-directory (==initial
        conditions
        @rtype: str"""
        self.reread()

        if self.first:
            return path.join(self.name,self.first)
        else:
            return None
        
    def latestDir(self):
        """@param region: Specify the region for cases with more than 1 mesh
        @return: the name of the first last-directory (==simulation
        results)
        @rtype: str"""
        self.reread()

        last=self.getLast()
        if last:
            return path.join(self.name,last)
        else:
            return None
        
    def constantDir(self,region=None,processor=None):
        """@param region: Specify the region for cases with more than 1 mesh
        @param processor: name of the processor directory
        @return: the name of the C{constant}-directory
        @rtype: str"""
        pre=self.name
        if processor!=None:
            pre=path.join(pre,processor)
            
        if region==None and self.region!=None:
            region=self.region
        if region:
            return path.join(pre,"constant",region)
        else:
            return path.join(pre,"constant")

    def systemDir(self,region=None):
        """@param region: Specify the region for cases with more than 1 mesh
        @return: the name of the C{system}-directory
        @rtype: str"""
        if region==None and self.region!=None:
            region=self.region
        if region:
            return path.join(self.name,"system",region)
        else:
            return path.join(self.name,"system")

    def controlDict(self):
        """@param region: Specify the region for cases with more than 1 mesh
        @return: the name of the C{controlDict}
        @rtype: str"""
        return path.join(self.systemDir(),"controlDict")

    def polyMeshDir(self,region=None,time="constant",processor=None):
        """@param region: Specify the region for cases with more than 1 mesh
        @return: the name of the C{polyMesh}
        @param time: Time for which the  mesh should be looked at
        @param processor: Name of the processor directory for decomposed cases
        @rtype: str"""
        if region==None and self.region!=None:
            region=self.region
        return path.join(self.constantDir(region=region,processor=processor),"polyMesh")

    def boundaryDict(self,region=None,time="constant",processor=None):
        """@param region: Specify the region for cases with more than 1 mesh
        @return: name of the C{boundary}-file
        @rtype: str"""
        if region==None and self.region!=None:
            region=self.region
        return path.join(self.polyMeshDir(region=region,time=time,processor=processor),"boundary")
    
    def blockMesh(self,region=None):
        """@param region: Specify the region for cases with more than 1 mesh
        @return: the name of the C{blockMeshDict} if it exists. Returns
        an empty string if it doesn't
        @rtype: str"""
        if region==None and self.region!=None:
            region=self.region
        p=path.join(self.polyMeshDir(region=region),"blockMeshDict")
        if path.exists(p):
            return p
        else:
            return ""
        
    def makeFile(self,name):
        """create a file in the solution directory and return a
        corresponding BasicFile-object

        @param name: Name of the file
        @rtype: L{BasicFile}"""
        return BasicFile(path.join(self.name,name))

    def getRegions(self):
        """Gets a list of all the available mesh regions by checking all
        directories in constant and using all those that have a polyMesh-subdirectory"""
        lst=[]
        for d in self.listDirectory(self.constantDir()):
            if path.isdir(path.join(self.constantDir(),d)):
                if path.exists(self.polyMeshDir(region=d)):
                    lst.append(d)
        lst.sort()
        return lst
    
class ChemkinSolutionDirectory(SolutionDirectory):
    """Solution directory with a directory for the Chemkin-files"""

    chemkinName = "chemkin"
    
    def __init__(self,name,archive="ArchiveDir"):
        SolutionDirectory.__init__(self,name,archive=archive)

        self.addToClone(self.chemkinName)

    def chemkinDir(self):
        """@rtype: str
        @return: The directory with the Chemkin-Files"""

        return path.join(self.name,self.chemkinName)
    
