#  ICE Revision: $Id: SolutionDirectory.py 12792 2013-02-06 13:22:52Z bgschaid $
"""Working with a solution directory"""

from PyFoam.Basics.Utilities import Utilities
from PyFoam.Basics.BasicFile import BasicFile
from PyFoam.Error import warning
from PyFoam import configuration as conf

from PyFoam.RunDictionary.TimeDirectory import TimeDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile,WriteParameterFile

from PyFoam.Basics.DataStructures import DictProxy

from PyFoam.ThirdParty.six import print_

from os import listdir,path,mkdir,stat,environ
from platform import uname
from time import asctime
from stat import ST_CTIME
import tarfile,fnmatch,glob
import re,os

try:
    from os import getlogin
except ImportError:
    try:
        import PyFoam.ThirdParty.winhacks
    except ImportError:
        print "Unable to import the getlogin function."
        import sys
        sys.exit(-1)

class SolutionDirectory(Utilities):
    """Represents a solution directory

    In the solution directory subdirectories whose names are numbers
    are assumed to be solutions for a specific time-step

    A sub-directory (called the Archive) is created to which solution
    data is copied"""

    def __init__(self,
                 name,
                 archive="ArchiveDir",
                 paraviewLink=True,
                 parallel=False,
                 addLocalConfig=False,
                 region=None):
        """@param name: Name of the solution directory
        @param archive: name of the directory where the lastToArchive-method
        should copy files, if None no archive is created
        @param paraviewLink: Create a symbolic link controlDict.foam for paraview
        @param parallel: use the first processor-subdirectory for the authorative information
        @param region: Mesh region for multi-region cases"""

        self.name=path.abspath(name)
        self.archive=None
        if archive!=None:
            self.archive=path.join(name,archive)
            if not path.exists(self.archive):
                mkdir(self.archive)

        self.region=region
        self.backups=[]

        self.parallel=parallel

        self.lastReread=0
        self.reread()

        self.dirPrefix=''
        if self.processorDirs() and parallel:
            self.dirPrefix = self.processorDirs()[0]

        self.essential=[self.systemDir(),
                        self.constantDir(),
                        self.initialDir()]
        self.addToClone("PyFoamHistory")

        self.addToClone("customRegexp")
        self.addToClone("LocalConfigPyFoam")

        emptyFoamFile=path.join(self.name,path.basename(self.name)+".foam")
        if paraviewLink and not path.exists(emptyFoamFile):
            dummy=open(emptyFoamFile,"w") # equivalent to touch

        if addLocalConfig:
            self.addLocalConfig()

    def setToParallel(self):
        """Use the parallel times instead of the serial.

        Used to reset the behaviour after it has been set by the constructor"""
        if self.parallel:
            warning(self.name,"is already in parallel mode")
        else:
            self.parallel=True
            if self.processorDirs():
                self.dirPrefix = self.processorDirs()[0]
            self.reread(force=True)

    def addLocalConfig(self):
        """Add the local configuration file of the case to the configuration"""
        fName=path.join(self.name,"LocalConfigPyFoam")
        if path.exists(fName):
            conf().addFile(fName)

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
            return TimeDirectory(self.name, self.fullPath(ind), region=self.region)

    def __setitem__(self,key,value):
        self.reread()
        if type(key)!=str:
            raise TypeError(type(key),"of",key,"is not 'str'")

        if type(value)!=TimeDirectory:
            raise TypeError(type(value),"is not TimeDirectory")

        dest=TimeDirectory(self.name, self.fullPath(key), create=True,region=self.region)
        dest.copy(value)

        self.reread(force=True)

    def __delitem__(self,key):
        self.reread()
        nm=self.timeName(key)
        if nm==None:
            raise KeyError(key)

        self.rmtree(path.join(self.name, self.fullPath(nm)),ignore_errors=True)

        self.reread(force=True)

    def __iter__(self):
        self.reread()
        for key in self.times:
            yield TimeDirectory(self.name, self.fullPath(key), region=self.region)

    def timeName(self,item,minTime=False):
        """Finds the name of a directory that corresponds with the given parameter
        @param item: the time that should be found
        @param minTime: search for the time with the minimal difference.
        Otherwise an exact match will be searched"""

        if type(item)==int:
            return self.times[item]
        else:
            ind=self.timeIndex(item,minTime)
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

    def fullPath(self,time):
        if self.dirPrefix:
            return path.join(self.dirPrefix, time)
        return time

    def isValid(self):
        """Checks whether this is a valid case directory by looking for
        the system- and constant-directories and the controlDict-file"""

        return len(self.missingFiles())==0

    def missingFiles(self):
        """Return a list of all the missing files and directories that
        are needed for a valid case"""
        missing=[]
        if not path.exists(self.systemDir()):
            missing.append(self.systemDir())
        elif not path.isdir(self.systemDir()):
            missing.append(self.systemDir())
        if not path.exists(self.constantDir()):
            missing.append(self.constantDir())
        elif not path.isdir(self.constantDir()):
            missing.append(self.constantDir())
        if not path.exists(self.controlDict()):
            missing.append(self.controlDict())

        return missing

    def addToClone(self,name):
        """add directory to the list that is needed to clone this case
        @param name: name of the subdirectory (the case directory is prepended)"""
        if path.exists(path.join(self.name,name)):
            self.essential.append(path.join(self.name,name))
        elif self.parallel:
            if path.exists(path.join(self.name,"processor0",name)):
                self.essential.append(path.join(self.name,name))

    def cloneCase(self,name,svnRemove=True,followSymlinks=False):
        """create a clone of this case directory. Remove the target directory, if it already exists

        @param name: Name of the new case directory
        @param svnRemove: Look for .svn-directories and remove them
        @param followSymlinks: Follow symbolic links instead of just copying them
        @rtype: L{SolutionDirectory} or correct subclass
        @return: The target directory"""

        additional=eval(conf().get("Cloning","addItem"))
        for a in additional:
            self.addToClone(a)

        cpOptions="-R"
        if followSymlinks:
            cpOptions+=" -L"

        if path.exists(name):
            self.rmtree(name)
        mkdir(name)
        if self.parallel:
            for i in range(self.nrProcs()):
                mkdir(path.join(name,"processor%d" % i))

        for d in self.essential:
            if d!=None:
                if self.parallel:
                    pth,fl=path.split(d)
                    if path.exists(path.join(pth,"processor0",fl)):
                        for i in range(self.nrProcs()):
                            self.copytree(path.join(pth,"processor%d" % i,fl),
                                          path.join(name,"processor%d" % i),
                                          symlinks=not followSymlinks)

                if path.exists(d):
                    self.copytree(d,name,symlinks=not followSymlinks)

        if svnRemove:
            self.execute("find "+name+" -name .svn -exec rm -rf {} \\; -prune")

        return self.__class__(name,archive=self.archive)

    def packCase(self,tarname,last=False,exclude=[],additional=[],base=None):
        """Packs all the important files into a compressed tarfile.
        Uses the essential-list and excludes the .svn-directories.
        Also excludes files ending with ~
        @param tarname: the name of the tar-file
        @param last: add the last directory to the list of directories to be added
        @param exclude: List with additional glob filename-patterns to be excluded
        @param additional: List with additional glob filename-patterns
        that are to be added
        @param base: Different name that is to be used as the baseName for the case inside the tar"""

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
            self.addToTar(tar,m,exclude=ex,base=base)

        additional=eval(conf().get("Cloning","addItem"))
        for a in additional:
            self.addToTar(tar,
                          path.join(self.name,a),
                          exclude=ex,
                          base=base)

        tar.close()

    def addToTar(self,tar,name,exclude=[],base=None):
        """The workhorse for the packCase-method"""

        if base==None:
            base=path.basename(self.name)

        for e in exclude:
            if fnmatch.fnmatch(path.basename(name),e):
                return

        if path.isdir(name):
            for m in listdir(name):
                self.addToTar(tar,path.join(name,m),exclude=exclude,base=base)
        else:
            arcname=path.join(base,name[len(self.name)+1:])
            tar.add(name,arcname=arcname)

    def getParallelTimes(self):
        """Get a list of the times in the processor0-directory"""
        result=[]

        proc0=path.join(self.name,"processor0")
        if path.exists(proc0):
            for f in listdir(proc0):
                try:
                    val=float(f)
                    result.append(f)
                except ValueError:
                    pass
        result.sort(key=float)
        return result

    def reread(self,force=False):
        """Rescan the directory for the time directories"""

        if not force and stat(self.name)[ST_CTIME]<=self.lastReread:
            return

        self.times=[]
        self.first=None
        self.last=None
        procDirs = self.processorDirs()
        self.procNr=len(procDirs)

        if procDirs and self.parallel:
            timesDir = path.join(self.name, procDirs[0])
        else:
            timesDir = self.name

        for f in listdir(timesDir):
            try:
                val=float(f)
                self.times.append(f)
            except ValueError:
                pass

        self.lastReread=stat(self.name)[ST_CTIME]

        self.times.sort(key=float)
        if self.times:
            self.first = self.times[0]
            self.last = self.times[-1]

    def processorDirs(self):
        """List with the processor directories"""
        try:
            return self.procDirs
        except:
            pass
        self.procDirs=[]
        for f in listdir(self.name):
            if re.compile("processor[0-9]+").match(f):
                self.procDirs.append(f)

        return self.procDirs

    def nrProcs(self):
        """The number of directories with processor-data"""
        self.reread()
        return self.procNr

    def getTimes(self):
        """ @return: List of all the available times"""
        self.reread()
        return self.times

    def addBackup(self,pth):
        """add file to list of files that are to be copied to the
        archive"""
        self.backups.append(path.join(self.name,pth))

    def getFirst(self):
        """@return: the first time for which a solution exists
        @rtype: str"""
        self.reread()
        return self.first

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
            print_("Warning: nor Archive-directory")
            return

        self.reread()
        fname=path.join(self.archive,name)
        if path.exists(fname):
            self.rmtree(fname)
        mkdir(fname)
        self.copytree(path.join(self.name,self.last),fname)
        for f in self.backups:
            self.copytree(f,fname)

    def clearResults(self,
                     after=None,
                     removeProcs=False,
                     keepLast=False,
                     vtk=True,
                     keepRegular=False,
                     functionObjectData=False):
        """remove all time-directories after a certain time. If not time ist
        set the initial time is used
        @param after: time after which directories ar to be removed
        @param removeProcs: if True the processorX-directories are removed.
        Otherwise the timesteps after last are removed from the
        processor-directories
        @param keepLast: Keep the data from the last timestep
        @param vtk: Remove the VTK-directory if it exists
        @param keepRegular: keep all the times (only remove processor and other stuff)
        @param functionObjectData: tries do determine which data was written by function obejects and removes it"""

        self.reread()

        last=self.getLast()

        if after==None:
            try:
                time=float(self.first)
            except TypeError:
                warning("The first timestep in",self.name," is ",self.first,"not a number. Doing nothing")
                return
        else:
            time=float(after)

        if not keepRegular:
            for f in self.times:
                if float(f)>time and not (keepLast and f==last):
                    self.rmtree(path.join(self.name,f))

        if path.exists(path.join(self.name,"VTK")) and vtk:
            self.rmtree(path.join(self.name,"VTK"))

        if self.nrProcs():
            for f in listdir(self.name):
                if re.compile("processor[0-9]+").match(f):
                    if removeProcs:
                        self.rmtree(path.join(self.name,f))
                    else:
                        pDir=path.join(self.name,f)
                        for t in listdir(pDir):
                            try:
                                val=float(t)
                                if val>time:
                                    self.rmtree(path.join(pDir,t))
                            except ValueError:
                                pass

        if functionObjectData:
            cd=ParsedParameterFile(self.controlDict())
            if "functions" in cd:
                if type(cd["functions"]) in [DictProxy,dict]:
                    for f in cd["functions"]:
                        pth=path.join(self.name,f)
                        if path.exists(pth):
                            self.rmtree(pth)
                else:
                    for f in cd["functions"][0::2]:
                        pth=path.join(self.name,f)
                        if path.exists(pth):
                            self.rmtree(pth)

        additional=eval(conf().get("Clearing","additionalpatterns"))
        for a in additional:
            self.clearPattern(a)

    def clearPattern(self,globPat):
        """Clear all files that fit a certain shell (glob) pattern
        @param glob: the pattern which the files are going to fit"""

        for f in glob.glob(path.join(self.name,globPat)):
            if path.isdir(f):
                self.rmtree(f,ignore_errors=False)
            else:
                os.unlink(f)

    def clearOther(self,
                   pyfoam=True,
                   clearHistory=False):
        """Remove additional directories
        @param pyfoam: rremove all directories typically created by PyFoam"""

        if pyfoam:
            self.clearPattern("PyFoam.?*")
            self.clearPattern("*?.analyzed")
        if clearHistory:
            self.clearPattern("PyFoamHistory")

    def clear(self,
              after=None,
              processor=True,
              pyfoam=True,
              keepLast=False,
              vtk=True,
              keepRegular=False,
              clearHistory=False,
              functionObjectData=False):
        """One-stop-shop to remove data
        @param after: time after which directories ar to be removed
        @param processor: remove the processorXX directories
        @param pyfoam: rremove all directories typically created by PyFoam
        @param keepLast: Keep the last time-step
        @param additional: list with additional patterns to clear"""
        self.clearResults(after=after,
                          removeProcs=processor,
                          keepLast=keepLast,
                          vtk=vtk,
                          keepRegular=keepRegular,
                          functionObjectData=functionObjectData)
        self.clearOther(pyfoam=pyfoam,
                        clearHistory=clearHistory)

    def initialDir(self):
        """@return: the name of the first time-directory (==initial
        conditions)
        @rtype: str"""
        self.reread()

        if self.first:
            return path.join(self.name,self.first)
        else:
            if path.exists(path.join(self.name,"0.org")):
                return path.join(self.name,"0.org")
            else:
                return None

    def latestDir(self):
        """@return: the name of the first last-directory (==simulation
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
            if type(processor)==int:
                processor="processor%d" % processor
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
        """@return: the name of the C{controlDict}
        @rtype: str"""
        return path.join(self.systemDir(),"controlDict")

    def polyMeshDir(self,region=None,time=None,processor=None):
        """@param region: Specify the region for cases with more than 1 mesh
        @return: the name of the C{polyMesh}
        @param time: Time for which the  mesh should be looked at
        @param processor: Name of the processor directory for decomposed cases
        @rtype: str"""
        if region==None and self.region!=None:
            region=self.region
        if time==None:
            return path.join(
                self.constantDir(
                    region=region,
                    processor=processor),
                "polyMesh")
        else:
            return path.join(
                TimeDirectory(self.name,
                              time,
                              region=region,
                              processor=processor).name,
                "polyMesh")

    def boundaryDict(self,region=None,time=None,processor=None):
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

    def getRegions(self,defaultRegion=False):
        """Gets a list of all the available mesh regions by checking all
        directories in constant and using all those that have a polyMesh-subdirectory
        @param defaultRegion: should the default region also be added (as None)"""
        lst=[]
        for d in self.listDirectory(self.constantDir()):
            if path.isdir(path.join(self.constantDir(),d)):
                if path.exists(self.polyMeshDir(region=d)):
                    lst.append(d)

        if defaultRegion:
            if path.exists(self.polyMeshDir()):
                lst.append(None)

        lst.sort()
        return lst

    def addToHistory(self,*text):
        """Adds a line with date and username to a file 'PyFoamHistory'
        that resides in the local directory"""
        hist=open(path.join(self.name,"PyFoamHistory"),"a")

        try:
            # this seems to fail when no stdin is available
            username=getlogin()
        except OSError:
            username=environ["USER"]

        hist.write("%s by %s in %s :" % (asctime(),username,uname()[1]))

        for t in text:
            hist.write(str(t)+" ")

        hist.write("\n")
        hist.close()

    def listFiles(self,directory=None):
        """List all the plain files (not directories) in a subdirectory
        of the case
        @param directory: the subdirectory. If unspecified the
        case-directory itself is used
        @return: List with the plain filenames"""

        result=[]
        theDir=self.name
        if directory:
            theDir=path.join(theDir,directory)

        for f in listdir(theDir):
            if f[0]!='.' and f[-1]!='~':
                if path.isfile(path.join(theDir,f)):
                    result.append(f)

        return result

    def getDictionaryText(self,directory,name):
        """@param directory: Sub-directory of the case
        @param name: name of the dictionary file
        @return: the contents of the file as a big string"""

        result=None
        theDir=self.name
        if directory:
            theDir=path.join(theDir,directory)

        if path.exists(path.join(theDir,name)):
            result=open(path.join(theDir,name)).read()
        else:
            warning("File",name,"does not exist in directory",directory,"of case",self.name)

        return result

    def writeDictionaryContents(self,directory,name,contents):
        """Writes the contents of a dictionary
        @param directory: Sub-directory of the case
        @param name: name of the dictionary file
        @param contents: Python-dictionary with the dictionary contents"""

        theDir=self.name
        if directory:
            theDir=path.join(theDir,directory)

        result=WriteParameterFile(path.join(theDir,name))
        result.content=contents
        result.writeFile()

    def writeDictionaryText(self,directory,name,text):
        """Writes the contents of a dictionary
        @param directory: Sub-directory of the case
        @param name: name of the dictionary file
        @param text: String with the dictionary contents"""

        theDir=self.name
        if directory:
            theDir=path.join(theDir,directory)

        result=open(path.join(theDir,name),"w").write(text)

    def getDictionaryContents(self,directory,name):
        """@param directory: Sub-directory of the case
        @param name: name of the dictionary file
        @return: the contents of the file as a python data-structure"""

        result={}
        theDir=self.name
        if directory:
            theDir=path.join(theDir,directory)

        if path.exists(path.join(theDir,name)):
            result=ParsedParameterFile(path.join(theDir,name)).content
        else:
            warning("File",name,"does not exist in directory",directory,"of case",self.name)

        return result

    def determineVCS(self):
        """Find out whether this directory is controlled by a VCS and
        return the abbreviation of that VCS"""

        if path.isdir(path.join(self.name,".hg")):
            return "hg"
        elif path.isdir(path.join(self.name,".git")):
            return "git"
        elif path.isdir(path.join(self.name,".svn")):
            return "svn"
        else:
            return None

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

class NoTouchSolutionDirectory(SolutionDirectory):
    """Convenience class that makes sure that nothing new is created"""

    def __init__(self,
                 name,
                 region=None):
        SolutionDirectory.__init__(self,
                                  name,
                                  archive=None,
                                  paraviewLink=False,
                                  region=region)

# Should work with Python3 and Python2
