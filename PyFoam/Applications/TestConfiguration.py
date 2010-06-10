#  ICE Revision: $Id: TestConfiguration.py 11497 2010-04-21 16:01:10Z bgschaid $ 
"""
Application class that implements pyFoamTestConfiguration.py
"""

import sys,re
import ConfigParser

from PyFoamApplication import PyFoamApplication

from CommonParserOptions import CommonParserOptions

from PyFoam.FoamInformation import foamVersionString
from PyFoam import configuration as config

class TestConfiguration(PyFoamApplication,
                     CommonParserOptions):
    def __init__(self,args=None):
        description="""
Tests what value a section/option pair gives for a specific OpenFOAM-version

Used to find configuration problems
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <section> <option>",
                                   nr=2,
                                   interspersed=True)
        
    def addOptions(self):
        CommonParserOptions.addOptions(self)
    
    def run(self):
        section=self.parser.getArgs()[0]
        option=self.parser.getArgs()[1]

        print "Foam-Version: ",foamVersionString()
        print "Section:      ",section
        print "Option:       ",option
        print "Value:        ",
        try:
            print config().get(section,option)
        except ConfigParser.NoSectionError:
            print "<section not found>"
        except ConfigParser.NoOptionError:
            print "<option not found>"
            
