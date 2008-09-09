#  ICE Revision: $Id: FoamOptionParser.py 9161 2008-08-04 08:01:05Z bgschaid $ 
"""Parse options for the PyFoam-Scripts"""

from optparse import OptionParser,TitledHelpFormatter
from PyFoam import versionString

from PyFoam.FoamInformation import changeFoamVersion
from PyFoam.FoamInformation import oldAppConvention as oldApp

from os import path

class FoamOptionParser(OptionParser):
    """Wrapper to the usual OptionParser to honor the conventions of OpenFOAM-utilities

    Options that are not used by the script are passed to the OpenFOAM-application"""
    
    def __init__(self,args=None,usage=None,version=None,description=None,interspersed=False):
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
            
        OptionParser.__init__(self,usage=usage,version=version,description=description,formatter=TitledHelpFormatter())

        if interspersed:
            self.enable_interspersed_args()
        else:
            self.disable_interspersed_args()
        
        self.options=None
        self.args=None
        
    def parse(self,nr=None,exactNr=True):
        """
        parse the options
        @param nr: minimum number of arguments that are to be passed to the application
        3 is default for pre-1.5 versions of OpenFOAM
        """
        (self.options,self.args)=self.parse_args(args=self.argLine)
        
        if "foamVersion" in dir(self.options):
            if self.options.foamVersion!=None:
                changeFoamVersion(self.options.foamVersion)
            
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
                return self.getArgs()[self.getArgs().index("-case")+1]
            else:
                return path.curdir
