#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/RunDictionary/ChemkinFiles.py 1917 2007-08-29T20:48:07.428000Z bgschaid  $ 
"""Parses Chemkin-Files"""

# raise "PyFoam","Work in progress. DO NOT USE"

import sys

from FileBasis import FileBasisBackup
from PyFoam.Basics.PlyParser import PlyParser

class ChemkinParser(PlyParser):
    """Overclass for the Chemkin-Parsers"""

    def __init__(self,content,debug=False):
        """@param content: the string to be parsed
        @param debug: output debug information during parsing"""

        PlyParser.__init__(self,debug=debug)

    def printContext(self,c,ind):
        """Prints the context of the current index"""
        print "------"
        print c[max(0,ind-100):max(0,ind-1)]
        print "------"
        print ">",c[ind-1],"<"
        print "------"
        print c[min(len(c),ind):min(len(c),ind+100)]
        print "------"

    def parserError(self,text,c,ind):
        """Prints the error message of the parser and exit"""
        print "PARSER ERROR:",text
        print "On index",ind
        self.printContext(c,ind)
        raise ParseError
        sys.exit(-1)

    tokens = (
        'THERMO',
        'ALL',
        'END',
        'ELEMENTS',
        'SPECIE',
        'REACTIONS',
        )
    
class ChemkinThermoFile(FileBasisBackup):
    """Parses a Chemkin-Thermo-File and makes it available"""

    def __init__(self,name,backup=False,debug=False):
        """@param name: The name of the parameter file
        @param backup: create a backup-copy of the file"""

        FileBasisBackup.__init__(self,name,backup=backup)

class ChemkinThermoParser(ChemkinParser):
    """Class that parses a string that contains the contents of an
    Chemkin-Thermo-file and builds a nested structure of directories and
    lists from it"""

    def __init__(self,content,debug=False):
        """@param content: the string to be parsed
        @param debug: output debug information during parsing"""

        ChemkinParser.__init__(self,content,debug=debug)
        
class ChemkinReactionsFile(FileBasisBackup):
    """Parses a Chemkin-Reaction-File and makes it available"""

    def __init__(self,name,backup=False,debug=False):
        """@param name: The name of the parameter file
        @param backup: create a backup-copy of the file"""

        FileBasisBackup.__init__(self,name,backup=backup)

class ChemkinReactionsParser(ChemkinParser):
    """Class that parses a string that contains the contents of an
    Chemkin-Reactions-file and builds a nested structure of directories and
    lists from it"""

    def __init__(self,content,debug=False,noHeader=False):
        """@param content: the string to be parsed
        @param debug: output debug information during parsing
        @param noHeader: switch that turns off the parsing of the header"""

        ChemkinParser.__init__(self,content,debug=debug)
        

