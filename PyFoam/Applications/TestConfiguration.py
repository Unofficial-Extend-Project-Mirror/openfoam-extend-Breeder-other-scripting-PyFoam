#  ICE Revision: $Id: TestConfiguration.py 12762 2013-01-03 23:11:02Z bgschaid $
"""
Application class that implements pyFoamTestConfiguration.py
"""

import sys,re
from PyFoam.ThirdParty.six.moves import configparser as ConfigParser
from PyFoam.ThirdParty.six import print_

from .PyFoamApplication import PyFoamApplication

from .CommonParserOptions import CommonParserOptions

from PyFoam.FoamInformation import foamVersionString
from PyFoam import configuration as config

class TestConfiguration(PyFoamApplication,
                     CommonParserOptions):
    def __init__(self,args=None):
        description="""\
Tests what value a section/option pair gives for a specific
OpenFOAM-version

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

        print_("Foam-Version: ",foamVersionString())
        print_("Section:      ",section)
        print_("Option:       ",option)
        print_("Value:        ",end="")
        try:
            print_(config().get(section,option))
        except ConfigParser.NoSectionError:
            print_("<section not found>")
        except ConfigParser.NoOptionError:
            print_("<option not found>")

# Should work with Python3 and Python2
