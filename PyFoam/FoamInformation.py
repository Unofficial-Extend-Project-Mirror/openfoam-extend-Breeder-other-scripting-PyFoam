#  ICE Revision: $Id$ 
"""Getting Information about the Foam-Installation (like the installation directory)"""

from os import environ,path,listdir
import sys

if sys.version_info<(2,6):
    from popen2 import popen4
else:
    from subprocess import Popen,PIPE,STDOUT

import re

from PyFoam.Error import error,warning

from PyFoam import configuration as config

def getPathFromEnviron(name):
    """Gets a path from an environment variable
    @return: the path
    @rtype: string
    @param name: the name of the environment variable"""

    tmp=""
    if name in environ:
        tmp=path.normpath(environ[name])

    return tmp

def foamTutorials():
    """@return: directory in which the tutorials reside"""

    return getPathFromEnviron("FOAM_TUTORIALS")

def foamMPI():
    """@return: the used MPI-Implementation"""
    if "WM_MPLIB" not in environ:
        return ()
    else:
        vStr=environ["WM_MPLIB"]
        return vStr
    
def foamVersionString(useConfigurationIfNoInstallation=False):
    """@return: string for the  Foam-version as found
    in $WM_PROJECT_VERSION"""
    
    if "WM_PROJECT_VERSION" not in environ and not useConfigurationIfNoInstallation:
        return ""
    else:
        if "WM_PROJECT_VERSION" in environ:
            vStr=environ["WM_PROJECT_VERSION"]
        else:
            vStr=""
            
        if vStr=="" and  useConfigurationIfNoInstallation:
            vStr=config().get("OpenFOAM","Version")

    return vStr

def foamVersion(useConfigurationIfNoInstallation=False):
    """@return: tuple that represents the Foam-version as found
    in $WM_PROJECT_VERSION"""

    vStr=foamVersionString(useConfigurationIfNoInstallation=useConfigurationIfNoInstallation)
    
    if vStr=="":
        return ()
    else:
        res=[]

        for el in vStr.split("."):
            for e in el.split("-"):
                try:
                    res.append(int(e))
                except:
                    res.append(e)
                
        return tuple(res)
    
def foamVersionNumber(useConfigurationIfNoInstallation=False):
    """@return: tuple that represents the Foam-Version-Number (without
    strings"""

    ver=foamVersion(useConfigurationIfNoInstallation=useConfigurationIfNoInstallation)

    nr=[]

    for e in ver:
        if type(e)==int:
            nr.append(e)
        else:
            break

    return tuple(nr)

def oldAppConvention():
    """Returns true if the version of OpenFOAM is older than 1.5 and
    it therefor uses the 'old' convention to call utilities ("dot, case")
    """
    return foamVersionNumber()<(1,5)

def oldTutorialStructure():
    """Returns true if the version of OpenFOAM is older than 1.6 and
    it therefor uses the 'old' (flat) structure for the tutorials
    """
    return foamVersionNumber()<(1,6)

def findInstalledVersions(basedir,valid):
    versions=set()

    try:
        candidates=listdir(basedir)
    except OSError:
        return versions

    for f in candidates:
        m=valid.match(f)
        if m:
            dname=path.join(basedir,f)
            if path.isdir(dname):
                name=m.groups(1)[0]
                dotDir=path.join(dname,".OpenFOAM-"+name)
                etcDir=path.join(dname,"etc")
                if path.isdir(etcDir) and path.exists(path.join(etcDir,"bashrc")):
                    versions.add(m.groups(1)[0])
                elif path.isdir(dotDir) and path.exists(path.join(dotDir,"bashrc")):
                    versions.add(m.groups(1)[0])
    
    return versions

def findBaseDir(newDir):
    if "WM_PROJECT_INST_DIR" in environ:
        basedir=environ["WM_PROJECT_INST_DIR"]
    else:
        basedir=path.expanduser(config().get("OpenFOAM","Installation"))
    
    for bdir in [basedir]+config().getList("OpenFOAM","AdditionalInstallation"):
        if path.exists(path.join(bdir,"OpenFOAM-"+newDir)):
            return (bdir,"OpenFOAM-")
        elif path.exists(path.join(bdir,"openfoam"+newDir)):
            return (bdir,"openfoam")
    
    error("Can't find basedir for OpenFOAM-version",newDir)

