#  ICE Revision: $Id: EchoDictionary.py 10485 2009-05-25 14:50:08Z bgschaid $ 
"""
Application class that implements pyFoamEchoDictionary
"""

import sys,re

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from CommonParserOptions import CommonParserOptions

class EchoDictionary(PyFoamApplication,
                     CommonParserOptions):
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
        CommonParserOptions.addOptions(self)
    
    def run(self):
        fName=self.parser.getArgs()[0]
        try:
            dictFile=ParsedParameterFile(fName,
                                         backup=False,
                                         debug=self.opts.debugParser,
                                         noHeader=self.opts.noHeader,
                                         noBody=self.opts.noBody,
                                         boundaryDict=self.opts.boundaryDict,
                                         listDict=self.opts.listDict,
                                         listDictWithHeader=self.opts.listDictWithHeader,
                                         doMacroExpansion=self.opts.doMacros)
        except IOError,e:
            self.error("Problem with file",fName,":",e)

        print dictFile
            
