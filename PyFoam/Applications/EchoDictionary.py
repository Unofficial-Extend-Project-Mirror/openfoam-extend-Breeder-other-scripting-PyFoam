#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/EchoDictionary.py 7660 2012-01-07T16:44:40.128256Z bgschaid  $ 
"""
Application class that implements pyFoamEchoDictionary
"""

import sys,re

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from CommonParserOptions import CommonParserOptions

from PyFoam.Error import PyFoamException

class EchoDictionary(PyFoamApplication,
                     CommonParserOptions):
    def __init__(self,args=None):
        description="""\
Reads a Foam-Dictionary and prints it to the screen. Mainly for
reformatting unformated dictionaries and debugging the parser
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
                                         preserveComments=self.opts.preserveComments,
                                         boundaryDict=self.opts.boundaryDict,
                                         listDict=self.opts.listDict,
                                         listDictWithHeader=self.opts.listDictWithHeader,
                                         doMacroExpansion=self.opts.doMacros)
        except IOError,e:
            self.error("Problem with file",fName,":",e)
        
        print dictFile
            
