#  ICE Revision: $Id: FoamInformation.py 10943 2009-10-09 07:31:48Z bgschaid $ 
"""Getting Information about the Foam-Installation (like the installation directory)"""

from os import environ,path,listdir
import sys

if sys.version_info<(2,6):
    from popen2 import popen4
else:
    from subprocess import Popen,PIPE,STDOUT

import re

from Error import error,warning

from PyFoam import configuration as config

def getPathFromEnviron(name):
    """Gets a path from an environment variable
    @return: the path
    @rtype: string
    @param name: the name of the environment variable"""

    tmp=""
    if environ.has_key(name):
        tmp=path.normpath(environ[name])

    return tmp

def foamTutorials():
    """@return: directory in which the tutorials reside"""

    return getPathFromEnviron("FOAM_TUTORIALS")

def foamMPI():
    """@return: the used MPI-Implementation"""
    if not environ.has_key("WM_MPLIB"):
        return ()
    else:
        vStr=environ["WM_MPLIB"]
        return vStr
    
def foamVersion():
    """@return: tuple that represents the Foam-version as found
    in $WM_PROJECT_VERSION"""
    
    if not environ.has_key("WM_PROJECT_VERSION"):
        return ()
    else:
        vStr=environ["WM_PROJECT_VERSION"]
        res=[]

        for el in vStr.split("."):
            for e in el.split("-"):
                try:
                    res.append(int(e))
                except:
                    res.append(e)
                
        return tuple(res)
    
def foamVersionNumber():
    """@return: tuple that represents the Foam-Version-Number (without
    strings"""

    ver=foamVersion()

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

def foamInstalledVersions():
    """@return: A list with the installed versions of OpenFOAM"""

    versions=[]

    valid=re.compile("^OpenFOAM-([0-9]\.[0-9].*)$")

    if environ.has_key("WM_PROJECT_INST_DIR"):
        basedir=environ["WM_PROJECT_INST_DIR"]
    else:
        basedir=path.expanduser("~/OpenFOAM")
        
    for f in listdir(basedir):
        m=valid.match(f)
        if m:
            dname=path.join(basedir,f)
            if path.isdir(dname):
                name=m.groups(1)[0]
                dotDir=path.join(dname,".OpenFOAM-"+name)
                etcDir=path.join(dname,"etc")
                if path.isdir(etcDir) and path.exists(path.join(etcDir,"bashrc")):
                    versions.append(m.groups(1)[0])
                elif path.isdir(dotDir) and path.exists(path.join(dotDir,"bashrc")):
                    versions.append(m.groups(1)[0])
            
    return versions
    
def changeFoamVersion(new,force64=False,force32=False,compileOption=None):
    """Changes the used FoamVersion. Only valid during the runtime of
    the interpreter (the script or the Python session)
    @param new: The new Version
    @param force64: Forces the 64-bit-version to be chosen
    @param force32: Forces the 32-bit-version to be chosen
    @param compileOption: Forces Debug or Opt"""

    if not new in foamInstalledVersions():
        error("Version",new,"is not an installed version: ",foamInstalledVersions())

    if environ.has_key("WM_PROJECT_VERSION"):
        if new==environ["WM_PROJECT_VERSION"]:
            warning(new,"is already being used")
    else:
        warning("No OpenFOAM-Version installed")
        
    if environ.has_key("WM_PROJECT_INST_DIR"):
        basedir=environ["WM_PROJECT_INST_DIR"]
    else:
        basedir=path.expanduser(config().get("OpenFOAM","Installation"))

    if path.exists(path.join(basedir,"OpenFOAM-"+new,"etc")):
        script=path.join(basedir,"OpenFOAM-"+new,"etc","bashrc")
    else:
        script=path.join(basedir,"OpenFOAM-"+new,".OpenFOAM-"+new,"bashrc")

    forceArchOption=None
    if force64:
       forceArchOption="64"
    elif force32:
       forceArchOption="32"
       
    injectVariables(script,
                    forceArchOption=forceArchOption,
                    compileOption=compileOption)
    
    if new!=environ["WM_PROJECT_VERSION"]:
        error("Problem while changing to version",new,"old version still used:",environ["WM_PROJECT_VERSION"])

def injectVariables(script,forceArchOption=None,compileOption=None):
    """Executes a script in a subshell and changes the current
    environment with the enivironment after the execution
    @param script: the script that is executed
    @param forceArchOption: To which architecture Option should be forced
    @param compileOption: to which value the WM_COMPILE_OPTION should be forced"""

    if not path.exists(script):
        error("Can not execute",script,"it does not exist")
        
    try:    
        if environ.has_key("SHELL"):
            shell=environ["SHELL"]

        if(path.basename(shell)=="python"):
            # this assumes that the 'shell' is a PyFoam-Script on a cluster
            shell=config().get("Paths","bash")
            environ["SHELL"]=shell

        allowedShells = [ "bash", "zsh"]
        if not path.basename(shell) in allowedShells:
            error("Currently only implemented for the shells",allowedShells,", not for",shell)

        cmd=""
        if forceArchOption!=None:
            cmd+="export WM_ARCH_OPTION="+forceArchOption+"; "
        if compileOption!=None:
            cmd+="export WM_COMPILE_OPTION="+compileOption+"; "
        cmd+=". "+script+'; echo "Starting The Dump Of Variables"; export'
    except KeyError,name:
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

    exp=re.compile('export (.+)="(.*)"\n')

    cnt=0
    
    for l in lines:
        m=exp.match(l)
        if m:
            cnt+=1
            environ[m.groups()[0]]=m.groups()[1]
    
