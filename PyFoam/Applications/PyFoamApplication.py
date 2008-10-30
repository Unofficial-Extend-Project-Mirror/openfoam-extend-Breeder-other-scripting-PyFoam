#  ICE Revision: $Id: PyFoamApplication.py 9442 2008-09-23 09:11:07Z bgschaid $ 
"""Base class for pyFoam-applications

Classes can also be called with a command-line string"""

from optparse import OptionGroup
from PyFoam.Basics.FoamOptionParser import FoamOptionParser
from PyFoam.Error import error,warning
from PyFoam.FoamInformation import oldAppConvention as oldApp

import sys
from os import path

class PyFoamApplication(object):
    def __init__(self,
                 args=None,
                 description=None,
                 usage=None,
                 interspersed=False,
                 nr=None,
                 changeVersion=True,
                 exactNr=True):
        """
        @param description: description of the command
        @param usage: Usage
        @param interspersed: Is the command line allowed to be interspersed (options after the arguments)
        @param args: Command line arguments when using the Application as a 'class' from a script
        @param nr: Number of required arguments
        @param chaneVersion: May this application change the version of OF used?
        @param exactNr: Must not have more than the required number of arguments
        """
        self.parser=FoamOptionParser(args=args,
                                     description=description,
                                     usage=usage,
                                     interspersed=interspersed)
        self.generalOpts=None
        
        grp=OptionGroup(self.parser,
                        "Default",
                        "Options common to all PyFoam-applications")

        if changeVersion:
            grp.add_option("--foamVersion",
                           dest="foamVersion",
                           default=None,
                           help="Change the OpenFOAM-version that is to be used")

        grp.add_option("--psyco-accelerated",
                       dest="psyco",
                       default=False,
                       action="store_true",
                       help="Accelerate the script using the psyco-library (EXPERIMENTAL and requires a separatly installed psyco)")
        grp.add_option("--profile-python",
                       dest="profilePython",
                       default=False,
                       action="store_true",
                       help="Profile the python-script (not the OpenFOAM-program) - mostly of use for developers")
        grp.add_option("--profile-hotshot",
                       dest="profileHotshot",
                       default=False,
                       action="store_true",
                       help="Profile the python-script using the hotshot-library (not the OpenFOAM-program) - mostly of use for developers - EXPERIMENTAL")

        self.parser.add_option_group(grp)

        self.addOptions()
        self.parser.parse(nr=nr,exactNr=exactNr)
        self.opts=self.parser.getOptions()

        if self.opts.psyco:
            try:
                import psco
                psyco.full()
            except ImportError:
                warning("No psyco installed. Continuing without acceleration")

        if self.opts.profilePython or self.opts.profileHotshot:
            if self.opts.profilePython and self.opts.profileHotshot:
                self.error("Profiling with hotshot and regular profiling are mutual exclusive")
            print "Running profiled"
            if self.opts.profilePython:
                import profile
            else:
                import hotshot
            profileData=path.basename(sys.argv[0])+".profile"
            if self.opts.profilePython:            
                profile.runctx('self.run()',None,{'self':self},profileData)
                print "Reading python profile"
                import pstats
                stats=pstats.Stats(profileData)
            else:
                profileData+=".hotshot"
                prof=hotshot.Profile(profileData)
                prof.runctx('self.run()',{},{'self':self})
                print "Writing and reading hotshot profile"
                prof.close()
                import hotshot.stats
                stats=hotshot.stats.load(profileData)
            stats.strip_dirs()
            stats.sort_stats('time','calls')
            stats.print_stats(20)
        else:
            self.run()

    def ensureGeneralOptions(self):
        if self.generalOpts==None:
            self.generalOpts=OptionGroup(self.parser,
                                         "General",
                                         "General options for the control of OpenFOAM-runs")
            self.parser.add_option_group(self.generalOpts)
            
    def addOptions(self):
        """
        Add options to the parser
        """
        pass

    def run(self):
        """
        Run the real application
        """
        error("Not a valid application")
        

    def error(self,*args):
        """
        Prints an error message and exits
        @param args: Arguments that are to be printed
        """
        print "Error in",sys.argv[0],":",
        for a in args:
            print a,
        print
        sys.exit(-1)
        
    def checkCase(self,name):
        """
        Check whether this is a valid OpenFOAM-case
        @param name: the directory-bame that is supposed to be the case
        """
        if not path.exists(name):
            self.error("Case",name,"does not exist")
        if not path.isdir(name):
            self.error("Case",name,"is not a directory")
        if not path.exists(path.join(name,"system")):
            self.error("Case",name,"does not have a 'system' directory")
        if not path.exists(path.join(name,"constant")):
            self.error("Case",name,"does not have a 'constant' directory")
