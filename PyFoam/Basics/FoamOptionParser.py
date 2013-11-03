#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/FoamOptionParser.py 7815 2012-01-30T19:52:34.081422Z bgschaid  $ 
"""Parse options for the PyFoam-Scripts"""

from optparse import OptionParser,TitledHelpFormatter
from PyFoam import versionString

from PyFoam.FoamInformation import changeFoamVersion
from PyFoam.FoamInformation import oldAppConvention as oldApp

from PyFoam.Error import error,warning

from os import path,environ
from copy import deepcopy

class FoamOptionParser(OptionParser):
    """Wrapper to the usual OptionParser to honor the conventions of OpenFOAM-utilities

    Options that are not used by the script are passed to the OpenFOAM-application"""
    
    def __init__(self,
                 args=None,
                 usage=None,
                 version=None,
                 description=None,
                 interspersed=False):
        """
        @param usage: usage string. If missing a default is used
        @param version: if missing the PyFoam-version is used
        @param description: description of the utility
        @param interspersed: needs to be false if options should be passed to an OpenFOAM-utility
        @param args: Command line arguments. If unset sys.argv[1:] is used.
        Can be a string: it will be splitted then unsing the spaces (very primitive), or a list of strings (prefered)
        """
        if usage==None:
            if oldApp():
                usage="%prog [options] <foamApplication> <caseDir> <caseName> [foamOptions]"
            else:
                usage="%prog [options] <foamApplication> [foamOptions]"
                
        if version==None:
            version="%prog "+versionString()

        if args==None:
            self.argLine=None
        elif type(args)==str:
            self.argLine=args.split()
        else:
            self.argLine=map(str,args)
            
        OptionParser.__init__(self,
                              usage=usage,
                              # prog=self.__type__.__name__,
                              version=version,
                              description=description,
                              formatter=TitledHelpFormatter())

        if interspersed:
            self.enable_interspersed_args()
        else:
            self.disable_interspersed_args()
        
        self.options=None
        self.args=None
        
        self.__foamVersionChanged=False
        self.__oldEnvironment=None

    def restoreEnvironment(self):
        """Restore the environment to its old glory... if it was changed"""
        if self.__foamVersionChanged:
            #            print "Restoring the environment"
            environ.update(self.__oldEnvironment)

    def parse(self,nr=None,exactNr=True):
        """
        parse the options
        @param nr: minimum number of arguments that are to be passed to the application
        3 is default for pre-1.5 versions of OpenFOAM
        """
        (self.options,self.args)=self.parse_args(args=self.argLine)
            
        if "foamVersion" in dir(self.options):
            if self.options.foamVersion!=None:
                if self.options.force32 and self.options.force64:
                    error("A version can't be 32 and 64 bit at the same time")

                self.__foamVersionChanged=True
                self.__oldEnvironment=deepcopy(environ)

                changeFoamVersion(self.options.foamVersion,
                                  force64=self.options.force64,
                                  force32=self.options.force32,
                                  compileOption=self.options.compileOption)
            elif self.options.force32 or self.options.force64:
                warning("Foring version to be 32 or 64 bit, but no version chosen. Doing nothing")
            elif self.options.compileOption:
                warning("No OpenFOAM-version chosen. Can't set compile-option to",self.options.compileOption)
                
        if nr==None:
            if oldApp():
                nr=3
            else:
                nr=1
                
        if len(self.args)<nr:
            self.error("Too few arguments (%d needed, %d given)" %(nr,len(self.args)))

        maxNr=nr
        if not oldApp():
            if "-case" in self.args:
                maxNr+=2
                
        if exactNr and len(self.args)>maxNr:
            self.error("Too many arguments (%d needed, %d given)" %(nr,len(self.args)))
            
        tmp=self.args
        self.args=[]
        for a in tmp:
            if a.find(" ")>=0 or a.find("(")>=0:
                a="\""+a+"\""
            self.args.append(a)
        
    def getArgs(self):
        """Return the arguments left after parsing"""
        if self.args!=None:
            return self.args
        else:
            return []

    def getApplication(self):
        """Return the OpenFOAM-Application to be run"""
        if self.args!=None:
            return self.args[0]
        else:
            return None

    def getOptions(self):
        """Return the options"""
        if self.options==None:
            self.error("options have not been parsed yet")
            
        return self.options
        
    def casePath(self):
        """Returns the path to the case (if applicable)"""
        if oldApp():
            return path.join(self.getArgs()[1],self.getArgs()[2])
        else:
            if "-case" in self.getArgs():
                return path.normpath(self.getArgs()[self.getArgs().index("-case")+1])
            else:
                return path.abspath(path.curdir)
