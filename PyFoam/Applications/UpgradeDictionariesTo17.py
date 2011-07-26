#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/UpgradeDictionariesTo17.py 7548 2011-07-20T21:43:14.778950Z bgschaid  $ 
"""
Application class that implements pyFoamUpgradeDictionariesTo17
"""

import sys,re
from optparse import OptionGroup
from os import path

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.Utilities import copyfile
from PyFoam.Basics.DataStructures import DictProxy
from PyFoam.Basics.FoamFileGenerator import makeString
from PyFoam.Error import error

class DictionaryUpgradeInfo(object):
    """This class knows how to detect old versions and how to upgrade them"""
    def __init__(self):
        self.case=None
        self.enabled=True
        
    def path(self):
        return path.join(self.case,self.location())

    def disable(self):
        self.enabled=False
        
    def disableCallback(self, opt, value, parser, *args, **kwargs):
        self.disable()

    def needsUpgrade(self):
        f=ParsedParameterFile(self.path())
        return self.checkUpgrade(f.content)

    def upgrade(self,force,print_):
        backup=self.path()+".upgradeBackup"
        if not print_:
            if path.exists(backup):
                if not force:
                    error("The backup-file",backup,"does already exist")

            copyfile(self.path(),backup)
        f=ParsedParameterFile(self.path())
        self.manipulate(f.content)
        if not print_:
            f.writeFile()
        else:
            print f
            
    def makeComment(self,data):
        s=makeString(data)
        s="\n old Value: "+s
        s=s.replace("\n","\n//")
        return s
    
class FvSolutionUpgradeInfo(DictionaryUpgradeInfo):
    def __init__(self):
        DictionaryUpgradeInfo.__init__(self)

    def location(self):
        return path.join("system","fvSolution")

    def checkUpgrade(self,content):
        if "solvers" not in content:
            return False
        
        for s in content["solvers"]:
            if type(content["solvers"][s]) not in [dict,DictProxy]:
                return True
        return False

    def manipulate(self,content):
        for s in content["solvers"]:
            comment=self.makeComment(content["solvers"][s])
            alg,rest=content["solvers"][s]
            rest["solver"]=alg
            content["solvers"][s]=rest
            content["solvers"].addDecoration(s,comment)
            
class UpgradeDictionariesTo17(PyFoamApplication):
    def __init__(self,
                 args=None,
                 description=None):
        if not description:
            description="""
Examines dictionaries in a case and tries to upgrade them to a form that is
compatible with OpenFOAM 1.7
        """
        
        self.dicts=[]

        self.addDicts()

        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <case>",
                                   changeVersion=False,
                                   nr=1,
                                   interspersed=True)

    def addDicts(self):
        self.dicts.append(FvSolutionUpgradeInfo())

    def addOptions(self):
        behaveGroup=OptionGroup(self.parser,
                                "Behaviour",
                                "General behaviour of the program")
        
        behaveGroup.add_option("--apply-changes",
                               action="store_true",
                               dest="applyChanges",
                               default=False,
                               help="Apply changes to the dictionaries in question. Without this option only the results of the analysis will be shown")

        behaveGroup.add_option("--print",
                               action="store_true",
                               dest="print_",
                               default=False,
                               help="Only print the modified dictionaries to the screen")
        
        behaveGroup.add_option("--verbose",
                               action="store_true",
                               dest="verbose",
                               default=False,
                               help="Speak out aloud which decisions are made")
        
        behaveGroup.add_option("--force",
                               action="store_true",
                               dest="force",
                               default=False,
                               help="Force even if backup-files exist")
        
        self.parser.add_option_group(behaveGroup)
    
        self.dictGroup=OptionGroup(self.parser,
                              "Dictionaries",
                              "Dictionaries that should be updated")

        for d in self.dicts:
            self.dictGroup.add_option("--disable-"+"-".join(reversed(d.location().split(path.sep))),
                                      action="callback",
                                      callback=d.disableCallback,
                                      help="Disable the modification of "+d.location())
            
        self.parser.add_option_group(self.dictGroup)
    
    def run(self):
        case=self.parser.getArgs()[0]
        self.checkCase(case)
        
        if self.opts.verbose:
            print "Working on case",case

        for d in self.dicts:
            d.case=case
            if self.opts.verbose:
                print "  Checking",d.location()

            if not d.enabled:
                if self.opts.verbose:
                    print "    Disabled"
                continue
            
            if not path.exists(d.path()):
                d.disable()
                if self.opts.verbose:
                    print "    Does not exist - disabling"
                continue

            if not d.needsUpgrade():
                d.disable()
                if self.opts.verbose:
                    print "    Does not need an upgrade - disbling"
                continue
            
            print d.location(),"needs an upgrade"

        if self.opts.applyChanges or self.opts.print_:
            print
            if self.opts.applyChanges:
                print "Doing the upgrades"
            for d in self.dicts:
                if d.enabled:
                    if self.opts.verbose:
                        print "Upgrading",d.location()
                    d.upgrade(self.opts.force,self.opts.print_)
                    
    
