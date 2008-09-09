#  ICE Revision: $Id: EchoDictionary.py 9240 2008-08-18 10:44:50Z bgschaid $ 
"""
Application class that implements pyFoamEchoDictionary
"""

import sys,re

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

class EchoDictionary(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Reads a Foam-Dictionary and prints it to the screen. Mainly for reformatting
unformated dictionaries and debugging the parser
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <dictfile>",
                                   nr=1,
                                   changeVersion=False,
                                   interspersed=True)
        
    def addOptions(self):
        self.parser.add_option("--debug",
                               action="store_true",
                               default=None,
                               dest="debug"
                               ,help="Debugs the parser")
        
        self.parser.add_option("--no-header",
                               action="store_true",
                               default=False,
                               dest="noHeader",
                               help="Don't expect a header while parsing")
        
        self.parser.add_option("--no-body",
                               action="store_true",
                               default=False,
                               dest="noBody",
                               help="Don't expect a body while parsing (only parse the header)")
        
        self.parser.add_option("--boundary",
                               action="store_true",
                               default=False,
                               dest="boundaryDict",
                               help="Expect that this file is a boundary dictionary")
        
        self.parser.add_option("--list",
                               action="store_true",
                               default=False,
                               dest="listDict",
                               help="Expect that this file only contains a list")
        
    
    def run(self):
        fName=self.parser.getArgs()[0]
        try:
            dictFile=ParsedParameterFile(fName,
                                         backup=False,
                                         debug=self.opts.debug,
                                         noHeader=self.opts.noHeader,
                                         noBody=self.opts.noBody,
                                         boundaryDict=self.opts.boundaryDict,
                                         listDict=self.opts.listDict)
        except IOError,e:
            self.error("Problem with file",fName,":",e)

        print dictFile
            
