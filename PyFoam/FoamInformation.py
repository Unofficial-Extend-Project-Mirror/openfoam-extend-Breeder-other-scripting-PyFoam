#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/FoamInformation.py 2998 2008-04-09T16:20:08.924143Z bgschaid  $ 
"""Getting Information about the Foam-Installation (like the installation directory)"""

from os import environ,path,listdir
from popen2 import popen4

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
    """@return the used MPI-Implementation"""
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
                if path.isdir(dotDir) and path.exists(path.join(dotDir,"bashrc")):
                    versions.append(m.groups(1)[0])
            
    return versions
    
def changeFoamVersion(new):
    """Changes the used FoamVersion. Only valid during the runtime of
    the interpreter (the script or the Python session)
    @param new: The new Version"""

    if not new in foamInstalledVersions():
        error("Version",new,"is not an installed version: ",foamInstalledVersions())

    if environ.has_key("WM_PROJECT_VERSION"):
        if new==environ["WM_PROJECT_VERSION"]:
            warning(new,"is already being used")
            return
    else:
        warning("No OpenFOAM-Version installed")
        
    if environ.has_key("WM_PROJECT_INST_DIR"):
        basedir=environ["WM_PROJECT_INST_DIR"]
    else:
        basedir=path.expanduser(config().get("OpenFOAM","Installation"))
            
    script=path.join(basedir,"OpenFOAM-"+new,".OpenFOAM-"+new,"bashrc")

    injectVariables(script)
    
    if new!=environ["WM_PROJECT_VERSION"]:
        error("Problem while changing to version",new,"old version still used:",environ["WM_PROJECT_VERSION"])

def injectVariables(script):
    """Executes a script in a subshell and changes the current
    environment with the enivironment after the execution
    @param script: the script that is executed"""

    if not path.exists(script):
        error("Can not execute",script,"it does not exist")
        
    try:    
        if environ.has_key("SHELL"):
            shell=environ["SHELL"]

        if(path.basename(shell)=="python"):
            # this assumes that the 'shell' is a PyFoam-Script on a cluster
            shell=config().get("Paths","bash")
            environ["SHELL"]=shell
            
        if(path.basename(shell)!="bash"):
            error("Currently only implemented for bash-shell, not for",shell)

        cmd=". "+script+'; echo "Starting The Dump Of Variables"; export'
    except KeyError,name:
        error("Can't do it, because shell variable",name,"is undefined")

    raus,rein = popen4(cmd)
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
    