def foamInstalledVersions():
    """@return: A list with the installed versions of OpenFOAM"""

    versions=set()

    valid=re.compile("^OpenFOAM-([0-9]\.[0-9].*)$")
    valid2=re.compile("^openfoam([0-9]+)$")

    if "WM_PROJECT_INST_DIR" in environ:
        basedir=environ["WM_PROJECT_INST_DIR"]
    else:
        basedir=path.expanduser(config().get("OpenFOAM","Installation"))

    if not path.exists(basedir) or not path.isdir(basedir):
        warning("Basedir",basedir,"does not exist or is not a directory")
        return []

    for bdir in [basedir]+config().getList("OpenFOAM","AdditionalInstallation"):
        for val in [valid,valid2]:
            versions |= findInstalledVersions(bdir,val)

    return list(versions)
    
def changeFoamVersion(new,force64=False,force32=False,compileOption=None):
    """Changes the used FoamVersion. Only valid during the runtime of
    the interpreter (the script or the Python session)
    @param new: The new Version
    @param force64: Forces the 64-bit-version to be chosen
    @param force32: Forces the 32-bit-version to be chosen
    @param compileOption: Forces Debug or Opt"""

    if not new in foamInstalledVersions():
        error("Version",new,"is not an installed version: ",foamInstalledVersions())

    old=None
    if "WM_PROJECT_VERSION" in environ:
        old=environ["WM_PROJECT_VERSION"]
        if new==old:
            warning(new,"is already being used")
    else:
        warning("No OpenFOAM-Version installed")
        
    basedir,prefix=findBaseDir(new)

    if path.exists(path.join(basedir,prefix+new,"etc")):
        script=path.join(basedir,prefix+new,"etc","bashrc")
    else:
        script=path.join(basedir,prefix+new,".OpenFOAM-"+new,"bashrc")

    forceArchOption=None
    if force64:
       forceArchOption="64"
    elif force32:
       forceArchOption="32"

    injectVariables(script,
                    forceArchOption=forceArchOption,
                    compileOption=compileOption)
    
    try:
        if old==environ["WM_PROJECT_VERSION"]:
            warning("Problem while changing to version",new,"old version still used:",environ["WM_PROJECT_VERSION"])
    except KeyError:
        pass

def injectVariables(script,forceArchOption=None,compileOption=None):
    """Executes a script in a subshell and changes the current
    environment with the enivironment after the execution
    @param script: the script that is executed
    @param forceArchOption: To which architecture Option should be forced
    @param compileOption: to which value the WM_COMPILE_OPTION should be forced"""

    # Certan bashrc-s fail if these are set
    for v in ["FOAM_INST_DIR",
              "WM_THIRD_PARTY_DIR",
              "WM_PROJECT_USER_DIR",
              "OPAL_PREFIX"]:
        try:
            del environ[v]
        except KeyError:
            pass

    if not path.exists(script):
        error("Can not execute",script,"it does not exist")
        
    try:    
        if "SHELL" in environ:
            shell=environ["SHELL"]

        if(path.basename(shell).find("python")==0):
            # this assumes that the 'shell' is a PyFoam-Script on a cluster
            shell=config().get("Paths","bash")
            environ["SHELL"]=shell

        allowedShells = [ "bash", "zsh"]
        if not path.basename(shell) in allowedShells:
            error("Currently only implemented for the shells",allowedShells,", not for",shell)

        cmd=""
        postCmd=""
        if forceArchOption!=None:
            cmd+="export WM_ARCH_OPTION="+forceArchOption+"; "
            postCmd+=" WM_ARCH_OPTION="+forceArchOption
        if compileOption!=None:
            cmd+="export WM_COMPILE_OPTION="+compileOption+"; "
            postCmd+=" WM_COMPILE_OPTION="+compileOption
        cmd+=". "+script+postCmd+'; echo "Starting The Dump Of Variables"; export'
    except KeyError:
        # Instead of 'KeyError as name'. This is compatible with 2.4-3.2
        # http://docs.pythonsprints.com/python3_porting/py-porting.html#handling-exceptions
        name = sys.exc_info()[1]
        error("Can't do it, because shell variable",name,"is undefined")

    if sys.version_info<(2,6):
        raus,rein = popen4(cmd)
    else:
        p = Popen(cmd, shell=True,
                  stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        (rein,raus)=(p.stdin,p.stdout)
        
    lines=raus.readlines()
    rein.close()
    raus.close()

    # clumsy but avoids more complicated expressions
    exp=re.compile('export (.+)="(.*)"\n')
    exp2=re.compile("export (.+)='(.*)'\n")

    cnt=0
    
    for l in lines:
        m=exp.match(str(l))
        if not m:
            m=exp2.match(str(l))
        if m:
            cnt+=1
            environ[m.groups()[0]]=m.groups()[1]

# Should work with Python3 and Python2
