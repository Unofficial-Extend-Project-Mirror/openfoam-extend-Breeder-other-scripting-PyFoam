#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/LineReader.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Read a file line by line"""

from PyFoam.Infrastructure.Logging import foamLogger

class LineReader(object):
    """Read a line from a file

    The line is stripped of whitespaces at the start and the end of
    the line and stored in a variable self.line"""
    
    def __init__(self):
        self.line=""
        self.goOn=True
        self.wasInterupted=False
        self.bytes=0L

    def bytesRead(self):
        """@return: number of bytes that were already read"""
        return self.bytes

    def userSaidStop(self):
        """@return: whether the reader caught a Keyboard-interrupt"""
        return self.wasInterupted
    
    def read(self,fh):
        """reads the next line

        fh - filehandle to read from

        Return value: False if the end of the file was reached. True
        otherwise"""

        if not self.goOn:
            return False
        
        try:
            self.line=fh.readline()
            self.bytes+=len(self.line)
        except KeyboardInterrupt,e:
            foamLogger().warning("Keyboard Interrupt")
            print " Interrupted by the Keyboard"
            self.wasInterupted=True
            self.goOn=False
            self.line=""
            return False
        
        if len(self.line)>0:
            status=True
        else:
            status=False
        self.line=self.line.strip()
        
        return status
