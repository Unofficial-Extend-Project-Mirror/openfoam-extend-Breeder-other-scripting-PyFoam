#  ICE Revision: $Id: ListFile.py 7832 2007-08-28 13:07:26Z bgschaid $ 
"""File that contains only a list (for instance points)"""

from PyFoam.Basics.LineReader import LineReader
from SolutionFile import SolutionFile

class ListFile(SolutionFile):
    """Represents a OpenFOAM file with only a list"""
    
    def __init__(self,place,name):
        """@param place: directory of the file
        @param name: The name of the list file"""

        SolutionFile.__init__(self,place,name)
            
    def getSize(self):
        """@return: the size of the list"""

        size=-1L

        l=LineReader()
        self.openFile()

        erg=""
        
        while l.read(self.fh):
            try:
                size=long(l.line)
                break
            except ValueError:
                pass

        self.closeFile()

        return size
