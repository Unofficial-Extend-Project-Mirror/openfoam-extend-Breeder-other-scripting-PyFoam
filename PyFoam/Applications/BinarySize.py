"""
Application-class that implements pyFoamBinarySize.py
"""
from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication

from PyFoam.ThirdParty.six import print_

from PyFoam.Basics.Utilities import diskUsage,humanReadableSize

import PyFoam.FoamInformation as FI

from os import listdir,path

class BinarySize(PyFoamApplication):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
Goes through the OpenFOAM-installation and records the size of all the binary
files (linked as well as object files) and reports them for each compiliation
option separately (Debug/Opt, compilers)

This should provide the user with an overview how much disk space each variation
of the binaries needs.

The reported OpenfOAM-installation can be selected using the usual Foam-version
switching.
"""
        examples="""\
%prog

  List the disk space used by the current OpenFOAM-installation

%prog --foamVersion=1.7.x

  List the disk space used by binaries in OpenFOAM-1.7.x

%prog --all-installations

  List the disk space used by all the available installations

%prog --all-installations --follow-symlinked-installations

  Also follow symlinked installations (this may count binaries twice)"""

        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   examples=examples,
                                   usage="%prog <caseDirectory>",
                                   interspersed=True,
                                   changeVersion=True,
                                   nr=0,
                                   exactNr=True,
                                   **kwargs)

    def addOptions(self):
        what=OptionGroup(self.parser,
                         "What",
                         "What should be reported")
        self.parser.add_option_group(what)

        what.add_option("--all-installations",
                        action="store_true",
                        dest="allInstallations",
                        default=False,
                        help="Report the disk usage for all installations (this may take quite a while)")
        what.add_option("--follow-symlinked-installations",
                        action="store_true",
                        dest="symlinkInstallations",
                        default=False,
                        help="Also count the installation if it is a symlink (otherwise only report the original installation and skip it)")

    def scanDir(self,dPath,usages):
        dName=path.basename(dPath)
        if dName[0]==".":
            return
        elif dName in ["lnInclude","Doxygen"]:
            return
        elif dName in ["Make","platform","bin"]:
            for f in listdir(dPath):
                if f[0]==".":
                    continue
                nPath=path.join(dPath,f)
                if path.isdir(nPath):
                    isBin=False
                    for end in ["Opt","Debug","Prof"]:
                        if f.find(end)>0 and (f.find(end)+len(end))==len(f):
                            isBin=True
                    if isBin:
                        sz=diskUsage(nPath)
                        try:
                            usages[f]+=sz
                        except KeyError:
                            usages[f]=sz
                           # print_("Found architecture",f,"in",dPath)
        else:
            try:
                for f in listdir(dPath):
                    nPath=path.join(dPath,f)
                    if path.isdir(nPath) and not path.islink(nPath):
                        self.scanDir(nPath,usages)
            except OSError:
                self.warning("Can't process",dPath)

    def reportInstallation(self,fName):
        """Report the usages of a OpenFOAM-installation"""

        print_("\nScanning",fName)
        if path.islink(fName):
            print_("Symlinked to",path.realpath(fName))
            if not self.opts.symlinkInstallations:
                print_("Skipping symlinked installation")
                return 0
        usages={}
        self.scanDir(fName,usages)
        if len(usages)>0:
            nameLength=max([len(k) for k in usages.keys()])
            sizeLength=max([len(str(k)) for k in usages.values()])
            formatString="    %%%ds - %%%dd (%%s)" % (nameLength,sizeLength)
            total=0
            for k in sorted(usages.keys()):
                v=usages[k]
                total+=v
                print_(formatString % (k,v,humanReadableSize(v)))
            print_("Sum of binaries",humanReadableSize(total))
            return total
        else:
            print_("    No binaries found")
            return 0

    def run(self):
        if self.opts.allInstallations:
             installed=FI.foamInstalledVersions()
             total=0
             for k in sorted(installed.keys()):
                 instPath=installed[k]
                 total+=self.reportInstallation(instPath)
             print_("\nTotal disk space used by binaries:"+humanReadableSize(total))
        else:
             self.reportInstallation(FI.installationPath())