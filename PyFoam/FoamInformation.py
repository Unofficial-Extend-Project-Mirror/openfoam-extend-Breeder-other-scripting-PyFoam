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

class VersionTuple(tuple):
    """Wrapper around the regular tuple that is printed in a way that
    can be parsed as a tuple in a OF-dictionary

    """

    # Python3 doesn't like this. But it was only here out of courtesy
#    def __init__(self,data):
#        tuple.__init__(self,data)

    def __str__(self):
        return ".".join([str(e) for e in self])

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

        return VersionTuple(res)

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

    return VersionTuple(nr)

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

def installationPath():
    """Path to the installation"""
    return path.abspath(environ["WM_PROJECT_DIR"])

def findInstalledVersions(basedir,valid,forkName="openfoam"):
    versions={}

    basedir=path.abspath(basedir)

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
                    versions[(forkName,m.groups(1)[0])]=dname
                elif path.isdir(dotDir) and path.exists(path.join(dotDir,"bashrc")):
                    versions[(forkName,m.groups(1)[0])]=dname

    return versions

__foamInstallations=None

def findInstallationDir(newVersion):
    installed=foamInstalledVersions()
    found=[]

    for fork,version in installed.keys():
        if newVersion==version:
            found.append((fork,version))
        elif newVersion==(fork+"-"+version):
            found.append((fork,version))

    if len(found)==0:
        error("Can't find basedir for OpenFOAM-version",newVersion,"in",
              ", ".join([ a[0]+"-"+a[1] for a in installed.keys() ]))
    elif len(found)==1:
        return found[0][0],found[0][1],installed[found[0]]
    else:
        error("Requested version:",newVersion,"Matches found:",
              ", ".join([ a[0]+"-"+a[1] for a in found ]))

def foamInstalledVersions():
    """@return: A list with the installed versions of OpenFOAM"""
    global __foamInstallations

    if __foamInstallations:
        return __foamInstallations

    __foamInstallations={}

    "^OpenFOAM-([0-9]\.[0-9].*)$","^openfoam([0-9]+)$"
    forks=config().getList("OpenFOAM","Forks")

    for fork in forks:
        currentFork=foamFork()

        if "WM_PROJECT_INST_DIR" in environ and currentFork==fork:
            basedir=environ["WM_PROJECT_INST_DIR"]
        else:
            basedir=path.expanduser(config().get("OpenFOAM","Installation-"+fork))

        if not path.exists(basedir) or not path.isdir(basedir):
            warning("Basedir",basedir,"for fork",fork,"does not exist or is not a directory")
            continue

        for bdir in [basedir]+config().getList("OpenFOAM","AdditionalInstallation"):
            for val in [re.compile(s) for s in config().getList("OpenFOAM","DirPatterns-"+fork)]:
                __foamInstallations.update(findInstalledVersions(bdir,val,fork))

    return __foamInstallations

def foamFork():
    """The currently used fork of OpenFOAM/Foam"""
    try:
        return environ["WM_FORK"]
    except KeyError:
        return "openfoam"

def changeFoamVersion(new,
                      force64=False,
                      force32=False,
                      compileOption=None,
                      foamCompiler=None,
                      wmCompiler=None):
    """Changes the used FoamVersion. Only valid during the runtime of
    the interpreter (the script or the Python session)
    @param new: The new Version
    @param force64: Forces the 64-bit-version to be chosen
    @param force32: Forces the 32-bit-version to be chosen
    @param compileOption: Forces Debug or Opt
    @param wmCompiler: Force new value for WM_COMPILER
    @param foamCompiler: Force system or OpenFOAM-Compiler"""

    newFork,newVersion,basedir=findInstallationDir(new)

    old=None
    oldFork=foamFork()
    if "WM_PROJECT_VERSION" in environ:
        old=environ["WM_PROJECT_VERSION"]
        if newVersion==old and newFork==oldFork:
            warning(old+"-"+foamFork(),"is already being used")
    else:
        warning("No OpenFOAM-Version installed")

    if path.exists(path.join(basedir,"etc")):
        script=path.join(basedir,"etc","bashrc")
    else:
        script=path.join(basedir,".OpenFOAM-"+new,"bashrc")

    forceArchOption=None
    if force64:
       forceArchOption="64"
    elif force32:
       forceArchOption="32"

    injectVariables(script,
                    forceArchOption=forceArchOption,
                    compileOption=compileOption,
                    foamCompiler=foamCompiler,
                    wmCompiler=wmCompiler)

    try:
        if old==environ["WM_PROJECT_VERSION"] and oldFork==foamFork():
            warning("Problem while changing to version",new,"old version still used:",foamFork()+"-"+environ["WM_PROJECT_VERSION"])
    except KeyError:
        pass

def injectVariables(script,
                    forceArchOption=None,
                    compileOption=None,
                    foamCompiler=None,
                    wmCompiler=None):
    """Executes a script in a subshell and changes the current
    environment with the enivironment after the execution
    @param script: the script that is executed
    @param forceArchOption: To which architecture Option should be forced
    @param compileOption: to which value the WM_COMPILE_OPTION should be forced
    @param wmCompiler: Force new value for WM_COMPILER
    @param foamCompiler: Force system or OpenFOAM-Compiler"""

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
        if foamCompiler!=None:
            cmd+="export foamCompiler="+foamCompiler+"; "
            postCmd+=" foamCompiler="+foamCompiler
        if wmCompiler!=None:
            cmd+="export WM_COMPILER="+wmCompiler+"; "
            postCmd+=" WM_COMPILER="+wmCompiler
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

    lines=[l.strip().decode() for l in raus.readlines()]
    rein.close()
    raus.close()

    # clumsy but avoids more complicated expressions
    exp=re.compile('export (.+)="(.*)"$')
    exp2=re.compile("export (.+)='(.*)'$")

    cnt=0

    for l in lines:
        m=exp.match(str(l))
        if not m:
            m=exp2.match(str(l))
        if m:
            cnt+=1
            environ[m.groups()[0]]=m.groups()[1]

# Should work with Python3 and Python2
